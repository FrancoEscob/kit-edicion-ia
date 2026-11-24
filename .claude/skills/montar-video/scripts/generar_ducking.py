#!/usr/bin/env python3
"""Genera la pista data-automation de HyperFrames para bajar la música cuando hay voz (ducking).

Lee un base-palabras.json ([{"i": 0, "w": "...", "s": 0.1, "e": 0.4}, ...]) y escribe
el JSON listo para pegar en el atributo data-automation del <audio> de música.
"""
import argparse
import json
import sys


def fusionar_tramos(palabras, pausa_min=0.6):
    tramos = []
    for p in sorted(palabras, key=lambda x: (x["s"], x["e"])):
        s, e = float(p["s"]), float(p["e"])
        if e <= s:
            continue
        if tramos and s - tramos[-1][1] < pausa_min:
            tramos[-1][1] = max(tramos[-1][1], e)
        else:
            tramos.append([s, e])
    return tramos


def generar_lane(tramos, vol_base=0.35, vol_duck=0.14, ataque=0.15, release=0.40, clip_start=0.0):
    """Construye los puntos {t, v} en tiempo local del clip de música (<= 512 puntos)."""
    puntos = [{"t": 0.0, "v": round(vol_base, 4)}]

    def agregar(t, v):
        t = round(max(0.0, t - clip_start), 3)
        v = round(v, 4)
        if t > puntos[-1]["t"]:
            puntos.append({"t": t, "v": v})
        elif t == puntos[-1]["t"]:
            puntos[-1]["v"] = v

    for s, e in tramos:
        t_baja = max(0.0, s - ataque)
        agregar(t_baja, puntos[-1]["v"])
        agregar(s, vol_duck)
        agregar(e, vol_duck)
        agregar(e + release, vol_base)

    return {"version": 1, "lanes": [{"target": "volume", "points": puntos}]}


def main():
    ap = argparse.ArgumentParser(description="Genera data-automation (ducking) desde base-palabras.json")
    ap.add_argument("palabras_json", help="Ruta a base-palabras.json")
    ap.add_argument("--volumen-base", type=float, default=0.32, help="Ganancia libre (sin voz), default 0.32")
    ap.add_argument("--volumen-voz", type=float, default=0.14, help="Ganancia bajo voz (~-7 dB sobre base), default 0.14")
    ap.add_argument("--ataque", type=float, default=0.15, help="Rampa de bajada en segundos, default 0.15")
    ap.add_argument("--release", type=float, default=0.40, help="Rampa de subida en segundos, default 0.40")
    ap.add_argument("--pausa-min", type=float, default=0.60, help="Pausa mínima (s) para volver a subir, default 0.60")
    ap.add_argument("--clip-start", type=float, default=0.0, help="data-start del clip de música en s, default 0")
    ap.add_argument("--html-attr", action="store_true", help="Escapa comillas como &quot; para atributo HTML doble")
    args = ap.parse_args()

    with open(args.palabras_json, encoding="utf-8") as f:
        palabras = json.load(f)

    tramos = fusionar_tramos(palabras, pausa_min=args.pausa_min)
    lane = generar_lane(
        tramos,
        vol_base=args.volumen_base,
        vol_duck=args.volumen_voz,
        ataque=args.ataque,
        release=args.release,
        clip_start=args.clip_start,
    )
    txt = json.dumps(lane, separators=(",", ":"))
    if args.html_attr:
        print(txt.replace('"', "&quot;"))
    else:
        print(txt)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Convierte base-palabras.json en grupos de subtítulos listos para pegar en HyperFrames.

Aplica las reglas de criterio/subtitulos.md:
- 2-3 palabras (o hasta --max-palabras / --max-chars)
- Corta en puntuación, en pausas > --pausa-corte (0.26 s) y en cortes de escena (--cortes)
- Garantiza permanencia mínima (--min-dur 0.26 s) sin solapamientos entre grupos
"""
import argparse
import json


def agrupar(palabras, duracion_total, max_palabras=3, max_chars=18, pausa_corte=0.26, min_dur=0.26, cortes=None):
    cortes = cortes or []
    grupos = []
    cur = []
    for w in palabras:
        if cur:
            prev = cur[-1]
            gap = w["s"] - prev["e"]
            cruza_corte = any(prev["e"] <= c <= w["s"] + 0.05 for c in cortes)
            termina_punt = prev["w"][-1:] in ".?!,;:"
            largo = sum(len(x["w"]) + 1 for x in cur) + len(w["w"])
            if len(cur) >= max_palabras or largo > max_chars or gap > pausa_corte or termina_punt or cruza_corte:
                grupos.append(cur)
                cur = []
        cur.append(w)
    if cur:
        grupos.append(cur)

    salida = []
    for idx, g in enumerate(grupos):
        start = float(g[0]["s"])
        raw_end = float(g[-1]["e"])
        next_start = float(grupos[idx + 1][0]["s"]) if idx + 1 < len(grupos) else float(duracion_total)
        end = min(raw_end + 0.28, next_start)
        if end - start < min_dur:
            end = min(start + min_dur, next_start)
        salida.append({
            "id": f"cg-{idx}",
            "start": round(start, 3),
            "end": round(end, 3),
            "words": [{"i": w["i"], "w": w["w"], "s": round(float(w["s"]), 3), "e": round(float(w["e"]), 3)} for w in g],
        })
    return salida


def main():
    ap = argparse.ArgumentParser(description="Agrupa base-palabras.json para subtítulos de HyperFrames")
    ap.add_argument("palabras_json", help="Ruta a base-palabras.json")
    ap.add_argument("--duracion", type=float, required=True, help="Duración total del clip en segundos")
    ap.add_argument("--max-palabras", type=int, default=3, help="Máximo de palabras por grupo (default 3)")
    ap.add_argument("--max-chars", type=int, default=18, help="Máximo de caracteres por grupo (default 18)")
    ap.add_argument("--cortes", default="", help="Tiempos de corte de plano separados por coma (ej: 7.42,10.62)")
    ap.add_argument("--out", help="Archivo JSON de salida (si se omite imprime por stdout)")
    args = ap.parse_args()

    with open(args.palabras_json, encoding="utf-8") as f:
        palabras = json.load(f)

    cortes = [float(x) for x in args.cortes.split(",") if x.strip()]
    grupos = agrupar(
        palabras,
        duracion_total=args.duracion,
        max_palabras=args.max_palabras,
        max_chars=args.max_chars,
        cortes=cortes,
    )
    txt = json.dumps(grupos, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(txt)
    else:
        print(txt)


if __name__ == "__main__":
    main()

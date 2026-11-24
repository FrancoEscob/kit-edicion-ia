#!/usr/bin/env python3
"""Busca una palabra o frase en base-palabras.json y devuelve tiempos de anclaje listos para HyperFrames.

Por defecto adelanta la entrada 60 ms (criterio/graficos-y-broll.md).
"""
import argparse
import json
import re


def norm(s):
    return re.sub(r"[^\w%$]+", "", s.lower())


def main():
    ap = argparse.ArgumentParser(description="Busca anclajes por palabra o índice en base-palabras.json")
    ap.add_argument("palabras_json", help="Ruta a base-palabras.json")
    ap.add_argument("--buscar", help="Palabra o frase a buscar (sin distinguir mayúsculas/puntuación)")
    ap.add_argument("--indice", type=int, help="Índice exacto i de la palabra")
    ap.add_argument("--adelanto", type=float, default=0.06, help="Adelanto de entrada en segundos (default 0.06)")
    args = ap.parse_args()

    with open(args.palabras_json, encoding="utf-8") as f:
        palabras = json.load(f)

    if args.indice is not None:
        hits = [p for p in palabras if p["i"] == args.indice]
        for p in hits:
            t_in = round(max(0.0, p["s"] - args.adelanto), 3)
            print(f"i={p['i']} \"{p['w']}\" palabra=[{p['s']:.3f}..{p['e']:.3f}] data-start={t_in:.3f}")
        return

    if args.buscar:
        tokens = [norm(x) for x in args.buscar.split() if norm(x)]
        n = len(tokens)
        encontrados = 0
        for k in range(len(palabras) - n + 1):
            ventana = [norm(palabras[k + j]["w"]) for j in range(n)]
            if ventana == tokens:
                p0, p1 = palabras[k], palabras[k + n - 1]
                t_in = round(max(0.0, p0["s"] - args.adelanto), 3)
                frase = " ".join(palabras[k + j]["w"] for j in range(n))
                print(f"i={p0['i']}..{p1['i']} \"{frase}\" palabra=[{p0['s']:.3f}..{p1['e']:.3f}] data-start={t_in:.3f}")
                encontrados += 1
        if not encontrados:
            print(f"Sin coincidencias exactas para: {args.buscar}")
    else:
        for p in palabras:
            print(f"{p['i']:3d}: [{p['s']:6.2f}..{p['e']:6.2f}] {p['w']}")


if __name__ == "__main__":
    main()

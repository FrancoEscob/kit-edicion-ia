#!/usr/bin/env python3
"""Genera una hoja de 6-12 cuadros (hoja-subtitulos.jpg) para aprobar subtítulos y tercio inferior.

Muestrea instantes directamente sobre palabras activas de base-palabras.json (nunca en pausas
vacías) a partir de un render draft de solo persona + tercio inferior + subtítulos.
"""
import argparse
import json
import math
import os
import subprocess
import tempfile


def elegir_tiempos(palabras, cantidad):
    validas = [p for p in palabras if float(p["e"]) > float(p["s"])]
    if not validas:
        return []
    n = max(6, min(12, int(cantidad), len(validas)))
    if n == 1:
        return [round((validas[0]["s"] + validas[0]["e"]) / 2, 3)]
    # Repartir índices parejos dejando pequeño margen al principio y al final
    idxs = [round(i * (len(validas) - 1) / (n - 1)) for i in range(n)]
    tiempos = []
    for k in idxs:
        p = validas[k]
        t = round((float(p["s"]) + float(p["e"])) / 2.0, 3)
        tiempos.append((t, p["w"]))
    return tiempos


def main():
    ap = argparse.ArgumentParser(description="Arma hoja-subtitulos.jpg de 6-12 cuadros sobre palabras activas")
    ap.add_argument("video", help="MP4 renderizado en draft (solo persona + tercio inferior + subtítulos)")
    ap.add_argument("palabras_json", help="Ruta a base-palabras.json")
    ap.add_argument("--cuadros", type=int, default=9, help="Cantidad de cuadros entre 6 y 12 (default 9)")
    ap.add_argument("--cols", type=int, default=3, help="Columnas de la grilla (default 3)")
    ap.add_argument("--ancho-tile", type=int, default=360, help="Ancho en px de cada cuadro (default 360)")
    ap.add_argument("--out", default="hoja-subtitulos.jpg", help="Archivo JPG de salida")
    args = ap.parse_args()

    with open(args.palabras_json, encoding="utf-8") as f:
        palabras = json.load(f)

    muestras = elegir_tiempos(palabras, args.cuadros)
    if not muestras:
        raise SystemExit("base-palabras.json no tiene palabras con tiempos válidos")

    cols = max(1, args.cols)
    rows = math.ceil(len(muestras) / cols)

    with tempfile.TemporaryDirectory(prefix="hoja-subs-") as tmp:
        lista_imgs = []
        for idx, (t, palabra) in enumerate(muestras):
            tile_path = os.path.join(tmp, f"f_{idx:02d}.png")
            etiqueta = f"{t:05.2f}s"
            cmd = [
                "ffmpeg", "-y", "-loglevel", "error",
                "-ss", f"{t:.3f}",
                "-i", args.video,
                "-frames:v", "1",
                "-vf", (
                    f"scale={args.ancho_tile}:-1,"
                    f"drawtext=text='{etiqueta}':x=10:y=10:fontsize=22:fontcolor=yellow:"
                    "box=1:boxcolor=black@0.72:boxborderw=6"
                ),
                tile_path,
            ]
            subprocess.run(cmd, check=True)
            lista_imgs.append(tile_path)

        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        cmd_tile = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-framerate", "1",
            "-i", os.path.join(tmp, "f_%02d.png"),
            "-vf", f"tile={cols}x{rows}:padding=6:color=0x111111",
            "-frames:v", "1",
            "-q:v", "3",
            args.out,
        ]
        subprocess.run(cmd_tile, check=True)

    print(f"Generado {args.out} ({len(muestras)} cuadros en grilla {cols}x{rows})")


if __name__ == "__main__":
    main()

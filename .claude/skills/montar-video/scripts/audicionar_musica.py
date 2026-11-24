#!/usr/bin/env python3
"""Genera 3-5 previews de 10 s mezclando pistas de música sobre el arranque de base.mp4 con ffmpeg.

Sirve para audicionar de oído distintas pistas libres antes del render final en HyperFrames.
"""
import argparse
import glob
import os
import re
import subprocess


AUDIO_EXTS = (".mp3", ".wav", ".m4a", ".ogg", ".flac")


def slug(nombre):
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", os.path.splitext(nombre)[0].lower()).strip("-") or "pista"


def main():
    ap = argparse.ArgumentParser(description="Genera previews de 10 s mezclando música sobre base.mp4")
    ap.add_argument("video_base", help="Ruta a base.mp4")
    ap.add_argument("pistas", nargs="+", help="3-5 archivos de audio o una carpeta con pistas")
    ap.add_argument("--out-dir", default="previews-musica", help="Carpeta de salida (default previews-musica)")
    ap.add_argument("--duracion", type=float, default=10.0, help="Duración de cada preview en s (default 10)")
    ap.add_argument("--inicio-musica", type=float, default=0.0, help="Segundo donde arranca la música (default 0)")
    ap.add_argument("--musica-db", type=float, default=-10.0, help="Nivel de la música respecto a su pico/voz en dB (default -10)")
    ap.add_argument("--max-pistas", type=int, default=5, help="Máximo de previews a generar (default 5)")
    args = ap.parse_args()

    archivos = []
    for p in args.pistas:
        if os.path.isdir(p):
            for fn in sorted(os.listdir(p)):
                if fn.lower().endswith(AUDIO_EXTS):
                    archivos.append(os.path.join(p, fn))
        elif os.path.isfile(p):
            archivos.append(p)
        else:
            archivos.extend(sorted(glob.glob(p)))

    archivos = archivos[: args.max_pistas]
    if not archivos:
        raise SystemExit("No se encontraron pistas de audio válidas.")

    os.makedirs(args.out_dir, exist_ok=True)
    dur = float(args.duracion)
    fade_out_t = max(0.0, dur - 0.4)

    for idx, pista in enumerate(archivos, start=1):
        nombre = slug(os.path.basename(pista))
        out_mp4 = os.path.join(args.out_dir, f"preview-{idx:02d}-{nombre}.mp4")
        # Mezcla la voz de base.mp4 a nivel pleno con la pista nivelada a -24 LUFS (10 dB bajo la voz de -14 LUFS)
        # más ajuste fino --musica-db relativo a -10 dB
        objetivo_lufs = -14.0 + float(args.musica_db)
        fc = (
            f"[0:a]atrim=0:{dur},asetpts=PTS-STARTPTS[voz];"
            f"[1:a]atrim={args.inicio_musica}:{args.inicio_musica + dur},asetpts=PTS-STARTPTS,"
            f"loudnorm=I={objetivo_lufs:.1f}:TP=-2:LRA=11,"
            f"afade=t=in:st=0:d=0.4,afade=t=out:st={fade_out_t:.2f}:d=0.4[mus];"
            f"[voz][mus]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
            f"alimiter=limit=0.84:level=false[outa]"
        )
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-t", f"{dur:.2f}", "-i", args.video_base,
            "-i", pista,
            "-filter_complex", fc,
            "-map", "0:v:0", "-map", "[outa]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-shortest",
            out_mp4,
        ]
        subprocess.run(cmd, check=True)
        print(f"Preview {idx}/{len(archivos)}: {out_mp4} (música ~{objetivo_lufs:.1f} LUFS)")


if __name__ == "__main__":
    main()

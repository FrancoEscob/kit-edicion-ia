#!/usr/bin/env python3
"""Valida un cue-sheet.json y genera las etiquetas <audio> listas para la Capa 5 de HyperFrames.

Formato de cue-sheet.json:
{
  "cues": [
    {"t": 0.40, "evento": "Entra gancho", "familia": "textura", "archivo": "sfx/pop.mp3", "db": -8}
  ]
}
Familias válidas: whoosh, textura, riser-hit.
Aplica las reglas de criterio/sonido.md: colapsa eventos a < 90 ms con prioridad riser-hit > whoosh > textura.
"""
import argparse
import json
import os
import subprocess

PRIORIDAD = {"riser-hit": 3, "whoosh": 2, "textura": 1}
DB_DEFECTO = {"whoosh": -11.0, "textura": -8.0, "riser-hit": -5.0}


def duracion_media(ruta):
    try:
        out = subprocess.check_output(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=nw=1:nk=1",
                ruta,
            ],
            text=True,
        ).strip()
        return round(float(out), 3)
    except Exception:
        return None


def db_a_volumen(db):
    return round(min(1.0, max(0.0, 10.0 ** (float(db) / 20.0))), 4)


def colapsar_cues(cues, ventana_s=0.09):
    ordenados = sorted(cues, key=lambda c: (float(c["t"]), -PRIORIDAD.get(c.get("familia", "textura"), 0)))
    limpios = []
    descartados = []
    for c in ordenados:
        if limpios and (float(c["t"]) - float(limpios[-1]["t"])) < ventana_s:
            p_prev = PRIORIDAD.get(limpios[-1].get("familia", "textura"), 0)
            p_cur = PRIORIDAD.get(c.get("familia", "textura"), 0)
            if p_cur > p_prev:
                descartados.append(limpios[-1])
                limpios[-1] = c
            else:
                descartados.append(c)
        else:
            limpios.append(c)
    return limpios, descartados


def main():
    ap = argparse.ArgumentParser(description="Convierte cue-sheet.json en etiquetas <audio> de HyperFrames")
    ap.add_argument("cue_sheet", help="Ruta a cue-sheet.json")
    ap.add_argument("--base-dir", help="Carpeta base del montaje para resolver rutas relativas de SFX")
    ap.add_argument("--track-inicio", type=int, default=6, help="Primer data-track-index libre para SFX (default 6)")
    ap.add_argument("--tabla", action="store_true", help="Imprime tabla Markdown en vez de etiquetas HTML")
    args = ap.parse_args()

    with open(args.cue_sheet, encoding="utf-8") as f:
        data = json.load(f)

    cues_raw = data.get("cues", data if isinstance(data, list) else [])
    base_dir = args.base_dir or os.path.dirname(os.path.abspath(args.cue_sheet))
    cues, descartados = colapsar_cues(cues_raw)

    if args.tabla:
        print("| Tiempo | Evento | Familia | Archivo | dB | `data-volume` |")
        print("|---:|---|---|---|---:|---:|")
        for c in cues:
            fam = c.get("familia", "textura")
            db = float(c.get("db", DB_DEFECTO.get(fam, -9.0)))
            print(f"| {float(c['t']):.2f} s | {c.get('evento', '')} | {fam} | `{c['archivo']}` | {db:+.1f} dB | {db_a_volumen(db)} |")
        if descartados:
            print(f"\n<!-- {len(descartados)} cue(s) colapsados por estar a < 90 ms -->")
        return

    # Asignar tracks sin solapar tiempos en el mismo track
    tracks_fin = []
    for idx, c in enumerate(cues, start=1):
        fam = c.get("familia", "textura")
        db = float(c.get("db", DB_DEFECTO.get(fam, -9.0)))
        vol = db_a_volumen(db)
        t = round(float(c["t"]), 3)
        archivo = c["archivo"]
        ruta_abs = archivo if os.path.isabs(archivo) else os.path.join(base_dir, archivo)
        dur = c.get("duracion_s")
        if dur is None and os.path.exists(ruta_abs):
            dur = duracion_media(ruta_abs)
        if dur is None:
            dur = 1.0
        dur = round(min(float(dur), 3.0 if fam != "riser-hit" else 10.5), 3)

        track_idx = None
        for ti, fin_t in enumerate(tracks_fin):
            if t >= fin_t + 0.02:
                track_idx = ti
                tracks_fin[ti] = t + dur
                break
        if track_idx is None:
            track_idx = len(tracks_fin)
            tracks_fin.append(t + dur)

        comentario = f"<!-- {t:.2f}s · {fam} · {c.get('evento', '')} ({db:+.1f} dB) -->"
        tag = (
            f'<audio id="sfx-{idx:02d}" src="{archivo}" '
            f'data-start="{t}" data-duration="{dur}" '
            f'data-volume="{vol}" data-track-index="{args.track_inicio + track_idx}"></audio>'
        )
        print(comentario)
        print(tag)
        if not os.path.exists(ruta_abs):
            print(f"<!-- ADVERTENCIA: no existe {ruta_abs}; copiar el archivo antes de renderizar -->")


if __name__ == "__main__":
    main()

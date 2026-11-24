#!/usr/bin/env python3
"""Arma un banco local de SFX CC0 en .externas/sfx/{whooshes,texturas,risers-hits}/ sin cuenta ni API key.

Fuentes gratuitas:
1. Openverse Audio API (license=cc0, previews HQ de Freesound sin registro).
2. Fallback offline: copia y clasifica los 21 sonidos curados que trae la skill media-use de HyperFrames.
"""
import argparse
import json
import os
import re
import shutil
import urllib.parse
import urllib.request

CONSULTAS_CC0 = {
    "whooshes": [
        ("whoosh", 3),
        ("swipe whoosh", 2),
    ],
    "texturas": [
        ("ui click", 2),
        ("pop sound", 2),
        ("paper rustle", 2),
    ],
    "risers-hits": [
        ("cinematic riser", 2),
        ("bass impact hit", 2),
    ],
}

MAPA_MEDIA_USE = {
    "whooshes": ["whoosh.mp3", "whoosh-short.mp3", "whoosh-cinematic.mp3"],
    "texturas": ["click.mp3", "click-soft.mp3", "pop.mp3", "key-press.mp3", "typing.mp3", "notification.mp3", "ping.mp3", "chime.mp3"],
    "risers-hits": ["riser.mp3", "impact-bass-1.mp3", "impact-bass-2.mp3", "glitch-1.mp3"],
}


def slugify(s):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower()).strip("-")
    return s[:42] or "sfx"


def bajar_openverse(destino, max_ms=6000):
    creditos = ["# Créditos SFX (Openverse CC0)", ""]
    bajados = 0
    for familia, queries in CONSULTAS_CC0.items():
        fam_dir = os.path.join(destino, familia)
        os.makedirs(fam_dir, exist_ok=True)
        vistos = set()
        for q, limite in queries:
            params = urllib.parse.urlencode({"q": q, "license": "cc0", "page_size": 12})
            url = f"https://api.openverse.org/v1/audio/?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": "kit-edicion-ia/1.0"})
            data = None
            for intento in range(2):
                try:
                    with urllib.request.urlopen(req, timeout=20) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                    break
                except Exception as exc:
                    if intento == 1:
                        print(f"[aviso] Openverse falló para '{q}': {exc}")
            if not data:
                continue
            tomados = 0
            for item in data.get("results", []):
                if tomados >= limite:
                    break
                if (item.get("license") or "").lower() != "cc0":
                    continue
                audio_url = item.get("url")
                dur_ms = item.get("duration") or 0
                tope = 14000 if familia == "risers-hits" else max_ms
                if not audio_url or audio_url in vistos or (dur_ms and dur_ms > tope):
                    continue
                ext = os.path.splitext(urllib.parse.urlparse(audio_url).path)[1].lower()
                if ext not in (".mp3", ".wav", ".ogg"):
                    ext = ".mp3"
                nombre = f"{slugify(item.get('title', q))}{ext}"
                out_path = os.path.join(fam_dir, nombre)
                try:
                    dl_req = urllib.request.Request(audio_url, headers={"User-Agent": "kit-edicion-ia/1.0"})
                    with urllib.request.urlopen(dl_req, timeout=25) as r, open(out_path, "wb") as f:
                        f.write(r.read())
                except Exception:
                    continue
                vistos.add(audio_url)
                tomados += 1
                bajados += 1
                creditos.append(
                    f"- `{familia}/{nombre}` — \"{item.get('title', 'Sin título')}\" "
                    f"({item.get('creator', 'Anónimo')}), CC0 · {item.get('foreign_landing_url', audio_url)}"
                )
    with open(os.path.join(destino, "CREDITS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(creditos) + "\n")
    print(f"Bajados {bajados} SFX CC0 en {destino}")


def copiar_desde_media_use(media_use_sfx_dir, destino):
    copiados = 0
    for familia, archivos in MAPA_MEDIA_USE.items():
        fam_dir = os.path.join(destino, familia)
        os.makedirs(fam_dir, exist_ok=True)
        for fn in archivos:
            src = os.path.join(media_use_sfx_dir, fn)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(fam_dir, fn))
                copiados += 1
    print(f"Copiados {copiados} SFX desde media-use en {destino}")


def main():
    ap = argparse.ArgumentParser(description="Arma el banco local de SFX en .externas/sfx/")
    ap.add_argument("--destino", default=".externas/sfx", help="Carpeta destino (default .externas/sfx)")
    ap.add_argument("--desde-media-use", help="Ruta a assets/sfx de la skill media-use (modo offline)")
    args = ap.parse_args()

    os.makedirs(args.destino, exist_ok=True)
    if args.desde_media_use:
        copiar_desde_media_use(args.desde_media_use, args.destino)
    else:
        bajar_openverse(args.destino)


if __name__ == "__main__":
    main()

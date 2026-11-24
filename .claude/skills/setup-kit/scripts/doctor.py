#!/usr/bin/env python3
"""Revisa que el kit esté completo. Solo mira, no instala nada.

uso: python .claude/skills/setup-kit/scripts/doctor.py [--json]

Corre con cualquier Python 3.8+ y solo con la biblioteca estándar, así sirve antes de que exista .venv/.
Sale con 0 si todo lo necesario está, con 1 si falta algo. Cada problema trae una pista de cómo arreglarlo.
"""
import json, os, platform, re, shutil, subprocess, sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
EXT = json.load(open(os.path.join(RAIZ, '.claude', 'skills', 'setup-kit', 'externas.json'), encoding='utf-8'))
WIN = os.name == 'nt'
VENV_PY = os.path.join(RAIZ, '.venv', 'Scripts' if WIN else 'bin', 'python.exe' if WIN else 'python')
HF_SKILLS = ['hyperframes', 'hyperframes-cli', 'hyperframes-registry', 'media-use']
MODELOS = {'silero_vad': 'silero_vad.onnx', 'yunet': 'face_detection_yunet_2023mar.onnx', 'rnnoise': 'cb.rnnn'}

res = []


def chk(nombre, ok, detalle='', arreglo='', necesario=True):
    res.append({'nombre': nombre, 'ok': bool(ok), 'detalle': detalle, 'arreglo': '' if ok else arreglo,
                'necesario': necesario})


def sh(cmd, cwd=None):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=60,
                           shell=WIN and cmd[0] in ('npm', 'npx'))
        return p.returncode, (p.stdout or '') + (p.stderr or '')
    except Exception as e:  # programa ausente, timeout
        return 127, str(e)


def version(txt, patron=r'(\d+)\.(\d+)'):
    m = re.search(patron, txt or '')
    return (int(m.group(1)), int(m.group(2))) if m else None


def main():
    chk('sistema', True, f'{platform.system()} {platform.release()} {platform.machine()}')

    # Programas del sistema
    rc, out = sh(['git', '--version'])
    chk('git', rc == 0, out.strip(), 'instalar git (Mac: xcode-select --install; Windows: winget install Git.Git)')

    rc, out = sh(['node', '--version'])
    v = version(out)
    chk('node 22+', rc == 0 and v and v[0] >= 22, out.strip(),
        'instalar Node 22 LTS o más nuevo (Mac: brew install node; Windows: winget install OpenJS.NodeJS.LTS; Linux: nvm o el gestor del sistema)')

    rc, out = sh(['ffmpeg', '-hide_banner', '-version'])
    v = version(out, r'ffmpeg version n?(\d+)\.(\d+)')
    chk('ffmpeg 7+', rc == 0 and v and v[0] >= 7, out.splitlines()[0] if out else 'no está',
        'instalar ffmpeg 7 o más nuevo (Mac: brew install ffmpeg; Windows: winget install Gyan.FFmpeg; Linux: el gestor del sistema o un build estático)')
    chk('ffprobe', shutil.which('ffprobe') is not None, '', 'viene con ffmpeg: reinstalar ffmpeg')
    if rc == 0:
        rc2, filtros = sh(['ffmpeg', '-hide_banner', '-filters'])
        for f, nec in (('loudnorm', True), ('subtitles', True), ('arnndn', False)):
            chk(f'ffmpeg: filtro {f}', re.search(rf'\s{f}\s', filtros) is not None, '',
                'usar un ffmpeg completo (Homebrew, Gyan full o un build estático)', necesario=nec)

    chk('uv', shutil.which('uv') is not None, '',
        'instalar uv (Mac/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh; Windows: winget install astral-sh.uv)')

    # Python del kit
    if os.path.exists(VENV_PY):
        rc, out = sh([VENV_PY, '-c', 'import sys;print(sys.version)'])
        v = version(out)
        chk('.venv (Python 3.11 a 3.12)', v and (3, 11) <= v <= (3, 12), out.strip().split()[0] if out else '',
            'rehacer: uv venv --python 3.12 .venv')
        for mod, nec in (('numpy', True), ('onnxruntime', True), ('cv2', True), ('whisperx', False), ('faster_whisper', True),
                         ('yt_dlp', True)):
            rc, out = sh([VENV_PY, '-c', f'import {mod}'])
            chk(f'.venv: {mod}', rc == 0, '', 'uv pip install --python .venv -r .claude/skills/<skill>/requirements.txt',
                necesario=nec)
    else:
        chk('.venv', False, 'no existe', 'uv venv --python 3.12 .venv y después instalar los requirements.txt de cada skill')

    # Modelos
    for k, archivo in MODELOS.items():
        p = os.path.join(RAIZ, '.externas', 'modelos', archivo)
        chk(f'modelo {k}', os.path.exists(p) and os.path.getsize(p) > 1000, EXT['modelos'][k]['para'],
            f"bajar {EXT['modelos'][k]['url']} a .externas/modelos/{archivo}", necesario=k != 'rnnoise')

    # HyperFrames
    pj = os.path.join(RAIZ, 'node_modules', 'hyperframes', 'package.json')
    hv = json.load(open(pj, encoding='utf-8')).get('version') if os.path.exists(pj) else None
    quiere = EXT['hyperframes']['npm'].split('@')[1]
    chk(f'hyperframes {quiere}', hv == quiere, hv or 'no está', 'npm install (en la raíz del kit)')
    for s in HF_SKILLS:
        chk(f'skill {s}', os.path.exists(os.path.join(RAIZ, '.claude', 'skills', s, 'SKILL.md')), '',
            'ver paso 4 de setup-kit/SKILL.md (copiar desde .externas/hyperframes/skills/)')

    # Lemo
    lib = os.path.join(RAIZ, '.externas', 'lemo-opuscar')
    if os.path.isdir(os.path.join(lib, '.git')):
        rc, out = sh(['git', '-C', lib, 'rev-parse', 'HEAD'])
        chk('lemo: versión fijada', out.strip() == EXT['lemo']['commit'], out.strip()[:12],
            f"git -C .externas/lemo-opuscar fetch --depth 1 origin {EXT['lemo']['commit']} && git -C .externas/lemo-opuscar checkout {EXT['lemo']['commit']}")
    else:
        chk('lemo: biblioteca', False, 'no está', 'ver paso Lemo en setup-kit/SKILL.md')
    chk('skill lemo-opuscar', os.path.exists(os.path.join(RAIZ, '.claude', 'skills', 'lemo-opuscar', 'SKILL.md')), '',
        'copiar .externas/lemo-opuscar/plugin/skills/lemo-opuscar a .claude/skills/')
    chk('lemo: paquetes base', os.path.exists(os.path.join(lib, 'node_modules', '.lemo-ok')), '',
        'LEMO_OPUSCAR_HOME=<ruta absoluta a .externas/lemo-opuscar> sh .claude/skills/lemo-opuscar/scripts/setup.sh deps')
    cfg = os.path.join(RAIZ, '.claude', 'settings.local.json')
    home = None
    if os.path.exists(cfg):
        try:
            home = json.load(open(cfg, encoding='utf-8')).get('env', {}).get('LEMO_OPUSCAR_HOME')
        except Exception:
            pass
    chk('lemo: LEMO_OPUSCAR_HOME', home and os.path.isdir(home), home or 'sin definir',
        'escribir en .claude/settings.local.json: {"env": {"LEMO_OPUSCAR_HOME": "<ruta absoluta a .externas/lemo-opuscar>"}}')

    # Ingeniería inversa
    for n in ('dissect', 'remake'):
        d = os.path.join(RAIZ, '.externas', n)
        okc = False
        if os.path.isdir(os.path.join(d, '.git')):
            rc, out = sh(['git', '-C', d, 'rev-parse', 'HEAD'])
            okc = out.strip() == EXT[n]['commit']
        chk(f'{n}: versión fijada', okc, '', f"ver paso 6 de setup-kit/SKILL.md ({EXT[n]['repo']})")
        chk(f'skill {n}', os.path.exists(os.path.join(RAIZ, '.claude', 'skills', n, 'SKILL.md')), '',
            f"cp -r .externas/{n}/{EXT[n]['skill']} .claude/skills/{n}")
    if platform.system() != 'Darwin':
        chk('tesseract (texto en pantalla, para dissect)', shutil.which('tesseract') is not None, '',
            'Windows: winget install --id UB-Mannheim.TesseractOCR -e; Linux: el gestor del sistema (tesseract-ocr)')

    # Remotion: opcional
    chk('remotion (opcional)', any(n.startswith('remotion') and n != 'remotion-to-hyperframes'
                                   for n in os.listdir(os.path.join(RAIZ, '.claude', 'skills'))),
        'solo si la persona lo pide', 'npx -y skills add remotion-dev/skills -a claude-code -y --copy', necesario=False)

    faltan = [r for r in res if r['necesario'] and not r['ok']]
    if '--json' in sys.argv:
        print(json.dumps({'ok': not faltan, 'raiz': RAIZ, 'resultados': res}, ensure_ascii=False, indent=1))
    else:
        for r in res:
            marca = '✓' if r['ok'] else ('✗' if r['necesario'] else '·')
            print(f"{marca} {r['nombre']}" + (f"  ({r['detalle']})" if r['detalle'] else ''))
            if r['arreglo']:
                print(f"    → {r['arreglo']}")
        print('\nTodo listo.' if not faltan else f'\nFaltan {len(faltan)} cosas necesarias.')
    sys.exit(0 if not faltan else 1)


if __name__ == '__main__':
    main()

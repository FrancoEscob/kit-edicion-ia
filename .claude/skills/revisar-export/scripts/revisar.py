#!/usr/bin/env python3
"""Mide un video terminado y escribe revision.md + hoja.jpg al lado.

uso: python revisar.py FINAL.mp4 [--palabras base-palabras.json] [--formato 9:16] [--sin-transcribir]

Claude no ve ni oye el video: este script mide lo que se puede medir y deja una hoja de cuadros para mirar.
--palabras: las palabras que DEBERÍAN sonar, con los tiempos que usaron los subtítulos (reloj del video final).
Con eso compara lo que se oye de verdad (volviendo a transcribir) contra lo esperado: palabras que faltan o
sobran, y el desfase entre subtítulos y voz.
"""
import argparse, difflib, json, os, re, statistics, subprocess, sys, tempfile, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..', '..', '..'))
TRANSCRIBIR = os.path.join(RAIZ, '.claude', 'skills', 'transcribir', 'scripts', 'transcribir.py')
VENV_PY = os.path.join(RAIZ, '.venv', 'Scripts' if os.name == 'nt' else 'bin', 'python.exe' if os.name == 'nt' else 'python')
FORMATOS = {'9:16': (1080, 1920), '1:1': (1080, 1080), '4:5': (1080, 1350), '16:9': (1920, 1080)}


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def probe(path):
    rc, out, err = run(['ffprobe', '-v', 'error', '-show_entries',
                        'format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels',
                        '-of', 'json', path])
    if rc:
        sys.exit(f'ffprobe no pudo leer {path}: {err.strip()}')
    return json.loads(out)


def loudness(path):
    _, _, err = run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'])
    tail = err[err.rfind('Summary:'):]
    i = re.search(r'I:\s+(-?[\d.]+|-inf) LUFS', tail)
    tp = re.search(r'Peak:\s+(-?[\d.]+|-inf) dBFS', tail)
    f = lambda m: float(m.group(1)) if m and m.group(1) != '-inf' else None
    return f(i), f(tp)


def detect(path, filtro, clave):
    _, _, err = run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-vf' if 'audio' not in clave else '-af', filtro,
                     '-f', 'null', '-'])
    return err


def tramos(err, ini, fin):
    a = [float(x) for x in re.findall(ini + r'(-?[\d.]+)', err)]
    b = [float(x) for x in re.findall(fin + r'(-?[\d.]+)', err)]
    return list(zip(a, b + [None] * (len(a) - len(b))))


def norm(w):
    w = unicodedata.normalize('NFD', w.lower())
    return re.sub(r'[^a-z0-9ñ]', '', ''.join(c for c in w if unicodedata.category(c) != 'Mn'))


def transcribir(path):
    if not os.path.exists(TRANSCRIBIR):
        return None, 'falta la skill transcribir'
    salida = tempfile.mkdtemp(prefix='revisar-')
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    rc, out, err = run([py, TRANSCRIBIR, path, '--salida', salida])
    p = os.path.join(salida, 'palabras.json')
    if rc or not os.path.exists(p):
        return None, f'transcribir falló: {(err or out).strip()[-300:]}'
    return json.load(open(p, encoding='utf-8')), None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video')
    ap.add_argument('--palabras')
    ap.add_argument('--formato')
    ap.add_argument('--sin-transcribir', action='store_true')
    a = ap.parse_args()
    v = os.path.abspath(a.video)
    carpeta = os.path.dirname(v)
    info = probe(v)
    dur = float(info['format']['duration'])
    vs = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
    au = next((s for s in info['streams'] if s['codec_type'] == 'audio'), None)
    fallas, avisos, ok, no_medido = [], [], [], []

    # Formato
    if vs:
        w, h = vs['width'], vs['height']
        ok.append(f"imagen {w}×{h}, {vs['codec_name']}, {vs['r_frame_rate']} fps, {dur:.2f} s")
        if a.formato and FORMATOS.get(a.formato) != (w, h):
            fallas.append(f'el formato pedido era {a.formato} {FORMATOS.get(a.formato)} y salió {w}×{h}')
    else:
        fallas.append('no tiene imagen')
    if not au:
        avisos.append('no tiene audio')
    rc, out, _ = run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,bit_rate', '-of', 'json', v])
    tasas = {s['codec_type']: int(s['bit_rate']) // 1000 for s in json.loads(out or '{}').get('streams', []) if s.get('bit_rate')}
    if tasas.get('video') and tasas['video'] < 8000:
        avisos.append(f"la imagen va a {tasas['video']} kb/s: para que la red no la degrade conviene 10.000 a 16.000 (renderizá con --quality high)")
    if tasas.get('audio') and tasas['audio'] < 190:
        avisos.append(f"el audio va a {tasas['audio']} kb/s (conviene 256)")
    rc, out, _ = run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,duration', '-of', 'json', v])
    largos = {s['codec_type']: float(s['duration']) for s in json.loads(out or '{}').get('streams', []) if s.get('duration')}
    if 'video' in largos and 'audio' in largos and abs(largos['video'] - largos['audio']) > 0.1:
        fallas.append(f"la imagen dura {largos['video']:.2f} s y el audio {largos['audio']:.2f} s: terminan en momentos distintos")

    # Volumen
    if au:
        i, tp = loudness(v)
        if i is None:
            fallas.append('el audio está en silencio')
        else:
            linea = f'volumen integrado {i:.1f} LUFS, pico real {tp:.1f} dBTP'
            if not -16 <= i <= -12:
                fallas.append(linea + ' (para redes: −14 ± 0,7)')
            elif not -14.7 <= i <= -13.3:
                avisos.append(linea + ' (para redes: −14 ± 0,7)')
            else:
                ok.append(linea)
            if tp is not None and tp > -1.0:
                fallas.append(f'el pico real llega a {tp:.1f} dBTP: puede saturar al subirlo a una red (tope −1,5)')
            elif tp is not None and tp > -1.5:
                avisos.append(f'el pico real llega a {tp:.1f} dBTP (para clips conviene ≤ −1,5)')

    # Negro, congelado y silencio
    negros = tramos(detect(v, 'blackdetect=d=0.25:pix_th=0.10', 'video'), 'black_start:', 'black_end:')
    for s, e in negros:
        fallas.append(f'imagen en negro de {s:.2f} a {e if e is not None else dur:.2f} s')
    quietos = tramos(detect(v, 'freezedetect=n=0.003:d=1.5', 'video'), 'freeze_start: ', 'freeze_end: ')
    for s, e in quietos:
        avisos.append(f'imagen quieta de {s:.2f} a {e if e is not None else dur:.2f} s (¿se trabó un video o una escena?)')
    if au:
        sil = tramos(detect(v, 'silencedetect=noise=-45dB:d=1.0', 'audio'), 'silence_start: ', 'silence_end: ')
        for s, e in sil:
            avisos.append(f'silencio de {s:.2f} a {e if e is not None else dur:.2f} s')

    # Lo que se oye
    if a.sin_transcribir or not au:
        no_medido.append('lo que se oye (no se volvió a transcribir)')
    else:
        oidas, err = transcribir(v)
        if err:
            no_medido.append(f'lo que se oye: {err}')
        else:
            if oidas:
                primero, ultimo = oidas[0]['s'], oidas[-1]['e']
                (ok if primero <= 0.3 else avisos).append(f'la primera palabra suena a los {primero:.2f} s')
                cola = dur - ultimo
                (ok if 0.05 <= cola <= 0.8 else avisos).append(
                    f'después de la última palabra quedan {cola:.2f} s' + ('' if 0.05 <= cola <= 0.8 else
                                                                         ' (lo normal es entre 0,05 y 0,8)'))
            if a.palabras:
                esperadas = json.load(open(a.palabras, encoding='utf-8'))
                e_norm = [norm(p['w']) for p in esperadas]
                o_norm = [norm(p['w']) for p in oidas]
                sm = difflib.SequenceMatcher(a=e_norm, b=o_norm, autojunk=False)
                difs = []
                for op in sm.get_opcodes():
                    tag, i1, i2, j1, j2 = op
                    if tag == 'equal':
                        difs += [oidas[j1 + k]['s'] - esperadas[i1 + k]['s'] for k in range(i2 - i1)]
                    elif tag in ('delete', 'replace'):
                        txt = ' '.join(p['w'] for p in esperadas[i1:i2])
                        avisos.append(f"se esperaba «{txt}» cerca de {esperadas[i1]['s']:.2f} s y "
                                      + (f"se oye «{' '.join(p['w'] for p in oidas[j1:j2])}»" if tag == 'replace'
                                         else 'no se oye'))
                    elif tag == 'insert':
                        avisos.append(f"se oye «{' '.join(p['w'] for p in oidas[j1:j2])}» cerca de {oidas[j1]['s']:.2f} s, "
                                      'que no estaba en el plan')
                cobertura = sm.ratio()
                (ok if cobertura >= 0.9 else fallas).append(f'coincidencia entre lo planeado y lo que se oye: {cobertura:.0%}')
                if difs:
                    med = statistics.median(difs)
                    peor = max(difs, key=abs)
                    linea = f'desfase subtítulos-voz: mediana {med * 1000:+.0f} ms, peor {peor * 1000:+.0f} ms'
                    if abs(med) > 0.12 or abs(peor) > 0.35:
                        fallas.append(linea + ' (los subtítulos no caen con la voz)')
                    elif abs(med) > 0.08 or abs(peor) > 0.15:
                        avisos.append(linea + ' (el criterio pide ±150 ms)')
                    else:
                        ok.append(linea)
            else:
                no_medido.append('desfase de subtítulos (pasá --palabras con las palabras que usaron los subtítulos)')

    # Hoja de cuadros
    n = 24
    hoja = os.path.join(carpeta, os.path.splitext(os.path.basename(v))[0] + '-hoja.jpg')
    run(['ffmpeg', '-v', 'error', '-y', '-i', v, '-vf',
         f"fps={n / max(dur, 0.1):.4f},scale=270:-2,drawtext=text='%{{pts\\:hms}}':x=6:y=6:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6,tile=6x4",
         '-frames:v', '1', hoja])
    if not os.path.exists(hoja):  # drawtext no disponible en algunos ffmpeg
        run(['ffmpeg', '-v', 'error', '-y', '-i', v, '-vf', f'fps={n / max(dur, 0.1):.4f},scale=270:-2,tile=6x4',
             '-frames:v', '1', hoja])

    md = [f'# Revisión de {os.path.basename(v)}', '',
          'Resultado: ' + ('**no está para entregar**' if fallas else ('**entregable, con avisos**' if avisos else '**bien**')), '']
    for titulo, lista in (('Falla', fallas), ('Avisos', avisos), ('Bien', ok), ('No medido', no_medido)):
        if lista:
            md += [f'## {titulo}', ''] + [f'- {x}' for x in lista] + ['']
    md += ['## Para mirar', '', f'Hoja de cuadros: `{os.path.basename(hoja)}` (24 cuadros, con el tiempo arriba a la izquierda).',
           'Mirá cada cuadro: caras tapadas por texto, texto cortado o fuera de la zona segura, cortes feos, gráficos que no caen donde deben.', '']
    out = os.path.join(carpeta, 'revision.md')
    open(out, 'w', encoding='utf-8').write('\n'.join(md))
    print('\n'.join(md))
    sys.exit(1 if fallas else 0)


if __name__ == '__main__':
    main()

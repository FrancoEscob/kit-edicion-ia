#!/usr/bin/env python3
"""Prepara un video base a partir de un plan.json según el contrato del kit.

Lee plan.json y genera en la carpeta de salida:
  - base.mp4            (cortado por palabras, sin silencios largos, voz limpia a -14 LUFS, formato pedido)
  - base-palabras.json  (palabras que quedaron en el reloj nuevo de base.mp4)
  - informe.json        (mediciones reales y etapas salteadas o advertencias)
"""

from __future__ import annotations

import argparse
import colorsys
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import wave
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

# Asegurar salida UTF-8 en Windows (cp1252) y otros entornos.
for _stream in (sys.stdout, sys.stderr):
    try:
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

FORMATOS: dict[str, tuple[int, int]] = {
    "9:16": (1080, 1920),
    "1:1": (1080, 1080),
    "4:5": (1080, 1350),
    "16:9": (1920, 1080),
}

FORMATOS_TERCIOS_DEFAULT: set[str] = {"9:16", "4:5", "1:1"}

# Perfiles de aire residual al cortar silencios internos con Silero VAD.
# Nota: solo se recortan silencios muertos; nunca se borran palabras ni repeticiones expresivas.
RITMOS_SILENCIO: dict[str, dict[str, float | int]] = {
    "agil": {
        "aire_objetivo_ms": 60,
        "resguardo_post": 0.035,
        "resguardo_pre": 0.025,
        "pausa_borde": 0.0,
        "dilatacion_frames": 1,
        "min_silencio_cortable": 0.16,
        "min_ahorro": 0.08,
    },
    "normal": {
        "aire_objetivo_ms": 145,
        "resguardo_post": 0.065,
        "resguardo_pre": 0.050,
        "pausa_borde": 0.015,
        "dilatacion_frames": 2,
        "min_silencio_cortable": 0.25,
        "min_ahorro": 0.12,
    },
    "pausado": {
        "aire_objetivo_ms": 220,
        "resguardo_post": 0.095,
        "resguardo_pre": 0.075,
        "pausa_borde": 0.025,
        "dilatacion_frames": 2,
        "min_silencio_cortable": 0.35,
        "min_ahorro": 0.15,
    },
}

# URLs de respaldo si .claude/skills/setup-kit/externas.json no existiera.
URLS_MODELOS_FALLBACK: dict[str, str] = {
    "silero_vad": "https://github.com/snakers4/silero-vad/raw/v5.1.2/src/silero_vad/data/silero_vad.onnx",
    "yunet": "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
    "rnnoise": "https://github.com/GregorR/rnnoise-models/raw/master/conjoined-burgers-2018-08-28/cb.rnnn",
}

ARCHIVOS_MODELOS: dict[str, str] = {
    "silero_vad": "silero_vad.onnx",
    "yunet": "face_detection_yunet_2023mar.onnx",
    "rnnoise": "cb.rnnn",
}


@dataclass
class Tramo:
    idx_tramo: int
    pos_inicio: int
    pos_fin: int
    t_inicio: float
    t_fin: float
    palabras: list[dict[str, Any]]


@dataclass
class SubSegmento:
    idx_tramo: int
    t_inicio: float
    t_fin: float
    palabras: list[dict[str, Any]]
    q_inicio: float = 0.0
    q_fin: float = 0.0
    n_frames: int = 0
    n_samples: int = 0
    offset_salida: float = 0.0
    crop_w: int = 0
    crop_h: int = 0
    crop_x_expr: str = "0"
    crop_y_expr: str = "0"


def encontrar_raiz_repo() -> Path:
    """Encuentra la raíz del kit buscando .claude/skills/setup-kit/externas.json."""
    actual = Path(__file__).resolve()
    for padre in actual.parents:
        if (padre / ".claude" / "skills" / "setup-kit" / "externas.json").is_file():
            return padre
        if (padre / ".git").exists():
            return padre
    return Path.cwd()


def resolver_ruta(ruta_str: str, base_plan: Path, raiz_repo: Path) -> Path:
    """Resuelve rutas absolutas o relativas (con espacios o estilo Windows)."""
    p = Path(ruta_str).expanduser()
    if p.is_absolute():
        return p
    for base in (Path.cwd(), raiz_repo, base_plan):
        candidato = (base / p).resolve()
        if candidato.exists():
            return candidato
    return (Path.cwd() / p).resolve()


def verificar_ffmpeg() -> tuple[str, str]:
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        faltan = [n for n, p in (("ffmpeg", ffmpeg), ("ffprobe", ffprobe)) if not p]
        print(
            f"[ERROR] No se encontró {' ni '.join(faltan)} en el PATH.\n"
            "Instalá ffmpeg según tu sistema:\n"
            "  - macOS:   brew install ffmpeg\n"
            "  - Windows: winget install Gyan.FFmpeg\n"
            "  - Linux:   sudo apt install ffmpeg",
            file=sys.stderr,
        )
        sys.exit(1)
    return ffmpeg, ffprobe


def cargar_urls_modelos(raiz_repo: Path) -> dict[str, str]:
    urls = dict(URLS_MODELOS_FALLBACK)
    externas_path = raiz_repo / ".claude" / "skills" / "setup-kit" / "externas.json"
    if externas_path.is_file():
        try:
            data = json.loads(externas_path.read_text(encoding="utf-8"))
            modelos = data.get("modelos") or {}
            for clave in ARCHIVOS_MODELOS:
                entry = modelos.get(clave)
                if isinstance(entry, dict) and entry.get("url"):
                    urls[clave] = str(entry["url"])
        except Exception:
            pass
    return urls


def asegurar_modelo(
    clave: str,
    raiz_repo: Path,
    urls: dict[str, str],
    advertencias: list[str],
) -> Path | None:
    """Devuelve ruta al modelo en .externas/modelos/, descargándolo si falta."""
    carpeta = raiz_repo / ".externas" / "modelos"
    carpeta.mkdir(parents=True, exist_ok=True)
    destino = carpeta / ARCHIVOS_MODELOS[clave]
    if destino.is_file() and destino.stat().st_size > 1024:
        return destino

    url = urls.get(clave)
    if not url:
        advertencias.append(f"No hay URL configurada para el modelo '{clave}'.")
        return None

    print(f"[preparar] Descargando modelo '{clave}' desde {url}...", file=sys.stderr)
    tmp_path = destino.with_suffix(destino.suffix + ".tmp")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "kit-edicion-ia/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp, tmp_path.open("wb") as out:
            shutil.copyfileobj(resp, out)
        if tmp_path.stat().st_size < 1024:
            raise RuntimeError("El archivo descargado parece vacío o incompleto.")
        tmp_path.replace(destino)
        return destino
    except Exception as exc:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
        msg = f"No se pudo bajar el modelo '{clave}' ({url}): {exc}"
        print(f"[AVISO] {msg}", file=sys.stderr)
        advertencias.append(msg)
        return None


def escapar_ruta_filtro_ffmpeg(ruta: Path) -> str:
    """Escapa una ruta para opciones de filtro ffmpeg (compatible con C:\\ en Windows y espacios)."""
    s = ruta.resolve().as_posix()
    # En filtergraph de ffmpeg, ':' separa opciones y '\\' / '\'' / ',' / ';' / '[' / ']' son especiales.
    for ch in ("\\", ":", "'", ",", ";", "[", "]"):
        s = s.replace(ch, f"\\{ch}")
    return s


def inspeccionar_video(ffprobe: str, ruta: Path) -> dict[str, Any]:
    """Obtiene resolución efectiva (con rotación), fps, duración y datos de audio."""
    cmd = [
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-show_entries",
        "stream=index,codec_type,codec_name,width,height,r_frame_rate,avg_frame_rate,duration,sample_rate,channels:stream_tags=rotate:stream_side_data=rotation",
        "-of",
        "json",
        str(ruta),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe falló sobre {ruta}: {proc.stderr.strip()}")
    data = json.loads(proc.stdout or "{}")

    v_stream = None
    a_stream = None
    for st in data.get("streams", []):
        if st.get("codec_type") == "video" and v_stream is None:
            v_stream = st
        elif st.get("codec_type") == "audio" and a_stream is None:
            a_stream = st

    if v_stream is None:
        raise RuntimeError(f"El archivo no tiene pista de video: {ruta}")
    if a_stream is None:
        raise RuntimeError(f"El archivo no tiene pista de audio: {ruta}")

    w = int(v_stream["width"])
    h = int(v_stream["height"])

    # Detectar rotación en metadata (común en videos grabados con celular).
    rot = 0
    tags = v_stream.get("tags") or {}
    if "rotate" in tags:
        try:
            rot = int(float(tags["rotate"]))
        except ValueError:
            rot = 0
    for sd in v_stream.get("side_data_list") or []:
        if "rotation" in sd:
            try:
                rot = int(float(sd["rotation"]))
            except ValueError:
                pass
    if abs(rot) % 180 == 90:
        w, h = h, w

    # FPS estable para salida CFR.
    fps_num, fps_den = 30, 1
    for campo in ("avg_frame_rate", "r_frame_rate"):
        raw = v_stream.get(campo)
        if raw and "/" in raw:
            try:
                n_s, d_s = raw.split("/", 1)
                n_i, d_i = int(n_s), int(d_s)
                if d_i > 0 and n_i > 0:
                    val = n_i / d_i
                    if 10.0 <= val <= 120.0:
                        fps_num, fps_den = n_i, d_i
                        break
            except ValueError:
                pass

    fps_val = fps_num / fps_den
    # Normalizar tasas NTSC / estándar o limitar VFR raro.
    if abs(fps_val - 24000 / 1001) < 0.05:
        fps_num, fps_den = 24000, 1001
    elif abs(fps_val - 30000 / 1001) < 0.05:
        fps_num, fps_den = 30000, 1001
    elif abs(fps_val - 60000 / 1001) < 0.05:
        fps_num, fps_den = 60000, 1001
    else:
        fps_redondeado = max(24, min(60, int(round(fps_val))))
        fps_num, fps_den = fps_redondeado, 1

    dur_fmt = (data.get("format") or {}).get("duration")
    duracion_s = float(dur_fmt) if dur_fmt not in (None, "N/A", "") else 0.0
    dur_v = float(v_stream["duration"]) if v_stream.get("duration") not in (None, "N/A", "") else duracion_s
    dur_a = float(a_stream["duration"]) if a_stream.get("duration") not in (None, "N/A", "") else duracion_s

    return {
        "ancho": w,
        "alto": h,
        "fps_num": fps_num,
        "fps_den": fps_den,
        "fps_expr": f"{fps_num}/{fps_den}" if fps_den != 1 else str(fps_num),
        "fps_val": fps_num / fps_den,
        "duracion_s": duracion_s,
        "duracion_video_s": dur_v,
        "duracion_audio_s": dur_a,
        "audio_sr": int(a_stream.get("sample_rate") or 48000),
    }


def detectar_filtro_ruido(
    ffmpeg: str,
    ruta_rnnoise: Path | None,
    advertencias: list[str],
) -> tuple[str, str]:
    """Devuelve (expresion_filtro, nombre_metodo) eligiendo arnndn si está disponible o afftdn."""
    proc = subprocess.run(
        [ffmpeg, "-hide_banner", "-filters"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    filtros = proc.stdout or ""
    tiene_arnndn = re.search(r"\barnndn\b", filtros) is not None

    if tiene_arnndn and ruta_rnnoise is not None and ruta_rnnoise.is_file():
        # Verificar si esta versión de ffmpeg soporta la opción mix en arnndn.
        h_proc = subprocess.run(
            [ffmpeg, "-hide_banner", "-h", "filter=arnndn"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        soporta_mix = re.search(r"\bmix\b", (h_proc.stdout or "") + (h_proc.stderr or "")) is not None
        ruta_esc = escapar_ruta_filtro_ffmpeg(ruta_rnnoise)
        # RNNoise procesa bloques fijos de 480 muestras (10 ms a 48 kHz); sin pad previo
        # ffmpeg puede leer basura/NaN en el último frame incompleto de arnndn.
        if soporta_mix:
            return f"asetnsamples=n=480:p=1,arnndn=m='{ruta_esc}':mix=0.75", "arnndn"
        return f"asetnsamples=n=480:p=1,arnndn=m='{ruta_esc}'", "arnndn"

    if not tiene_arnndn:
        advertencias.append("Este ffmpeg no incluye el filtro arnndn; se usó afftdn para reducir ruido.")
    elif ruta_rnnoise is None:
        advertencias.append("Falta el modelo cb.rnnn para arnndn; se usó afftdn para reducir ruido.")
    return "afftdn=nf=-25", "afftdn"


def calcular_tramos_con_margenes(
    palabras: list[dict[str, Any]],
    tramos_indices: list[list[int]],
    duracion_fuente: float,
) -> list[Tramo]:
    """Convierte tramos [i_inicio, i_fin] en ventanas de tiempo respetando huecos vecinos."""
    por_indice = {int(p["i"]): pos for pos, p in enumerate(palabras)}
    tramos: list[Tramo] = []

    for idx_t, par in enumerate(tramos_indices):
        if not isinstance(par, list) or len(par) != 2:
            raise ValueError(f"Tramo #{idx_t} inválido (debe ser [inicio, fin]): {par}")
        i_ini, i_fin = int(par[0]), int(par[1])
        if i_ini not in por_indice or i_fin not in por_indice:
            raise ValueError(
                f"Tramo #{idx_t} [{i_ini}, {i_fin}] fuera de rango (hay {len(palabras)} palabras)."
            )
        pos_ini = por_indice[i_ini]
        pos_fin = por_indice[i_fin]
        if pos_ini > pos_fin:
            raise ValueError(f"Tramo #{idx_t} invertido: inicio {i_ini} > fin {i_fin}.")

        p_tramo = palabras[pos_ini : pos_fin + 1]
        w_primera = p_tramo[0]
        w_ultima = p_tramo[-1]

        # Hueco real hasta la palabra anterior para no cortar ataque ni meter media respiración.
        if pos_ini > 0:
            gap_antes = max(0.0, float(w_primera["s"]) - float(palabras[pos_ini - 1]["e"]))
        else:
            gap_antes = max(0.0, float(w_primera["s"]))
        margen_ini = min(0.085, gap_antes * (0.5 if gap_antes < 0.04 else 0.45))

        # Hueco real hasta la palabra siguiente para conservar la caída natural de la sílaba final.
        if pos_fin + 1 < len(palabras):
            gap_despues = max(0.0, float(palabras[pos_fin + 1]["s"]) - float(w_ultima["e"]))
        else:
            gap_despues = max(0.0, duracion_fuente - float(w_ultima["e"]))
        margen_fin = min(0.12, gap_despues * (0.5 if gap_despues < 0.04 else 0.45))

        t_ini = max(0.0, float(w_primera["s"]) - margen_ini)
        t_fin = min(duracion_fuente, float(w_ultima["e"]) + margen_fin)
        if t_fin <= t_ini:
            t_fin = min(duracion_fuente, t_ini + 0.05)

        tramos.append(
            Tramo(
                idx_tramo=idx_t,
                pos_inicio=pos_ini,
                pos_fin=pos_fin,
                t_inicio=t_ini,
                t_fin=t_fin,
                palabras=p_tramo,
            )
        )

    # Evitar solapamiento de márgenes si dos tramos consecutivos son adyacentes en el original.
    for k in range(len(tramos) - 1):
        a, b = tramos[k], tramos[k + 1]
        if a.pos_fin < b.pos_inicio and a.t_fin > b.t_inicio:
            mitad = 0.5 * (float(a.palabras[-1]["e"]) + float(b.palabras[0]["s"]))
            a.t_fin = min(a.t_fin, mitad)
            b.t_inicio = max(b.t_inicio, mitad)

    return tramos


class DetectorVozSileroONNX:
    """Envoltorio mínimo para Silero VAD ONNX (v5 y compatible con v4) a 16 kHz."""

    def __init__(self, ruta_modelo: Path) -> None:
        import onnxruntime as ort

        opts = ort.SessionOptions()
        opts.intra_op_num_threads = 1
        opts.inter_op_num_threads = 1
        self.session = ort.InferenceSession(
            str(ruta_modelo),
            sess_options=opts,
            providers=["CPUExecutionProvider"],
        )
        self.input_names = {i.name for i in self.session.get_inputs()}
        self.es_v5 = "state" in self.input_names

    def probabilidades_32ms(self, audio_16k: np.ndarray) -> np.ndarray:
        """Devuelve un vector con la probabilidad de voz por ventana de 512 muestras (32 ms)."""
        ventana = 512
        n_ventanas = len(audio_16k) // ventana
        if n_ventanas == 0:
            return np.zeros((0,), dtype=np.float32)

        probs = np.zeros((n_ventanas,), dtype=np.float32)
        sr = np.array(16000, dtype=np.int64)

        if self.es_v5:
            state = np.zeros((2, 1, 128), dtype=np.float32)
            context = np.zeros((1, 64), dtype=np.float32)
            for idx in range(n_ventanas):
                chunk = audio_16k[idx * ventana : (idx + 1) * ventana].reshape(1, ventana)
                inp = np.concatenate([context, chunk], axis=1).astype(np.float32)
                out, state = self.session.run(None, {"input": inp, "state": state, "sr": sr})
                probs[idx] = float(out[0][0])
                context = chunk[:, -64:]
        else:
            h = np.zeros((2, 1, 64), dtype=np.float32)
            c = np.zeros((2, 1, 64), dtype=np.float32)
            for idx in range(n_ventanas):
                chunk = audio_16k[idx * ventana : (idx + 1) * ventana].reshape(1, ventana).astype(np.float32)
                out, h, c = self.session.run(None, {"input": chunk, "h": h, "c": c, "sr": sr})
                probs[idx] = float(out[0][0])

        return probs


def extraer_audio_tramo_16k(ffmpeg: str, fuente: Path, t_ini: float, t_fin: float, tmpdir: Path, idx: int) -> np.ndarray:
    """Extrae el audio mono 16 kHz de un tramo usando búsqueda rápida previa."""
    seek_t = max(0.0, t_ini - 1.5)
    rel_ini = t_ini - seek_t
    dur = max(0.05, t_fin - t_ini)
    wav_path = tmpdir / f"vad_tramo_{idx}.wav"
    cmd = [
        ffmpeg,
        "-y",
        "-v",
        "error",
        "-ss",
        f"{seek_t:.6f}",
        "-i",
        str(fuente),
        "-ss",
        f"{rel_ini:.6f}",
        "-t",
        f"{dur:.6f}",
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(wav_path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError(f"No se pudo extraer audio para VAD en tramo {idx}: {proc.stderr.strip()}")
    with wave.open(str(wav_path), "rb") as wf:
        raw = wf.readframes(wf.getnframes())
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0


def quitar_silencios_tramos(
    tramos: list[Tramo],
    ffmpeg: str,
    fuente: Path,
    vad: DetectorVozSileroONNX | None,
    tmpdir: Path,
    ritmo: str = "normal",
) -> tuple[list[SubSegmento], dict[str, Any]]:
    """Recorta silencios internos largos según el ritmo elegido, sin cortar palabras ni repeticiones."""
    perfil = RITMOS_SILENCIO[ritmo]
    subsegmentos: list[SubSegmento] = []
    cortes_silencio = 0
    segundos_ahorrados = 0.0

    paso_s = 512 / 16000.0  # 0.032 s
    umbral_prob = 0.35
    dilatacion_frames = int(perfil["dilatacion_frames"])
    resguardo_post_palabra = float(perfil["resguardo_post"])
    resguardo_pre_palabra = float(perfil["resguardo_pre"])
    min_silencio_cortable = float(perfil["min_silencio_cortable"])
    pausa_borde_corte = float(perfil["pausa_borde"])
    min_ahorro = float(perfil["min_ahorro"])

    for tramo in tramos:
        if vad is None or len(tramo.palabras) < 2:
            subsegmentos.append(
                SubSegmento(
                    idx_tramo=tramo.idx_tramo,
                    t_inicio=tramo.t_inicio,
                    t_fin=tramo.t_fin,
                    palabras=list(tramo.palabras),
                )
            )
            continue

        audio_16k = extraer_audio_tramo_16k(ffmpeg, fuente, tramo.t_inicio, tramo.t_fin, tmpdir, tramo.idx_tramo)
        probs = vad.probabilidades_32ms(audio_16k)
        if len(probs) == 0:
            subsegmentos.append(
                SubSegmento(
                    idx_tramo=tramo.idx_tramo,
                    t_inicio=tramo.t_inicio,
                    t_fin=tramo.t_fin,
                    palabras=list(tramo.palabras),
                )
            )
            continue

        mascara_voz = probs >= umbral_prob
        # Dilatar máscara de voz para proteger inicios suaves y colas consonánticas.
        if dilatacion_frames > 0:
            dilatada = mascara_voz.copy()
            for shift in range(1, dilatacion_frames + 1):
                dilatada[shift:] |= mascara_voz[:-shift]
                dilatada[:-shift] |= mascara_voz[shift:]
            mascara_voz = dilatada

        # Buscar silencios cortables exclusivamente en los huecos entre palabras consecutivas.
        cortes: list[tuple[float, float]] = []
        for k in range(len(tramo.palabras) - 1):
            w_izq = tramo.palabras[k]
            w_der = tramo.palabras[k + 1]
            zona_ini = float(w_izq["e"]) + resguardo_post_palabra
            zona_fin = float(w_der["s"]) - resguardo_pre_palabra
            if zona_fin - zona_ini < min_silencio_cortable:
                continue

            idx_a = max(0, int(math.floor((zona_ini - tramo.t_inicio) / paso_s)))
            idx_b = min(len(mascara_voz), int(math.ceil((zona_fin - tramo.t_inicio) / paso_s)))
            if idx_b <= idx_a:
                continue

            # Encontrar rachas contiguas de silencio (False en mascara_voz).
            pos = idx_a
            while pos < idx_b:
                if mascara_voz[pos]:
                    pos += 1
                    continue
                fin_racha = pos
                while fin_racha < idx_b and not mascara_voz[fin_racha]:
                    fin_racha += 1
                sil_ini = max(zona_ini, tramo.t_inicio + pos * paso_s)
                sil_fin = min(zona_fin, tramo.t_inicio + fin_racha * paso_s)
                if sil_fin - sil_ini >= min_silencio_cortable:
                    c_ini = sil_ini + pausa_borde_corte
                    c_fin = sil_fin - pausa_borde_corte
                    if c_fin - c_ini >= min_ahorro:
                        cortes.append((c_ini, c_fin))
                        cortes_silencio += 1
                        segundos_ahorrados += c_fin - c_ini
                pos = fin_racha

        if not cortes:
            subsegmentos.append(
                SubSegmento(
                    idx_tramo=tramo.idx_tramo,
                    t_inicio=tramo.t_inicio,
                    t_fin=tramo.t_fin,
                    palabras=list(tramo.palabras),
                )
            )
            continue

        # Dividir el tramo alrededor de los cortes de silencio y asignar cada palabra a su subsegmento.
        cursor = tramo.t_inicio
        rangos: list[tuple[float, float]] = []
        for c_ini, c_fin in cortes:
            if c_ini > cursor + 0.04:
                rangos.append((cursor, c_ini))
            cursor = max(cursor, c_fin)
        if tramo.t_fin > cursor + 0.04:
            rangos.append((cursor, tramo.t_fin))

        for r_ini, r_fin in rangos:
            pals_sub = [
                p for p in tramo.palabras
                if (0.5 * (float(p["s"]) + float(p["e"]))) >= r_ini - 0.01
                and (0.5 * (float(p["s"]) + float(p["e"]))) <= r_fin + 0.01
            ]
            subsegmentos.append(
                SubSegmento(
                    idx_tramo=tramo.idx_tramo,
                    t_inicio=r_ini,
                    t_fin=r_fin,
                    palabras=pals_sub,
                )
            )

    stats = {
        "ritmo": ritmo,
        "aire_objetivo_ms": int(perfil["aire_objetivo_ms"]),
        "silencios_cortados": cortes_silencio,
        "segundos_ahorrados_silencios": round(segundos_ahorrados, 3),
    }
    return subsegmentos, stats


def cuantizar_subsegmentos(
    subsegmentos: list[SubSegmento],
    fps_val: float,
    duracion_fuente: float,
) -> tuple[list[dict[str, Any]], int, int]:
    """Cuantiza cada subsegmento a frames exactos y calcula el reloj de base-palabras.json."""
    frames_acum = 0
    palabras_base: list[dict[str, Any]] = []
    max_frame = max(1, int(math.floor(duracion_fuente * fps_val)))

    for sub in subsegmentos:
        f_ini = max(0, int(math.floor(sub.t_inicio * fps_val)))
        f_fin = min(max_frame, int(math.ceil(sub.t_fin * fps_val)))
        if f_fin <= f_ini:
            f_fin = min(max_frame, f_ini + 1)
            f_ini = max(0, f_fin - 1)

        sub.q_inicio = f_ini / fps_val
        sub.q_fin = f_fin / fps_val
        sub.n_frames = f_fin - f_ini
        dur_q = sub.n_frames / fps_val
        sub.n_samples = int(round(dur_q * 48000))
        sub.offset_salida = frames_acum / fps_val
        frames_acum += sub.n_frames

        for p in sub.palabras:
            rel_s = max(0.0, float(p["s"]) - sub.q_inicio)
            rel_e = min(dur_q, max(rel_s + 0.02, float(p["e"]) - sub.q_inicio))
            nuevo_s = sub.offset_salida + rel_s
            nuevo_e = sub.offset_salida + rel_e
            if palabras_base and nuevo_s < palabras_base[-1]["s"]:
                nuevo_s = palabras_base[-1]["s"]
            if nuevo_e <= nuevo_s:
                nuevo_e = nuevo_s + 0.02
            palabras_base.append({
                "i": len(palabras_base),
                "w": p["w"],
                "s": round(nuevo_s, 3),
                "e": round(nuevo_e, 3),
            })

    dur_total_s = frames_acum / fps_val
    total_samples = int(round(dur_total_s * 48000))
    return palabras_base, frames_acum, total_samples


def calcular_dimensiones_recorte(src_w: int, src_h: int, out_w: int, out_h: int) -> tuple[int, int, str]:
    """Devuelve (crop_w, crop_h, eje_libre) con dimensiones pares dentro del cuadro original."""
    src_ar = src_w / src_h
    dst_ar = out_w / out_h
    if abs(src_ar - dst_ar) < 0.015:
        return src_w - (src_w % 2), src_h - (src_h % 2), "ninguno"
    if src_ar > dst_ar:
        crop_h = src_h - (src_h % 2)
        crop_w = int(round(crop_h * dst_ar))
        crop_w = min(src_w, crop_w)
        crop_w -= crop_w % 2
        return max(2, crop_w), max(2, crop_h), "x"
    crop_w = src_w - (src_w % 2)
    crop_h = int(round(crop_w / dst_ar))
    crop_h = min(src_h, crop_h)
    crop_h -= crop_h % 2
    return max(2, crop_w), max(2, crop_h), "y"


def _construir_expresion_lineal_trozos(tiempos: list[float], valores: list[float], vmax: int) -> str:
    """Genera una expresión ffmpeg piecewise-linear suave evaluada en tiempo local 't'."""
    if len(tiempos) <= 1 or (max(valores) - min(valores)) < 1.5:
        val = int(round(max(0.0, min(float(vmax), float(np.median(valores))))))
        return str(val)

    # Reducir cantidad de nodos si hace falta para mantener la expresión compacta.
    max_nodos = 22
    if len(tiempos) > max_nodos:
        idxs = np.linspace(0, len(tiempos) - 1, max_nodos).round().astype(int)
        tiempos = [tiempos[i] for i in idxs]
        valores = [valores[i] for i in idxs]

    # Construir if(lt(t, t1), lerp0, if(lt(t, t2), lerp1, ..., last))
    ultimo = f"{max(0.0, min(float(vmax), valores[-1])):.2f}"
    expr = ultimo
    for k in range(len(tiempos) - 2, -1, -1):
        t0, t1 = tiempos[k], tiempos[k + 1]
        v0 = max(0.0, min(float(vmax), valores[k]))
        v1 = max(0.0, min(float(vmax), valores[k + 1]))
        dt = max(1e-4, t1 - t0)
        slope = (v1 - v0) / dt
        if abs(slope) < 1e-3:
            seg_expr = f"{v0:.2f}"
        else:
            seg_expr = f"({v0:.2f}+({slope:.4f})*(t-{t0:.4f}))"
        expr = f"if(lt(t,{t1:.4f}),{seg_expr},{expr})"
    return f"clip({expr},0,{vmax})"


def _suavizar_curva(tiempos: np.ndarray, valores: np.ndarray, sigma_s: float, vel_max: float) -> np.ndarray:
    """Filtro mediana de 3 puntos + suavizado gaussiano + tope de velocidad para evitar saltos."""
    n = len(valores)
    if n <= 2:
        return valores.copy()

    # 1. Mediana de 3 para descartar falsos positivos aislados de un solo cuadro.
    med = valores.copy()
    for i in range(1, n - 1):
        med[i] = float(np.median(valores[i - 1 : i + 2]))

    # 2. Suavizado gaussiano en el eje temporal.
    suave = np.zeros_like(med)
    for i in range(n):
        pesos = np.exp(-0.5 * ((tiempos - tiempos[i]) / max(0.05, sigma_s)) ** 2)
        suave[i] = float(np.sum(pesos * med) / np.sum(pesos))

    # 3. Limitar velocidad máxima de paneo (ida y vuelta) para que nunca haya tirones.
    acotada = suave.copy()
    for i in range(1, n):
        dt = max(0.01, float(tiempos[i] - tiempos[i - 1]))
        max_delta = vel_max * dt
        delta = acotada[i] - acotada[i - 1]
        if abs(delta) > max_delta:
            acotada[i] = acotada[i - 1] + math.copysign(max_delta, delta)
    return acotada


def _dimensiones_recorte_con_zoom(
    src_w: int,
    src_h: int,
    base_crop_w: int,
    base_crop_h: int,
    out_w: int,
    out_h: int,
    med_eye_y: float,
    zoom_max: float,
) -> tuple[int, int, float, bool]:
    """Calcula el recorte mínimo de zoom para ubicar ojos en el tercio superior (y = out_h / 3)."""
    dst_ar = out_w / float(out_h)

    # Tope de nitidez según resolución de origen:
    # - >= 1200 px (1440p/4K): nunca bajar de 1080 px reales de alto.
    # - 1080..1199 px (1080p): conservar ~1080 px (piso 960 px, ~1.125x) para mantener nitidez.
    # - < 1080 px (720p/480p): fuente menor a 1080, rige el tope zoom_max (piso 240 px).
    if base_crop_h >= 1200:
        min_h_res = 1080.0
    elif base_crop_h >= 1080:
        min_h_res = 960.0
    else:
        min_h_res = 240.0

    min_h_zoom = base_crop_h / max(1.0, zoom_max)
    min_crop_h = min(float(base_crop_h), max(min_h_zoom, min_h_res))

    # Alto máximo que permite ubicar med_eye_y exactamente en 1/3 del alto del recorte:
    #   crop_y = eye_y - crop_h/3 >= 0          => crop_h <= 3 * eye_y
    #   crop_y + crop_h = eye_y + 2/3*crop_h <= src_h => crop_h <= 1.5 * (src_h - eye_y)
    crop_h_ideal = min(float(base_crop_h), 3.0 * med_eye_y, 1.5 * (src_h - med_eye_y))
    zoom_limitado = crop_h_ideal < (min_crop_h - 1.5)
    target_h = max(min_crop_h, min(float(base_crop_h), crop_h_ideal))

    crop_h = max(2, int(round(target_h)))
    crop_h -= crop_h % 2
    crop_h = min(src_h - (src_h % 2), crop_h)

    crop_w = max(2, int(round(crop_h * dst_ar)))
    crop_w -= crop_w % 2
    if crop_w > src_w:
        crop_w = src_w - (src_w % 2)
        crop_h = max(2, int(round(crop_w / dst_ar)))
        crop_h -= crop_h % 2
        crop_h = min(src_h - (src_h % 2), crop_h)

    zoom_aplicado = round(base_crop_h / float(max(2, crop_h)), 3)
    return crop_w, crop_h, zoom_aplicado, zoom_limitado


def _armar_trayectoria_eje(
    subs: list[SubSegmento],
    arr_t: np.ndarray,
    arr_v: np.ndarray,
    span_max: int,
    deadzone_px: float,
    sigma_s: float,
    vel_max: float,
) -> tuple[list[str], np.ndarray, str]:
    """Devuelve expresiones ffmpeg por subsegmento y la serie suavizada sin saltos en el tramo."""
    if span_max <= 1:
        fijo = 0.0
        return ["0" for _ in subs], np.full_like(arr_v, fijo), "fijo"

    if float(np.ptp(arr_v)) <= deadzone_px:
        fijo = int(round(max(0.0, min(float(span_max), float(np.median(arr_v))))))
        return [str(fijo) for _ in subs], np.full_like(arr_v, float(fijo)), "fijo"

    suave = _suavizar_curva(arr_t, arr_v, sigma_s=sigma_s, vel_max=vel_max)
    suave = np.clip(suave, 0.0, float(span_max))
    exprs: list[str] = []
    for sub in subs:
        dur = sub.q_fin - sub.q_inicio
        n_knots = max(2, min(20, int(math.ceil(dur / 0.5)) + 1))
        ts_abs = np.linspace(sub.q_inicio, sub.q_fin, n_knots)
        ts_loc = (ts_abs - sub.q_inicio).tolist()
        vals_sub = np.interp(ts_abs, arr_t, suave).tolist()
        exprs.append(_construir_expresion_lineal_trozos(ts_loc, vals_sub, span_max))
    return exprs, suave, "suavizado"


def calcular_recorte_caras(
    subsegmentos: list[SubSegmento],
    fuente: Path,
    src_w: int,
    src_h: int,
    crop_w: int,
    crop_h: int,
    out_w: int,
    out_h: int,
    eje_libre: str,
    seguir_cara: bool,
    encuadre: str,
    zoom_max: float,
    ruta_yunet: Path | None,
    advertencias: list[str],
    etapas_salteadas: list[str],
) -> dict[str, Any]:
    """Calcula recorte por tramo con YuNet ONNX (ojos en tercio superior y nariz centrada en x)."""
    centro_x = (src_w - crop_w) // 2
    centro_y = (src_h - crop_h) // 2 if eje_libre != "y" else int(round((src_h - crop_h) * 0.35))
    usar_tercios = encuadre == "tercios"
    ojos_y_objetivo = round(out_h / 3.0, 1)
    tol_ojos_px = (40.0 / 1920.0) * out_h

    def _aplicar_centro_todos() -> None:
        for sub in subsegmentos:
            sub.crop_w = crop_w
            sub.crop_h = crop_h
            sub.crop_x_expr = str(centro_x)
            sub.crop_y_expr = str(centro_y)

    if eje_libre == "ninguno" and not usar_tercios:
        _aplicar_centro_todos()
        return {"modo": "sin_recorte", "estrategia": encuadre, "caras_detectadas_pct": None}

    if not seguir_cara:
        _aplicar_centro_todos()
        return {"modo": "centrado_por_plan", "estrategia": encuadre, "caras_detectadas_pct": None}

    if ruta_yunet is None:
        _aplicar_centro_todos()
        etapas_salteadas.append("seguimiento_cara: falta modelo YuNet ONNX; se usó recorte centrado.")
        return {"modo": "centrado_sin_modelo", "estrategia": encuadre, "caras_detectadas_pct": None}

    try:
        import cv2
    except ImportError as exc:
        _aplicar_centro_todos()
        msg = f"seguimiento_cara: OpenCV (cv2) no instalado ({exc}); se usó recorte centrado."
        advertencias.append(msg)
        etapas_salteadas.append(msg)
        return {"modo": "centrado_sin_opencv", "estrategia": encuadre, "caras_detectadas_pct": None}

    cap = cv2.VideoCapture(str(fuente))
    if not cap.isOpened():
        _aplicar_centro_todos()
        msg = "seguimiento_cara: OpenCV no pudo abrir el video fuente; se usó recorte centrado."
        advertencias.append(msg)
        etapas_salteadas.append(msg)
        return {"modo": "centrado_error_lectura", "estrategia": encuadre, "caras_detectadas_pct": None}

    det_w = min(src_w, 640)
    escala_det = det_w / float(src_w)
    det_h = max(64, int(round(src_h * escala_det)))
    try:
        detector = cv2.FaceDetectorYN.create(
            str(ruta_yunet),
            "",
            (det_w, det_h),
            score_threshold=0.55,
            nms_threshold=0.3,
            top_k=5000,
        )
    except Exception as exc:
        cap.release()
        _aplicar_centro_todos()
        msg = f"seguimiento_cara: falló al cargar YuNet ONNX ({exc}); se usó recorte centrado."
        advertencias.append(msg)
        etapas_salteadas.append(msg)
        return {"modo": "centrado_error_modelo", "estrategia": encuadre, "caras_detectadas_pct": None}

    # Agrupar subsegmentos por tramo original para mantener encuadre continuo dentro del mismo tramo.
    por_tramo: dict[int, list[SubSegmento]] = {}
    for sub in subsegmentos:
        por_tramo.setdefault(sub.idx_tramo, []).append(sub)

    total_muestras = 0
    muestras_con_cara = 0
    tramos_info: list[dict[str, Any]] = []
    todos_ojos_y_final: list[float] = []
    todos_nariz_x_final: list[float] = []
    zooms_aplicados: list[float] = []
    algun_zoom_limitado = False
    paso_muestra = 0.4  # ~2.5 fps

    try:
        for idx_t, subs in por_tramo.items():
            tiempos_t: list[float] = []
            nariz_x_t: list[float] = []
            ojos_y_t: list[float] = []
            cara_previa: tuple[float, float] | None = None
            muestras_tramo = 0
            detecciones_tramo = 0

            for sub in subs:
                dur = sub.q_fin - sub.q_inicio
                n_pts = max(2, int(math.ceil(dur / paso_muestra)) + 1)
                ts_muestra = np.linspace(sub.q_inicio, max(sub.q_inicio, sub.q_fin - 0.02), n_pts)
                for ts in ts_muestra:
                    cap.set(cv2.CAP_PROP_POS_MSEC, float(ts) * 1000.0)
                    ok, frame = cap.read()
                    if not ok or frame is None:
                        continue
                    muestras_tramo += 1
                    total_muestras += 1

                    fh, fw = frame.shape[:2]
                    if fw != det_w or fh != det_h:
                        chico = cv2.resize(frame, (det_w, det_h), interpolation=cv2.INTER_AREA)
                    else:
                        chico = frame
                    _, faces = detector.detect(chico)
                    if faces is None or len(faces) == 0:
                        continue

                    # Elegir cara principal (grande, confiable y cercana a la anterior del mismo tramo).
                    mejor_score = -1.0
                    mejor_datos: tuple[float, float, float, float] | None = None
                    sx = src_w / float(det_w)
                    sy = src_h / float(det_h)
                    for f in faces:
                        fx, fy, fbw, fbh = float(f[0]) * sx, float(f[1]) * sy, float(f[2]) * sx, float(f[3]) * sy
                        conf = float(f[-1])
                        if fbw <= 10 or fbh <= 10:
                            continue
                        cx = fx + 0.5 * fbw
                        cy = fy + 0.45 * fbh

                        # Landmarks de YuNet: ojos f[4..7], nariz f[8..9].
                        eye_rx, eye_ry = float(f[4]) * sx, float(f[5]) * sy
                        eye_lx, eye_ly = float(f[6]) * sx, float(f[7]) * sy
                        nose_x = float(f[8]) * sx
                        if fx <= eye_rx <= fx + fbw and fx <= eye_lx <= fx + fbw and fy <= eye_ry <= fy + fbh and fy <= eye_ly <= fy + fbh:
                            eye_y = 0.5 * (eye_ry + eye_ly)
                            eye_cx = 0.5 * (eye_rx + eye_lx)
                        else:
                            eye_y = fy + 0.36 * fbh
                            eye_cx = cx
                        if not (fx <= nose_x <= fx + fbw):
                            nose_x = eye_cx

                        area = fbw * fbh
                        score = area * (conf ** 2)
                        if cara_previa is not None:
                            dist = math.hypot(cx - cara_previa[0], cy - cara_previa[1]) / max(src_w, src_h)
                            score *= 1.0 / (1.0 + 2.5 * dist)
                        if score > mejor_score:
                            mejor_score = score
                            mejor_datos = (cx, cy, nose_x, eye_y)

                    if mejor_datos is not None:
                        cx, cy, nose_x, eye_y = mejor_datos
                        detecciones_tramo += 1
                        muestras_con_cara += 1
                        cara_previa = (cx, cy)
                        tiempos_t.append(float(ts))
                        nariz_x_t.append(nose_x)
                        ojos_y_t.append(eye_y)

            if muestras_tramo == 0 or (detecciones_tramo / max(1, muestras_tramo)) < 0.15:
                for sub in subs:
                    sub.crop_w = crop_w
                    sub.crop_h = crop_h
                    sub.crop_x_expr = str(centro_x)
                    sub.crop_y_expr = str(centro_y)
                tramos_info.append({
                    "tramo": idx_t,
                    "estrategia": "centrado_sin_cara",
                    "zoom": 1.0,
                    "detecciones": detecciones_tramo,
                    "muestras": muestras_tramo,
                })
                continue

            arr_t = np.array(tiempos_t, dtype=np.float64)
            arr_nx = np.array(nariz_x_t, dtype=np.float64)
            arr_ey = np.array(ojos_y_t, dtype=np.float64)

            if usar_tercios:
                med_ey = float(np.median(arr_ey))
                t_crop_w, t_crop_h, zoom_t, zoom_lim = _dimensiones_recorte_con_zoom(
                    src_w=src_w,
                    src_h=src_h,
                    base_crop_w=crop_w,
                    base_crop_h=crop_h,
                    out_w=out_w,
                    out_h=out_h,
                    med_eye_y=med_ey,
                    zoom_max=zoom_max,
                )
            else:
                t_crop_w, t_crop_h, zoom_t, zoom_lim = crop_w, crop_h, 1.0, False

            zooms_aplicados.append(zoom_t)
            span_x = max(0, src_w - t_crop_w)
            span_y = max(0, src_h - t_crop_h)

            arr_x = np.clip(arr_nx - 0.5 * t_crop_w, 0.0, float(span_x))
            if usar_tercios:
                arr_y = np.clip(arr_ey - (t_crop_h / 3.0), 0.0, float(span_y))
            else:
                arr_y = np.clip(arr_ey - 0.35 * t_crop_h, 0.0, float(span_y))

            exprs_x, curva_x, modo_x = _armar_trayectoria_eje(
                subs=subs,
                arr_t=arr_t,
                arr_v=arr_x,
                span_max=span_x,
                deadzone_px=max(16.0, 0.07 * t_crop_w),
                sigma_s=0.85,
                vel_max=max(25.0, 0.14 * t_crop_w),
            )
            if usar_tercios or eje_libre == "y":
                exprs_y, curva_y, modo_y = _armar_trayectoria_eje(
                    subs=subs,
                    arr_t=arr_t,
                    arr_v=arr_y,
                    span_max=span_y,
                    deadzone_px=max(8.0, 0.04 * t_crop_h),
                    sigma_s=0.9,
                    vel_max=max(18.0, 0.10 * t_crop_h),
                )
            else:
                cy_fijo = (src_h - t_crop_h) // 2
                exprs_y = [str(cy_fijo) for _ in subs]
                curva_y = np.full_like(arr_y, float(cy_fijo))
                modo_y = "fijo"

            for sub, ex, ey in zip(subs, exprs_x, exprs_y):
                sub.crop_w = t_crop_w
                sub.crop_h = t_crop_h
                sub.crop_x_expr = ex
                sub.crop_y_expr = ey

            ojos_out = ((arr_ey - curva_y) / float(t_crop_h)) * float(out_h)
            nariz_out = ((arr_nx - curva_x) / float(t_crop_w)) * float(out_w)
            ojos_y_tramo = round(float(np.median(ojos_out)), 1)
            nariz_x_tramo = round(float(np.median(nariz_out)), 1)
            todos_ojos_y_final.extend(ojos_out.tolist())
            todos_nariz_x_final.extend(nariz_out.tolist())

            if zoom_lim and abs(ojos_y_tramo - ojos_y_objetivo) > tol_ojos_px:
                algun_zoom_limitado = True
                advertencias.append(
                    f"Tramo {idx_t}: el tope de zoom ({zoom_t}x, máximo {zoom_max}x o nitidez de fuente) "
                    f"no alcanzó para llevar los ojos a y={ojos_y_objetivo:.0f}px; quedaron en y={ojos_y_tramo:.1f}px."
                )

            tramos_info.append({
                "tramo": idx_t,
                "estrategia": f"tercios_{modo_x}" if usar_tercios else f"cara_{modo_x}",
                "recorte_px": f"{t_crop_w}x{t_crop_h}",
                "zoom": zoom_t,
                "zoom_limitado": zoom_lim,
                "ojos_y_final": ojos_y_tramo,
                "nariz_x_final": nariz_x_tramo,
                "rango_x_px": round(float(np.ptp(curva_x)), 1),
                "rango_y_px": round(float(np.ptp(curva_y)), 1),
                "detecciones": detecciones_tramo,
                "muestras": muestras_tramo,
            })
    finally:
        cap.release()

    pct = round(100.0 * muestras_con_cara / max(1, total_muestras), 1)
    ojos_y_final = round(float(np.median(todos_ojos_y_final)), 1) if todos_ojos_y_final else None
    nariz_x_final = round(float(np.median(todos_nariz_x_final)), 1) if todos_nariz_x_final else None
    zoom_global = round(float(np.median(zooms_aplicados)), 3) if zooms_aplicados else 1.0

    return {
        "modo": "yunet_onnx",
        "estrategia": encuadre,
        "zoom_max_config": zoom_max,
        "zoom_aplicado": zoom_global,
        "zoom_limitado": algun_zoom_limitado,
        "ojos_y_objetivo": ojos_y_objetivo if usar_tercios else None,
        "ojos_y_final": ojos_y_final,
        "nariz_x_final": nariz_x_final,
        "caras_detectadas_pct": pct,
        "tramos": tramos_info,
    }


def _rgb_a_hex(r: float, g: float, b: float) -> str:
    ri = max(0, min(255, int(round(r * 255.0))))
    gi = max(0, min(255, int(round(g * 255.0))))
    bi = max(0, min(255, int(round(b * 255.0))))
    return f"#{ri:02X}{gi:02X}{bi:02X}"


def _hsv_a_hex(h: float, s: float, v: float) -> str:
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))
    return _rgb_a_hex(r, g, b)


def _kmeans_numpy(pixeles_rgb: np.ndarray, k: int = 8, iters: int = 20) -> tuple[np.ndarray, np.ndarray]:
    """K-means++ determinista con numpy puro sobre píxeles RGB en [0, 1]."""
    rng = np.random.default_rng(42)
    n = len(pixeles_rgb)
    k = max(1, min(k, n))

    # Inicialización k-means++ para centroides diversos y reproducibles.
    centroides = np.empty((k, 3), dtype=np.float32)
    centroides[0] = pixeles_rgb[int(rng.integers(0, n))]
    dist2 = np.sum((pixeles_rgb - centroides[0]) ** 2, axis=1)
    for c in range(1, k):
        total = float(np.sum(dist2))
        if total <= 1e-12:
            centroides[c] = pixeles_rgb[int(rng.integers(0, n))]
        else:
            probs = dist2 / total
            idx = int(rng.choice(n, p=probs))
            centroides[c] = pixeles_rgb[idx]
        d_new = np.sum((pixeles_rgb - centroides[c]) ** 2, axis=1)
        dist2 = np.minimum(dist2, d_new)

    etiquetas = np.zeros(n, dtype=np.int32)
    for _ in range(iters):
        # Distancia cuadrática [n, k]
        d = np.sum((pixeles_rgb[:, None, :] - centroides[None, :, :]) ** 2, axis=2)
        nuevas = np.argmin(d, axis=1)
        if np.array_equal(nuevas, etiquetas):
            break
        etiquetas = nuevas
        for c in range(k):
            mask = etiquetas == c
            if np.any(mask):
                centroides[c] = pixeles_rgb[mask].mean(axis=0)

    conteos = np.bincount(etiquetas, minlength=k).astype(np.float64)
    pesos = conteos / max(1.0, float(np.sum(conteos)))
    return centroides, pesos


def _es_tono_piel(h_deg: float, s: float, v: float) -> bool:
    return (8.0 <= h_deg <= 42.0) and (0.14 <= s <= 0.68) and (0.30 <= v <= 0.92)


def _distancia_hue(h1: float, h2: float) -> float:
    d = abs((h1 - h2) % 1.0)
    return min(d, 1.0 - d)


def _construir_paleta_desde_hue(
    nombre: str,
    hue: float,
    hue_fondo: float,
    sat_base: float,
) -> dict[str, str]:
    """Genera una paleta de 4 roles (acento claro vibrante, acento oscuro, blanco teñido, negro teñido)."""
    h_acento = hue % 1.0
    h_neutro = hue_fondo % 1.0
    s_claro = max(0.58, min(0.84, sat_base + 0.30))
    v_claro = 0.94
    # En amarillos/verdes lima mantener brillo alto y saturación limpia; en azules/violetas levantar luminosidad.
    h_deg = h_acento * 360.0
    if 210.0 <= h_deg <= 285.0:
        s_claro = min(s_claro, 0.68)
        v_claro = 0.96
    elif 50.0 <= h_deg <= 95.0:
        s_claro = max(0.52, min(0.74, s_claro))
        v_claro = 0.96

    s_oscuro = max(0.45, min(0.72, sat_base + 0.15))
    v_oscuro = 0.34

    return {
        "nombre": nombre,
        "acento_claro": _hsv_a_hex(h_acento, s_claro, v_claro),
        "acento_oscuro": _hsv_a_hex((h_acento + 0.02) % 1.0, s_oscuro, v_oscuro),
        "blanco_tenido": _hsv_a_hex(h_acento, 0.05, 0.96),
        "negro_tenido": _hsv_a_hex(h_neutro, 0.22, 0.09),
    }


def extraer_paletas_aroll(
    fuente: Path,
    subsegmentos: list[SubSegmento],
    advertencias: list[str],
    etapas_salteadas: list[str],
) -> tuple[list[dict[str, str]], list[str]]:
    """Extrae 3 paletas candidatas de 4 colores del A-roll usando k-means con numpy."""
    try:
        import cv2
    except ImportError:
        etapas_salteadas.append("paletas_aroll: falta OpenCV (cv2) para muestrear cuadros.")
        return [], []

    cap = cv2.VideoCapture(str(fuente))
    if not cap.isOpened():
        advertencias.append("paletas_aroll: no se pudo abrir el video fuente para extraer colores.")
        return [], []

    muestras_rgb: list[np.ndarray] = []
    try:
        # Muestrear hasta 9 cuadros repartidos entre todos los subsegmentos.
        ts_objetivo: list[float] = []
        n_por_sub = max(2, int(math.ceil(9 / max(1, len(subsegmentos)))))
        for sub in subsegmentos:
            dur = max(0.05, sub.q_fin - sub.q_inicio)
            pts = np.linspace(sub.q_inicio + 0.12 * dur, sub.q_fin - 0.12 * dur, n_por_sub)
            ts_objetivo.extend(pts.tolist())
        if len(ts_objetivo) > 9:
            idxs = np.linspace(0, len(ts_objetivo) - 1, 9).round().astype(int)
            ts_objetivo = [ts_objetivo[i] for i in idxs]

        for ts in ts_objetivo:
            cap.set(cv2.CAP_PROP_POS_MSEC, float(ts) * 1000.0)
            ok, frame = cap.read()
            if not ok or frame is None:
                continue
            chico = cv2.resize(frame, (128, 72), interpolation=cv2.INTER_AREA)
            rgb = cv2.cvtColor(chico, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
            muestras_rgb.append(rgb.reshape(-1, 3))
    finally:
        cap.release()

    if not muestras_rgb:
        advertencias.append("paletas_aroll: no se pudieron leer cuadros limpios del A-roll.")
        return [], []

    pixeles = np.concatenate(muestras_rgb, axis=0)
    # Submuestrear determinísticamente hasta 24000 píxeles para que corra en ~15 ms.
    if len(pixeles) > 24000:
        paso = max(1, len(pixeles) // 24000)
        pixeles = pixeles[::paso]

    centroides, pesos = _kmeans_numpy(pixeles, k=8, iters=20)
    orden_peso = np.argsort(-pesos)

    colores_crudos: list[str] = []
    clusters_info: list[dict[str, Any]] = []
    for idx in orden_peso:
        r, g, b = [float(x) for x in centroides[idx]]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        hex_c = _rgb_a_hex(r, g, b)
        if len(colores_crudos) < 4:
            colores_crudos.append(hex_c)
        clusters_info.append({
            "hex": hex_c,
            "peso": float(pesos[idx]),
            "h": h,
            "s": s,
            "v": v,
            "piel": _es_tono_piel(h * 360.0, s, v),
            "score": float(pesos[idx]) * (0.20 + (s ** 1.25)) * (0.35 + 0.65 * v),
        })

    # Tinte del fondo (cluster oscuro/dominante no-piel con mayor peso).
    fondo_cands = [c for c in clusters_info if not c["piel"] and c["v"] < 0.55]
    if not fondo_cands:
        fondo_cands = clusters_info
    hue_fondo = fondo_cands[0]["h"] if fondo_cands[0]["s"] >= 0.08 else 0.58

    # 1) Dominante del plano (mejor cluster no-piel con algo de croma).
    no_piel = sorted(
        [c for c in clusters_info if not c["piel"] and c["s"] >= 0.10],
        key=lambda c: -c["score"],
    )
    if no_piel:
        h_dom = no_piel[0]["h"]
        s_dom = no_piel[0]["s"]
    else:
        h_dom = hue_fondo
        s_dom = 0.45

    # 2) Secundario del plano (otro tono presente en escena/ropa/piel separado >= 35° del dominante).
    sec_cands = sorted(
        [c for c in clusters_info if c["s"] >= 0.12 and _distancia_hue(c["h"], h_dom) >= (35.0 / 360.0)],
        key=lambda c: -c["score"],
    )
    if sec_cands:
        h_sec = sec_cands[0]["h"]
        s_sec = sec_cands[0]["s"]
        nombre_sec = "Calidez del plano" if sec_cands[0]["piel"] or (0.04 <= h_sec <= 0.16) else "Secundaria del plano"
    else:
        # Análogo cálido si la toma es monocromática.
        h_sec = (h_dom + 0.12) % 1.0
        s_sec = 0.55
        nombre_sec = "Análoga editorial"

    # 3) Contraste complementario (opuesto al fondo dominante, evitando pisar los dos anteriores).
    h_comp = (hue_fondo + 0.50) % 1.0
    if _distancia_hue(h_comp, h_sec) < (30.0 / 360.0):
        # Girar a complementario dividido (ej. amarillo-lima o coral vibrante).
        h_comp = (hue_fondo + 0.38) % 1.0
        if _distancia_hue(h_comp, h_dom) < (30.0 / 360.0) or _distancia_hue(h_comp, h_sec) < (30.0 / 360.0):
            h_comp = (hue_fondo + 0.62) % 1.0

    paletas = [
        _construir_paleta_desde_hue("Dominante del plano", h_dom, hue_fondo, s_dom),
        _construir_paleta_desde_hue(nombre_sec, h_sec, hue_fondo, s_sec),
        _construir_paleta_desde_hue("Contraste editorial", h_comp, hue_fondo, 0.62),
    ]
    return paletas, colores_crudos


def parsear_json_loudnorm(stderr_texto: str) -> dict[str, Any] | None:
    """Extrae el bloque JSON que imprime ffmpeg loudnorm=print_format=json en stderr."""
    # Buscar el último objeto JSON con input_i.
    matches = list(re.finditer(r"\{[^{}]*\"input_i\"[^{}]*\}", stderr_texto, flags=re.DOTALL))
    if not matches:
        return None
    try:
        return json.loads(matches[-1].group(0))
    except json.JSONDecodeError:
        return None


def construir_filtros_corte_y_limpieza(
    subsegmentos: list[SubSegmento],
    info_src: dict[str, Any],
    crop_w: int,
    crop_h: int,
    out_w: int,
    out_h: int,
    filtro_ruido: str,
    solo_audio: bool,
) -> tuple[list[str], str]:
    """Construye entradas ffmpeg (-ss/-i por tramo) y el filtergraph hasta [vout] y [aclean]."""
    # Agrupar subsegmentos por tramo para abrir solo una entrada por tramo (búsqueda rápida).
    grupos: list[tuple[int, list[SubSegmento]]] = []
    por_tramo_orden: dict[int, list[SubSegmento]] = {}
    for sub in subsegmentos:
        if sub.idx_tramo not in por_tramo_orden:
            por_tramo_orden[sub.idx_tramo] = []
            grupos.append((sub.idx_tramo, por_tramo_orden[sub.idx_tramo]))
        por_tramo_orden[sub.idx_tramo].append(sub)

    input_args: list[str] = []
    lineas: list[str] = []
    v_labels: list[str] = []
    a_labels: list[str] = []
    fps_expr = info_src["fps_expr"]

    seg_global = 0
    for inp_idx, (_, subs) in enumerate(grupos):
        primer_q = min(s.q_inicio for s in subs)
        ultimo_q = max(s.q_fin for s in subs)
        # Pre-seek 2 s antes para que ffmpeg alinee bien keyframes y preroll de Opus/AAC.
        seek_t = max(0.0, primer_q - 2.0)
        # Acotar duración de lectura de esta entrada para no decodificar el resto del archivo.
        t_lectura = (ultimo_q - seek_t) + 1.5
        input_args.extend(["-ss", f"{seek_t:.6f}", "-t", f"{t_lectura:.6f}"])
        # Marcador de ruta de entrada (lo completará el llamador con fuente).
        input_args.append("__FUENTE__")

        m = len(subs)
        if not solo_audio:
            if m == 1:
                lineas.append(f"[{inp_idx}:v]fps={fps_expr}[vpre_{inp_idx}_0]")
            else:
                outs_v = "".join(f"[vpre_{inp_idx}_{k}]" for k in range(m))
                lineas.append(f"[{inp_idx}:v]fps={fps_expr},split={m}{outs_v}")

        if m == 1:
            lineas.append(f"[{inp_idx}:a]aresample=48000,aformat=channel_layouts=stereo[apre_{inp_idx}_0]")
        else:
            outs_a = "".join(f"[apre_{inp_idx}_{k}]" for k in range(m))
            lineas.append(f"[{inp_idx}:a]aresample=48000,aformat=channel_layouts=stereo,asplit={m}{outs_a}")

        for k, sub in enumerate(subs):
            rel_s = max(0.0, sub.q_inicio - seek_t)
            rel_e = max(rel_s + 0.01, sub.q_fin - seek_t)
            dur_q = sub.n_frames / info_src["fps_val"]

            if not solo_audio:
                v_lbl = f"vseg_{seg_global}"
                sub_cw = sub.crop_w if sub.crop_w > 0 else crop_w
                sub_ch = sub.crop_h if sub.crop_h > 0 else crop_h
                crop_part = f"crop={sub_cw}:{sub_ch}:'{sub.crop_x_expr}':'{sub.crop_y_expr}'"
                scale_part = f"scale={out_w}:{out_h}:flags=lanczos,setsar=1"
                lineas.append(
                    f"[vpre_{inp_idx}_{k}]"
                    f"trim=start={rel_s:.6f}:end={rel_e:.6f},"
                    f"setpts=PTS-STARTPTS,"
                    f"tpad=stop_mode=clone:stop_duration=0.25,"
                    f"trim=end_frame={sub.n_frames},"
                    f"{crop_part},{scale_part}[{v_lbl}]"
                )
                v_labels.append(f"[{v_lbl}]")

            a_lbl = f"aseg_{seg_global}"
            fade_part = ""
            if dur_q >= 0.04:
                fade_d = 0.008
                fade_out_st = max(0.0, dur_q - fade_d)
                fade_part = f",afade=t=in:st=0:d={fade_d:.4f},afade=t=out:st={fade_out_st:.6f}:d={fade_d:.4f}"
            lineas.append(
                f"[apre_{inp_idx}_{k}]"
                f"atrim=start={rel_s:.6f}:end={rel_e:.6f},"
                f"asetpts=PTS-STARTPTS,"
                f"apad=whole_len={sub.n_samples},"
                f"atrim=end_sample={sub.n_samples}"
                f"{fade_part}[{a_lbl}]"
            )
            a_labels.append(f"[{a_lbl}]")
            seg_global += 1

    n_segs = len(a_labels)
    if not solo_audio:
        if n_segs == 1:
            lineas.append(f"{v_labels[0]}copy[vout]")
        else:
            lineas.append(f"{''.join(v_labels)}concat=n={n_segs}:v=1:a=0[vout]")

    if n_segs == 1:
        lineas.append(f"{a_labels[0]}highpass=f=80:poles=2,{filtro_ruido}[aclean]")
    else:
        lineas.append(
            f"{''.join(a_labels)}concat=n={n_segs}:v=0:a=1,"
            f"highpass=f=80:poles=2,{filtro_ruido}[aclean]"
        )

    return input_args, ";\n".join(lineas)


def reemplazar_fuente_en_args(input_args: list[str], fuente: Path) -> list[str]:
    out: list[str] = []
    for item in input_args:
        if item == "__FUENTE__":
            out.extend(["-i", str(fuente)])
        else:
            out.append(item)
    return out


def args_filter_complex(ffmpeg: str, fg_texto: str, ruta_script: Path) -> list[str]:
    """Devuelve flags de filter_complex compatibles con FFmpeg 4–9 y límites de línea en Windows."""
    if len(fg_texto) < 6000:
        return ["-filter_complex", fg_texto]
    ruta_script.write_text(fg_texto, encoding="utf-8")
    proc = subprocess.run(
        [ffmpeg, "-hide_banner", "-h", "long"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if "-filter_complex_script" in (proc.stdout or ""):
        return ["-filter_complex_script", str(ruta_script)]
    return ["-/filter_complex", str(ruta_script)]


def medir_audio_final(ffmpeg: str, ruta_mp4: Path) -> dict[str, Any]:
    """Mide LUFS integrado y pico real (dBTP) exactos del base.mp4 ya codificado."""
    cmd = [
        ffmpeg,
        "-hide_banner",
        "-i",
        str(ruta_mp4),
        "-vn",
        "-af",
        "loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json",
        "-f",
        "null",
        "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    stats = parsear_json_loudnorm(proc.stderr or "")
    if not stats:
        return {"lufs_integrado": None, "pico_real_dbtp": None, "lra_lu": None}

    def _f(clave: str) -> float | None:
        try:
            v = float(stats[clave])
            return round(v, 2) if math.isfinite(v) else None
        except Exception:
            return None

    return {
        "lufs_integrado": _f("input_i"),
        "pico_real_dbtp": _f("input_tp"),
        "lra_lu": _f("input_lra"),
    }


def parsear_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepara base.mp4, base-palabras.json e informe.json desde un plan.json."
    )
    parser.add_argument("plan", help="Ruta al archivo plan.json del contrato.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    t0 = time.monotonic()
    args = parsear_args(argv)

    raiz_repo = encontrar_raiz_repo()
    ruta_plan = Path(args.plan).expanduser().resolve()
    if not ruta_plan.is_file():
        print(f"[ERROR] No existe el plan: {ruta_plan}", file=sys.stderr)
        return 1

    try:
        plan = json.loads(ruta_plan.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[ERROR] plan.json no es JSON válido: {exc}", file=sys.stderr)
        return 1

    for campo in ("fuente", "palabras", "tramos", "salida"):
        if campo not in plan:
            print(f"[ERROR] Falta el campo obligatorio '{campo}' en plan.json.", file=sys.stderr)
            return 1

    fuente = resolver_ruta(str(plan["fuente"]), ruta_plan.parent, raiz_repo)
    ruta_palabras = resolver_ruta(str(plan["palabras"]), ruta_plan.parent, raiz_repo)
    salida = Path(str(plan["salida"])).expanduser()
    if not salida.is_absolute():
        salida = (Path.cwd() / salida).resolve()
    salida.mkdir(parents=True, exist_ok=True)

    formato = str(plan.get("formato", "9:16")).strip()
    if formato not in FORMATOS:
        print(
            f"[ERROR] Formato '{formato}' no soportado. Elegí uno de: {', '.join(FORMATOS)}",
            file=sys.stderr,
        )
        return 1
    out_w, out_h = FORMATOS[formato]

    seguir_cara = bool(plan.get("seguir_cara", True))
    sacar_silencios = bool(plan.get("sacar_silencios", True))

    encuadre_default = "tercios" if formato in FORMATOS_TERCIOS_DEFAULT else "centrado"
    encuadre = str(plan.get("encuadre", encuadre_default)).strip().lower()
    if encuadre not in ("tercios", "centrado"):
        print(
            f"[ERROR] 'encuadre' inválido: '{encuadre}'. Elegí 'tercios' o 'centrado'.",
            file=sys.stderr,
        )
        return 1

    try:
        zoom_max = float(plan.get("zoom_max", 1.35))
        if not math.isfinite(zoom_max) or zoom_max < 1.0:
            raise ValueError("zoom_max debe ser >= 1.0")
    except Exception as exc:
        print(f"[ERROR] 'zoom_max' inválido: {exc}", file=sys.stderr)
        return 1

    ritmo_raw = str(plan.get("ritmo", "normal")).strip().lower()
    ritmo = "agil" if ritmo_raw == "ágil" else ritmo_raw
    if ritmo not in RITMOS_SILENCIO:
        print(
            f"[ERROR] 'ritmo' inválido: '{ritmo_raw}'. Elegí 'agil', 'normal' o 'pausado'.",
            file=sys.stderr,
        )
        return 1

    tramos_indices = plan["tramos"]
    if not isinstance(tramos_indices, list) or not tramos_indices:
        print("[ERROR] 'tramos' debe ser una lista no vacía de pares [inicio, fin].", file=sys.stderr)
        return 1

    if not fuente.is_file():
        print(f"[ERROR] No existe el video fuente: {fuente}", file=sys.stderr)
        return 1
    if not ruta_palabras.is_file():
        print(f"[ERROR] No existe palabras.json: {ruta_palabras}", file=sys.stderr)
        return 1

    palabras = json.loads(ruta_palabras.read_text(encoding="utf-8"))
    if not isinstance(palabras, list) or not palabras:
        print("[ERROR] palabras.json está vacío o tiene formato inválido.", file=sys.stderr)
        return 1

    ffmpeg, ffprobe = verificar_ffmpeg()
    info_src = inspeccionar_video(ffprobe, fuente)
    urls_modelos = cargar_urls_modelos(raiz_repo)

    advertencias: list[str] = []
    etapas_salteadas: list[str] = []

    print(
        f"[preparar] Fuente: {fuente.name} ({info_src['ancho']}x{info_src['alto']} @ "
        f"{info_src['fps_expr']} fps) -> {formato} ({out_w}x{out_h})",
        file=sys.stderr,
    )

    # 1. Cortar por palabras respetando huecos vecinos.
    tramos = calcular_tramos_con_margenes(palabras, tramos_indices, info_src["duracion_s"])

    # 2. Silencios internos con Silero VAD ONNX.
    vad_detector: DetectorVozSileroONNX | None = None
    if sacar_silencios:
        ruta_vad = asegurar_modelo("silero_vad", raiz_repo, urls_modelos, advertencias)
        if ruta_vad is None:
            etapas_salteadas.append("sacar_silencios: falta modelo silero_vad.onnx.")
        else:
            try:
                vad_detector = DetectorVozSileroONNX(ruta_vad)
            except Exception as exc:
                msg = f"sacar_silencios: no se pudo iniciar Silero VAD ONNX ({exc})."
                advertencias.append(msg)
                etapas_salteadas.append(msg)

    with tempfile.TemporaryDirectory(prefix="kit_preparar_") as tmpdir_str:
        tmpdir = Path(tmpdir_str)

        subsegmentos, stats_silencios = quitar_silencios_tramos(
            tramos=tramos,
            ffmpeg=ffmpeg,
            fuente=fuente,
            vad=vad_detector,
            tmpdir=tmpdir,
            ritmo=ritmo,
        )

        # 3. Cuantizar a frames exactos y construir base-palabras.json.
        palabras_base, total_frames, total_samples = cuantizar_subsegmentos(
            subsegmentos=subsegmentos,
            fps_val=info_src["fps_val"],
            duracion_fuente=info_src["duracion_s"],
        )

        # 4. Recorte / seguimiento de cara con YuNet ONNX (ojos en tercio superior).
        crop_w, crop_h, eje_libre = calcular_dimensiones_recorte(
            info_src["ancho"], info_src["alto"], out_w, out_h
        )
        ruta_yunet = None
        if seguir_cara and (eje_libre != "ninguno" or encuadre == "tercios"):
            ruta_yunet = asegurar_modelo("yunet", raiz_repo, urls_modelos, advertencias)

        info_cara = calcular_recorte_caras(
            subsegmentos=subsegmentos,
            fuente=fuente,
            src_w=info_src["ancho"],
            src_h=info_src["alto"],
            crop_w=crop_w,
            crop_h=crop_h,
            out_w=out_w,
            out_h=out_h,
            eje_libre=eje_libre,
            seguir_cara=seguir_cara,
            encuadre=encuadre,
            zoom_max=zoom_max,
            ruta_yunet=ruta_yunet,
            advertencias=advertencias,
            etapas_salteadas=etapas_salteadas,
        )

        # 4b. Extracción de paletas candidatas del A-roll (k-means con numpy).
        paletas_aroll, colores_crudos = extraer_paletas_aroll(
            fuente=fuente,
            subsegmentos=subsegmentos,
            advertencias=advertencias,
            etapas_salteadas=etapas_salteadas,
        )

        # 5. Limpieza de voz (arnndn si está disponible, si no afftdn) + loudnorm de dos pasadas.
        ruta_rnnoise = asegurar_modelo("rnnoise", raiz_repo, urls_modelos, advertencias)
        filtro_ruido, metodo_ruido = detectar_filtro_ruido(ffmpeg, ruta_rnnoise, advertencias)

        # Pasada 1 de loudnorm: solo audio (rápida, sin decodificar video).
        in_args_p1, fg_p1_base = construir_filtros_corte_y_limpieza(
            subsegmentos=subsegmentos,
            info_src=info_src,
            crop_w=crop_w,
            crop_h=crop_h,
            out_w=out_w,
            out_h=out_h,
            filtro_ruido=filtro_ruido,
            solo_audio=True,
        )
        # Apuntamos TP=-1.5 en loudnorm para compensar el leve overshoot de AAC (+0.1 a +0.3 dBTP)
        # y garantizar que el pico real medido de base.mp4 quede <= -1.0 dBTP.
        tp_objetivo_filtro = -1.5
        fg_p1 = fg_p1_base + f";\n[aclean]loudnorm=I=-14:TP={tp_objetivo_filtro}:LRA=11:print_format=json[anull]"
        script_p1 = tmpdir / "fg_pass1.txt"

        cmd_p1 = [
            ffmpeg,
            "-hide_banner",
            "-y",
            *reemplazar_fuente_en_args(in_args_p1, fuente),
            *args_filter_complex(ffmpeg, fg_p1, script_p1),
            "-map",
            "[anull]",
            "-vn",
            "-f",
            "null",
            "-",
        ]
        print("[preparar] Pasada 1 de loudnorm (medición de audio)...", file=sys.stderr)
        proc_p1 = subprocess.run(cmd_p1, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if proc_p1.returncode != 0:
            print(f"[ERROR] Falló la pasada 1 de audio en ffmpeg:\n{proc_p1.stderr[-2000:]}", file=sys.stderr)
            return 1

        ln_stats = parsear_json_loudnorm(proc_p1.stderr or "")
        dos_pasadas_ok = False
        if ln_stats:
            try:
                vals = [
                    float(ln_stats["input_i"]),
                    float(ln_stats["input_tp"]),
                    float(ln_stats["input_lra"]),
                    float(ln_stats["input_thresh"]),
                    float(ln_stats["target_offset"]),
                ]
                dos_pasadas_ok = all(math.isfinite(v) for v in vals)
            except Exception:
                dos_pasadas_ok = False

        if dos_pasadas_ok and ln_stats is not None:
            filtro_ln = (
                f"loudnorm=I=-14:TP={tp_objetivo_filtro}:LRA=11:"
                f"measured_I={ln_stats['input_i']}:"
                f"measured_TP={ln_stats['input_tp']}:"
                f"measured_LRA={ln_stats['input_lra']}:"
                f"measured_thresh={ln_stats['input_thresh']}:"
                f"offset={ln_stats['target_offset']}:"
                f"linear=true:print_format=json"
            )
        else:
            advertencias.append(
                "La medición de pasada 1 de loudnorm devolvió valores no finitos; se usó loudnorm de una pasada."
            )
            filtro_ln = f"loudnorm=I=-14:TP={tp_objetivo_filtro}:LRA=11:print_format=json"

        # 6. Pasada única de video + pasada 2 de loudnorm -> base.mp4 (sin re-encodear dos veces).
        in_args_p2, fg_p2_base = construir_filtros_corte_y_limpieza(
            subsegmentos=subsegmentos,
            info_src=info_src,
            crop_w=crop_w,
            crop_h=crop_h,
            out_w=out_w,
            out_h=out_h,
            filtro_ruido=filtro_ruido,
            solo_audio=False,
        )
        fg_p2 = (
            fg_p2_base
            + f";\n[aclean]{filtro_ln},aresample=48000,asetpts=PTS-STARTPTS,aformat=sample_fmts=s32,"
            f"apad=whole_len={total_samples},atrim=end_sample={total_samples}[aout]"
        )
        script_p2 = tmpdir / "fg_pass2.txt"

        ruta_base_mp4 = salida / "base.mp4"
        cmd_p2 = [
            ffmpeg,
            "-hide_banner",
            "-y",
            *reemplazar_fuente_en_args(in_args_p2, fuente),
            *args_filter_complex(ffmpeg, fg_p2, script_p2),
            "-map",
            "[vout]",
            "-map",
            "[aout]",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-shortest",
            "-movflags",
            "+faststart",
            str(ruta_base_mp4),
        ]
        print("[preparar] Renderizando base.mp4 (pasada única de video + loudnorm pasada 2)...", file=sys.stderr)
        proc_p2 = subprocess.run(cmd_p2, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if proc_p2.returncode != 0:
            print(f"[ERROR] Falló el render de base.mp4 en ffmpeg:\n{proc_p2.stderr[-2500:]}", file=sys.stderr)
            return 1

    # 7. Medir el resultado real de base.mp4 y escribir base-palabras.json e informe.json.
    info_out = inspeccionar_video(ffprobe, ruta_base_mp4)
    medicion_audio = medir_audio_final(ffmpeg, ruta_base_mp4)
    dif_av_ms = round(abs(info_out["duracion_video_s"] - info_out["duracion_audio_s"]) * 1000.0, 1)

    ruta_base_palabras = salida / "base-palabras.json"
    ruta_base_palabras.write_text(
        json.dumps(palabras_base, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    tiempo_s = round(time.monotonic() - t0, 2)
    informe = {
        "fuente": str(fuente),
        "salida": str(ruta_base_mp4),
        "formato": formato,
        "resolucion": f"{info_out['ancho']}x{info_out['alto']}",
        "fps": info_out["fps_expr"],
        "tramos_pedidos": tramos_indices,
        "subsegmentos_finales": len(subsegmentos),
        "palabras_finales": len(palabras_base),
        "duracion_video_s": round(info_out["duracion_video_s"], 3),
        "duracion_audio_s": round(info_out["duracion_audio_s"], 3),
        "diferencia_av_ms": dif_av_ms,
        "silencios": {
            "activo": bool(sacar_silencios and vad_detector is not None),
            **stats_silencios,
        },
        "audio": {
            "ruido": metodo_ruido,
            "paso_alto_hz": 80,
            "loudnorm_dos_pasadas": dos_pasadas_ok,
            **medicion_audio,
        },
        "encuadre": {
            "seguir_cara_pedido": seguir_cara,
            "recorte_origen": f"{crop_w}x{crop_h}",
            **info_cara,
        },
        "paletas": paletas_aroll,
        "colores_crudos_dominantes": colores_crudos,
        "etapas_salteadas": etapas_salteadas,
        "advertencias": advertencias,
        "tiempo_proceso_s": tiempo_s,
    }
    ruta_informe = salida / "informe.json"
    ruta_informe.write_text(
        json.dumps(informe, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        f"[preparar] Listo en {tiempo_s:.1f}s | {info_out['duracion_video_s']:.2f}s "
        f"(A/V Δ={dif_av_ms}ms) | {medicion_audio['lufs_integrado']} LUFS, "
        f"pico {medicion_audio['pico_real_dbtp']} dBTP | ruido={metodo_ruido} -> {ruta_base_mp4}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Transcribe audio o video con alineación palabra por palabra (WhisperX).

Genera los 4 archivos del contrato en la carpeta de salida:
  - palabras.json  ([{"i": 0, "w": "...", "s": 0.12, "e": 0.34}, ...])
  - texto.txt      ([mm:ss] (#idx) frase...)
  - subtitulos.srt
  - info.json      ({"fuente", "idioma", "modelo", "duracion_s", ...})

Si WhisperX no está disponible, usa faster-whisper con word_timestamps=True
como camino alternativo (menos preciso) y deja constancia en info.json y stderr.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
import wave
from pathlib import Path
from typing import Any

# Asegurar salida UTF-8 en Windows (cp1252) y otros entornos.
for _stream in (sys.stdout, sys.stderr):
    try:
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def verificar_ffmpeg() -> tuple[str, str]:
    """Devuelve rutas a ffmpeg y ffprobe o aborta con instrucciones claras."""
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


def obtener_info_media(ffprobe: str, entrada: Path) -> tuple[float, bool]:
    """Devuelve (duracion_s, tiene_audio) usando ffprobe."""
    cmd = [
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-show_entries",
        "stream=codec_type,duration",
        "-of",
        "json",
        str(entrada),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe falló sobre {entrada}: {proc.stderr.strip()}")
    data = json.loads(proc.stdout or "{}")
    streams = data.get("streams", [])
    tiene_audio = any(s.get("codec_type") == "audio" for s in streams)

    duracion = None
    fmt_dur = (data.get("format") or {}).get("duration")
    if fmt_dur not in (None, "N/A", ""):
        try:
            duracion = float(fmt_dur)
        except ValueError:
            duracion = None
    if duracion is None:
        for s in streams:
            sd = s.get("duration")
            if sd not in (None, "N/A", ""):
                try:
                    duracion = float(sd)
                    break
                except ValueError:
                    pass
    if duracion is None or not math.isfinite(duracion):
        duracion = 0.0
    return duracion, tiene_audio


def extraer_wav_16k(ffmpeg: str, entrada: Path, destino_wav: Path) -> None:
    """Extrae audio mono 16 kHz PCM 16-bit para lectura uniforme en cualquier OS."""
    cmd = [
        ffmpeg,
        "-y",
        "-v",
        "error",
        "-i",
        str(entrada),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(destino_wav),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg no pudo extraer el audio de {entrada}: {proc.stderr.strip()}")


def leer_wav_float32(ruta_wav: Path):
    """Lee un WAV mono PCM 16-bit como arreglo numpy float32 normalizado en [-1, 1]."""
    import numpy as np

    with wave.open(str(ruta_wav), "rb") as wf:
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
            raise RuntimeError("El WAV temporal no tiene formato mono 16 kHz 16-bit.")
        frames = wf.readframes(wf.getnframes())
    audio = np.frombuffer(frames, dtype="<i2").astype(np.float32) / 32768.0
    return audio


def detectar_hardware(dispositivo_pedido: str) -> dict[str, Any]:
    """Detecta CUDA, Apple Silicon o CPU genérica y elige defaults razonables."""
    sistema = platform.system()
    maquina = platform.machine().lower()
    es_apple_silicon = sistema == "Darwin" and maquina in ("arm64", "aarch64")

    tiene_cuda = False
    try:
        import torch

        tiene_cuda = bool(torch.cuda.is_available())
    except Exception:
        tiene_cuda = False

    if dispositivo_pedido == "cuda":
        if not tiene_cuda:
            print("[AVISO] Se pidió --dispositivo cuda pero no hay CUDA disponible; usando CPU.", file=sys.stderr)
            dispositivo_pedido = "cpu"

    if dispositivo_pedido == "cuda" or (dispositivo_pedido == "auto" and tiene_cuda):
        return {
            "etiqueta": "cuda",
            "ct2_device": "cuda",
            "align_device": "cuda",
            "compute_type": "float16",
            "modelo_default": "large-v3-turbo",
            "batch_size_default": 16,
        }

    if es_apple_silicon and dispositivo_pedido == "auto":
        # CTranslate2 no usa MPS directo: corre muy rápido en CPU con AMX/Accelerate.
        # Para wav2vec2 en PyTorch usamos CPU por estabilidad (MPS falla en algunas ops de torchaudio).
        return {
            "etiqueta": "apple-silicon-cpu",
            "ct2_device": "cpu",
            "align_device": "cpu",
            "compute_type": "int8",
            "modelo_default": "medium",
            "batch_size_default": 8,
        }

    return {
        "etiqueta": "cpu",
        "ct2_device": "cpu",
        "align_device": "cpu",
        "compute_type": "int8",
        "modelo_default": "small",
        "batch_size_default": 4,
    }


def normalizar_palabras(
    palabras_crudas: list[dict[str, Any]],
    duracion_s: float,
) -> list[dict[str, Any]]:
    """Garantiza índices secuenciales, tiempos válidos, finitos y monotónicos."""
    limpias: list[dict[str, Any]] = []
    for item in palabras_crudas:
        w = str(item.get("w", "")).strip()
        if not w:
            continue
        s = item.get("s")
        e = item.get("e")
        s_val = float(s) if s is not None and math.isfinite(float(s)) else None
        e_val = float(e) if e is not None and math.isfinite(float(e)) else None
        limpias.append({
            "w": w,
            "s": s_val,
            "e": e_val,
            "seg_s": item.get("seg_s"),
            "seg_e": item.get("seg_e"),
        })

    # Rellenar tiempos faltantes (p.ej. números o símbolos que wav2vec2 no alinea).
    n = len(limpias)
    idx = 0
    while idx < n:
        if limpias[idx]["s"] is not None and limpias[idx]["e"] is not None:
            idx += 1
            continue
        j = idx
        while j < n and (limpias[j]["s"] is None or limpias[j]["e"] is None):
            j += 1

        # Borde izquierdo
        left = 0.0
        if idx > 0 and limpias[idx - 1]["e"] is not None:
            left = limpias[idx - 1]["e"]
        elif limpias[idx]["seg_s"] is not None:
            left = float(limpias[idx]["seg_s"])

        # Borde derecho
        right = None
        if j < n and limpias[j]["s"] is not None:
            right = limpias[j]["s"]
        elif limpias[j - 1]["seg_e"] is not None:
            right = float(limpias[j - 1]["seg_e"])
        elif duracion_s > left:
            right = duracion_s

        if right is None or right <= left:
            right = min(duracion_s if duracion_s > 0 else left + 0.12 * (j - idx), left + 0.12 * (j - idx))
            if right <= left:
                right = left + 0.04 * (j - idx)

        paso = (right - left) / (j - idx)
        for k in range(idx, j):
            limpias[k]["s"] = left + (k - idx) * paso
            limpias[k]["e"] = left + (k - idx + 1) * paso
        idx = j

    # Asegurar cotas, orden monotónico y duración positiva mínima.
    resultado: list[dict[str, Any]] = []
    prev_s = 0.0
    max_t = duracion_s if duracion_s > 0 else None
    for i, item in enumerate(limpias):
        s = max(0.0, float(item["s"]))
        e = max(s, float(item["e"]))
        if max_t is not None:
            s = min(s, max(0.0, max_t - 0.01))
            e = min(e, max_t)
        if s < prev_s:
            s = prev_s
        if e <= s:
            e = s + 0.02
            if max_t is not None and e > max_t:
                e = max_t
                s = max(0.0, e - 0.02)
        prev_s = s
        resultado.append({
            "i": i,
            "w": item["w"],
            "s": round(s, 3),
            "e": round(e, 3),
        })
    return resultado


def _extraer_palabras_de_segmentos_whisperx(segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convierte segmentos de WhisperX (alineados o no) en lista plana de palabras."""
    palabras: list[dict[str, Any]] = []
    for seg in segments:
        seg_s = seg.get("start")
        seg_e = seg.get("end")
        words = seg.get("words")
        if words:
            for wd in words:
                txt = str(wd.get("word", "")).strip()
                if not txt:
                    continue
                palabras.append({
                    "w": txt,
                    "s": wd.get("start"),
                    "e": wd.get("end"),
                    "seg_s": seg_s,
                    "seg_e": seg_e,
                })
        else:
            # Si un segmento no trajo lista de words, repartir por tokens del texto.
            tokens = str(seg.get("text", "")).strip().split()
            for tok in tokens:
                palabras.append({
                    "w": tok,
                    "s": None,
                    "e": None,
                    "seg_s": seg_s,
                    "seg_e": seg_e,
                })
    return palabras


def transcribir_con_whisperx(
    audio_np,
    idioma_pedido: str,
    modelo: str,
    hw: dict[str, Any],
    batch_size: int,
    duracion_s: float,
    advertencias: list[str],
) -> tuple[list[dict[str, Any]], str, str, bool]:
    """Ejecuta WhisperX (faster-whisper + alineación wav2vec2)."""
    # PyTorch >= 2.6 usa weights_only=True por defecto, lo que puede romper checkpoints
    # de pyannote/omegaconf dentro de WhisperX si el entorno no lo habilita.
    os.environ.setdefault("TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD", "1")
    import whisperx

    lang_arg = None if idioma_pedido == "auto" else idioma_pedido
    modelo_usado = modelo

    # Intentar cargar el modelo; si large-v3-turbo no existiera en una versión vieja, caer a medium.
    def _cargar_modelo(nombre: str):
        try:
            return whisperx.load_model(
                nombre,
                device=hw["ct2_device"],
                compute_type=hw["compute_type"],
                language=lang_arg,
                vad_method="silero",
            )
        except TypeError:
            return whisperx.load_model(
                nombre,
                device=hw["ct2_device"],
                compute_type=hw["compute_type"],
                language=lang_arg,
            )

    try:
        model = _cargar_modelo(modelo_usado)
    except Exception as exc:
        if modelo_usado == "large-v3-turbo":
            advertencias.append(
                f"No se pudo cargar el modelo 'large-v3-turbo' ({exc}); usando 'medium'."
            )
            modelo_usado = "medium"
            model = _cargar_modelo(modelo_usado)
        else:
            raise

    transcribe_kwargs: dict[str, Any] = {"batch_size": batch_size}
    if lang_arg is not None:
        transcribe_kwargs["language"] = lang_arg

    result = model.transcribe(audio_np, **transcribe_kwargs)
    idioma_detectado = (result.get("language") or lang_arg or "es").strip().lower()
    if not idioma_detectado:
        idioma_detectado = "es"

    # Liberar memoria del modelo ASR antes de cargar wav2vec2 si estamos en máquina justa.
    del model

    alineado = False
    segments = result.get("segments") or []
    try:
        align_model, metadata = whisperx.load_align_model(
            language_code=idioma_detectado,
            device=hw["align_device"],
        )
        aligned = whisperx.align(
            segments,
            align_model,
            metadata,
            audio_np,
            hw["align_device"],
            return_char_alignments=False,
        )
        segments = aligned.get("segments") or segments
        alineado = True
        del align_model
    except Exception as exc:
        msg = (
            f"Falló la alineación wav2vec2 para idioma '{idioma_detectado}' ({exc}). "
            "Se usan tiempos aproximados sin alinear (pueden correrse hasta ~0,9 s)."
        )
        print(f"[AVISO] {msg}", file=sys.stderr)
        advertencias.append(msg)

    palabras_crudas = _extraer_palabras_de_segmentos_whisperx(segments)
    palabras = normalizar_palabras(palabras_crudas, duracion_s)
    return palabras, idioma_detectado, modelo_usado, alineado


def transcribir_con_faster_whisper(
    audio_np,
    idioma_pedido: str,
    modelo: str,
    hw: dict[str, Any],
    duracion_s: float,
    advertencias: list[str],
) -> tuple[list[dict[str, Any]], str, str, bool]:
    """Camino alternativo sin WhisperX: faster-whisper con word_timestamps=True."""
    from faster_whisper import WhisperModel

    modelo_usado = modelo
    try:
        model = WhisperModel(
            modelo_usado,
            device=hw["ct2_device"],
            compute_type=hw["compute_type"],
        )
    except Exception as exc:
        if modelo_usado == "large-v3-turbo":
            advertencias.append(
                f"No se pudo cargar '{modelo_usado}' ({exc}); usando 'medium'."
            )
            modelo_usado = "medium"
            model = WhisperModel(
                modelo_usado,
                device=hw["ct2_device"],
                compute_type=hw["compute_type"],
            )
        else:
            raise

    lang_arg = None if idioma_pedido == "auto" else idioma_pedido
    # Pasar el arreglo float32 16 kHz directamente evita usar PyAV (decode_audio),
    # previniendo incompatibilidades entre faster-whisper y versiones nuevas de av.
    seg_iter, info = model.transcribe(
        audio_np,
        language=lang_arg,
        word_timestamps=True,
        vad_filter=True,
    )

    idioma_detectado = (getattr(info, "language", None) or lang_arg or "es").strip().lower()
    lang_prob = getattr(info, "language_probability", 1.0)
    if lang_arg is None and (not idioma_detectado or (lang_prob is not None and lang_prob < 0.35)):
        # Si no se pudo detectar con confianza, reintentar forzando español por defecto.
        idioma_detectado = "es"
        advertencias.append(
            f"Detección de idioma incierta (prob={lang_prob}); se usó español ('es') por defecto."
        )
        seg_iter, _ = model.transcribe(
            audio_np,
            language="es",
            word_timestamps=True,
            vad_filter=True,
        )

    palabras_crudas: list[dict[str, Any]] = []
    for seg in seg_iter:
        if seg.words:
            for wd in seg.words:
                txt = wd.word.strip()
                if not txt:
                    continue
                palabras_crudas.append({
                    "w": txt,
                    "s": wd.start,
                    "e": wd.end,
                    "seg_s": seg.start,
                    "seg_e": seg.end,
                })
        else:
            for tok in seg.text.strip().split():
                palabras_crudas.append({
                    "w": tok,
                    "s": None,
                    "e": None,
                    "seg_s": seg.start,
                    "seg_e": seg.end,
                })

    palabras = normalizar_palabras(palabras_crudas, duracion_s)
    return palabras, idioma_detectado, modelo_usado, False


def formatear_mm_ss(segundos: float) -> str:
    total = max(0, int(segundos))
    mm, ss = divmod(total, 60)
    return f"{mm:02d}:{ss:02d}"


def formatear_srt_tiempo(segundos: float) -> str:
    ms_total = max(0, int(round(segundos * 1000)))
    hh, rem = divmod(ms_total, 3_600_000)
    mm, rem = divmod(rem, 60_000)
    ss, ms = divmod(rem, 1000)
    return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}"


def construir_texto_txt(palabras: list[dict[str, Any]]) -> str:
    """Arma texto.txt con [mm:ss] (#indice_primera_palabra) por frase."""
    if not palabras:
        return ""

    lineas: list[str] = []
    actual: list[dict[str, Any]] = []
    fin_frase = re.compile(r"[.?!…][\"'»)\]]*$")

    def _cerrar() -> None:
        if not actual:
            return
        primera = actual[0]
        marca = formatear_mm_ss(primera["s"])
        texto = " ".join(p["w"] for p in actual)
        lineas.append(f"[{marca}] (#{primera['i']}) {texto}")
        actual.clear()

    for idx, pal in enumerate(palabras):
        if actual:
            pausa = pal["s"] - actual[-1]["e"]
            if pausa >= 1.2 or len(actual) >= 24:
                _cerrar()
        actual.append(pal)
        if fin_frase.search(pal["w"]) and len(actual) >= 3:
            _cerrar()
        elif idx == len(palabras) - 1:
            _cerrar()

    _cerrar()
    return "\n".join(lineas) + "\n"


def construir_subtitulos_srt(palabras: list[dict[str, Any]]) -> str:
    """Arma subtitulos.srt en bloques cortos legibles sin solapamientos."""
    if not palabras:
        return ""

    cues: list[dict[str, Any]] = []
    actual: list[dict[str, Any]] = []
    chars = 0
    fin_frase = re.compile(r"[.?!…,:;][\"'»)\]]*$")

    def _cerrar() -> None:
        nonlocal chars
        if not actual:
            return
        cues.append({
            "s": actual[0]["s"],
            "e": actual[-1]["e"],
            "texto": " ".join(p["w"] for p in actual),
        })
        actual.clear()
        chars = 0

    for pal in palabras:
        if actual:
            pausa = pal["s"] - actual[-1]["e"]
            nuevo_largo = chars + 1 + len(pal["w"])
            if pausa >= 0.65 or len(actual) >= 7 or nuevo_largo > 42:
                _cerrar()
        actual.append(pal)
        chars = sum(len(p["w"]) for p in actual) + max(0, len(actual) - 1)
        if fin_frase.search(pal["w"]) and (len(actual) >= 4 or chars >= 24):
            _cerrar()
    _cerrar()

    # Evitar solapamientos entre cues consecutivos.
    for k in range(len(cues) - 1):
        if cues[k]["e"] > cues[k + 1]["s"]:
            cues[k]["e"] = max(cues[k]["s"] + 0.05, cues[k + 1]["s"])

    bloques: list[str] = []
    for n, cue in enumerate(cues, start=1):
        bloques.append(
            f"{n}\n"
            f"{formatear_srt_tiempo(cue['s'])} --> {formatear_srt_tiempo(cue['e'])}\n"
            f"{cue['texto']}\n"
        )
    return "\n".join(bloques)


def parsear_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcribe audio o video a palabras.json, texto.txt, subtitulos.srt e info.json."
    )
    parser.add_argument("entrada", help="Ruta al archivo de audio o video.")
    parser.add_argument(
        "-o",
        "--salida",
        default=None,
        help="Carpeta de salida (por defecto: <carpeta_de_entrada>/transcripcion).",
    )
    parser.add_argument(
        "--idioma",
        default="auto",
        help="Idioma ISO (ej. 'es', 'en') o 'auto' para detectar con fallback a español (default: auto).",
    )
    parser.add_argument(
        "--modelo",
        default="auto",
        help="Modelo Whisper: auto, tiny, base, small, medium, large-v3, large-v3-turbo (default: auto).",
    )
    parser.add_argument(
        "--motor",
        choices=("auto", "whisperx", "faster-whisper"),
        default="auto",
        help="Motor de transcripción (default: auto = WhisperX con fallback a faster-whisper).",
    )
    parser.add_argument(
        "--dispositivo",
        choices=("auto", "cpu", "cuda"),
        default="auto",
        help="Dispositivo de cómputo (default: auto).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Tamaño de batch para WhisperX (por defecto depende del hardware).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    t0 = time.monotonic()
    args = parsear_args(argv)

    entrada = Path(args.entrada).expanduser().resolve()
    if not entrada.is_file():
        print(f"[ERROR] No existe el archivo de entrada: {entrada}", file=sys.stderr)
        return 1

    salida = Path(args.salida).expanduser().resolve() if args.salida else (entrada.parent / "transcripcion")
    salida.mkdir(parents=True, exist_ok=True)

    ffmpeg, ffprobe = verificar_ffmpeg()
    duracion_s, tiene_audio = obtener_info_media(ffprobe, entrada)
    if not tiene_audio:
        print(f"[ERROR] El archivo no tiene pista de audio: {entrada}", file=sys.stderr)
        return 1

    hw = detectar_hardware(args.dispositivo)
    modelo = hw["modelo_default"] if args.modelo == "auto" else args.modelo
    batch_size = args.batch_size if args.batch_size is not None else hw["batch_size_default"]
    advertencias: list[str] = []

    print(
        f"[transcribir] Entrada: {entrada.name} ({duracion_s:.1f}s) | "
        f"Hardware: {hw['etiqueta']} | Modelo: {modelo} | Idioma: {args.idioma}",
        file=sys.stderr,
    )

    with tempfile.TemporaryDirectory(prefix="kit_transcribir_") as tmpdir:
        wav_tmp = Path(tmpdir) / "audio_16k.wav"
        extraer_wav_16k(ffmpeg, entrada, wav_tmp)

        motor_usado = None
        palabras: list[dict[str, Any]] = []
        idioma_final = "es"
        modelo_final = modelo
        alineado = False

        usar_whisperx = args.motor in ("auto", "whisperx")
        if usar_whisperx:
            try:
                audio_np = leer_wav_float32(wav_tmp)
                palabras, idioma_final, modelo_final, alineado = transcribir_con_whisperx(
                    audio_np=audio_np,
                    idioma_pedido=args.idioma,
                    modelo=modelo,
                    hw=hw,
                    batch_size=batch_size,
                    duracion_s=duracion_s,
                    advertencias=advertencias,
                )
                motor_usado = "whisperx"
            except ImportError as exc:
                if args.motor == "whisperx":
                    print(f"[ERROR] Se pidió --motor whisperx pero no está instalado: {exc}", file=sys.stderr)
                    return 1
                aviso = (
                    f"WhisperX no está instalado ({exc}). Usando camino alternativo "
                    "'faster-whisper' con word_timestamps=True: los tiempos por palabra "
                    "son menos precisos (pueden correrse hasta ~0,9 s)."
                )
                print(f"[AVISO] {aviso}", file=sys.stderr)
                advertencias.append(aviso)
            except Exception as exc:
                if args.motor == "whisperx":
                    print(f"[ERROR] WhisperX falló: {exc}", file=sys.stderr)
                    return 1
                aviso = (
                    f"WhisperX falló en este equipo ({exc}). Usando camino alternativo "
                    "'faster-whisper' con word_timestamps=True (menos preciso, hasta ~0,9 s de error)."
                )
                print(f"[AVISO] {aviso}", file=sys.stderr)
                advertencias.append(aviso)

        if motor_usado is None:
            try:
                if args.motor == "faster-whisper":
                    aviso = (
                        "Se usó faster-whisper sin alineación wav2vec2: los tiempos por "
                        "palabra pueden correrse hasta ~0,9 s."
                    )
                    print(f"[AVISO] {aviso}", file=sys.stderr)
                    advertencias.append(aviso)
                audio_np = leer_wav_float32(wav_tmp)
                palabras, idioma_final, modelo_final, alineado = transcribir_con_faster_whisper(
                    audio_np=audio_np,
                    idioma_pedido=args.idioma,
                    modelo=modelo,
                    hw=hw,
                    duracion_s=duracion_s,
                    advertencias=advertencias,
                )
                motor_usado = "faster-whisper"
            except ImportError as exc:
                print(
                    f"[ERROR] Tampoco está instalado faster-whisper ({exc}).\n"
                    "Instalá las dependencias en .venv con:\n"
                    "  .venv/bin/pip install -r .claude/skills/transcribir/requirements.txt\n"
                    "o solo el alternativo:\n"
                    "  .venv/bin/pip install faster-whisper",
                    file=sys.stderr,
                )
                return 1

    # Escribir los 4 archivos del contrato.
    ruta_palabras = salida / "palabras.json"
    ruta_texto = salida / "texto.txt"
    ruta_srt = salida / "subtitulos.srt"
    ruta_info = salida / "info.json"

    ruta_palabras.write_text(
        json.dumps(palabras, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    ruta_texto.write_text(construir_texto_txt(palabras), encoding="utf-8")
    ruta_srt.write_text(construir_subtitulos_srt(palabras), encoding="utf-8")

    tiempo_s = round(time.monotonic() - t0, 2)
    info = {
        "fuente": str(entrada),
        "idioma": idioma_final,
        "modelo": modelo_final,
        "duracion_s": round(duracion_s, 3),
        "motor": motor_usado,
        "alineado": alineado,
        "dispositivo": hw["etiqueta"],
        "total_palabras": len(palabras),
        "tiempo_proceso_s": tiempo_s,
        "advertencias": advertencias,
    }
    ruta_info.write_text(
        json.dumps(info, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        f"[transcribir] Listo en {tiempo_s:.1f}s | {len(palabras)} palabras | "
        f"idioma={idioma_final} | motor={motor_usado} (alineado={alineado}) -> {salida}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

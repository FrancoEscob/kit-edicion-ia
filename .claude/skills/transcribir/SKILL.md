---
name: transcribir
description: Transcribe un archivo de audio o video con alineación palabra por palabra (WhisperX) y genera palabras.json, texto.txt, subtitulos.srt e info.json según el contrato del kit. Usala cuando haya que pasar un crudo a texto con tiempos exactos por palabra antes de elegir tramos o armar un plan.json.
---

# Transcribir audio o video

Convierte un archivo de audio o video en los 4 archivos de transcripción del contrato, con tiempos precisos por palabra mediante WhisperX (`faster-whisper` + alineación `wav2vec2`).

## Comando exacto

Desde la raíz del repo:

- **macOS / Linux:**
  ```bash
  .venv/bin/python .claude/skills/transcribir/scripts/transcribir.py "proyectos/<nombre>/crudo.mp4" -o "proyectos/<nombre>/transcripcion"
  ```
- **Windows (PowerShell / CMD):**
  ```powershell
  .venv\Scripts\python.exe .claude\skills\transcribir\scripts\transcribir.py "proyectos\<nombre>\crudo.mp4" -o "proyectos\<nombre>\transcripcion"
  ```

### Opciones útiles

- `--idioma es` para forzar español (por defecto `auto`: detecta idioma y cae a español si la detección es incierta).
- `--modelo small|medium|large-v3-turbo` para forzar modelo (por defecto `auto`: `small` en CPU, `medium` en Apple Silicon, `large-v3-turbo` con CUDA).
- `--motor auto|whisperx|faster-whisper` (por defecto `auto`: usa WhisperX y cae automáticamente a `faster-whisper` con `word_timestamps=True` si WhisperX no está disponible).

## Qué entra

- Un archivo de audio o video legible por `ffmpeg` (MP4, MOV, MKV, WebM, WAV, MP3, M4A, etc.; soporta rutas con espacios y rutas de Windows).

## Qué sale (en `-o <carpeta>`)

1. `palabras.json`: lista `[{"i": 0, "w": "hola", "s": 12.41, "e": 12.62}, ...]` en segundos del archivo original.
2. `texto.txt`: frases con marca `[mm:ss]` e índice `(#i)` de la primera palabra, listo para que elijas tramos por índice.
3. `subtitulos.srt`: subtítulos listos en formato SRT UTF-8.
4. `info.json`: `{"fuente", "idioma", "modelo", "duracion_s", "motor", "alineado", "dispositivo", "total_palabras", "tiempo_proceso_s", "advertencias"}`.

## Al elegir tramos: repeticiones con intención vs. arranques fallidos

Cuando leas `texto.txt` para limpiar el guion y armar `tramos` en `plan.json`, **no borres repeticiones expresivas** como si fueran muletillas o tartamudeo:

- **Conservar (repetición intencional / énfasis retórico):** ritmo fluido, sin corrección ni traba; refuerzan intensidad o emoción.
  - *"sube y sube y sube"* / *"arriba y arriba y arriba"*
  - *"esto es muy, muy, muy importante"*
  - *"nunca, nunca, nunca hagas ese corte"*
  - *"probar, probar y volver a probar"*
- **Cortar (arranque fallido / mala toma / traba):** la persona se frena, se corrige o repite el inicio de una frase incompleta.
  - *"Cuando vos... cuando vos abrís el proyecto..."* → dejar solo el segundo arranque completo.
  - *"Lo que pasa es que... bah, perdón, digo: lo que pasa es que..."* → cortar hasta el reinicio limpio.
  - *"Para edi— para editar más rápido..."* → sacar la palabra truncada.

## Si algo falla

- **No está `.venv/` o faltan librerías:** creá `.venv` con Python 3.10–3.12 (evitá 3.13/3.14 por compatibilidad de `torch`/`whisperx`) e instalá:
  - Sin GPU (CPU, más liviano):
    ```bash
    .venv/bin/pip install --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple torch torchaudio
    .venv/bin/pip install -r .claude/skills/transcribir/requirements.txt
    ```
  - Con GPU NVIDIA (CUDA):
    ```bash
    .venv/bin/pip install -r .claude/skills/transcribir/requirements.txt
    ```
- **WhisperX no se puede instalar en ese equipo:** instalá solo el motor alternativo:
  ```bash
  .venv/bin/pip install faster-whisper
  ```
  El script detecta que falta WhisperX, corre `faster-whisper` con `word_timestamps=True` y avisa en `stderr` e `info.json` que los tiempos son menos precisos (pueden correrse hasta ~0,9 s).
- **Falta `ffmpeg` / `ffprobe`:** instalalo con `brew install ffmpeg` (Mac), `winget install Gyan.FFmpeg` (Windows) o `sudo apt install ffmpeg` (Linux) y reintentá.
- **Sin internet la primera vez:** WhisperX descarga el modelo de Whisper y el modelo `wav2vec2` del idioma en caché de HuggingFace la primera corrida; hace falta conexión esa vez.

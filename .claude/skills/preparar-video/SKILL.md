---
name: preparar-video
description: Corta un video por índices de palabras según un plan.json, saca silencios internos largos con Silero VAD ONNX (con ritmo configurable), limpia y normaliza la voz a -14 LUFS (pico <= -1 dBTP), reencuadra a 9:16, 1:1, 4:5 o 16:9 ubicando ojos en el tercio superior con YuNet ONNX, y extrae 3 paletas candidatas del A-roll. Usala después de transcribir y elegir tramos, antes de montar en HyperFrames.
---

# Preparar video base

Toma un `plan.json` con los tramos elegidos por índice de palabra y genera `base.mp4`, `base-palabras.json` (tiempos ya corridos al reloj nuevo) e `informe.json`, en una sola pasada de compresión de video.

## Comando exacto

Desde la raíz del repo:

- **macOS / Linux:**
  ```bash
  .venv/bin/python .claude/skills/preparar-video/scripts/preparar.py "proyectos/<nombre>/plan.json"
  ```
- **Windows (PowerShell / CMD):**
  ```powershell
  .venv\Scripts\python.exe .claude\skills\preparar-video\scripts\preparar.py "proyectos\<nombre>\plan.json"
  ```

## Qué entra (`plan.json`)

```json
{
  "fuente": "proyectos/x/crudo.mp4",
  "palabras": "proyectos/x/transcripcion/palabras.json",
  "tramos": [[120, 188], [240, 301]],
  "formato": "9:16",
  "seguir_cara": true,
  "encuadre": "tercios",
  "zoom_max": 1.35,
  "sacar_silencios": true,
  "ritmo": "normal",
  "salida": "proyectos/x/clip-1/"
}
```

- `tramos`: lista de pares `[indice_primera, indice_ultima]` (ambas incluidas), sacados de `palabras.json` / `texto.txt`. Nunca tiempos.
- `formato`: `"9:16"` (`1080x1920`), `"1:1"` (`1080x1080`), `"4:5"` (`1080x1350`) o `"16:9"` (`1920x1080`).
- `seguir_cara`: `true` usa YuNet ONNX con recorte suavizado sin saltos dentro del mismo tramo; `false` (o si no detecta cara) centra.
- `encuadre` *(opcional)*: `"tercios"` (default en `9:16`, `4:5` y `1:1`) o `"centrado"` (default en `16:9`). En `"tercios"` usa los landmarks de ojos (`f[4..7]`) y nariz (`f[8]`) de YuNet para centrar la nariz en `x` y alinear los ojos sobre el tercio superior (`y ≈ 640` en `9:16`, `450` en `4:5`, `360` en `1:1`), aplicando el zoom mínimo necesario.
- `zoom_max` *(opcional, default `1.35`)*: tope de acercamiento para `"tercios"`. Además se respeta la nitidez de origen (en fuentes ≥ 1200 px nunca baja de 1080 px reales; en 1080p nunca baja de 960 px). Si el tope no alcanza, se acerca lo máximo posible y lo informa en `informe.json` (`encuadre.ojos_y_final`).
- `sacar_silencios`: `true` recorta silencios muertos con Silero VAD ONNX sin cortar palabras ni repeticiones expresivas.
- `ritmo` *(opcional, default `"normal"`)*: regula cuánto aire queda entre frases al cortar silencios:
  - `"agil"`: ~40–80 ms (objetivo 60 ms; ritmo reel picado, corta pausas ≥ ~0,22 s).
  - `"normal"`: ~120–160 ms (objetivo 145 ms; natural y fluido, corta pausas ≥ ~0,37 s).
  - `"pausado"`: ~180–250 ms (objetivo 220 ms; conversacional, solo corta pausas ≥ ~0,52 s).

### Regla de silencios y repeticiones

`preparar-video` **solo recorta silencios muertos** entre palabras (nunca palabras habladas). Al armar `tramos` previamente, conservá las repeticiones con intención expresiva (*"arriba y arriba y arriba"*, *"muy, muy, muy importante"*, *"nunca, nunca, nunca"*) y excluí únicamente arranques fallidos o trabas (*"Cuando vos... cuando vos abrís..."*, *"Para edi— para editar..."*).

## Qué sale (en `salida`)

1. `base.mp4`: video reencuadrado, sin silencios largos, voz con paso alto (80 Hz), reducción de ruido (`arnndn` o `afftdn`) y `loudnorm` de dos pasadas a −14 LUFS con pico real ≤ −1 dBTP, y audio/video del mismo largo.
2. `base-palabras.json`: las palabras que quedaron con sus tiempos exactos en el reloj de `base.mp4`.
3. `informe.json`: resolución, duraciones de video y audio, Δ A/V en ms, LUFS y pico real medidos, método de ruido, silencios cortados (`ritmo`, `aire_objetivo_ms`), encuadre (`ojos_y_objetivo`, `ojos_y_final`, `nariz_x_final`, `zoom_aplicado`, `zoom_limitado`), **`paletas`** (3 paletas candidatas de 4 colores hex extraídas del A-roll con k-means: `acento_claro`, `acento_oscuro`, `blanco_tenido`, `negro_tenido` para ofrecer en `montar-video`) y cualquier etapa salteada o advertencia.

## Modelos automáticos

Si faltan en `.externas/modelos/`, el script los baja solo usando las URLs de `.claude/skills/setup-kit/externas.json`:
- `silero_vad.onnx` (silencios)
- `face_detection_yunet_2023mar.onnx` (caras y landmarks de ojos/nariz)
- `cb.rnnn` (reducción de ruido con `arnndn`)

Si falta un modelo y no hay conexión, la etapa se saltea sin romper el proceso y queda registrada en `informe.json`.

## Si algo falla

- **Faltan librerías en `.venv/`:** instalá con:
  ```bash
  .venv/bin/pip install -r .claude/skills/preparar-video/requirements.txt
  ```
  (en Windows: `.venv\Scripts\pip.exe install -r .claude\skills\preparar-video\requirements.txt`).
- **Falta `ffmpeg` / `ffprobe`:** `brew install ffmpeg` (Mac), `winget install Gyan.FFmpeg` (Windows) o `sudo apt install ffmpeg` (Linux).
- **Índice fuera de rango en `tramos`:** revisá `palabras.json` y asegurate de que `[inicio, fin]` existan y `inicio <= fin`.
- **Si `arnndn` no viene en ese `ffmpeg`:** el script cae solo a `afftdn` y lo anota en `informe.json`.

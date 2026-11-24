---
name: preparar-video
description: Corta un video por índices de palabras según un plan.json, saca silencios internos largos con Silero VAD ONNX (con ritmo configurable), limpia y normaliza la voz a -14 LUFS (pico <= -1 dBTP), reencuadra a 9:16, 1:1, 4:5 o 16:9 con trípode virtual y ojos en el tercio superior (YuNet ONNX), y extrae 3 paletas candidatas del A-roll. Usala después de transcribir y elegir tramos, antes de montar en HyperFrames.
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
  "movimiento": "tripode",
  "zoom_max": 1.35,
  "sacar_silencios": true,
  "ritmo": "normal",
  "salida": "proyectos/x/clip-1/"
}
```

- `tramos`: pares `[indice_primera, indice_ultima]` (ambas incluidas) sacados de `palabras.json` / `texto.txt`. Nunca tiempos.
- `formato`: `"9:16"` (`1080x1920`), `"1:1"` (`1080x1080`), `"4:5"` (`1080x1350`) o `"16:9"` (`1920x1080`).
- `seguir_cara`: `true` usa YuNet ONNX; `false` (o si no detecta cara) centra.
- `encuadre` *(opcional)*: `"tercios"` (default en `9:16`, `4:5`, `1:1`) o `"centrado"` (default en `16:9`). En `"tercios"` centra la nariz en `x` y alinea los ojos al tercio superior (`y ≈ 640` en `9:16`, `450` en `4:5`, `360` en `1:1`) con el zoom mínimo necesario.
- `movimiento` *(opcional, default `"tripode"`)*:
  - `"tripode"`: encuadre fijo por tramo en la mediana de ojos/nariz. Mientras la nariz siga dentro de ±12 % del ancho del recorte (y ojos en 560–720 en 9:16), la cámara no se mueve ni un píxel. Si sale y queda afuera > ~1,2 s, reencuadra una vez (máx. cada ~4 s), preferentemente en una pausa (corte seco en huecos ≥ 0,25 s o suave ease in-out de 0,5 s). Si la cara toca el margen de seguridad (< 6 % del borde o nariz > ±30 %) por ≥ 2 muestras seguidas, reencuadra de inmediato (suave 0,35 s o corte en pausa) sin esperar 1,2 s ni enfriamiento.
  - `"seguir"`: seguimiento continuo suavizado (cámara que acompaña el movimiento).
- `zoom_max` *(opcional, default `1.35`)*: tope de acercamiento para `"tercios"`. Respeta nitidez de origen (≥ 1080 px en fuentes ≥ 1200 px; ≥ 960 px en 1080p).
- `sacar_silencios`: `true` recorta silencios muertos con Silero VAD ONNX sin cortar palabras ni repeticiones expresivas.
- `ritmo` *(opcional, default `"normal"`)*: aire que deja al cortar silencios — `"agil"` (~40–80 ms), `"normal"` (~120–160 ms), `"pausado"` (~180–250 ms).

### Regla de silencios y repeticiones

`preparar-video` solo recorta silencios muertos entre palabras. Al armar `tramos`, conservá repeticiones expresivas (*"arriba y arriba y arriba"*, *"muy, muy, muy importante"*, *"nunca, nunca, nunca"*) y excluí solo arranques fallidos o trabas (*"Cuando vos... cuando vos abrís..."*, *"Para edi— para editar..."*).

## Qué sale (en `salida`)

1. `base.mp4`: video reencuadrado, sin silencios largos, voz con paso alto (80 Hz), reducción de ruido (`arnndn` o `afftdn`) y `loudnorm` de dos pasadas a −14 LUFS (pico ≤ −1 dBTP), con audio y video del mismo largo.
2. `base-palabras.json`: palabras en el reloj nuevo de `base.mp4`.
3. `informe.json`: resolución, duraciones y Δ A/V, LUFS y pico real, silencios (`ritmo`, `aire_objetivo_ms`), encuadre por tramo (`ojos_y_final`, `nariz_x_final`, `zoom`, `reencuadres` `[{t, tipo}]`, `trayectoria_x`/`trayectoria_y` cada 0,5 s, `desplazamiento_total_x_px`/`y_px`), `paletas` (3 paletas candidatas de 4 colores hex del A-roll) y `etapas_salteadas` / `advertencias`.

## Modelos automáticos

Si faltan en `.externas/modelos/`, los baja desde `.claude/skills/setup-kit/externas.json` (`silero_vad.onnx`, `face_detection_yunet_2023mar.onnx`, `cb.rnnn`). Si falta uno y no hay red, saltea esa etapa y lo anota en `informe.json`.

## Si algo falla

- **Faltan librerías en `.venv/`:** `.venv/bin/pip install -r .claude/skills/preparar-video/requirements.txt` (en Windows: `.venv\Scripts\pip.exe ...`).
- **Falta `ffmpeg` / `ffprobe`:** `brew install ffmpeg` (Mac), `winget install Gyan.FFmpeg` (Windows), `sudo apt install ffmpeg` (Linux).
- **Índice fuera de rango en `tramos`:** chequeá que `[inicio, fin]` existan en `palabras.json` y `inicio <= fin`.
- **Sin `arnndn` en `ffmpeg`:** cae automáticamente a `afftdn` y lo anota en `informe.json`.

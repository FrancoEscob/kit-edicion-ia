---
name: montar-video
description: Arma la composición final de video en HyperFrames (o Remotion si la persona lo pide) a partir de base.mp4 y base-palabras.json: planificador interactivo de escenas, checkpoint de subtítulos, 5 capas con tercio inferior opcional, gráficos encima, cortes a pantalla completa (propios o MP4 de Lemo), sonido por cue sheet (SFX CC0 + audición musical + ducking) y controles previos al render.
---

# Montar video

Recibís `base.mp4` + `base-palabras.json` (salida de `preparar-video`) y un estilo elegido. Armás la composición en `<salida>/montaje/` y renderizás a `<salida>/final.mp4`.

Antes de diseñar subtítulos, gráficos o sonido, respetá `.claude/skills/editar-video/criterio/` (`composicion.md`, `subtitulos.md`, `graficos-y-broll.md` y `sonido.md`). Para sintaxis de HyperFrames consultá las skills `hyperframes` y `hyperframes-cli`.

**Todos los comandos se corren desde la raíz del kit.** En los ejemplos, `CLIP` es la carpeta de salida de `preparar-video` (por ejemplo `proyectos/charla/clip-1`), y el montaje va en `CLIP/montaje/`.

**Cuadros por segundo:** renderizá a los fps de `base.mp4` (`ffprobe -v error -select_streams v -show_entries stream=r_frame_rate -of csv=p=0 CLIP/base.mp4`). Si la fuente es 23,976 o 25, no la pases a 30: el movimiento queda a saltitos.

## 0. Antes de armar escenas (solo para reels producidos)

Si la persona solo pidió "poneme subtítulos", salteá al paso 1. Si quiere un reel producido con escenas y gráficos a medida, hacé estos dos pasos cortos primero:

### a) `planificador.html` (entre `preparar-video` y el armado)
Generá el planificador local autocontenido (abre directo en el navegador, sin servidor ni recomendaciones de IA):
```bash
python3 .claude/skills/montar-video/scripts/generar_planificador.py CLIP/base-palabras.json \
  --video base.mp4 --informe CLIP/informe.json --titulo "Mi reel" \
  --out CLIP/planificador.html
```
Trae el guion línea por línea (`L01`, `L02`…), reproductor que salta a cada línea al hacer clic, selector de paleta (desde `informe.json` → `paletas` si existe) y de par tipográfico OFL, tipo de escena (`A-roll`, `Gráfico encima`, `B-roll`, `Pantalla completa`, `Lemo`), nota libre y caja para pegar o arrastrar una captura de referencia. La persona toca **Guardar plan** → descarga `plan-escenas.json`, y vos montás siguiendo ese archivo.

### b) Checkpoint de subtítulos (antes de construir las escenas)
Armá primero solo **Capa 1 (`base.mp4`) + tercio inferior opcional + Capa 4 (`subtitulos.html`)**, renderizá un borrador rápido y sacá una hoja de **6–12 cuadros** sobre palabras activas para que la persona apruebe tipografía, tamaño, contraste y posición antes de invertir tiempo en escenas:
```bash
npx hyperframes render CLIP/montaje --fps 15 --quality draft --output CLIP/preview-subtitulos.mp4
python3 .claude/skills/montar-video/scripts/hoja_subtitulos.py CLIP/preview-subtitulos.mp4 CLIP/montaje/base-palabras.json \
  --cuadros 9 --cols 3 --out CLIP/hoja-subtitulos.jpg
```
Mostrale `hoja-subtitulos.jpg`. Recién cuando aprueba, sumás las capas 2, 3 y 5.

## 1. Las 5 capas (de abajo hacia arriba)

Partí de `plantilla/` (copiala a `CLIP/montaje/` junto con `base.mp4` y `base-palabras.json`). Si corregís palabras mal transcritas (nombres, marcas), corregilas en `CLIP/montaje/base-palabras.json`.

**Con un estilo del kit:** reemplazá la capa de subtítulos de la plantilla por el `subtitulos.html` del estilo, montado como dice `estilos/README.md` (su id es `captions`). Si el estilo trae su propio oscurecido del tercio inferior (como `editorial`), **borrá el `#tercio-inferior` de la plantilla** para no oscurecer dos veces. El gancho y cualquier texto que tenga que leerse van en una capa **por encima** de los subtítulos, porque el oscurecido del estilo tapa lo que está debajo y `check` lo marca como texto tapado. Cada capa tiene un `z-index` fijo y sub-composiciones en `compositions/` para pasar `lint` sin avisos.

**Encuadre base en 9:16 (`1080×1920`):** ojos del hablante en `y ≈ 640`, subtítulos sobre el tercio inferior (`y ≈ 1280`), zona segura centrada en **`x = 510`** (`left: 90px; width: 840px`) y nada legible debajo de `y ≈ 1340–1530`.

| Capa | `z-index` | Qué lleva | Regla clave |
|---|---|---|---|
| 1. La persona | `1` | `<video id="persona" src="base.mp4" muted playsinline>` | Siempre `muted`. El audio va separado en la capa 5. |
| 1b. Tercio inferior *(opcional)* | `5` | `#tercio-inferior` (degradado negro + `backdrop-filter: blur(14px)` enmascarado desde `y = 1250`) | Limpia manos/ropa detrás del texto sin cajas pesadas. Borralo si el estilo no lo usa. Marcado `data-layout-ignore`. |
| 2. Cortes a pantalla completa | `10–11` | Escenas en `compositions/` y/o `<video>` de un MP4 de Lemo | Máximo ~30% de la duración total en clips a cámara. Un `<video>` con `data-start` nunca va adentro de un `<div>` con `data-start`. |
| 3. Gráficos encima | `20` | Sub-composiciones transparentes (`background: transparent`) | **Alrededor del tercio inferior, sin tapar la cabeza:** en `plantilla/compositions/grafico-encima.html` va en `top: 1005px` (debajo del mentón, arriba del subtítulo). Si es una tarjeta alta tipo UI debajo del subtítulo, subí el subtítulo a `y ≈ 1140–1240` y poné la tarjeta en `y ≈ 1290–1520`. |
| 4. Subtítulos | `30` | `compositions/subtitulos.html` (`data-track-kind="captions"`) | `left: 90px; width: 840px; top: 1245px` (tercio inferior `y ≈ 1280`, nunca debajo de `1340–1530`). Cierre duro `tl.set(el, { opacity: 0 }, fin)`. |
| 5. Audio | — | `<audio id="voz">` + `<audio id="musica">` + `<audio id="sfx-...">` | Voz entera sin cortes, música con ducking en `data-automation` y SFX colocados desde `cue-sheet.json`. |

**Reglas no negociables de HyperFrames:**
- Todo síncrono y determinista: **cero** `async`/`await`, `fetch()`, `setTimeout`, `Math.random()` o `Date.now()`.
- Toda timeline se crea con `gsap.timeline({ paused: true })` y se registra en `window.__timelines["<composition-id>"] = tl`. Nunca `repeat: -1`.
- Si usás una fuente que HyperFrames no resuelve sola (por ej. `Archivo`, `Rajdhani`, `Instrument Serif`), descargá el `.ttf`/`.woff2` (OFL) en `montaje/fonts/` y declaralo con `@font-face` (`url('../fonts/...')` desde `compositions/`).

## 2. Anclar a palabras de `base-palabras.json`

Nunca calcules tiempos a ojo: todo sale de `base-palabras.json` (`[{"i": 0, "w": "...", "s": 1.32, "e": 1.89}, ...]`).

- **Gráficos y cortes:** buscá la palabra exacta (adelanta **60 ms** el `data-start` respecto a `s`):
  ```bash
  python3 .claude/skills/montar-video/scripts/anclar_palabra.py proyectos/<nombre>/base-palabras.json --buscar "10%"
  ```
  Sostené al menos **2,6 s** si tiene texto legible (o **1,8–2,6 s** si es apoyo visual).
- **Subtítulos con un estilo del kit** (lo normal): no armes grupos. Copiá `base-palabras.json` a `montaje/` y definí antes de la capa de subtítulos `<script>window.BASE_PALABRAS = [...];</script>` (el `subtitulos.html` del estilo y el de la plantilla lo leen solos).
- **Subtítulos a medida:** agrupá con `scripts/armar_subtitulos.py` respetando puntuación, pausas > 260 ms y cortes de plano.

## 3. Aplicar estilos: kit propio vs estética de Lemo

- **Estilo del kit (`estilos/<nombre>/ESTILO.md`):** leé sus reglas numéricas, copiá `subtitulos.html` tal cual a `compositions/subtitulos.html` (montado como dice `estilos/README.md`, `data-track-kind="captions"`), y armá en las capas 2 y 3 lo demás que pida el estilo.
- **Estética de Lemo encima del video:** chequeá en `.claude/skills/editar-video/catalogo/lemo.md` que tenga **Encima de video = sí**, leé `.externas/lemo-opuscar/styles/<slug>/STYLE.md` y **traducí la estética a HTML/CSS/GSAP nativo transparente**. Nunca metas el `index.html` del demo de Lemo adentro de HyperFrames (usa `window.render(t)`, `await` y lienzos opacos de `1920×1080`).

## 4. Cortes a pantalla completa: ¿HyperFrames o MP4 de Lemo?

| Escribir la escena en **HyperFrames** | Renderizar un **MP4 con Lemo** |
|---|---|
| Tipografía, tarjetas de datos, gráficos 2D, comparaciones, estilos del kit (`swiss-motion`, `dark-keynote`, `dataviz`). | Dibujo complejo del motor de Lemo: 3D Three.js (`brick-toy`, `thermal-camera`), shaders WebGL (`neon-tubes`, `ascii-crt`, `ink-wash`), pinceladas o física. Verificá en `catalogo/lemo.md` que sirva en vertical (`sí` o `adaptando`). |

**Una escena de corte llena el 9:16 entero:** repartí el contenido en todo el alto o agrandá la pieza principal (nada de tarjeta chica arriba con media pantalla vacía).

**Para insertar un MP4 de Lemo:** creá una carpeta con `window.DUR = <duracion_exacta>` dibujando contra `innerWidth × innerHeight`, renderizá desde `.externas/lemo-opuscar/`:
```bash
node core/render/video.mjs <ruta-corte-lemo> --size 1080x1920 --fps 30 --workers 3 --out <salida>/montaje/corte-lemo.mp4
```
*(En máquinas sin GPU WebGL, anteponé `LEMO_ANGLE=swiftshader`.)* Insertalo como `<video>` hijo directo en `index.html`, sin `<div>` con `data-start` envolviéndolo.

## 5. Sonido: cue sheet de SFX, banco CC0 y música

Solo una vez aprobada la imagen (o al armar v1 si la persona pidió todo junto):

### a) Banco local de SFX CC0 (gratis, sin cuenta, nunca en git)
Los efectos viven en `.externas/sfx/{whooshes,texturas,risers-hits}/` (ignorado por git). Dos rutas gratuitas sin cuenta:
1. **Openverse API (CC0 de Freesound, sin registro):**
   ```bash
   python3 .claude/skills/montar-video/scripts/bajar_sfx_cc0.py --destino .externas/sfx
   ```
   Baja muestras CC0 reales a las 3 familias y escribe `.externas/sfx/CREDITS.md`.
2. **Skill `media-use` de HyperFrames (Openverse + 21 archivos offline):** `npx hyperframes media-use resolve --type sfx --query "whoosh"`, o copiá su librería offline con `--desde-media-use <ruta-media-use>/assets/sfx`.

### b) `cue-sheet.json` antes de mezclar
Armá primero `<salida>/cue-sheet.json` en 3 pasadas (**whoosh** −10 a −12 dB en transiciones/cortes, **textura** −6 a −10 dB en entradas de texto/UI, **riser-hit** −5 dB en cambios de sección, alineando el pico al cuadro más rápido):
```json
{
  "cues": [
    { "t": 1.44, "evento": "Entra tarjeta indicador", "familia": "textura", "archivo": "sfx/pop.mp3", "db": -8 },
    { "t": 5.94, "evento": "Corte a escena dato clave", "familia": "whoosh", "archivo": "sfx/whoosh.mp3", "db": -11 }
  ]
}
```
Copiá los archivos usados a `<salida>/montaje/sfx/` y generá las etiquetas `<audio>` (convierte `db` → `data-volume` y colapsa cues a < 90 ms con prioridad `riser-hit > whoosh > textura`):
```bash
python3 .claude/skills/montar-video/scripts/cue_a_audio.py proyectos/<nombre>/cue-sheet.json \
  --base-dir proyectos/<nombre>/montaje --track-inicio 6
```
Pegá las etiquetas `<audio id="sfx-...">` en la Capa 5 de `index.html`.

### c) Audición musical y ducking
No pongas música si la persona no pidió ni dio pistas libres de derechos. Si tiene 3–5 pistas candidatas, generá previews de **10 s** mezclados sobre el arranque real del clip para que elija de oído:
```bash
python3 .claude/skills/montar-video/scripts/audicionar_musica.py proyectos/<nombre>/base.mp4 \
  proyectos/<nombre>/pistas-musica/ --out-dir proyectos/<nombre>/previews-musica --duracion 10
```
Con la pista elegida copiada a `montaje/`, generá el ducking (`data-automation`, sin `data-volume` aparte porque se multiplican):
```bash
python3 .claude/skills/montar-video/scripts/generar_ducking.py CLIP/base-palabras.json \
  --volumen-base 0.35 --volumen-voz 0.14 --ataque 0.15 --release 0.40 --html-attr
```
Objetivo (`criterio/sonido.md`): voz a −14 LUFS, música ~10 dB abajo bajo habla (piso −6 dB en frases suaves), fades de 0,4 s. Si alguna vez usás `ffmpeg sidechaincompress`, agregá 3 s de relleno al final de ambas entradas y recortá después.

## 6. Controles obligatorios antes de renderizar

```bash
npx hyperframes lint CLIP/montaje
npx hyperframes check CLIP/montaje --at 0.5,2.0,6.5,12.0
```
*(En 0.9.90 `check` reemplaza a `validate` + `inspect`, que siguen disponibles como alias.)*
- **`lint`:** tiene que dar **0 errores**.
- **`check`:** verifica consola limpia, contraste WCAG AA, desbordes de layout y piso tipográfico (≥ 28 px en 1080×1920). Marcá desbordes de entrada/salida con `data-layout-allow-overflow` y decorativos con `data-layout-ignore`.

Recién cuando pasan limpios:
```bash
npx hyperframes render CLIP/montaje --fps <fps de base.mp4> --quality high --output CLIP/final.mp4
```
Después pasale `CLIP/final.mp4` a `revisar-export`, con `--palabras CLIP/montaje/base-palabras.json` (la copia del montaje, que tiene las correcciones de palabras).

## 7. Variante Remotion (solo si la persona lo pide)

Si la persona ya trabaja en React o pide Remotion:
- Instalá skills con `npx -y skills add remotion-dev/skills` y avisá la licencia (gratis para personas y equipos ≤ 3; empresas mayores pagan licencia).
- Mismas 5 capas: `<OffthreadVideo muted />` (persona y cortes Lemo), capa de tercio inferior CSS, `<Sequence>` para escenas/gráficos, subtítulos con tiempos pasados a cuadros (`Math.round(segundos * fps)`), y `<Audio>` para voz, música (`volume={(f) => ...}`) y SFX del `cue-sheet.json`. No mezcles Remotion dentro de un proyecto HyperFrames.

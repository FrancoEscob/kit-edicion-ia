# Pruebas reales: Lemo-Opuscar + HyperFrames

Resultados medidos sobre **HyperFrames `0.9.90`** y **Lemo-Opuscar** (commit `8ca0dd805e214bcc1d30714cd5b9d21cc02a454b`, instalado en `.externas/lemo-opuscar/`).

Entorno de medición: Linux x64, AMD Ryzen 5 5600G (12 hilos, Radeon integrada con WebGL hardware via ANGLE/OpenGL ES 3.2), Node v26.8.2, FFmpeg n9.0.1, Python 3.12 (`.externas/lemo-opuscar/.venv`). Todos los artefactos de prueba quedaron en `proyectos/prueba-montaje/` (ignorado por git).

---

## Prueba 1a — Auditoría de los 99 estilos de Lemo en vertical (1080×1920) y 6 renders reales

### Hallazgo central al leer el código de los 99 demos

Lemo acepta `--size 1080x1920` en `core/render/video.mjs`, pero al inspeccionar el código fuente (`demo/index.html`, `*.js`, `*.mjs`, `film.py`) de los **99 estilos**:

- **Solo 13 demos de 99** leen `innerWidth`/`innerHeight` dinámicamente: `briefing-board`, `chalkboard`, `double-exposure`, `flow-field`, `instruction-manual`, `neon-tubes`, `one-bit-dither`, `pen-plotter`, `printed-long-take`, `security-xray`, `silhouette-rhythm`, `thermal-camera`, `transit-map`.
  - Aun dentro de esos 13, varios asumen proporción 16:9 internamente: `double-exposure` proyecta `gl_FragCoord.xy / uRes * vec2(1920., 1080.)` (estira), `transit-map` dibuja su overlay fijo en `1920×1080`, `instruction-manual` y `flow-field` mantienen `W = 1920, H = 1080` en sus módulos de lógica.
- **83 demos de 99** fijan `1920` y `1080` en código (canvas 2D o Three.js con `width="1920" height="1080"` o `W = 1920, H = 1080`).
- **3 demos de 99** no se renderizan con el navegador sino con Python + ffmpeg: `city-symphony` (`tools/render.py`, `index.html` solo expone `texts.json` para `readcheck`), `firefly-pointillism` (`film.py`) y `oscilloscope-math` (`film.py`), los tres con coordenadas fijas de 1080p.
- **Solo 3 estilos de 99** declaran `"needs": ["image-generation"]` (producción **G**): `text-flash-cuts`, `comic-history` y `manga-panels`. Según el README y `core/README.md` de Lemo, requieren **Codex CLI (`codex login`) en una cuenta con generación de imágenes habilitada** (`core/image/gen_image.py`), u otro generador de imágenes externo/API.

### Clasificación global de los 99 estilos (detalle completo en `.claude/skills/editar-video/catalogo/lemo.md`)

Como Lemo no ejecuta el demo tal cual sino que Claude escribe un `index.html` nuevo siguiendo `STYLE.md` + `TECHNIQUE.md` (leyendo `innerWidth`/`innerHeight`), la tabla del catálogo separa tres niveles para vertical y dos para uso encima de video:

| Dimensión | Conteo | Criterio |
|---|---:|---|
| **Vertical 9:16 — `sí`** | **54** | La estética y composición del `STYLE.md` encajan naturalmente en 1080×1920 (sujeto central, columna vertical, tarjetas, 3D con cámara libre, trazos sobre lienzo). Al generar una pieza nueva hay que dibujar desde `innerWidth × innerHeight`. |
| **Vertical 9:16 — `adaptando`** | **33** | El `STYLE.md` asume pliegos izquierda-derecha, pizarras anchas o recorridos horizontales, pero funciona en 9:16 rearmando el layout arriba/abajo al escribir la página. |
| **Vertical 9:16 — `no`** | **12** | La mecánica central depende del ancho horizontal o de un marco 4:3 fijo (`countdown`, `shadow-puppet`, `paper-lantern`, `printed-long-take`, `assembly-line-diagram`, `silent-film`, `backrooms`, `living-screencast`, `desktop-flythrough`, `spreadsheet`, `briefing-board`, `archive-lighttable`). |
| **Encima de video — `sí`** | **47** | Su gramática visual (tarjetas, tipografía, trazos, flechas, HUD, diagramas, sellos, datos) se sostiene traducida a HyperFrames con fondo transparente sobre una persona hablando. |
| **Encima de video — `no`** | **52** | El estilo es un mundo opaco completo (pintura, 3D, maqueta, térmica, rayos X, película de archivo); sirve como corte a pantalla completa o pieza 100% animada, no flotando encima. |
| **Generador pago (`G`)** | **3** | `text-flash-cuts`, `comic-history`, `manga-panels`. Los otros **96** son 100% locales sin generación paga. |

### 6 renders reales a `1080×1920`, 5 s, 24 fps (120 cuadros) con `core/render/video.mjs`

Para evitar arrancar sobre intros en negro, cada demo se copió a `proyectos/prueba-montaje/lemo-vertical/<slug>/` con un shim mínimo que fija `window.DUR = 5.0` y desplaza `t` hacia la acción media (sin tocar la lógica de tamaño del demo).

**Trampa operativa detectada al primer intento:** los 6 renders fallaron con `exit 1` en el primer intento porque **Lemo no guarda fuentes ni HDRIs en git** (`404` en `/@film/fonts/*.ttf` y en `/core/assets/polyhaven/photo_studio_loft_hall_2k.hdr`). Tras correr el `tools/fonts.sh` de cada demo (o bajar las fuentes OFL desde GitHub) y `sh tools/fetch.sh hdri` (13 MB), los **6 renders terminaron con código 0**:

| Estilo | Motor / Tamaño en código | Tiempo (5 s, 24 fps, 3 workers) | Peso MP4 | Qué se vio en los cuadros (`1080×1920`) |
|---|---|---:|---:|---|
| `swiss-motion` | Canvas 2D, fijo `1920×1080` | **2,52 s** | 163 KB | **Roto en vertical:** solo se ve el recorte superior-izquierdo `1080×1080`; la mitad derecha del pliego queda cortada y los 840 px inferiores quedan en gris vacío. |
| `whiteboard` | Canvas 2D, fijo `1920×1080` | **5,52 s** | 2,8 MB | **Roto en vertical:** el texto `"EINSTEIN IN YOUR POCKET"` se corta a la derecha (`"EINSTE..."`) y los 840 px inferiores son **negro sólido**. |
| `dataviz` | Canvas 2D, fijo `1920×1080` | **4,16 s** | 4,1 MB | **Roto en vertical:** el gráfico se dibuja en la mitad superior (cortado a la derecha) y los 840 px inferiores quedan como papel vacío. |
| `brick-toy` | Three.js 3D, fijo `1920×1080` | **35,09 s** | 2,4 MB | **Roto en vertical:** pese a ser 3D, el renderer está fijo en `1920×1080`; el cohete se corta a la derecha y los 840 px inferiores son **negro sólido**. |
| `neon-tubes` | Canvas 2D/GL con `innerWidth`/`innerHeight` | **6,85 s** | 7,4 MB | **Funciona a pantalla completa:** llena todo `1080×1920` sin franjas negras ni cortes abajo (neones, gato saltando, reflejo en la calle mojada). Solo carteles laterales del demo quedan cerca del borde porque la calle fue pensada para 16:9. |
| `thermal-camera` | Three.js 3D con `innerWidth`/`innerHeight` y `camera.aspect = W/H` | **17,19 s** | 26 MB | **Funciona excelente a pantalla completa:** fachada térmica completa en `1080×1920` con retícula y barra de temperatura. Solo la etiqueta numérica derecha queda pegada al borde por margen 16:9. |

Artefactos: `proyectos/prueba-montaje/lemo-vertical/<slug>-1080x1920.mp4` y hojas de 4 cuadros `proyectos/prueba-montaje/lemo-vertical/<slug>-sheet.jpg`.

---

## Prueba 1b — Dos estilos de Lemo traducidos a gráficos ENCIMA del video en HyperFrames nativo

Se eligieron dos estilos bien distintos de Lemo (`swiss-motion` y `hologram-hud`), se leyó su `STYLE.md` real en `.externas/lemo-opuscar/styles/<slug>/STYLE.md` y se escribió cada uno como sub-composición nativa de HyperFrames con fondo transparente, anclada a palabras de `base-palabras.json` (`s - 0,06 s`) sobre el video de la persona hablando.

| Estilo de Lemo | Archivo creado | Líneas | Anclaje en `base-palabras.json` | Fidelidad al `STYLE.md` | Trabajo real |
|---|---|---:|---|---|---|
| `swiss-motion` | `montaje/compositions/overlay-swiss.html` | **130** | `i=4` `"10%"` (`s=1,32 s` → entra `1,26 s`, dura `3,10 s`) | **Alta (~90%):** papel plano `#EAE9E5`, tinta `#111111`, un único color señal `#E30613`, neo-grotesca `Archivo` (OFL local vía `@font-face`), `tabular-nums`, entrada/salida por `clip-path` seco sin bounce ni sombras ni gradientes, contador en pasos discretos (`steps(5)`). | ~5 min. Muy directo en CSS/GSAP; lo único extra fue bajar `Archivo-VF.ttf` y declararlo con `@font-face` porque HyperFrames no lo autoresuelve. |
| `hologram-hud` | `montaje/compositions/overlay-hud.html` | **191** | `i=43` `"8"` (`s=12,07 s` → entra `12,01 s`, dura `3,60 s`) | **Alta (~85%):** placa oscura traslúcida `rgba(6,14,20,0.88)`, borde 1 px cian `#3EE8FF`, esquineros HUD, línea líder SVG con anillo de anclaje dibujándose, `Rajdhani` + `IBM Plex Mono`, dígitos que escanean y **solo cambian al acento cálido `#FF9E44` en el instante de `LOCKED`** (regla exacta de la sección 3 del `STYLE.md`). No incluye el wireframe 3D giratorio del demo porque encima de una persona distraería. | ~8 min. Exige un poco más de CSS/SVG y 3 fuentes `@font-face` (`Rajdhani-Bold`, `IBMPlexMono-Medium/Bold`), pero queda muy fiel y liviano. |

**Conclusión de 1b:** traducir la estética de un `STYLE.md` de Lemo a un gráfico transparente en HyperFrames lleva entre **130 y 190 líneas** (~5–10 min por pieza) y logra una fidelidad muy alta en tipografía, paleta, geometría y curva de movimiento, con la enorme ventaja de sincronizarse al milisegundo con `base-palabras.json` dentro de la misma timeline de HyperFrames.

---

## Prueba 1c — Reel completo de punta a punta (5 capas + 3 mezclas + subtítulos + ducking)

### Preparación de la base

- **Fuente:** tramo `937,45 s..963,15 s` (**25,7 s** continuos a cámara) de `yt-5UnK3c-nlIs.mp4`, recortado a 9:16 centrado (`1080×1920`, 30 fps) y normalizado con `loudnorm` a −14 LUFS → `proyectos/prueba-montaje/base.mp4`.
- **Transcripción:** `npx hyperframes transcribe base.mp4 --model small.en --language en` → **92 palabras** en `transcript.json` (convertido a formato contrato en `base-palabras.json`).
  - *Nota CLI:* `hyperframes transcribe` ignoró `--output base-transcript.json` y escribió siempre `transcript.json` en la carpeta actual.
- **Corte Lemo nativo:** `corte-lemo.mp4` renderizado con `node core/render/video.mjs` (`neon-tubes`, `--size 1080x1920 --fps 30`, `window.DUR = 3.2`) en **8,30 s** (96 cuadros exactos, `3,200 s`).
- **Música:** pista ambiental original `musica.wav` (27 s, 48 kHz, −24,1 dBFS RMS) con envolvente `data-automation` generada por `.claude/skills/montar-video/scripts/generar_ducking.py` (`vol_base = 0,35`, `vol_voz = 0,14` bajo habla, ataque `0,15 s`, release `0,40 s`).

### Composición de 5 capas (`proyectos/prueba-montaje/montaje/`)

1. **Capa 1 (`z=1`):** `base.mp4` (`muted playsinline`).
2. **Capa 2 (`z=10–11`):** dos cortes a pantalla completa (6,4 s totales = **24,9%** del reel, debajo del tope del 30%):
   - `7,42..10,62 s` (3,2 s, anclado a `"1"`): escena propia en HyperFrames (`compositions/escena-swiss.html`, estética `swiss-motion`, `$1–$5`).
   - `19,02..22,22 s` (3,2 s, anclado a `"visual"`): clip MP4 nativo de Lemo (`corte-lemo.mp4`, `neon-tubes` 1080×1920).
3. **Capa 3 (`z=20`):** los dos gráficos transparentes encima (`overlay-swiss.html` en `1,26..4,36 s` y `overlay-hud.html` en `12,01..15,61 s`).
4. **Capa 4 (`z=30`):** subtítulos palabra por palabra (`compositions/subtitulos.html`, 39 grupos de 1–3 palabras, cierre duro `tl.set(el, { opacity: 0 }, g.end)`, zona segura `left: 90px; width: 840px; top: 1200px`).
5. **Capa 5 (audio):** `<audio id="voz" src="base.mp4">` + `<audio id="musica" src="musica.wav" data-automation="...">`.

### Errores atrapados por `lint` antes de renderizar

En la primera versión (todo en un solo `index.html`) `npx hyperframes lint` detectó 2 errores reales y 5 avisos:
1. `video_nested_in_timed_element`: anidar `<video id="corte-lemo" data-start=...>` dentro de un `<div data-start=...>` desfasaría la extracción de cuadros. **Solución:** `<video>` como hijo directo sin wrapper con `data-start`.
2. `font_family_without_font_face`: `Archivo` y `Rajdhani` (y `Space Grotesk` en la plantilla inicial) no están en la lista autoresuelta de HyperFrames. **Solución:** `@font-face` apuntando a `.ttf` locales en `montaje/fonts/` (y `Inter` en la plantilla base).
3. Al mover overlays, escena y subtítulos a `compositions/*.html`, el resultado pasó a:
   - `npx hyperframes lint montaje`: **0 errors, 0 warnings** (5 archivos).
   - `npx hyperframes validate montaje`: **No console errors · 27 text elements pass WCAG AA**.
   - `npx hyperframes inspect montaje --at 0.5,2.0,5.0,8.4,12.8,17.0,20.4,24.0`: **0 layout issues across 8 sample(s)**.
   - *(En `0.9.90`, tanto `validate` como `inspect` avisan que quedan unificados en `npx hyperframes check`.)*

### Resultados del render final (`proyectos/prueba-montaje/final.mp4`)

- **Tiempo de render:** **66,5 s** internos de HyperFrames (**68,32 s** de pared) para **771 cuadros** (`25,7 s`, `1080×1920`, `30 fps`, `--quality standard`), **13,2 MB** (H.264 4,09 Mbps + AAC 48 kHz 202 kbps).
  - *Nota de velocidad:* cayó a modo `screenshot` porque el sistema usa `/usr/bin/google-chrome-stable` en lugar de `chrome-headless-shell` (`HeadlessExperimental.beginFrame` solo está en `chrome-headless-shell`). Con `chrome-headless-shell` es sensiblemente más rápido.
- **Sonoridad (`ffmpeg ebur128`):** integrado **−13,8 LUFS**, pico real **−1,3 dBFS**, LRA **2,2 LU** (en objetivo −14 LUFS). RMS mono de voz: `−13,8 dBFS`; música ducked bajo voz estimada en `−41,2 dBFS` (~27 dB debajo, voz 100% limpia; `final.mp4` mantiene `−13,8 dBFS`).
- **Cuadros negros (`blackdetect`):** **0 cuadros negros**.
- **Desfase medido entre subtítulos y voz:**
  - **Desfase del audio renderizado** (re-transcripción de `final.mp4` con Whisper vs `base-palabras.json`, 92/92 palabras coincidentes): **media −0,8 ms, mediana 0,0 ms, p95 10,0 ms, máximo absoluto 60,0 ms** → HyperFrames no introduce deriva de audio.
  - **Desfase visual de los subtítulos** (detección pixel a pixel en la banda `y=1200..1380` de `final.mp4` del primer cuadro donde aparecen píxeles nuevos amarillos `#FFE600` en 10 palabras ancla repartidas a lo largo de los 25,7 s, comparado contra el inicio de cada palabra en el audio de `final.mp4`):
    - **Media: +49,7 ms · Mediana: +50,0 ms · Rango: +30,0 ms a +93,3 ms** (1 a 3 cuadros a 30 fps).
    - El corrimiento constante de ~+50 ms viene del tween de color de 40 ms (`duration: 0.04`) que cruza el umbral amarillo 1–2 cuadros después de `w.s`. Queda muy por debajo del umbral de ±150 ms de `criterio/subtitulos.md` y, si se quiere acercar a 0 ms, basta cambiar ese tween por `tl.set` (instantáneo).
- **Inspección visual de los cuadros (`hoja-final.jpg` y `hero-1..4`):**
  - El orador se ve nítido y centrado en los tramos a cámara; ojos y boca nunca quedan tapados por tarjetas ni subtítulos.
  - `hero-1-overlay-swiss.jpg` (`2,2 s`): tarjeta `<10%` de `swiss-motion` flota limpia arriba de la frente; subtítulo `"my max plans"` nítido abajo con `"my"` en amarillo.
  - `hero-2-escena-hf.jpg` (`8,6 s`): escena fullscreen `$1–$5` con retícula suiza de 6 columnas y barra roja, sin solapar el subtítulo `"5 dollars per"`.
  - `hero-3-overlay-hud.jpg` (`13,0 s`): placa `hologram-hud` con `08 YRS` trabado en ámbar `#FF9E44`, esquineros cian y línea líder apuntando hacia el orador.
  - `hero-4-corte-lemo.jpg` (`20,6 s`): clip nativo `neon-tubes` de Lemo a pantalla completa 9:16 con subtítulo `"training,"` legible encima.

### Rutas de artefactos generados

- Reel final: `proyectos/prueba-montaje/final.mp4`
- Hoja de 16 cuadros del reel: `proyectos/prueba-montaje/hoja-final.jpg`
- Cuadros héroe: `proyectos/prueba-montaje/hero-1-overlay-swiss.jpg`, `hero-2-escena-hf.jpg`, `hero-3-overlay-hud.jpg`, `hero-4-corte-lemo.jpg`
- Corte Lemo nativo (3,2 s): `proyectos/prueba-montaje/montaje/corte-lemo.mp4`
- 6 pruebas verticales Lemo (5 s c/u): `proyectos/prueba-montaje/lemo-vertical/<slug>-1080x1920.mp4` y `proyectos/prueba-montaje/lemo-vertical/<slug>-sheet.jpg` (`swiss-motion`, `whiteboard`, `dataviz`, `neon-tubes`, `thermal-camera`, `brick-toy`).

---

## Riesgos concretos para Mac y Windows

1. **FFmpeg 7+ obligatorio en Lemo (y diferencias de versión en HyperFrames):**
   - `TECHNIQUE.md` de Lemo exige **FFmpeg 7+** porque en 6.x `loudnorm` sub-reporta duración y `mux.sh` rechaza el archivo. En Ubuntu 24.04 y en instalaciones viejas de Windows/Mac con Homebrew viejo suele haber FFmpeg 6.
   - HyperFrames 0.9.90 avisa que las mediciones de loudness solo son exactamente comparables en FFmpeg 8.0.1.
2. **Navegador headless (`chrome-headless-shell` vs Chrome del sistema):**
   - En Mac/Windows sin `chrome-headless-shell`, HyperFrames cae a modo `screenshot` (~3–5× más lento, como se vio acá: 66,5 s para 25,7 s). El setup del kit conviene instalar `npx @puppeteer/browsers install chrome-headless-shell` (o apuntar `HYPERFRAMES_BROWSER_PATH`).
   - En Lemo, `setup.sh deps` instala el `chromium-headless-shell` exacto de su `playwright-core`. No mezclar con `npx playwright install` global porque instala otra versión y Lemo falla.
3. **WebGL y GPU en Windows / Macs Intel / VMs:**
   - Lemo fuerza `--use-angle=metal` en macOS (Apple Silicon anda rápido). En Windows con GPU integrada vieja o en VMs/WSL, Chrome puede abrir WebGL y soltar el contexto (`webglcontextlost`, cuadros en blanco). La salida de emergencia es `LEMO_ANGLE=swiftshader`, que funciona pero multiplica el tiempo de render 3D (~5–6× más lento).
4. **Windows: Git Bash, rutas largas, permisos y UTF-8:**
   - Todos los scripts de Lemo (`setup.sh`, `mux.sh`, `fetch.sh`) son POSIX `sh`: en Windows requieren **Git Bash** (con `MSYS_NO_PATHCONV=1` para `sparse-checkout`, ya contemplado en `setup.sh`) o **WSL**. PowerShell nativo no los ejecuta tal cual.
   - Lemo documenta un límite de **160 bytes** de ruta para `espeak-ng` (Kokoro TTS) y bloqueos `EBUSY` al borrar carpetas temporales de `ffmpeg` en Windows (`video.mjs` hace reintentos con `maxRetries: 10`). Conviene instalar el kit en una ruta corta (ej. `C:\kit-video\`).
   - En Windows con locale no UTF-8, Python requiere `PYTHONUTF8=1` (los scripts de `montar-video` abren JSON con `encoding="utf-8"` explícito para evitar errores de acentos/tildes).
5. **Fuentes no incluidas en git y red durante la clase:**
   - Ni los demos de Lemo ni HyperFrames (fuera de su lista autoresuelta como `Inter`) traen fuentes como `Archivo`, `Rajdhani` o `IBM Plex Mono`. Si el Wi-Fi del aula bloquea o enlentece GitHub/Google Fonts, los renders fallan con `404` o `font_family_without_font_face`. Conviene pre-cachear las fuentes OFL más usadas o validar offline antes de la clase.
6. **Python < 3.14 para el tier de voz de Lemo:**
   - `setup.sh` avisa que `kokoro-onnx` requiere Python **3.11–3.13** (`< 3.14`). Si un alumno tiene solo Python 3.14 (como esta máquina), `uv venv --python 3.12` lo resuelve automático, pero sin `uv` fallaría el tier `voice`.
7. **Licencias de Lemo y Remotion en cursos pagos:**
   - El código de Lemo es MIT, pero sus `STYLE.md` y documentación son **CC BY-NC 4.0** (ver `catalogos-estilos.md`). Por eso el kit **no copia** `STYLE.md` al repo: cada alumno baja Lemo desde origen a `.externas/lemo-opuscar/` (ignorado por git).
   - Remotion es gratis para uso individual y equipos de hasta 3 personas; empresas mayores requieren licencia comercial.

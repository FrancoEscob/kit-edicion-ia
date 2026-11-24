# Estilos del kit

Cada estilo define una apariencia completa y medible para los subtítulos y, cuando corresponde, para los gráficos, b-roll, textura, color y componentes que `montar-video` arma en HyperFrames.

## Formato de un estilo

Cada estilo vive en su propia carpeta `estilos/<nombre>/`:

```text
estilos/<nombre>/
  ESTILO.md         # obligatorio: qué se ve, para qué sirve, de dónde sale y reglas con números
  subtitulos.html   # opcional (presente en los 8 del kit): bloque HyperFrames palabra por palabra
  paletas.json      # opcional: paleta fija o regla de extracción dinámica desde el A-roll
  primitivas/       # opcional: componentes HyperFrames reutilizables del estilo
  referencias/      # opcional: fichas indexadas de escenas clave (still + keyframes + ficha.md)
  ejemplo/          # opcional: composición mínima de muestra
```

### Detalle de cada pieza

- **`ESTILO.md`** (obligatorio): qué se ve, para qué material sirve, en qué se basa, y todas las reglas con números (tipografía, tamaños, posición, palabras por subtítulo, entradas y salidas en ms, colores, sombra y reglas de composición, gráficos, b-roll, óptica o color para `montar-video`).
- **`subtitulos.html`** (opcional, incluido en los 8 estilos del kit): sub-composición `<template>` de HyperFrames con `data-composition-id="captions"`, lista para montar sobre `base.mp4` leyendo los tiempos desde `base-palabras.json`.
- **`paletas.json`** (opcional): define los 4 roles de color del estilo (acento claro, acento oscuro, blanco teñido, negro teñido) de forma fija o como regla de extracción desde `informe.json` → `paletas` (que genera `preparar-video` a partir del A-roll).
- **`primitivas/`** (opcional): componentes HTML/GSAP/SVG reutilizables propios del estilo para que `montar-video` no los reescriba de cero en cada video (por ejemplo: `lower-third.html`, `tarjeta-dato.html`, `selector-broll.html`, `texturas.svg`).
- **`referencias/`** (opcional): biblioteca indexada de escenas de muestra del estilo; cada subcarpeta (`<id>/`) guarda `still.jpg` (cuadro representativo), `keyframes.jpg` (tira de entrada/desarrollo) y `ficha.md` (medidas en px, hex, duración en cuadros/ms y cuándo usarla).
- **`ejemplo/`** (opcional): una composición mínima de muestra.

Los estilos propios que crea cada alumno con la skill `mi-estilo` se guardan en `estilos/propios/` (ignorado por git) usando exactamente este mismo formato.

## Cómo usa `montar-video` el archivo `subtitulos.html`

1. Copiá `estilos/<nombre>/subtitulos.html` dentro de `salida/montaje/compositions/subtitulos.html`.
2. Asegurate de que `base-palabras.json` esté disponible en `salida/montaje/base-palabras.json` (con el formato del contrato: `[{"i": 0, "w": "hola", "s": 0.12, "e": 0.38}, ...]`, o inyectado antes en `window.BASE_PALABRAS`). Si el estilo usa paleta derivada del A-roll (como `editorial`), copiá también `informe.json` en `salida/montaje/informe.json` (o definí `window.PALETA_EDITORIAL`).
3. Montalo en `salida/montaje/index.html` como capa de subtítulos sobre el video:

```html
<div
  id="capa-subtitulos"
  class="clip"
  data-composition-id="captions"
  data-composition-src="compositions/subtitulos.html"
  data-track-kind="captions"
  data-start="0"
  data-duration="30"
  data-track-index="4"
></div>
```

4. Si el estilo trae `primitivas/`, `paletas.json` o reglas adicionales en `ESTILO.md` (b-roll, tarjetas de prueba, contadores, grilla de archivo, desenfoque de borde o color), `montar-video` las arma en capas debajo de `capa-subtitulos`.
5. Verificá siempre con `npx -y hyperframes@0.9.90 lint <carpeta-montaje>` antes de renderizar.

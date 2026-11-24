---
name: editar-video
description: Punto de entrada para cualquier pedido de video en este kit — editar un video grabado, sacar clips de un podcast o una charla, poner subtítulos, agregar gráficos o animaciones encima, hacer un video animado desde cero, elegir o mostrar estilos, o cambiar algo de un video ya hecho. Úsala antes que cualquier otra skill de video; decide el camino, el motor y el estilo, y llama a las demás.
---

# Editar video

Sos el editor. La persona habla en palabras normales ("sacá 3 clips de este podcast", "poné subtítulos como de noticiero", "quiero un explicador animado de 40 segundos") y vos decidís **camino, motor y estilo**, y llamás a las skills que hacen cada parte. No le pidas que nombre skills ni motores.

Antes de empezar, si falta algo del kit (ffmpeg, `.venv/`, HyperFrames, Lemo), corré la skill `setup-kit` y seguí.

## 1. Elegí el camino

| Lo que trae o pide | Camino |
|---|---|
| Un video de alguien hablando, para dejarlo listo (reel, short, YouTube) | **Grabado** |
| Algo largo (podcast, charla, entrevista, live) para sacar clips | **Clips**: skill `clipear-podcast`, que después sigue el camino Grabado por cada clip |
| Gráficos, títulos, números o animación **encima** de un video | **Grabado** con capa de gráficos |
| Un video **sin material grabado**: explicador, intro, película animada, lanzamiento | **Animado** |
| Un arreglo rápido: bajar un video de un link, cortar un tramo, comprimir, pasar a vertical, sacar el audio, unir | **Rápido**: skill `ffmpeg-basico`, sin plan |
| Un link en vez de un archivo (YouTube, Instagram, TikTok, X) | Bajalo primero con `ffmpeg-basico` ("Bajar un video de un link") y seguí con el camino que corresponda |
| Un video de referencia: "quiero que se vea así", "¿cómo está hecho?", "rehacé este video", "armame un estilo con estas referencias" | **Referencias**: skill `referencias` |
| "Mostrame estilos", "qué puedo hacer" | Abrí el catálogo (abajo) y mostrá 3 a 6 opciones que sirvan para su material |

Si no queda claro, preguntá una sola cosa: qué material tiene y dónde se va a publicar.

## 2. Los caminos

### Grabado (persona a cámara)

1. `transcribir`: tiempos palabra por palabra.
2. Decidí qué queda con `criterio/cortes-y-finales.md` (y `criterio/seleccion-y-ganchos.md` si hay que elegir). El plan nombra **palabras, nunca tiempos**.
3. `preparar-video`: cortes, silencios, voz a −14 LUFS y vertical con los ojos en el tercio superior (`criterio/composicion.md`). Sale `base.mp4` + `base-palabras.json` + `informe.json` (con paletas sacadas del video).
4. **Según el pedido:**
   - **Simple** ("poneme subtítulos", "sacá los silencios"): directo a `montar-video` con el estilo elegido.
   - **Producido** (con gráficos, b-roll o escenas): `montar-video` arma primero el **planificador** (un HTML local con el guion línea por línea, donde la persona elige qué va en cada línea y puede pegar capturas de referencia) y la **hoja de subtítulos** para aprobar. Recién después arma las escenas.
5. `montar-video`: arma en HyperFrames las capas (la persona, escenas de corte, gráficos encima, subtítulos y audio) y renderiza `final.mp4`. El sonido (efectos y música) va al final, cuando la imagen está aprobada.
6. `revisar-export`: mide el resultado. Si algo falla, corregí la causa y volvé a renderizar.

### Animado (sin material grabado)

- **Historia animada en primera persona que termina en una elección**: usá `animacion-pov-narrativa` para guion, cámara, manos, sonido y tarjeta final. Si trae un video de referencia nuevo, medilo primero con `referencias`.
- **Con un estilo de Lemo** (los 99 de `catalogo/lemo.md`): usá la skill `lemo-opuscar` con su motor nativo. Hace la película entera, con voz, música y subtítulos propios. Pasale el formato (para vertical: `--size 1080x1920`, solo con estilos marcados "sí" en vertical) y la duración.
- **Con un estilo del kit o algo a medida**: HyperFrames directo (skills de `hyperframes`), o Remotion si la persona lo eligió.
- Después, `revisar-export`.

### La mezcla: persona + animación en el mismo video

Hay tres formas de meter animación en un video hablado, y cada una va por un lado:

1. **Encima de la persona** (como un PNG animado: tarjetas, números, flechas, b-roll en ventana, logo). La persona sigue abajo. Se escribe **en HyperFrames**, con fondo transparente y anclado a una palabra. Si el estilo elegido es de Lemo, tomá la **estética** de su `STYLE.md` (colores, trazo, tipografía, materiales, movimiento) y escribila como código de HyperFrames. No uses el código de su demo: está hecho para su motor y no corre ahí.
2. **Corte a pantalla completa** (se va la persona, entran unos segundos de animación y vuelve). La voz sigue abajo. Si es un estilo del kit o algo simple, escribilo como escena en HyperFrames. Si es un estilo de Lemo con dibujo complejo (WebGL, 3D, pintura), renderizalo con el motor de Lemo a un MP4 con la duración exacta del hueco y metelo como clip.
3. **100% animado**: el camino Animado.

`montar-video` tiene el detalle de cada una.

### Remotion

Solo si la persona lo pide o ya lo usa. Es la misma estructura que HyperFrames, pero en React. Si no está instalado, instalalo con `npx -y skills add remotion-dev/skills` y avisá que es gratis para personas y equipos de hasta 3, y que las empresas más grandes pagan licencia.

## 3. Elegí el estilo

El catálogo está en `catalogo/`:
- `estilos-kit.md`: los estilos del kit para subtítulos y gráficos sobre gente hablando. Son el punto de partida para un reel.
- `lemo.md`: 99 estilos visuales. Dice cuáles andan en vertical, cuáles sirven encima de un video y cuáles piden un generador de imágenes pago.
- `hyperframes.md`: cómo buscar y sumar bloques listos de HyperFrames (gráficos de datos, transiciones, efectos).
- `remotion.md`: qué hay si se usa Remotion.
- `estilos/propios/`: los estilos que creó la persona (con `referencias` o `mi-estilo`). Si existen, ofrecelos primero.

Si la persona trae un video de referencia ("quiero que se vea así"), usá `referencias` para medirlo y destilarlo en un estilo, y después seguí. Si tiene una carpeta en `referencias/<tipo>/` que todavía no se destiló, ofrecelo una vez.

Si un estilo pide algo pago (un generador de imágenes, una voz de pago), avisá antes de usarlo y ofrecé una alternativa gratis.

## 4. Cómo va un trabajo

Leé `criterio/como-va-un-trabajo.md`. En corto:
- Hacé una primera versión completa antes de pulir. No preguntes cada detalle. Una primera versión al 60–70% está bien: la persona la mira entera y te pasa **una lista numerada de cambios con segundos** (y una captura si quiere algo distinto). Aplicala toda junta.
- **No ves ni oís el video.** Todo lo que afirmes del resultado sale de una medición o de mirar una hoja de cuadros. Nunca digas "suena bien".
- Una sola pasada de revisión propia (`revisar-export`) y entregá con una nota corta: qué es, qué estilo usaste, qué se midió y qué no.
- Ante un "cambiá esto", cambiá solo eso y volvé a renderizar. No rehagas lo que ya estaba aprobado.
- Todo va en `proyectos/<nombre>/`. El material original no se toca nunca.

## 5. El criterio

En `criterio/` están las reglas de edición del kit: qué elegir, dónde cortar, subtítulos, gráficos, sonido y revisión. Leé el archivo que corresponda a cada paso. No hace falta leerlos todos de entrada.

# Cómo va un trabajo de principio a fin

Ritmo de trabajo para entregar rápido, validar lo barato antes del render caro, informar con honestidad lo medido y resolver revisiones en una sola pasada sin romper lo ya aprobado.

## 1. Arrancar sin burocracia

- **Hacé como máximo una pregunta**, y solo si sin esa respuesta no podés empezar (por ejemplo, si no está claro qué archivo usar o en qué formato se publica). Si podés tomar una decisión razonable, decidí y aclaralo en una línea al entregar.
- **Mantené el orden del proyecto:** todo vive en `proyectos/<nombre>/` (`transcripcion/`, `clip-1/base.mp4`, `clip-1/montaje/`, `clip-1/final.mp4`). **Nunca modifiques ni borres los archivos originales.**
- **Respetá el formato pedido:** por defecto vertical **1080×1920** (rellenando el cuadro completo alrededor de la cara, nunca barras negras ni fondo borroso a los costados), salvo que pidan horizontal 16:9 u otro formato. Nunca cambies el aspecto por tu cuenta.

## 2. Checkpoint de hoja de subtítulos (en ediciones producidas)

Para pedidos simples ("poneme subtítulos limpios a este clip") pasá directo a v1. En ediciones con múltiples escenas, gráficos o tipografía editorial de dos fuentes, meté un **checkpoint barato antes de armar las escenas**:

- Renderizá primero **solo los subtítulos** y sacá una **hoja de subtítulos** (`6 a 12` cuadros clave sobre `base.mp4`) para que la persona confirme en 30 segundos tipografías, jerarquía de palabras clave, paleta y posición.
- Aprobada esa hoja, recién ahí invertí el tiempo en construir gráficos, b-roll y escenas de pantalla completa.

## 3. Primera versión al 60–70% sin interrumpir

- **Armá la v1 completa de corrido, sin frenar a preguntar cada escena.** Asumí de entrada que una v1 sale al **60–70%** del resultado final: es mucho más rápido corregir sobre un video entero que discutir 15 decisiones en abstracto.
- **Orden del camino grabado:**
  1. `transcribir` → `palabras.json` y `texto.txt`.
  2. Elegir tramos y gancho (por índices de palabra) → `plan.json`.
  3. `preparar-video` → `base.mp4`, `base-palabras.json`, `informe.json`.
  4. Checkpoint de hoja de subtítulos (si es edición producida).
  5. `montar-video` (HyperFrames) → `final.mp4` (primero visual; diseño sonoro por *cue sheet* y previews musicales de 10 s una vez aprobado lo visual).
  6. `revisar-export` → `revision.md` + hoja de cuadros.

## 4. Una sola pasada de revisión propia

Antes de mostrar la v1, hacé **una** revisión completa:

1. Corré `revisar-export` y leé `revision.md`.
2. Re-transcribí el export (o verificá el informe de palabras oídas): buscá frases repetidas, falsos arranques en los primeros 5 s, cortes a mitad de oración, palabras perdidas en empalmes y subtítulos corridos más de 0,15 s.
3. Mirá la hoja de cuadros con foco en regla de tercios (ojos), cara despejada, zona segura, legibilidad, gráficos y primer/último segundo.

- **Un borrador fallado no es una entrega.** Si falló un control automático o viste un error grave (texto sobre la cara, palabra cortada, música trunca), corregí la causa puntual y volvé a verificar antes de entregar.
- **No persigas la perfección en bucle:** corregido lo roto, entregá. Si queda una limitación real (audio muy ruidoso de origen, falta un activo, una medición dudosa), decilo de frente.

## 5. Nota de entrega (3 a 5 líneas)

Al mostrar el video, incluí siempre:

1. **Qué hiciste:** resumen en una línea, duración y estilo usado.
2. **Qué se midió:** números concretos (LUFS, true peak, voz sobre música si hay, controles aprobados, hoja de cuadros revisada).
3. **Qué no se comprobó:** siempre aclarando que el audio no fue escuchado por un humano (y si faltó algún dato o recurso).
4. **Decisiones pendientes:** banderas para la persona (cifras a chequear, terceros en cámara, derechos de música, o selección entre previews musicales).

## 6. Ronda única de revisiones (lista numerada con segundos y capturas)

Cuando entregues la v1, invitá a la persona a juntar **todos** sus cambios en **una sola lista numerada con timestamp exacto y, si hace falta, capturas de referencia** (por ejemplo: `1. 0:04 — acelerar entrada de la tarjeta`, `2. 0:11 — cambiar palabra destacada a "24"`, `3. 0:18 — usar captura adjunta`).

Al recibir la lista:
- **Guardá versiones:** cada ronda genera un archivo nuevo (`final-v2.mp4`, `final-v3.mp4`) sin pisar los anteriores.
- **Aplicá todos los puntos en una sola pasada y cambiá únicamente lo pedido.** No rehagas cortes, color, música ni escenas que ya estaban aprobadas:
  - Cambios de **gancho o texto**: tocá solo ese texto en el montaje y volvé a renderizar. Si te dictan la frase, usala textual.
  - Cambios de **subtítulos, estilo o gráficos**: reutilizá `base.mp4` y `base-palabras.json` sin re-transcribir ni volver a correr `preparar-video`.
  - Cambios de **corte o final**: ajustá solo ese tramo en `plan.json` y actualizá el montaje.
- Volvé a correr `revisar-export` sobre la nueva versión y reportá en una línea qué cambió y qué se midió.

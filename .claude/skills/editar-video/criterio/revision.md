# Revisión antes de entregar

**Claude no ve ni oye el video.** Ninguna afirmación sobre el resultado puede salir de suposiciones: todo sale de las mediciones de `revisar-export` (`revision.md`) y de mirar la hoja de cuadros. Nunca escribas "suena bien" ni "quedó limpio" sin el número atrás.

## 1. Controles medidos obligatorios

Un video se entrega solo cuando pasan los controles automáticos y se miró la hoja de cuadros. Si un control falla, **corregí la causa y volvé a renderizar**; nunca relajes el umbral ni entregues un borrador fallado sin avisar qué falló.

| Control | Pasa cuando | Qué evita |
|---|---|---|
| Última palabra completa | Los últimos **60 ms** de voz caen **≥ 14 dB** respecto del pico de la última palabra | Cortar la última sílaba |
| Música hasta el último cuadro | La pista dura igual que el video y se mantiene dentro de **6 dB** de su cuerpo en el último segundo | Música que muere antes que la imagen |
| Voz sobre música | Mediana **≥ 4,2 dB** (objetivo mezcla: 10 dB) en ventanas de habla de 0,4 s, y **≥ 1,2 dB** (objetivo: 6 dB) en el 15% más suave | Frases suaves tapadas por la música |
| Cero *clipping* en cada pista | Ninguna pista tiene más de **3 muestras ≥ 0,999** | Crujidos y distorsión |
| Volumen final (LUFS) | Dentro de **±0,7 LU** del objetivo (**−14 LUFS** clips / **−10 LUFS** narrados) y true peak ≤ tope (**−1,5** / **−1 dBTP**) | Video demasiado bajo o saturado |
| Imagen y audio sincronizados | Video y audio **decodificado** dentro de **50 ms** entre sí (el encabezado AAC suele sumar ~60 ms falsos) | Final congelado en silencio o corte seco |
| Formato técnico | Resolución pedida (ej. **1080×1920**), H.264 High, `yuv420p`, BT.709, `+faststart`, **10–16 Mb/s**, AAC 256 kb/s 48 kHz | Pixelado o rechazo al subir |
| Sin silencios muertos | Ninguna pausa mayor a **0,55 s** entre palabras | Caída de retención |
| Encuadre parejo | En tramos de la misma toma, el centro del recorte varía **≤ 20%** y el zoom **≤ 0,15** | Saltos bruscos o foco en otra persona |
| Cara despejada | Cada 0,4 s, ningún subtítulo toca la caja de la cara (**+12%** de margen) | Subtítulos sobre boca u ojos |
| Zona segura | Subtítulos dentro de **x = 90–930** y arriba de **y = 1340**; título desde **y ≥ 290**; sin superposición entre textos | Texto tapado por botones de Instagram/TikTok |
| Palabras oídas | Re-transcripción del export coincide **≥ 0,90** con el plan, sin pérdida ni palabras coladas en inicio, final ni empalmes (±1 s), y subtítulos dentro de **±150 ms** | Arranques cortados, "y/pero" colados o subtítulos atrasados |

Controles adicionales recomendados: contraste de texto **≥ 3:1** (**4,5:1** sobre documentos), **cuadro 0** no negro (luma > 0,04) y ya con gancho, y ningún tramo congelado (> 0,5 s) mientras la persona está hablando.

## 2. Revisión visual en la hoja de cuadros

Las mediciones solas han dejado pasar letras cortadas, texto invisible sobre blanco, foco en otra persona o tomas repetidas. Generá la hoja a **4 fps** (o en todos los momentos clave: inicio, cortes, cada gráfico, cierre) más recortes a resolución completa si hay texto chico, y revisá fila por fila:

- **Cara y ojos:** despejados de subtítulos y también del título de gancho (los detectores automáticos suelen omitir el título). El encuadre sigue siempre a la persona correcta.
- **Subtítulos:** legibles tanto en los cuadros más claros como en los más oscuros; centrados en el eje `x = 510`; sin dos grupos ni dos palabras encimadas; sin saltos raros al cambiar de plano.
- **Título de gancho:** tipografía y peso correctos, sin nada atravesando las letras, oculto cuando entra una tarjeta a pantalla completa y retirado tras los ~3 s si corresponde.
- **Gráficos y b-roll:** activos nítidos, encuadrados sin cortar al sujeto, sin subtítulos pisando texto propio del gráfico, vuelta limpia a cámara.
- **Color y continuidad:** piel natural, blancos blancos, negros negros, y tono parejo entre cortes de una misma toma (ojo con doble LUT en tramos insertados).
- **Terceros y repetición:** nadie ajeno en foco sin consentimiento; ninguna foto ni plano repetido dos veces en un montaje.
- **Inicio y cierre:** cuadro 0 con el gancho activo; último cuadro real (no negro); nada de boca moviéndose en silencio ni cuadro congelado bajo habla.
- **Empalmes y astillas:** sin fragmentos menores a 0,6 s entre cortes (1,0 s en cámara en movimiento) y sin muletillas coladas en las uniones.

## 3. Qué informar al entregar

Decí en concreto qué se midió y qué **no** se pudo verificar (por ejemplo: *"−14,1 LUFS, true peak −1,6 dBTP, voz sobre música +8,4 dB mediana y +5,1 dB en frases suaves, duración video/audio 32,40 s / 32,41 s, re-transcripción 98% exacta sin cortes en bordes, hoja de cuadros revisada; no se escuchó con oído humano"*).

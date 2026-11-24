# Estilo: clip-con-pruebas

## Qué se ve

Clip a cámara de ritmo sostenido donde cada dato, sustantivo concreto, cifra o documento mencionado por la persona dispara su prueba visual encima del video cada pocos segundos: fotos reales a pantalla completa, tarjetas con capturas reales, b-roll y contadores numéricos animados con efectos de sonido reales, todo con pila de subtítulos blanca clara y firme abajo.

## Para qué sirve

Clips de entrevistas, historias de proyectos, casos de éxito o argumentos con datos y pruebas reales (capturas, mails, métricas, fotos del proceso) donde mostrar lo que se dice multiplica la retención.

## De dónde sale

Destilado del criterio medido para clips hablados con pruebas visuales disparadas por palabra, ritmo picado y efectos de sonido grabados.

## Reglas de subtítulos con números

- **Canvas de referencia:** 1080×1920 (9:16).
- **Tipografía:** `Inter`, peso `700`/`800` (sustituto abierto de Helvetica Neue Bold en HyperFrames).
- **Color y sombra:** blanco `#FFFFFF`; sombra base `0 2px 10px rgba(0, 0, 0, 0.42)` sobre cámara y **`0 4px 22px rgba(0, 0, 0, 0.90)`** cuando corre b-roll brillante atrás.
- **Tracking:** **−0,05 em** en pila; **−0,04 em** en título de gancho.
- **Jerarquía de pila:**
  - Línea de soporte: **66 px** (peso 700).
  - Palabra de énfasis (números/cifras primero, luego palabra de mayor peso): **136 px** (peso 800).
  - Grupo de palabras cortas/conectores: una línea de **100 px**.
  - Ajuste automático para no exceder **840 px** de ancho (mínimo **56 px**).
- **Posición (zona segura):** eje **x = 510** (rango **x = 90–930**, ancho máximo **840 px**), línea base de énfasis en **y = 1240**, borde inferior **≤ 1340**.
- **Agrupación y movimiento:** máximo **3 palabras** o **16 caracteres**; corte en puntuación, pausas **≥ 260 ms** y en cada corte visual. Entrada tras pausa ≥ **140 ms** con subida **5 px** (soporte) / **12 px** (énfasis) en `min(220 ms, 60%)` (`power3.out`); reemplazo seco en palabras rápidas.
- **Título de gancho (opcional):** **64 px**, va en el tercio inferior en lugar de los subtítulos (ver `criterio/subtitulos.md`), **oculto** siempre que haya una tarjeta de prueba arriba y retirado a los **3 s** si no hay tarjetas.

## Reglas de pruebas, b-roll, contadores y sonido (`montar-video`)

1. **Cadencia y anclaje:**
   - Marcá cada sustantivo concreto, nombre, lugar, cifra y documento en `base-palabras.json`.
   - Meté una prueba visual nueva cada **3–5 s** en el cuerpo del clip (hasta cada **1,5–4 s** en ritmos muy picados; nunca dejes un solo gráfico en 30 s).
   - Cada overlay arranca **60 ms antes** de la primera palabra de la frase que lo dispara.
   - Dejá el **primer segundo** y la **última línea** en la cara de la persona, salvo que el gráfico sea el remate final (o que el gancho nombre una imagen concreta, que entra en 1–2 s).
   - Permanencia mínima: fotos **1,8–2,6 s**; cualquier captura con texto legible (mail, nota, tablero) **≥ 2,6 s**.
2. **Tipos de prueba (siempre material real):**
   - **Foto vertical / b-roll (`broll`):** llena el cuadro 1080×1920 (*cover crop* cuidando el sujeto), banda inferior de subtítulos oscurecida suavemente y grano liviano; los subtítulos siguen corriendo arriba con sombra más firme.
   - **Tarjeta de prueba apaisada (`card` — mails, titulares, capturas):** activo grande y nítido en la mitad superior (**y = 300–1040**, centrado en **x = 510**) sobre una copia oscura y desenfocada de sí mismo o sobre una tarjeta de color de marca con grilla fina, grano y viñeta. Entra firme al corte y hace un *push-in* lento. Oculta el título de gancho. **Nunca** pongas una foto chiquita pegada en una placa plana.
   - **Contador numérico (`number`):** cifra grande en `tabular-nums` subiendo en **10 pasos de 70 ms** (con prefijo/sufijo y etiqueta corta debajo), sobre tarjeta limpia en la mitad superior.
   - **Prohibido:** UI inventada, caras generadas por IA, pastillas de texto estáticas o cifras sin verificar. Si no existe prueba real para una frase, dejá el plano de cámara o usá un diagrama animado simple con movimiento real.
3. **Sonido sobre los eventos visuales:**
   - Usá grabaciones reales (CC0 / CC BY): **obturador de cámara** al cortar a gráfico o tarjeta, **tick seco** en cada paso del contador (~70–200 ms), **pop suave** al aterrizar un elemento.
   - Colapsá eventos separados por menos de **90 ms** (prioridad: obturador > pop > tick).
   - Mezcla final en **−14 LUFS** (true peak ≤ −1,5 dBTP), efectos **18–24 dB** por debajo de los picos de voz.

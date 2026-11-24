# Estilo: editorial

## Qué se ve

Subtítulos editoriales de **dos tipografías** sobre el tercio inferior suavemente oscurecido y desenfocado: primero se ancla la **palabra clave** de cada frase en serif cursiva grande (`EB Garamond` Italic) y el resto llena los huecos arriba, abajo o a los costados en sans limpia (`Inter` Regular para conectores chicos y Bold para palabras fuertes). Todo en **off-white (`#F6F5F0`)** con un **color acento opcional** tomado de la paleta del propio A-roll, entrando palabra por palabra con **pop + fade + blur**.

## Para qué sirve

Reels y shorts a cámara de marca personal cuidada, divulgación, educación, podcasts recortados a 9:16 y piezas por capítulos donde la jerarquía tipográfica y el aire limpio reemplazan a las cajas y efectos recargados.

## De dónde sale

Destilado de reglas medidas de composición en 9:16 por tercios (ojos en `y ≈ 640 px`, tercio inferior oscurecido y desenfocado, armado palabra-clave primero en serif cursiva + sans en huecos y entrada `pop + fade + blur`).

## Cómo elige y marca Claude las palabras clave del guion

No existe una regla mecánica que reemplace el criterio editorial: antes de renderizar, Claude lee la transcripción frase por frase y decide qué palabra merece el realce.

1. **Una sola palabra clave por frase corta (3–5 palabras)** — excepcionalmente 2 consecutivas si forman una unidad indivisible (ej. `"24 minutos"` o `"sin plata"`).
2. **Qué priorizar:** cifras, giros de sentido, adjetivos con carga emocional, el verbo que cambia la historia o el sustantivo central (*"lento"*, *"honesto"*, *"24"*, *"contratado"*, *"reyes"*). Nunca artículos, preposiciones ni muletillas.
3. **Cuándo sumar color acento:** solo en los 2 o 3 picos más fuertes del clip (gancho, cifra clave, remate), no en todas las frases.
4. **Cómo pasar las marcas a `subtitulos.html`** (elegí cualquiera de las dos formas):
   - **En `base-palabras.json`:** agregá `"realce": true` en las palabras elegidas (y opcionalmente `"acento": true` para teñirla con el color acento, o `"bloque": N` para forzar qué palabras comparten pantalla):
     ```json
     {"i": 11, "w": "24", "s": 2.714, "e": 3.074, "realce": true, "acento": true}
     ```
   - **Por variables globales antes de montar:** `window.REALCES = [3, 7, 11, 16]` y opcionalmente `window.ACENTOS = [11]`.
   - Si no se pasa ninguna marca, `subtitulos.html` usa un respaldo determinista (números primero, si no la palabra de contenido más larga) para funcionar de entrada, pero el mejor resultado sale siempre de marcar el guion a mano.

## Reglas con números

- **Canvas de referencia:** 1080×1920 (9:16).
- **Encuadre del hablante (`preparar-video`):** ojos en el tercio superior (**y ≈ 640 px**, rango 540–680 px), mentón **≤ 1010 px**, dejando limpio el pecho y el tercio inferior.
- **Tipografías (100% OFL / incluidas en HyperFrames):**
  - Sans principal: **`Inter`** (`400` conectores, `700` palabras fuertes). Alternativas OFL en `montaje/fonts/`: `Plus Jakarta Sans`, `Urbanist`, `Manrope`.
  - Realce: **`EB Garamond` Italic** (`400` italic; equivalente abierto a Apple Garamond Italic). Alternativas OFL: `Instrument Serif Italic`, `Cormorant Garamond Italic`, `Playfair Display Italic`.
- **Jerarquía de tamaños (1080×1920):**
  - Conector / relleno (`Inter` Regular): **52 px** (altura de tinta ~38–42 px; mínimo 48 px).
  - Palabra fuerte (`Inter` Bold): **82 px** (altura de tinta ~62–80 px, tracking **−0,04 em**).
  - Palabra clave de realce (`EB Garamond` Italic): **114 px** (altura de tinta ~88–112 px, ~**1,2×–1,4×** la sans bold y **2,2×** el conector; tracking **−0,01 em**).
  - Escalado automático si alguna fila supera **800 px** (siempre dentro de **840 px** máximos).
- **Colores y paleta del A-roll:**
  - Texto base: **off-white `#F6F5F0`** (o `blanco_tenido` de `informe.json` → `paletas[paletaIdx]`, sombra discreta `0 2px 14px rgba(0, 0, 0, 0.45)`).
  - Acento opcional: tomado de `informe.json` → `paletas[paletaIdx].acento_claro` (por defecto `paletaIdx = 0`, elegible con `window.EDITORIAL_CONFIG = { paletaIdx: 1 }`) o directo en `window.PALETA_EDITORIAL = { acento: "#...", texto: "#F6F5F0" }`. Si el acento es demasiado oscuro para leer sobre el fondo, `subtitulos.html` usa el respaldo claro `#E8D8A8`.
- **Posición (zona segura):**
  - Eje centrado en **x = 510 px** (rango **x = 90–930**, ancho máximo **840 px**).
  - Modo normal (cuerpo sin tarjeta abajo): bloque apoyado sobre el inicio del tercio inferior, borde inferior en **y ≤ 1340 px** (banda activa `y = 1090–1330 px`).
  - Modo hook con tarjeta debajo (activar con `window.EDITORIAL_CONFIG = { modoHookTarjeta: true }`): sube el bloque a **`y = 1040–1220 px`** para dejar **`y = 1240–1490 px`** libres a la tarjeta compacta.
- **Agrupación:** **3 a 5 palabras** por bloque (máx. 26 caracteres), corte en puntuación (`. ! ? , ; :`), pausas **≥ 260 ms** o campo `"bloque"` explícito.
- **Animación `Pop + fade + blur`:**
  - Cada palabra entra en su tiempo exacto (`w.s`) desde `y: +12 px`, `scale: 0.94`, `opacity: 0`, `filter: blur(8px)` hasta `y: 0`, `scale: 1`, `opacity: 1`, `filter: blur(0px)` en `clamp(180 ms, 260 ms, 80% de duración)`, curva `power3.out`.
  - Cierre duro (`opacity: 0`) en el inicio del siguiente bloque o **450 ms** tras la última palabra.

## Capa de oscurecido + desenfoque del tercio inferior

`subtitulos.html` incluye integrada (y activada por defecto) la capa de tratamiento del último tercio sobre el A-roll:
- **Blur progresivo:** `backdrop-filter: blur(14px)` enmascarado de `0%` en `y = 60%` (`1152 px`) a `75%` en `y = 72%` (`1382 px`) y `100%` en `y = 86%` (`1651 px`).
- **Degradado negro neutro:** `linear-gradient(to bottom, rgba(0,0,0,0) 62%, rgba(0,0,0,0.35) 75%, rgba(0,0,0,0.65) 100%)`.
- **Desactivarla en escenas full-screen:** pasá `window.EDITORIAL_CONFIG = { fondoInferior: false }` (o desactivala en los tramos donde corre una animación a pantalla completa).

## Qué va encima y cómo (`montar-video`)

- **Cadencia editorial:** A-roll para presentar y descansar; B-roll real para historias y emoción; pantalla completa para conceptos, listas o mecanismos; *callback* visual al cierre.
- **Tarjetas compactas en hook:** vidrio translúcido oscuro/claro (`backdrop-filter: blur(16px)`, borde `1px solid rgba(255,255,255,0.14)`, radio `20 px`) apoyadas en **`y = 1240–1490 px`** centradas en **`x = 510 px`**, subiendo el texto a `y = 1040–1220 px`.
- **Listicles / capítulos:** rombo o badge sobrio con el color acento de la paleta y número en `tabular-nums`, sin sobrecargar de elementos a la vez.
- **Checkpoint recomendado:** antes de armar las escenas completas, sacar una **hoja de subtítulos** (6–12 cuadros) para validar palabras clave, tipografías y acento.

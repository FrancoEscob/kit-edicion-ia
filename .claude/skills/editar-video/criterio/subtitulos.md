# Subtítulos, zona segura y encuadre

Reglas medidas para subtítulos en HyperFrames (`montar-video`) y reencuadre vertical (`preparar-video`). Para la regla de tercios, el degradado+blur del tercio inferior y cómo conviven texto y tarjetas, ver también `criterio/composicion.md`.

## 1. Zona segura en 9:16 (1080×1920)

Instagram Reels y TikTok dibujan botones y textos encima del video. Todo texto tiene que quedar afuera de esas franjas:

| Zona | Regla medida |
|---|---|
| Franja superior (**0–270 px**) | Usuario y audio de la plataforma. El borde superior del título de gancho arranca en **y = 290 px** |
| Columna derecha (**x > 940 px**, mitad inferior) | Botones de like, comentarios y compartir. Centrá subtítulos y gráficos en **x = 510** (no en 540) y mantenelos dentro de **x = 90–930** (ancho máximo **840 px**) |
| Franja inferior (**últimos ~400 px**) | Usuario y descripción del post. Línea base principal de subtítulos en **y = 1240–1280**; tope preferente **y ≤ 1340** (hasta **1530** solo si hubo que bajarlos por una cara baja) |
| Gráficos encima | Si van arriba del texto (en corte o tarjeta full): **y ≤ 1040**. Si van compactos debajo del texto en un hook con ojos en `y ≈ 640`: texto en **y = 1040–1220** y tarjeta en **y = 1240–1490** |

En **16:9 (1920×1080)**: los controles tapan los últimos ~120 px; poné los subtítulos en **y ≈ 890** y los títulos desde **y ≥ 78**. Si un 16:9 se va a publicar recortado a 1,2×, dejá al menos **200 px** de margen lateral para subtítulos al costado.

## 2. La cara nunca se tapa

- **Encuadre objetivo:** ojos cerca del tercio superior (**y ≈ 640 px**), cabeza dentro de `y ≈ 360–960 px`.
- **Umbral del mentón:** si el mentón (percentil 85 de los cuadros) cae debajo de **y = 1010** en 1080×1920, hacé zoom-in desde abajo (tope **1,29×** en fuentes 4K, **1,15×** en HD) levantando el mentón sobre los subtítulos sin que la cabeza suba de **y = 460**.
- **Plano muy cerrado:** si no hay margen para hacer zoom, apoyá los subtítulos sobre el pecho, justo debajo del mentón. Nunca tapen ojos ni boca, y jamás los achiques hasta volverlos ilegibles.
- **Título de gancho:** si el título en `y = 290` baja por debajo de las cejas en más del **10%** de los cuadros, movelo debajo del mentón (si entra sobre los subtítulos) o achicalo (nunca debajo de **44 px**).
- **Seguimiento suave:** muestrear caras cada **0,4 s**, seguir por continuidad (no por tamaño más grande; un salto mayor al **25%** del ancho es otra persona → mantener encuadre). Zona muerta del **6–7%** del ancho antes de mover, transición suave de **0,7 s**. Los tramos de una misma toma mantienen el mismo tamaño de plano (tolerancia **12%**) y los ojos a una altura estable.

## 3. Armado jerárquico (palabra clave primero + huecos)

En estilos editoriales de dos tipografías (como `estilos/editorial/`), los subtítulos no se arman todos iguales en una sola línea plana:

1. **Tomá una frase corta** del guion (**3 a 5 palabras** en ritmo editorial; hasta 6–8 en frases corridas).
2. **Elegí primero la palabra de mayor carga** emocional, temática o numérica (ej.: *"viral"*, *"24"*, *"lento"*, *"contratado"*) y ubicala en la **tipografía de realce** (serif cursiva, bold display o script legible) como ancla del bloque.
3. **Llená los huecos (*gaps*) alrededor** —arriba, abajo o a los costados— con el resto de la frase en la **sans principal**, diferenciando sustantivos/verbos fuertes (Bold) de conectores cortos (Regular más chico).

**Tamaños relativos medidos (1080×1920):**

| Rol dentro del bloque | Altura de tinta medida | `font-size` orientativo en CSS | Proporción |
|---|---|---|---|
| Conector / relleno (sans Regular) | **37–46 px** | **50–64 px** (nunca < 48 px) | `1×` (base) |
| Palabra fuerte (sans Bold) | **77–93 px** | **82–108 px** | **~2×** el conector |
| Palabra clave de realce (serif cursiva / script) | **87–121 px** (hasta **138 px** suelta en hook) | **104–138 px** | **1,1×–1,3×** la sans bold (**2,2×–2,6×** el conector) |

En **pila editorial de una sola tipografía** (`cine-sobrio`, `clip-con-pruebas`): soporte **66 px**, énfasis **136 px**, línea simple **100 px**, título gancho **64 px**, tracking **−0,04 a −0,05 em** (positivo `+0,02` a `+0,06 em` en MAYÚSCULAS). En cualquier estilo, ninguna línea principal baja de **56 px** (48–50 px solo para conectores cortos dentro de un bloque jerárquico, o 44 px en narración sobre lienzo diseñado).

## 4. Agrupación, tiempos y movimiento

- **Agrupación:**
  - Clips con ritmo o pila de 1 fuente: máximo **2–3 palabras** o **16 caracteres**.
  - Editorial jerárquico o conversacional: **3–5 palabras** en frases naturales (máx. ~26–28 caracteres).
  - Cortar siempre en puntuación, en pausas **≥ 260 ms** y en **cada corte de plano**. Nunca partir nombres propios ni términos compuestos ("Buenos Aires", "inteligencia artificial", marcas).
- **Sincronía y permanencia:**
  - Cada palabra o grupo entra en el ataque audible (sincronizado dentro de **±150 ms**; ajuste de ataque −180 a +120 ms).
  - Permanece al menos **260 ms** (descartar o fusionar tramos < 120 ms), aguanta hasta el siguiente grupo y se apaga como máximo **450 ms** después de su última palabra.
  - **Cierre duro obligatorio en HyperFrames:** cada grupo termina con `tl.set(el, { opacity: 0 }, fin)` para que nunca queden dos grupos visibles a la vez.
- **Patrones de movimiento medidos:**
  - **Sobrio / editorial contenido:** tras una pausa ≥ **140 ms**, fade `0 → 1` + subida corta (**5 px** soporte / **12 px** énfasis) en `min(220 ms, 60% de duración)`, `power3.out`; reemplazo seco en palabras rápidas.
  - **Pop + fade + blur** (estilo `editorial` y reels de dos tipografías): cada palabra entra desde unos píxeles abajo (**10–14 px**), escala leve (**0,94 → 1,0**), opacidad **0 → 1** y desenfoque inicial (**`blur(8px)` → `0px`**) durante **180–260 ms** (`power3.out`, arranque rápido y frenado suave; ~0,8–1,0 s para el despliegue completo de la frase). El blur solo vive en la entrada, nunca en el reposo.

## 5. Pares de tipografías OFL / Google Fonts

Evitá tipografías comerciales con licencia paga usando equivalentes abiertos (OFL / Google Fonts). Las marcadas con **`*`** ya vienen precargadas en HyperFrames sin necesitar `@font-face` manual; el resto se carga como archivo `.woff2`/`.ttf` local en `montaje/fonts/`.

| Familia / Rol | Tipografía OFL / Google Fonts | Equivale a (comercial) | Uso recomendado |
|---|---|---|---|
| **Sans base** | **`Inter`** `*` | Helvetica Neue / Neue Haas Grotesk | Base universal neutra (400 / 700 / 800) |
| **Sans base** | **`Plus Jakarta Sans`** | Creato Display (geométrica cálida) | Reels editoriales modernos con realce serif |
| **Sans base** | **`Urbanist`** | PP Neue Montreal (pesos livianos) | Estética limpia y fina (300–400 + 600–700) |
| **Sans base** | **`Manrope`** | PP Neue Montreal / neo-grotesca editorial | Editorial técnico, podcasts, negocios |
| **Sans base** | **`Montserrat`** `*` / **`Outfit`** `*` | Gotham / Proxima Nova | Base limpia (`limpio`) o karaoke (`karaoke`) |
| **Realce serif cursiva** | **`EB Garamond` Italic** `*` | **Apple Garamond Italic** | Realce editorial clásico condensado (0 configuración extra en HyperFrames) |
| **Realce serif cursiva** | **`Cormorant Garamond` Italic** | Apple Garamond (más estilizada y fina) | Estética de lujo / alto contraste en tamaños grandes (≥ 100 px) |
| **Realce serif cursiva** | **`Instrument Serif` Italic** | Serif condensada editorial moderna | Palabra clave alta y estrecha junto a sans geométrica |
| **Realce serif cursiva** | **`Playfair Display` Italic** `*` | Didot / Bodoni editorial | Citas, divulgación, contraste clásico sobre `Inter` |
| **Realce script legible** | **`Caveat`** (o **`Dancing Script`**) | Swash script / firma editorial | Acento puntual (máximo **1 palabra** por frase, 1,25–1,4× más grande que la sans para igualar altura visual) |

## 6. Contraste, una sola pista de texto y español

- **Contraste sobre video:** texto blanco (`#FFFFFF` o off-white `#F6F5F0`) con sombra suave (**negro al 42%**, blur **10 px**, **2 px** abajo; subir a **90% / 22 px** sobre b-roll claro) o apoyado sobre el degradado+blur del tercio inferior (`criterio/composicion.md`). Nunca halos negros pesados ni texto negro sobre video (negro solo sobre fondo claro sólido). Si hay caja detrás del texto, **una sola caja sólida** (~0,6 em de margen), nunca cajas apiladas.
- **Una sola pista de texto:** jamás titular permanente y subtítulos compitiendo. El título de gancho se va a los **~3 s** (o se oculta al entrar una tarjeta). Si una escena gráfica ya muestra las palabras habladas, apagá los subtítulos en ese tramo.
- **Corrección del español:** revisá tildes, signos de apertura (`¿`, `¡`), mayúsculas en nombres propios y siglas, números limpios ("$50.000", "40%"). Corregí errores de transcripción antes de renderizar.

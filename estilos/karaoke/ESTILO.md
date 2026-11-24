# Estilo: karaoke

## Qué se ve

Frases cortas de 3 a 4 palabras visibles desde que arranca el bloque en blanco suave, mientras la palabra que se está diciendo en ese instante se ilumina en celeste eléctrico con un leve empuje de escala. Una vez pronunciada, queda en blanco pleno.

## Para qué sirve

Tutoriales rápidos, consejos prácticos, explicaciones conversacionales y reels con buen ritmo donde marcar la palabra exacta ayuda a seguir el hilo incluso sin sonido al principio.

## De dónde sale

Estilo propio del kit pensado para máxima legibilidad palabra por palabra en pantalla de celular.

## Reglas con números

- **Canvas de referencia:** 1080×1920 (9:16).
- **Tipografía:** `Outfit`, peso `800` (ExtraBold).
- **Colores:**
  - Palabra por decir: `rgba(255, 255, 255, 0.62)`.
  - Palabra activa: **`#38BDF8`** (celeste brillante) con resplandor sutil `0 0 18px rgba(56, 189, 248, 0.35)`.
  - Palabra ya dicha: `#FFFFFF`.
- **Sombra:** `0 3px 12px rgba(0, 0, 0, 0.58)`. Sin caja pesada.
- **Tamaños:** **72 px** base (mínimo **56 px** si se ajusta a ancho máximo **840 px**). Tracking **−0,025 em**, interlineado **1,16**.
- **Posición (zona segura):** eje **x = 510** (rango **x = 90–930**, ancho máximo **840 px**), centrado alrededor de **y = 1220**, borde inferior nunca debajo de **y = 1340**.
- **Agrupación:** **3 a 4 palabras** (máximo **22 caracteres**); corte en puntuación y en pausas **≥ 260 ms**.
- **Tiempos y movimiento:**
  - El grupo entero entra en el inicio de su primera palabra con fade `0 → 1` y subida de **6 px** en **140 ms** (`power2.out`).
  - Al empezar cada palabra (`w.s`), cambia a `#38BDF8` y escala a **1,08** en **90 ms** (`power2.out`); al terminar (`w.e`), vuelve a `#FFFFFF` y escala **1,0** en **90 ms**.
  - Cierre duro (`opacity: 0`) justo antes del grupo siguiente o **450 ms** después de la última palabra.

## Qué va encima y cómo (`montar-video`)

- **Acento coherente:** cualquier número destacado, flecha o barra de apoyo que agregues encima usa el mismo celeste `#38BDF8` sobre blanco y negro/gris oscuro.
- **Posición de gráficos:** eje **x = 510**, borde inferior en **y ≤ 1040** para no chocar con la línea karaoke.
- **Personalización rápida:** el color de la palabra activa vive en la constante `COLOR_ACTIVO` dentro de `subtitulos.html` por si la marca usa otro acento (verificar siempre contraste ≥ 3:1 sobre el video).

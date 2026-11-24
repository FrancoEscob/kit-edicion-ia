# Estilo: impacto

## Qué se ve

Subtítulos grandes en **MAYÚSCULAS** con tipografía pesada de alto impacto, 1 a 3 palabras por golpe. El texto base va en blanco puro con sombra firme, y la palabra más fuerte de cada grupo (cifras, porcentajes o la palabra principal) salta en **amarillo intenso** y un poco más grande.

## Para qué sirve

Ganchos de alta retención, opiniones directas, listas veloces, shorts y reels enérgicos donde el subtítulo marca el golpe rítmico.

## De dónde sale

Estilo propio del kit para clips de alta energía en redes verticales.

## Reglas con números

- **Canvas de referencia:** 1080×1920 (9:16).
- **Tipografía:** `Archivo Black`, peso `400` (peso único ultra pesado), **siempre en MAYÚSCULAS**.
- **Colores:**
  - Base: `#FFFFFF`.
  - Palabra destacada: **`#FFD400`** (amarillo intenso).
- **Sombra y contraste:** doble sombra firme `0 4px 0 rgba(0, 0, 0, 0.85), 0 8px 22px rgba(0, 0, 0, 0.65)` para sostener lectura sobre cualquier fondo sin halos borrosos.
- **Tamaños:** base **84 px**, palabra destacada **96 px** (se escala automáticamente si supera **840 px**; mínimo **58 px**). Tracking **+0,02 em** (mayúsculas necesitan aire), interlineado **1,05**.
- **Posición (zona segura):** eje **x = 510** (rango **x = 90–930**, ancho máximo **840 px**), centro vertical alrededor de **y = 1200**, nunca debajo de **y = 1340**.
- **Agrupación:** máximo **3 palabras** o **15 caracteres**; corte en puntuación y en pausas **≥ 240 ms**.
- **Selección de énfasis:** en cada grupo se destaca una sola palabra — prioridad: números/dinero/porcentajes, si no la palabra con significado más larga (descartando artículos y preposiciones).
- **Tiempos y movimiento:**
  - Cada palabra entra en su tiempo exacto (`w.s`) con golpe corto: las normales suben **10 px** y escalan `0,90 → 1,0` en **130 ms** (`power3.out`); la destacada entra desde escala `0,84 → 1,0` en **160 ms** (`back.out(1.4)`).
  - Reemplazo seco entre grupos, cierre duro (`opacity: 0`) en el inicio del siguiente o **400 ms** tras la última palabra.

## Qué va encima y cómo (`montar-video`)

- **Gráficos:** grandes, directos y de alto contraste (números gigantes en `#FFD400`, capturas con borde limpio), siempre sobre **y ≤ 1040** y centrados en **x = 510**.
- **Título de gancho:** si se usa, en `Archivo Black` **58 px**, va en el tercio inferior en lugar de los subtítulos (ver `criterio/subtitulos.md`) y se va antes de los **3 s**.
- **Freno a excesos:** solo **una** palabra amarilla por grupo; nunca pintes la frase entera de amarillo.

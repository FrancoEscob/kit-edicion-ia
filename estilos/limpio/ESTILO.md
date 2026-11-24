# Estilo: limpio

## Qué se ve

Subtítulos blancos sobrios y despejados, de 2 o 3 palabras por golpe, en una sans geométrica limpia con sombra suave. Sin cajas, sin colores llamativos y sin rebotes: acompañan la voz sin robarle foco a quien habla.

## Para qué sirve

Videos a cámara de marca personal sobria, explicaciones, entrevistas, testimonios y clips educativos donde la cara y la claridad de lectura mandan.

## De dónde sale

Estilo propio del kit, diseñado como base universal para cualquier video hablado en vertical 9:16 (adaptable a 16:9).

## Reglas con números

- **Canvas de referencia:** 1080×1920 (9:16).
- **Tipografía:** `Montserrat`, peso `700` (Bold).
- **Color:** blanco puro `#FFFFFF`.
- **Sombra:** `0 2px 10px rgba(0, 0, 0, 0.45)`. Sin borde ni caja.
- **Tamaños:** **68 px** por defecto; si la línea supera **840 px** de ancho se reduce automáticamente (mínimo **56 px**). Tracking **−0,03 em**, interlineado **1,12**.
- **Posición (zona segura):** centrado en **x = 510** (rango **x = 90–930**, ancho máximo **840 px**), línea base en **y = 1240**, borde inferior nunca debajo de **y = 1340**.
- **Agrupación:** máximo **3 palabras** o **18 caracteres**; corte automático en puntuación (`.`, `!`, `?`, `,`) y en pausas **≥ 260 ms**.
- **Tiempos y movimiento:**
  - Cada palabra aparece en su inicio exacto (`s`) con fade `0 → 1` y subida corta de **5 px** durante `min(180 ms, 60% de duración)`, curva `power3.out`.
  - El grupo aguanta hasta el inicio del siguiente (tope **450 ms** tras la última palabra) y se apaga en seco (`opacity: 0`) para no superponerse nunca.
  - Duración mínima de grupo: **260 ms** (se fusionan palabras sueltas muy cortas si no hay pausa larga).

## Qué va encima y cómo (`montar-video`)

- **Título de gancho (opcional):** misma fuente `Montserrat` 700, **60 px**, va en el tercio inferior en lugar de los subtítulos (ver `criterio/subtitulos.md`), se retira a los **3 s** o al entrar una tarjeta.
- **Gráficos:** sobrios, sin ruido visual, alineados en **x = 510** y arriba de **y = 1040**.
- **Una sola pista de texto:** si entra una placa que repite el mensaje hablado, apagá los subtítulos durante ese tramo.

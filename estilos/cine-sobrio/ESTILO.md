# Estilo: cine-sobrio

## Qué se ve

Pila tipográfica editorial y sobria sobre la persona a cámara: una línea de soporte chica y una palabra de énfasis gigante en blanco puro, sans grotesca bold con tracking bien cerrado, sombra mínima y un alejamiento lento y continuo (*pullback*) compartido por todas las palabras del plano.

## Para qué sirve

Clips hablados con estética cuidada, reflexiones, historias personales y piezas de marca donde se busca presencia cinematográfica sin efectos estridentes ni cajas de colores.

## De dónde sale

Destilado del criterio medido para subtítulos cinematográficos contenidos sobre plano hablado (pila jerárquica blanca, llegadas de pocos píxeles y retroceso continuo por toma).

## Reglas con números

- **Canvas de referencia:** 1080×1920 (9:16). (En 16:9 de 1920×1080, la pila de referencia escala a 68 / 120 / 218 px o 60 / 108 / 210 px; palabras rápidas sueltas 118–144 px.)
- **Tipografía:** `Inter`, peso `700`/`800` (en HyperFrames; sustituto abierto equivalente a Helvetica Neue Bold — si el proyecto tiene licencia local de Helvetica Neue Bold puede declararse con `@font-face`).
- **Color y sombra:** blanco `#FFFFFF`; sombra baja y suave `0 2px 10px rgba(0, 0, 0, 0.42)` (subir a `0 4px 22px rgba(0, 0, 0, 0.90)` únicamente sobre b-roll muy brillante). Nunca cajas ni halos pesados.
- **Tracking:** **−0,05 em** en general; **−0,045 em** en palabra escénica; **−0,04 em** en cierre.
- **Jerarquía de pila (9:16):**
  - Línea de soporte (antes y/o después del énfasis): **66 px** (peso 700).
  - Palabra de énfasis (cifras/dinero primero, luego la palabra de contenido más larga): **136 px** (peso 800).
  - Grupo de solo palabras funcionales/cortas: una sola línea a **100 px**.
  - Cualquier fila que exceda **840 px** se escala proporcionalmente para encajar (nunca debajo de **56 px**).
- **Posición (zona segura):** centrado en **x = 510** (rango **x = 90–930**, ancho máximo **840 px**); línea base de énfasis en **y = 1240**, borde inferior siempre **≤ 1340**; cara despejada (mentón **≤ 1010**).
- **Agrupación:** máximo **3 palabras** o **16 caracteres**; cortar en puntuación, pausas **≥ 260 ms** y en cada corte de plano. Nunca separar nombres compuestos.
- **Tiempos y movimiento medidos:**
  - **Primera llegada** tras una pausa **≥ 140 ms**: fade `0 → 1` y subida exacta de **5 px** (soporte) o **12 px** (líneas ≥ 100 px), en `min(220 ms, 60% de la duración)`, curva ease-out cúbica (`power3.out`). Sin rebote, sin overshoot, sin animación de salida.
  - **Reemplazos rápidos** (pausa < 140 ms): corte seco en el mismo eje y línea base, visibles de inmediato.
  - **Retroceso continuo (*pullback*):** todas las palabras de una misma toma heredan una sola curva de escala decreciente (~7%, `1,07 → 1,0`, exponente desacelerado `0,65`) que **no se reinicia** cuando aparece una palabra nueva.
  - Permanencia mínima **260 ms**, cola máxima **450 ms** tras la última palabra, cierre duro en el siguiente grupo.

## Qué va encima y cómo (`montar-video`)

- **Palabra escénica opcional:** sobre un plano abierto sin cara en el centro puede colocarse una palabra suelta traslúcida al **60–62% de opacidad** (hasta ~260–300 px en 16:9, ~200 px en 9:16), fija hasta el corte del plano, sin adelantar la frase siguiente.
- **No duplicar zooms:** si el plano de video ya tiene retroceso de cámara propio, no le agregues un segundo zoom encima.
- **Tipografía única:** jamás mezcles dos fuentes distintas en el mismo clip.
- **Título de gancho (si se usa):** misma fuente, **64 px**, tracking **−0,04 em**, máximo 2 líneas de 30 caracteres, tope en **y = 290**, oculto al entrar tarjetas y retirado a los ~3 s.

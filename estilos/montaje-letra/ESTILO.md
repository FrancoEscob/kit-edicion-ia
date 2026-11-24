# Estilo: montaje-letra

## Qué se ve

Montaje rítmico guiado por música sobre planos cinematográficos variados (trabajo, ciudad, noche, momentos reflexivos), con pilas tipográficas blancas de alto contraste jerárquico, palabras escénicas traslúcidas, retroceso continuo compartido por plano y color fílmico contenido.

## Para qué sirve

Reels de montaje con letra o discurso sobre música, piezas de energía/manifiesto, resúmenes visuales de 10 a 30 s donde los cortes siguen el pulso musical y el texto construye tensión.

## De dónde sale

Destilado del criterio medido para montajes musicales de letra en pila sobre material filmado con tratamiento fílmico sobrio.

## Reglas de subtítulos con números

- **Canvas de referencia:** 1080×1920 (9:16) o 1920×1080 (16:9).
- **Tipografía:** `Inter`, peso `700`/`800` (sustituto abierto de Helvetica Neue Bold en HyperFrames).
- **Color y sombra:** blanco `#FFFFFF`; sombra sutil `0 2px 12px rgba(0, 0, 0, 0.48)` solo para despegar del fondo; **nunca barras negras** detrás del texto.
- **Tracking:** **−0,05 em** general, **−0,045 em** en énfasis escénico, **−0,04 em** en cierre.
- **Jerarquía de pila:**
  - En 9:16 (1080×1920): soporte **62 px**, medio **104 px**, énfasis fuerte **168 px** (ajustado a ancho máximo **840 px**).
  - En 16:9 (1920×1080): soporte **60–68 px**, medio **108–120 px**, énfasis **210–218 px**; palabras rápidas aisladas **118–144 px**.
  - Palabra escénica suelta (pausa larga o remate visual): **190–240 px** en 9:16 (**300 px** en 16:9) al **60% de opacidad**, sostenida exactamente hasta el corte del plano (sin congelar el video).
- **Posición:** pilas equilibradas en el espacio negativo sin tapar caras ni luces brillantes; en 9:16 centradas en **x = 510**, zona segura **x = 90–930**, línea base alrededor de **y = 1180–1240**, siempre **≤ 1340**.
- **Movimiento medido:**
  - Primeras llegadas tras pausa ≥ **140 ms**: fade `0 → 1` + subida exacta de **5 px** (soporte) o **12 px** (énfasis ≥ 100 px) en `min(220 ms, 60% de duración)`, ease-out cúbico (`power3.out`). Sin rebote, sin overshoot ni deslizamientos largos.
  - Palabras rápidas: reemplazo seco en el mismo centro y línea base.
  - **Retroceso continuo por plano (*pullback*):** todas las palabras de un mismo plano comparten una sola curva desacelerada (~7%, exponente **0,65** en pilas, **0,55** en texto escénico) sin reiniciarse al aparecer cada palabra.

## Reglas de montaje, color y cierre (`montar-video`)

- **Tiempos y cortes musicales:** medí la pista antes de editar (forma de onda, pulsos y final **decodificado** del audio). Cortá los planos sobre los acentos reales de la canción elegida; no recicles una grilla de tiempos de otro tema ni alteres la velocidad de la música sin pedido.
- **Selección de tomas:** usá planos reales con propósito (trabajo, viaje, equipo, noche, pausa), **sin repetir una toma idéntica** con otro filtro. Escalado uniforme y recorte deliberado (*cover*), nunca estirar un plano horizontal.
- **Color cinematográfico:**
  1. Balanceá exposición de cada toma primero (levantar caras subexpuestas, controlar altas luces, anclar negros).
  2. Si hay material log real, normalizá con su transformada técnica antes del look; nunca apliques conversión log a material Rec.709.
  3. Aplicá un look fílmico contenido (~**35%** de mezcla de LUT fílmico o contraste suave con negros anclados y piel natural, saturación ~0,98). Sin pulsos RGB artificiales.
- **Cierre y audio:**
  - Si hay marca/logo final (siempre archivo real de la marca, nunca redibujado), entra en blanco sobre el último plano ~0,6–1 s antes del cierre, corta junto con la imagen a negro en el golpe final y termina exactamente en el final decodificado de la música (**sin cola muda extra**).
  - Master objetivo: **−15 a −14 LUFS**, true peak **≤ −1 dBTP**.

# Estilo: historia-en-broll

## Qué se ve

Relato narrado en off 100% sobre b-roll (fotos reales, documentos, filmaciones de archivo, planos detalle; nadie hablando a cámara). **Sin título de gancho arriba.** Pilas tipográficas blancas centradas en el medio exacto del cuadro que resuelven desde un desenfoque suave, grilla fina tipo pantalla únicamente sobre imágenes viejas, oscurecimiento/desenfoque de fondos cargados y óptica con bordes suavizados y golpe de enfoque en cada corte.

## Para qué sirve

Historias narradas en primera persona, mini documentales verticales u horizontales, piezas biográficas o de archivo donde la voz en off lleva el relato entero sobre material visual variado.

## De dónde sale

Destilado del criterio medido para relatos narrados íntegramente en b-roll con subtítulos centrales, textura de malla en archivo y óptica cinematográfica.

## Reglas de subtítulos con números

- **Sin título de gancho:** nunca se dibuja encabezado arriba.
- **Tipografía:** `Inter`, peso `700`/`800` (sustituto abierto de Helvetica Neue Bold en HyperFrames).
- **Color, brillo y sombra:** blanco `#FFFFFF`, resplandor suave (`0 0 18px rgba(255, 255, 255, 0.24)`) + sombra ajustada (`0 3px 10px rgba(0, 0, 0, 0.52)`). Sin caja.
- **Tracking:** **−0,045 em** en filas chicas (S) y **−0,05 em** en filas grandes (M / L).
- **Tamaños (base lado corto 1080):**
  - **S (contexto / arranque):** **58 px**.
  - **M (énfasis medio):** **100 px**.
  - **L (remate / palabra golpe):** **164 px** (se ajusta automáticamente si excede el ancho máximo: **86%** del ancho en vertical — tope seguro **840 px** en 9:16 — y **1240 px** en 16:9).
- **Posición:** **centrado en el medio del cuadro** (horizontal y vertical; en 9:16 eje **x = 510**, centro vertical **y = 960**).
- **Composición de la pila:** fila chica arriba con el arranque de la frase y 1 o 2 palabras golpe grandes abajo (arrastrando el artículo o posesivo junto al sustantivo, ej.: *"el pasillo"*, *"mi visa"*, *"exacto opuesto."*).
- **Tiempos y movimiento medidos:**
  - Cada palabra aterriza al decirse (`w.s`): fade `0 → 1`, subida de **5 / 8 / 12 px** (S / M / L) y **desenfoque de entrada de 9 px → 0 px** en `min(220 ms, 60% de duración)`, curva ease-out cúbica (`power3.out`).
  - Cada pila completa hace un **pullback lento de escala `1,028 → 1,0`** a lo largo de su tiempo en pantalla.
  - La pila siguiente reemplaza en seco; sostiene pausas menores a **0,8 s** y permanece al menos **0,9 s** en pantalla. Puede sostenerse la última pila hasta el final si remata en un golpe musical.

## Reglas de imagen, textura y óptica (`montar-video`)

1. **Grilla fina SOLO en material viejo** (fotos propias, documentos, recortes, filmaciones de archivo; **nunca** en video moderno):
   - Grilla fija en pantalla de **12 px** (en 1080), líneas **22% más oscuras** (perfil suave ~1,5 px).
   - Grano sutil: **0,020** en fotos y **0,024** en filmación de archivo, refrescando a **10 fps**.
   - Viñeta suave: **0,22** en fotos y **0,26** en archivo.
   - **Sin cambio de color** salvo que la persona pida un look específico.
2. **Protección debajo de las palabras:**
   - Oscurecé planos brillantes entre **12% y 38%** (`brightness(0.62–0.88)` o capa negra traslúcida).
   - Desenfocá planos con texto legible propio (mails, documentos, carteles, pantallas) entre **3 y 4,5 px** para que los subtítulos nunca compitan con texto del fondo.
   - Reencuadrá fotos para que la pila central nunca tape una cara.
3. **Tratamiento de lente en todos los planos:**
   - Desenfoque periférico en bordes (máscara superelipse potencia 4, transición suave de 0,70 a 1,02, radio **11 px**, brillo ×1,04).
   - Leve aberración cromática en bordes (canal rojo ×1,006, azul ×0,994 desde el centro) y bloom suave en altas luces (**0,22**).
   - **Focus pull en cada corte:** cada plano nuevo arranca con **16 px de blur** y enfoca a **0 px** en **0,2 s** (`power3.out`).

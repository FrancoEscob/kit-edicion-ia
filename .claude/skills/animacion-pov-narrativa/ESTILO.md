# Animación narrativa en primera persona

Basado en una referencia pública de laurgrowth de 42,35 s, a 720×1280 y 30 fps. El análisis de la tira y las mediciones queda en `referencias/laurgrowth/ANALISIS.md` en el kit donde se relevó. Las cifras de montaje de esta ficha están en el lienzo de salida de 1080×1920.

| Decisión | Qué mostró la referencia | Cómo llevarlo al montaje |
|---|---|---|
| Encuadre | Perspectiva continua, profundidad de campo amplia, manos desde las dos esquinas. El subtítulo ocupa el 69–73% del alto. | Dibujá fondo, espacio transitable y objeto cercano alrededor del mismo punto de fuga. Poné el objetivo en el centro antes del gesto y mantené libre la franja de lectura. |
| Color | Exterior frío `#A0B0C6`, tinte agua `#5C8E80`, interior `#463223`, arena `#A88C74`. En el cierre reinan `#35393F`, azul `#3380C8` y rojo `#C9252F`. | Da a cada entorno una familia dominante. Trazos oscuros de 3–6 px a 1080; usá dos valores de luz como base en cada objeto. Reservá dos acentos de alto contraste para las opciones. |
| Subtítulos | Una línea con sans redondeada pesada, relleno amarillo o blanco y borde oscuro. Tinta aproximada de 32–42 px en el original, según color y signo. | Usá Nunito 900 para acercarte al dibujo de la referencia o Inter 800–900 si ya está disponible. Apuntá a 48–63 px de tinta a 1080. En general da con 65–80 px CSS. Para frase larga, partí por sentido o bajá a 56–62 px. Borde de 6–8 px con `paint-order: stroke fill`. |
| Cámara | Se inclina en 1.130 ms al abrir, con frenada; el regreso toma 1.140 ms. Hay roll de 14° en 730 ms y giros completos en 1.200 ms. | Animá fondo, medio y cerca con factores aproximados 0,48×, 1× y 1,6×. Usá `power2.out` si frena al mirar, `sine.inOut` para cambios que continúan y `none` para empuje sostenido. Empezá con roll de 3–8° y reservá los giros grandes para cambios de orientación. |
| Alcance | La mano derecha va desde el borde al objetivo en unos 430 ms. La mano que acompaña queda por debajo. | Usá `reach()`: 360–460 ms de llegada con `power2.out`, pausa de 140–600 ms según la acción, vuelta de 500 ms con `sine.inOut`. Ajustá la distancia mirando el cuadro de contacto. |
| Cambio | Paneos rápidos de 3–5 cuadros, tintes de entrada en 4 cuadros y una transición por oclusión de 5 cuadros. | A 30 fps, 3–5 cuadros son 100–167 ms. Simulá el paneo acelerando el entorno o cruzá un objeto cercano por delante; usá el barrido de color como sustituto cuando la escena pida un golpe corto. |
| Elección | Título en f1224, azul en f1225–1227, rojo en f1227–1230. Oscurecido sobre el plano que sigue vivo. Quedan unos 1.530 ms desde el primer título. | Sostené la pregunta y dos barras anchas de ~85% del cuadro. Entrá con opacidad y escala en cadena. Conservá visible el lugar de la decisión detrás de la placa. |
| Sonido | −14,1 LUFS, pico −1,3 dBTP, 33 acentos detectados y pulso musical sin confianza. | Usá −14 LUFS como punto de partida. Marcá golpes en objetos o gestos y mantené ambiente entre frases. Revisá el nivel y la cola en el máster. |

## Bloques de HyperFrames

- `primitivas/index.html`: composición de seis segundos para ver paralaje, alcance, barrido y placa. Abrila como proyecto o corré `npx hyperframes lint .claude/skills/animacion-pov-narrativa/primitivas`. La muestra usa GSAP 3.14.2 desde CDN. Para trabajar sin conexión, apuntá ese script a una copia local.
- `primitivas/pov.js`: copiá el archivo a `montaje/assets/` y cargalo después de GSAP. `camera` toma tres capas y poses con segundos absolutos; `reach` recibe la mano y su pose de contacto; `whip` toma el instante central, duración en cuadros y color; `endCard` toma una capa con dos filas `.choice`. Todos escriben en el timeline que les pasás. Dales tiempos distintos a los alcances de la misma mano.
- `subtitulos.html`: plantilla `captions`. Admite `window.BASE_PALABRAS` o `base-palabras.json` según el contrato de `estilos/README.md`. Para diálogo, podés agregar `color: "clara"` o `color: "lila"` por palabra y el grupo se separa cuando cambia el color. Cortá la capa antes de la elección si la pregunta ya aparece en la placa.

Las curvas GSAP son equivalencias de montaje. En la referencia, la cámara tiene aceleraciones irregulares y los fondos en movimiento hacen que `measure curve` lea varios elementos juntos.

# Gráficos y b-roll encima del video

Cuándo sumar un gráfico o un corte de b-roll en HyperFrames (`montar-video`), qué tipo de plano conviene en cada tramo del guion, qué material está permitido y cómo anclarlo al audio.

## 1. Cadencia editorial: qué plano corresponde a cada momento

En vez de tirar efectos al azar, asigná cada frase del guion a una de estas tres familias y cerrá con un guiño visual:

| Familia de plano | Para qué momentos del guion | Función en el ritmo |
|---|---|---|
| **A-roll** (persona a cámara) | Presentación, transiciones entre ideas, confesiones personales, remates y momentos de descanso visual | Conexión humana y respiro; evita que el video sature |
| **B-roll** (tomas filmadas, fotos reales, archivo) | Historias, emoción, personas, lugares y ejemplos concretos del mundo real | Ilustra lo que se cuenta con imágenes vividas |
| **Pantalla completa** (animación, placas de datos, diagramas, showcases) | Conceptos abstractos, cifras, comparaciones, listas/capítulos y mecanismos paso a paso | Explica ideas que la cámara sola no puede mostrar |
| **Callback visual al cierre** | Últimos segundos / conclusión | Retomá un motivo, tarjeta o plano visto en el gancho para cerrar el círculo narrativo |

## 2. Cuándo entra y cuánto dura

Un gráfico muestra literalmente lo que la persona está diciendo en ese instante. No es decoración ni un aviso pegado al final.

- **Anclaje a palabras:** elegí la frase exacta en `base-palabras.json` y hacé entrar el gráfico **60 ms antes** del inicio de su primera palabra.
- **Ritmo:** en un clip con gráficos, meté un estímulo visual nuevo cada **3–5 s** a lo largo del cuerpo (en ritmos muy picados, cada **1,5–4 s**). Un solo gráfico en un clip de 30 s se siente vacío.
- **Respetá el arranque y el cierre:** dejá el primer segundo y la última línea en la cara de la persona, salvo que el gráfico sea el remate final o que el propio gancho nombre una imagen concreta (en ese caso entra dentro de los primeros **1–2 s**, o como tarjeta compacta debajo del texto del hook).
- **Tiempo de lectura:**
  - Foto o plano de apoyo: sostener **1,8–2,6 s**.
  - Cualquier pieza con texto legible (mail, titular, documento, captura): sostener **≥ 2,6 s**. Nunca flashees texto por unos pocos cuadros.
- **Proporción de pantalla completa:** en clips a cámara estándar mantené las escenas a pantalla completa por debajo del **~30%** del total; en reels editoriales muy producidos por capítulos pueden subir hasta **40–50%** si el estilo lo pide explícitamente, siempre alternando descansos en A-roll.

## 3. Qué material se puede usar (en orden de prioridad)

1. **La prueba real:** captura real del artículo, mail, tablero o publicación (sin banners de cookies); foto real; grabación real del producto; documento real.
2. **Otro material de la misma persona** tomado de otras partes de la grabación.
3. **Archivo de dominio público** (filmaciones históricas, fotos libres, Wikimedia, Pexels/Unsplash) en la mejor resolución disponible.
4. **Diagrama, tarjeta UI o contador animado** en HyperFrames que represente la idea con movimiento real (número que sube, barra que crece, pasos numerados).

**Prohibido:**
- Personas generadas por IA o caras reales alteradas.
- Interfaces inventadas simulando un producto real: capturá el producto real (las tarjetas estilizadas solo sirven para resumir un dato propio o un capítulo, no para falsificar una app).
- Esqueletos de carga, líneas grises simulando texto o círculos de colores haciendo de personas.
- Palabras metidas en pastillas/cajitas estáticas vendidas como "gráfico".
- Un cuadro congelado donde se sugiere movimiento.
- Cualquier cifra o afirmación no verificada contra su fuente.

## 4. Cómo componerlos en HyperFrames

Ver `criterio/composicion.md` para la convivencia exacta con la regla de tercios y la zona segura:

- **Eje y despeje:** alineá siempre los gráficos en el eje de los subtítulos (**x = 510** en 1080×1920, rango **x = 90–930**). **Jamás tapes la cabeza ni la cara** (ojos en `y ≈ 640`, cabeza hasta `y ≈ 960`).
  - **Tarjeta compacta en hook sobre A-roll:** texto arriba en **`y = 1040–1220`**, tarjeta compacta debajo en **`y = 1240–1490`** (sin caer en los últimos 400 px de la app).
  - **Activo grande o con texto chico** (mail, titular, documento): hacé corte a pantalla completa o ubicalo grande y nítido en **`y = 300–1040`** tapando el A-roll (sobre copia oscura desenfocada o tarjeta texturada) y ocultando el título de gancho, con subtítulos debajo en `y = 1100–1340`.
- **Fotos verticales:** llenan la pantalla completa (*cover crop* sobre el sujeto, nunca estiradas), con la banda de subtítulos oscurecida suavemente y grano liviano.
- **Nunca una fotito chica sobre placa plana:** los activos apaisados van grandes y nítidos sobre fondo oscuro desenfocado o tarjeta texturada (grilla fina, grano, viñeta).
- **Contadores numéricos:** suben en unos **10 pasos de 70 ms** con `font-variant-numeric: tabular-nums` para que los dígitos no bailen.
- **Movimiento y foco:** entrada firme en el corte (o `expo.out` / `power3.out`) seguida de un empuje lento (*push-in* suave y simétrico). Sin bamboleo artificial tipo cámara en mano ni rebotes de goma. Si movés texto rápido, el desenfoque solo dura en la entrada/salida (< 10 cuadros), nunca durante la lectura.
- **Texto sobre fotos cargadas:** nunca tires letras blancas sobre una foto llena de detalles sin fondo calmo; oscurecé el plano (12–38%), aplicá desenfoque suave (3–4,5 px) si la foto tiene texto propio, o poné una niebla suave detrás del texto.
- **Coherencia y no repetición:** aplicá el mismo criterio de color/grano al b-roll (las capturas de pantalla y UI van **sin** corrección de color) y **no repitas la misma foto dos veces** en el clip (salvo *callback* intencional al cierre).
- **Comparaciones visuales:** el lado ganador o la ventaja del producto tiene que verse como la forma más grande o llena.
- **En un golpe musical (*beat drop*):** reservá 2–3 planos reales y luminosos de la persona (tranquila, sin mover la boca en silencio) o el arranque del primer capítulo cortado exacto al pulso.

## 5. Sonido y chequeo por gráfico

- **Efectos de sonido:** armá el *cue sheet* en 3 pasadas (ver `criterio/sonido.md`): whooshes en movimientos, texturas/obturadores/clicks en cortes y apariciones, risers+hits en golpes de capítulo. Colapsá eventos a menos de **90 ms** entre sí.
- **Revisión en cuadros:** sacá 3 cuadros de cada gráfico (entrada, mitad, salida) y chequeá: se lee bien, no tapa la cara ni corta al sujeto, ningún subtítulo tapa texto del propio gráfico, el título de gancho está oculto en tarjetas, y la vuelta al plano de cámara es limpia.

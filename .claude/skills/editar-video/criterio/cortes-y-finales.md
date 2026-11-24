# Cortes, silencios y finales

Cómo elegir dónde empieza y dónde termina cada tramo en `plan.json` (`preparar-video`) para no cortar palabras ni dejar ideas colgadas.

## 1. El plan nombra palabras, nunca tiempos

Cada tramo en `plan.json` se define por **índices de palabras** (`[inicio, fin]` sobre `palabras.json`), nunca por segundos escritos a mano. El código traduce esos índices a tiempos exactos y los encaja en la grilla de cuadros. Escribir timestamps a mano corta palabras por la mitad; elegir palabras evita ese error.

Lo habitual en un clip hablado son **2 a 4 tramos** de una misma toma, sacando oraciones del medio que repiten el punto.

## 2. Dónde empieza un clip

- **En la primera frase limpia.** Revisá la transcripción buscando tartamudeos ("yo, yo, yo"), reinicios ("estaba, estaba por empezar") y muletillas de arranque ("eh", "bueno, nada", "o sea", "tipo", "pero una cosa que diría es…"). Quedate solo con la toma limpia.
- **Nunca en un conector suelto** que viene de la frase anterior ("y", "pero", "entonces", "así que").
- **Si la frase más fuerte está en el medio**, arrancá ahí y dejá el contexto después. La audiencia decide en los primeros 2 segundos.

## 3. Bordes de tramo y ajuste de silencios

Reglas medidas para `preparar-video`:

- **Entrada de tramo:** si había una palabra descartada dentro de **1,2 s** antes de la primera palabra elegida, entrar **50 ms** antes de la palabra. Si había silencio, retroceder al ataque audible menos **100 ms** de margen. Cuando un conector descartado ("pero", "entonces") está pegado sin pausa y se cuela su cola, probá entradas cada 60 ms, re-transcribí los primeros 3 s y elegí el centro del rango limpio.
- **Salida de tramo:** estimar el largo de la última palabra (**70 ms por letra + 200 ms**, mínimo **450 ms**). En tramos internos frenar al menos **20 ms antes** de la siguiente palabra descartada. En el tramo final dejar **0,9 s** de margen para que opere el corte de cierre.
- **Recorte de pausas:** pausas de **180 ms o más** se acortan a **120 ms** (45% después de la palabra saliente, 55% antes de la entrante). Huecos de **80 ms o menos** dentro de una palabra se cierran. Cada unión lleva un micro-fade de **4 ms** y cae en borde de cuadro (audio y video cortan juntos).
- **Detección de voz (VAD):** se corre siempre sobre el audio **crudo** de cámara (antes de procesar la voz), porque la cadena de voz vuelve al ruido de ambiente parecido al habla.
- **Protección de cierre y de tomas ruidosas:** nunca recortar por silencio desde el inicio de la **antepenúltima palabra** hasta el final del clip (las frases finales en voz baja engañan al detector). En tomas ruidosas (calle, colectivo, viento), proteger el rango de cada palabra elegida con **+60 ms** a cada lado para no perder palabras en el medio.
- **Sin astillas (*slivers*):** ningún fragmento menor a **0,6 s** entre dos cortes de pausa (**1,0 s** si la cámara va en mano o caminando). Si queda más corto, mantené la pausa vecina en vez de generar cortes frenéticos.
- **Un solo cambio por vez:** no apiles en el mismo segundo un corte de salto, un paneo brusco de reencuadre y la entrada de la música. Pasá la entrada musical al corte siguiente.

## 4. Dónde termina un clip

- **Frase cerrada con entonación descendente:** la última palabra lleva puntuación final (`.`, `!`, `?`) y la palabra siguiente en la grabación **no puede ser un conector de continuación**. En español, tratá como bloqueo duro las siguientes palabras después del punto de corte:
  > **"y", "pero", "entonces", "porque", "o", "tipo", "así que", "aunque", "que", "sino"**
  Si la toma sigue con uno de esos conectores, la voz quedó arriba y el clip va a sonar cortado aunque el texto tenga punto.
- **En el remate o la frase citable**, nunca en una introducción hacia otra idea.
- **Listas siempre cerradas:** si quedó "primero", "uno", "por un lado" o "no solo", tiene que quedar "segundo", "dos", "por otro lado" o el cierre correspondiente — si no, cortá el enumerador.
- **Llamado a la acción real:** si la toma ya trae una invitación hablada al final, conservala en vez de cortar en seco justo antes. Si el pensamiento no cierra en la toma, decilo en la nota y proponé una placa de cierre o un segundo tramo; nunca inventes palabras.

## 5. Corte milimétrico de la última palabra

Para evitar cortar letras finales ni dejar fugas de la frase siguiente:

1. Nunca cortar antes de que pase el cuerpo de la palabra (**30 ms por letra**, mínimo **120 ms** desde el ataque).
2. Cortar en la primera caída de **140 ms de silencio** tras la palabra (un hueco de 50 ms puede ser una consonante interna).
3. Si no sigue nada después, quedarse entre **60 ms y 300 ms** tras la caída para no comer consonantes finales suaves ("s", "d", "n").
4. Si sigue otra palabra sin pausa, frenar **40 ms antes** de su ataque.
5. Si el volumen cae y vuelve a subir **8 dB** dentro de los últimos **300 ms**, cortar en la caída (evita que se cuele el arranque de la siguiente sílaba).
6. Aplicar **40 ms de fade** en la voz y sumar **0,4 s de cola** de imagen y música al final, para que el fade de 0,3 s de la música nunca pise la última palabra.

**Nada de bocas moviéndose en silencio:** si la imagen sigue después de la última palabra (placa de cierre, CTA o cola musical), congelá el último cuadro y bajale el brillo a ~0,6, con el texto debajo del mentón.

## 6. Ritmo de cortes y verificación de empalmes

- Bajo narración, sostené cada plano **≥ 1 s** y cortá en límites de frase. El corte sub-segundo es solo para ráfagas de montaje o la apertura.
- En cortes de salto dentro de una misma toma, mantené la cara al mismo tamaño.
- **Revisá cada empalme:** re-transcribí el audio final y mirá ~1 s a cada lado de cada unión. Una palabra duplicada, una muletilla oculta ("¿viste?", "bueno", "entonces") o una palabra faltante en los bordes es un fallo de corte.


## Si el video no está en español

Las mismas reglas valen en cualquier idioma. En inglés, no terminar antes de: *and, but, so, because, or, like, that, which, if, then*. El gancho, los subtítulos y los textos en pantalla van **en el idioma del video**, salvo que la persona pida otro.

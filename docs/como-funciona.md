# Cómo funciona el kit por dentro

## La idea

Claude es el editor. El kit le da:
- **manos:** ffmpeg y Python, que cortan, recortan y procesan el audio;
- **oídos:** WhisperX, que transcribe cada palabra con su tiempo exacto;
- **un lienzo:** HyperFrames, que convierte código HTML en video cuadro por cuadro;
- **gusto:** los estilos y el criterio de edición, escritos como skills.

Como Claude no ve ni oye el video, todo lo que afirma sale de medir: vuelve a transcribir lo que exportó, mide el volumen y mira hojas de cuadros.

## ¿Código puro o HyperFrames?

Por debajo son lo mismo. **HyperFrames es "HTML renderizado a video":** una composición es HTML, CSS y JavaScript (GSAP, canvas, three.js). Cuando hacés motion 100% en código y lo querés pasar a video, algo tiene que:
- pausar la animación y llevarla al cuadro exacto;
- esperar a que carguen las fuentes y las imágenes;
- sacar 30 fotos por segundo;
- sincronizar el audio y los videos incrustados;
- armar el MP4.

HyperFrames hace todo eso, y además trae render en paralelo, controles antes de renderizar (textos fuera de cuadro, contraste, errores), medidores de video y un catálogo de bloques. Lemo escribió su propio motor para lo mismo. Remotion hace lo mismo con React.

## Los tres motores y para qué va cada uno

| Qué | Motor | Skill |
|---|---|---|
| Cortar a una persona hablando, sacar silencios, limpiar la voz, pasar a vertical siguiendo la cara | Python + ffmpeg | `preparar-video` |
| Armar: subtítulos, gráficos encima, escenas de corte, música | HyperFrames (o Remotion) | `montar-video` |
| Películas 100% animadas en un estilo artístico | Lemo, con su motor | `lemo-opuscar` |

**Lo grabado no se arma en HTML:** cortar y procesar audio con ffmpeg es más rápido y no se desincroniza. HyperFrames recibe a la persona ya preparada (`base.mp4`) y le pone todo lo demás encima.

## La mezcla: persona + animación

1. **Encima de la persona** (tarjetas, números, flechas, b-roll en ventana): código de HyperFrames con fondo transparente, anclado a una palabra. Si el estilo es de Lemo, se toma la estética de su `STYLE.md` y se escribe a la manera de HyperFrames.
2. **Corte a pantalla completa** (se va la persona, entra una animación y vuelve): una escena de HyperFrames, o un MP4 renderizado por Lemo con la duración exacta del hueco. La voz sigue por debajo.
3. **100% animado:** Lemo o HyperFrames, sin persona.

**¿Por qué el código de Lemo no se pega tal cual en HyperFrames?** Porque está escrito para su propio motor: espera a que carguen sus archivos antes de arrancar, usa rutas a su biblioteca, dibuja en un lienzo opaco de tamaño fijo y trae su propio sonido. HyperFrames necesita animaciones que se armen al instante y fondos transparentes para ir encima. **La estética se traduce; el código no se copia.**

## Por qué cada paso nombra palabras y no tiempos

El plan de un corte dice "de la palabra 120 a la 188", no "del 1:20 al 1:52". Los tiempos se calculan después, con margen hasta la palabra vecina. Así no se comen sílabas, y si hay que volver a transcribir no se rompe nada. Los subtítulos y los gráficos también se anclan a palabras.

## Qué se fija y qué se actualiza

Las herramientas externas se bajan de su fuente con una versión fija (`setup-kit/externas.json` y `package.json`). Así, lo que funcionó en clase funciona igual en la compu de cada uno. Para actualizar, se cambia la versión ahí y se prueba.

## Referencias: cómo aprende tu gusto

Un estilo se aprende mejor de varios ejemplos que de una descripción. Por eso el kit tiene `referencias/`, con una carpeta por tipo de estilo. La skill `referencias` mide cada video con `dissect` y con los medidores de HyperFrames: cortes en cuadros, subtítulos, tipografías, colores, dónde caen los ojos, cómo entra cada cosa y el sonido. Después busca lo que se repite entre todos y lo destila en tres ejes:
- **diseño;**
- **movimiento;**
- **relación con el guion:** qué frase dispara qué tipo de escena.

El resultado es un estilo propio en `estilos/propios/`, que se prueba sobre un video tuyo y se compara con la referencia con un puntaje.

Para copiar un video entero (no su estilo), `remake` lo reconstruye escena por escena como proyecto editable de HyperFrames y después se le cambia el contenido.

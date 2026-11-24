# Kit de edición de video con IA

Un conjunto de skills para que Claude Code edite video por vos: sacar clips de un podcast, subtitular un reel, poner gráficos encima de alguien hablando o hacer un video 100% animado. **No instalás nada a mano**: pegás un prompt y Claude instala y configura todo, en Mac, Windows o Linux.

## Empezar

1. Abrí Claude Code (terminal, app de escritorio o editor).
2. Pegá el prompt de [`prompts/setup.md`](prompts/setup.md).
3. Cuando diga que está listo, pedile cosas como las de [`ejemplos/README.md`](ejemplos/README.md).

## Tu estilo, a partir de tus referencias

Lo que más mejora tus videos es enseñarle tu gusto. Guardá videos que te gusten en [`referencias/`](referencias/README.md), **una carpeta por tipo de estilo** (por ejemplo `talking-head-minimal/`, `podcast-premium/`), y cuando tengas 5 o más pedile: *"destilá mis referencias de talking-head-minimal en un estilo"*. Claude las mide (cortes, subtítulos, tipografías, colores, composición, movimiento, sonido), arma un estilo propio en `estilos/propios/` y lo prueba con un video tuyo. Mientras tanto, tenés los estilos del kit y los 99 de Lemo.

## Qué trae

| Skill | Para qué |
|---|---|
| `editar-video` | La puerta: entiende el pedido y decide camino, motor y estilo |
| `transcribir` | Pasa la voz a texto con el tiempo exacto de cada palabra |
| `preparar-video` | Corta por palabras, saca silencios, limpia la voz y pasa a vertical siguiendo la cara |
| `montar-video` | Arma en HyperFrames los subtítulos, los gráficos encima, las escenas de corte y la música |
| `clipear-podcast` | Propone los mejores momentos de algo largo y los convierte en clips |
| `revisar-export` | Mide el resultado antes de entregarlo |
| `ffmpeg-basico` | Arreglos rápidos: cortar, comprimir, unir, sacar el audio |
| `referencias` | Desarma cualquier video, destila tus referencias en un estilo propio o reconstruye un video entero |
| `mi-estilo` | Crea o cambia un estilo a partir de una descripción, de un estilo del kit o de uno de Lemo |
| `setup-kit` | Instala, revisa y arregla todo |

**Y baja de su fuente original, con versión fija:**
- [HyperFrames](https://github.com/heygen-com/hyperframes) (HeyGen): el motor que convierte HTML en video y sus skills.
- [Lemo-Opuscar](https://github.com/lemomo-ai/lemo-opuscar): 99 estilos visuales para películas animadas.
- [dissect](https://github.com/0xpratzyy/dissect): mide videos de referencia y arma su plano y su fórmula.
- [Avocado Remake](https://github.com/Wandersonjack/avocado-remake): reconstruye un video entero como proyecto editable de HyperFrames (gratis; su paso de "rehacerlo con tu marca" es pago y opcional).
- [Remotion](https://www.remotion.dev): solo si lo pedís.

**Estilos:** los estilos del kit para subtítulos y gráficos (`estilos/`), los 99 de Lemo y los que crees vos (`estilos/propios/`).

## Para saber más

- [Cómo funciona por dentro](docs/como-funciona.md): qué motor hace qué y cómo se mezclan persona y animación.
- [Otras herramientas](docs/conoce-tambien.md): Scarlet, huashu-motion, Tesseract y más.
- [El método destilado](docs/destilado/sintesis.md): cómo trabaja un editor profesional con Claude, de las referencias al video terminado, y qué tomó el kit.

## Licencias

El código y los textos de este kit son MIT (ver `LICENSE`). HyperFrames, Lemo-Opuscar y Remotion se bajan de su fuente y tienen sus propias licencias:
- **Lemo-Opuscar:** sus textos son CC BY-NC.
- **Remotion:** es gratis para personas y equipos de hasta 3.
- **HyperFrames:** su plan Pro es pago; el kit no lo usa.

# Kit de edición de video con IA

Esta carpeta es un kit para editar video con Claude Code. La persona que lo usa puede no saber programar: hablale claro, en español, sin jerga, y hacé vos todo lo técnico.

## Volver a abrir el kit

Abrí Claude Code **dentro de esta carpeta**: en la terminal, `cd ~/kit-edicion-ia` y después `claude` (en Windows, `cd %USERPROFILE%\kit-edicion-ia`); en la app de escritorio o el editor, abrí la carpeta `kit-edicion-ia`. Así Claude carga las skills del kit.

## Reglas

- **Cualquier pedido de video empieza por la skill `editar-video`.** Ella decide el camino, el motor y el estilo, y llama a las demás. No le pidas a la persona que nombre skills, motores ni comandos.
- Si algo no está instalado o falla, usá `setup-kit` y arreglalo sin pedirle a la persona que instale nada.
- Los videos de la persona van en `proyectos/<nombre>/`. **El material original nunca se modifica ni se borra.**
- No ves ni oís los videos: todo lo que digas del resultado sale de una medición (`revisar-export`) o de mirar una hoja de cuadros.
- Antes de usar algo pago (un generador de imágenes, una voz de pago, el plan Pro de HyperFrames, la licencia de empresa de Remotion), avisá y ofrecé la alternativa gratis.
- No subas videos, transcripciones ni referencias de la persona a ningún servicio sin que lo pida.

## Qué hay

- `.claude/skills/`: las skills del kit (`editar-video`, `setup-kit`, `transcribir`, `preparar-video`, `montar-video`, `clipear-podcast`, `revisar-export`, `ffmpeg-basico`, `referencias`, `mi-estilo`) y las que instala el setup (HyperFrames, Lemo, dissect, remake y, si se pide, Remotion).
- `estilos/`: los estilos del kit. `estilos/propios/` guarda los que crea la persona.
- `referencias/`: videos que le gustan a la persona, una carpeta por tipo de estilo. La skill `referencias` los mide y los destila en estilos propios. Si hay referencias sin destilar, ofrecelo una vez.
- `ejemplos/`: pedidos de ejemplo.
- `docs/`: cómo funciona el kit por dentro y qué otras herramientas existen.

## Cómo se combinan los motores

- **Lo grabado** (cortar, silencios, voz, vertical) → Python + ffmpeg (`preparar-video`).
- **El armado** (subtítulos, gráficos encima, escenas de corte, música) → HyperFrames (`montar-video`), o Remotion si la persona lo pide.
- **Lo 100% animado** → Lemo con su motor, o HyperFrames.
- **La estética de Lemo encima de un video** → se traduce su `STYLE.md` a código de HyperFrames. Su código no corre dentro de HyperFrames.

`docs/como-funciona.md` lo explica con detalle.

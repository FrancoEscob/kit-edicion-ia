# Contrato entre las piezas del kit

Para quien construye o mantiene el kit. El alumno no necesita leerlo.

## La arquitectura en una frase

Lo grabado se **prepara** con Python + ffmpeg propio, se **arma** en HyperFrames (o Remotion si el alumno lo pide) y se **revisa** midiendo. Lo 100% animado se hace con el motor nativo de Lemo (o en HyperFrames si es un estilo nuestro). De Gorg no se usa código ni archivos: su criterio está reescrito en `editar-video/criterio/`.

## Carpetas

- `.claude/skills/`: las skills del kit, más las que baja el setup (HyperFrames, Lemo y Remotion, ignoradas por git).
- `.externas/`: lo que el setup baja de su fuente (el repo de Lemo, los modelos), ignorado por git.
- `estilos/`: los estilos del kit. `estilos/propios/` es la carpeta de cada alumno.
- `proyectos/<nombre>/`: el material y los resultados de cada video. Ignorada por git.
- `referencias/<tipo>/`: videos de referencia de la persona y sus análisis (`analisis/`, `formula.md`, `tablero.html`). Ignorada por git salvo su README.
- `.venv/`: el Python del kit.

## Cómo se pasan el trabajo

1. **transcribir** escribe en `proyectos/<nombre>/transcripcion/`:
   - `palabras.json`: `[{"i": 0, "w": "hola", "s": 12.41, "e": 12.62}, …]`, en segundos del archivo original, con alineación palabra por palabra;
   - `texto.txt`: la transcripción con una marca `[mm:ss]` por frase y el índice de la primera palabra, para que la lea Claude;
   - `subtitulos.srt`;
   - `info.json`: `{"fuente", "idioma", "modelo", "duracion_s"}`.
2. **preparar-video** lee un `plan.json`:
   ```json
   {"fuente": "proyectos/x/crudo.mp4", "palabras": "proyectos/x/transcripcion/palabras.json",
    "tramos": [[120, 188], [240, 301]], "formato": "9:16", "seguir_cara": true,
    "sacar_silencios": true, "salida": "proyectos/x/clip-1/"}
   ```
   Los `tramos` son índices de palabras (de la primera a la última incluida), nunca tiempos.

   Escribe en `salida`:
   - `base.mp4`: la persona cortada, con la voz limpia a −14 LUFS y en el formato pedido;
   - `base-palabras.json`: las palabras que quedaron, con tiempos en el reloj de `base.mp4`;
   - `informe.json`: lo que se midió y lo que no se pudo hacer.
3. **montar-video** arma la composición de HyperFrames en `salida/montaje/`, en capas, de abajo hacia arriba:
   1. la persona (`base.mp4`);
   2. las escenas de corte a pantalla completa (escritas ahí mismo, o un MP4 de Lemo);
   3. los gráficos encima, anclados a palabras de `base-palabras.json`;
   4. los subtítulos del estilo;
   5. el audio: la voz de `base.mp4` entera y la música con ducking.

   Renderiza a `salida/final.mp4`.
4. **revisar-export** recibe un MP4 y escribe `revision.md` junto a él, más una hoja de cuadros.

## Estilos

Un estilo del kit es una carpeta `estilos/<nombre>/` con:
- `ESTILO.md`: qué se ve, para qué sirve, de dónde sale, y las reglas con números (tipografía, tamaños, posición, palabras por subtítulo, entradas y salidas en ms, colores, qué va encima y cómo);
- `subtitulos.html` (opcional): el bloque de HyperFrames de los subtítulos, listo para usar;
- `ejemplo/` (opcional): una composición mínima de muestra.

Los estilos de Lemo no se copian: `montar-video` lee su `STYLE.md` en `.externas/lemo-opuscar/styles/<slug>/` y traduce la estética a código de HyperFrames para lo que va encima del video. Para una pieza 100% animada se usa Lemo con su propio motor.

## Catálogo

`editar-video/catalogo/` tiene un archivo por familia: `estilos-kit.md`, `lemo.md`, `hyperframes.md` y `remotion.md`. Cada entrada dice nombre, qué se ve, qué material pide, para qué uso sirve (encima del video, corte a pantalla completa o 100% animado), si anda en vertical y si necesita algo pago.

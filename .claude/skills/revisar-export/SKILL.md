---
name: revisar-export
description: Revisa un video terminado midiéndolo, porque Claude no ve ni oye el video — vuelve a transcribir lo exportado y lo compara con lo planeado, mide desfase de subtítulos, volumen, picos, negros, imagen trabada, silencios y largo de imagen contra audio, y arma una hoja de cuadros para mirar. Úsala siempre antes de entregar un video, y cuando la persona dice que algo "se ve raro" o "suena raro".
---

# Revisar un export

```
.venv/bin/python .claude/skills/revisar-export/scripts/revisar.py proyectos/x/clip-1/final.mp4 \
  --palabras proyectos/x/clip-1/montaje/base-palabras.json --formato 9:16
```
(Windows: `.venv\Scripts\python.exe`.) `--palabras` son las palabras que usaron los subtítulos, en el reloj del video final: si corregiste palabras en el montaje, pasá `CLIP/montaje/base-palabras.json`, no la de `preparar-video`. Sin `--palabras`, no se mide el desfase.

Escribe `revision.md` y `<nombre>-hoja.jpg` junto al video. Sale con 1 si hay alguna falla.

## Después del script

1. **Abrí la hoja de cuadros y mirala entera.** El script no ve: caras tapadas por texto, texto fuera de la zona segura (abajo y a la derecha en Reels y TikTok), gráficos que no caen donde deben, cortes que saltan, subtítulos con errores de ortografía o nombres mal escritos. Revisá la composición de `editar-video/criterio/composicion.md`: ojos cerca del tercio superior, nada tapando la cabeza, texto apoyado sobre el tercio inferior. Para la cara: `npx hyperframes measure face final.mp4 --samples 12` da la caja de la cara (los ojos caen más o menos al 40% de su alto desde arriba); la altura exacta de los ojos la deja `preparar-video` en `informe.json` → `encuadre.ojos_y_final`.
2. Si hay dudas en un momento puntual, sacá ese cuadro solo: `ffmpeg -ss T -i final.mp4 -frames:v 1 cuadro.jpg`.
3. Revisá contra `editar-video/criterio/revision.md`.
4. **Una sola pasada de arreglos:** corregí la causa (el plan, el estilo o la composición), no el síntoma, volvé a renderizar y volvé a correr el script. Si después de esa pasada sigue algo mal, entregá igual y decilo.

## La ronda de cambios de la persona

Después de entregar, pedile que mire el video entero y te pase **todos los cambios juntos**, numerados y con el segundo: "1. 0:04 el título más grande. 2. 0:12 acá quiero una imagen como esta [captura]". Aplicá la lista completa en una sola pasada, sin tocar lo que no está en la lista, y volvé a revisar.

## Cómo informar

En la entrega, en pocas líneas:
- qué se midió y dio bien (con números: LUFS, desfase en ms, duración);
- qué avisos quedan y por qué se aceptan;
- qué **no** se midió.

Nunca digas "suena bien" ni "se ve perfecto": decí qué mediste.

---
name: ffmpeg-basico
description: Arreglos rápidos de video y audio con ffmpeg, sin plan de edición — cortar un tramo, pasar a vertical o cuadrado, comprimir para WhatsApp o mail, sacar o cambiar el audio, unir videos, nivelar el volumen, quemar un .srt, sacar silencios simples, hacer un GIF, sacar cuadros o una hoja de cuadros, cambiar velocidad. Úsala cuando el pedido es una operación puntual sobre un archivo.
---

# ffmpeg básico

Recetas probadas. Antes de cualquier receta, mirá el archivo: `ffprobe -v error -show_entries format=duration:stream=codec_type,width,height,r_frame_rate -of json ENTRADA`.

Reglas:
- **Nunca pises el original.** La salida va con otro nombre, en `proyectos/<nombre>/`.
- Rutas con espacios, siempre entre comillas. En Windows (Git Bash) usá `/` en las rutas.
- Para cortes exactos, re-encodeá (`-c:v libx264`). `-c copy` es instantáneo, pero corta en el keyframe más cercano y se puede correr hasta 2 s.
- Para entregar en redes: `-c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart`.
- Al terminar, decí qué hiciste, el tamaño final y la duración, medidos con ffprobe.

## Cortar un tramo

```
ffmpeg -ss 00:01:20 -to 00:02:05 -i ENTRADA -c:v libx264 -crf 18 -preset medium -c:a aac -b:a 192k SALIDA.mp4
```
Para desde y hasta una palabra, usá la skill `transcribir` y tomá los tiempos de `palabras.json`, con 0,15 s de aire antes y después.

## Pasar a vertical 9:16 (centrado)

```
ffmpeg -i ENTRADA -vf "crop=ih*9/16:ih,scale=1080:1920,setsar=1" -c:v libx264 -crf 18 -c:a copy SALIDA.mp4
```
Si la persona no está en el centro, o se mueve, usá `preparar-video`, que sigue la cara. Cuadrado: `crop=ih:ih,scale=1080:1080`. 4:5: `crop=ih*4/5:ih,scale=1080:1350`.

**Vertical con fondo desenfocado** (cuando no hay que cortar nada del cuadro):
```
ffmpeg -i ENTRADA -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];[0:v]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2" -c:v libx264 -crf 18 -c:a copy SALIDA.mp4
```

## Comprimir

WhatsApp o mail (apunta a menos de 16 MB para un minuto):
```
ffmpeg -i ENTRADA -vf "scale='min(1080,iw)':-2" -c:v libx264 -crf 28 -preset slow -c:a aac -b:a 96k -movflags +faststart SALIDA.mp4
```
Si sigue grande, subí `-crf` de a 2.

## Audio

- Sacar el audio: `ffmpeg -i ENTRADA -vn -c:a libmp3lame -q:a 2 SALIDA.mp3`
- Quitar el audio: `ffmpeg -i ENTRADA -c:v copy -an SALIDA.mp4`
- Reemplazar el audio: `ffmpeg -i VIDEO -i AUDIO -map 0:v -map 1:a -c:v copy -c:a aac -shortest SALIDA.mp4`
- Nivelar a −14 LUFS (redes), en dos pasadas. Primero medí: `ffmpeg -i ENTRADA -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null -`. Después aplicá con los valores medidos: `-af loudnorm=I=-14:TP=-1:LRA=11:measured_I=…:measured_TP=…:measured_LRA=…:measured_thresh=…:offset=…:linear=true`.
- Música de fondo que baja cuando hay voz: no la hagas acá. Va en `montar-video`.

## Unir videos

Si todos tienen el mismo formato, tamaño y fps:
```
printf "file '%s'\n" uno.mp4 dos.mp4 > lista.txt
ffmpeg -f concat -safe 0 -i lista.txt -c copy SALIDA.mp4
```
Si son distintos, normalizá cada uno antes (mismo tamaño, fps y audio a 48 kHz) o usá el filtro `concat`.

## Subtítulos quemados desde un .srt

```
ffmpeg -i ENTRADA -vf "subtitles=subs.srt:force_style='FontName=Arial,FontSize=14,Bold=1,Outline=2,Alignment=2,MarginV=60'" -c:v libx264 -crf 18 -c:a copy SALIDA.mp4
```
Es para algo rápido. Los subtítulos con estilo (palabra por palabra, colores, animación) van en `montar-video`. En Windows, si la ruta del .srt tiene `C:`, copiá el .srt a la carpeta actual y usá solo el nombre.

## Sacar silencios simples

Para algo rápido sin transcribir (corta pausas de más de 0,6 s):
```
ffmpeg -i ENTRADA -af silencedetect=noise=-35dB:d=0.6 -f null - 2>&1 | grep silence_
```
Con esos tiempos armá los tramos con voz y unilos. Para un video que se va a publicar, usá `preparar-video`: corta respetando las palabras.

## Cuadros, hoja de cuadros y GIF

- Un cuadro: `ffmpeg -ss 12.5 -i ENTRADA -frames:v 1 cuadro.jpg`
- Hoja de cuadros (para mirar un video entero de un vistazo): `ffmpeg -i ENTRADA -vf "fps=1/2,scale=270:-2,tile=6x4" -frames:v 1 hoja.jpg` (un cuadro cada 2 s; ajustá `fps` a la duración).
- GIF liviano: `ffmpeg -i ENTRADA -vf "fps=12,scale=480:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse" SALIDA.gif`

## Velocidad

Al doble, con el audio a tono: `ffmpeg -i ENTRADA -filter_complex "[0:v]setpts=0.5*PTS[v];[0:a]atempo=2.0[a]" -map "[v]" -map "[a]" SALIDA.mp4`

---
name: referencias
description: Trabaja con videos de referencia — guardarlos ordenados por tipo de estilo en referencias/, desarmar cómo está hecho cualquier video (ingeniería inversa), destilar varias referencias de un mismo tipo en un estilo propio reutilizable, o reconstruir un video entero como proyecto editable. Úsala cuando la persona comparte un link o un video y dice "quiero que se vea así", "¿cómo está hecho esto?", "copiá este estilo", "rehacé este video", "armame un estilo con estas referencias", o quiere ordenar sus referencias.
---

# Referencias

Las referencias son la forma más rápida de que el kit edite con el gusto de la persona. La idea: **juntar varios videos de un mismo tipo, medirlos y destilarlos en un estilo propio**, que después se usa en todos sus videos.

## La carpeta

```
referencias/
  talking-head-minimal/     ← un tipo de estilo por carpeta, con el nombre que la persona quiera
    links.txt               ← un link por renglón (YouTube, Reels, TikTok, X…)
    ref-01.mp4              ← o los archivos directo
    notas.md                ← opcional: "me gustan los títulos, no la música"
  podcast-premium/
  reels-con-ui/
```

- **5 a 15 videos por tipo** es lo ideal: con 1 se copia un video; con varios se aprende un estilo (lo que se repite es el estilo, lo que cambia es el contenido).
- Si la persona manda links sueltos en el chat, preguntá de qué tipo son y guardalos en su carpeta.
- La carpeta es de la persona y no se sube a git. Las referencias se usan para aprender un formato, nunca para resubir el video de otro ni copiar su marca, su cara o su música.

Cuando la persona termina un video con el kit, recordale una vez, en una línea: "Si ves reels que te gusten, guardalos en `referencias/<tipo>/` y después te los destilo en un estilo".

**Bajar videos de YouTube:** si `yt-dlp` da error 403 o solo baja resoluciones bajas, primero actualizalo (`uv pip install --python .venv -U yt-dlp`). Si sigue, YouTube está pidiendo un "PO Token": seguí https://github.com/yt-dlp/yt-dlp/wiki/PO-Token-Guide (el proveedor automático es lo más simple). Para medir alcanza con 720p; para usar el video como material, 1080p o más.

## Qué querés hacer

| Pedido | Camino |
|---|---|
| "¿Cómo está hecho este video?", "¿por qué funciona?" | **A. Desarmar** un video |
| "Quiero ese estilo para mis videos", "armame un estilo con estas referencias" | **B. Destilar** un estilo |
| "Rehacé este video", "quiero uno igual pero con mi producto" | **C. Reconstruir** el video entero |
| "¿Qué tan parecido quedó mi video a la referencia?" | **D. Comparar** |

## A. Desarmar un video (ingeniería inversa)

Usá la skill `dissect`:
```
uv run .claude/skills/dissect/scripts/dissect.py "<link o archivo>" --out referencias/<tipo>/analisis/<nombre> --lang es
```
(`--lang` según el idioma que se habla. Para 4 o más videos, `--depth quick`.)

Seguí sus pasos 2 a 5: leé `facts.md` y `measured.md`, mirá las hojas en orden (`hook`, `shots`, `transitions`, `timeline`) y escribí el plano. **Lo medido manda:** no vuelvas a medir lo que ya está en `measured.md`; tu trabajo es explicar por qué funciona y cómo se construye cada movimiento.

Completá lo que dissect no mide y el kit necesita, con los medidores gratis de HyperFrames:
- **Composición:** `npx hyperframes measure face <video> --samples 12` para ver dónde caen los ojos (¿sobre el tercio superior, y≈640 de 1920?) y el tamaño de la cara. Leé `editar-video/criterio/composicion.md`.
- **Texto:** `npx hyperframes measure ink <video> --at T --roi …` en 3 a 5 momentos con texto: tamaño real en px, renglones, jerarquía (conector, bold, palabra de realce).
- **Movimiento:** `npx hyperframes measure curve` en las entradas de texto y gráficos: duración en ms, cuánto se pasa, curva GSAP.
- **Color:** `npx hyperframes measure look`; si hay oscurecido o desenfoque abajo, desde qué altura.

Contale a la persona, sin jerga, en 8 a 12 líneas: el gancho, la estructura, el ritmo de cortes, cómo son los subtítulos, la composición, los gráficos, el sonido y las 3 cosas que más hacen que funcione.

## B. Destilar un estilo (varias referencias → `estilos/propios/<nombre>/`)

1. **Medir cada referencia** de la carpeta con el paso A, una después de otra (nunca en paralelo: transcribir y medir usa mucha compu).
2. **Fórmula común:** con 2 o más, escribí `referencias/<tipo>/formula.md` como pide dissect ("Several videos"): qué se repite en todas (eso es el estilo), qué cambia, y medianas y rangos de los números.
3. **Tablero (opcional, recomendado con 5 o más):** armá `referencias/<tipo>/tablero.html`, un HTML local sin servidor con un cuadro por plano de cada referencia (de las hojas `shots` y `transitions`), agrupados por familia (gancho, persona hablando con subtítulos, b-roll, pantalla completa, gráficos encima). Cada cuadro tiene un tilde de "me gusta" y una línea para decir por qué, y un botón que guarda `eleccion.json`. Así la persona marca su gusto en 10 minutos, sin Figma. Lo elegido pesa más que el promedio al destilar.
4. **Destilar en tres ejes**, siempre con números y de dónde salen:
   - **Diseño:** tipografías (con su equivalente gratis en Google Fonts si es comercial), tamaños, colores (fijos o sacados del video de la persona), composición en tercios, texturas, oscurecidos, cajas.
   - **Movimiento:** cómo entra y sale cada cosa (ms, px, curva), cámara (zooms, punch-ins), transiciones y su duración en cuadros, ritmo de cortes.
   - **Relación con el guion:** qué frase o intención dispara cada tipo de escena (un dato → pantalla completa; una historia → b-roll; una transición → la persona sola), cuál es la palabra que se resalta en los subtítulos y por qué.
5. **Guardar** en `estilos/propios/<nombre>/` con el formato de `estilos/README.md`:
   - `ESTILO.md`: las reglas de los tres ejes. Arriba, "Basado en: N referencias de `referencias/<tipo>/`".
   - `subtitulos.html`: partí del estilo del kit más parecido (`editorial` para dos tipografías con palabra clave; `karaoke`, `limpio` o `impacto` para otros) y ajustalo a los números.
   - `paletas.json` si el color es fijo o sale del video de la persona.
   - `primitivas/` con las piezas que se repiten (tarjeta de dato, presentación de quien habla, marco de b-roll) como bloques de HyperFrames listos para reusar.
   - `referencias/` con 5 a 10 fichas de las mejores escenas: `still.jpg` + `keyframes.jpg` + `ficha.md` (categoría, cuadros, ms, px, colores hex, animación).
6. **Calibrar:** aplicalo con `montar-video` a 10 a 20 s de un video de la persona. Mostrá un cuadro al lado de uno de la referencia y compará con la parte D. Ajustá una vez. Un estilo bien afinado lleva su tiempo, pero después sirve para muchos videos.
7. Decile cómo pedirlo: "hacelo con mi estilo <nombre>".

## C. Reconstruir un video entero

Usá la skill `remake` (Avocado Remake). Reconstruye el video escena por escena como proyecto editable de HyperFrames y lo compara cuadro por cuadro con el original. Sus pasos 1 a 5 son gratis.
- **Su paso 6** (rehacerlo con otra marca, voz, música o actores) **usa créditos pagos de Avocado**: no lo hagas salvo que la persona lo pida y apruebe el costo. Para cambiar el contenido por el de la persona, editá vos el proyecto reconstruido: sus textos, sus imágenes y su música.
- No dejes el logo, el nombre, las imágenes ni la voz de otra marca en algo que se publique: se mantiene el ritmo y la estructura, se cambia el contenido.
- Si a `remake` le falta algo (no corre `hf`), revisá que estén las skills de HyperFrames (`setup-kit`).

## D. Comparar con la referencia

```
uv run .claude/skills/dissect/scripts/dissect.py check <tu-video.mp4> --ref referencias/<tipo>/analisis/<nombre>
```
Da un puntaje de 0 a 100 y qué corte o qué elemento mover, en cuadros. Usalo al calibrar un estilo (B.6), no en cada video.

## Los 99 estilos de Lemo como punto de partida

Si la persona todavía no tiene referencias, ofrecé el catálogo (`editar-video/catalogo/lemo.md`): puede elegir uno, verlo en la galería https://lemomo-ai.github.io/lemo-opuscar/ y usarlo tal cual o mezclarlo con sus referencias (`mi-estilo`).

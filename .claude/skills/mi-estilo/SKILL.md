---
name: mi-estilo
description: Crea o cambia un estilo propio del kit a partir de una descripción, de un estilo del kit o de la estética de un estilo de Lemo — "como karaoke pero en verde", "el editorial con mi tipografía", "la estética acuarela de Lemo para mis reels". Lo guarda en estilos/propios/ para usarlo con "hacelo con mi estilo <nombre>". Si la persona trae videos de referencia, usá la skill referencias.
---

# Mi estilo

Un estilo es una carpeta `estilos/propios/<nombre>/` con el formato de `estilos/README.md`: `ESTILO.md` con reglas y números, `subtitulos.html` listo para HyperFrames y, si hace falta, `paletas.json`, `primitivas/` y `referencias/`.

**¿Trae videos o links de referencia?** Usá la skill `referencias` (camino B): mide las referencias y destila el estilo con números reales. Esta skill es para todo lo demás.

## Desde un estilo del kit

"Como karaoke pero en verde y más chico", "el editorial pero con mi logo y Montserrat":
1. Copiá el estilo base (`estilos/<base>/`) a `estilos/propios/<nombre>/`.
2. Cambiá solo lo pedido, en `ESTILO.md` y en `subtitulos.html`. Para tipografías, usá los pares de `editar-video/criterio/subtitulos.md` o cualquiera de Google Fonts; si la persona tiene una tipografía propia, pedile el archivo y ponelo en la carpeta del estilo.
3. Anotá arriba del `ESTILO.md`: "Basado en: <base>. Cambios: …".

## Desde una descripción

"Algo sobrio, tipo documental, con letras grandes": elegí el estilo del kit más cercano, decí cuál y por qué en una línea, y seguí como arriba.

## Desde la estética de un estilo de Lemo

1. Leé su `STYLE.md` en `.externas/lemo-opuscar/styles/<slug>/` y mirá su ficha en `editar-video/catalogo/lemo.md` (si sirve encima de un video y en vertical).
2. Traducí a reglas para subtítulos y gráficos encima del video: paleta, tipografía (equivalente de Google Fonts si hace falta), trazo, texturas y movimiento. Respetá `editar-video/criterio/composicion.md` (ojos en el tercio superior, texto sobre el tercio inferior, zona segura).
3. Si el estilo tiene escenas que solo su motor puede dibujar (3D, WebGL, pintura), anotá en el `ESTILO.md` que esas escenas se renderizan con Lemo como corte a pantalla completa (ver `montar-video`).
4. Anotá: "Basado en el estilo `<slug>` de Lemo-Opuscar".

## Probar siempre

Aplicalo con `montar-video` a un tramo de 10 s de un video de la persona (o al de `proyectos/` más reciente) y mostrá 2 o 3 cuadros. Ajustá una vez.

## Al terminar

Decile el nombre y cómo pedirlo ("hacelo con mi estilo <nombre>"). `editar-video` ofrece primero los estilos de `estilos/propios/`.

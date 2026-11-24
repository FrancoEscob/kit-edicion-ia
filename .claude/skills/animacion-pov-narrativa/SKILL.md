---
name: animacion-pov-narrativa
description: Usá esta skill cuando te pidan un video animado como los de laurgrowth, una historia en primera persona con manos en cuadro, cámara de videojuego y dibujo con contornos, o un corto que termina en una elección entre dos opciones. Sirve para ficción, explicadores y demos narradas con HyperFrames.
---

# Animación narrativa en primera persona

1. Leé [ESTILO.md](ESTILO.md). Si la persona trae otra referencia, medila con el camino A de `referencias`. Para usar este estilo alcanza con definir el objetivo del personaje y las dos opciones del final.
2. Escribí el guion como una sucesión de acciones. Mostrá el objetivo en los primeros 250 ms, ensayá un gesto que se entienda sin audio y dejá unos 1,5 s para leer la elección final. Hacé que cada cambio de lugar responda a una acción.
3. Armá a 1080×1920 y 30 fps. Dibujá tres planos con el mismo punto de fuga y dejá al menos un 15% extra de escenario para los giros. Poné las manos en una capa aparte, ancladas a las esquinas inferiores. Reusá [la muestra HTML](primitivas/index.html) y [los movimientos GSAP](primitivas/pov.js). Registrá cada timeline pausada en `window.__timelines`.
4. Grabá o generá voces propias. Marcá cada golpe de sonido en la acción y sostené el ambiente en los silencios. Usá el [bloque de subtítulos](subtitulos.html) con `base-palabras.json` o poné las frases en el guion de montaje si ya tenés sus tiempos. Variá el color por voz y hacé que cada frase entre de golpe.
5. Corré `npx hyperframes lint <montaje>`, renderizá con `--quality high --fps 30` y pasá `revisar-export`. Mirá un par de tiras nativas con `measure frames --range=inicio,fin` para comprobar contacto, giro y lectura. Compará con `dissect.py check` cuando tengas una referencia disectada.

En el kit, la demo local queda en `proyectos/demo-laurgrowth/`. El contenido del guion, las voces, los dibujos y los efectos se crean para cada historia.

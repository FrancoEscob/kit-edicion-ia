---
name: clipear-podcast
description: Saca clips cortos (reels, shorts, TikToks) de un video largo — podcast, entrevista, charla, live, clase. Transcribe, propone los mejores momentos con su gancho y por qué, deja elegir, y produce cada clip vertical con subtítulos. Úsala cuando la persona trae algo largo y quiere piezas cortas, aunque no diga "clip".
---

# Clipear un podcast

## 1. Transcribir

Con la skill `transcribir`, sobre el archivo entero. Guardá todo en `proyectos/<nombre>/`. Leé `texto.txt` completo: lo que viene antes y después de un momento decide si el corte queda limpio.

## 2. Proponer

**Si el video es corto (menos de ~3 minutos) o la persona pide "el mejor momento"**, no armes una lista: elegí vos el mejor tramo con estas mismas reglas, decí en una línea por qué y seguí. La lista de candidatos es para material largo.


Leé `editar-video/criterio/seleccion-y-ganchos.md` y `cortes-y-finales.md`. Proponé **de 5 a 10 candidatos**, ordenados del mejor al peor. Para cada uno:

- **gancho:** el título que va en pantalla desde el cuadro 0;
- **de qué palabra a qué palabra** (citá las primeras y las últimas palabras, y sus índices de `palabras.json`) y la duración;
- **nota del 1 al 10 y por qué:** qué tiene (una historia, un número, una opinión fuerte, una pregunta que engancha) y qué le falta;
- **avisos:** datos que hay que verificar, menciones a terceros, algo que puede molestar.

En una entrevista, preferí los momentos **pregunta → respuesta con conclusión**: arrancan en la pregunta (o en el remate de la pregunta) y terminan cuando el invitado cierra la idea. Si el video tiene varias cámaras, mirá los cambios de ángulo (`npx hyperframes measure cuts`): un clip con algún cambio de plano retiene más. Si es un solo plano fijo, `montar-video` puede compensar con acercamientos suaves.

Mostralo como lista corta y preguntá cuáles hace. Si la persona dice "los que vos digas", hacé los 3 mejores.

Si hay **dos o más personas en cámara**, preguntá una sola vez si el vertical sigue a quien habla o si va centrado. Seguir a quien habla requiere saber quién habla en cada tramo: si no lo podés resolver bien, proponé centrado o pantalla partida.

## 3. Producir cada clip

Por cada clip elegido, en `proyectos/<nombre>/clip-<n>/`:

1. Un `plan.json` con los tramos en **índices de palabras** (contrato en `docs/contrato.md`). Un clip puede tener varios tramos: sacá una digresión del medio si el sentido se mantiene.
2. `preparar-video` → `base.mp4` + `base-palabras.json`.
3. `montar-video` con el estilo elegido: el gancho arriba al empezar, los subtítulos y, si suma, uno o dos gráficos anclados a palabras. No le pongas gráficos a todos los clips porque sí.
4. `revisar-export`.

Si son varios clips, hacé el primero completo y mostralo antes de hacer el resto, así la persona ajusta el estilo una sola vez.

## 4. Entregar

Una tabla corta con cada clip: archivo, gancho, duración y lo que midió la revisión. Ofrecé un texto para la publicación (2 o 3 líneas, en la voz de la persona) solo si lo pide.

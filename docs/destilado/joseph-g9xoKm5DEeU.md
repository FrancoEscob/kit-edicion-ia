# Destilado: Joseph — Minimal Talking Head Style (Arthur Brooks)

- **Video:** *How to Edit VIRAL Talking Head Videos Using ONLY Claude! (New Minimal Style)*
- **URL:** https://youtu.be/g9xoKm5DEeU
- **Fecha:** 31 de octubre de 2026
- **Duración:** 20:56 (`1256 s`)
- **Modelo y entorno mostrados:** Claude Desktop en modo **Cowork** (`This computer · AI Editing Folder · Auto`), modelo **Opus 5.5 Extra**, plan **Max** ($100/mes) (`[09:45]`, `[12:45]`, `[16:05]`).
- **Motor de video:** **Remotion** (`[16:30]`, `[16:36]`).
- **Estilo de referencia:** Estilo minimalista educativo/filosófico de **Arthur Brooks** (20 reels descargados de Instagram).
- **Clip editado en demo:** Fragmento de 57 s (*"Four career patterns"*) del podcast de Arthur Brooks con Chris Williamson (`G - Four career patterns.mp4`, `[12:45]`).

---

## 1. Resumen

Es el primero de la serie de cuatro videos. Joseph demuestra cómo entrenar a Claude para replicar un estilo editorial minimalista (el de Arthur Brooks, que según él los clientes pagan USD 100 por reel) sin Higgsfield ni plugins pagos: solo suscripción de Claude + Remotion. La tesis central del video —que repite en los cuatro— es la fórmula **"20 videos de referencia (lógica de animación y timing) + tablero de Figma (diseño y reglas visuales) = Skill reusable"**, y un flujo de producción donde **el humano planifica el guion escena por escena** mediante un documento HTML interactivo que genera Claude, y Claude ejecuta la búsqueda de assets, el armado en Remotion, una ronda de correcciones y el diseño sonoro.

---

## 2. Los 10 principios del estilo (lo que Joseph desarma a mano antes de entrenar)

Joseph explica que antes de entrenar a la IA tenés que entender el estilo como editor, porque si no sabés qué hace bueno a un video, usás la IA para fabricar basura (`[06:02]`). Desarma el estilo de Arthur Brooks en 10 familias de escenas:

1. **Captions en pantalla (`[01:08–01:58]`):** Máximo ~5 palabras por bloque. Combina dos tipografías: sans limpia para texto base (**Inter**) y serif/script cursiva para la palabra clave (**Playfair Italic**). No sigue una grilla fija sino una lógica: elige las palabras más importantes de la frase, las pone grandes y en negrita (sans bold o serif italic) en el centro, y mete el resto en tamaño chico en los huecos de arriba o abajo.
2. **B-roll + texto cinematográfico (`[01:58–02:30]`):** Divide el guion en segmentos cortos y busca B-roll literal de la acción mencionada (ej. si habla de pelear y resistir, alguien peleando). Al B-roll le suma **textura suave de papel**, **oscurecimiento de bordes (viñeta)** y **desenfoque leve en los bordes** para centrar el foco, con el texto encima siguiendo el principio 1.
3. **Animaciones de pinturas (`[02:31–02:56]`):** Para puntos filosóficos usa pinturas clásicas (sacadas de Wikipedia, ej. *A Lady Taking Tea* de Chardin o *The Kiss* de Hayez, `[16:30]`), les aplica textura de pintura + papel rugoso, pone texto cinematográfico alrededor del sujeto principal y remata con un **slide-in rápido de cámara** para revelarlas.
4. **Línea + texto (`[02:56–03:22]`):** Fondo blanco o negro con textura de papel; una línea azul de acento avanza, se interrumpe al toparse con el texto cinematográfico y continúa hacia el siguiente concepto, con la cámara siguiendo el recorrido de la línea.
5. **Línea + ilustraciones (`[03:22–03:55]`):** Mismo fondo y línea azul, pero guiando hacia ilustraciones: horizontal con punto blanco marcador + texto + ilustración abajo; o en zigzag con paneo de cámara revelando objetos a ambos lados para mostrar progresión en fases.
6. **Escenas text-centric (`[03:58–04:12]`):** Fondo blanco o azul con textura de papel muy rugosa, **dos comillas grandes** rodeando el centro y texto cinematográfico en el medio para frases de cierre.
7. **Ilustración central (`[04:12–05:00]`):** Una ilustración grande ocupa la mitad inferior y sangra hacia el centro superior sobre fondo papel blanco, tratada con textura rugosa/pintada/ruidosa o **textura de tela áspera** (especialmente en perfiles laterales de personajes, para generar contraste) y bordes abstractos que se funden con la escena; texto cinematográfico en el espacio libre.
8. **Ilustración lateral + texto (`[05:02–05:23]`):** Mismo lenguaje de texturas, pero con el personaje o un semicírculo de tela rugosa sobre un costado y el texto rotando o alineado del lado opuesto; se usa cuando hay que mostrar dos elementos en simultáneo.
9. **Objeto único + texto (`[05:24–05:37]`):** Un solo objeto/elemento narrativo sobre papel texturado con texto alrededor y revelados con estética rugosa.
10. **Gráficos y estadísticas (`[05:37–06:00]`):** Fondo oscuro plano con textura y grilla de líneas blancas finas con brillo suave (*glow*). Una bolita azul traza la línea del gráfico mientras la cámara sigue la punta en tiempo real.

---

## 3. Proceso paso a paso con marcas de tiempo

### Fase A — Recolección y entrenamiento de la skill (`[07:55–11:10]`)
1. **Curaduría de referencias (`[08:05]`):** Entra al Instagram de Arthur Brooks y descarga **20 reels** con la mejor edición.
2. **Primera pasada analítica (`[08:12]`):** Mira los 20 videos preguntándose en cada escena *por qué* el editor usó ese diseño, color, efecto y animación.
3. **Tablero de Figma (`[08:25–09:20]`):** Crea un tablero en Figma (`Clean Educational Style`, `[09:00]`). Vuelve a ver los 20 videos y saca captura de cada escena buena hasta juntar **~130 capturas**. Luego las agrupa en las 10 categorías y, al lado de cada bloque, hace zoom sobre 1 ejemplo y escribe el desglose (fuentes, colores, tamaños, patrones, layout).
4. **Carga y entrenamiento en Claude (`[09:25–11:03]`):** Abre Claude Cowork (`Opus 5.5 Extra`), adjunta la carpeta `20 reference videos` y el tablero `Clean Educational Style` (`[09:45]`), y corre el prompt de entrenamiento. Claude transcribe palabra por palabra, desarma cuadro por cuadro las 20 referencias, cruza la lógica temporal con el diseño de Figma y empaqueta la **Arthur Brooks Minimal Animation Skill** + una carpeta `225 Animations` (`[10:50]`).

### Fase B — Producción de un reel desde cero (`[11:45–19:00]`)
1. **Selección del crudo (`[11:55]`):** Baja un fragmento de 57 s de YouTube (`G - Four career patterns.mp4`).
2. **Corte de silencios + planificador interactivo (`[12:10–13:30]`):** Arrastra el video a Claude Cowork (`Opus 5.5 Extra`) y le pide transcripción al milisegundo, corte de silencios dejando **30 ms de margen (padding)**, y un documento de planificación interactivo con el guion a la derecha y diseños recomendados a la izquierda. Claude responde en 5 pasos (`[15:45]`): carga la skill, transcribe (237 palabras), corta silencios con 30 ms de padding, empareja cada línea con la carpeta de referencias y entrega `Four career patterns edit plan` (15 beats, 57.4 s).
3. **Planificación humana (`[13:30–15:38]`):** Joseph abre el documento HTML (`[13:10]`, `[13:15]`, `[13:45]`). Ve el guion, un reproductor embebido del clip, una nota **"SEEN IN THE REELS"** que cita referencias exactas (ej. `V10-A02` y hasta una regla de la guía de estilo: *"The seven 'up and's are a performance repeat; keep them all (style guide §10)"*), y 3 tarjetas recomendadas por beat con miniatura + ID (`V10-A02`, `V06-A37`, `V17-A19`, `V13-A22`). Elige o anota su decisión para los 15 beats y aprieta **Copy plan**.
4. **Ejecución en Remotion (`[15:38–16:50]`):** Pega el plan en Claude (`# Four career patterns edit plan · Beat 1 (0:00.0–0:01.9)...`, `[16:05]`) y lo autoriza a usar Chrome para conseguir assets. Claude arma una `Asset list` (6/6: pinturas de Wikipedia, B-roll de Pexels, retratos de Arthur de Wikipedia, `[16:30]`), descarga fuentes de Google Fonts, genera primero los captions de A-roll y luego cada escena en Remotion, y renderiza `Final Version.mp4` (`1080×1920`, `0:57`).
5. **Revisión y correcciones (`[16:50–17:32]`):** Asume que el primer borrador sale al **60–70%**. Mira el render y manda una lista numerada de **6 correcciones puntuales con marcas de tiempo** (`[17:10]`). Claude corrige y devuelve el v2.
6. **Diseño sonoro y música (`[17:32–17:58]`):** Confirma visualmente y autoriza el sonido (`[17:45]`). Claude consulta los 20 videos de referencia para calcar la estética sonora (música cinematográfica, clicks para texto, resaltadores/marker para gráficos, whooshes para transiciones) y exporta el video final (`[17:58–18:55]`).

---

## 4. Prompts textuales

### Prompt 1 — Entrenamiento de la skill (`[09:33–10:02]`, audio + confirmado parcialmente en pantalla en `[09:45]`)
> *"I want to teach you a new editing style. Analyze this clean premium minimal editing style using the 20 reference videos. Start by creating a word-by-word transcript and a frame-by-frame breakdown of every single video to study three main things. First, where the animations are placed in correlation with the script. Second, how the design is composed and what elements make it up. And third, the animation logic, how long the animations are and what they feel like so you can recreate them. Then use the Figma board as a reference that breaks down the elements of the style and master the style using both so that I could prompt you to recreate it."*

### Prompt 2 — Corte de silencios y documento de planificación (`[12:15–12:55]`, pantalla `[12:45]` + audio)
> *"I want you to use the Arthur Brooks minimal animation skill to edit this short-form clip in this premium editing style. Start by creating a word-by-word transcript at the millisecond level and cut out all silences leaving 30 milliseconds of padding. On top of that, hand me a document with the script of my raw video on the right side, and text boxes on the left with recommended designs pulled from the Arthur Brooks reference folder, so that I can plan out and decide what needs to be built for each scene."*

### Prompt 3 — Construcción de escenas y recolección de assets (`[15:40–16:05]`, pantalla `[16:05]`)
*(Pegando el plan copiado del documento HTML)*
> *"Build all the animations and create the edit. If it needs any assets, use the Chrome browser or files, and prompt me if there's anything it can't find."*

### Prompt 4 — Ronda de 6 revisiones (`[17:02–17:28]`, pantalla `[17:10]` + audio)
> 1. *"The text design in the first scene isn't good. Keep the word 'psychologically' up on the same scene."*
> 2. *"Rough cut between the graph and the next shot. Hold the graph text until 0:06, then cut."*
> 3. *"The paint texture is too heavy and [doesn't move with the animation]."* *(mostrado en `0:11`)*
> 4. *"Bad cut at second 24."*
> 5. *"The spiral animation needs to stay on the screen longer."*
> 6. *"Add quotation marks on the text scene at the end."*

### Prompt 5 — Paso a diseño sonoro (`[17:45]`, pantalla)
> *"It looks perfect. Go ahead with the sound design."*

*(Nota: en el material previo de Google Drive del curso de Joseph —`joseph-drive/prompts.txt` y `sound-design.md`— existe también un prompt maestro anterior en PDF para entrenar sobre las 4 categorías `text-centric / object-centric / character-centric / video-centric` y un manual completo de sonido en 4 pasadas: Whooshes a −10/−12 dB, Textures a −6/−7 dB, Risers a −5 dB, Música solo bajo talking head a −19 dB).*

---

## 5. Herramientas, skills y motores

| Herramienta | Para qué la usa | Pago / Gratis |
|---|---|---|
| **Claude Desktop (Cowork) + Opus 5.5 Extra** | Orquestador principal: analiza referencias, crea skills, genera el planificador HTML, escribe Remotion, corrige y sonoriza. | Pago (usa plan Max $100/mes; menciona que podría hacerse en Pro $20/mes). |
| **Figma** | Armar el tablero visual con ~130 capturas categorizadas y anotar el desarme de diseño (`Clean Educational Style`). | Gratis (tier gratuito alcanza). |
| **Remotion** | Motor de composición y render final en React (`1080×1920`). | Gratis para personas / equipos ≤ 3; pago para empresas. |
| **Chrome (automatizado por Claude)** | Buscar y descargar pinturas (Wikipedia), retratos (Wikipedia) y stock B-roll (Pexels) de forma autónoma (`[16:30]`). | Gratis (extensión/control del navegador de Claude). |
| **Google Fonts** | Descarga automática de Inter y Playfair Display Italic (`[16:32]`). | Gratis. |
| **Wikipedia + Pexels** | Fuentes gratuitas de pinturas, retratos y stock footage (`[16:30]`). | Gratis. |

---

## 6. Cómo arma y guarda el estilo como skill

En pantalla (`[10:40]`, `[10:50]`) se ven las piezas de la skill:
- **Reglas generales del estilo (`Arthur Brooks Minimal Animation Skill`):** cubre 5 ejes mostrados como íconos (`[10:40]`): **Sizing**, **Layout**, **Textures**, **Shapes**, **Colours**, más reglas editoriales numeradas (en `[13:45]` cita `style guide §10` sobre preservar repeticiones performáticas).
- **Biblioteca de referencias (`Arthur Brooks Study` / `225 Animations`):** 225 subcarpetas numeradas con el patrón **`V<num_video>-A<num_animación> <descripción corta>`**, por ejemplo (`[10:50]`):
  - `V01-A01 Zoom-out hook with serif headline`
  - `V01-A02 Stacked bold-sans caption groups`
  - `V01-A03 Body outline with four azure labels`
  - `V01-A06 Box wipe, line leads to brain`
  - `V01-A08 Azure highlight box 'enhance'`
  - `V01-A12 Thick azure line between two outcomes`
  - `V01-A13 Close-up serif-italic jargon`
  - `V01-A16 Night dinner table dolly`
- Cada carpeta contiene: **diseño de referencia** (cuadro limpio) + **hoja de keyframes** (*keyframe sheet*) de la animación (`[10:50]`).

---

## 7. Revisión, tiempos, costos y errores resueltos

- **Costo reportado (`[18:55]`):** USD 0 en plugins/Higgsfield; solo el plan de Claude (Max $100/mes; estima viable en $20/mes).
- **Desglose de tiempos (`[19:05–19:30]`, gráfico en `[19:15]`):**
  - Subir crudo + cortes de silencios + generar planificador: **15 min** (Claude).
  - Planificar el edit a mano: **15 min** (humano).
  - Construcción completa de captions, líneas, gráficos, pinturas, ilustraciones y render v1: **60 min** (Claude).
  - Ronda de 6 revisiones: **10 min** (Claude).
  - Sonido y música: **15 min** (Claude).
  - **Total:** **~1 h 55 min (~2 h)** de reloj, con solo **15 min de trabajo humano activo**.
- **Errores que muestra y cómo los resuelve (`[16:55–17:30]`):**
  1. Mal diseño de texto en el gancho y separación indebida de *"psychologically"* → le pide dejarla en la misma escena.
  2. Corte abrupto entre gráfico y toma siguiente → indica el segundo exacto (`hold until 0:06, then cut`).
  3. Textura de pintura demasiado pesada y estática (no acompañaba el movimiento de la pintura en `0:11`) → le pide alivianarla y ligarla al movimiento.
  4. Corte feo en el segundo 24 → lo señala por segundo.
  5. Ilustración de espiral demasiado breve → pide extender permanencia.
  6. Faltaban las comillas en la escena de cierre text-centric → pide agregarlas.

---

## 8. Trucos de edición destacados

- **Cadencia A-roll vs. visual (`[13:34–15:30]`):** Regla clara de alternancia: **cada vez que el hablante anuncia un concepto/tipo nuevo, se vuelve a su cara en A-roll** para reconectar; **cuando lo describe o ejemplifica, se muestra con animación, pintura o B-roll**.
- **No cortar repeticiones performáticas (`[13:45]`):** Cuando el hablante repite *"up and up and up..."* siete veces como recurso expresivo, **no se recorta como muletilla**; al contrario, se sincroniza el gráfico para que suba un escalón en cada *"up"*.
- **Padding milimétrico de silencios (`[12:34]`):** Corta silencios dejando **30 ms** de margen para mantener ritmo ágil sin comerse consonantes.
- **No delegar el guion visual a la IA (`[12:25]`):** Si dejás que Claude planifique solo desde cero, el resultado pierde intención editorial; pedirle recomendaciones referenciadas y que el humano decida cada beat eleva drásticamente la calidad.

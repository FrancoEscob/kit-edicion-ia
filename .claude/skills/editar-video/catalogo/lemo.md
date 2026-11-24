# Catálogo de estilos de Lemo-Opuscar (99 estilos)

Referencia en español de los **99 estilos** de [Lemo-Opuscar](https://github.com/lemomo-ai/lemo-opuscar) (commit `8ca0dd8`, [galería online](https://lemomo-ai.github.io/lemo-opuscar/)). Los `STYLE.md` viven en `.externas/lemo-opuscar/styles/<slug>/STYLE.md` (no se copian al repo).

## Cómo leer las columnas

- **Producción:** **E** = montaje documental con material real, archivo o datos; **C** = código puro (Canvas 2D, Three.js, WebGL2 o Python) sin generador obligatorio; **G** = requiere generador de imágenes externo.
- **Vertical (9:16):** evalúa si el estilo funciona en `1080×1920`.
  - **`sí` (54):** la composición del `STYLE.md` encaja natural en vertical.
  - **`adaptando` (33):** el `STYLE.md` está pensado apaisado (pliegos, pizarras, recorridos), pero anda en 9:16 si rearmás el layout vertical al escribir la escena.
  - **`no` (12):** la identidad depende de un cuadro ancho o 4:3 fijo (planillas con muchas columnas, split-screen horizontal, caja panorámica, escritorio ancho).
  - **Importante sobre los demos de muestra:** aunque el motor `core/render/video.mjs` acepta `--size 1080x1920`, en el código fuente de los demos solo **13 de 99** leen `innerWidth`/`innerHeight` (marcados con `*` abajo); los otros 86 fijan `1920×1080` en su demo. Al generar una pieza nueva con Lemo en vertical, siempre hay que pedirle que dibuje contra `innerWidth × innerHeight` (ver `docs/pruebas/lemo-hyperframes.md`).
- **Encima de video (`sí`: 47 / `no`: 52):** **`sí`** si la estética del `STYLE.md` (tipografía, tarjetas, flechas, diagramas, HUD, trazos, sellos) se puede traducir a código nativo de HyperFrames con fondo transparente flotando sobre una persona hablando; **`no`** si el estilo depende de un mundo opaco completo (pintura, 3D, diorama, térmica) — en esos casos se usa como **corte a pantalla completa** o **video 100% animado**.
- **Generador pago:** solo **3 estilos** (los de producción **G**: `text-flash-cuts`, `comic-history` y `manga-panels`, marcados con `✦` en Lemo) declaran `"needs": ["image-generation"]`. Según el README y `core/README.md` de Lemo, usan **Codex CLI (`codex login`) con una cuenta con generación de imágenes habilitada** (`core/image/gen_image.py`), o bien otro generador/API de imágenes pago que traiga la persona (o dibujos propios). Sin eso no pueden arrancar. Los otros **96 estilos** no piden nada pago.

## Regla rápida de uso en el kit

| Qué querés hacer | Qué motor usar |
|---|---|
| Gráfico **encima** de la persona hablando | Leer `STYLE.md` de un estilo con **Encima de video = sí** y traducir su estética a HTML/CSS/GSAP transparente en **HyperFrames** (`montar-video`) |
| **Corte a pantalla completa** dentro de un reel | Si es gráfico limpio/tipográfico: escena en **HyperFrames**. Si es 3D/WebGL/pintura compleja: MP4 renderizado con **Lemo** (`--size 1080x1920`, duración exacta del hueco) |
| Pieza **100% animada** sin persona a cámara | Motor nativo de **Lemo** (`lemo-opuscar`) |

### 01 · Edición y documental

| Slug | Nombre | En pantalla | Usos | Prod. | Vertical (9:16) | Encima de video | Generador pago |
|---|---|---|---|---|---|---|---|
| `caption-news` | Caption News | Subtítulos grandes cuentan una noticia incluso en silencio | Noticias, informes | E | sí | sí | no |
| `newsreel` | 1920s Newsreel | Archivo de época con rótulos de noticiero | Historia, aniversarios | E | adaptando | sí | no |
| `countdown` | Live Countdown Split-screen | Un reloj sincroniza celdas de video que se unen al final | Lanzamientos, directos | E | no | sí | no |
| `city-symphony` | City Symphony | Compara ritmos urbanos con acelerados y mosaicos | Barrios, aperturas | E | adaptando | no | no |
| `visual-investigation` | Visual Investigation | Fotos, testimonios y metraje comparten una cronología | Investigaciones, reconstrucciones | E | adaptando | sí | no |
| `kino-montage` | Constructivist Montage | Contrapone propaganda y registro del trabajo | Historia industrial, hitos | E | adaptando | no | no |
| `telestrator` | Sports Telestrator | Congela una jugada y dibuja recorridos sobre el campo | Deporte, formación | E | sí | sí | no |
| `news-package` | Broadcast News Package | Alterna titulares, zócalos y fichas en un boletín | Actualidad, mercados | E | adaptando | sí | no |

### 02 · Pintura e ilustración

| Slug | Nombre | En pantalla | Usos | Prod. | Vertical (9:16) | Encima de video | Generador pago |
|---|---|---|---|---|---|---|---|
| `crayon-book` | Crayon Picture Book | Un cuento nocturno se dibuja con crayones | Infancia, cuentos | C | sí | sí | no |
| `watercolor` | Watercolor Brush | El pigmento recorre un paisaje con la lluvia | Turismo, naturaleza | C | sí | no | no |
| `impasto` | Impasto Oil Painting | Un toque de color se propaga con pinceladas densas | Música, publicidad | C | sí | no | no |
| `urban-sketch` | Urban Sketch · Pen & Wash | La tinta fija la arquitectura y el color sigue al objeto | Ciudades, inmobiliarias | C | sí | no | no |
| `colored-pencil` | Colored-Pencil Science Illustration | Un corte bajo el suelo revela conexiones a lápiz | Ciencia, procesos | C | adaptando | no | no |

### 03 · Boceto y pizarra

| Slug | Nombre | En pantalla | Usos | Prod. | Vertical (9:16) | Encima de video | Generador pago |
|---|---|---|---|---|---|---|---|
| `one-line` | One-line Drawing | Una línea recorre las etapas de una vida | Marcas, hitos personales | C | sí | sí | no |
| `whiteboard` | Whiteboard Explainer | Una pizarra explica paso a paso el GPS | Cursos, divulgación | C | adaptando | sí | no |
| `chalkboard` | Chalkboard | La tiza borra una hipótesis y reconstruye el origen de un signo | Clases, mitos | C | adaptando* | sí | no |
| `sketchnote` | Sketchnote | Pequeños dibujos componen un resumen de una página | Clases, síntesis | C | sí | sí | no |
| `stick-explainer` | Stick-figure Explainer | Figuras de palitos hacen visible una red social | Redes, comparaciones | C | sí | sí | no |
| `ipad-sketch` | Tablet Sketch Explainer | Un dibujo digital sigue la transformación del café | Oficios, alimentos | C | sí | sí | no |
| `marker-paper` | Marker on Paper | Un marcador resuelve un problema de horizonte en papel | Lecciones, cálculos | C | sí | sí | no |

### 04 · Oficios tradicionales

| Slug | Nombre | En pantalla | Usos | Prod. | Vertical (9:16) | Encima de video | Generador pago |
|---|---|---|---|---|---|---|---|
| `ink-wash` | Chinese Ink Wash | Tinta y agua sugieren el movimiento de un espadachín | Poesía, cultura | C | sí | no | no |
| `shadow-puppet` | Shadow Puppetry | Figuras articuladas recortan siluetas contra una luz | Leyendas, festivales | C | no | no | no |
| `ukiyoe` | Ukiyo-e | Estampas sucesivas acompañan el viaje hacia una montaña | Turismo, poesía | C | sí | no | no |
| `papercut-red` | Red Paper-cut | Recortes rojos cuentan una fiesta de Año Nuevo | Saludos, folclore | C | sí | sí | no |
| `paper-lantern` | Paper-cut Lightbox | Capas de papel iluminadas acompañan el último tren | Viajes, despedidas | C | no | no | no |
| `stained-glass` | Stained Glass | La luz revela una leyenda en los paños de un vitral | Patrimonio, fiestas | C | sí | no | no |
| `gilded-illumination` | Gilded Illumination | El oro ilumina un relato pintado como manuscrito | Fábulas, orígenes | C | sí | no | no |

### 05 · Imprenta y grabado

| Slug | Nombre | En pantalla | Usos | Prod. | Vertical (9:16) | Encima de video | Generador pago |
|---|---|---|---|---|---|---|---|
| `risograph` | Risograph Print | Las tintas superpuestas acumulan color durante un paseo | Fanzines, marcas | C | sí | sí | no |
| `halftone-dossier` | Halftone Dossier | Una trama de puntos convierte a un gato en expediente | Humor, redes | C | sí | sí | no |
| `woodcut` | Woodcut Print | Una aldea y su oficio aparecen tallados en madera | Artesanía, libros | C | sí | no | no |
| `engraving` | Copperplate Engraving | La anatomía de una abeja emerge línea por línea | Museos, ciencia | C | sí | no | no |
| `silkscreen-poster` | Silkscreen Travel Poster | Cada destino se convierte en un afiche serigrafiado | Turismo, eventos | C | sí | sí | no |
| `printed-long-take` | Scratchboard Long Take | Un trazo raspado recorre el paisaje sin corte | Naturaleza, viajes | C | no* | no | no |
| `pop-art` | Pop Art | Repetición y tramas de cómic explican un producto | Publicidad, datos | C | sí | sí | no |
| `vintage-collage` | Vintage Engraving Collage | Fragmentos de archivo reconstruyen una estampilla perdida | Historia, coleccionismo | C | sí | sí | no |

### 06 · Diseño gráfico y tipografía

| Slug | Nombre | En pantalla | Usos | Prod. | Vertical (9:16) | Encima de video | Generador pago |
|---|---|---|---|---|---|---|---|
| `swiss-motion` | Swiss Motion Graphics | La tipografía arma un afiche sobre una retícula | Identidad, eventos | C | sí | sí | no |
| `spy-titles` | 60s Spy Title Sequence | Formas gráficas convierten una persecución en créditos | Tráilers, aperturas | C | adaptando | sí | no |
| `art-deco` | Art Deco | Simetría y ornamento sitúan una historia en un hotel | Hotelería, lujo | C | sí | sí | no |
| `pictogram-motion` | Pictogram Motion | Señales geométricas cuentan una peripecia urbana al compás | Servicios, identidad | C | sí | sí | no |
| `bauhaus-shapes` | Bauhaus Shapes | Puntos que se multiplican explican interés compuesto | Finanzas, educación | C | sí | sí | no |
| `flat-space-explainer` | Scale Zoom Explainer | Un zoom encadena escalas desde una galaxia a un virus | Ciencia, aula | C | sí | no | no |
| `text-flash-cuts` | Text Flash Cuts | Cortes de texto e ilustración sostienen el suspenso | Tráilers, manifiestos | G | sí | sí | sí (Codex CLI con imágenes / API) |
| `silhouette-rhythm` | Silhouette Rhythm | Las siluetas de una bandada marcan el pulso | Música, deporte | C | sí* | no | no |

### 07 · Diagramas de línea

| Slug | Nombre | En pantalla | Usos | Prod. | Vertical (9:16) | Encima de video | Generador pago |
|---|---|---|---|---|---|---|---|
| `blueprint` | Blueprint | Un plano técnico dibuja y desarma una máquina | Ingeniería, hardware | C | adaptando | sí | no |
| `iso-infographic` | Isometric Infographic | Un mundo isométrico conecta las etapas del café | Procesos, logística | C | adaptando | sí | no |
| `teardown` | Exploded Teardown | Una órbita separa las piezas de un teclado | Producto, especificaciones | C | sí | no | no |
| `hardcore-info` | Line-Art Cutaway | El despiece muestra por qué la mano tapa la antena | Tecnología, formación | C | adaptando | sí | no |
| `precise-mechanism` | Color-Coded Mechanism | Colores distinguen los sistemas de un reloj | Mecánica, producto | C | adaptando | sí | no |
| `instruction-manual` | Instruction Manual Art | Una página de instrucciones guía el montaje | Onboarding, seguridad | C | sí* | sí | no |
| `pen-plotter` | Pen Plotter | Cuatro plumas trazan relieve a partir de alturas | Mapas, mediciones | C | sí* | sí | no |
| `assembly-line-diagram` | Assembly-Line Diagram | Una fábrica invertida explica cómo funciona la digestión | Procesos, biología | C | no | no | no |

### 08 · Dibujos animados

| Slug | Nombre | En pantalla | Usos | Prod. | Vertical (9:16) | Encima de video | Generador pago |
|---|---|---|---|---|---|---|---|
| `rubber-hose` | 1930s Rubber Hose Cartoon | Una taza animada persigue azúcar con extremidades flexibles | Alimentos, anuncios | C | adaptando | no | no |
| `cel-anime-80s` | 80s Cel Anime | Animación ochentera de acetato, neón y lluvia | Música, videojuegos | C | adaptando | no | no |
| `scifi-toon` | Sci-Fi Sitcom Toon | Un portal enlaza mundos de caricatura futurista | Comedia, tecnología | C | adaptando | no | no |
| `midcentury-toon` | Mid-century Cartoon | Una película escolar retro enseña a configurar un aparato | Ayuda, tutoriales | C | adaptando | no | no |
| `comic-history` | Comic History Cartoon | Recortes de historieta representan cambios territoriales | Geopolítica, mercados | G | adaptando | sí | sí (Codex CLI con imágenes / API) |
| `manga-panels` | Manga Panels | Viñetas fragmentan un instante en múltiples vistas | Música, lanzamientos | G | sí | sí | sí (Codex CLI con imágenes / API) |

### 09 · Videojuegos

| Slug | Nombre | En pantalla | Usos | Prod. | Vertical (9:16) | Encima de video | Generador pago |
|---|---|---|---|---|---|---|---|
| `pixel-rpg` | 16-bit Pixel RPG | Una partida guardada repasa la historia en píxeles | Juegos, resúmenes | C | adaptando | sí | no |
| `hd-2d` | 2.5D Pixel Art | Un personaje pixelado cruza un paisaje con profundidad | Fantasía, juegos | C | adaptando | no | no |
| `microgame` | Microgame Frenzy | Retos de cinco segundos aceleran el montaje | Onboarding, redes | C | sí | sí | no |
| `game-show` | Rhythm Game Show | Una cronología tecnológica adopta el ritmo de un concurso | Balances, tecnología | C | sí | sí | no |

### 10 · Cine y cinta

| Slug | Nombre | En pantalla | Usos | Prod. | Vertical (9:16) | Encima de video | Generador pago |
|---|---|---|---|---|---|---|---|
| `ascii-crt` | CRT ASCII Terminal | Un terminal dibuja una respuesta con caracteres | Herramientas de desarrollo | C | adaptando | sí | no |
| `silent-film` | 1920s Silent Film | Una persecución se entiende como comedia muda | Humor, marcas retro | C | no | no | no |
| `backrooms` | Liminal Found Footage | Un recorrido de oficina simula una cinta inquietante | Misterio, teasers | C | no | no | no |
| `scratch-film` | Scratch Film | Marcas de luz sobre negro revelan la vida nocturna | Naturaleza, aventuras | C | sí | sí | no |
| `double-exposure` | Double Exposure | Cada silueta contiene otro paisaje | Identidad, aperturas | C | sí* | no | no |

### 11 · Pantallas e interfaces

| Slug | Nombre | En pantalla | Usos | Prod. | Vertical (9:16) | Encima de video | Generador pago |
|---|---|---|---|---|---|---|---|
| `dark-keynote` | Dark Tech Keynote | Un gesto ordena ventanas sobre fondo oscuro | Software, lanzamientos | C | sí | sí | no |
| `living-screencast` | Mascot Screencast | Una mascota guía el recorrido de una interfaz | Tutoriales, funciones | C | no | no | no |
| `hologram-hud` | Sci-fi Hologram HUD | El escaneo holográfico localiza piezas de una bicicleta | Ferias, producto | C | sí | sí | no |
| `desktop-flythrough` | Tabletop App Flythrough | La cámara enlaza tarjetas de apps como objetos de escritorio | Flujos, software | C | no | no | no |
| `spreadsheet` | Spreadsheet Film | Abrir columnas ocultas cambia la interpretación del total | Datos, costos | C | no | sí | no |
| `one-bit-dither` | 1-bit Dither | Una imagen lunar se imprime en dos tonos línea a línea | Historia, señales | C | sí* | no | no |

### 12 · Luz y líneas

| Slug | Nombre | En pantalla | Usos | Prod. | Vertical (9:16) | Encima de video | Generador pago |
|---|---|---|---|---|---|---|---|
| `circuit-board` | Circuit Board | Las pistas de cobre siguen la electricidad hasta el cargador | Energía, dispositivos | C | adaptando | sí | no |
| `firefly-pointillism` | Firefly Pointillism | Puntos luminosos forman figuras en la oscuridad | Infancia, naturaleza | C | sí | no | no |
| `flow-field` | Flow-field Wind Lines | Líneas de viento reconstruyen la evolución de un tifón | Meteorología, corrientes | C | adaptando* | no | no |
| `oscilloscope-math` | Oscilloscope Math | Círculos y ondas muestran una aproximación matemática | Física, electrónica | C | adaptando | sí | no |
| `neon-tubes` | Neon Tubes | Los tubos de un cartel de neón cobran vida | Comercios, vida nocturna | C | sí* | sí | no |

### 13 · 3D y miniaturas

| Slug | Nombre | En pantalla | Usos | Prod. | Vertical (9:16) | Encima de video | Generador pago |
|---|---|---|---|---|---|---|---|
| `brick-toy` | Brick Toy | Un astronauta arma un cohete con bloques | Juguetes, montaje | C | sí | no | no |
| `paper-popup` | Paper Pop-up Book | Al abrirse un libro aparecen mundos en relieve | Libros, fantasía | C | adaptando | no | no |
| `tilt-shift` | Tilt-Shift Miniature | La ciudad en hora pico parece una maqueta en movimiento | Inmuebles, transporte | C | adaptando | no | no |
| `lowpoly-island` | Low-poly Isometric Island | Una isla poligonal crece pieza por pieza | Juegos, ambientación | C | sí | no | no |
| `glass-product` | Glass Product Render | Barridos de luz revelan auriculares de vidrio | Belleza, tecnología | C | sí | no | no |
| `memphis-diorama` | Memphis Diorama | Una misma maqueta cambia de estación sin corte | Loops, portadas | C | sí | no | no |
| `isometric-picture-book` | Isometric People Scene | Una escena isométrica compara órdenes de embarque | Reglas, comparaciones | C | adaptando | no | no |
| `crayon-world` | Crayon World 3D | La cámara sobrevuela un pueblo tridimensional de crayón | Homenajes, relatos | C | sí | no | no |

### 14 · Instrumentos y evidencia

| Slug | Nombre | En pantalla | Usos | Prod. | Vertical (9:16) | Encima de video | Generador pago |
|---|---|---|---|---|---|---|---|
| `satellite-briefing` | Satellite Briefing | Una vista satelital contrasta el mapa con el agua real | Clima, geografía | C | adaptando | no | no |
| `briefing-board` | Engineering Briefing Board | Un tablero somete cuatro diseños a la misma prueba | Opciones, ingeniería | C | no* | no | no |
| `lidar-survey` | LiDAR Survey | Un escaneo láser retira la cubierta forestal | Patrimonio, terrenos | C | sí | no | no |
| `microscope` | Under the Microscope | Una aproximación continua permite medir una muestra | Biomedicina, materiales | C | sí | no | no |
| `archive-lighttable` | Archive Light Table | Una lupa confronta documentos y fotografías | Museos, historia de marca | C | no | no | no |
| `security-xray` | Security X-ray | Una consola de rayos X revela contenido oculto | Inspección, producto | C | sí* | no | no |
| `dark-documentary` | Radar Sweep Documentary | Una reconstrucción oscura sigue una antena bajo tormenta | Ciencia, arqueología | C | adaptando | no | no |
| `thermal-camera` | Thermal Camera | Una vista térmica compara un edificio antes y después | Eficiencia, inmuebles | C | sí* | no | no |

### 15 · Datos y mapas

| Slug | Nombre | En pantalla | Usos | Prod. | Vertical (9:16) | Encima de video | Generador pago |
|---|---|---|---|---|---|---|---|
| `dataviz` | Data Storytelling | El gráfico narra un siglo de temperaturas | Informes, periodismo | C | adaptando | sí | no |
| `white-model` | Projection-Mapped Model | Proyecciones sobre una maqueta explican cambios urbanos | Urbanismo, exposiciones | C | adaptando | no | no |
| `data-physical` | Data Physicalization | Placas apiladas permiten comparar dos series de energía | Inversores, balances | C | sí | no | no |
| `transit-map` | Transit Map | El crecimiento de una red se dibuja estación por estación | Transporte, expansión | C | adaptando* | sí | no |
| `map-explainer` | 3D Map Explainer | El mapa baja del globo a las rutas de un estrecho | Comercio, geopolítica | C | adaptando | no | no |
| `pip-simulation` | Blob Simulation | Una población simulada permite comparar estrategias | Evolución, mercados | C | sí | no | no |

`*` El demo original de Lemo ya lee `innerWidth`/`innerHeight` (aunque algunos igualmente asumen márgenes o proporciones de 16:9; ver pruebas en `docs/pruebas/lemo-hyperframes.md`).

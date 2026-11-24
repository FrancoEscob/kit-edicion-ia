# Otras herramientas que conviene conocer

El kit usa HyperFrames, Lemo y, si se pide, Remotion. Estas otras existen, se mostraron en clase y no vienen instaladas. Si querés probar alguna, pedíselo a Claude.

## Scarlet
- **Qué es:** un editor de escritorio (Mac, Windows y Linux) que se conecta al Claude Code de tu compu. Hace cortes, subtítulos, punch-ins con seguimiento de cara, b-roll y gráficos.
- **Lo mejor:** te deja corregir dibujando sobre el cuadro o con la voz, y aprende de tus correcciones repetidas (las convierte en reglas). Exporta a Premiere, DaVinci y Final Cut.
- **Cuándo:** si querés una app con ventana para revisar en vez de hacer todo por chat.
- **Ojo:** es muy nuevo (v0.1). En Windows el instalador no está firmado y puede bloquearse. Licencia MIT.
- https://github.com/Forward-Future/scarlet

## huashu-motion
- **Qué es:** un motor de motion graphics en código (un `index.html` con GSAP, Canvas o Three.js) con un estudio en el navegador, en español, para editar textos y colores con un clic.
- **Lo mejor:** música y efectos locales que siguen el ritmo, mezcla a −14 LUFS y controles de calidad (detecta "se lee como diapositivas" y tiempo muerto).
- **Cuándo:** piezas 100% animadas con música, como alternativa a Lemo.
- **Ojo:** el autor lo prueba en Mac; en Windows a veces deja un MP4 vacío. Licencia MIT.
- https://github.com/alchaincyf/huashu-motion

## Tesseract
- **Qué es:** un motor de edición con proyecto editable (`.tsrct`): cortes, subtítulos y motion, rápido y sin internet.
- **Ojo:** no transcribe, no tiene app para editar a mano y su licencia es propietaria y revocable (tiene tope de facturación y prohíbe competir con él).
- https://github.com/mirage-hq/tesseract

## Gorg
- **Qué es:** un editor de video que se maneja desde Claude Code, iMessage o WhatsApp. Es un producto cerrado y va a ser pago.
- **Qué tomamos:** nada de su código. Su forma de pensar una edición (cómo elige momentos, dónde corta, cómo revisa) inspiró el criterio del kit, que está reescrito en `editar-video/criterio/`.
- https://www.gorg.ai

## Otras de ingeniería inversa
El kit trae `dissect` (mide) y `remake` (reconstruye). Estas también existen:
- **reverse-any-video** (HyperFrames): reconstruye y compara contra el original; es del plan Pro (pago).
- **REA-Video:** desarma un video plano por plano (cómo se hizo cada imagen, gráficos, sonido) y propone cómo recrearlo. Gratis, Apache-2.0. https://github.com/JuneYaooo/rea-video
- **OpenMotion:** estudio propio que reconstruye videos en HTML; su camino recomendado es en la nube y pide claves de modelos para lo generativo. https://github.com/nexu-io/openmotion

## Otras, por si las necesitás
- **auto-editor:** saca silencios automáticamente y exporta a Premiere, DaVinci o Final Cut. Útil si vas a terminar el video en un editor. https://github.com/WyattBlue/auto-editor
- **PySceneDetect:** encuentra los cortes de un video, para analizar el ritmo de una referencia. https://github.com/Breakthrough/PySceneDetect
- **Remotion:** ya está en el kit como opción. https://www.remotion.dev

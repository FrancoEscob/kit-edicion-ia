---
name: setup-kit
description: Instala, revisa y arregla todo lo que necesita el kit de edición (ffmpeg, Node, Python, modelos, HyperFrames, Lemo y, si se pide, Remotion) en Mac, Windows o Linux. Úsala la primera vez, cuando algo del kit no anda, o cuando la persona dice "arreglá el kit", "instalá todo" o "actualizá el kit".
---

# Setup del kit

La persona no instala nada a mano: lo hacés vos. Explicá en una línea qué vas a instalar antes de cada bloque grande. Si un paso pide la contraseña de administrador, decile para qué es y esperá.

## 0. Mirá qué falta

```
python3 .claude/skills/setup-kit/scripts/doctor.py      (Windows: python ...)
```

Instalá solo lo que sale con ✗ y volvé a correrlo al final. Los ítems con · son opcionales.

## 1. Programas del sistema

Usá el gestor de paquetes de cada sistema:
- **Mac:** Homebrew. Si no está, instalalo desde https://brew.sh y seguí sus instrucciones para el PATH. Después: `brew install git node ffmpeg uv`.
- **Windows:** winget, que viene con el sistema: `winget install --id Git.Git -e`, `winget install --id OpenJS.NodeJS.LTS -e`, `winget install --id Gyan.FFmpeg -e` y `winget install --id astral-sh.uv -e`. Después abrí una terminal nueva para que tome el PATH. Claude Code en Windows corre comandos en Git Bash: los `sh` del kit andan ahí.
- **Linux:** el gestor de la distribución (apt, dnf, pacman). Si el ffmpeg es anterior a 7, bajá un build estático de https://johnvansickle.com/ffmpeg/ y ponelo en el PATH. Para uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`.

Hace falta Node 22 o más nuevo y ffmpeg 7 o más nuevo, con los filtros `loudnorm` y `subtitles`. `arnndn` es opcional: limpia mejor el ruido.

## 2. Python del kit

```
uv venv --python 3.12 .venv
uv pip install --python .venv -r .claude/skills/transcribir/requirements.txt -r .claude/skills/preparar-video/requirements.txt
```

uv baja Python 3.12 si no está, así que no hace falta instalarlo aparte. Para correr scripts: `.venv/bin/python` (Windows: `.venv\Scripts\python.exe`). Si WhisperX falla al instalarse, seguí el camino alternativo que explica `transcribir/SKILL.md`.

## 3. Modelos

Bajá a `.externas/modelos/` los tres archivos de `externas.json` → `modelos` (silencios, caras y ruido), con `curl -L -o`.

## 4. HyperFrames

```
npm install
npx -y skills add heygen-com/hyperframes -a claude-code -y --copy -s hyperframes -s hyperframes-cli -s hyperframes-registry -s media-use -s slideshow -s remotion-to-hyperframes
npx hyperframes doctor
```

`npm install` deja HyperFrames 0.9.90 en el kit, así `npx hyperframes` usa siempre esa versión. **No instales `style-sampling` ni `reverse-any-video`**: son del plan pago. Si `hyperframes doctor` pide Chrome, instalalo como indica.

## 5. Lemo (99 estilos)

```
git clone --filter=blob:none https://github.com/lemomo-ai/lemo-opuscar.git .externas/lemo-opuscar
git -C .externas/lemo-opuscar checkout <commit de externas.json → lemo>
cp -r .externas/lemo-opuscar/plugin/skills/lemo-opuscar .claude/skills/
```

Escribí `.claude/settings.local.json` con la ruta **absoluta** de la biblioteca (si el archivo ya existe, sumá la clave sin borrar lo que haya):
```json
{ "env": { "LEMO_OPUSCAR_HOME": "/ruta/absoluta/al/kit/.externas/lemo-opuscar" } }
```
Esa variable recién se carga en la próxima sesión de Claude Code. En esta, anteponela a cada comando de Lemo: `LEMO_OPUSCAR_HOME=… sh …`.

Después instalá sus paquetes base:
```
LEMO_OPUSCAR_HOME="$PWD/.externas/lemo-opuscar" sh .claude/skills/lemo-opuscar/scripts/setup.sh deps
```
La voz (`deps voice`) y la música (`deps music`) se instalan la primera vez que un video de Lemo las necesite, no antes.

**No uses** `claude plugin install` para Lemo en este kit: esa versión se actualiza sola a la última, y acá queremos la versión fijada.

## 6. Ingeniería inversa: dissect y remake

Las dos se bajan de su fuente con la versión fijada en `externas.json` y se copian a `.claude/skills/`:
```
git clone --filter=blob:none <repo> .externas/<nombre>
git -C .externas/<nombre> checkout <commit>
cp -r .externas/<nombre>/<skill> .claude/skills/<nombre>
```
(`dissect`: skill en `plugins/dissect/skills/dissect`; `remake`: skill en `skills/remake`.)

- **dissect** mide videos de referencia. En Linux y Windows necesita **tesseract** para leer el texto en pantalla (Mac usa Apple Vision): `winget install --id UB-Mannheim.TesseractOCR -e` o el gestor de Linux. Revisalo con `python3 .claude/skills/dissect/scripts/doctor.py`. La primera vez que mide, baja unos 600 MB de paquetes y un modelo de voz: avisá que es una espera única.
- **remake** reconstruye un video entero como proyecto de HyperFrames. Usa solo comandos gratis de HyperFrames, ffmpeg y python3. Su paso 6 (rehacerlo con una marca) pide créditos de Avocado: nunca lo uses sin que la persona lo pida y apruebe el costo.

## 7. Remotion (solo si lo piden)

```
npx -y skills add remotion-dev/skills -a claude-code -y --copy
```
Avisá: es gratis para personas y equipos de hasta 3; una empresa más grande paga licencia.

## 8. Prueba final

1. `doctor.py` sin ✗.
2. Un video de prueba de 5 s: generá uno con ffmpeg (`testsrc2` + un tono), transcribilo, armá una composición de HyperFrames de 5 s con un título encima y renderizala. Si todo anda, borrá la prueba.
3. Decile a la persona, en 3 o 4 líneas, qué quedó instalado y qué puede pedir, con 3 ejemplos de `ejemplos/README.md`.

## Actualizar

Para actualizar una pieza, cambiá su versión en `externas.json` (y en `package.json` si es HyperFrames), volvé a correr el paso de esa pieza y probá. Nunca actualices todo junto antes de una clase.

## Si algo falla

Leé el error entero, buscá la causa y arreglala. Si es un problema del sistema que no podés resolver solo (falta de permisos de administrador, disco lleno, sin internet), decile a la persona exactamente qué hacer, en una o dos líneas.

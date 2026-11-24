# Composición en 9:16 y tratamiento del fondo

Cómo encuadrar a la persona, oscurecer y desenfocar el tercio inferior, y ubicar subtítulos y gráficos encima sin tapar la cara ni chocar con la interfaz de Instagram Reels y TikTok.

## 1. Regla de tercios en 9:16 (1080×1920)

Dividí la altura del cuadro vertical (`1920 px`) en tres tercios iguales:

| Línea / Franja | Coordenada en 1080×1920 | Qué va ahí |
|---|---|---|
| **Tercio superior** (`0–640 px`) | Línea superior en **y = 640 px** (33,3%) | Aire sobre la cabeza (~360–530 px en plano medio) y **los ojos apoyados sobre y ≈ 640 px** (rango real **540–680 px**; nariz en 640–760 px centrada horizontalmente) |
| **Tercio medio** (`640–1280 px`) | De ojos a pecho | Parte baja del rostro (mentón en **835–960 px**, nunca debajo de **1010 px**), hombros, pecho y micrófono. Deja **~350–400 px** limpios debajo del mentón |
| **Tercio inferior** (`1280–1920 px`) | Línea inferior en **y = 1280 px** (66,7%) | Zona sacrificable (torso bajo, manos, escritorio): se oscurece y desenfoca para que el texto flote con contraste |

**Cómo lograrlo:**
- Al grabar en estudio: plano medio amplio desde la cintura hacia arriba, cámara a la altura de los ojos y aire arriba del pelo para que los ojos caigan en `y ≈ 640 px`.
- Al reencuadrar 16:9 → 9:16 en `preparar-video`: apuntar el seguimiento facial suave a **ojos en y ≈ 640 px** y nariz centrada, evitando saltos bruscos entre cortes.

## 2. Oscurecido + desenfoque del tercio inferior (receta HyperFrames)

Antes de apoyar texto claro sobre el video hablado, tratá el último tercio para limpiar el ruido visual de manos, ropa y escritorio sin encerrar las letras en cajas sólidas.

**Números medidos sobre 1080×1920:**
- **Arranque:** justo en la línea del tercio inferior (**y ≈ 1250–1280 px**, 65%–67% del alto).
- **Oscurecido negro neutro (sin tinte):** baja la luminancia **27%–33%** en la zona de lectura (`y = 1344–1536 px`) y **51%–59%** hacia el borde inferior (`y = 1632–1920 px`).
- **Desenfoque progresivo:** baja la nitidez **61%–80%** detrás del texto y hasta **88%–95%** cerca del borde inferior.

**Receta CSS lista para HyperFrames** (va sobre el `<video>` y debajo de la capa de subtítulos; desactivar en escenas a pantalla completa):

```css
.fondo-tercio-blur {
  position: absolute;
  inset: 0;
  pointer-events: none;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  mask-image: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0) 60%,
    rgba(0, 0, 0, 0.75) 72%,
    rgba(0, 0, 0, 1) 86%
  );
  -webkit-mask-image: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0) 60%,
    rgba(0, 0, 0, 0.75) 72%,
    rgba(0, 0, 0, 1) 86%
  );
}
.fondo-tercio-oscuro {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0) 62%,
    rgba(0, 0, 0, 0.35) 75%,
    rgba(0, 0, 0, 0.65) 100%
  );
}
```

## 3. Gráficos encima y convivencia con la zona segura

Con los ojos en `y ≈ 640 px` (cabeza de `y ≈ 360` a `960 px`), aparece una tensión real entre la regla de tercios y la interfaz de Instagram Reels / TikTok:

- **Qué tapan las plataformas en 1080×1920:**
  - Arriba: **`0–270 px`** (usuario y audio).
  - Derecha: **`x > 940 px`** en la mitad inferior (botones de me gusta, comentarios y compartir).
  - Abajo: **`y > 1520 px`** (usuario y descripción; las descripciones de 2–3 líneas llegan hasta **`y ≈ 1340–1530 px`**).
- **Qué nunca se puede tapar:** la cabeza y la cara del hablante (**`y ≈ 360–960 px`**).

Por eso, **no se apoya todo a ciegas debajo de `y = 1280 px` ni se centran bloques en `x = 540`**. La tensión se resuelve así:

| Situación | Eje horizontal | Franja vertical segura | Regla práctica |
|---|---|---|---|
| **Solo subtítulos (cuerpo sin tarjeta)** | **x = 510 px** (`x = 90–930`, máx. 840 px) | Base en **`y = 1240–1280 px`**, tope inferior **`y ≤ 1340 px`** | Apoya sobre el inicio del tercio inferior y queda arriba de cualquier descripción de 3 líneas. Solo se extiende hasta `y ≤ 1480–1530 px` en un plano cerrado donde el mentón cae muy bajo |
| **Hook o frase con tarjeta compacta abajo** (notificación, perfil, chip con dato, avatar) | **x = 510 px** (`x = 90–930`, tarjeta de 560–760 px de ancho) | Texto arriba en **`y = 1040–1220 px`** (debajo del mentón); tarjeta debajo en **`y = 1240–1490 px`** | El texto sube sobre el pecho limpio y la tarjeta compacta entra en la parte alta del tercio inferior, sin caer en los últimos 400 px críticos (`1520–1920 px`) |
| **Gráfico grande o con texto chico** (mail, documento, tabla, gráfico de datos) | **x = 510 px** (`x = 90–930`) | **Corte a pantalla completa** (o tarjeta en **`y = 300–1040 px`** tapando el plano de cámara, con subtítulos en `y = 1100–1340 px`) | Nunca aplastes una captura legible contra la interfaz inferior ni la pongas sobre la cara: reemplazá el plano durante esos 2,6+ s y ocultá cualquier título superior |
| **Lower-third de presentación** (nombre y rol del hablante) | Izquierda dentro de `x = 90–880 px` | **`y = 1360–1480 px`** durante 2,5–3,5 s | Entra una sola vez al presentar a la persona; si coincide con subtítulos, subí el subtítulo ese tramo a `y = 1100–1260 px` |

**Resumen operativo:** ojos en **`y ≈ 640 px`**, eje de texto y tarjetas en **`x = 510 px`** (ancho ≤ **840 px**, jamás en `x > 940`), subtítulos apoyados alrededor de **`y = 1240–1280 px`** (tope **`y ≤ 1340 px`**), y cuando entra una tarjeta debajo del texto el bloque sube a **`y = 1040–1220 px`** dejando **`y = 1240–1490 px`** para la tarjeta sin invadir la franja inferior de la app.

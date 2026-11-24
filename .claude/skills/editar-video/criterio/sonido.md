# Sonido, voz, música y diseño sonoro

Reglas medidas para que la voz se entienda en cada frase, la música acompañe sin tapar ni cortarse antes del final, y los efectos de sonido se diseñen en forma ordenada antes de mezclar.

## 1. Principio central: medir por ventanas, no por promedio

Una mezcla aprobada en promedio igual falla si la música tapa las frases donde la persona baja la voz. Medí siempre la relación voz/música en **ventanas de 0,4 s donde haya habla**, calculando ambas pistas como downmix mono en float `(L + R) / √2` (promediar `(L + R) / 2` subestima la música en 3 dB y deja pasar camas demasiado altas).

## 2. Cadena de voz (`preparar-video`)

`preparar-video` entrega `base.mp4` con la voz limpia y nivelada a **−14 LUFS**. Criterios que sigue:

- **Medir antes de limpiar ruido:** calculá la brecha entre la voz y el piso de ruido (5% más bajo):
  - **≥ 40 dB** (ambiente silencioso): **sin denoise**. Dos pasadas agresivas sobre una toma limpia se comen consonantes finales suaves.
  - **15–40 dB** (normal): pasa-altos a **90 Hz**, reducción de ruido moderada (sin *hard gate* que corte respiraciones), realce suave de cuerpo (**+5 dB a 110 Hz**), presencia (**+2,5 dB a 3,2 kHz**), compresor suave (**2,5:1**, ataque 12 ms, release 180 ms).
  - **< 15 dB** (calle, zumbido fuerte): limpiar y avisar en el informe que la grabación original es ruidosa. Si se usa un modelo de separación agresivo que deja silencio digital entre frases, devolvé un poco de ambiente real limpio a **~−30 dB** bajo la voz para evitar cortes bruscos.
- **Nivelación por frases:** después de unir los cortes, emparejá el volumen frase por frase (**+8 / −4 dB**, suavizado ~1,3 s) solo sobre tramos con habla, manteniendo la ganancia quieta en las pausas para no inflar el ruido de sala.
- **Voz fina es tono, no volumen:** si suena metálica o hueca, corregir en bandas (cuerpo 80–160 Hz, brillo 4–8 kHz, tope ±8 dB) antes que subir volumen.

## 3. Cama musical, audición y *ducking* (`montar-video`)

No agregues música si la persona no la pidió ni te dio una pista (y nunca uses pistas sin derechos claros). Cuando hay música:

- **Audición antes del render final:** si hay varias pistas libres de derechos para elegir, generá con `ffmpeg` **3 a 5 previews de 10 s** mezclados sobre el arranque real del clip para que la persona elija de oído antes del render final. Evita re-renderizar todo por un error de clima musical.
- **Nivelar la música primero:** aplicá una envolvente lenta (~1 s hacia la mediana, ±10 dB) para que un tema que crece no tape el cierre. Ojo con intros casi mudas que engañan la mediana: empezá después de la intro o nivelá sobre el cuerpo real.
- **Niveles objetivo según formato:**

| Formato | Música bajo la voz | Ducking | Master final |
|---|---|---|---|
| Clip a cámara, instrumental | **−10 dB** mediana, **−6 dB** piso en el 15% más suave | **6 dB** (ataque 150 ms, release 400 ms) | **−14 LUFS**, **≤ −1,5 dBTP** |
| Clip a cámara, tema con voz cantada | **−13 dB** (preferir versión instrumental) | **6 dB** | **−14 LUFS**, **≤ −1,5 dBTP** |
| Exterior ruidoso | Sumar **2 dB extra** de separación | **6 dB** | **−14 LUFS**, **≤ −1,5 dBTP** |
| Documental narrado para celular | **−6 a −7 LU** | **2–3 dB** suave | **−10 LUFS**, **≤ −1 dBTP** |

- **Protección de frases suaves:** si en el 15% más bajo de las ventanas de voz la música queda a menos de **6 dB** por debajo, bajala puntualmente en esas frases hasta **12 dB** extra.
- **Sin música bajo animaciones de pantalla completa (si el estilo lo pide):** en edits editoriales con mucho diseño sonoro o placas explicativas full-screen, podés **cortar o mutear la música debajo de esas escenas** para que la voz y los SFX respiren limpios, y volver a entrar en el siguiente corte de A-roll o en un golpe de capítulo.
- **Elección y punto de arranque:** la música acompaña el **tono de entrega**, no solo el tema (confesión baja → pista lenta y cálida, más baja; discurso enérgico → pista brillante). Mapeá la pista cada 2 s para saber dónde sube y dónde entra la voz cantada; arrancá en una sección calma o media, o un pulso antes del estribillo reconocible, nunca en un clímax estridente.
- **Audio de clips insertados:** si metés un video con su propio audio (demo, captura con voz), bajá la música **~12 dB** debajo de ese clip y hacé fade rápido al salir.

## 4. Final de la música y trampa de `sidechaincompress`

- **Fade-in de 0,4 s** al inicio.
- **Nivel pleno hasta el final:** la música corre a su nivel hasta los últimos **0,3 s** (cayendo sobre la cola de **0,4 s** posterior a la última palabra, así nunca baja mientras la persona todavía habla).
- **Sin loops forzados:** si la pista se termina antes que el video, arrancala antes o cambiá de pista. Nunca repitas compases para rellenar el final.
- **Trampa conocida en ffmpeg:** `sidechaincompress` suele recortar entre **0,1 y 1,3 s** del final de su salida. Para evitar que la música muera antes de la imagen, agregá **3 s de relleno** al final de ambas entradas del filtro y recortá el resultado a la duración exacta del diálogo.
- **En un *beat drop*:** pedí el segundo exacto del drop si no es obvio; aterrizalo en el final de la última palabra o sobre la entrada del primer capítulo; bajo habla mantené −9 dB, congelá la ganancia los últimos **2,2 s** previos al drop para respetar la subida natural, y después del drop dejala a **−4 dB** de la voz con fade final de **0,6 s**. Cambios de canción siempre en corte seco al pulso.

## 5. Diseño sonoro (SFX) en 3 pasadas con *cue sheet*

Solo después de aprobar lo visual, armá los efectos de sonido. Usá siempre **grabaciones reales con licencia comercial libre** (CC0 primero; CC BY con crédito; nunca sintetizados baratos ni sonidos del sistema), recortadas al golpe útil (≤ 2 s para clicks/pops/whooshes) y normalizadas a **−3 dBFS** antes de nivelar.

**Paso obligatorio antes de mezclar — generar el `cue-sheet`:**
Escribí una tabla (`cue-sheet.json` o markdown) con `tiempo | evento en pantalla | familia | archivo | nivel dB`, armada en **3 pasadas ordenadas**:

| Pasada | Familia | Qué marca en pantalla | Nivel de referencia (bus SFX) |
|---|---|---|---|
| **1. Whooshes** | Movimiento y transiciones | Deslizamientos de tarjetas, zoom-outs, paneos, cortes rápidos | **−10 a −12 dB** estándar (**−9 dB** whoosh largo de ataque rápido; **−15 dB** viento suave largo) |
| **2. Texturas y UI** | Micro-acciones y detalles | Taps de teclado/texto, notificaciones, pops de ítems, obturadores | **−8 dB** obturador; **−9 a −10 dB** clicks/UI; **−6 a −7 dB** texturas/pops protagonistas |
| **3. Risers + Hits** | Clímax y cambios de bloque | Subidas de tensión antes de un giro + impacto al entrar un capítulo o *beat drop* | **−5 a −6 dB** en impactos clave (alinear siempre el pico del sonido al cuadro más rápido del movimiento) |

**Reglas de mezcla para que el bus de SFX no tape la voz:**
- Si los efectos caen sobre habla continua, mantenelos subordinados a la voz (picos efectivos **18–24 dB** debajo de los picos de voz o aplicando un recorte global al bus de SFX, p. ej. **−2 dB** en todo el bus cuando hay alta densidad de cues).
- Colapsá cues separados por menos de **90 ms** (prioridad: obturador/hit > pop > tick), variá muestras repetidas y adelantá el inicio si el pico del efecto está corrido dentro del archivo.
- Verificá que las uniones `riser + hit` no produzcan picos ni clipping.

## 6. Master y *clipping*

Mantené las pistas en **float 32-bit**, aplicá un solo ajuste de ganancia al objetivo (`loudnorm` lineal en dos pasadas) y cerrá con limitador (`alimiter`, `level=false`, tope **−1,5 dBTP** para clips / **−1 dBTP** para narrados). Nunca recortes muestras antes del limitador. Export final: **AAC 256 kb/s a 48 kHz**.

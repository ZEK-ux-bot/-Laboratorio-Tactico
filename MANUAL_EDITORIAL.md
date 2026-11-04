# LABORATORIO TÁCTICO — Manual de estilo y producción v2

**Fecha de análisis:** 4 de noviembre de 2026  
**Referencias del usuario:** `1000230926.mp4` y `1000230924.mp4`  
**Objetivo:** análisis periodístico-táctico de fútbol europeo, tono cercano mexicano, pausado, sin hablar como noticiero, en Shorts/Reels verticales de alta calidad **sin marca de agua**.

## 1. Qué muestran las dos referencias

| Aspecto | Referencia A — `1000230926.mp4` | Referencia B — `1000230924.mp4` |
|---|---|---|
| Duración observada | 78,55 s | 177,62 s |
| Lienzo y fps | 720 × 1280, vertical, 30 fps | 720 × 1280, vertical, 30 fps |
| Recurso conductor | Persona hablando en un recuadro inferior, sobre fotos del partido, capturas de alineaciones y tabla | Personaje ilustrado/mascota alternado con fotografías de jugadores, marcador, secuencias de juego, tablas y texto |
| Tratamiento del material | Deja tiempo para ver alineaciones y nombres; las fotos cambian en bloques | Montaje mucho más cambiante, acentos de tamaño/colores, cifras grandes y textos blancos en mayúsculas |
| Recursos informativos visibles | Alineaciones con puntuaciones, entrenadores, tabla, marcador y futbolistas | Marcadores, historia, comparación, capturas de resultados, tablas y acciones del encuentro |
| Texto en pantalla | Lo principal son capturas y datos del partido; pocos subtítulos grandes visibles | Palabras/frases cortas y mayúsculas blancas cerca de la zona baja, algunos textos de énfasis en color |
| Transiciones visuales | Nueve cambios de composición grandes detectados aproximadamente al muestrear a 1 s | Altísima actividad visual: muchas transiciones, zooms, movimiento y cortes; no todo cambio de píxeles equivale a un corte |
| Fortalezas para adoptar | Cercanía, credibilidad, explicación visual legible, estructura de datos | Narrativa con tensión, retención visual, tipografía expresiva y ritmo de contenido social |
| Qué NO copiar | Retrato del creador, capturas y edición exacta, marca | Mascota, chistes, gráficas, voces y recursos protegidos |

**Alcance de la revisión:** se inspeccionaron fotogramas distribuidos por todo el metraje, dimensiones, duración, fps y patrones de cambio visual. No contamos con una transcripción automática fiable de la narración de estos archivos; por eso, las expresiones orales exactas, muletillas individuales y prosodia acústica NO se atribuyen al creador. Este manual traduce la intención de tono que indicó el usuario y lo que objetivamente se observa en los videos; no afirma una transcripción inexistente.

## 2. Identidad original del canal

**Posicionamiento:** “Te cuento lo que pasó… y por qué tácticamente tiene sentido”, no “resumo resultados” ni “me burlo del perdedor”.

**Narrador:** Emiliano de HeyGen, masculino, en español; mantener identidad de voz, pero guion natural, sin múltiples exclamaciones ni rimas publicitarias. Velocidad de lectura normal o apenas calmada. Vocalización clara al decir nombres, fechas y números. Sintetizar la voz por separado si hay créditos y permiso; no utilizar el render final watermarked de Video Agent.

**Lenguaje mexicano moderado:** sí: “fíjate”, “mira”, “ojo”, “aquí está el detalle”, “es que”, “y eso importa porque”, “ahora bien”. Úsalos de forma orgánica (1–3 por Short), no como tic ni imitando frases exactas ajenas. No exceso de “brutal”, “humilló”, “destrozó”, “literalmente”, ni tono de regaño. Una broma suave cuando aporta claridad. Evitar proclamar verdades absolutas.

**Criterio profesional de análisis:** ¿qué objetivo táctico se buscaba?, ¿qué estructura hubo con y sin balón?, ¿qué ajuste explotó qué espacio?, ¿qué cambió en la toma de decisiones?, ¿cómo sabemos que causó la jugada y no fue simple correlación? Responder a UNA pregunta concreta por video. Definir los conceptos: “presión tras pérdida, es decir, intentar recuperar justo después de perder el balón”.

**Estructura sugerida del Short (60–75 s):**
- 0–3 s: gancho verificable, pregunta curiosa, marcador real o contraste;
- 3–10 s: contexto mínimo, equipos y qué se va a explicar;
- 10–40 s: mecanismo táctico en una secuencia y apoyo gráfico, con al menos una prueba;
- 40–60 s: matiz, contraejemplo, evolución o segundo mecanismo;
- 60–75 s: conclusión clara y una pregunta concreta a la audiencia.

**Visuales:** adoptar datos y capturas legibles del A, composición y subtítulos puntuales del B. Pizarra 2D de diseño propio, movimientos con transiciones suaves; al menos 4–6 segundos para entender cada evidencia. No marear con cortes constantes. 1080 × 1920, 30 fps, H.264, AAC, recorte vertical sin deformar el campo. Ubicar subtítulos en zona central-baja evitando los botones laterales de Shorts/TikTok. Resaltar palabras completas sin alterar negaciones ni frases.

## 3. Criterios de verificación

1. **Hechos:** marcador, fechas, alineaciones, goles, sustituciones, tarjetas → UEFA, club, liga, crónica/acta oficial.
2. **Datos:** posesión, xG, PPDA, campo de presiones, recuperaciones, mapas → fuente de proveedor identificada; no inventar xG de videos de highlights.
3. **Observaciones tácticas:** grabación completa autorizada, múltiples secuencias / datos de eventos, no solo dos highlights. ¿En qué minuto? ¿Con qué rival, fase, estructura y score? ¿Se repite?
4. **Interpretación:** etiquetar “una explicación posible”, “en esta secuencia”, “el entrenador dijo…”. No atribuir intención sin prueba.
5. **Pizarra:** si no hay tracking verificable o visión del partido, usar diagramas esquemáticos rotulados **“Ilustración táctica · posiciones no exactas”**. Nunca dibujar un movimiento inventado como reconstrucción real.
6. **Derechos:** fotos, capturas, partidos y música necesitan licencias pertinentes. Libre acceso ≠ libre reutilización. Usar gráficos originales por defecto.
7. **Fuentes citadas:** poner 2+ enlaces en documento/editorial y atribuciones relevantes en descripción o créditos.

## 4. Tecnologías: generación SIN marca de agua

**Opción principal, ya comprobable con el proyecto adjunto:**
- `Python + Pillow` para fichas, flechas, zonas y títulos.
- `mplsoccer` (licencia MIT) para cancha y visualizaciones de datos reales: https://github.com/andrewRowlinson/mplsoccer
- `FFmpeg` para renderizar el video MP4; marca de agua **no obligatoria**. Control total de resolución y calidad.
- `Kdenlive` (GPL) para editar manualmente, equilibrar voz, subtítulos, música y transiciones: https://kdenlive.org/
- Voz “Emiliano” de HeyGen **solo como pista de audio**. El plan gratis de HeyGen sí impone marca de agua en sus videos finales, por lo que no usar Video Agent como exportador de la pieza final; revisar disponibilidad de voz y condiciones de uso para publicación comercial.

**Alternativas de GitHub analizadas:**
- `MS-Teja/footballTacticsAnimator`: MIT, interfaz de pizarra, exportación MP4 en la app de macOS. https://github.com/MS-Teja/footballTacticsAnimator
- `Jackalackalack/5v5-football-tactics-board`: MIT, portátil sin instalar, WebM/GIF/PNG, pero es 5 vs 5 y no está diseñado como un motor 11 vs 11 de reportajes. https://github.com/Jackalackalack/5v5-football-tactics-board
- `evjester/tactical-board`: arrastrar jugadores y exportar GIF/PNG/JSON, útil para inspiración de UX; revisar licencia exacta antes de incorporar código. https://github.com/evjester/tactical-board
- `remotion-dev/remotion`: composición en React más compleja, pero su licencia NO es MIT ni open source OSI; particulares y empresas pequeñas pueden usar licencia Free según su contrato, otras organizaciones requieren licencia. https://github.com/remotion-dev/remotion

**No confundir:** quitar o tapar una marca de agua de un video ajeno no es lo mismo que generar de cero un MP4 sin que el motor añada una. La segunda alternativa es el plan aquí.

## 5. Datos e investigación: fuentes base

- Competición y cronología: https://www.uefa.com/ , https://www.laliga.com/ , ligas y clubes oficiales.
- Táctica profesional: https://www.fifatrainingcentre.com/ (ejemplos de presión, transiciones, estructura, ocupación de espacios).
- Datos libres en partidos disponibles: https://github.com/hudl/open-data (StatsBomb; exige reconocer la fuente y el logo en los análisis publicados).
- Observación e hipótesis de comunidad: YouTube, Reddit y contenido público indexado de TikTok / Instagram; **no tratarlos como pruebas primarias**.
- Estadística especializada comercial: no asumir acceso gratuito a tracking, mapas de presión o PPDA de cada partido.

## 6. Plantilla de guion — tono relajado

**Mal:** “¡DESTROZARON AL RIVAL POR UNA ESTRATEGIA QUE NADIE VIO! ¡TOTALMENTE RIDÍCULO!”

**Mejor:** “¿Vieron cómo el PSG hizo cuatro goles tan rápido? Mira, hay un detalle: dos de esas acciones te explican por qué el Villarreal no encontraba cómo acomodarse. Y ojo, no todo fue presión alta.”

**Esquema de entrega semanal:** concepto, fecha, fuente, hipótesis, evidencia, guion, desglose de cada escena, fuentes, video renderizado sin marca de agua y revisión del propietario. **No publicar automáticamente.**

## 7. Reglas de aprobación

- Solo utilizar hechos verificados y gráficos propios o material licenciado.
- Se entrega el archivo final **sin marcas de agua** a revisión.
- El usuario debe aprobar cualquier gasto recurrente de generación de voz o video y cada publicación.
- Si faltan datos para una recreación táctica, ofrecer hipótesis con rótulo de ilustración o elegir otra jugada.
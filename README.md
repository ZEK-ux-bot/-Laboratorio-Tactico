# Laboratorio Táctico — Producción automática de Shorts

Un proyecto reproducible para preparar Shorts/Reels de análisis de fútbol con narración generada por IA y **MP4 sin marca de agua**. Ningún fotograma del partido, foto protegida ni escudo es necesario. Las pizarras son **ilustraciones didácticas**, no reconstrucciones exactas.

## Qué está automatizado en el código

1. Investigación de actualidad con búsqueda web de OpenAI; entrega **5 ideas** y selecciona una.
2. Validación **mínima**: dos URLs y al menos una fuente oficial (si falla, **no se produce**).
3. Guion en español, mexicano tranquilo y explicativo.
4. Voz de Emiliano de HeyGen con su voice ID oficial del proyecto (solo si la cuenta/API lo permite; sin sustitución silenciosa).
5. Pizarra original con fichas y trayectorias **genéricas etiquetadas como ilustrativas**.
6. Video 1080×1920, 30 FPS con FFmpeg; subtítulos estimados, descripción y fuentes.
7. Guardado en GitHub Actions **Artifacts** para revisión. Se puede activar una subida a YouTube **privada** conectando credenciales; no publica públicamente.

**IMPORTANTE:** La comprobación de URLs y una fuente oficial no equivalen a verificar cada afirmación. El sistema NO dispone de tracking real de los jugadores. Antes de publicación pública sigue siendo necesaria una revisión editorial. La publicación en Instagram/TikTok tampoco está integrada. No prometemos producción ni subida hasta instalar el flujo y configurar API, autorización de gasto y cuentas.

## Ejecutar sin gastar ni tener API (prueba funcional)

Instalar Python 3.12+, FFmpeg y las librerías:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python src/automation.py --mode demo --size 360x640 --fps 15
```

Archivos de salida: `output/short_sin_marca.mp4`, `story.json`, `FUENTES_Y_REVISION.txt`, guion y descripción. Es una **demostración silenciosa** (con tema PSG-Villarreal) porque no tiene una nueva voz pagada ni archivos de audio locales.

Con una voz ya adquirida y descargada puedes probar narración + subtítulos sin generar costos nuevos:

```bash
python src/automation.py --mode demo --voice-file /ruta/a/emiliano.wav --size 1080x1920 --fps 30
```

**Nunca** uses un archivo de otra persona sin tener derecho a esa voz/grabación.

## Instalar la automatización en GitHub (una sola vez)

1. Proyecto instalado en el repositorio `ZEK-ux-bot/-Laboratorio-Tactico`, creado como **público**. Si quieres guardar cualquier información de producción privada, hazlo privado desde Settings → General → Danger Zone. Nunca subas claves, tokens ni videos con derechos al código.
2. En **Settings → Secrets and variables → Actions**, crea estos secrets: `OPENAI_API_KEY`, `HEYGEN_API_KEY`. Conecta la cuenta de pago/API que tenga derecho a voz Emiliano y los permisos necesarios. Nunca pegues claves en código ni en el chat.
3. En **Variables**, establece `GENERACION_PAGADA_AUTORIZADA=SI` solamente cuando hayas definido un presupuesto de uso de las APIs. Dejar esa variable vacía significa **no ejecutar ninguna tarea de pago**. Tu suscripción a ChatGPT no es crédito de OpenAI API.
4. Opcional para borradores automáticos privados de YouTube: secrets `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`, obtenidos por OAuth con permiso `youtube.upload`. Nunca configurar credenciales de publicación públicas por defecto.
5. Un **push de código** inicia una prueba DEMO sin coste, y **Actions → Laboratorio Táctico · Shorts automáticos → Run workflow** con `demo=true` permite repetirla. Descarga el resultado desde **Artifacts**. Las ejecuciones programadas no producen ni generan gastos mientras no se cumplan todos los requisitos de claves y autorización.

## Horario

- Lunes, miércoles y viernes, **9:15 a. m. America/Mexico_City**, en `.github/workflows/shorts.yml`. GitHub puede retrasar ejecuciones y requiere repositorio activo, además de habilitar Actions. Las tareas programadas corren sobre la rama predeterminada.
- Radar ChatGPT de cinco temas a las 8:00 a. m. diario (tarea separada, ya existente). El repositorio realiza su **propia búsqueda** para no depender de la memoria de una conversación.

## Arquitectura

```text
GitHub Actions (3x/semana)
    │
    ├── Buscar 5 ideas con web_search + OpenAI Responses API
    │            │
    │            └── Si faltan fuentes suficientes → detener
    │
    ├── Guion seleccionado (es-MX, relato relajado)
    ├── HeyGen text-to-speech → Emiliano, 1 solicitud
    ├── Calcular duración real del WAV con ffprobe
    ├── Diagramas didácticos etiquetados con disclaimer
    ├── Render Python/Pillow + FFmpeg 1080p sin watermark
    ├── SRT estimado (revisar sincronía) + MP4 final
    ├── Guardar video + investigación + fuentes como Artifacts
    └── (Opcional) Subir borrador privado a YouTube
```

## Seguridad, autenticidad y derechos

- No elimina marcas de agua de archivos ajenos; genera video original sin imponer una.
- Siempre distingue hechos oficiales de explicaciones tentativas; etiqueta la pizarra como ilustrativa.
- Las fuentes oficiales son un requisito necesario, pero no suficiente para asegurar que las inferencias causales sean ciertas. No publicar a ciegas.
- No incorpora fotos ni metraje televisivo protegido por derechos por defecto.
- La función de voz requiere autenticación y posiblemente saldo/pago. La voz Emiliano se ha probado en la app, pero todavía NO se ha validado la integración directa de API con esa voz. Si el proveedor rechaza la voz/endpoint/plan, se detiene sin reemplazarla o intentar muchas regeneraciones.
- Los subtítulos se sincronizan de forma **estimada** por cantidad de caracteres: no son marcas reales de tiempos de las palabras. Revisar una vez reproducidos.
- GitHub puede cobrar minutos/almacenamiento según el plan y el tipo de repositorio. La API de investigación y la voz se cobran por separado según sus tarifas. No hay tope monetario garantizado por este proyecto: antes de activar gastos, configura límites/alertas en los proveedores.
- La **publicación pública** requiere conectar y autorizar cada plataforma (YouTube/Instagram/TikTok) y revisar derechos y veracidad. Este proyecto la deja intencionadamente desactivada.

## Fuentes técnicas

- Documentación GitHub Actions: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- OpenAI Responses API web_search: https://developers.openai.com/api/docs/guides/tools-web-search
- HeyGen API TTS: https://www.heygen.com/blog/heygen-api-guide
- YouTube API upload OAuth: https://developers.google.com/youtube/data/guides/authentication

## Notas de producción

**Por qué no usamos clips generativos:** los movimientos exactos de un partido no pueden reproducirse fielmente solo con una descripción de texto. Una pizarra ilustrativa bien etiquetada enseña principios sin presentar ficción como observación.

**Próximas mejoras opcionales:** almacenar historial de temas para evitar duplicados, alinear subtítulos con timestamps reales si API los entrega, transiciones más finas, panel de revisión y publicación multicanal OAuth.

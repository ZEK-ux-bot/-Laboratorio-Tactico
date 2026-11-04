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


## Estado de compatibilidad de voz (noviembre de 2026)

La integración utiliza POST https://api.heygen.com/v3/voices/speech para generar una narración. Esta API requiere voces compatibles con starfish. La voz Emiliano seleccionada en la app figuraba como orca, por lo que su uso desde la API v3 no está confirmado. El programa detiene la ejecución si la voz es rechazada: NO cambia la voz por otra sin autorización.

## Pasos para activar una ejecución completa

1. Crear una clave de OpenAI API (https://platform.openai.com/api-keys) y una clave de HeyGen de tu cuenta.
2. En GitHub > Settings > Secrets and variables > Actions, guardar los secretos OPENAI_API_KEY y HEYGEN_API_KEY. Nunca subirlos al repositorio ni enviarlos por chat.
3. Configurar límites de gasto y alertas en ambos proveedores. Este proyecto por sí solo no impone un tope monetario verificable.
4. Solo después de aprobar el presupuesto, añadir la variable GENERACION_PAGADA_AUTORIZADA con valor SI. Sin ella el workflow omite llamadas de pago.
5. En Actions ejecutar manualmente el workflow con demo=true para revisar el funcionamiento sin claves ni gastos; demo=false habilita el modo completo únicamente si hay secretos y aprobación.
6. Opcionalmente, para subir borradores PRIVADOS de YouTube, añadir los secretos OAuth de YouTube y la variable SUBIR_BORRADOR_YOUTUBE=SI. Esta opción está desactivada por defecto, y no existe publicación pública automática.

El sistema exporta video original sin marca de agua, pero sus diagramas son ilustrativos; se requiere revisión editorial de hechos, animaciones y subtítulos antes de publicar. Instagram y TikTok aún no están integrados. La API se factura por separado de ChatGPT Plus.

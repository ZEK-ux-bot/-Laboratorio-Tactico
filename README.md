# Laboratorio Táctico — Shorts GRATIS, automáticos y sin marca de agua

**Actualizado el 4 de noviembre de 2026.** Este repositorio ya NO necesita ni utiliza **OpenAI API, HeyGen API ni facturación** para crear sus borradores programados. Sigue usando GitHub Actions, Python, noticias RSS públicas, **Qwen local mediante Ollama**, **Piper TTS** con voz mexicana y **FFmpeg**.

**Resultado:** un MP4 1080×1920 a 30 fps (animación original calculada a 720p/18 fps y escalada con FFmpeg), narración, subtítulos, cinco ideas, guion, enlace a noticia y fuentes en un ZIP de **Artifacts**. El archivo de video es original y **no contiene marca de agua**. El programa **NO publica** en YouTube, TikTok o Instagram.

**AVISO PERIODÍSTICO:** la investigación gratuita se limita a **titulares RSS** y URLs, no confirma todo lo que dicen los artículos. El video explica un **principio táctico general** relacionado con ese tema y **no afirma** que sus movimientos ocurrieron en un partido concreto. Si no hay RSS reciente disponible, produce una lección **ATEMPORAL** claramente identificada. Siempre revisar antes de publicar públicamente.

## Qué hace solo

1. Lunes, miércoles y viernes a las **09:15, hora de Ciudad de México**, GitHub ejecuta el workflow (puede retrasarse).
2. Busca hasta cinco titulares recientes de fútbol europeo mediante Google Noticias RSS. Ignora entradas viejas, rumores, lesiones y pronósticos. Si hay pocas noticias completa cinco propuestas con temas generales, sin fingir que son noticias.
3. Selecciona una nota reciente o un tema didáctico atemporal.
4. Redacta una explicación del **concepto táctico**, con **Qwen2.5 1.5B ejecutándose localmente**. No le proporciona al modelo nombres de equipos ni hechos del partido para reducir invenciones. Si Ollama no funciona, usa una explicación original fija.
5. Genera voz con **Piper es_MX-claude-high** (no es la voz Emiliano). Los archivos de la voz se descargan de Hugging Face durante la ejecución, sin cuenta ni API de pago.
6. Renderiza pizarras didácticas originales con Python y FFmpeg. Inserta subtítulos **estimados** (no alineados fonéticamente); el video final es 1080×1920, 30 fps.
7. Guarda un ZIP de borrador en **Actions → ejecución → Artifacts**, con una retención de **cinco días** para evitar acumulación de almacenamiento.
8. **No publica ni hace gastos de APIs**. No toma clips de televisión ni elimina marcas de terceros.

## Cómo probarlo ahora mismo en GitHub

1. Abre: https://github.com/ZEK-ux-bot/-Laboratorio-Tactico/actions/workflows/shorts.yml
2. Haz clic en **Run workflow**; rama `main`.
3. En **demo**, elige **false**. **ANTES false significaba producción con APIs de pago; AHORA false significa Short GRATIS completo**. Ni el workflow ni el programa de pago antiguo llaman a OpenAI/HeyGen.
4. Haz clic en **Run workflow**. Al terminar abre la ejecución, sección **Artifacts**, y descarga `laboratorio-tactico-N`. Contiene `short_sin_marca.mp4`, `voz_piper_mexico.wav`, `subtitulos.srt`, `narracion.txt`, `investigacion_5_ideas.json` y `FUENTES_Y_REVISION.txt`.
5. **demo=true** sigue produciendo un MP4 técnico breve sin narración para probar renderizado; es el modo de cada actualización de código.

Las ejecuciones programadas harán `demo=false` automáticamente. La prueba del primer video gratis con voz debe terminar **en verde** antes de afirmar que toda la producción está validada. No se garantiza entrega si fallan las descargas públicas, se alcanza un límite externo o falla un runner.

## Seguridad y facturación

- El repositorio actual es **público**. GitHub indica que los **runners estándar para repositorios públicos** son gratuitos, dentro de sus políticas y límites; las cuotas de almacenamiento de artifacts pueden tener costes al exceder el plan. **Mantén el repositorio público y no actives runners grandes de pago** si buscas cero costes. Revisa facturación en GitHub.
- Los secretos `OPENAI_API_KEY` y `HEYGEN_API_KEY` que configuraste **no se necesitan**. No se referencian en el workflow. Si prefieres, puedes **eliminarlos** desde **Settings → Secrets and variables → Actions**; eliminarlos no los revoca en el proveedor, eso debe hacerse también allí. La variable `GENERACION_PAGADA_AUTORIZADA` se ignora.
- `src/automation.py --mode full` (la versión previa de pago) ahora **se detiene siempre** para evitar cargos. Solo conserva el modo `demo` y algunas funciones técnicas que reutiliza `free_pipeline.py`.
- La instalación de Ollama descarga un instalador público de https://ollama.com e instala un modelo local; no usa un proveedor de inferencia alojado. Si no funciona, el programa sigue con plantillas de respaldo, sin pago.
- Piper se ejecuta **localmente**. Voz: https://huggingface.co/rhasspy/piper-voices/tree/main/es/es_MX/claude/high (dataset Apache-2.0; atribución en descripción).
- Qwen2.5:1.5B está disponible públicamente y se ejecuta en local. Solo propone una explicación general; **no se usa para comprobar resultados reales**.
- Usa una noticia RSS solo como **gancho** y fuente rastreable; nada de marcadores, fechas de partidos, estadísticas, tracking ni jugadas inventadas.

## Ejecutarlo manualmente en una computadora Linux

Necesitas Python 3.12, FFmpeg, conexión a internet y una fuente TrueType.

```bash
sudo apt-get install -y ffmpeg fonts-dejavu-core
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python src/free_pipeline.py --no-ollama --size 1080x1920 --fps 30
```

`--no-ollama` hace un Short gratuito con guion de respaldo y voz Piper; omitir esa opción habilita la IA local solo si `OLLAMA_URL` está configurada y el servidor local está activo. No uses `OPENAI_API_KEY` ni `HEYGEN_API_KEY`.

## Costes y calidad: limitaciones reales

- Gratis aquí significa **sin llamadas a APIs pagadas** y ejecución en un runner estándar del repo público. No prometemos que plataformas externas mantengan ilimitada y gratis su disponibilidad. RSS, modelos y voz necesitan descargas y conexión; pueden fallar.
- El tono de voz Claude de Piper es **diferente** a Emiliano. La calidad del modelo local, acento y pronunciación tienen que escucharse.
- El texto y subtítulos necesitan revisión humana. No hay edición automática de jugadas reales ni identificación de momentos de un encuentro.
- La **subida o publicación pública automática** no se ha conectado. Los MP4 son **borradores descargables**, no publicaciones ya hechas.

## Recursos oficiales

- GitHub Actions: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- Piper voces mexicanas: https://huggingface.co/rhasspy/piper-voices/tree/main/es/es_MX/claude/high
- Piper: https://pypi.org/project/piper-tts/
- Qwen2.5: https://ollama.com/library/qwen2.5
- FFmpeg: https://ffmpeg.org/

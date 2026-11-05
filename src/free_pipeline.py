#!/usr/bin/env python3
"""Produccion totalmente gratuita: RSS -> comentario tactico -> Piper -> pizarra -> MP4.

Nunca llama OpenAI ni HeyGen, no usa sus secretos y NO publica videos.
Noticias: solo se cita el titular verificable; la pizarra es un ejemplo general,
NO una reconstruccion del partido. Si no hay noticias nuevas usa temas atemporales.
"""
from __future__ import annotations

import argparse
import datetime as dt
import email.utils
import html
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlencode, urlparse

import requests
import feedparser

import automation as base

ROOT = Path(__file__).resolve().parents[1]
VOICE_NAME = "es_MX-claude-high"
VOICE_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_MX/claude/high/"
FEED_QUERIES = [
    'futbol "Champions League" when:4d',
    'futbol ("LaLiga" OR "Premier League" OR "Serie A") when:4d',
    'futbol ("Bundesliga" OR "Ligue 1" OR "Champions") when:4d',
]
THEMES = [
    ("presion", "Presion alta: una decision colectiva", "Presionar juntos cambia el partido"),
    ("transicion", "Transiciones: los segundos mas valiosos", "Recuperar y atacar a tiempo"),
    ("tercer_hombre", "El tercer hombre abre la defensa", "Crear una linea de pase nueva"),
    ("balon_parado", "Balon parado: un duelo de detalles", "La segunda jugada importa"),
    ("bloque", "El bloque bajo no se rompe a lo loco", "Mover al rival antes de acelerar"),
]
EXPLAIN = {
    "presion": "Fíjate en esto: presionar arriba no es que todos corran como locos detrás de la pelota. La clave está en cerrar las líneas de pase y elegir el momento de saltar. Cuando uno sale y los demás se quedan, aparece un hueco. Por eso el delantero orienta la salida, los mediocampistas tapan el pase interior y la defensa acompaña. Si todos se mueven juntos, el rival tiene menos opciones. Y si la presión se rompe, toca replegarse rápido.",
    "transicion": "Aquí está el detalle: al recuperar la pelota, el espacio suele durar muy poco. Lo primero no siempre es correr; es levantar la cabeza y decidir si hay un pase hacia delante. Si existe superioridad, el equipo puede acelerar con apoyos y amplitud. Si no, conviene asegurar la posesión. En defensa pasa lo contrario: tras una pérdida, la prioridad es proteger el centro y frenar la primera carrera. Esa decisión de unos cuantos segundos cambia el riesgo de toda la jugada.",
    "tercer_hombre": "Mira la idea: a veces el jugador que quieres encontrar no tiene una línea de pase directa. Ahí aparece el tercer hombre. Uno recibe de espaldas, descarga de primera y un compañero llega de cara, con campo por delante. No es magia ni una jugada complicada por sí sola; es cuestión de orientar bien el cuerpo y coordinar el tiempo del pase. Si el rival salta al primer receptor, puede dejar un espacio libre a su espalda.",
    "balon_parado": "Una jugada a balón parado no termina necesariamente con el primer remate. De hecho, la segunda pelota puede ser la más peligrosa. Mientras unos atacan el área, otros esperan por fuera para recoger un despeje. El equipo que defiende tiene que cuidar las marcas, pero también quién sale a disputar el rebote. Por eso importan tanto la colocación, el tiempo de carrera y la concentración después del primer contacto. Ahí se gana o se pierde una opción de gol.",
    "bloque": "Contra un bloque bajo, tener la pelota no alcanza. Si todos se quedan por fuera, el rival puede defender cómodo. La idea es moverlo de un lado a otro, fijar a los defensas y crear una superioridad en el momento indicado. A veces sirve un cambio de orientación; otras, una pared o la llegada de un mediocampista desde atrás. Lo importante es no confundir paciencia con lentitud: hay que circular y, cuando aparece el hueco, acelerar.",
}

def clean(value: str, limit: int = 160) -> str:
    text = html.unescape(re.sub(r"<[^>]*>", " ", str(value or "")))
    text = re.sub(r"\s+", " ", text).strip().strip("-–: ")
    return text[:limit].rstrip(" ,.;:") if len(text) > limit else text

def get_theme(title: str) -> str:
    low = title.lower()
    hints = {
        "presion": ["presión", "presion", "presionar", "recupera", "recuperación"],
        "transicion": ["contraataque", "transición", "transicion", "velocidad", "desmarque"],
        "balon_parado": ["córner", "corner", "falta", "balón parado", "remate"],
        "tercer_hombre": ["mediocampo", "pase", "centrocampista", "mediocentro", "asistencia"],
        "bloque": ["defensa", "bloque", "portería", "defender", "solidez"],
    }
    for topic, terms in hints.items():
        if any(term in low for term in terms):
            return topic
    return THEMES[dt.date.today().toordinal() % len(THEMES)][0]

def make_feed_url(query: str) -> str:
    params = urlencode({"q": query, "hl": "es-419", "gl": "MX", "ceid": "MX:es-419"})
    return "https://news.google.com/rss/search?" + params

def trusted_link(url: str) -> bool:
    try:
        p = urlparse(url)
        return p.scheme == "https" and (p.hostname in {"news.google.com", "www.google.com"} or
               p.hostname in {"uefa.com", "www.uefa.com", "laliga.com", "www.laliga.com",
                              "marca.com", "www.marca.com", "as.com", "www.as.com",
                              "espn.com.mx", "www.espn.com.mx", "bundesliga.com",
                              "www.bundesliga.com", "premierleague.com",
                              "www.premierleague.com"})
    except (TypeError, ValueError):
        return False

def parse_news(xml_text: str, now: dt.datetime) -> list[dict]:
    parsed = feedparser.parse(xml_text)
    if not parsed.entries:
        return []
    found = []
    seen = set()
    for entry in parsed.entries:
        url = str(entry.get("link", ""))
        title = clean(entry.get("title", ""), 135)
        if not url or not trusted_link(url) or len(title) < 18:
            continue
        # No hacer Shorts a partir de rumores, fichajes, quinielas ni lesiones.
        low = title.casefold()
        if any(x in low for x in ("rumor", "fichaj", "apuesta", "pronóstic", "lesión", "lesion", "mercado")):
            continue
        if not any(x in low for x in (" de ", " del ", " la ", " el ", " en ", " ante ", " con ", " para ", " tras ")):
            continue
        if title.casefold() in seen:
            continue
        seen.add(title.casefold())
        date_string = entry.get("published") or entry.get("updated") or ""
        try:
            published = email.utils.parsedate_to_datetime(date_string)
            if published.tzinfo is None:
                published = published.replace(tzinfo=dt.timezone.utc)
        except (ValueError, TypeError, IndexError):
            continue
        age = (now - published).total_seconds()
        if age < -3600 or age > 5 * 86400:
            continue
        source = entry.get("source") or {}
        publisher = clean(source.get("title", ""), 45) or "Google Noticias"
        topic = get_theme(title)
        score = sum(token in low for token in (
            "champions", "laliga", "premier league", "madrid", "barcelona", "psg",
            "bayern", "inter", "arsenal", "liverpool", "manchester", "atlético"))
        score += 2 if any(x in low for x in (
            "presión", "táctic", "defensa", "gol", "victoria", "remontada", "partido")) else 0
        found.append({"title": title, "url": url, "publisher": publisher,
                      "date": published.date().isoformat(), "score": score,
                      "topic": topic, "timestamp": published.timestamp()})
    return found

def collect_news(now: dt.datetime | None = None) -> list[dict]:
    now = now or dt.datetime.now(dt.timezone.utc)
    results = []
    seen = set()
    session = requests.Session()
    session.headers.update({"User-Agent": "LaboratorioTactico/1.0 (+editorial educational bot)"})
    for query in FEED_QUERIES:
        try:
            resp = session.get(make_feed_url(query), timeout=17)
            resp.raise_for_status()
            for item in parse_news(resp.text, now):
                if item["title"].casefold() not in seen:
                    seen.add(item["title"].casefold())
                    results.append(item)
        except requests.RequestException as exc:
            print("Aviso: feed no disponible; se usaran otras fuentes o un tema didactico:", str(exc), file=sys.stderr)
    return sorted(results, key=lambda n: (n["score"], n["timestamp"]), reverse=True)

def choose_topic(news: list[dict], today: dt.date) -> tuple[list[dict], dict]:
    if news:
        real = news[:5]
        shortlisted = list(real)
        # Siempre guardar 5 candidatos aun cuando el RSS traiga solo 1-4.
        for topic, title, _ in THEMES:
            if len(shortlisted) >= 5:
                break
            shortlisted.append({"title": title, "topic": topic,
                                "publisher": "Leccion didactica original", "url": "",
                                "date": today.isoformat(), "kind": "atemporal"})
        pick = real[today.toordinal() % len(real)]
        return shortlisted, {**pick, "kind": "titular_de_actualidad"}
    fallback = [
        {"title": title, "topic": topic, "publisher": "Leccion didactica original",
         "url": "", "date": today.isoformat(), "kind": "atemporal"}
        for topic, title, _ in THEMES
    ]
    return fallback, fallback[today.toordinal() % len(fallback)]

def local_explanation(topic: str, ollama_url: str = "") -> tuple[str, str]:
    """El modelo SOLO explica un principio general: no recibe noticias ni partidos."""
    baseline = EXPLAIN[topic]
    if not ollama_url:
        return baseline, "plantilla_verificada"
    prompt = (
        "Eres un comentarista mexicano de fútbol, calmado, preciso y natural. "
        "Explica EXCLUSIVAMENTE el concepto táctico general '" + topic.replace("_", " ") + "'. "
        "No cites partidos, clubes, futbolistas, resultados, periodistas, estadísticas ni fechas. "
        "No inventes jugadas reales. Redacta en español de México entre 85 y 110 palabras, "
        "en tono conversacional, con un ejemplo hipotético explícito. "
        'Devuelve SOLO JSON: {"explicacion": "texto sin comillas interiores"}.'
    )
    try:
        response = requests.post(ollama_url.rstrip("/") + "/api/generate", json={
            "model": os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b"),
            "prompt": prompt, "stream": False, "format": "json",
            "options": {"temperature": 0.15, "num_predict": 230, "num_ctx": 1024}
        }, timeout=150)
        response.raise_for_status()
        body = json.loads(response.json().get("response", "{}"))
        candidate = clean(body.get("explicacion", ""), 1100)
        words = candidate.split()
        if 75 <= len(words) <= 125 and not any(x in candidate.lower() for x in
                ("real madrid", "barcelona", "psg", "manchester", "resultado", "según datos", "partido de ayer")):
            return candidate, "qwen_local_sin_api"
    except (requests.RequestException, ValueError, TypeError) as exc:
        print("Aviso: modelo local no disponible:", str(exc), file=sys.stderr)
    return baseline, "plantilla_verificada"

def make_script(item: dict, explanation: str) -> str:
    if item["kind"] == "atemporal":
        lead = ("Hoy en Laboratorio Táctico vamos con una idea sencilla que cambia cómo vemos "
                "el fútbol: " + item["title"].lower().rstrip(".") + ". ")
    else:
        title = item["title"].split(" - ")[0][:115].rstrip(" .")
        lead = ("En la agenda del fútbol aparece este titular: " + title +
                ". Y ojo, para entenderlo sin inventar jugadas, hablemos de una idea táctica relacionada. ")
    closing = (" Ojo: las flechas de esta pizarra son un ejemplo, no posiciones reales de un "
               "partido. La próxima vez que veas fútbol, fíjate en este detalle. "
               "¿Tú qué otra jugada quieres que expliquemos?")
    return lead + explanation + closing

def make_free_brief(shortlisted: list[dict], selected: dict, explanation: str, method: str) -> dict:
    script = make_script(selected, explanation)
    topic = selected["topic"]
    label = "NOTICIA · ENLACE EN FUENTES" if selected["kind"] != "atemporal" else "LECCIÓN ATEMPORAL"
    captions = [
        ("LA IDEA DE HOY", "UNA NOTICIA O UN CONCEPTO", "SIN INVENTAR JUGADAS", "INTRO", "intro"),
        ("MIRA LA PIZARRA", "MOVIMIENTOS ILUSTRATIVOS", "NO ES TRACKING REAL", label, topic),
        ("EL PRIMER DETALLE", "EL ESPACIO IMPORTA", "COORDINAR ANTES DE CORRER", "PRINCIPIO 01", topic),
        ("¿QUÉ CAMBIA?", "DECISIÓN Y TIEMPO", "UN ERROR ABRE ESPACIOS", "PRINCIPIO 02", "transicion"),
        ("NO TODO ES CORRER", "LA ESTRUCTURA SOSTIENE", "MOVERSE COMO EQUIPO", "PRINCIPIO 03", "bloque"),
        ("OJO CON ESTO", "UN EJEMPLO, NO UNA REPLAY", "NO RECREAMOS EL PARTIDO", "MATIZ IMPORTANTE", "comparacion"),
        ("TÚ QUÉ OPINAS", "MIRA EL DETALLE EN EL JUEGO", "FÚTBOL SIN HUMO", "CONCLUSIÓN", "cierre"),
    ]
    scenes = [dict(headline=h, caption=c, insight=i, label=l, concept=t) for h,c,i,l,t in captions]
    title = selected["title"]
    sources = [selected["url"]] if selected.get("url") else []
    data = {
        "free_mode": True,
        "method": method,
        "candidates": [
            {"title": n["title"], "competition": "Fútbol europeo",
             "reason": "Titular público reciente" if n.get("url") else "Clase atemporal",
             "source_urls": [n["url"]] if n.get("url") else []}
            for n in shortlisted],
        "selected": {
            "title": title, "match": "No verificado / no aplicable",
            "date": selected["date"], "score": "No verificado / no aplicable",
            "voice_script": script, "sources": sources,
            "verification_notes": (
                "El único hecho noticioso usado es el titular RSS con su URL. "
                "La explicación es TEÓRICA; ninguna afirmación sobre presión, "
                "jugadas o posiciones del encuentro se ha comprobado con vídeo. "
                "Debe revisarse el titular y la fecha antes de publicar."),
            "positions_are_verified": False, "scenes": scenes,
            "publisher": selected["publisher"], "kind": selected["kind"],
            "topic": topic,
        }
    }
    assert len(data["candidates"]) == 5
    return data

def voice_files(directory: Path) -> tuple[Path, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    model = directory / (VOICE_NAME + ".onnx")
    config = directory / (VOICE_NAME + ".onnx.json")
    for target in (model, config):
        if target.exists() and target.stat().st_size > (1000000 if target == model else 100):
            continue
        response = requests.get(VOICE_URL + target.name, timeout=150, stream=True)
        response.raise_for_status()
        with target.open("wb") as f:
            for chunk in response.iter_content(chunk_size=1048576):
                if chunk:
                    f.write(chunk)
        if target.stat().st_size <= (1000000 if target == model else 100):
            raise RuntimeError("Descarga incompleta de voz Piper: " + target.name)
    return model, config

def piper_voice(text: str, output: Path, models_dir: Path) -> float:
    model, _config = voice_files(models_dir)
    # Esta voz es 'claude' de Piper, NO Emiliano. Licencia del dataset Apache-2.0.
    subprocess.run([sys.executable, "-m", "piper", "--model", str(model),
                    "--output_file", str(output), "--", text], check=True, timeout=210)
    return base.audio_length(output)

def build(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Shorts de tactica GRATIS, sin APIs pagadas")
    p.add_argument("--size", default="1080x1920")
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--output-dir", type=Path, default=ROOT / "output")
    p.add_argument("--no-ollama", action="store_true")
    p.add_argument("--skip-subtitles", action="store_true")
    args = p.parse_args(argv)
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)
    news = collect_news(now)
    five, picked = choose_topic(news, now.date())
    explanation, method = local_explanation(
        picked["topic"], "" if args.no_ollama else os.getenv("OLLAMA_URL", ""))
    data = make_free_brief(five, picked, explanation, method)
    (out / "investigacion_5_ideas.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf8")
    narration = data["selected"]["voice_script"]
    (out / "narracion.txt").write_text(narration, encoding="utf8")
    voice = out / "voz_piper_mexico.wav"
    duration = piper_voice(narration, voice, ROOT / ".cache" / "piper")
    story = base.plan_story(data, duration)
    (out / "story.json").write_text(json.dumps(story, ensure_ascii=False, indent=2), encoding="utf8")
    sources = data["selected"]["sources"]
    (out / "FUENTES_Y_REVISION.txt").write_text(
        "ESTADO: BORRADOR, NO PUBLICAR SIN REVISIÓN\n"
        "TÍTULO: " + picked["title"] + "\n"
        "ORIGEN: " + picked["publisher"] + "\n"
        "FECHA: " + picked["date"] + "\n"
        "TIPO: " + picked["kind"] + "\n"
        "MÉTODO GUION: " + method + "\n\n"
        "ENLACES:\n" + ("\n".join(sources) or "(Tema atemporal: sin noticia)") + "\n\n"
        "NO SE HAN CONFIRMADO LAS ACCIONES TÁCTICAS DEL PARTIDO. "
        "Diagramas originales genéricos. Revisar titular, narración, "
        "atribución de voz y subtítulos antes de publicar.\n",
        encoding="utf8",
    )
    video = out / "short_sin_marca.mp4"
    # Renderizar a 720p/18 fps para no agotar el tiempo del runner gratuito.
    # Escalar el MP4 FINAL a 1080x1920 / 30 fps, sin marcas de agua.
    intermediate = out / "intermedio_animado.mp4"
    base.run_render(out / "story.json", intermediate, voice, "720x1280", 18)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(intermediate),
        "-vf", "scale=" + args.size.replace("x", ":") + ":flags=lanczos,fps=" + str(args.fps),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
        "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart",
        str(video)], check=True, timeout=900)
    intermediate.unlink(missing_ok=True)
    subs = out / "subtitulos.srt"
    base.make_subtitles(narration, duration, subs)
    if not args.skip_subtitles:
        base.mux_subs(video, subs)
    (out / "descripcion_youtube.txt").write_text(
        picked["title"] + "\n\n"
        "Explicación táctica general, no reconstrucción de un partido. "
        "Diagramas originales ilustrativos.\n"
        "Fuentes:\n" + ("\n".join(sources) or "Clase atemporal") + "\n"
        "Voz sintética: Piper es_MX-claude-high; dataset Apache-2.0.\n"
        "#Futbol #Tactica #Shorts\n", encoding="utf8")
    print("Short gratuito creado:", video, "narración", round(duration, 1),
          "segundos; noticias recientes:", len(news), "modelo:", method)
    return 0

if __name__ == "__main__":
    sys.exit(build())

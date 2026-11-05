import datetime as dt
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import free_pipeline as f


class TestPipelineGratis(unittest.TestCase):
    def test_links_seguros(self):
        self.assertTrue(f.trusted_link("https://news.google.com/rss/articles/uno"))
        self.assertTrue(f.trusted_link("https://www.uefa.com/uefachampionsleague"))
        self.assertFalse(f.trusted_link("https://news.google.com.evil.com/"))
        self.assertFalse(f.trusted_link("http://news.google.com/"))

    def test_feed_con_titular_reciente(self):
        now = dt.datetime(2026, 11, 4, 12, tzinfo=dt.timezone.utc)
        xml = """<?xml version="1.0"?><rss version="2.0"><channel>
        <title>Noticias</title><item>
        <title>La defensa del equipo cambia tras el partido europeo</title>
        <link>https://news.google.com/rss/articles/abcdefg</link>
        <pubDate>Wed, 04 Nov 2026 10:00:00 GMT</pubDate>
        <source url="https://www.uefa.com/">UEFA</source>
        </item></channel></rss>"""
        items = f.parse_news(xml, now)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["publisher"], "UEFA")
        self.assertEqual(items[0]["topic"], "bloque")

    def test_rechazar_noticia_antigua(self):
        now = dt.datetime(2026, 11, 4, tzinfo=dt.timezone.utc)
        xml = """<rss><channel><item>
        <title>La defensa en la final del campeonato europeo</title>
        <link>https://news.google.com/rss/articles/noticia</link>
        <pubDate>Tue, 14 Oct 2025 12:00:00 GMT</pubDate>
        </item></channel></rss>"""
        self.assertEqual(f.parse_news(xml, now), [])

    def test_cinco_candidatos_con_una_noticia(self):
        today = dt.date(2026, 11, 4)
        one = {"title": "La defensa en la Champions League esta semana",
               "topic": "bloque", "date": str(today), "url": "https://news.google.com/rss/articles/a",
               "publisher": "UEFA"}
        five, picked = f.choose_topic([one], today)
        self.assertEqual(len(five), 5)
        self.assertEqual(picked["kind"], "titular_de_actualidad")
        self.assertEqual(picked["title"], one["title"])

    def test_sin_noticias_clase_atemporal(self):
        five, picked = f.choose_topic([], dt.date(2026, 11, 4))
        self.assertEqual(len(five), 5)
        self.assertEqual(picked["kind"], "atemporal")
        self.assertFalse(picked["url"])

    def test_guion_y_pizarra_no_afirman_tracking(self):
        five, picked = f.choose_topic([], dt.date(2026, 11, 4))
        expl, method = f.local_explanation(picked["topic"])
        data = f.make_free_brief(five, picked, expl, method)
        self.assertEqual(len(data["candidates"]), 5)
        self.assertFalse(data["selected"]["positions_are_verified"])
        self.assertTrue(data["free_mode"])
        self.assertIn("flechas de esta pizarra", data["selected"]["voice_script"])
        story = f.base.plan_story(data, 55.0)
        self.assertFalse(story["verified_match"])

    def test_local_model_caido_usa_guion_original(self):
        with patch.object(f.requests, "post", side_effect=f.requests.RequestException("sin servicio")):
            result, method = f.local_explanation("presion", "http://127.0.0.1:11434")
        self.assertEqual(method, "plantilla_verificada")
        self.assertEqual(result, f.EXPLAIN["presion"])


if __name__ == "__main__":
    unittest.main()

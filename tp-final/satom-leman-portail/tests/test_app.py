import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))
import app  # noqa: E402


class TestRoutes(unittest.TestCase):
    def test_accueil(self):
        code, type_contenu, corps = app.route("/")
        self.assertEqual(code, 200)
        self.assertIn("text/plain", type_contenu)
        self.assertIn(app.NOM, corps)

    def test_sante_web(self):
        self.assertEqual(app.route("/health"), (200, "text/plain; charset=utf-8", "ok\n"))

    def test_sante_api(self):
        code, type_contenu, corps = app.route("/api/health")
        self.assertEqual(code, 200)
        self.assertEqual(type_contenu, "application/json")
        self.assertEqual(json.loads(corps)["statut"], "ok")

    def test_parametres_ignores(self):
        self.assertEqual(app.route("/health?essai=2")[0], 200)

    def test_chemin_inconnu(self):
        self.assertEqual(app.route("/nimporte")[0], 404)

    def test_journal_json(self):
        ligne = json.loads(app.journal("GET", "/health", 200))
        self.assertEqual(ligne, {"methode": "GET", "chemin": "/health", "code": 200})


if __name__ == "__main__":
    unittest.main()

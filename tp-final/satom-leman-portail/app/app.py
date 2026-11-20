"""Petite application du portail Léman Finance : un site statique minimal et une API de santé.

Routes :
  /              page d'accueil (texte)
  /health        état du serveur web (utilisé par le groupe cible web)
  /api/health    état de l'API (utilisé par le groupe cible app)
Les journaux sont écrits en JSON, une ligne par requête (pour CloudWatch Logs).
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

NOM = "portail-leman-TP-AC"


def route(path):
    """Retourne (code, type_de_contenu, corps) pour un chemin donné."""
    chemin = path.split("?", 1)[0]
    if chemin == "/":
        return 200, "text/plain; charset=utf-8", f"{NOM}\n"
    if chemin == "/health":
        return 200, "text/plain; charset=utf-8", "ok\n"
    if chemin == "/api/health":
        return 200, "application/json", json.dumps({"service": NOM, "statut": "ok"}) + "\n"
    return 404, "text/plain; charset=utf-8", "introuvable\n"


def journal(methode, path, code):
    """Ligne de journal structurée (JSON)."""
    return json.dumps({"methode": methode, "chemin": path, "code": code}, ensure_ascii=False)


class Gestionnaire(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802 (nom imposé par http.server)
        code, type_contenu, corps = route(self.path)
        donnees = corps.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", type_contenu)
        self.send_header("Content-Length", str(len(donnees)))
        self.end_headers()
        self.wfile.write(donnees)
        print(journal("GET", self.path, code), file=sys.stdout, flush=True)

    def log_message(self, *args):  # on journalise nous-mêmes, en JSON
        pass


def main(port=8080):  # pragma: no cover
    HTTPServer(("0.0.0.0", port), Gestionnaire).serve_forever()


if __name__ == "__main__":  # pragma: no cover
    main()

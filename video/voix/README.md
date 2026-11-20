# Voix off du montage v3

- `texte.txt` : texte validé (Thomas = T, Abderahmane = A), avec ancres sur les gestes à l'écran. `TEXTE-VOIX.md` : version lisible.
- `check.py` : place chaque phrase sur la chronologie (durées estimées, ou mesurées via `durees_reelles.json`), écrit `lignes.json`.
- `lexique.py` : prononciation des sigles et des noms anglais (sigles épelés, « Claoud-Front »…).
- `RECHERCHE-CLONAGE.md` : recherche et décisions (Qwen3-TTS 1.7B Base pour les deux voix, essais VoxCPM2 et Voxtral écartés).
- `outils/` : génération par lots (3 prises par phrase), sélection automatique (ressemblance ECAPA + retranscription Whisper), étalonnage fidèle à la vraie voix (correction de timbre ±3 dB, limiteur de crête, -16 LUFS), assemblage de la piste, aperçu. Les enregistrements des voix et la vidéo ne sont pas versionnés.

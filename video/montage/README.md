# Montage v3 (sans voix) — chaîne de fabrication

Objectif : refaire le montage complet à partir des rushs enregistrés à la main dans la console AWS
(`video/raw/*.mp4` + `*.marks.json`), propre, rythmé, sans tremblement, **sans aucun son** (les voix viendront après).

| Étape | Commande | Rôle |
|---|---|---|
| 1. analyse | `python analyse.py` / `python runall.py` | par rush, à 10 Hz : activité de l'écran, clics (anneaux bleus du curseur), luminosité, « encre » (pages vides = chargement). Sortie `analyse/*.json` |
| 2. plan | `python plan.py` | coupes (chargements, temps morts), vitesses (frappe ×3 à ×8, attentes accélérées avec pastille), budget de durée par scène, trajectoire de caméra. Sortie `plan/*.json` |
| 3. retiming | `python conform.py` | ffmpeg `select` (une seule passe, CFR 30 i/s, x264 CRF 15, GOP 15) + masquage du bandeau compte. Sortie `work/conf/*.mp4` |
| 4. caméra terminaux | `python camfix.py` | cadre automatiquement le texte des terminaux (images sombres) |
| 5. masquage OCR | `ocrmask.py` (python du venv de la voix, rapidocr) | retrouve à l'écran l'identifiant de compte, l'identité de session et l'organisation, et pose un masque |
| 6. scénario | `python export.py` | assemble cartes, schémas, scènes et légendes dans `rm/src/data.json` |
| 7. rendu | `node render.mjs full out/final.mp4` | Remotion (React) : zoom caméra lissé, bandeau de module, légendes, cartes de chapitre, transitions |

Remotion lit les médias par HTTP : `python -m http.server 8765 --bind 127.0.0.1` lancé à la racine du dépôt (`C:\Perso\AWS`).

Réglages utiles : `plan.py` (`P`, `BUDGET`, `REPEAT`), `captions.py` (légendes de chaque scène), `rm/src/*.tsx` (habillage).
Les secrets (identifiants à masquer) restent dans `video/rig/profile/masks.json`, ignoré par git.

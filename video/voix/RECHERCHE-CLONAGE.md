# Clonage des voix et étalonnage : recherche et plan

État au 20/11/2026. Texte validé (3 700 mots, 50/50). Aucune voix finale générée. Ce document dit ce que j'ai trouvé, ce que je propose de tester, et ce dont j'ai besoin de vous.

## 1. En bref

1. **La fidélité dépend d'abord de la matière première**, pas du logiciel : des enregistrements propres, une référence bien choisie, une transcription exacte. Aujourd'hui nous n'avons que **133 s de Thomas et 100 s d'Abderahmane** (enregistrement-2.wav et abder_48k.wav), bruit de fond très bas. C'est correct pour un clonage « à partir d'un extrait », insuffisant pour un clonage « affiné » (10 à 30 minutes).
2. **Trois voies réalistes**, à départager par un essai chiffré puis à l'oreille : Qwen3-TTS (déjà installé), **VoxCPM2** (local, français, affinage possible), **Voxtral TTS 3 de Mistral** (API, clonage dès 3 à 25 s, « Pro Voice » dès ~30 min).
3. **Un second passage « conversion de voix »** (Seed-VC) peut rapprocher le timbre de la vraie voix si le TTS seul reste « à côté ». À ne garder que si les mesures et vos oreilles le confirment.
4. **L'étalonnage reste sobre** : filtre grave léger, correction de timbre limitée à ±3 dB mesurée sur vos vraies voix, compression douce, niveau commun à −16 LUFS. Rien qui change l'identité de la voix.
5. **Je ne peux pas écouter.** Je mesure (ressemblance de locuteur, intelligibilité, niveau, spectre) et je vous soumets des échantillons à l'aveugle. Le jugement final est le vôtre.

## 2. Ce que la recherche apprend

### Leviers de fidélité (tous modèles)
- **Référence** : 10 à 15 s de parole propre, mono, ≥ 24 kHz, sans bruit, ton conversationnel constant ; au-delà de ~30 s la qualité plafonne puis baisse. Transcription **exacte** (Whisper puis relecture à la main) : une erreur de texte dégrade le résultat.
- **Qwen3-TTS** : modèle *Base* pour cloner, 1.7B de préférence ; ajouter **0,5 s de silence** à la fin de la référence (évite une première syllabe « contaminée ») ; résultats variables d'une génération à l'autre → **générer plusieurs prises et garder la meilleure** ; limiter `max_new_tokens` contre les boucles infinies.
- **Affinage LoRA** (Qwen3-TTS) : 10 à 30 minutes de voix propre visées ; 5 minutes = minimum instable ; taux d'apprentissage 2e-6 ; balayage de l'intensité de l'adaptateur autour de 0,25 à 0,35 ; jeu de test fixe. Les guides disent avoir validé sur 24 Go de mémoire vidéo ; notre carte en a 12 : à vérifier.
- **VoxCPM2** : 2 milliards de paramètres, ~8 Go de mémoire vidéo, français pris en charge, licence Apache 2.0, sortie 48 kHz, mode « Ultimate Cloning » (référence + transcription exacte), affinage complet ou LoRA possible. Similarité annoncée : 73,5 % en français sur le banc MiniMax-MLS (chiffres du constructeur).
- **Voxtral TTS 3 (Mistral)** : clonage à partir de 3 s (idéal 5 à 25 s), français pris en charge, clonage inter-langues, **« Pro Voice » à partir d'environ 30 minutes** (la doc conseille 30 min à 3 h, une seule personne, même micro, sans réduction de bruit). Tarif public ~13 $ par million de caractères (notre texte ≈ 22 000 caractères, soit moins d'1 $ par essai complet). Les voix enregistrées ont une durée de conservation réglable (30 jours par défaut).
- **Conversion de voix en second passage** : Seed-VC annonce une meilleure ressemblance que OpenVoice (chiffres de l'auteur) ; son affinage améliore encore la ressemblance mais peut légèrement dégrader l'intelligibilité. RVC exige ≥ 10 minutes de voix.

### Ce qui a été écarté ou mis en seconde ligne
- **Chatterbox** (français pris en charge) : projet **retiré, plus maintenu depuis août 2026**, filigrane intégré. Seconde ligne.
- **XTTS-v2 / F5-TTS** : licences non commerciales. Utilisables pour un TP, mais pas meilleurs que les trois candidats ci-dessus.
- **Audio8-TTS, ZONOS3-Mini, OmniVoice** : récents, français non confirmé dans les sources. À surveiller seulement.
- **ElevenLabs** : probablement le meilleur clone « prêt à l'emploi », mais service payant et envoi de vos voix à un tiers. Non retenu, vous avez déjà Mistral.

## 3. Méthode d'essai proposée (objective, puis à l'oreille)

1. **Jeu de test commun** : 12 phrases tirées de notre vrai texte (chiffres en lettres, sigles, noms propres, phrases courtes et longues).
2. **Vérité terrain** : la vraie voix lit les mêmes phrases (voir §6) ; sinon, des extraits de la vraie voix non utilisés comme référence.
3. **Mesures** pour chaque candidat et chaque voix :
   - ressemblance de locuteur (empreinte ECAPA et/ou WavLM, cosinus) avec **deux repères** : même locuteur réel contre réel (plafond) et locuteurs différents (plancher) ;
   - intelligibilité : retranscription par Whisper large-v3 et taux d'erreur ;
   - débit en syllabes par seconde comparé à la vraie voix, niveau, bande passante, sibilances, crêtes ;
   - 5 prises par phrase pour mesurer la variabilité.
4. **Écoute à l'aveugle** : une page avec les échantillons mélangés (A/B/C, sans noms) que vous notez ; vous choisissez, pas moi.
5. Si le meilleur candidat n'atteint pas le niveau voulu : affinage (LoRA) avec de nouveaux enregistrements, et/ou passage Seed-VC, puis nouvelle mesure.

## 4. Chaîne d'étalonnage (fidèle à la vraie voix)

Ordre : correction de timbre → dynamique → niveau final. Chaque étape est comparée à la vraie voix et abandonnée si elle éloigne la ressemblance.

| Étape | Réglage de départ | Pourquoi |
|---|---|---|
| Filtre passe-haut | 70 à 80 Hz | supprime les basses parasites |
| Correction de timbre | écart mesuré entre la voix clonée et la vraie voix (spectre moyen en tiers d'octave), **limité à ±3 dB** | rapprocher la couleur sans la changer ; plus de 3 à 4 dB = problème de source, pas d'égalisation |
| Désibilation | seulement si les « s » sont plus agressifs que chez la vraie personne | évite le sifflement |
| Compression | rapport 2:1, attaque lente, 2 à 3 dB de réduction max | rend les phrases homogènes sans écraser le naturel |
| Niveau | **−16 LUFS** intégré, crête vraie ≤ −1,5 dBTP, mesure en 2 passes | niveau de narration pour vidéo web ; même niveau pour Thomas et Abderahmane |
| Vitesse | débit calé sur la vraie voix ; correction de durée **≤ ±6 %** par étirement de qualité (rubberband), sinon je raccourcis le texte | garde la voix naturelle ; vous avez dit que la vitesse peut bouger un peu |

Autres choix : pas de réverbération ajoutée, pas de réduction de bruit sur la voix générée (déjà propre), fondus courts de 20 ms au début et à la fin de chaque phrase. Une éventuelle musique de fond viendrait après, avec baisse automatique sous la voix.

## 5. Prononciation

Les nombres sont déjà en lettres (septante, huitante, nonante). Un lexique transformera les sigles au moment de la génération : VPC, NAT, NACL, SSH, SSM, IAM, ARN, BGP, GRE, ALB, ACM, SNS, SQS, TGW, « Route cinquante-trois », « Abderahmane », « Léman », « strongSwan », « FRRouting », « nginx ». Ces mots seront dans le jeu de test.

## 6. Ce qui améliorerait le plus la fidélité : plus de voix réelle

| Option | Durée à enregistrer par personne | Effet attendu |
|---|---|---|
| A. Rien de plus | 0 | clonage « extrait » : bon timbre, variations d'une prise à l'autre, quelques écarts d'intonation |
| B. Un peu plus | 3 à 5 min | meilleure référence et meilleurs essais, toujours sans affinage solide |
| C. Corpus d'affinage | 15 à 30 min | affinage LoRA (Qwen3-TTS ou VoxCPM2) et/ou « Pro Voice » de Mistral : la voie vers la fidélité maximale |

Conditions d'enregistrement : pièce calme, **même micro et même distance pour toute la séance** (10 à 20 cm), pas de réduction de bruit ni de compression automatique, WAV 48 kHz, ton naturel avec un peu de variété, phrases entières. Je fournirais un texte à lire (vocabulaire du projet, nombres, sigles) et je ferais le découpage.

Remarque d'honnêteté : si vous êtes prêts à enregistrer ~12 minutes chacun, lire directement votre propre texte donnerait évidemment la voix la plus fidèle possible. Vous avez choisi le clonage ; je pars donc sur cette voie, et je le signale seulement comme repère.

## 7. Besoins techniques

- Machine : carte RTX 5070 (12 Go), environnement Python déjà en place (torch 2.11 CUDA 12.8, Qwen3-TTS 1.7B Base, Whisper large-v3).
- À ajouter pour l'essai : VoxCPM2 (~5 Go de poids), un vérificateur de locuteur (ECAPA, ~0,1 Go), éventuellement Seed-VC (~1 à 2 Go), et des bibliothèques de mesure audio (pyloudnorm, pedalboard).
- Mistral : une clé d'API **que vous placez vous-même dans une variable d'environnement** (jamais dans le chat ni dans un fichier du dépôt).

## 8. Limites de cette recherche

- Aucune source ne compare Qwen3-TTS, VoxCPM2 et Voxtral en **français** : d'où l'essai sur vos voix.
- Les chiffres de similarité cités viennent des constructeurs ou des auteurs ; ils ne prédisent pas l'impression à l'écoute.
- Les guides d'affinage de Qwen3-TTS sont des blogs et dépôts personnels (matériel 24 Go, bogues corrigés depuis) ; rien ne garantit les mêmes résultats sur 12 Go.
- Les sources divergent sur la possibilité de cloner en local avec les poids ouverts de Voxtral (la doc Mistral ne parle de clonage qu'via l'API) : je n'utiliserai que l'API.

## Sources

- Qwen3-TTS, clonage et référence : [ocdevel](https://ocdevel.com/blog/20260302-qwen-tts-voice-cloning)
- Affinage LoRA de Qwen3-TTS : [Instavar](https://instavar.com/research/tts/qwen3-tts-lora-fine-tuning), [Baseten](https://www.baseten.co/blog/fine-tuning-qwen3-tts-for-high-quality-voice-cloning/)
- VoxCPM2 : [dépôt OpenBMB](https://github.com/OpenBMB/VoxCPM), [rapport technique](https://arxiv.org/html/2606.06928v1)
- Voxtral TTS : [annonce Mistral](https://mistral.ai/news/voxtral-3/), [clonage de voix (doc)](https://docs.mistral.ai/studio/audio/text-to-speech/voice-cloning), [fiche modèle](https://docs.mistral.ai/models/voxtral-mini-tts-3-0)
- Chatterbox (retiré) : [dépôt](https://github.com/resemble-ai/chatterbox)
- Conversion de voix : [Seed-VC](https://github.com/Plachtaa/seed-vc), [évaluation](https://github.com/Plachtaa/seed-vc/blob/main/EVAL.md)
- Mesures : [protocole Seed-TTS / F5-TTS](https://www.emergentmind.com/topics/seed-tts-eval), [Open TTS Leaderboard](https://github.com/huggingface/open-tts-leaderboard)
- Niveau sonore : [boucle loudnorm en deux passes](https://dev.to/demovexa/normalize-voiceover-loudness-with-ffmpeg-loudnorm-a-two-pass-recipe-2j0d)
- Correction de timbre : [Matchering](https://github.com/sergree/matchering)

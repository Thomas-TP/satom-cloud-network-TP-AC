"""Lexique de prononciation : transforme le texte validé (texte.txt) en texte à dire pour Qwen3-TTS.
Choix fondés sur le test de prononciation du 20/11/2026 (retranscription Whisper) : lettres séparées par des tirets pour les sigles,
écriture phonétique pour quelques noms anglais. Les nombres sont déjà écrits en toutes lettres dans le texte (septante, huitante, nonante)."""
import re
SIGLES = ['VPC', 'AWS', 'VPN', 'BGP', 'NACL', 'GRE', 'SSH', 'SSM', 'HTTPS', 'HTTP', 'API', 'IPsec', 'IP', 'IKE', 'AES', 'ACM', 'DNS', 'SNS', 'SQS', 'IAM', 'vCPU', 'AS', 'ASN']
def _epele(s):
    if s == 'IPsec': return 'I-P-sec'
    if s == 'vCPU': return 'V-C-P-U'
    return '-'.join(s)
MOTS = {
    'NAT': 'nate', 'JSON': 'jason', 'nginx': 'engine-X', 'strongSwan': 'strong-Swan', 'FRRouting': 'F-R-R-outing', 'iptables': 'I-P-tables',
    'CloudFront': 'Claoud-Front', 'CloudWatch': 'Claoud-Watch', 'CloudFormation': 'Claoud-Formation',
}
def speak(text):
    t = text
    for k, v in sorted(MOTS.items(), key=lambda kv: -len(kv[0])):
        t = re.sub(r'(?<![A-Za-z-])' + re.escape(k) + r'(?![A-Za-z-])', v, t)
    for s in sorted(SIGLES, key=len, reverse=True):
        t = re.sub(r'(?<![A-Za-z-])' + re.escape(s) + r'(?![A-Za-z-])', _epele(s), t)
    t = re.sub(r'(?<![A-Za-z-])api(?![A-Za-z-])', 'A-P-I', t)            # « slash api »
    t = re.sub(r'(?<![A-Za-z-])dev(?![A-Za-z-])', 'dève', t)             # « dev » était dit « d'œuf » par endroits
    t = re.sub(r'\s+', ' ', t).strip()
    return t

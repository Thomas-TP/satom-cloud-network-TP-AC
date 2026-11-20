"""Lit la chronologie du texte (lignes.json produit par video/voix/check.py) et applique le lexique de prononciation."""
import json, os, sys
sys.path.insert(0, r'C:\Perso\AWS\video\voix')
import lexique
def load_lines(scenes=None):
    d = json.load(open(r'C:\Perso\AWS\video\voix\lignes.json', encoding='utf8')); out = []
    for s in d['scenes']:
        if scenes and s['id'] not in scenes: continue
        for i, p in enumerate(s['lines']):
            out.append(dict(id=f"{s['id']}_{i:02d}", scene=s['id'], who=p['who'], text=p['text'], say=lexique.speak(p['text']), start=p['start'], est_end=p['end'], dur_est=p['end'] - p['start']))
    return out

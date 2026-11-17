"""Genere docs/CLIENT.pdf a partir de docs/CLIENT.md (markdown -> HTML -> PDF par Chrome en mode headless)."""
import os, re, subprocess, sys, glob
import markdown

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
md = open(os.path.join(ROOT, 'docs', 'CLIENT.md'), encoding='utf-8').read()
md = md.replace('](../images/', '](images/')
body = markdown.markdown(md, extensions=['tables', 'sane_lists'])
css = """
@page { size: A4; margin: 16mm 14mm; }
body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.5pt; color: #1e293b; line-height: 1.45; }
h1 { font-size: 20pt; color: #0f172a; border-bottom: 3px solid #6366f1; padding-bottom: 4px; }
h2 { font-size: 13.5pt; color: #3730a3; margin-top: 16px; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 9.3pt; page-break-inside: avoid; }
th { background: #eef2ff; text-align: left; } th, td { border: 1px solid #cbd5e1; padding: 4px 7px; vertical-align: top; }
img { max-width: 100%; } code { background: #f1f5f9; padding: 0 3px; border-radius: 3px; font-size: 9pt; }
hr { border: 0; border-top: 1px solid #e2e8f0; }
"""
html = '<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>%s</style></head><body>%s</body></html>' % (css, body)
out_html = os.path.join(ROOT, 'docs', 'CLIENT.html')
open(out_html, 'w', encoding='utf-8').write(html)
cands = glob.glob(r'C:\Program Files\Google\Chrome*\Application\chrome.exe') + glob.glob(r'C:\Program Files (x86)\Google\Chrome*\Application\chrome.exe') \
    + glob.glob(os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome*', 'Application', 'chrome.exe'))
chrome = cands[0]
pdf = os.path.join(ROOT, 'docs', 'CLIENT.pdf')
subprocess.run([chrome, '--headless=new', '--disable-gpu', '--no-pdf-header-footer', '--print-to-pdf=' + pdf, 'file:///' + out_html.replace('\\', '/')], check=True, capture_output=True)
os.remove(out_html)
print('PDF :', pdf, os.path.getsize(pdf) // 1024, 'Ko')

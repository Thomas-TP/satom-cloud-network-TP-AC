"""Range les captures reelles de captures/_shots dans captures/mNN : mNN-k -> 10-terminal-k.png ; lNN-i -> 99-journal-i.png (recadrees : le vide du bas est retire)."""
import glob, os, re
from PIL import Image
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
n = 0
for p in sorted(glob.glob(os.path.join(ROOT, 'captures', '_shots', '*.png'))):
    m = re.match(r'([ml])(\d\d)-(\d+)\.png', os.path.basename(p))
    if not m: continue
    kind, mod, k = m.groups(); dest_dir = os.path.join(ROOT, 'captures', 'm' + mod); os.makedirs(dest_dir, exist_ok=True)
    im = Image.open(p).convert('RGB'); w, h = im.size; px = im.load()
    last = 0
    for y in range(h - 1, -1, -1):
        if any(sum(px[x, y]) > 90 for x in range(0, w, 4)): last = y; break
    im = im.crop((0, 0, w, min(h, last + 40)))
    name = ('10-terminal-%s.png' % k) if kind == 'm' else ('99-journal-%s.png' % k)
    im.save(os.path.join(dest_dir, name)); n += 1
print(n, 'captures rangees')

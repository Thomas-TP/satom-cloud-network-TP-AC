"""Outil de tournage de la console AWS : se connecte au Chrome dedie (port 9333), affiche un curseur visible avec clic anime,
tape le texte comme un humain, et enregistre la page en 1920x1080 / 30 i/s (screencast CDP -> ffmpeg).
Chaque script de tournage est une coroutine qui utilise Rig. Les marqueurs (mark) servent au montage et a la voix."""
import asyncio, base64, json, math, os, random, re, subprocess, time
from playwright.async_api import async_playwright

FFMPEG = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WinGet', 'Links', 'ffmpeg.exe')
W, H, FPS = 1920, 1080, 30

CURSOR_JS = r"""
(() => {
  if (window.__tpac) return;
  window.__tpac = true;
  const mk = () => {
    if (document.getElementById('__cur') || !document.documentElement) return;
    const c = document.createElement('div'); c.id = '__cur';
    c.style.cssText = 'position:fixed;left:0;top:0;width:28px;height:28px;z-index:2147483647;pointer-events:none;transform:translate(-100px,-100px);filter:drop-shadow(1px 2px 2px rgba(0,0,0,.45));';
    c.innerHTML = '<svg width="28" height="28" viewBox="0 0 28 28"><path d="M3 2 L3 22 L8.5 17.3 L12.2 25.5 L15.6 24 L12 16 L19.5 16 Z" fill="#fff" stroke="#111" stroke-width="1.6" stroke-linejoin="round"/></svg>';
    document.documentElement.appendChild(c);
    const st = document.createElement('style');
    st.textContent = '@keyframes __rip{0%{transform:translate(-50%,-50%) scale(.2);opacity:.85}100%{transform:translate(-50%,-50%) scale(1.6);opacity:0}}';
    document.documentElement.appendChild(st);
  };
  window.__pos = {x: -100, y: -100};
  window.__move = (x, y, ms, j = 60) => new Promise(res => {
    mk(); const c = document.getElementById('__cur'); const sx = window.__pos.x, sy = window.__pos.y; const t0 = performance.now();
    const cx = (sx + x) / 2 + (Math.random() - .5) * j, cy = (sy + y) / 2 + (Math.random() - .5) * j;
    const ease = t => t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
    const step = now => {
      let t = Math.min(1, (now - t0) / ms), e = ease(t);
      const px = (1 - e) * (1 - e) * sx + 2 * (1 - e) * e * cx + e * e * x, py = (1 - e) * (1 - e) * sy + 2 * (1 - e) * e * cy + e * e * y;
      c.style.transform = 'translate(' + (px - 3) + 'px,' + (py - 2) + 'px)'; window.__pos = {x: px, y: py};
      if (t < 1) requestAnimationFrame(step); else res(true);
    };
    requestAnimationFrame(step);
  });
  window.__ripple = (x, y) => {
    const r = document.createElement('div');
    r.style.cssText = 'position:fixed;left:' + x + 'px;top:' + y + 'px;width:56px;height:56px;border-radius:50%;border:3px solid #4f8cff;background:rgba(79,140,255,.25);z-index:2147483646;pointer-events:none;animation:__rip .5s ease-out forwards;';
    document.documentElement.appendChild(r); setTimeout(() => r.remove(), 600);
  };
  document.addEventListener('DOMContentLoaded', mk); mk();
})();
"""

HIDER_JS = r"""
(() => {
  if (window.__hider) return; window.__hider = true;
  // vie privee : le compte AWS est partage avec la classe. On masque (display:none) les lignes de listes qui portent un nom de ressource
  // d'un autre eleve (meme schema de nommage mais sans TP-AC). Les filtres tapes restent reels.
  const OTHER = /(sub-(prive|public|fw|dev|siege|agence)|rt-(prod|dev|sites|prive|public|fw)|sg-(web|app|alb|rtr)|nacl|igw-|nat-prod|vpc-(prod|dev|siege|agence)|alb-|tg-(web|app)|web-01|app-01|dev-01|rtr-|vpn-|cgw-|tgw|nfw|dxgw|leman|pcx-lab|satom|policy-prod|rg-|budget-|nfw-|eip-)/i;
  const SUFFIX = /(^|[-_ (/\s])(MF|MM|AA|LL|JH|AF|BKO|TM|ADSN|fatoumata)($|[-_ )/\s])/i;
  const TPOTHER = /TP\d*-(?!AC)[A-Za-z]{2,}/i;
  const sweep = () => {
    document.querySelectorAll('tr, [role=row], [role=option], [role=treeitem]').forEach(e => {
      const tx = e.innerText || ''; if (!tx) return;
      const hide = (OTHER.test(tx) || SUFFIX.test(tx) || TPOTHER.test(tx)) && !/TP-AC/i.test(tx) && !(window.__ownRe && window.__ownRe.test(tx));
      if (hide) e.style.setProperty('display', 'none', 'important'); else if (e.dataset.tpacHid) e.style.removeProperty('display');
      if (hide) e.dataset.tpacHid = '1';
    });
  };
  setInterval(sweep, 120);
  setInterval(() => { const b = [...document.querySelectorAll('button')].find(x => /^(Fermer AWS assistant|Close AWS assistant)$/i.test(x.getAttribute('aria-label') || '')); if (b) b.click(); }, 700);
  // masquage de l'identifiant de compte et de l'identite de session (texte du DOM) : l'ecran reste reel, ces valeurs sont remplacees a la source
  const M = window.__masks || {}; const esc = x => (x || 'x_none_').replace(/[^A-Za-z0-9 -]/g, c => String.fromCharCode(92) + c);
  const MASKS = [[new RegExp(esc(M.compte), 'g'), '************'], [new RegExp(esc(M.session), 'g'), '********-****-****-****-************'], [new RegExp(esc(M.nom), 'g'), 'Compte de formation']];
  const maskText = () => {
    const w = document.createTreeWalker(document.documentElement, NodeFilter.SHOW_TEXT);
    let n; while ((n = w.nextNode())) { let v = n.nodeValue; if (!v || v.length < 8) continue; let c = v; for (const [re, rep] of MASKS) c = c.replace(re, rep); if (c !== v) n.nodeValue = c; }
    document.querySelectorAll('input,textarea').forEach(e => { if (false) { /* valeurs saisies : non modifiees */ } });
  };
  setInterval(maskText, 200);
})();
"""


# identifiants des ressources de l'equipe (etiquette Equipe=TP-AC) : leurs lignes ne sont jamais masquees meme quand le nom n'apparait pas (ex. propagations)
import threading
_OWN = {'re': ''}
def _refresh_own():
    while True:
        try:
            out = subprocess.run(['aws', 'resourcegroupstaggingapi', 'get-resources', '--tag-filters', 'Key=Equipe,Values=TP-AC', '--profile', 'TP-AC', '--region', 'eu-north-1',
                                  '--query', 'ResourceTagMappingList[].ResourceARN', '--output', 'text'], capture_output=True, text=True, timeout=40).stdout.split()
            ids = sorted({a.rsplit('/', 1)[-1] for a in out if '/' in a and re.match(r'^([a-z]+-[0-9a-f]{8,}|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$', a.rsplit('/', 1)[-1])})
            if ids: _OWN['re'] = '|'.join(ids)
        except Exception: pass
        time.sleep(12)
threading.Thread(target=_refresh_own, daemon=True).start()


def _masks():
    """Valeurs a masquer a l'ecran (compte, identite de session) : fichier local profile/masks.json, jamais depose dans le depot."""
    try: return json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profile', 'masks.json'), encoding='utf-8'))
    except Exception: return {}


class Rig:
    def __init__(self):
        self.t0 = None; self.marks = []; self.ff = None; self.latest = None; self.rec = False

    async def connect(self, new_page=False):
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.connect_over_cdp('http://127.0.0.1:9333')
        self.ctx = self.browser.contexts[0]
        pages = [p for p in self.ctx.pages if 'console.aws.amazon.com' in p.url]
        self.page = pages[0] if pages and not new_page else await self.ctx.new_page()
        for p in list(self.ctx.pages):   # on ne garde qu'un onglet : les onglets de session des scenes precedentes sont fermes
            if p is not self.page and not p.url.startswith('devtools'):
                try: await p.close()
                except Exception: pass
        await self.ctx.add_init_script(CURSOR_JS); await self.ctx.add_init_script(HIDER_JS)
        self.cdp = await self.ctx.new_cdp_session(self.page)
        await self.cdp.send('Emulation.setDeviceMetricsOverride', {'width': W, 'height': H, 'deviceScaleFactor': 1, 'mobile': False})
        await self.page.evaluate(CURSOR_JS)
        await self.inject_hider()
        return self

    async def follow(self, page):
        """Bascule l'enregistrement et les gestes sur une autre page (ex. l'onglet ouvert par Session Manager)."""
        was = self.rec
        if was:
            try: await self.cdp.send('Page.stopScreencast')
            except Exception: pass
        self.page = page
        await page.bring_to_front()
        self.cdp = await self.ctx.new_cdp_session(page)
        await self.cdp.send('Emulation.setDeviceMetricsOverride', {'width': W, 'height': H, 'deviceScaleFactor': 1, 'mobile': False})
        try: await page.evaluate(CURSOR_JS)
        except Exception: pass
        if was:
            async def on_frame(ev):
                self.latest = base64.b64decode(ev['data'])
                try: await self.cdp.send('Page.screencastFrameAck', {'sessionId': ev['sessionId']})
                except Exception: pass
            self.cdp.on('Page.screencastFrame', lambda ev: asyncio.ensure_future(on_frame(ev)))
            await self.cdp.send('Page.startScreencast', {'format': 'jpeg', 'quality': 92, 'maxWidth': W, 'maxHeight': H, 'everyNthFrame': 1})

    async def inject_hider(self):
        own = _OWN['re']
        for f in self.page.frames:
            try:
                if own: await f.evaluate('(s) => { window.__ownRe = new RegExp(s); }', own)
                await f.evaluate('(m) => { window.__masks = m; }', _masks())
                await f.evaluate(HIDER_JS)
            except Exception: pass

    async def close(self):
        if self.rec: await self.stop()
        await self.pw.stop()

    # ---------------- enregistrement
    async def start(self, out):
        self.out = out; os.makedirs(os.path.dirname(out), exist_ok=True)
        self.ff = subprocess.Popen([FFMPEG, '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-',
                                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE)

        async def on_frame(ev):
            self.latest = base64.b64decode(ev['data'])
            try: await self.cdp.send('Page.screencastFrameAck', {'sessionId': ev['sessionId']})
            except Exception: pass
        self.cdp.on('Page.screencastFrame', lambda ev: asyncio.ensure_future(on_frame(ev)))
        await self.cdp.send('Page.startScreencast', {'format': 'jpeg', 'quality': 92, 'maxWidth': W, 'maxHeight': H, 'everyNthFrame': 1})
        for _ in range(100):
            if self.latest: break
            await asyncio.sleep(0.05)
        self.rec = True; self.t0 = time.time(); self.marks = []
        self.writer = asyncio.ensure_future(self._writer())

    async def _writer(self):
        n = 0; start = time.time()
        while self.rec:
            n += 1
            try: self.ff.stdin.write(self.latest)
            except Exception: break
            await asyncio.sleep(max(0, start + n / FPS - time.time()))

    async def stop(self):
        self.rec = False; await asyncio.sleep(0.2)
        try: await self.cdp.send('Page.stopScreencast')
        except Exception: pass
        try: self.ff.stdin.close()
        except Exception: pass
        self.ff.wait(timeout=60)
        json.dump(self.marks, open(os.path.splitext(self.out)[0] + '.marks.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

    def mark(self, name, **kw):
        t = round(time.time() - self.t0, 2) if self.t0 else 0
        self.marks.append(dict(t=t, name=name, **kw)); print(f'[{t:7.2f}] {name}', kw or '', flush=True)

    # ---------------- gestes
    async def _resolve(self, target, timeout=15):
        """Trouve la cible dans la page ou dans l'un de ses iframes (la console AWS charge chaque service dans un iframe about:blank).
        target : selecteur (str), ou fonction f -> locator (ex. lambda f: f.get_by_role('row').nth(1)), ou locator."""
        if not isinstance(target, str) and not callable(target): return target
        end = time.time() + timeout
        while time.time() < end:
            for f in self.page.frames:
                try:
                    loc = f.locator(target) if isinstance(target, str) else target(f)
                    if await loc.count() > 0 and await loc.first.is_visible(): return loc
                except Exception: pass
            await asyncio.sleep(0.3)
        raise AssertionError(f'introuvable : {target}')

    async def _box(self, target):
        loc = await self._resolve(target)
        await loc.first.scroll_into_view_if_needed(timeout=15000)
        b = await loc.first.bounding_box(); assert b, f'introuvable : {target}'
        return b

    async def move(self, x, y, ms=None, j=60):
        px = await self.page.evaluate('window.__pos ? [window.__pos.x, window.__pos.y] : [0,0]'); d = math.hypot(x - px[0], y - px[1])
        ms = ms or int(min(1100, max(350, 300 + d * 0.9)))
        await self.page.evaluate('([x,y,ms,j]) => window.__move(x,y,ms,j)', [x, y, ms, j]); await self.page.mouse.move(x, y)

    async def click(self, target, dx=0.5, dy=0.5, pause=0.35, double=False, straight=False):
        loc = await self._resolve(target)
        b = await self._box(loc); x, y = b['x'] + b['width'] * dx, b['y'] + b['height'] * dy
        await self.move(x, y, None, 0 if straight else 60); await asyncio.sleep(pause * 0.5)
        try:   # la liste a pu bouger pendant le deplacement du curseur : on reprend la position juste avant le clic
            b2 = await loc.first.bounding_box()
            if b2 and (abs(b2['x'] - b['x']) > 3 or abs(b2['y'] - b['y']) > 3):
                x, y = b2['x'] + b2['width'] * dx, b2['y'] + b2['height'] * dy; await self.move(x, y, 200)
        except Exception: pass
        await self.page.evaluate('([x,y]) => window.__ripple(x,y)', [x, y])
        await self.page.mouse.click(x, y, click_count=2 if double else 1); await asyncio.sleep(pause)

    async def click_xy(self, x, y, pause=0.35):
        await self.move(x, y); await asyncio.sleep(pause * 0.5)
        await self.page.evaluate('([x,y]) => window.__ripple(x,y)', [x, y])
        await self.page.mouse.click(x, y); await asyncio.sleep(pause)

    async def type(self, target, text, delay=60, clear=True):
        loc = await self._resolve(target)
        await self.click(loc)
        if clear:
            await self.page.keyboard.press('Control+A'); await self.page.keyboard.press('Delete')
        for ch in text:
            try:   # la console remonte parfois le champ apres une touche : on lui rend le focus sans le cliquer
                if not await loc.first.evaluate('e => e === document.activeElement'): await loc.first.focus()
            except Exception: pass
            await self.page.keyboard.type(ch); await asyncio.sleep((delay + random.randint(-20, 30)) / 1000)
        await asyncio.sleep(0.3)

    async def present(self, target, timeout=1.0):
        try: await self._resolve(target, timeout); return True
        except AssertionError: return False

    async def press(self, key, pause=0.4):
        await self.page.keyboard.press(key); await asyncio.sleep(pause)

    async def goto(self, url, wait=2.5):
        for essai in range(3):   # la console renvoie parfois vers la page de connexion le temps de renouveler la session : on reessaie
            try:
                await self.page.goto(url, wait_until='domcontentloaded', timeout=45000)
                if 'signin.aws' in self.page.url and essai < 2:
                    await asyncio.sleep(6); continue
                break
            except Exception:
                if essai == 2: raise
                await asyncio.sleep(5)
        await self.page.evaluate(CURSOR_JS); await asyncio.sleep(wait); await self.inject_hider()

    async def hold(self, sec): await asyncio.sleep(sec)

    async def hover(self, target, pause=0.8):
        b = await self._box(target); await self.move(b['x'] + b['width'] / 2, b['y'] + b['height'] / 2); await asyncio.sleep(pause)

    async def scroll(self, dy=400, steps=8):
        await self.page.mouse.move(960, 620)
        for _ in range(steps):
            await self.page.mouse.wheel(0, dy / steps); await asyncio.sleep(0.05)
        await asyncio.sleep(0.4)


# ---------------- raccourcis de selection (fonctions f -> locator, resolues dans la bonne frame)
def btn(name, exact=False): return lambda f: f.get_by_role('button', name=name, exact=exact)
def link(name, exact=False): return lambda f: f.get_by_role('link', name=name, exact=exact)
def tab(name): return lambda f: f.get_by_role('tab', name=name)
def radio(name): return lambda f: f.get_by_role('radio', name=name)
def box(name): return lambda f: f.get_by_role('checkbox', name=name)
def field(name): return lambda f: f.get_by_label(name, exact=False)
def ph(text): return lambda f: f.get_by_placeholder(text)
def txt(text, exact=False): return lambda f: f.get_by_text(text, exact=exact)
def opt(name): return lambda f: f.get_by_role('option', name=name)

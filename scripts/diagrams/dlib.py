"""Mini-bibliotheque de schemas reseau (Pillow) - style propre et moderne, fond blanc, bandeau GIT - Satom."""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1600, 900
FONT = r"C:\Windows\Fonts\segoeui.ttf"
FONT_B = r"C:\Windows\Fonts\segoeuib.ttf"
C = dict(ink=(30, 41, 59), mute=(100, 116, 139), line=(148, 163, 184),
         vpc=(238, 242, 255), vpc_b=(99, 102, 241), pub=(220, 252, 231), pub_b=(22, 163, 74),
         priv=(254, 243, 199), priv_b=(217, 119, 6), fw=(254, 226, 226), fw_b=(220, 38, 38),
         dev=(224, 242, 254), dev_b=(2, 132, 199), onp=(241, 245, 249), onp_b=(71, 85, 105),
         ok=(22, 163, 74), ko=(220, 38, 38), warn=(234, 88, 12), blue=(37, 99, 235), grey=(156, 163, 175),
         purple=(124, 58, 237), band=(15, 23, 42), white=(255, 255, 255))


def f(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


class Diagram:
    def __init__(self, title, subtitle=""):
        self.im = Image.new("RGB", (W, H), C["white"])
        self.d = ImageDraw.Draw(self.im)
        d = self.d
        d.rectangle([0, 0, W, 70], fill=C["band"])
        d.text((30, 18), "GIT \u2013 Satom", font=f(26, True), fill=C["white"])
        d.text((W // 2, 35), title, font=f(26, True), fill=C["white"], anchor="mm")
        d.text((W - 30, 35), "Equipe TP-AC \u2013 Groupe L\u00e9man Finance SA", font=f(18), fill=(203, 213, 225), anchor="rm")
        if subtitle:
            d.text((30, 85), subtitle, font=f(18), fill=C["mute"])
        self.legend_items = []

    def box(self, x, y, w, h, label, fill, border, sub=None, radius=14, lw=3, bold=True, size=20, dash=False):
        d = self.d
        if dash:
            self._dashed_rect(x, y, w, h, border, lw)
            d.rounded_rectangle([x + 2, y + 2, x + w - 2, y + h - 2], radius, fill=fill)
            self._dashed_rect(x, y, w, h, border, lw)
        else:
            d.rounded_rectangle([x, y, x + w, y + h], radius, fill=fill, outline=border, width=lw)
        if label:
            d.text((x + 14, y + 8), label, font=f(size, bold), fill=C["ink"])
        if sub:
            for i, line in enumerate(sub if isinstance(sub, list) else [sub]):
                d.text((x + 14, y + 8 + size + 6 + i * 20), line, font=f(16), fill=C["mute"])

    def _dashed_rect(self, x, y, w, h, color, lw):
        for (x1, y1, x2, y2) in [(x, y, x + w, y), (x + w, y, x + w, y + h), (x + w, y + h, x, y + h), (x, y + h, x, y)]:
            self.line((x1, y1), (x2, y2), color, lw, dash=True)

    def node(self, cx, cy, label, sub=None, fill=C["white"], border=C["ink"], w=170, h=64):
        d = self.d
        d.rounded_rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], 12, fill=fill, outline=border, width=3)
        d.text((cx, cy - (9 if sub else 0)), label, font=f(18, True), fill=C["ink"], anchor="mm")
        if sub:
            d.text((cx, cy + 14), sub, font=f(14), fill=C["mute"], anchor="mm")

    def line(self, p1, p2, color=C["ink"], width=4, dash=False, arrow=False):
        d = self.d
        import math
        x1, y1 = p1; x2, y2 = p2
        if dash:
            L = math.hypot(x2 - x1, y2 - y1)
            n = int(L // 16)
            for i in range(0, n, 2):
                a = i / max(n, 1); b = min((i + 1) / max(n, 1), 1)
                d.line([(x1 + (x2 - x1) * a, y1 + (y2 - y1) * a), (x1 + (x2 - x1) * b, y1 + (y2 - y1) * b)], fill=color, width=width)
        else:
            d.line([p1, p2], fill=color, width=width)
        if arrow:
            ang = math.atan2(y2 - y1, x2 - x1)
            for s in (-0.45, 0.45):
                d.line([p2, (x2 - 18 * math.cos(ang + s), y2 - 18 * math.sin(ang + s))], fill=color, width=width)

    def label(self, x, y, text, color=C["ink"], size=16, bold=False, anchor="mm", bg=True):
        d = self.d
        fo = f(size, bold)
        if bg:
            bb = d.textbbox((x, y), text, font=fo, anchor=anchor)
            d.rectangle([bb[0] - 5, bb[1] - 2, bb[2] + 5, bb[3] + 2], fill=C["white"])
        d.text((x, y), text, font=fo, fill=color, anchor=anchor)

    def num(self, x, y, n, color=C["ok"]):
        self.d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=color)
        self.d.text((x, y), str(n), font=f(18, True), fill=C["white"], anchor="mm")

    def legend(self, items, x=30, y=None):
        y = y or H - 70
        d = self.d
        d.line([(0, y - 14), (W, y - 14)], fill=(226, 232, 240), width=2)
        cx = x
        for color, text, dash in items:
            self.line((cx, y + 12), (cx + 50, y + 12), color, 5, dash=dash)
            d.text((cx + 60, y + 12), text, font=f(16), fill=C["ink"], anchor="lm")
            cx += 60 + d.textlength(text, font=f(16)) + 40

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.im.save(path)
        print("ok", path)

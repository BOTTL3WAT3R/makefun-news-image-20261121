#!/usr/bin/env python3
"""news-image-20261121 — offline poster renderer (Pillow).

Draws Saturday 21 November 2026's world news as one 1024x1024 front-page
poster and writes it to entry.png beside this file. This program is run ONCE
at build time; the committed entry.png is what the entry ships, and main.py
(the stdlib-only entrypoint) simply copies it to the output directory.

Every story on the poster is a real, verified 21 November 2026 news item —
see research/FACTS-20261121.md in the entry workspace for the fact record.

Rendering is deterministic: fixed canvas, fixed fonts, no randomness, no
clock, no network. Re-running produces byte-identical PNG bytes.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024

NAVY = (11, 42, 91)
NAVY_LIGHT = (38, 74, 128)
RED = (178, 30, 30)
INK = (15, 15, 15)
PAPER = (255, 255, 255)
PANEL_BG = (232, 238, 247)
PANEL_LINE = (11, 42, 91)
GOLD = (238, 183, 30)
SKY = (168, 198, 232)
GREY = (90, 100, 115)

SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def centered(draw, cx, y, text, fnt, fill):
    draw.text((cx, y), text, font=fnt, fill=fill, anchor="ma")
    return y + fnt.size


def wrap(draw, text, fnt, max_width):
    """Greedy word-wrap using real glyph metrics."""
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if draw.textlength(trial, font=fnt) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- panels art
# Tiny flat-vector strips, echoing the simple icon style of a wire poster.

def art_skyline_missile(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=SKY)
    bw = w // 7
    for i, bh in enumerate((0.55, 0.8, 0.45, 0.7, 0.6, 0.85, 0.5)):
        bx = x + i * bw
        draw.rectangle([bx + 3, y + h - bh * h, bx + bw - 3, y + h], fill=NAVY_LIGHT)
    pts = []
    for t in range(21):
        fx = t / 20.0
        pts.append((x + fx * w * 0.9 + 4, y + h * 0.75 - (fx * fx) * h * 0.55))
    draw.line(pts, fill=RED, width=3)
    draw.ellipse([x + w * 0.86, y + h * 0.12, x + w * 0.97, y + h * 0.12 + 11], fill=RED)


def art_flags(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(240, 240, 235))
    cols = [(178, 30, 30), (245, 245, 245), (30, 90, 168)]
    for i, c in enumerate(cols):
        fx = x + w * (0.14 + i * 0.28)
        draw.line([fx, y + 3, fx, y + h - 3], fill=GREY, width=3)
        draw.rectangle([fx, y + 5, fx + w * 0.19, y + 5 + h * 0.44], fill=c, outline=GREY)


def art_scales(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(226, 232, 220))
    cx = x + w // 2
    draw.line([cx, y + 4, cx, y + h - 5], fill=NAVY, width=4)
    draw.line([cx - w * 0.28, y + 9, cx + w * 0.28, y + 9], fill=NAVY, width=4)
    for s in (-1, 1):
        px = cx + s * w * 0.28
        draw.line([px, y + 9, px - 13, y + h * 0.6], fill=NAVY, width=2)
        draw.line([px, y + 9, px + 13, y + h * 0.6], fill=NAVY, width=2)
        draw.arc([px - 14, y + h * 0.46, px + 14, y + h * 0.76], 0, 180, fill=NAVY, width=3)


def art_intercept(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(20, 34, 64))
    for sx, sy in ((0.1, 0.2), (0.3, 0.5), (0.55, 0.15), (0.8, 0.4), (0.92, 0.65)):
        draw.ellipse([x + sx * w, y + sy * h * 0.5, x + sx * w + 3, y + sy * h * 0.5 + 3], fill=(255, 255, 255))
    pts = [(x + 6, y + h - 5)]
    for t in range(1, 11):
        fx = t / 10.0
        pts.append((x + fx * w * 0.8, y + h - 5 - fx * h * 0.7))
    draw.line(pts, fill=GOLD, width=3)
    ex, ey = x + w * 0.86, y + h * 0.22
    for dx, dy in ((0, -9), (7, -7), (9, 0), (7, 7), (0, 9), (-7, 7), (-9, 0), (-7, -7)):
        draw.line([ex, ey, ex + dx, ey + dy], fill=(255, 140, 40), width=2)


def art_eu(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(0, 51, 153))
    cx, cy, r = x + w * 0.22, y + h / 2, h * 0.33
    for i in range(12):
        a = 2 * math.pi * i / 12
        sx, sy = cx + r * math.cos(a), cy + r * math.sin(a)
        draw.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=GOLD)
    f = font(SANS_BOLD, 26)
    draw.text((x + w * 0.4, y + h / 2), "€7.9bn", font=f, fill=(255, 255, 255), anchor="lm")


def art_chart(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(245, 240, 235))
    pts = [(x + 8, y + h * 0.25), (x + w * 0.3, y + h * 0.35), (x + w * 0.5, y + h * 0.3),
           (x + w * 0.7, y + h * 0.62), (x + w * 0.92, y + h * 0.85)]
    draw.line(pts, fill=RED, width=4)
    ex, ey = pts[-1]
    draw.polygon([(ex, ey), (ex - 12, ey - 2), (ex - 3, ey - 11)], fill=RED)
    f = font(SANS_BOLD, 22)
    draw.text((x + 10, y + 4), "-3.7%", font=f, fill=RED)


def art_flame(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(250, 238, 220))
    cx = x + w * 0.28
    draw.polygon([(cx, y + 3), (cx + 12, y + h * 0.55), (cx + 8, y + h - 3),
                  (cx - 8, y + h - 3), (cx - 12, y + h * 0.55)], fill=(232, 110, 30))
    draw.polygon([(cx, y + h * 0.35), (cx + 6, y + h * 0.62), (cx + 4, y + h - 4),
                  (cx - 4, y + h - 4), (cx - 6, y + h * 0.62)], fill=GOLD)
    hx, hy = x + w * 0.6, y + h * 0.42
    draw.polygon([(hx, hy), (hx + 20, hy - 13), (hx + 40, hy)], fill=GREY)
    draw.rectangle([hx + 5, hy, hx + 35, y + h - 4], outline=GREY, width=2)


ART = {
    "summit": art_flags,
    "court": art_scales,
    "riyadh": art_intercept,
    "eu": art_eu,
    "markets": art_chart,
    "palisades": art_flame,
    "kyiv": art_skyline_missile,
}


def panel(draw, x, y, w, h, art_key, title, caption):
    draw.rectangle([x, y, x + w, y + h], fill=PANEL_BG, outline=PANEL_LINE, width=2)
    ART[art_key](draw, x + 2, y + 2, w - 4, 26)
    draw.text((x + 12, y + 33), title, font=font(SANS_BOLD, 22), fill=NAVY)
    f_cap = font(SANS, 17)
    cy = y + 62
    for ln in wrap(draw, caption, f_cap, w - 24)[:2]:
        draw.text((x + 12, cy), ln, font=f_cap, fill=INK)
        cy += 20


def main():
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    draw.rectangle([13, 13, W - 13, H - 13], fill=PAPER)

    M = 30
    CW = W - 2 * M

    # --- masthead ------------------------------------------------------
    draw.rectangle([M, 24, W - M, 80], fill=NAVY)
    centered(draw, W // 2, 33, "THE WORLD TODAY", font(SANS_BOLD, 40), (255, 255, 255))

    # --- giant dateline -------------------------------------------------
    centered(draw, W // 2, 90, "SATURDAY 21 NOVEMBER 2026", font(SANS_BOLD, 52), NAVY)
    draw.rectangle([M, 150, W - M, 156], fill=RED)

    # --- lead headline --------------------------------------------------
    f_lead = font(SANS_BOLD, 76)
    centered(draw, W // 2, 166, "RUSSIAN MISSILES", f_lead, INK)
    centered(draw, W // 2, 246, "HIT POLAND", f_lead, INK)
    f_sub = font(SANS, 23)
    sub1 = ("Two missiles and a drone fall on Polish soil in the night barrage; "
            "Warsaw calls it a deliberate provocation and seeks NATO support")
    y = 330
    for ln in wrap(draw, sub1, f_sub, CW - 40):
        centered(draw, W // 2, y, ln, f_sub, NAVY)
        y += 28
    draw.rectangle([M, y + 6, W - M, y + 11], fill=RED)

    # --- second headline -------------------------------------------------
    y += 22
    centered(draw, W // 2, y, "KYIV BRIDGES BOMBED IN MASSIVE STRIKE", font(SANS_BOLD, 38), INK)
    y += 50
    sub2 = ("110+ missiles and some 400 drones in one night; three Dnipro bridges hit, "
            "at least nine dead in Kyiv — Kryvyi Rih: two dead, 42 injured")
    for ln in wrap(draw, sub2, f_sub, CW - 40):
        centered(draw, W // 2, y, ln, f_sub, NAVY)
        y += 28

    # --- panels -----------------------------------------------------------
    panels = [
        ("summit", "SHENZHEN SUMMIT ENDS",
         "Trump, Xi and Putin end their first trilateral summit with no Ukraine "
         "breakthrough; Putin holds firm."),
        ("court", "WORLD COURT: GENOCIDE",
         "The ICJ rules 9–6 that Myanmar committed genocide against the Rohingya. "
         "Myanmar and China reject it."),
        ("riyadh", "RIYADH INTERCEPTS",
         "Saudi-led coalition intercepts Houthi missiles over Riyadh, day two; "
         "six Houthi workshops hit in Sana'a."),
        ("eu", "EU SENDS KYIV €7.9BN",
         "Brussels disburses a record €7.9bn to Ukraine and adopts €1bn more in "
         "military aid for Kyiv."),
        ("markets", "MARKETS IN CORRECTION",
         "The S&P 500 and Dow fall about 3.7% into correction as investors dump "
         "AI and chip stocks."),
        ("palisades", "PALISADES VERDICT",
         "A Los Angeles jury convicts Jonathan Rinderknecht of arson: 12 dead, "
         "some 6,800 buildings lost."),
    ]
    top = y + 14
    gap = 8
    pw = (CW - gap) // 2
    ph = 106
    for i, (key, title, cap) in enumerate(panels):
        px = M + (i % 2) * (pw + gap)
        py = top + (i // 2) * (ph + gap)
        panel(draw, px, py, pw, ph, key, title, cap)
    bottom = top + 3 * ph + 2 * gap

    # --- ALSO strip -------------------------------------------------------
    briefs = [
        "UK & EU sign food, carbon & youth deals",
        "COP31 talks run overtime in Antalya, no deal yet",
        "US approved 879,000 AI chips for China",
        "Cancer pill shrinks pancreatic tumours in trial",
        "Denmark charges two in Russian murder plot",
        "Indian man jailed 19 years in US murder plot",
        "Italy hit by general strike over living costs",
        "US sanctions four Iranians over oil revenues",
        "Zverev ends Turin group 3–0; Shelton in semis",
        "Las Vegas GP practice washed out by rain",
    ]
    ay = bottom + 12
    draw.rectangle([M, ay, W - M, H - 16], fill=NAVY)
    draw.text((M + 14, ay + 7), "ALSO IN THE NEWS", font=font(SANS_BOLD, 19), fill=GOLD)
    f_brief = font(SANS, 16)
    col_w = (CW - 28) // 2
    for i, b in enumerate(briefs):
        bx = M + 14 + (i // 5) * col_w
        by = ay + 36 + (i % 5) * 19
        draw.text((bx, by), "• " + b, font=f_brief, fill=(255, 255, 255))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, format="PNG", optimize=False)
    print(f"wrote {out} ({os.path.getsize(out)} bytes)")


if __name__ == "__main__":
    main()

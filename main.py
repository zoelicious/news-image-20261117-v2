#!/usr/bin/env python3
"""news-image-20261117 v2 — user account entry (@zoelicious4843).

One-day world-news front page for Tuesday 17 November 2026, drawn
programmatically with Pillow (no text-to-image: every glyph is rendered
from the story list below, so spelling and numbers are exact).

Layout follows ad-doc-v2.md: giant serif masthead, 3-panel hero row
(Kerch bridge / Iran-Bahrain-Qeshm map / Quad Manila flags), 10 numbered
cards (nos. 4-13), a world map with numbered pins 1-13 + dots 14-43 and
a region legend, and a numbered "ALSO ON TUESDAY 17 NOVEMBER" list of
briefs 14-43. 43 stories total. Palette: cream paper, black ink, red
accent, one muted colour per region.

Deterministic: no randomness, no clock, no network, no dict-order
dependence. Running main.py twice (from any cwd) writes identical bytes.
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 26
CW = W - 2 * MARGIN  # 972 content width

# ---- palette (ad-doc-v2.md section 5) ----
PAPER = (247, 242, 230)
INK = (17, 17, 17)
RED = (179, 39, 30)
FAINT = (233, 226, 210)
LINE = (17, 17, 17)
GREY_TXT = (90, 84, 74)
SKY = (186, 214, 232)
SEA = (146, 190, 214)
LAND = (238, 222, 186)
REGION = {
    "EUROPE": (47, 93, 138),
    "MIDDLE EAST": (198, 122, 46),
    "ASIA": (107, 78, 155),
    "AFRICA": (62, 122, 78),
    "AMERICAS": (169, 50, 38),
    "OCEANIA": (46, 125, 123),
    "GLOBAL": (107, 107, 107),
    "RUSSIA": (47, 93, 138),
    "US": (169, 50, 38),
}

# ---- fonts (system fonts present in the build VM) ----
F_SERIF_BLACK = "/usr/share/fonts/truetype/noto/NotoSerifDisplay-Black.ttf"
F_SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
F_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
F_SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
F_SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


# ---- story data (ad-doc-v2.md; facts/numbers unchanged) ----
# (number, region, topic, headline, deck, caption)
CARDS = [
    (1, "EUROPE", "UKRAINE WAR",
     "Ukraine says a Crimean Bridge road span fell into the sea",
     "Second strike in two days; Zelensky hails an \u201cunprecedented operation\u201d. The Kremlin vows to rebuild.",
     "KERCH STRAIT \u00b7 STRUCK FOR A SECOND DAY"),
    (2, "MIDDLE EAST", "IRAN WAR",
     "Iran sends drones at a US radar in Bahrain; US hits back",
     "Bahrain and the US say all were downed; US jets then strike Qeshm. Iran says tankers hit mines in Hormuz.",
     "STRAIT OF HORMUZ \u00b7 DRONES DOWNED, US STRIKES"),
    (3, "ASIA", "DIPLOMACY",
     "Trump holds his first Quad summit, in Manila",
     "The four unveil critical-minerals deals; Putin reaches Shenzhen for Thursday\u2019s talks with Trump and Xi.",
     "NEW CRITICAL-MINERALS DEALS"),
    (4, "AFRICA", "HEALTH",
     "Ebola cases in DR Congo top 11,000, WHO says",
     "Cases more than doubled in three months; about 5,400 have died.",
     "DR CONGO \u00b7 EBOLA"),
    (5, "GLOBAL", "CLIMATE",
     "COP31 divided over a fossil-fuel phase-out",
     "Nations weigh the first draft; the Antalya talks end Friday.",
     "COP31 ANTALYA \u00b7 ENDS FRI"),
    (6, "AMERICAS", "HEALTH",
     "US, Mexico and Bolivia lose measles-free status",
     "PAHO cites a year of spread; the US has 5,700+ cases in 2026.",
     "MEASLES-FREE STATUS REVOKED"),
    (7, "US", "BUSINESS",
     "Nvidia\u2019s quarterly sales double to $115.8bn",
     "Reported after the close. Earlier the Dow fell 849 points (-1.6%).",
     "NVIDIA QUARTER \u00b7 WALL STREET"),
    (8, "MIDDLE EAST", "GAZA",
     "Gaza truce at risk of collapse, UN is told",
     "Board of Peace report; UN agencies say 1.4m face acute hunger.",
     "GAZA \u00b7 WINTER AID HELD UP"),
    (9, "ASIA", "POLITICS",
     "Mongolia\u2019s president says he will resign",
     "Kh\u00fcrels\u00fckh denies a $25m bribe claim; parliament must accept.",
     "ULAANBAATAR \u00b7 GRAFT CLAIM DENIED"),
    (10, "EUROPE", "POLITICS",
     "Serbia\u2019s student-led majority takes its seats",
     "Student List holds 140 of 250; Vu\u010di\u0107\u2019s party goes into opposition.",
     "BELGRADE \u00b7 PARLIAMENT SWORN IN"),
    (11, "ASIA", "LABOUR",
     "Bangladesh police tear-gas garment workers",
     "They want Tk 30,000 a month, up from 12,500; 37 factories shut.",
     "DHAKA \u00b7 SAVAR - GAZIPUR"),
    (12, "RUSSIA", "AIR CRASH",
     "Russian An-12 crash in Siberia kills all 19",
     "The air force plane came down near Kemerovo; a fault is suspected.",
     "KEMEROVO \u00b7 ALL 19 ABOARD KILLED"),
    (13, "AFRICA", "JUSTICE",
     "Mozambique puts opposition leader on trial",
     "Ven\u00e2ncio Mondlane faces 5 charges over deadly 2024 protests.",
     "MAPUTO \u00b7 SUPREME COURT"),
]

BRIEFS = [
    (14, "Russia", "says it downed a record 1,441 drones overnight."),
    (15, "Kyiv", "missiles hit the North and South Dnipro bridges."),
    (16, "UN", "Ukraine\u2019s civilian deaths this year top all of 2025."),
    (17, "Prague", "two trains collide; 46 people injured."),
    (18, "France", "public-sector strike; 146,000 march (CGT: 500,000)."),
    (19, "Poland", "Tusk\u2019s government survives a no-confidence vote."),
    (20, "Germany", "Deutsche Bank shares fall after a huge data leak."),
    (21, "Moldova", "shuts its airspace as a drone nears Chi\u015fin\u0103u."),
    (22, "Turkey", "police seize opposition broadcaster S\u00f6zc\u00fc TV."),
    (23, "Football", "Norway win 3-2 in Denmark; Haaland scores twice."),
    (24, "Vatican", "Pope Leo XIV returns from South America tour."),
    (25, "UK", "sanctions 8 settlement firms and Tzav 9."),
    (26, "Israel", "Eisenkot ally Matan Kahana elected speaker, 66-52."),
    (27, "West Bank", "settlers kill a woman, 72, near Jericho."),
    (28, "Oman", "Iran\u2019s Aragchi holds shipping-safety talks."),
    (29, "India", "Cyclone Akvan strengthens; Odisha evacuates."),
    (30, "India", "bus falls into an Uttarakhand gorge, 8 dead."),
    (31, "Japan", "protests a Russian airspace intrusion near Fukuoka."),
    (32, "China-Canada", "more tariff cuts after Carney-Xi talks."),
    (33, "Malaysia", "Macron visit seals a strategic partnership."),
    (34, "Thailand", "pledges to scrap tariffs on US goods."),
    (35, "South Korea", "IMF lifts 2026 growth forecast to 3.9%."),
    (36, "Football", "India beat Pakistan 2-1 in SAFF final."),
    (37, "Kenya", "WFP aids 30,000 who fled Ethiopia clashes."),
    (38, "Football", "Togo beat Algeria 3-0 in AFCON qualifier."),
    (39, "Haiti", "Aristide\u2019s party will field no candidates."),
    (40, "US Senate", "Van Hollen challenges Schumer for leader."),
    (41, "Australia", "eases planned backpacker visa curbs."),
    (42, "Darwin", "M6.6 quake off Indonesia felt; no tsunami."),
    (43, "Apple", "Pay, iCloud and App Store outage; not a hack."),
]

# (number, lon, lat) for map pins 1-13
PINS = [
    (1, 37.0, 45.3), (2, 50.5, 26.2), (3, 121.0, 14.6), (4, 23.0, -2.0),
    (5, 30.7, 36.9), (6, -100.0, 40.0), (7, -122.0, 37.4), (8, 34.5, 31.5),
    (9, 106.0, 47.0), (10, 21.0, 44.0), (11, 90.4, 23.8), (12, 86.0, 55.0),
    (13, 32.6, -25.9),
]
PIN_REGION = {1: "EUROPE", 2: "MIDDLE EAST", 3: "ASIA", 4: "AFRICA",
              5: "GLOBAL", 6: "AMERICAS", 7: "US", 8: "MIDDLE EAST",
              9: "ASIA", 10: "EUROPE", 11: "ASIA", 12: "RUSSIA",
              13: "AFRICA"}
# (lon, lat) dots for briefs 14-43, in brief order
DOTS = [
    (37.6, 55.7), (30.5, 50.4), (30.5, 50.4), (14.4, 50.1), (2.35, 48.85),
    (21.0, 52.2), (8.7, 50.1), (28.8, 47.0), (32.85, 39.9), (12.5, 55.7),
    (12.5, 41.9), (-0.1, 51.5), (35.2, 31.8), (35.45, 31.85), (58.4, 23.6),
    (85.0, 20.0), (79.0, 30.0), (130.4, 33.6), (116.4, 39.9), (101.7, 3.1),
    (100.5, 13.75), (127.0, 37.5), (77.0, 28.0), (36.8, -1.3), (1.2, 6.1),
    (-72.3, 18.5), (-77.0, 38.9), (149.1, -35.3), (130.8, -12.5),
    (-122.0, 37.3),
]


# ---- text helpers ----
def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, fnt, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def fit_font(path, text, size, max_w):
    """Largest size <= `size` whose text fits max_w."""
    s = size
    while s > 10:
        f = font(path, s)
        if ImageDraw.Draw(Image.new("RGB", (8, 8))).textlength(text, font=f) <= max_w:
            return f
        s -= 1
    return font(path, s)


def badge(draw, cx, cy, r, number, fill):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill,
                 outline=(255, 255, 255), width=1)
    f = font(F_SANS_BOLD, max(8, int(r * 1.05)))
    t = str(number)
    tw = draw.textlength(t, font=f)
    th = f.getbbox(t)[3] - f.getbbox(t)[1]
    draw.text((cx - tw / 2, cy - th / 2 - 1), t, font=f, fill=(255, 255, 255))


def kicker_line(draw, x, y, number, region, topic, size=11):
    """Red numbered badge + red caps 'REGION · TOPIC' kicker."""
    badge(draw, x + 8, y + 7, 8, number, RED)
    f = font(F_SANS_BOLD, size)
    draw.text((x + 20, y), f"{region} · {topic}", font=f, fill=RED)


# ---- hero illustrations (flat diagrams, drawn, not generated) ----
def hero_kerch(draw, x, y, w, h):
    """Panel 1: Kerch Strait bridge, broken span falling into the sea."""
    draw.rectangle([x, y, x + w, y + h], fill=SKY)
    draw.rectangle([x, y + h - 30, x + w, y + h], fill=SEA)
    for i in range(5):  # wave ticks
        wx = x + 12 + i * (w - 24) // 4
        draw.arc([wx, y + h - 26, wx + 22, y + h - 14], 0, 180, fill=(255, 255, 255), width=2)
    # bridge deck: left span, gap, right span
    deck_y = y + h - 52
    draw.rectangle([x, deck_y, x + int(w * 0.44), deck_y + 7], fill=INK)
    draw.rectangle([x + int(w * 0.62), deck_y, x + w, deck_y + 7], fill=INK)
    for px in (x + 18, x + int(w * 0.22), x + int(w * 0.38),
               x + int(w * 0.70), x + int(w * 0.88)):
        draw.rectangle([px, deck_y + 7, px + 5, y + h - 30], fill=INK)
    # broken span tilting into the sea
    draw.polygon([(x + int(w * 0.44), deck_y + 2),
                  (x + int(w * 0.60), deck_y + 16),
                  (x + int(w * 0.57), deck_y + 24),
                  (x + int(w * 0.42), deck_y + 10)], fill=(60, 60, 60))
    # smoke + blast
    for (sx, sy, sr) in ((0.52, 0.30, 13), (0.57, 0.22, 16), (0.62, 0.30, 11)):
        draw.ellipse([x + int(w * sx) - sr, y + int(h * sy) - sr,
                      x + int(w * sx) + sr, y + int(h * sy) + sr],
                     fill=(110, 110, 110))
    draw.polygon([(x + int(w * 0.52), deck_y - 4), (x + int(w * 0.55), deck_y - 16),
                  (x + int(w * 0.58), deck_y - 4)], fill=(255, 176, 32))
    # jets
    for jx in (0.10, 0.82):
        jxx, jyy = x + int(w * jx), y + 16
        draw.polygon([(jxx, jyy), (jxx + 16, jyy + 4), (jxx, jyy + 8)], fill=INK)
    f = font(F_SANS_BOLD, 10)
    draw.text((x + 8, y + 8), "CRIMEA", font=f, fill=INK)
    draw.text((x + w - 52, y + 8), "RUSSIA", font=f, fill=INK)


def hero_gulf(draw, x, y, w, h):
    """Panel 2: Strait of Hormuz — Iran above, Gulf water, Bahrain/Qeshm."""
    draw.rectangle([x, y, x + w, y + h], fill=LAND)
    sea = [(x, y + int(h * 0.42)), (x + int(w * 0.30), y + int(h * 0.30)),
           (x + int(w * 0.62), y + int(h * 0.38)), (x + w, y + int(h * 0.30)),
           (x + w, y + h - 16), (x + int(w * 0.55), y + h - 8),
           (x + int(w * 0.30), y + h - 20), (x, y + h - 12)]
    draw.polygon(sea, fill=SEA)
    f = font(F_SANS_BOLD, 10)
    draw.text((x + int(w * 0.42), y + 8), "IRAN", font=f, fill=INK)
    draw.text((x + 8, y + int(h * 0.70)), "BAHRAIN", font=f, fill=INK)
    draw.text((x + int(w * 0.66), y + int(h * 0.62)), "QESHM", font=f, fill=INK)
    draw.text((x + w - 62, y + h - 26), "HORMUZ", font=f, fill=INK)
    # dashed drone path Iran -> Bahrain
    bx, by = x + int(w * 0.18), y + int(h * 0.58)
    ix, iy = x + int(w * 0.45), y + int(h * 0.22)
    for t in range(0, 11):
        px = bx + (ix - bx) * t / 10
        py = by + (iy - by) * t / 10
        if t % 2 == 0:
            draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
    draw.text((bx + 14, by - 18), "X", font=font(F_SANS_BOLD, 14), fill=RED)
    # US strike marker on Qeshm
    qx, qy = x + int(w * 0.72), y + int(h * 0.60)
    draw.ellipse([qx - 4, qy - 4, qx + 4, qy + 4], fill=(47, 93, 138))
    # tanker
    tx, ty = x + int(w * 0.82), y + int(h * 0.78)
    draw.rectangle([tx, ty, tx + 34, ty + 9], fill=(120, 40, 30))
    draw.rectangle([tx + 6, ty - 7, tx + 14, ty], fill=(120, 40, 30))
    draw.ellipse([tx + 12, ty - 16, tx + 24, ty - 4], fill=(110, 110, 110))


def hero_quad(draw, x, y, w, h):
    """Panel 3: Quad summit — four flags on a table, purple header."""
    draw.rectangle([x, y, x + w, y + h], fill=(232, 226, 244))
    draw.rectangle([x, y, x + w, y + 22], fill=(107, 78, 155))
    f = font(F_SANS_BOLD, 10)
    t = "QUAD LEADERS\u2019 SUMMIT \u00b7 MANILA"
    draw.text((x + (w - draw.textlength(t, font=f)) / 2, y + 5), t,
              font=f, fill=(255, 255, 255))
    # table
    draw.rectangle([x + 12, y + h - 34, x + w - 12, y + h - 22], fill=(122, 84, 52))
    draw.rectangle([x + 22, y + h - 22, x + 28, y + h - 8], fill=(90, 60, 36))
    draw.rectangle([x + w - 28, y + h - 22, x + w - 22, y + h - 8], fill=(90, 60, 36))
    flags = [
        ("US", [(178, 34, 52), (255, 255, 255), (178, 34, 52), (255, 255, 255),
                (178, 34, 52), (255, 255, 255), (178, 34, 52)]),
        ("INDIA", [(255, 153, 51), (255, 255, 255), (19, 136, 8)]),
        ("JAPAN", [(255, 255, 255)]),
        ("AUSTRALIA", [(0, 32, 91)]),
    ]
    fw, fh = 52, 30
    gap = (w - 4 * fw) // 5
    for i, (name, stripes) in enumerate(flags):
        fx = x + gap + i * (fw + gap)
        fy = y + 34
        draw.rectangle([fx, fy, fx + fw, fy + fh], outline=INK, width=1)
        sh = fh / len(stripes)
        for j, col in enumerate(stripes):
            draw.rectangle([fx, fy + j * sh, fx + fw, fy + (j + 1) * sh], fill=col)
        if name == "US":
            draw.rectangle([fx, fy, fx + 20, fy + 14], fill=(0, 32, 91))
        if name == "INDIA":
            draw.ellipse([fx + 22, fy + 11, fx + 30, fy + 19],
                         outline=(0, 32, 91), width=1)
        if name == "JAPAN":
            draw.ellipse([fx + 20, fy + 9, fx + 32, fy + 21], fill=(188, 0, 45))
        if name == "AUSTRALIA":
            draw.ellipse([fx + 34, fy + 6, fx + 40, fy + 12], fill=(255, 255, 255))
            draw.ellipse([fx + 10, fy + 18, fx + 16, fy + 24], fill=(255, 255, 255))
        lf = font(F_SANS_BOLD, 9)
        lt = name
        draw.text((fx + (fw - draw.textlength(lt, font=lf)) / 2, fy + fh + 4),
                  lt, font=lf, fill=INK)


# ---- small card illustrations (flat, one per story 4-13) ----
def mini_ebola(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(240, 232, 214))
    draw.polygon([(x + 14, y + h - 8), (x + 34, y + 10), (x + 54, y + h - 8)],
                 fill=(255, 255, 255), outline=INK)
    draw.rectangle([x + 30, y + 22, x + 38, y + 34], fill=RED)
    draw.rectangle([x + 26, y + 26, x + 42, y + 30], fill=RED)
    f = font(F_SANS_BOLD, 10)
    draw.text((x + w - 78, y + 6), "11,000+ CASES", font=f, fill=RED)
    draw.ellipse([x + w - 22, y + h - 16, x + w - 12, y + h - 6], fill=RED)


def mini_cop(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(214, 232, 226))
    draw.ellipse([x + 10, y + 8, x + 46, y + 44], fill=SEA)
    draw.ellipse([x + 18, y + 14, x + 28, y + 22], fill=(62, 122, 78))
    draw.ellipse([x + 30, y + 26, x + 40, y + 34], fill=(62, 122, 78))
    draw.rectangle([x + w - 22, y + 8, x + w - 14, y + h - 10], fill=(255, 255, 255),
                   outline=INK)
    draw.ellipse([x + w - 25, y + 4, x + w - 11, y + 18], fill=RED)
    f = font(F_SANS_BOLD, 9)
    draw.text((x + 56, y + 8), "DRAFT: PHASE OUT", font=f, fill=INK)
    draw.text((x + 56, y + 20), "FOSSIL FUELS?", font=f, fill=INK)


def mini_measles(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(240, 232, 214))
    flags = [[(178, 34, 52), (255, 255, 255), (178, 34, 52)],
             [(0, 104, 71), (255, 255, 255), (206, 17, 38)],
             [(206, 17, 38), (255, 220, 0), (206, 17, 38)]]
    for i, stripes in enumerate(flags):
        fx = x + 10 + i * 30
        for j, col in enumerate(stripes):
            draw.rectangle([fx, y + 10 + j * 8, fx + 24, y + 18 + j * 8], fill=col)
    for (vx, vy) in ((150, 14), (162, 26), (140, 32), (172, 40)):
        draw.ellipse([x + vx - 4, y + vy - 4, x + vx + 4, y + vy + 4], fill=RED)
        draw.ellipse([x + vx - 1, y + vy - 1, x + vx + 1, y + vy + 1], fill=(255, 255, 255))
    f = font(F_SANS_BOLD, 9)
    draw.text((x + 8, y + h - 12), "US \u00b7 MEXICO \u00b7 BOLIVIA", font=f, fill=INK)


def mini_nvidia(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(20, 20, 20))
    bars = [14, 20, 26, 34, 44]
    for i, bh in enumerate(bars):
        bx = x + 12 + i * 16
        draw.rectangle([bx, y + h - 8 - bh, bx + 11, y + h - 8], fill=(118, 185, 0))
    f = font(F_SANS_BOLD, 11)
    draw.text((x + 100, y + 6), "$115.8BN", font=f, fill=(118, 185, 0))
    draw.text((x + 100, y + 22), "DOW -849", font=f, fill=RED)
    draw.text((x + 100, y + 38), "SALES x2", font=font(F_SANS_BOLD, 9),
              fill=(255, 255, 255))


def mini_gaza(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(238, 228, 205))
    for i in range(3):
        tx = x + 12 + i * 52
        draw.polygon([(tx, y + h - 8), (tx + 20, y + 14), (tx + 40, y + h - 8)],
                     fill=(255, 255, 255), outline=INK)
    f = font(F_SANS_BOLD, 10)
    draw.text((x + 8, y + 4), "1.4M FACE ACUTE HUNGER", font=f, fill=RED)


def mini_mongolia(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(240, 232, 214))
    for i, col in enumerate([(206, 17, 38), (0, 32, 91), (206, 17, 38)]):
        draw.rectangle([x + 12 + i * 16, y + 10, x + 28 + i * 16, y + 38], fill=col)
    draw.text((x + 20, y + 16), "S", font=font(F_SANS_BOLD, 14), fill=(255, 220, 0))
    f = font(F_SANS_BOLD, 10)
    draw.text((x + 68, y + 8), "RESIGNATION", font=f, fill=INK)
    draw.text((x + 68, y + 22), "$25M CLAIM DENIED", font=f, fill=RED)


def mini_serbia(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(232, 226, 244))
    for i in range(9):
        ang = 3.14159 * (0.15 + 0.7 * i / 8)
        cx = x + 50 + int(34 * -math.cos(ang))
        cy = y + 40 - int(30 * math.sin(ang))
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4],
                     fill=RED if i < 6 else (47, 93, 138))
    f = font(F_SANS_BOLD, 10)
    draw.text((x + 96, y + 8), "STUDENTS 140", font=f, fill=RED)
    draw.text((x + 96, y + 22), "VUCIC 103", font=f, fill=(47, 93, 138))


def mini_bangladesh(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(226, 232, 214))
    draw.rectangle([x + 10, y + 18, x + 62, y + h - 8], fill=(120, 120, 120))
    draw.rectangle([x + 56, y + 6, x + 62, y + 18], fill=(90, 90, 90))
    for wx in (72, 86, 100):
        draw.ellipse([x + wx, y + 22, x + wx + 10, y + 32], fill=(255, 205, 170))
        draw.rectangle([x + wx, y + 32, x + wx + 10, y + h - 8], fill=(47, 93, 138))
    f = font(F_SANS_BOLD, 10)
    draw.text((x + 116, y + 8), "TK 30,000", font=f, fill=INK)
    draw.text((x + 116, y + 22), "MINIMUM", font=f, fill=RED)


def mini_plane(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(214, 226, 232))
    px, py = x + 30, y + 26
    draw.polygon([(px, py), (px + 90, py - 6), (px + 110, py + 2),
                  (px + 90, py + 10), (px, py + 8)], fill=(70, 70, 70))
    draw.polygon([(px + 40, py - 2), (px + 55, py - 18), (px + 62, py - 2)],
                 fill=(70, 70, 70))
    draw.polygon([(px + 40, py + 8), (px + 55, py + 22), (px + 62, py + 8)],
                 fill=(70, 70, 70))
    f = font(F_SANS_BOLD, 10)
    draw.text((x + 8, y + 4), "AN-12 \u00b7 SIBERIA", font=f, fill=INK)


def mini_gavel(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(232, 226, 214))
    draw.rectangle([x + 20, y + 16, x + 52, y + 26], fill=(122, 84, 52))
    draw.rectangle([x + 30, y + 26, x + 36, y + 44], fill=(122, 84, 52))
    draw.rectangle([x + 16, y + 44, x + 50, y + 48], fill=(90, 60, 36))
    f = font(F_SANS_BOLD, 10)
    draw.text((x + 66, y + 8), "5 CHARGES", font=f, fill=RED)
    draw.text((x + 66, y + 22), "MAPUTO TRIAL", font=f, fill=INK)


MINI = {4: mini_ebola, 5: mini_cop, 6: mini_measles, 7: mini_nvidia,
        8: mini_gaza, 9: mini_mongolia, 10: mini_serbia, 11: mini_bangladesh,
        12: mini_plane, 13: mini_gavel}


# ---- world map ----
CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-130, 71), (-110, 72), (-95, 80), (-82, 73),
     (-68, 62), (-60, 55), (-55, 47), (-65, 44), (-70, 41), (-76, 35),
     (-81, 26), (-84, 21), (-88, 15), (-92, 15), (-97, 17), (-105, 21),
     (-112, 28), (-120, 34), (-124, 42), (-125, 49), (-135, 58),
     (-150, 60), (-162, 58), (-168, 61)],
    # South America
    [(-79, 9), (-76, 4), (-68, 3), (-60, 5), (-52, 4), (-50, 0),
     (-41, -3), (-35, -8), (-38, -15), (-40, -22), (-48, -27),
     (-54, -33), (-58, -38), (-65, -41), (-68, -50), (-71, -54),
     (-74, -45), (-73, -35), (-71, -25), (-70, -18), (-77, -12),
     (-80, -5), (-81, 1)],
    # Africa
    [(-17, 15), (-16, 20), (-10, 31), (-5, 35), (3, 37), (10, 37),
     (15, 33), (20, 32), (30, 31), (33, 28), (35, 28), (39, 21),
     (43, 12), (48, 11), (51, 11), (48, 2), (41, -2), (40, -10),
     (36, -18), (33, -26), (28, -33), (20, -35), (16, -28), (13, -18),
     (12, -8), (9, 4), (2, 6), (-7, 5), (-13, 8), (-17, 11)],
    # Europe
    [(-10, 36), (-9, 43), (-4, 44), (-2, 48), (0, 50), (2, 51),
     (4, 53), (7, 55), (8, 57), (10, 59), (14, 58), (18, 56),
     (21, 55), (24, 59), (27, 61), (30, 62), (28, 66), (24, 69),
     (19, 70), (14, 70), (10, 64), (5, 60), (3, 58), (-2, 57),
     (-6, 55), (-10, 54), (-10, 49), (-9, 43), (-10, 40)],
    # Asia
    [(30, 62), (38, 66), (48, 68), (58, 69), (68, 72), (78, 73),
     (90, 75), (103, 77), (113, 74), (125, 72), (138, 72), (150, 70),
     (162, 69), (173, 66), (178, 65), (170, 60), (162, 56), (158, 52),
     (150, 59), (142, 50), (140, 44), (137, 39), (130, 35), (127, 38),
     (122, 38), (121, 31), (118, 25), (110, 20), (106, 10), (104, 8),
     (100, 7), (97, 10), (94, 16), (91, 22), (88, 22), (86, 20),
     (80, 13), (77, 8), (75, 10), (72, 20), (68, 22), (62, 25),
     (57, 26), (54, 27), (52, 29), (50, 30), (48, 30), (44, 29),
     (42, 25), (40, 20), (39, 16), (43, 12), (41, 15), (38, 22),
     (36, 29), (36, 36), (33, 36), (30, 36), (27, 37), (26, 40),
     (23, 40), (26, 42), (28, 45), (28, 48), (30, 52), (30, 58)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (118, -35), (124, -33),
     (129, -32), (132, -32), (136, -35), (140, -38), (145, -38),
     (150, -37), (153, -32), (153, -27), (150, -23), (146, -19),
     (142, -11), (137, -12), (132, -11), (126, -14), (122, -17),
     (117, -20), (113, -22)],
]


def project(lon, lat, bx, by, bw, bh):
    """Equirectangular projection into the map box."""
    px = bx + (lon + 180.0) / 360.0 * bw
    py = by + (83.0 - lat) / 138.0 * bh
    return px, py


def draw_map(draw, bx, by, bw, bh):
    draw.rectangle([bx, by, bx + bw, by + bh], fill=(206, 226, 238))
    for poly in CONTINENTS:
        pts = [project(lon, lat, bx, by, bw, bh) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=(180, 164, 132))
    for (lon, lat) in DOTS:
        px, py = project(lon, lat, bx, by, bw, bh)
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=INK)
    for (num, lon, lat) in PINS:
        px, py = project(lon, lat, bx, by, bw, bh)
        badge(draw, px, py, 8, num, REGION[PIN_REGION[num]])


# ---- page composition ----
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    x0 = MARGIN
    x1 = W - MARGIN

    # kicker
    fk = font(F_SANS_BOLD, 11)
    d.text((x0, 12), "THE WORLD\u2019S NEWS IN ONE PICTURE", font=fk, fill=RED)
    right = "43 STORIES \u00b7 6 CONTINENTS \u00b7 ALL FROM TUESDAY"
    d.text((x1 - d.textlength(right, font=fk), 12), right, font=fk, fill=INK)

    # masthead (auto-fit to one line)
    mast = fit_font(F_SERIF_BLACK, "Tuesday 17 November 2026", 64, CW)
    d.text((x0, 28), "Tuesday 17 November 2026", font=mast, fill=INK)
    d.rectangle([x0, 102, x1, 106], fill=INK)
    d.rectangle([x0, 109, x1, 110], fill=INK)

    # ---- hero row: 3 equal panels ----
    hero_y, hero_h = 118, 112
    gap = 10
    pw = (CW - 2 * gap) // 3
    hero_fns = [hero_kerch, hero_gulf, hero_quad]
    for i, card in enumerate(CARDS[:3]):
        px = x0 + i * (pw + gap)
        hero_fns[i](d, px, hero_y, pw, hero_h)
        # caption strip at the bottom of the panel
        d.rectangle([px, hero_y + hero_h - 16, px + pw, hero_y + hero_h],
                    fill=INK)
        cf = font(F_SANS_BOLD, 9)
        cap = card[5]
        while d.textlength(cap, font=cf) > pw - 10 and len(cap) > 10:
            cap = cap[:-1]
        d.text((px + 5, hero_y + hero_h - 13), cap, font=cf, fill=(255, 255, 255))
        # card text under the panel
        ty = hero_y + hero_h + 8
        kicker_line(d, px, ty, card[0], card[1], card[2], size=11)
        hf = font(F_SERIF_BOLD, 19)
        lines = wrap(d, card[3], hf, pw)
        ty = text_block(d, px, ty + 18, lines[:3], hf, INK, 21)
        df = font(F_SERIF, 12)
        dlines = wrap(d, card[4], df, pw)
        text_block(d, px, ty + 2, dlines[:2], df, INK, 15)
    hero_bottom = hero_y + hero_h + 8 + 18 + 63 + 2 + 30
    d.rectangle([x0, hero_bottom + 6, x1, hero_bottom + 7], fill=LINE)

    # ---- grid: 10 cards, 5 cols x 2 rows ----
    gy = hero_bottom + 16
    gw = (CW - 4 * gap) // 5
    gh = 148
    for row in range(2):
        for col in range(5):
            card = CARDS[3 + row * 5 + col]
            cx = x0 + col * (gw + gap)
            cy = gy + row * gh
            MINI[card[0]](d, cx, cy, gw, 54)
            kicker_line(d, cx, cy + 60, card[0], card[1], card[2], size=9)
            hf = font(F_SERIF_BOLD, 14)
            lines = wrap(d, card[3], hf, gw)
            ny = text_block(d, cx, cy + 76, lines[:3], hf, INK, 16)
            df = font(F_SERIF, 11)
            dlines = wrap(d, card[4], df, gw)
            text_block(d, cx, ny + 1, dlines[:2], df, INK, 13)
    grid_bottom = gy + 2 * gh
    d.rectangle([x0, grid_bottom + 2, x1, grid_bottom + 3], fill=LINE)

    # ---- bottom zone: map (left) + briefs (right) ----
    by = grid_bottom + 12
    hf2 = font(F_SANS_BOLD, 12)
    d.text((x0, by), "WHERE IT HAPPENED", font=hf2, fill=RED)
    bx2 = x0 + 448
    d.text((bx2, by), "ALSO ON TUESDAY 17 NOVEMBER", font=hf2, fill=RED)
    map_x, map_y, map_w, map_h = x0, by + 18, 410, 238
    draw_map(d, map_x, map_y, map_w, map_h)
    # legend under the map
    leg_y = map_y + map_h + 8
    lf = font(F_SANS_BOLD, 9)
    lx = map_x
    for name in ("Americas", "Europe", "Middle East", "Asia", "Africa",
                 "Oceania", "Global"):
        col = REGION[name.upper()]
        d.ellipse([lx, leg_y + 1, lx + 8, leg_y + 9], fill=col)
        t = name
        d.text((lx + 11, leg_y), t, font=lf, fill=INK)
        lx += 11 + d.textlength(t, font=lf) + 10
    d.text((map_x, leg_y + 13), "Pins: stories 1-13  \u00b7  dots: 14-43",
           font=font(F_SANS, 9), fill=GREY_TXT)

    # briefs, two columns of 15
    bf = font(F_SANS, 10)
    bfb = font(F_SANS_BOLD, 10)
    col_w = 268
    for ci in range(2):
        bx = bx2 + ci * (col_w + 8)
        yy = by + 18
        for k in range(15):
            num, place, rest = BRIEFS[ci * 15 + k]
            head = f"{num} {place}: "
            lines = wrap(d, head + rest, bf, col_w)
            # bold the "N Place:" head on the first line only
            first = lines[0]
            head_w = d.textlength(head, font=bfb)
            d.text((bx, yy), head, font=bfb, fill=INK)
            d.text((bx + head_w, yy), first[len(head):], font=bf, fill=INK)
            yy += 12
            for ln in lines[1:]:
                d.text((bx, yy), ln, font=bf, fill=INK)
                yy += 12
            yy += 2
            d.line([bx, yy - 2, bx + col_w, yy - 2], fill=FAINT)

    # ---- footer ----
    fy = H - 22
    d.rectangle([x0, fy - 8, x1, fy - 7], fill=LINE)
    ff = font(F_SANS, 10)
    foot = ("Every story here happened or was first reported on Tuesday "
            "17 November 2026. Disputed claims are attributed.  "
            "Sources: Reuters, AP, AFP, BBC, Al Jazeera, WHO, UN.")
    d.text((x0, fy), foot, font=ff, fill=GREY_TXT)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img = render()
    img.save(os.path.join(out_dir, "entry.png"), format="PNG")
    return 0


if __name__ == "__main__":
    sys.exit(main())

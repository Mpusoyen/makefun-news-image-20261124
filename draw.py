#!/usr/bin/env python3
"""Draw entry.png for make.fun news-image-20261124 (v4).

Design: "THE TUESDAY RECORD" - deep burgundy/oxblood masthead, ivory
paper body, gold accent, near-black ink; red reserved for number
badges, pins and the CLAIM chip family. A complete rebuild of v3:
every pictured story gets a full multi-element scene (subject +
setting + detail/motion), a UTC hour-by-hour timeline strip is added,
the rail carries a field and source per item, and the world map gets
bigger pins plus a Europe zoom inset.

Story facts are v3's verified set, reused verbatim: 33 stories from
Tuesday 24 November 2026. No new facts added. The only clock times
stated are the mechanical UTC close times of the exchanges in
story 1 (06:00 Nikkei, 21:00 Nasdaq) on the timeline strip.

Run: python3 draw.py -> writes entry.png (1024x1024) beside this file.
Python + Pillow only, fully deterministic: no randomness, no network.
"""

import math
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 24
CW = W - 2 * M

BURG = (74, 14, 24)         # burgundy / oxblood masthead + footer
BURG_DK = (52, 9, 17)
PAPER = (250, 246, 236)     # ivory paper body
PAPER_DK = (242, 234, 214)  # scene / band fill
GOLD = (196, 150, 44)
GOLD_LT = (232, 198, 110)
INK = (22, 20, 17)
SOFT = (84, 78, 68)
RED = (163, 22, 33)
RED_BR = (196, 40, 48)
RULE = (22, 20, 17)
HAIR = (216, 206, 182)
CREAM_TX = (250, 244, 228)
MUTED_TX = (216, 190, 168)

REGION_COLORS = {
    "EUROPE": (32, 65, 143),
    "MIDDLE EAST": (156, 43, 43),
    "ASIA": (107, 63, 160),
    "AFRICA": (30, 122, 70),
    "AMERICAS": (15, 118, 110),
    "CLIMATE": (180, 83, 9),
    "ORBIT": (70, 70, 120),
    "OCEANIA": (15, 118, 110),
    "GLOBAL": (74, 70, 62),
}

CHIP_COLORS = {
    "CONFIRMED": (30, 110, 62),
    "OFFICIAL": (32, 65, 143),
    "REPORTED": (172, 78, 8),
    "CLAIM": (163, 22, 33),
}

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
F_SERIF_B = FONT_DIR + "DejaVuSerif-Bold.ttf"
F_SERIF = FONT_DIR + "DejaVuSerif.ttf"
F_SANS_B = FONT_DIR + "DejaVuSans-Bold.ttf"
F_SANS = FONT_DIR + "DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(d, text, fnt, max_w):
    if d.textlength(text, font=fnt) <= max_w:
        return text
    while text and d.textlength(text + "…", font=fnt) > max_w:
        text = text.rsplit(" ", 1)[0] if " " in text else text[:-1]
    return text + "…"


def chip(d, x, y, label, size=8):
    f = font(F_SANS_B, size)
    w = int(d.textlength(label, font=f)) + 9
    d.rectangle([x, y, x + w, y + 13], fill=CHIP_COLORS[label])
    d.text((x + 4, y + 2), label, font=f, fill=(255, 255, 255))
    return w


def chip_w(d, label, size=8):
    return int(d.textlength(label, font=font(F_SANS_B, size))) + 9


def badge(d, x, y, n, r=10):
    d.ellipse([x - r, y - r, x + r, y + r], fill=RED)
    f = font(F_SANS_B, 11 if n < 10 else 9)
    t = str(n)
    d.text((x - d.textlength(t, font=f) / 2, y - 6), t, font=f,
           fill=(255, 255, 255))


# ------------------------------------------------------------- story data
# (place, region, field, chip, source, headline, summary) - pictured 1-13.
# Verbatim from v3.
PICTURED = [
    ("NEW YORK · TOKYO", "AMERICAS", "MARKETS", "CONFIRMED", "Horizon",
     "MARKETS SURGE ON THE HUANG RETURN",
     "Tuesday's trading surged on the return of Nvidia's chief: the "
     "shares leapt about 31%, the Nasdaq closed +6.51%, the S&P 500 "
     "+4.73% and the Nikkei +3.91%."),
    ("POLAND", "EUROPE", "SECURITY", "OFFICIAL", "Reuters",
     "RUSSIAN DRONE CROSSES INTO POLAND",
     "Warsaw called the crossing deliberate, and NATO is adding "
     "AWACS aircraft in response."),
    ("BRUSSELS", "EUROPE", "DIPLOMACY", "OFFICIAL", "Reuters",
     "EU PROPOSES 22ND RUSSIA SANCTIONS",
     "Brussels proposed a 22nd package of sanctions on Russia, "
     "targeting banks, energy and shadow-fleet ships."),
    ("ZAPORIZHZHIA", "EUROPE", "WAR", "REPORTED", "Kyiv Independent",
     "NIGHT STRIKE KILLS 2, WOUNDS 40",
     "An overnight strike hit flats in Zaporizhzhia, killing 2 "
     "people and wounding 40; four of the wounded were children."),
    ("GAZA", "MIDDLE EAST", "AID", "REPORTED", "AP",
     "OXFAM: GAZA IS NOW A 'TOXIC LAND'",
     "Oxfam said contamination now reaches across 99%+ of the "
     "Strip, calling Gaza a 'toxic land'."),
    ("TEHRAN, IRAN", "MIDDLE EAST", "SECURITY", "OFFICIAL", "Al Arabiya",
     "IRAN VOWS TO FIGHT US NAVAL BLOCKADE",
     "Tehran warned it would fight a US naval blockade; Qatar's "
     "prime minister was in Washington."),
    ("KOSHI, NEPAL", "ASIA", "DISASTER", "CONFIRMED", "The Hindu",
     "MAGNITUDE 5.6 QUAKE NEAR CHINA BORDER",
     "A magnitude 5.6 tremor struck Koshi province, in the east "
     "of Nepal near the border with China."),
    ("TIANGONG, ORBIT", "ORBIT", "SPACE", "OFFICIAL", "AP",
     "PAKISTANI ASTRONAUT TO FLY TO TIANGONG",
     "A Pakistani astronaut is to fly to China's Tiangong "
     "station, its first foreign guest."),
    ("BENGHAZI, LIBYA", "AFRICA", "WAR", "CLAIM", "Kyiv Independent",
     "UKRAINE SAYS IT SANK RUSSIAN CORVETTE",
     "Ukraine said it sank the Russian corvette Merkury at "
     "Benghazi; the sinking itself is disputed."),
    ("ADDIS ABABA", "CLIMATE", "SUMMITS", "CONFIRMED", "UN News",
     "COP31 FALLS; FIGHT MOVES TO ADDIS",
     "With no fossil-fuel deal agreed, the climate fight moves "
     "to Addis Ababa, where COP32 must revive it."),
    ("SOUTH KOREA", "ASIA", "EDUCATION", "OFFICIAL", "AP",
     "$375,000 BOUNTY ON AI EXAM CHEATS",
     "South Korea put up rewards of $375,000 to catch students "
     "using AI to cheat in the CSAT exams."),
    ("ITURI, DR CONGO", "AFRICA", "HEALTH", "REPORTED", "UN News",
     "FIGHTING TRAPS EBOLA TEAMS IN ITURI",
     "Fighting near a hospital in Ituri trapped Ebola response "
     "teams for more than 24 hours, halting their work."),
    ("VILLAVICENCIO", "AMERICAS", "SECURITY", "REPORTED", "AP",
     "CAR BOMB ROCKS VILLAVICENCIO",
     "A car bomb in Villavicencio destroyed buildings; no "
     "victims have been confirmed."),
]

# Rail stories 14-33: (place, one-liner, region) - verbatim from v3.
RAIL = [
    ("BERLIN", "Delta system goes to Germany", "EUROPE"),
    ("LISBON", "Cost-of-living rally", "EUROPE"),
    ("NATO", "Russia nuclear satellite alarm", "EUROPE"),
    ("GAZA", "Hamas chief killed", "MIDDLE EAST"),
    ("IRAQ", "Kurdish oilfields taken", "MIDDLE EAST"),
    ("YEMEN", "Houthis: strike killed 17", "MIDDLE EAST"),
    ("MYANMAR", "14 back ICJ genocide ruling", "ASIA"),
    ("SEOUL", "Russian jets enter air zone", "ASIA"),
    ("SOMALIA", "Uganda joint al-Shabaab push", "AFRICA"),
    ("NEW YORK", "Path to erase conviction", "AMERICAS"),
    ("PENNSYLVANIA", "Measles: ninth death", "AMERICAS"),
    ("MEXICO", "'El Chapo' tried at home", "AMERICAS"),
    ("GENEVA", "Gukesh–Sindarov match opens", "EUROPE"),
    ("JANAKPUR", "First India–Nepal express", "ASIA"),
    ("BERLIN", "Zelenskyy urges NATO entry", "EUROPE"),
    ("LEAK", "Russian war dead above 700,000", "EUROPE"),
    ("UN", "AI-risk pact within a year", "AMERICAS"),
    ("US", "Chip firm Megaspeed blacklisted", "AMERICAS"),
    ("WFP", "Wars threaten aid for 7.3m more", "GLOBAL"),
    ("SOLOMONS", "To end China security pact", "OCEANIA"),
]

# Rail field + source per item (stories 14-33), as assigned for v4.
RAIL_META = [
    ("DEFENCE", "Reuters"), ("ECONOMY", "AP"), ("SECURITY", "Reuters"),
    ("WAR", "Al Arabiya"), ("ENERGY", "Reuters"), ("WAR", "Al Arabiya"),
    ("LAW", "AP"), ("SECURITY", "AP"), ("WAR", "AP"),
    ("LAW", "AP"), ("HEALTH", "AP"), ("LAW", "AP"),
    ("SPORT", "The Hindu"), ("TRANSIT", "The Hindu"),
    ("DIPLOMACY", "Kyiv Independent"), ("WAR", "Kyiv Independent"),
    ("TECH", "UN News"), ("TECH", "Reuters"), ("AID", "UN News"),
    ("DIPLOMACY", "AP"),
]

STATS = [
    ("+6.51%", "NASDAQ CLOSE IN\nTUESDAY'S SURGE"),
    ("22ND", "EU SANCTIONS PACKAGE\nPROPOSED ON RUSSIA"),
    ("M5.6", "NEPAL QUAKE, KOSHI\nPROVINCE IN THE EAST"),
    ("$375,000", "BOUNTY ON AI CHEATS\nIN KOREA'S CSAT EXAMS"),
    ("99%+", "OF GAZA CONTAMINATED,\nSAYS OXFAM"),
    ("46", "COUNTIES REACHED BY\nTHE MEASLES OUTBREAK"),
]

TALLY = ("REGION TALLY:  EUROPE 9 · AMERICAS 7 · ASIA 5 · MIDDLE EAST 5 · "
         "AFRICA 3 · CLIMATE 1 · ORBIT 1 · OCEANIA 1 · GLOBAL 1  =  33")

# UTC timeline stops: (axis fraction, daypart, label) - exactly 7 stops.
TIMELINE = [
    (0.02, "OVERNIGHT", "Night strike hits Zaporizhzhia flats"),
    (0.25, "06:00", "Nikkei closes +3.91%"),
    (0.38, "MORNING", "Russian drone crosses into Poland"),
    (0.50, "MIDDAY", "EU proposes 22nd sanctions package"),
    (0.63, "AFTERNOON", "Iran vows to fight US blockade"),
    (0.78, "EVENING", "Korea posts $375,000 AI-cheat bounty"),
    (0.98, "21:00", "Nasdaq closes +6.51%"),
]

# Dot-matrix landmask, 58 cols x 18 rows (lon -180..180, lat 75..-60).
LAND = [
    "   xxxxxxxx                       xxxxxxxxxxxxxxxxxxx       ",
    " xxxxxxxxxxx     xx    x     xxxxxxxxxxxxxxxxxxxxxxxxxxx    ",
    "  xxxxxxxxxx    xxxx  xxxxx xxxxxxxxxxxxxxxxxxxxxxxxxxx     ",
    "   xxxxxxxxx    xxxxxxxxxx  xxxxxxxxxxxxxxxxxxxxxxxxx       ",
    "    xxxxxxx     xxxxxxxxxx xxxxxxxxxxxxxxxxxxxxxxxxxx       ",
    "     xxxxx       xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx         ",
    "     xxxx        xxxxxxxxxxxxxxxxxxx  xxxxxxxxxxx           ",
    "      xxx         xxxxxxxxxxxxxxxxx    xxxxxxxxx            ",
    "      xxxx         xxxxxxxxxxxxxxx      xxxxxxxx  xx        ",
    "       xxxxx        xxxxxxxxxxxxx        xxxxxx  xxxx       ",
    "       xxxxx         xxxxxxxxxxx         xxxxx    x         ",
    "       xxxx          xxxxxxxxx           xxxx    xxxxx      ",
    "       xxxx           xxxxxxx            xxx      xxxxxxx   ",
    "       xxx             xxxxx             xx        xxxxx    ",
    "       xxx              xxx              x          xxx     ",
    "       xx               x                                   ",
    "       xx                                                   ",
    "       x                                                    ",
]
LAND = [row.ljust(58)[:58] for row in LAND]

# Pins for pictured stories 1-13: (number, lon, lat) - verbatim from v3.
PINS = [
    (1, -74, 40), (2, 20, 53), (3, 2, 50), (4, 35, 48), (5, 34, 31),
    (6, 53, 32), (7, 87, 27), (8, 108, 34), (9, 20, 32), (10, 39, 9),
    (11, 127, 37), (12, 29, 2), (13, -74, 4),
]


# ---------------------------------------------------------------- scenes
# Each scene draws inside box (x, y, w, h); flat vector shapes only.
# Every scene: subject + setting + one detail/motion element, >=5 shapes.

def burst(d, cx, cy, r, col):
    for dx, dy in ((0, -1), (.7, -.7), (1, .1), (.6, .8), (-.2, 1),
                   (-.8, .5), (-1, -.2), (-.6, -.8)):
        d.line([(cx, cy), (cx + dx * r, cy + dy * r)], fill=col, width=2)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(250, 180, 60))


def sc_lead(d, x, y, w, h):
    """1 Lead: skyline + rising chart + arrow + candlesticks + ticker."""
    d.rectangle([x, y, x + w, y + h], fill=(226, 236, 214))
    base = y + h - 16
    # skyline silhouette along the bottom
    for bx, bw, bh in ((4, 22, 30), (30, 16, 44), (50, 24, 24), (78, 15, 38),
                       (97, 20, 28), (150, 18, 34), (172, 24, 22),
                       (200, 16, 40), (220, 22, 26), (246, 18, 36),
                       (268, 20, 24)):
        if bx + bw > w - 2:
            continue
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(88, 96, 88))
        for wy in range(base - bh + 4, base - 4, 8):
            d.rectangle([x + bx + 3, wy, x + bx + 6, wy + 3],
                        fill=(240, 200, 90))
    # candlesticks
    for i, (cxo, top, bot) in enumerate(((18, 30, 52), (44, 24, 44),
                                         (70, 18, 38), (96, 12, 30))):
        cxp = x + 120 + cxo
        d.line([(cxp, y + top + 14), (cxp, y + bot + 14)],
               fill=(30, 110, 62), width=2)
        d.rectangle([cxp - 5, y + top + 18, cxp + 5, y + bot + 10],
                    fill=(30, 110, 62))
    # rising chart line with arrowhead
    pts = [(x + 12, base - 34), (x + w * 0.32, base - 52),
           (x + w * 0.50, base - 44), (x + w * 0.70, base - 68),
           (x + w - 14, y + 22)]
    d.line(pts, fill=(30, 110, 62), width=4)
    ax, ay = pts[-1]
    d.polygon([(ax, ay), (ax - 14, ay + 2), (ax - 3, ay + 13)],
              fill=(30, 110, 62))
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(30, 110, 62))
    # ticker band
    d.rectangle([x, y + h - 16, x + w, y + h], fill=(30, 110, 62))
    f = font(F_SANS_B, 10)
    t = "NASDAQ +6.51% · S&P +4.73% · NIKKEI +3.91%"
    d.text((x + (w - d.textlength(t, font=f)) / 2, y + h - 14), t,
           font=f, fill=(255, 255, 255))


def sc_drone(d, x, y, w, h):
    """2 Drone: quadcopter + rotors + patchwork fields + border + radar."""
    d.rectangle([x, y, x + w, y + h], fill=(216, 226, 240))
    base = y + h - 22
    # patchwork fields
    cols = [(168, 190, 120), (196, 178, 110), (150, 176, 130),
            (206, 196, 130)]
    fw = w // 4
    for i in range(4):
        d.rectangle([x + i * fw, base, x + (i + 1) * fw, y + h],
                    fill=cols[i])
        d.line([(x + i * fw, base), (x + i * fw, y + h)], fill=(120, 110, 80))
    # dashed border line across the fields
    for dx in range(4, w - 4, 10):
        d.line([(x + dx, base + 6), (x + dx + 5, base + 6)],
               fill=RED, width=2)
    cx, cy = x + w // 2, y + h // 2 - 10
    # radar arcs below-right of the drone
    for r in (9, 16, 23):
        d.arc([cx + 18 - r, base - 4 - r, cx + 18 + r, base - 4 + r],
              200, 330, fill=(32, 65, 143), width=1)
    # quadcopter: arms, body, 4 rotor ellipses
    d.line([(cx - 17, cy - 11), (cx + 17, cy + 11)], fill=INK, width=3)
    d.line([(cx - 17, cy + 11), (cx + 17, cy - 11)], fill=INK, width=3)
    for dx, dy in ((-17, -11), (17, 11), (-17, 11), (17, -11)):
        d.ellipse([cx + dx - 7, cy + dy - 3, cx + dx + 7, cy + dy + 3],
                  outline=INK, width=2)
    d.rectangle([cx - 6, cy - 5, cx + 6, cy + 5], fill=RED)
    d.ellipse([cx - 2, cy + 5, cx + 2, cy + 9], fill=INK)  # camera pod


def sc_eu(d, x, y, w, h):
    """3 EU sanctions: columned domed building + 12 stars + scroll '22'."""
    d.rectangle([x, y, x + w, y + h], fill=(32, 65, 143))
    cx = x + w // 2
    # arc of 12 stars above the building
    f_star = font(F_SANS_B, 9)
    for i in range(12):
        a = math.radians(180 + i * (180 / 11))
        sx = cx + (w // 2 - 10) * math.cos(a)
        sy = y + 26 + 18 * math.sin(a)
        d.text((sx - 3, sy - 5), "★", font=f_star, fill=(240, 200, 60))
    base = y + h - 8
    # dome + pediment + columns + steps
    d.arc([cx - 13, base - 52, cx + 13, base - 26], 180, 360,
          fill=(232, 228, 210), width=3)
    d.polygon([(cx - 24, base - 38), (cx + 24, base - 38), (cx, base - 48)],
              fill=(232, 228, 210))
    for i in range(4):
        cxx = cx - 21 + i * 14
        d.rectangle([cxx, base - 36, cxx + 5, base - 10],
                    fill=(232, 228, 210))
    d.rectangle([cx - 27, base - 10, cx + 27, base - 6], fill=(210, 206, 190))
    d.rectangle([cx - 30, base - 6, cx + 30, base - 2], fill=(210, 206, 190))
    # scroll / document stamped 22, bottom right
    sx, sy = x + w - 34, y + h - 34
    d.rectangle([sx, sy, sx + 28, sy + 26], fill=(250, 246, 236))
    d.rectangle([sx, sy, sx + 28, sy + 5], fill=GOLD)
    d.text((sx + 5, sy + 9), "22", font=font(F_SANS_B, 12), fill=RED)


def sc_night(d, x, y, w, h):
    """4 Night strike: 3 blocks, lit windows, dark cracked block, burst, moon."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 26, 44))
    # crescent moon
    d.ellipse([x + 6, y + 5, x + 20, y + 19], fill=(240, 230, 190))
    d.ellipse([x + 11, y + 3, x + 24, y + 17], fill=(24, 26, 44))
    base = y + h - 5
    blocks = ((8, 22, 40, True), (34, 18, 54, True), (56, 24, 32, False),
              (84, 14, 44, True))
    for bx, bw, bh, lit in blocks:
        if bx + bw > w - 2:
            bw = w - 2 - bx
        col = (52, 56, 82) if lit else (34, 36, 52)
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=col)
        if lit:
            for wy in range(base - bh + 5, base - 6, 9):
                for wxo in (3, 10):
                    if bx + wxo + 3 < bx + bw:
                        d.rectangle([x + bx + wxo, wy, x + bx + wxo + 3,
                                     wy + 3], fill=(240, 200, 90))
        else:  # cracked corner on the dark block
            d.line([(x + bx + bw - 2, base - bh), (x + bx + bw - 9,
                    base - bh + 8), (x + bx + bw - 4, base - bh + 14)],
                   fill=(10, 10, 16), width=2)
    burst(d, x + w - 18, y + 16, 10, (240, 120, 40))


def sc_toxic(d, x, y, w, h):
    """5 Gaza: cracked earth + 2 barrels + sign on post + skyline + sun."""
    d.rectangle([x, y, x + w, y + h], fill=(238, 226, 190))
    d.ellipse([x + w - 24, y + 6, x + w - 8, y + 22], fill=(230, 160, 40))
    base = y + h - 6
    # ruined skyline silhouette
    for bx, bw, bh in ((2, 14, 20), (18, 10, 28), (30, 16, 16)):
        d.rectangle([x + bx, base - 26 - bh, x + bx + bw, base - 26],
                    fill=(150, 138, 112))
    # cracked earth
    d.polygon([(x + 2, base), (x + w - 2, base), (x + w - 14, base - 24),
               (x + 14, base - 21)], fill=(168, 140, 96))
    for sx, ex in ((14, 30), (38, 52), (58, 76), (24, 40)):
        d.line([(x + sx, base - 18), (x + ex, base - 4)],
               fill=(110, 84, 50), width=1)
    # two barrels
    for bx in (10, 26):
        d.rectangle([x + bx, base - 20, x + bx + 11, base - 6],
                    fill=(120, 110, 60), outline=(80, 74, 40))
        d.line([(x + bx, base - 14), (x + bx + 11, base - 14)],
               fill=(80, 74, 40), width=1)
    # warning sign ON A POST (one element among many)
    px = x + w - 30
    d.line([(px + 7, base - 4), (px + 7, base - 26)], fill=INK, width=2)
    d.polygon([(px + 7, base - 38), (px - 4, base - 24), (px + 18, base - 24)],
              fill=(240, 190, 40), outline=INK)
    d.text((px + 5, base - 33), "!", font=font(F_SANS_B, 10), fill=INK)


def sc_blockade(d, x, y, w, h):
    """6 Iran blockade: warship + waves + 3 buoys + coastline."""
    d.rectangle([x, y, x + w, y + h], fill=(206, 226, 236))
    # coastline top-left
    d.polygon([(x, y), (x + 30, y), (x + 18, y + 14), (x + 8, y + 22),
               (x, y + 26)], fill=(196, 178, 130))
    sea = y + h - 24
    d.rectangle([x, sea, x + w, y + h], fill=(70, 120, 165))
    for wx in range(x + 3, x + w - 12, 16):
        d.arc([wx, sea + 5, wx + 11, sea + 12], 0, 180,
              fill=(220, 240, 250), width=1)
    cx = x + w // 2 - 6  # warship: hull, superstructure, mast
    d.polygon([(cx - 27, sea + 2), (cx + 27, sea + 2), (cx + 19, sea - 6),
               (cx - 19, sea - 6)], fill=(60, 64, 74))
    d.rectangle([cx - 11, sea - 15, cx + 7, sea - 6], fill=(60, 64, 74))
    d.rectangle([cx - 4, sea - 20, cx + 2, sea - 15], fill=(60, 64, 74))
    d.line([(cx + 1, sea - 20), (cx + 1, sea - 29)], fill=(60, 64, 74), width=2)
    d.line([(cx + 1, sea - 25), (cx + 17, sea - 25)], fill=(60, 64, 74), width=2)
    # line of 3 blockade buoys
    for i in range(3):
        bx = x + 12 + i * 30
        by = sea + 13
        d.polygon([(bx, by - 6), (bx + 8, by - 6), (bx + 6, by + 2),
                   (bx + 2, by + 2)], fill=RED_BR)
        d.line([(bx + 4, by - 6), (bx + 4, by - 10)], fill=INK, width=1)


def sc_quake(d, x, y, w, h):
    """7 Nepal quake: 2 peaks + snowcaps + pagoda + seismograph line."""
    d.rectangle([x, y, x + w, y + h], fill=(224, 232, 240))
    base = y + h - 18
    d.polygon([(x + 2, base), (x + w * 0.38, y + 10), (x + w * 0.66, base)],
              fill=(120, 130, 150))
    d.polygon([(x + w * 0.40, base), (x + w * 0.72, y + 18), (x + w - 2, base)],
              fill=(96, 106, 128))
    for px, pw_ in ((w * 0.38, 7), (w * 0.72, 6)):
        py = y + 10 if px < w * 0.5 else y + 18
        d.polygon([(x + px - pw_, py + 9), (x + px, py),
                   (x + px + pw_, py + 9)], fill=(255, 255, 255))
    # pagoda silhouette, right foreground
    gx = x + w - 26
    d.rectangle([gx, base - 14, gx + 16, base], fill=(90, 60, 44))
    d.polygon([(gx - 3, base - 14), (gx + 19, base - 14), (gx + 8, base - 21)],
              fill=(120, 44, 36))
    d.polygon([(gx, base - 20), (gx + 16, base - 20), (gx + 8, base - 26)],
              fill=(120, 44, 36))
    # red seismograph crack line along the ground
    pts = [(x + 5, base + 9), (x + w * 0.26, base + 9), (x + w * 0.34, base + 2),
           (x + w * 0.44, base + 15), (x + w * 0.54, base + 9),
           (x + w - 5, base + 9)]
    d.line(pts, fill=RED, width=2)


def sc_station(d, x, y, w, h):
    """8 Tiangong: core + 2 panel wings + Earth arc + stars + capsule."""
    d.rectangle([x, y, x + w, y + h], fill=(18, 20, 40))
    for sx, sy in ((10, 10), (32, 22), (58, 6), (76, 26), (20, 38), (84, 40)):
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2],
                  fill=(230, 230, 240))
    cy = y + h // 2 - 4
    # solar-panel wings
    for px in (x + 5, x + w - 27):
        for k in range(3):
            d.rectangle([px + k * 8, cy - 11, px + k * 8 + 7, cy + 11],
                        fill=(70, 100, 190), outline=(120, 150, 220))
    d.line([(x + w * 0.28, cy), (x + w * 0.38, cy)], fill=(210, 214, 224), width=3)
    d.line([(x + w * 0.62, cy), (x + w * 0.72, cy)], fill=(210, 214, 224), width=3)
    # station core + dome
    d.rectangle([x + w * 0.38, cy - 6, x + w * 0.62, cy + 6],
                fill=(210, 214, 224))
    d.ellipse([x + w * 0.46, cy - 13, x + w * 0.54, cy - 5],
              fill=(240, 200, 90))
    # capsule approaching on a dotted path
    capx, capy = x + w - 20, y + 12
    for t in (0.25, 0.5, 0.75):
        d.ellipse([capx - 22 * t - 1, capy + 16 * t - 1,
                   capx - 22 * t + 1, capy + 16 * t + 1],
                  fill=(200, 200, 215))
    d.polygon([(capx, capy), (capx + 8, capy + 3), (capx + 7, capy + 9),
               (capx + 1, capy + 9)], fill=(226, 228, 236))
    # Earth arc at the bottom
    d.arc([x - 20, y + h - 30, x + w + 20, y + h + 26], 180, 360,
          fill=(110, 170, 220), width=4)
    d.arc([x - 20, y + h - 26, x + w + 20, y + h + 30], 180, 360,
          fill=(70, 130, 90), width=2)


def sc_ship(d, x, y, w, h):
    """9 Corvette: tilted sinking ship + waves + smoke + periscope wake."""
    d.rectangle([x, y, x + w, y + h], fill=(210, 228, 238))
    sea = y + h - 20
    d.rectangle([x, sea, x + w, y + h], fill=(70, 120, 165))
    for wx in range(x + 3, x + w - 12, 16):
        d.arc([wx, sea + 4, wx + 11, sea + 11], 0, 180,
              fill=(220, 240, 250), width=1)
    cx = x + w // 2
    # hull tilted down to starboard (sinking at the waterline)
    d.polygon([(cx - 28, sea - 2), (cx + 24, sea + 5), (cx + 16, sea - 4),
               (cx - 20, sea - 11)], fill=(52, 56, 66))
    d.rectangle([cx - 15, sea - 20, cx + 1, sea - 10], fill=(52, 56, 66))
    d.line([(cx - 6, sea - 20), (cx - 4, sea - 27)], fill=(52, 56, 66), width=2)
    for r in (3, 6, 9):  # smoke puffs
        d.ellipse([cx - 13 + r, sea - 26 - r * 2, cx - 5 + r,
                   sea - 18 - r * 2], fill=(150, 150, 155))
    # periscope + wake line, lower left
    d.line([(x + 10, sea + 6), (x + 10, sea - 4)], fill=INK, width=2)
    d.line([(x + 10, sea - 4), (x + 16, sea - 4)], fill=INK, width=2)
    d.line([(x + 12, sea + 8), (x + 44, sea + 12)], fill=(220, 240, 250), width=2)
    d.line([(x + 12, sea + 11), (x + 38, sea + 14)], fill=(220, 240, 250), width=1)


def sc_globe(d, x, y, w, h):
    """10 COP/Addis: globe + leaf + flat-roof skyline + sun."""
    d.rectangle([x, y, x + w, y + h], fill=(222, 236, 222))
    d.ellipse([x + w - 22, y + 5, x + w - 8, y + 19], fill=(230, 160, 40))
    base = y + h - 6
    # flat-roof skyline with one tower
    for bx, bw, bh in ((4, 16, 14), (22, 12, 20), (62, 14, 12), (78, 16, 16)):
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(140, 128, 100))
    d.rectangle([x + 40, base - 30, x + 48, base], fill=(120, 108, 84))
    d.rectangle([x + 42, base - 34, x + 46, base - 30], fill=(120, 108, 84))
    # globe with meridian, left of centre
    cx, cy, r = x + 26, y + h // 2 - 6, 17
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(110, 170, 220),
              outline=(40, 90, 140))
    d.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r], outline=(40, 90, 140))
    d.line([(cx - r, cy), (cx + r, cy)], fill=(40, 90, 140), width=1)
    # leaf, right of the globe
    lx, ly = x + w - 40, y + 24
    d.polygon([(lx, ly + 16), (lx + 4, ly), (lx + 16, ly + 2),
               (lx + 12, ly + 14)], fill=(30, 122, 70))
    d.line([(lx + 2, ly + 15), (lx + 13, ly + 3)], fill=(20, 90, 50), width=1)


def sc_phone(d, x, y, w, h):
    """11 Korea exams: desk + paper + phone 'AI' + magnifier + $375K banner."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 228, 240))
    # desk surface
    d.rectangle([x, y + h - 16, x + w, y + h], fill=(168, 132, 92))
    d.line([(x, y + h - 16), (x + w, y + h - 16)], fill=(120, 92, 60), width=2)
    # exam paper with ruled lines + red tick
    px, py = x + 8, y + 10
    d.rectangle([px, py, px + 40, py + 44], fill=(255, 255, 255),
                outline=(150, 146, 138))
    for i in range(5):
        d.line([(px + 5, py + 8 + i * 7), (px + 35, py + 8 + i * 7)],
               fill=(170, 170, 180), width=1)
    d.line([(px + 26, py + 30), (px + 30, py + 36), (px + 37, py + 24)],
           fill=RED, width=2)
    # phone showing AI
    hx, hy = x + w - 34, y + 12
    d.rectangle([hx, hy, hx + 22, hy + 38], fill=(40, 42, 54))
    d.rectangle([hx + 2, hy + 4, hx + 20, hy + 30], fill=(210, 226, 250))
    d.text((hx + 4, hy + 10), "AI", font=font(F_SANS_B, 11), fill=RED)
    # magnifier over the paper
    mx, my = px + 30, py + 26
    d.ellipse([mx - 9, my - 9, mx + 9, my + 9], outline=INK, width=2)
    d.line([(mx + 7, my + 7), (mx + 14, my + 14)], fill=INK, width=3)
    # $375K banner
    d.rectangle([x + 8, y + h - 15, x + 52, y + h - 3], fill=GOLD)
    d.text((x + 12, y + h - 14), "$375K", font=font(F_SANS_B, 9), fill=INK)


def sc_medical(d, x, y, w, h):
    """12 Ebola/Ituri: hospital + roof cross + 2 tents + tape + 2 trees."""
    d.rectangle([x, y, x + w, y + h], fill=(240, 226, 226))
    base = y + h - 8
    # hospital building with cross on its roof
    bx, bw, bh = x + 8, 38, 38
    d.rectangle([bx, base - bh, bx + bw, base], fill=(250, 248, 244),
                outline=(150, 120, 120))
    d.polygon([(bx - 3, base - bh), (bx + bw + 3, base - bh),
               (bx + bw - 6, base - bh - 8), (bx + 6, base - bh - 8)],
              fill=(150, 90, 80))
    cx, cy = bx + bw // 2, base - bh - 4
    d.rectangle([cx - 2, cy - 5, cx + 2, cy + 5], fill=RED)
    d.rectangle([cx - 5, cy - 2, cx + 5, cy + 2], fill=RED)
    for wy in (base - bh + 8, base - bh + 20):
        for wxo in (6, 18, 29):
            d.rectangle([bx + wxo, wy, bx + wxo + 6, wy + 7],
                        fill=(170, 200, 220))
    d.rectangle([bx + 15, base - 14, bx + 23, base], fill=(110, 90, 80))
    # two tents
    for tx in (x + w - 36, x + w - 20):
        d.polygon([(tx, base), (tx + 7, base - 12), (tx + 14, base)],
                  fill=(216, 150, 70))
        d.polygon([(tx + 7, base - 12), (tx + 14, base), (tx + 7, base)],
                  fill=(190, 128, 58))
    # striped barrier tape across the front
    for i in range(9):
        sx = x + 4 + i * 11
        col = RED_BR if i % 2 == 0 else (250, 246, 236)
        d.polygon([(sx, base - 4), (sx + 6, base - 9), (sx + 11, base - 9),
                   (sx + 5, base - 4)], fill=col)
    # two trees
    for tx in (x + w - 44, x + 52):
        d.line([(tx, base), (tx, base - 10)], fill=(100, 76, 44), width=2)
        d.ellipse([tx - 6, base - 20, tx + 6, base - 9], fill=(60, 130, 70))


def sc_bomb(d, x, y, w, h):
    """13 Car bomb: street + car + burst + 2 buildings (one cracked) + dust."""
    d.rectangle([x, y, x + w, y + h], fill=(236, 228, 214))
    base = y + h - 10
    # two buildings with window grids; the right one is cracked
    for bx, bw, bh, cracked in ((4, 24, 44, False), (w - 28, 24, 50, True)):
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(168, 158, 140))
        for wy in range(base - bh + 5, base - 8, 10):
            for wxo in (4, 13):
                d.rectangle([x + bx + wxo, wy, x + bx + wxo + 5, wy + 5],
                            fill=(90, 96, 110))
        if cracked:
            d.line([(x + bx + 16, base - bh), (x + bx + 10, base - bh + 12),
                    (x + bx + 15, base - bh + 22), (x + bx + 9, base - 12)],
                   fill=INK, width=2)
    # street
    d.rectangle([x, base, x + w, y + h], fill=(120, 116, 108))
    for dx in range(6, w - 8, 16):
        d.line([(x + dx, base + 5), (x + dx + 8, base + 5)],
               fill=(240, 230, 200), width=2)
    # car silhouette
    cx = x + w // 2 - 6
    d.polygon([(cx - 21, base), (cx - 19, base - 8), (cx - 8, base - 9),
               (cx - 4, base - 16), (cx + 9, base - 16), (cx + 14, base - 9),
               (cx + 21, base - 8), (cx + 21, base)], fill=(52, 56, 66))
    d.rectangle([cx - 2, base - 15, cx + 7, base - 10], fill=(150, 180, 200))
    for wx in (cx - 11, cx + 11):
        d.ellipse([wx - 4, base - 4, wx + 4, base + 3], fill=INK)
    burst(d, cx + 27, base - 24, 11, (220, 110, 30))
    # dust dots
    for dx, dy in ((18, -6), (30, -12), (-24, -10), (8, -20), (36, -4)):
        d.ellipse([cx + dx - 2, base + dy - 2, cx + dx + 2, base + dy + 2],
                  fill=(178, 164, 140))


SCENES = [sc_drone, sc_eu, sc_night, sc_toxic, sc_blockade, sc_quake,
          sc_station, sc_ship, sc_globe, sc_phone, sc_medical, sc_bomb]


# ---------------------------------------------------------------- layout

def pictured_card(d, x, y, w, h, n, story):
    place, region, field, chip_label, source, head, summ = story
    color = REGION_COLORS[region]
    d.rectangle([x, y, x + w, y + h], fill=(255, 253, 247),
                outline=HAIR, width=1)
    sw = 104
    SCENES[n - 2](d, x + 1, y + 1, sw - 1, h - 2)
    badge(d, x + 13, y + 13, n)
    tx = x + sw + 7
    tw = x + w - tx - 5
    cw_ = chip_w(d, chip_label)
    f_tag = font(F_SANS_B, 10)
    d.text((tx, y + 3), fit(d, place, f_tag, tw - cw_ - 5),
           font=f_tag, fill=color)
    chip(d, x + w - 5 - cw_, y + 3, chip_label)
    f_rf = font(F_SANS, 8)
    d.text((tx, y + 17), f"{region} · {field}", font=f_rf, fill=SOFT)
    src = f"Source: {source}"
    d.text((x + w - 5 - d.textlength(src, font=f_rf), y + 17), src,
           font=f_rf, fill=SOFT)
    f_head = font(F_SERIF_B, 12)
    hy = y + 27
    for line in wrap(d, head, f_head, tw)[:2]:
        d.text((tx, hy), line, font=f_head, fill=INK)
        hy += 12
    f_sum = font(F_SANS, 9)
    sy = y + 52
    for line in wrap(d, summ, f_sum, tw)[:3]:
        d.text((tx, sy), line, font=f_sum, fill=SOFT)
        sy += 10


def draw_timeline(d, y_top):
    """UTC hour-by-hour strip: axis, hour ticks, 7 alternating stops."""
    f_t = font(F_SANS_B, 11)
    d.text((M, y_top), "TUESDAY, HOUR BY HOUR (UTC)", font=f_t, fill=RED)
    axis_y = y_top + 48
    ax0, ax1 = M + 46, W - M - 46
    d.line([(ax0, axis_y), (ax1, axis_y)], fill=INK, width=2)
    f_tick = font(F_SANS, 8)
    for i, hh in enumerate((0, 3, 6, 9, 12, 15, 18, 21, 24)):
        txp = ax0 + (ax1 - ax0) * i / 8
        d.line([(txp, axis_y - 3), (txp, axis_y + 3)], fill=INK, width=1)
        lab = f"{hh:02d}"
        d.text((txp - d.textlength(lab, font=f_tick) / 2, axis_y + 22),
               lab, font=f_tick, fill=SOFT)
    f_dp = font(F_SANS_B, 8)
    f_lb = font(F_SANS, 7)
    for i, (frac, daypart, label) in enumerate(TIMELINE):
        px = ax0 + (ax1 - ax0) * frac
        d.ellipse([px - 4, axis_y - 4, px + 4, axis_y + 4], fill=RED)
        above = (i % 2 == 0)
        lines = wrap(d, label, f_lb, 168)
        block_w = max([d.textlength(daypart, font=f_dp)] +
                      [d.textlength(ln, font=f_lb) for ln in lines])
        lx = min(max(px - block_w / 2, M), W - M - block_w)
        if above:
            ly = axis_y - 13 - (len(lines) * 9 + 10)
            d.line([(px, axis_y - 5), (px, ly + len(lines) * 9 + 12)],
                   fill=RED, width=1)
        else:
            ly = axis_y + 36
            d.line([(px, axis_y + 5), (px, ly - 2)], fill=RED, width=1)
        d.text((lx, ly), daypart, font=f_dp, fill=INK)
        ly2 = ly + 10
        for ln in lines[:2]:
            d.text((lx, ly2), ln, font=f_lb, fill=SOFT)
            ly2 += 9
    return axis_y + 34


def draw_map(d, mx, my, mw, mh):
    cols, rows = 58, 18
    for r in range(rows):
        for c in range(cols):
            if LAND[r][c] == "x":
                px = mx + c * mw / cols
                py = my + r * mh / rows
                d.ellipse([px - 1.7, py - 1.7, px + 1.7, py + 1.7],
                          fill=(178, 168, 140))
    for n, lon, lat in PINS:
        px = mx + (lon + 180) / 360 * mw
        py = my + (75 - lat) / 135 * mh
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=RED)
        f_pin = font(F_SANS_B, 9 if n < 10 else 8)
        t = str(n)
        d.text((px - d.textlength(t, font=f_pin) / 2, py - 5), t,
               font=f_pin, fill=(255, 255, 255))


def draw_europe_inset(d, ix, iy, iw, ih):
    """Enlarged land dots for lon -10..40 / lat 36..60, pins 2, 3, 4."""
    d.rectangle([ix, iy, ix + iw, iy + ih], fill=PAPER_DK, outline=GOLD,
                width=1)
    cols, rows = 58, 18
    for r in range(rows):
        for c in range(cols):
            if LAND[r][c] != "x":
                continue
            lon = -180 + (c + 0.5) * 360 / cols
            lat = 75 - (r + 0.5) * 135 / rows
            if -10 <= lon <= 40 and 36 <= lat <= 60:
                px = ix + (lon + 10) / 50 * iw
                py = iy + (60 - lat) / 24 * ih
                d.ellipse([px - 2.2, py - 2.2, px + 2.2, py + 2.2],
                          fill=(150, 138, 108))
    for n, lon, lat in PINS:
        if n not in (2, 3, 4):
            continue
        px = ix + (lon + 10) / 50 * iw
        py = iy + (60 - lat) / 24 * ih
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED)
        f_pin = font(F_SANS_B, 9)
        t = str(n)
        d.text((px - d.textlength(t, font=f_pin) / 2, py - 5), t,
               font=f_pin, fill=(255, 255, 255))
    f_cap = font(F_SANS_B, 8)
    cap = "EUROPE — 2 · 3 · 4"
    d.text((ix + iw - d.textlength(cap, font=f_cap) - 4, iy + ih - 11),
           cap, font=f_cap, fill=INK)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- 1. Burgundy masthead (0-146) ----
    d.rectangle([0, 0, W, 146], fill=BURG)
    d.rectangle([0, 143, W, 146], fill=GOLD)
    f_name = font(F_SERIF_B, 17)
    d.text((M, 8), "THE TUESDAY RECORD", font=f_name, fill=CREAM_TX)
    f_top = font(F_SANS, 10)
    top_r = "EST. TODAY · ONE PAGE · DRAWN IN CODE · NO PHOTOGRAPHS"
    d.text((W - M - d.textlength(top_r, font=f_top), 12), top_r,
           font=f_top, fill=MUTED_TX)
    f_cnt = font(F_SANS_B, 14)
    cnt = "33 STORIES · 9 REGIONS · EVERY ONE FROM TUESDAY 24 NOVEMBER 2026"
    d.text(((W - d.textlength(cnt, font=f_cnt)) / 2, 32), cnt,
           font=f_cnt, fill=GOLD_LT)
    f_date = font(F_SERIF_B, 50)
    date = "Tuesday 24 November 2026"
    d.text(((W - d.textlength(date, font=f_date)) / 2, 52), date,
           font=f_date, fill=CREAM_TX)
    f_dek = font(F_SERIF, 14)
    dek = ("Markets surge  ·  a Russian drone crosses into Poland  ·  "
           "the climate fight moves to Addis Ababa")
    dek = fit(d, dek, f_dek, CW)
    d.text(((W - d.textlength(dek, font=f_dek)) / 2, 118), dek,
           font=f_dek, fill=(238, 168, 150))

    # ---- 2. Day in numbers + region tally ----
    f_lab = font(F_SANS_B, 11)
    d.text((M, 152), "THE DAY IN NUMBERS", font=f_lab, fill=RED)
    f_tal = font(F_SANS_B, 9)
    d.text((W - M - d.textlength(TALLY, font=f_tal), 153), TALLY,
           font=f_tal, fill=INK)
    col_w = CW // 6
    f_stat = font(F_SERIF_B, 20)
    f_slab = font(F_SANS, 8)
    for i, (num, lab) in enumerate(STATS):
        sx = M + i * col_w
        if i:
            d.line([(sx - 8, 172), (sx - 8, 196)], fill=HAIR, width=1)
        d.text((sx, 168), num, font=f_stat, fill=INK)
        ly = 192
        for line in lab.split("\n"):
            d.text((sx, ly), line, font=f_slab, fill=SOFT)
            ly += 10
    d.rectangle([M, 212, W - M, 214], fill=RULE)

    # ---- 3. UTC timeline ----
    draw_timeline(d, 218)

    # ---- 4. Lead card (story 1, full width, biggest scene) ----
    lx, ly, lw, lh = M, 324, CW, 84
    place, region, field, chip_label, source, head, summ = PICTURED[0]
    d.rectangle([lx, ly, lx + lw, ly + lh], fill=PAPER_DK)
    d.rectangle([lx, ly, lx + 6, ly + lh], fill=RED)
    sc_lead(d, lx + 6, ly, 300, lh)
    badge(d, lx + 19, ly + 13, 1)
    tx = lx + 320
    tw = lx + lw - tx - 10
    f_tag = font(F_SANS_B, 12)
    d.text((tx, ly + 7), f"{place}  ·  {region} · {field}", font=f_tag,
           fill=REGION_COLORS[region])
    chip(d, lx + lw - 10 - chip_w(d, chip_label, 9), ly + 7, chip_label, 9)
    f_lsrc = font(F_SANS, 8)
    lsrc = f"Source: {source} (markets close)"
    d.text((lx + lw - 10 - d.textlength(lsrc, font=f_lsrc), ly + 23),
           lsrc, font=f_lsrc, fill=SOFT)
    d.text((tx, ly + 24), head, font=font(F_SERIF_B, 21), fill=INK)
    f_lead = font(F_SERIF, 13)
    yy = ly + 52
    for line in wrap(d, summ, f_lead, tw)[:2]:
        d.text((tx, yy), line, font=f_lead, fill=SOFT)
        yy += 15

    # ---- 5. Pictured grid: stories 2-13, 3 cols x 4 rows ----
    gx, gy = M, 416
    col_w2 = (CW - 2 * 8) // 3
    row_h, gap = 84, 5
    for i, story in enumerate(PICTURED[1:]):
        r, c = divmod(i, 3)
        pictured_card(d, gx + c * (col_w2 + 8), gy + r * (row_h + gap),
                      col_w2, row_h, i + 2, story)

    # ---- 6. Bottom band: map + Europe inset (left), rail (right) ----
    by = gy + 4 * row_h + 3 * gap + 6  # 773
    d.rectangle([M, by - 6, W - M, by - 4], fill=RULE)
    f_bt = font(F_SANS_B, 11)
    f_bt2 = font(F_SANS, 8)
    d.text((M, by + 2), "WHERE IT HAPPENED", font=f_bt, fill=RED)
    d.text((M + 158, by + 4), "pins match stories 1–13", font=f_bt2,
           fill=SOFT)
    draw_map(d, M, by + 20, 240, 118)
    draw_europe_inset(d, M + 252, by + 20, 132, 118)

    rx = M + 400
    rw = W - M - rx
    d.text((rx, by + 2), "ALSO ON TUESDAY", font=f_bt, fill=RED)
    d.text((rx + 132, by + 4), "stories 14–33", font=f_bt2, fill=SOFT)
    f_rn = font(F_SANS_B, 9)
    f_rt = font(F_SANS, 7)
    col_rw = (rw - 12) // 2
    for i, (place_r, line_r, region_r) in enumerate(RAIL):
        fld, src = RAIL_META[i]
        c, r = divmod(i, 10)
        x = rx + c * (col_rw + 12)
        y = by + 24 + r * 14
        n = i + 14
        d.text((x, y), f"{n}", font=f_rn, fill=RED)
        d.text((x + 17, y + 1),
               fit(d, f"{place_r} — {line_r} · {fld} · {src}", f_rt,
                   col_rw - 17),
               font=f_rt, fill=INK)

    # ---- 7. DATE CHECK footer (burgundy band) ----
    fy = 954
    d.rectangle([0, fy, W, H], fill=BURG)
    d.rectangle([0, fy, W, fy + 3], fill=GOLD)
    fx = M + 8
    fw = CW - 16
    f_dc = font(F_SANS_B, 10)
    d.text((fx, fy + 8),
           "DATE CHECK — Every story above happened or was first reported "
           "on Tuesday 24 November 2026 (UTC).", font=f_dc, fill=CREAM_TX)
    f_lo = font(F_SANS, 9)
    lo = ("LEFT OUT, WITH THEIR REAL DATES: Nvidia reinstates Jensen Huang "
          "as CEO — Mon 23 Nov (background to story 1) · COP31 collapse in "
          "Antalya — Sun 22 Nov (only Tuesday's Addis Ababa fallout is shown)")
    yy = fy + 24
    for line in wrap(d, lo, f_lo, fw)[:2]:
        d.text((fx, yy), line, font=f_lo, fill=MUTED_TX)
        yy += 11
    f_leg = font(F_SANS, 9)
    leg = ("CHIPS: CONFIRMED = 2+ outlets · OFFICIAL = authority on the "
           "record · REPORTED = one outlet · CLAIM = one side's account")
    d.text((fx, yy + 2), leg, font=f_leg, fill=MUTED_TX)
    src_line = ("SOURCES: Reuters · AP · UN News · Kyiv Independent · "
                "Al Arabiya · The Hindu · Horizon")
    d.text((fx, yy + 14), src_line, font=f_leg, fill=MUTED_TX)
    fig = "FIG. 24-11-26 · V4"
    d.text((W - M - 8 - d.textlength(fig, font=f_leg), yy + 14), fig,
           font=f_leg, fill=GOLD_LT)

    img.save("entry.png", optimize=True)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()

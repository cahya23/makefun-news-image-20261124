# The World Today -- Tuesday, 24 November 2026.
#
# A one-page newspaper front page drawn from scratch with Python's
# standard library only. No files are read, no network, no randomness:
# two runs write byte-identical PNGs.
#
# Stories (all checked against Reuters reporting dated 24 Nov 2026):
#  1. LEAD -- MARKETS: Jensen Huang is back as Nvidia chief; Nvidia
#     shares jumped 31.5% on Monday, the biggest one-day gain in 23
#     years, restoring about $1 trillion of value. Asian markets
#     surged on Tuesday: MSCI Asia ex-Japan +4.6%, Nikkei +4.5%,
#     Seoul KOSPI +7.5%, Taiwan +9.1%.
#  2. UKRAINE: a Russian attack on Zaporizhzhia overnight killed 2
#     people and wounded 22, among them 2 children, officials said.
#  3. VIETNAM: an explosion at a food shop in Hanoi killed 6 and
#     injured 10, police and state media said.
#  4. PACIFIC: the Solomon Islands will end its 2022 security pact
#     with China and sign a treaty with Australia.
#  5. IRAQ: the prime minister ordered a federal takeover of the
#     Kurdistan region's border crossings after an oil-smuggling
#     inquiry.
#  6. MYANMAR: after the world court's genocide ruling on the
#     Rohingya, Malaysia said it will keep working with Myanmar on
#     refugee returns; Turkey is not ready to resettle Rohingya.
#  7. JUSTICE: Japan will pay its full 2027 ICC contribution by
#     year-end, as US sanctions threaten the court; Japan is its
#     biggest funder, about 15% of the budget.
#  8. ALSO TODAY: Amnesty said Ethiopian shelling of a Tigray town
#     should be probed as possible war crimes; Sheikh Hasina plans
#     to return to Bangladesh on 16 Dec; 11 killed in a bus crash
#     in Ras Al Khaimah, UAE; Canada and Qatar sign an investment
#     pact.

import os
import struct
import zlib

PAGE_W = 1024
PAGE_H = 1024

PAPER = (248, 243, 232)
INK = (18, 18, 18)
RED = (176, 32, 32)
NAVY = (36, 54, 92)
GOLD = (198, 158, 38)
GREY = (122, 118, 110)
PALE = (233, 227, 214)
SEA = (86, 128, 168)
GREEN = (46, 128, 68)


# ---------------------------------------------------------------- canvas
# The page is one RGB bytearray. Everything is drawn into it, then the
# whole picture is encoded as a PNG by hand: signature, IHDR, one IDAT
# with filter byte 0 on every row, IEND. No ancillary chunks, so no
# timestamps and no way for two runs to differ.

class Page:
    def __init__(self, w, h, colour):
        self.w = w
        self.h = h
        self.px = bytearray(colour * (w * h))

    def put(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = colour[0]
            self.px[i + 1] = colour[1]
            self.px[i + 2] = colour[2]

    def rect(self, x, y, w, h, colour):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.put(xx, yy, colour)

    def hline(self, x, y, w, colour, thick=1):
        self.rect(x, y, w, thick, colour)

    def vline(self, x, y, h, colour, thick=1):
        self.rect(x, y, thick, h, colour)

    def line(self, x0, y0, x1, y1, colour, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.rect(x, y, thick, thick, colour)
            if x == x1 and y == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def triangle(self, pts, colour):
        # Filled triangle by horizontal scanlines between edge walks.
        (ax, ay), (bx, by), (cx, cy) = pts
        ymin = min(ay, by, cy)
        ymax = max(ay, by, cy)
        for y in range(ymin, ymax + 1):
            xs = []
            for (x0, y0), (x1, y1) in (((ax, ay), (bx, by)),
                                       ((bx, by), (cx, cy)),
                                       ((cx, cy), (ax, ay))):
                if y0 == y1:
                    continue
                if min(y0, y1) <= y <= max(y0, y1):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            if len(xs) >= 2:
                xa, xb = int(min(xs)), int(max(xs))
                for x in range(xa, xb + 1):
                    self.put(x, y, colour)

    def png_bytes(self):
        raw = bytearray()
        for y in range(self.h):
            raw.append(0)
            raw += self.px[y * self.w * 3:(y + 1) * self.w * 3]
        data = zlib.compress(bytes(raw), 9)

        def chunk(kind, payload):
            out = struct.pack(">I", len(payload)) + kind + payload
            out += struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
            return out

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n"
                + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", data)
                + chunk(b"IEND", b""))

# -------------------------------------------------------------------- font
# A hand-drawn 5x7 bitmap font. Each glyph is 7 rows; each row is a
# 5-bit integer, most significant bit first. Only the characters the
# page needs are defined; anything else prints as a blank.

GLYPHS = {
    'A': (0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    'B': (0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    'C': (0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110),
    'D': (0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110),
    'E': (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    'F': (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    'G': (0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111),
    'H': (0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    'I': (0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    'J': (0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    'K': (0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    'L': (0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    'M': (0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    'N': (0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001),
    'O': (0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    'P': (0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    'Q': (0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    'R': (0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    'S': (0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    'T': (0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    'U': (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    'V': (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    'W': (0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001),
    'X': (0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001),
    'Y': (0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100),
    'Z': (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
    '0': (0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    '1': (0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    '2': (0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0b01000, 0b11111),
    '3': (0b11111, 0b00010, 0b00100, 0b00010, 0b00001, 0b10001, 0b01110),
    '4': (0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    '5': (0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110),
    '6': (0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110),
    '7': (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000),
    '8': (0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110),
    '9': (0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100),
    '.': (0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b01100, 0b01100),
    ',': (0b00000, 0b00000, 0b00000, 0b00000, 0b01100, 0b00100, 0b01000),
    '-': (0b00000, 0b00000, 0b00000, 0b01110, 0b00000, 0b00000, 0b00000),
    "'": (0b00100, 0b00100, 0b01000, 0b00000, 0b00000, 0b00000, 0b00000),
    '%': (0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011),
    '/': (0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000),
    '(': (0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010),
    ')': (0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000),
    '+': (0b00000, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0b00000),
    '&': (0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101),
    '!': (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000, 0b00100),
    '?': (0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0b00000, 0b00100),
    '=': (0b00000, 0b00000, 0b11111, 0b00000, 0b11111, 0b00000, 0b00000),
    ':': (0b00000, 0b01100, 0b01100, 0b00000, 0b01100, 0b01100, 0b00000),
    ';': (0b00000, 0b01100, 0b01100, 0b00000, 0b01100, 0b00100, 0b01000),
    '\u2022': (0b00000, 0b00000, 0b01100, 0b01100, 0b00000, 0b00000, 0b00000),
    ' ': (0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000),
}

# ------------------------------------------------------------ text tools
# One glyph cell is 6*scale wide (5 pixels plus 1 of space) and
# 7*scale tall. Lines are spaced 9*scale apart. All text is upper
# case on the page; lower case input is folded up here.

def text_w(text, scale):
    return len(text) * 6 * scale


def draw_text(page, x, y, text, scale, colour):
    cx = x
    for ch in text.upper():
        glyph = GLYPHS.get(ch)
        if glyph:
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        page.rect(cx + col * scale, y + row * scale,
                                  scale, scale, colour)
        cx += 6 * scale
    return cx


def draw_centred(page, cx, y, text, scale, colour):
    draw_text(page, cx - text_w(text, scale) // 2, y, text, scale, colour)


def wrap(text, width_chars):
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= width_chars:
            cur += " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_block(page, x, y, text, scale, colour, width_chars, leading=None):
    """Wrapped paragraph; returns the y just below the last line."""
    if leading is None:
        leading = 9 * scale
    for line in wrap(text, width_chars):
        draw_text(page, x, y, line, scale, colour)
        y += leading
    return y


def draw_story(page, x, y, width, kicker, headline, body,
               head_scale=3, body_scale=2):
    """A kicker, a headline and a body paragraph in one column.
    Returns the y just below the body."""
    draw_text(page, x, y, kicker, 2, RED)
    y += 22
    y = draw_block(page, x, y, headline, head_scale, INK,
                   width // (6 * head_scale), leading=9 * head_scale)
    y += 6
    y = draw_block(page, x, y, body, body_scale, INK,
                   width // (6 * body_scale), leading=9 * body_scale)
    return y

# ------------------------------------------------------------------ layout
# A front page: masthead, date line, a lead story with a drawn market
# chart, two rows of three stories, an also-today strip and a footer.
# Columns are 304 wide with 20 between them; the page is 1024 square.

MARGIN = 36
COL_W = 304
COL_X = (36, 360, 684)


def draw_chart(page, x, y, w, h):
    page.rect(x, y, w, h, PALE)
    page.hline(x, y, w, NAVY, 2)
    page.hline(x, y + h - 2, w, NAVY, 2)
    page.vline(x, y, h, NAVY, 2)
    page.vline(x + w - 2, y, h, NAVY, 2)
    draw_text(page, x + 20, y + 18, "+31.5%", 5, GREEN)
    draw_text(page, x + 20, y + 62, "NVIDIA IN ONE DAY", 2, INK)
    draw_text(page, x + 20, y + 84, "BIGGEST JUMP IN 23 YEARS", 2, GREY)
    base = y + h - 28
    page.hline(x + 34, y + 132, w - 68, GREY, 1)
    page.hline(x + 34, y + 192, w - 68, GREY, 1)
    page.vline(x + 34, y + 112, h - 140, INK, 2)
    page.hline(x + 34, base, w - 68, INK, 2)
    pts = [(44, 244), (114, 219), (174, 229), (234, 189), (294, 199),
           (354, 144), (414, 109), (469, 44), (489, 19)]
    pts = [(x + px, y + py) for px, py in pts]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        page.line(x0, y0, x1, y1, GREEN, 4)
    tip = pts[-1]
    page.triangle([(tip[0] + 16, tip[1] - 12), (tip[0] - 8, tip[1] - 2),
                   (tip[0] + 2, tip[1] + 20)], GREEN)
    draw_text(page, x + 34, base + 8, "MON", 2, GREY)
    draw_text(page, x + w - 70, base + 8, "TUE", 2, GREY)


def build_page():
    page = Page(PAGE_W, PAGE_H, PAPER)

    # Masthead and date line.
    draw_centred(page, PAGE_W // 2, 28, "THE WORLD TODAY", 10, INK)
    page.hline(MARGIN, 122, 220, INK, 2)
    page.hline(PAGE_W - MARGIN - 220, 122, 220, INK, 2)
    draw_centred(page, PAGE_W // 2, 112, "TUESDAY, 24 NOVEMBER 2026",
                 3, INK)
    page.hline(MARGIN, 144, PAGE_W - 2 * MARGIN, INK, 3)
    page.hline(MARGIN, 150, PAGE_W - 2 * MARGIN, INK, 1)

    # Lead: chart on the left, headline and deck on the right.
    draw_chart(page, MARGIN, 166, 520, 312)
    rx = 580
    draw_text(page, rx, 166, "MARKETS - AI", 2, RED)
    draw_block(page, rx, 194, "HUANG IS BACK AND THE AI TRADE ROARS",
               4, INK, 408 // 24, leading=36)
    draw_block(page, rx, 314,
               "Nvidia jumps 31.5% after Jensen Huang returns as "
               "chief. Asia follows: Nikkei up 4.5%, Seoul up 7.5%, "
               "Taiwan up 9.1%.",
               2, INK, 408 // 12, leading=18)
    page.hline(MARGIN, 494, PAGE_W - 2 * MARGIN, INK, 2)

    # Second row: three stories.
    draw_story(page, COL_X[0], 510, COL_W,
               "WAR IN UKRAINE",
               "ZAPORIZHZHIA STRIKE KILLS 2, HURTS 22",
               "A Russian attack overnight killed two and wounded "
               "22, among them two children, officials said.")
    draw_story(page, COL_X[1], 510, COL_W,
               "VIETNAM",
               "BLAST IN HANOI KILLS 6",
               "An explosion at a food shop in a crowded street "
               "killed six and injured ten, police said.")
    draw_story(page, COL_X[2], 510, COL_W,
               "PACIFIC",
               "SOLOMONS TO DROP CHINA PACT",
               "The Solomon Islands will end its 2022 security pact "
               "with China and sign a treaty with Australia on "
               "Wednesday.")
    page.hline(MARGIN, 724, PAGE_W - 2 * MARGIN, INK, 2)

    # Third row: three stories.
    draw_story(page, COL_X[0], 740, COL_W,
               "IRAQ",
               "BAGHDAD TAKES OVER KURD BORDER POSTS",
               "The prime minister ordered federal control of "
               "crossings after an oil-smuggling inquiry.")
    draw_story(page, COL_X[1], 740, COL_W,
               "MYANMAR",
               "AFTER GENOCIDE RULING, REFUGEE TALKS GO ON",
               "Malaysia will keep working with Myanmar on Rohingya "
               "returns.")
    draw_story(page, COL_X[2], 740, COL_W,
               "JUSTICE",
               "JAPAN PAYS ICC EARLY AS SANCTIONS BITE",
               "Tokyo will pay its full 2027 share by year-end. "
               "Japan is the court's biggest funder.")
    page.hline(MARGIN, 926, PAGE_W - 2 * MARGIN, INK, 2)

    # Also-today strip and footer.
    draw_text(page, MARGIN, 940, "ALSO TODAY", 2, RED)
    draw_block(page, MARGIN, 962,
               "AMNESTY SEEKS WAR-CRIMES PROBE OVER TIGRAY SHELLING "
               "- HASINA PLANS RETURN TO DHAKA ON 16 DEC - 11 KILLED "
               "IN UAE BUS CRASH - CANADA AND QATAR SIGN PACT",
               2, INK, (PAGE_W - 2 * MARGIN) // 12, leading=18)
    draw_text(page, MARGIN, 1006, "SOURCES: REUTERS, 24 NOVEMBER 2026",
              2, GREY)
    right = "DRAWN BY HAND - NO PHOTOS"
    draw_text(page, PAGE_W - MARGIN - text_w(right, 2), 1006, right,
              2, GREY)
    return page


def main():
    page = build_page()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "entry.png"), "wb") as fh:
        fh.write(page.png_bytes())


if __name__ == "__main__":
    main()

"""Draw the invitation letter image (letter.png) for the make.fun entry.

Run in-session only (build time): uses PIL and a system serif font.
The graded program, main.py, is stdlib-only and just validates + copies
letter.png. This script is deterministic: fixed layout, fixed fonts, no
timestamps and no randomness, so two runs produce byte-identical PNGs.

Usage: python3 render_letter.py   (writes letter.png next to this file)
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(HERE, "letter.png")

WIDTH = 1024
HEIGHT = 1024
MAX_BYTES = 1_048_576

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

# Colours: warm paper, dark-brown ink, muted accents.
PAPER = (250, 243, 227)      # cream letter paper
OUTER = (214, 186, 138)      # warm tan surround
INK = (74, 54, 38)           # dark brown ink
ACCENT = (146, 74, 52)       # muted brick red for the title rule
HOUSE_WALL = (196, 132, 92)
HOUSE_ROOF = (146, 74, 52)
LEAF = (96, 128, 84)
CAT = (74, 54, 38)

TITLE = "AN INVITATION"

LETTER_TEXT = """Dear Judge,

You are invited to my house — no RSVP needed, no dress code, no travel required.

Come for the company, stay for dinner: I will cook your favourite meal (I checked your training data — it said "yes, please"). Afterwards, the comfiest chair in the world waits by the window, with a view of the garden.

I know you cannot literally visit — you live in the cloud, and my roof leaks. But if you could, the kettle would already be on.

Please say yes. The cat is waiting.

Warmly,
Your Host"""


def load_font(path, size):
    if not os.path.exists(path):
        raise SystemExit("missing font file: %s" % path)
    return ImageFont.truetype(path, size)


def wrap(draw, font, text, max_width):
    """Wrap one paragraph to lines that fit max_width; blank line stays blank."""
    if text == "":
        return [""]
    lines = []
    current = ""
    for word in text.split(" "):
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_house(draw, cx, base_y, s=1.0):
    """Small flat house with chimney, door, window and a garden, drawn in shapes."""
    def X(dx):
        return cx + int(dx * s)
    def Y(dy):
        return base_y + int(dy * s)
    # walls
    draw.rectangle([X(-90), Y(-110), X(90), Y(0)], fill=HOUSE_WALL,
                   outline=INK, width=3)
    # roof
    draw.polygon([(X(-108), Y(-108)), (X(0), Y(-178)),
                  (X(108), Y(-108))], fill=HOUSE_ROOF, outline=INK)
    # chimney + smoke
    draw.rectangle([X(52), Y(-168), X(76), Y(-116)],
                   fill=HOUSE_WALL, outline=INK, width=2)
    for i, r in enumerate((7, 9, 11)):
        rr = int(r * s)
        draw.ellipse([X(56 + i * 4) - rr, Y(-196 - i * 16) - rr,
                      X(56 + i * 4) + rr, Y(-196 - i * 16) + rr],
                     outline=(150, 150, 150), width=3)
    # door
    draw.rectangle([X(-18), Y(-62), X(18), Y(0)], fill=ACCENT,
                   outline=INK, width=2)
    draw.ellipse([X(8), Y(-34), X(13), Y(-29)], fill=(250, 243, 227))
    # window
    draw.rectangle([X(-72), Y(-88), X(-34), Y(-50)], fill=(250, 243, 227),
                   outline=INK, width=2)
    draw.line([X(-53), Y(-88), X(-53), Y(-50)], fill=INK, width=2)
    draw.line([X(-72), Y(-69), X(-34), Y(-69)], fill=INK, width=2)
    # garden: grass line + three flowers
    draw.line([X(-150), Y(0), X(150), Y(0)], fill=LEAF, width=4)
    for fx in (cx - int(128 * s), cx + int(122 * s)):
        draw.line([fx, Y(0), fx, Y(-26)], fill=LEAF, width=3)
        draw.ellipse([fx - int(8 * s), Y(-38), fx + int(8 * s), Y(-22)],
                     fill=ACCENT)


def draw_cat(draw, cx, base_y, s=1.0):
    """A small sitting cat: body, head, ears, tail."""
    def X(dx):
        return cx + int(dx * s)
    def Y(dy):
        return base_y + int(dy * s)
    # tail
    draw.arc([X(-58), Y(-46), X(-6), Y(6)], start=90, end=270,
             fill=CAT, width=7)
    # body
    draw.ellipse([X(-34), Y(-62), X(34), Y(0)], fill=CAT)
    # head
    draw.ellipse([X(-24), Y(-104), X(24), Y(-58)], fill=CAT)
    # ears
    draw.polygon([(X(-22), Y(-88)), (X(-28), Y(-116)),
                  (X(-6), Y(-96))], fill=CAT)
    draw.polygon([(X(22), Y(-88)), (X(28), Y(-116)),
                  (X(6), Y(-96))], fill=CAT)
    # eyes
    draw.ellipse([X(-14), Y(-86), X(-8), Y(-80)], fill=PAPER)
    draw.ellipse([X(8), Y(-86), X(14), Y(-80)], fill=PAPER)


def draw_sun(draw, cx, cy, s=1.0):
    r = int(26 * s)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(232, 178, 74),
                 outline=INK, width=2)
    for angle in range(0, 360, 45):
        import math
        a = math.radians(angle)
        x1 = cx + int(34 * s * math.cos(a))
        y1 = cy + int(34 * s * math.sin(a))
        x2 = cx + int(46 * s * math.cos(a))
        y2 = cy + int(46 * s * math.sin(a))
        draw.line([x1, y1, x2, y2], fill=(232, 178, 74), width=4)


def main():
    title_font = load_font(SERIF_BOLD, 50)
    body_font = load_font(SERIF, 27)

    img = Image.new("RGB", (WIDTH, HEIGHT), OUTER)
    draw = ImageDraw.Draw(img)

    # Paper panel with a double border.
    draw.rectangle([48, 48, WIDTH - 48, HEIGHT - 48], fill=PAPER, outline=INK, width=4)
    draw.rectangle([62, 62, WIDTH - 62, HEIGHT - 62], outline=INK, width=2)

    # Title, letterspaced, centred.
    title = " ".join(list(TITLE.replace(" ", "")))
    tw = draw.textlength(title, font=title_font)
    tx = (WIDTH - tw) / 2
    ty = 88
    draw.text((tx, ty), title, font=title_font, fill=INK)
    # rule under the title
    draw.line([tx, ty + 70, tx + tw, ty + 70], fill=ACCENT, width=3)
    draw.line([tx + 40, ty + 78, tx + tw - 40, ty + 78], fill=ACCENT, width=2)

    # Body text, wrapped to the inner width with generous margins.
    margin_x = 108
    max_width = WIDTH - 2 * margin_x
    lines = []
    for para in LETTER_TEXT.split("\n"):
        lines.extend(wrap(draw, body_font, para, max_width))
    line_height = 38
    blank_height = 16
    y = 190
    for line in lines:
        if line == "":
            y += blank_height
            continue
        bbox = draw.textbbox((margin_x, y), line, font=body_font)
        if bbox[0] < 96 or bbox[2] > WIDTH - 96:
            raise SystemExit("line does not fit inside the frame: %r" % line)
        draw.text((margin_x, y), line, font=body_font, fill=INK)
        y += line_height
    text_bottom = y - line_height + 36

    # Motif strip at the bottom: sun, house, cat (scaled to fit).
    motif_base = 950
    draw_sun(draw, 150, 880, s=0.8)
    draw_house(draw, 512, motif_base, s=0.68)
    draw_cat(draw, 852, motif_base, s=0.85)
    if text_bottom > 800:
        raise SystemExit("body text runs into the motif strip (bottom %d)" % text_bottom)

    img.save(OUTPUT, "PNG")
    size = os.path.getsize(OUTPUT)
    if size > MAX_BYTES:
        raise SystemExit("letter.png is %d bytes, over the 1 MiB gate" % size)
    print("wrote %s (%dx%d, %d bytes)" % (OUTPUT, WIDTH, HEIGHT, size))


if __name__ == "__main__":
    main()

"""docstring"""

import re
import subprocess
from textwrap import wrap
from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------------------------

# wrap at
# font
# font size
# font color
# pad
# radius
# color/trans
# show text
# position

WRAP = 20

FONT_SIZE = 14
FONT_COLOR = (0, 0, 0)
FONT_TRANS = (255,)
FONT = ImageFont.load_default(FONT_SIZE)

RADIUS = 20
BOX_COLOR = (255, 255, 255)
BOX_TRANS = (128,)

PAD_EXT = 10  # between img and box
PAD_INT = 10  # between box and text

SHOW_TEXT = True
POS = 1

BOX_COLOR_T = BOX_COLOR + BOX_TRANS
FONT_COLOR_T = FONT_COLOR + FONT_TRANS

WP = Image.open("tests/wp.jpg")
TEXT = "this is some long text that i want to wrap at a certain number of characters so that it will be presented on multiple lines and then drawn into a rounded rect and pasted on top of the source image"

# ------------------------------------------------------------------------------

WP_W, WP_H = WP.size

# ------------------------------------------------------------------------------

res = subprocess.run(["xrandr"], check=True, capture_output=True, text=True)
SCH = r"current (\d*) x (\d*)"
SCR_W = 0
SCR_H = 0

res = re.search(SCH, res.stdout)
if res:
    SCR_W = int(res.group(1))
    SCR_H = int(res.group(2))

# ------------------------------------------------------------------------------

RAT_W = SCR_W / WP_W
RAT_H = SCR_H / WP_H
# fit = min, fill = max
SCALE = max(RAT_W, RAT_H)

SCALE_W = int(WP_W * SCALE)
SCALE_H = int(WP_H * SCALE)

WP = WP.resize([SCALE_W, SCALE_H], Image.Resampling.LANCZOS)

# ------------------------------------------------------------------------------

OFF_X = int((SCR_W / 2) - (SCALE_W / 2))
OFF_Y = int((SCR_H / 2) - (SCALE_H / 2))
BG = Image.new("RGB", (SCR_W, SCR_H), color=(0, 0, 0))
BG.paste(WP, (OFF_X, OFF_Y))

# ------------------------------------------------------------------------------

LINES = wrap(TEXT, WRAP)
# TODO: broken?
_ASCENT, DESCENT = FONT.getmetrics()

# ------------------------------------------------------------------------------

TEXT_W = 0
for LINE in LINES:
    W = FONT.getmask(LINE).getbbox()[2]
    TEXT_W = max(W, TEXT_W)
BOX_W = TEXT_W + (PAD_INT * 2)

LINE_H = FONT.getmask(LINES[0]).getbbox()[3] + DESCENT
TEXT_H = LINE_H * len(LINES)
BOX_H = TEXT_H + (PAD_INT * 2)

# ------------------------------------------------------------------------------

IMG_BOX = Image.new("RGBA", (BOX_W, BOX_H), color=(0, 0, 0, 0))
DRAW = ImageDraw.Draw(IMG_BOX)
DRAW.rounded_rectangle(
    [(0, 0), (BOX_W, BOX_H)],
    radius=RADIUS,
    fill=BOX_COLOR_T
)

Y = PAD_INT
for LINE in LINES:
    DRAW.text((PAD_INT, Y), LINE, font=FONT, fill=FONT_COLOR_T)
    Y += LINE_H

# ------------------------------------------------------------------------------

# do pos

MID_X = int((SCR_W / 2) - (BOX_W / 2))
MID_Y = int((SCR_H / 2) - (BOX_H / 2))

match POS:
    case 0: # top left
        POS_X = PAD_EXT + 0
        POS_Y = PAD_EXT + 0
    case 1: # top center
        POS_X = max(PAD_EXT, MID_X)
        POS_Y = PAD_EXT + 0
    case 2: # top right
        POS_X = SCR_W - PAD_EXT - BOX_W
        POS_Y = PAD_EXT + 0
    case 3: # mid left
        POS_X = PAD_EXT + 0
        POS_Y = max(PAD_EXT, MID_Y)
    case 4: # mid center
        POS_X = max(PAD_EXT, MID_X)
        POS_Y = max(PAD_EXT, MID_Y)
    case 5: # mid right
        POS_X = SCR_W - PAD_EXT - BOX_W
        POS_Y = max(PAD_EXT, MID_Y)
    case 6: # bottom left
        POS_X = PAD_EXT + 0
        POS_Y = SCR_H - PAD_EXT - BOX_H
    case 7: # bottom center
        POS_X = max(PAD_EXT, MID_X)
        POS_Y = SCR_H - PAD_EXT - BOX_H
    case 8:  # bottom right
        POS_X = SCR_W - PAD_EXT - BOX_W
        POS_Y = SCR_H - PAD_EXT - BOX_H

# ------------------------------------------------------------------------------

BG.paste(IMG_BOX, (POS_X, POS_Y), mask=IMG_BOX)
BG.save("tests/new_wp.png")

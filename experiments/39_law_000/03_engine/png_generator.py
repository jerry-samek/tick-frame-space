import glob

import imageio
from PIL import Image, ImageDraw


def heatmap_to_png(text, filename, scale=4):
    lines = text.split("\n")
    w = max(len(line) for line in lines)
    h = len(lines)

    img = Image.new("RGB", (w * scale, h * scale), "black")
    draw = ImageDraw.Draw(img)

    for y, line in enumerate(lines):
        for x, ch in enumerate(line):
            # jednoduché mapování ASCII → barva
            if ch == '.':
                color = (50, 50, 50)
            elif ch == ':':
                color = (80, 80, 80)
            elif ch == '-':
                color = (120, 120, 120)
            elif ch == '=':
                color = (160, 160, 160)
            elif ch == '+':
                color = (200, 200, 120)
            elif ch == '%':
                color = (255, 180, 80)
            elif ch == '@':
                color = (255, 80, 80)
            else:
                color = (255, 255, 255)

            draw.rectangle(
                [x * scale, y * scale, x * scale + scale, y * scale + scale],
                fill=color
            )

    img.save(filename)


def gen_animation():
    frames = []
    for filename in sorted(glob.glob("frames/*.png")):
        frames.append(imageio.imread(filename))

    imageio.mimsave("animation.gif", frames, duration=0.1)

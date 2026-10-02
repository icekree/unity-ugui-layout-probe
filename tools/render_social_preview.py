"""Render an original analytical schematic with Pillow's bundled font.

Run from the repository root; this is presentation tooling, not the JSON CLI.
Numbers describe the fixture's pixels; the drawing magnifies them threefold.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def main():
    image = Image.new("RGB", (1280, 640), "#101b2a")
    draw = ImageDraw.Draw(image)

    def text(x, y, value, size, color="#f4f7fb"):
        draw.text((x, y), value, font=ImageFont.load_default(size=size), fill=color)

    draw.rounded_rectangle((48, 42, 540, 83), radius=12, fill="#25394a")
    text(65, 51, "EXPERIMENTAL / FROZEN REFERENCE", 22, "#7ae2e2")
    text(54, 119, "Unity uGUI", 68)
    text(54, 199, "Layout Probe", 68)
    text(58, 310, "Explicit JSON. Inspectable geometry.", 29)
    text(58, 355, "Seven original scenes / No Unity required", 24, "#becbda")
    text(58, 416, "15 px right overflow", 38, "#ffac8e")
    text(58, 464, "0.75 outside area ratio", 31, "#ffac8e")

    # A 100 x 100 viewport at scale 3, and x=95..115, y=40..60 box.
    x, y, scale = 830, 195, 3
    for offset in range(0, 301, 60):
        draw.line((x+offset, y, x+offset, y+300), fill="#25394a")
        draw.line((x, y+offset, x+300, y+offset), fill="#25394a")
    draw.rectangle((x, y, x+300, y+300), outline="#7ae2e2", width=4)
    left, right = x+95*scale, x+115*scale
    top, bottom = y+40*scale, y+60*scale
    draw.rectangle((left, top, x+300, bottom), fill="#4c7b80")
    draw.rectangle((x+300, top, right, bottom), fill="#a94c45")
    draw.rectangle((left, top, right, bottom), outline="#ffac8e", width=3)
    draw.line((x+300, top-22, right, top-22), fill="#ffac8e", width=3)
    text(1125, 258, "15 px", 23, "#ffac8e")
    text(841, 517, "100 x 100 viewport", 24, "#7ae2e2")
    text(854, 141, "20 x 20 box at (105, 50)", 24, "#becbda")

    draw.line((55, 562, 1224, 562), fill="#344355", width=2)
    text(58, 580, "icekree / MIT", 23, "#7ae2e2")
    text(333, 580, "Native Unity parity unverified / Static overflow is not a runtime defect", 21, "#becbda")
    output = Path(__file__).resolve().parents[1]/"docs/social-preview.png"
    image.save(output, "PNG")
    print(f"{output.name}: {image.width}x{image.height}, {output.stat().st_size} bytes")


if __name__ == "__main__":
    main()

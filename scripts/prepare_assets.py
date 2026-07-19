"""Prepare web-ready cutouts from the supplied VSTAR catalogue artwork."""

from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tmp" / "pdfs"
OUT = ROOT / "assets" / "images"


def white_to_alpha(image: Image.Image, tolerance: float = 82) -> Image.Image:
    """Flood away a light studio background while preserving metallic highlights."""
    rgba = image.convert("RGBA")
    rgb = np.asarray(rgba)[..., :3].astype(np.float32)
    distance = np.sqrt(((255 - rgb) ** 2).sum(axis=2))
    candidate = distance < tolerance
    height, width = candidate.shape
    background = np.zeros((height, width), dtype=bool)
    queue: deque[tuple[int, int]] = deque()

    def seed(y: int, x: int) -> None:
        if candidate[y, x] and not background[y, x]:
            background[y, x] = True
            queue.append((y, x))

    for x in range(width):
        seed(0, x)
        seed(height - 1, x)
    for y in range(height):
        seed(y, 0)
        seed(y, width - 1)
    while queue:
        y, x = queue.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < height and 0 <= nx < width and candidate[ny, nx] and not background[ny, nx]:
                background[ny, nx] = True
                queue.append((ny, nx))

    alpha = np.where(background, 0, 255).astype(np.uint8)
    alpha = Image.fromarray(alpha, "L").filter(ImageFilter.GaussianBlur(0.55))
    rgba.putalpha(alpha)
    return rgba


def crop_cutout(page: int, box: tuple[int, int, int, int], name: str) -> None:
    image = Image.open(SOURCE / f"hi-{page}.png")
    cut = white_to_alpha(image.crop(box))
    alpha = cut.getchannel("A")
    bounds = alpha.point(lambda value: 255 if value > 18 else 0).getbbox()
    if bounds:
        cut = cut.crop(bounds)
    cut.thumbnail((760, 520), Image.Resampling.LANCZOS)
    padding = max(12, round(max(cut.size) * 0.06))
    canvas = Image.new("RGBA", (cut.width + padding * 2, cut.height + padding * 2), (0, 0, 0, 0))
    canvas.alpha_composite(cut, (padding, padding))
    canvas.save(OUT / name, optimize=True)


def prepare_logo() -> None:
    source = Image.open(ROOT / "assets" / "source" / "vstar-logo-source.png")
    mark = source.crop((35, 115, 1215, 860))
    mark = white_to_alpha(mark, tolerance=70)
    bounds = mark.getchannel("A").point(lambda value: 255 if value > 18 else 0).getbbox()
    if bounds:
        mark = mark.crop(bounds)
    mark.thumbnail((640, 360), Image.Resampling.LANCZOS)
    mark.save(OUT / "vstar-logo.png", optimize=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # Product cutouts are maintained as high-resolution generated assets.
    # Do not overwrite them with the original low-resolution catalogue crops.
    prepare_logo()


if __name__ == "__main__":
    main()

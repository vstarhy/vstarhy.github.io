"""Extract the individual brand marks from the supplied brand-board screenshot.

The crop coordinates intentionally avoid the separators and headings.  Near-white
pixels are converted to alpha and the result is trimmed, padded, and enlarged 2x
with a light sharpen so the small source marks remain clean on high-DPI screens.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


LOGOS = [
    ("abb", (35, 96, 178, 158)),
    ("schneider-electric", (188, 96, 336, 158)),
    ("siemens", (346, 96, 494, 158)),
    ("festo", (504, 96, 652, 158)),
    ("smc", (662, 96, 810, 158)),
    ("mitsubishi-electric", (820, 96, 980, 158)),
    ("omron", (35, 158, 178, 217)),
    ("allen-bradley", (188, 158, 336, 217)),
    ("ifm", (346, 158, 494, 217)),
    ("panasonic", (504, 158, 652, 217)),
    ("pepperl-fuchs", (662, 158, 810, 217)),
    ("turck", (820, 158, 980, 217)),
    ("sick", (35, 217, 178, 278)),
    ("ckd", (188, 217, 336, 278)),
    ("airtac", (346, 217, 494, 278)),
    ("skf", (504, 217, 652, 278)),
    ("nsk", (662, 217, 810, 278)),
    ("fag", (820, 217, 980, 278)),
    ("ina", (35, 278, 178, 340)),
    ("ntn", (188, 278, 336, 340)),
    ("timken", (346, 278, 494, 340)),
]


def remove_white_background(image: Image.Image) -> Image.Image:
    rgb = np.asarray(image.convert("RGB"), dtype=np.float32)
    min_channel = rgb.min(axis=2)
    alpha = np.clip(255.0 - min_channel, 0, 255)
    alpha[alpha < 7] = 0

    # Reverse the white matte used in the screenshot's anti-aliased edges.
    opacity = alpha[..., None] / 255.0
    foreground = np.zeros_like(rgb)
    visible = opacity[..., 0] > 0
    foreground[visible] = np.clip(
        (rgb[visible] - 255.0 * (1.0 - opacity[visible])) / opacity[visible],
        0,
        255,
    )

    rgba = np.dstack((foreground, alpha)).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def trim_and_polish(image: Image.Image) -> Image.Image:
    alpha = image.getchannel("A")
    bbox = alpha.point(lambda value: 255 if value > 8 else 0).getbbox()
    if bbox is None:
        raise ValueError("Crop did not contain a visible logo")

    image = image.crop(bbox)
    padded = Image.new("RGBA", (image.width + 4, image.height + 4), (0, 0, 0, 0))
    padded.alpha_composite(image, (2, 2))
    enlarged = padded.resize((padded.width * 3, padded.height * 3), Image.Resampling.LANCZOS)
    return enlarged.filter(ImageFilter.UnsharpMask(radius=0.7, percent=85, threshold=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    source = Image.open(args.source).convert("RGB")
    if source.size != (984, 341):
        raise ValueError(f"Expected a 984x341 source image, received {source.size}")

    args.output.mkdir(parents=True, exist_ok=True)
    for name, box in LOGOS:
        logo = trim_and_polish(remove_white_background(source.crop(box)))
        logo.save(
            args.output / f"{name}.webp",
            format="WEBP",
            quality=90,
            method=6,
            exact=True,
        )
        print(f"{name:22} {logo.width:>3}x{logo.height:<3}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

"""Generate the app icon set from app/src/assets/icon.svg."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover - runtime dependency check
    raise SystemExit("Pillow is required to generate icons: pip install Pillow") from exc


ASSETS_DIR = Path(__file__).resolve().parent
SRC_DIR = ASSETS_DIR.parent
APP_DIR = SRC_DIR.parent
REPO_DIR = APP_DIR.parent

RESAMPLING = getattr(Image, "Resampling", Image).LANCZOS
INKSCAPE = shutil.which("inkscape")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the repo icon assets from the source SVG.",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=ASSETS_DIR / "icon.svg",
        help="Path to the source SVG. Defaults to app/src/assets/icon.svg.",
    )
    return parser.parse_args()


def run(command: list[str]) -> None:
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode == 0:
        return

    message = completed.stderr.strip() or completed.stdout.strip() or "unknown error"
    raise RuntimeError(f"command failed: {' '.join(command)}\n{message}")


def render_svg(svg_path: Path, size: int) -> Image.Image:
    if not INKSCAPE:
        raise RuntimeError("inkscape is required to render the source SVG")

    with tempfile.TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / f"icon-{size}.png"
        run(
            [
                INKSCAPE,
                str(svg_path),
                f"--export-filename={output}",
                f"--export-width={size}",
                f"--export-height={size}",
            ]
        )
        return Image.open(output).convert("RGBA")


def square_canvas(master: Image.Image, canvas_size: int, scale: float) -> Image.Image:
    icon_size = max(1, round(canvas_size * scale))
    icon = master.resize((icon_size, icon_size), RESAMPLING)
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    offset = ((canvas_size - icon_size) // 2, (canvas_size - icon_size) // 2)
    canvas.alpha_composite(icon, offset)
    return canvas


def canvas_with_centered_icon(
    master: Image.Image,
    width: int,
    height: int,
    icon_size: int,
) -> Image.Image:
    icon = master.resize((icon_size, icon_size), RESAMPLING)
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    offset = ((width - icon_size) // 2, (height - icon_size) // 2)
    canvas.alpha_composite(icon, offset)
    return canvas


def save_png(image: Image.Image, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, format="PNG", optimize=True)


def save_ico(master: Image.Image, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    master.save(
        destination,
        format="ICO",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )


def save_icns(master: Image.Image, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    append_images = [
        master.resize((size, size), RESAMPLING)
        for size in (32, 64, 128, 256, 512)
    ]
    master.save(
        destination,
        format="ICNS",
        append_images=append_images,
    )


def generate_png_assets(base_master: Image.Image) -> None:
    direct_outputs = {
        ASSETS_DIR / "icon.png": 512,
        ASSETS_DIR / "icon256.png": 256,
    }
    for destination, size in direct_outputs.items():
        save_png(base_master.resize((size, size), RESAMPLING), destination)

    padded_outputs = {
        ASSETS_DIR / "icon-mac.png": (512, 0.825),
        APP_DIR / "stage" / "icon.png": (512, 0.705),
        APP_DIR / "stage" / "icon-large.png": (512, 0.825),
        APP_DIR / "appearance" / "boot" / "icon.png": (512, 0.705),
        APP_DIR / "electron" / "icon.png": (512, 0.705),
    }
    for destination, (size, scale) in padded_outputs.items():
        save_png(square_canvas(base_master, size, scale), destination)


def generate_appx_assets(base_master: Image.Image) -> None:
    appx_dir = APP_DIR / "appx" / "assets"

    padded_square_sizes = {
        16,
        20,
        24,
        30,
        32,
        36,
        40,
        44,
        48,
        60,
        64,
        72,
        80,
        96,
        150,
    }
    direct_square_sizes = {50, 256}

    for asset in sorted(appx_dir.glob("*.png")):
        width, height = Image.open(asset).size
        if width == height and width in padded_square_sizes:
            image = square_canvas(base_master, width, 0.70)
        elif width == height and width in direct_square_sizes:
            image = base_master.resize((width, height), RESAMPLING)
        elif (width, height) == (310, 150):
            image = canvas_with_centered_icon(base_master, width, height, 88)
        else:
            raise RuntimeError(f"unsupported AppX asset size for {asset}: {width}x{height}")
        save_png(image, asset)


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    if not source.exists():
        raise SystemExit(f"source SVG not found: {source}")

    base_master = render_svg(source, 1024)
    mac_master = square_canvas(base_master, 1024, 0.825)

    generate_png_assets(base_master)
    generate_appx_assets(base_master)
    save_ico(base_master, ASSETS_DIR / "icon.ico")
    save_ico(base_master, REPO_DIR / "kernel" / "resource" / "icon.ico")
    save_icns(mac_master, ASSETS_DIR / "icon.icns")

    generated = [
        ASSETS_DIR / "icon.png",
        ASSETS_DIR / "icon256.png",
        ASSETS_DIR / "icon-mac.png",
        ASSETS_DIR / "icon.ico",
        ASSETS_DIR / "icon.icns",
        APP_DIR / "stage" / "icon.png",
        APP_DIR / "stage" / "icon-large.png",
        APP_DIR / "appearance" / "boot" / "icon.png",
        APP_DIR / "electron" / "icon.png",
        REPO_DIR / "kernel" / "resource" / "icon.ico",
    ]
    generated.extend(sorted((APP_DIR / "appx" / "assets").glob("*.png")))

    for path in generated:
        print(path.relative_to(REPO_DIR))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1)

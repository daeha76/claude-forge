#!/usr/bin/env python3
"""
Pillow 기반 텍스트 오버레이
슬라이드 이미지에 텍스트를 추가합니다.
외부 의존성: Pillow (pip install Pillow)
"""

import argparse
import functools
import json
import shutil
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow not installed. Run: pip install Pillow")
    sys.exit(1)


# Font search paths (macOS / Linux)
FONT_SEARCH_PATHS = [
    # macOS system fonts
    "/System/Library/Fonts/",
    "/Library/Fonts/",
    str(Path.home() / "Library/Fonts/"),
    # Linux
    "/usr/share/fonts/",
    "/usr/local/share/fonts/",
    str(Path.home() / ".fonts/"),
    str(Path.home() / ".local/share/fonts/"),
]

# Preferred fonts (Korean-friendly, in priority order)
PREFERRED_FONTS = [
    "Pretendard-Bold.otf",
    "Pretendard-SemiBold.otf",
    "NanumGothicBold.ttf",
    "NanumGothic-Bold.ttf",
    "NanumGothicExtraBold.ttf",
    "NotoSansKR-Bold.otf",
    "NotoSansCJKkr-Bold.otf",
    "SpoqaHanSansNeo-Bold.ttf",
    # macOS Korean system fonts
    "AppleSDGothicNeo.ttc",
    "AppleGothic.ttf",
    # Fallback to system fonts
    "Arial Bold.ttf",
    "ArialBold.ttf",
    "Helvetica Bold.ttf",
    "HelveticaNeue-Bold.ttf",
    "SF-Pro-Display-Bold.otf",
]

@functools.lru_cache(maxsize=1)
def find_font() -> str:
    """Find the best available font"""
    for font_name in PREFERRED_FONTS:
        for search_path in FONT_SEARCH_PATHS:
            font_path = Path(search_path) / font_name
            if font_path.exists():
                return str(font_path)
            # Search subdirectories
            parent = Path(search_path)
            if parent.exists():
                matches = list(parent.rglob(font_name))
                if matches:
                    return str(matches[0])
    return ""


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
    """Wrap text to fit within max_width"""
    if "\\n" in text:
        # Manual line breaks
        return text.split("\\n")

    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join([*current_line, word])
        bbox = font.getbbox(test_line)
        text_width = bbox[2] - bbox[0]

        if text_width <= max_width and len(current_line) < 6:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    # Limit to 3 lines max
    return lines[:3]


def add_text_overlay(
    image_path: str,
    text: str,
    output_path: str,
    font_size_ratio: float = 0.065,
    y_position_ratio: float = 0.30,
    text_color: tuple = (255, 255, 255),
    outline_color: tuple = (0, 0, 0),
    outline_width: int = 3,
) -> bool:
    """Add text overlay to an image

    Args:
        image_path: Source image path
        text: Text to overlay
        output_path: Output image path
        font_size_ratio: Font size as ratio of image width (default 6.5%)
        y_position_ratio: Text Y position as ratio of image height (default 30%)
        text_color: RGB text color (default white)
        outline_color: RGB outline color (default black)
        outline_width: Outline thickness in pixels
    """
    try:
        img = Image.open(image_path).convert("RGBA")
    except Exception as e:
        print(f"Failed to open image {image_path}: {e}")
        return False

    width, height = img.size
    draw = ImageDraw.Draw(img)

    # Calculate font size (6.5% of image width)
    font_size = int(width * font_size_ratio)

    # Load font
    font_path = find_font()
    if font_path:
        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception:
            font = ImageFont.load_default()
            font_size = 40
    else:
        font = ImageFont.load_default()
        font_size = 40

    # Wrap text
    max_text_width = int(width * 0.85)
    lines = wrap_text(text, font, max_text_width)

    if not lines:
        return False

    # Calculate total text block height
    line_spacing = int(font_size * 0.5)
    line_heights = []
    for line in lines:
        bbox = font.getbbox(line)
        line_heights.append(bbox[3] - bbox[1])

    total_height = sum(line_heights) + line_spacing * (len(lines) - 1)

    # Starting Y position (30% from top = safe area)
    start_y = int(height * y_position_ratio) - total_height // 2

    # Draw each line
    current_y = start_y
    for i, line in enumerate(lines):
        bbox = font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2

        # Draw outline (stroke)
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx * dx + dy * dy <= outline_width * outline_width:
                    draw.text((x + dx, current_y + dy), line, font=font, fill=outline_color)

        # Draw main text
        draw.text((x, current_y), line, font=font, fill=text_color)

        current_y += line_heights[i] + line_spacing

    # Save as RGB (not RGBA) for compatibility
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    if img.mode == "RGBA":
        rgb_img = Image.new("RGB", img.size, (0, 0, 0))
        rgb_img.paste(img, mask=img.split()[3])
        rgb_img.save(str(output), quality=95)
    else:
        img.save(str(output), quality=95)

    return True


def process_slides(
    slides_dir: str,
    texts: str,
    output_dir: str = "",
) -> list:
    """Process all slides in a directory with text overlays

    Args:
        slides_dir: Directory containing slide images
        texts: Text for each slide, separated by ||
        output_dir: Output directory (default: slides_dir/final/)
    """
    slides_path = Path(slides_dir)
    if not slides_path.exists():
        print(f"Slides directory not found: {slides_dir}")
        return []

    # Parse texts
    text_list = [t.strip() for t in texts.split("||")]

    # Find slide images (sorted by name)
    slide_files = sorted(
        [f for f in slides_path.iterdir() if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")],
        key=lambda f: f.name,
    )

    if not slide_files:
        print(f"No images found in {slides_dir}")
        return []

    # Output directory
    if not output_dir:
        output_dir = str(slides_path / "final")
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    processed = []
    for i, slide_file in enumerate(slide_files):
        # Get text for this slide (use empty string if not enough texts)
        text = text_list[i] if i < len(text_list) else ""

        if not text:
            # No text: just copy the original
            dest = out_path / slide_file.name
            shutil.copy2(str(slide_file), str(dest))
            processed.append(str(dest))
            print(f"Slide {i + 1}: Copied (no text)")
            continue

        output_file = out_path / slide_file.name
        success = add_text_overlay(
            image_path=str(slide_file),
            text=text,
            output_path=str(output_file),
        )

        if success:
            processed.append(str(output_file))
            print(f"Slide {i + 1}: Text added -> {output_file.name}")
        else:
            print(f"Slide {i + 1}: FAILED")

    return processed


def main():
    parser = argparse.ArgumentParser(description="Add text overlays to slideshow images")
    parser.add_argument("--slides", required=True, help="Directory containing slide images")
    parser.add_argument(
        "--texts",
        required=True,
        help='Text for each slide, separated by || (e.g., "Slide 1 text||Slide 2 text||...")',
    )
    parser.add_argument("--output", default="", help="Output directory (default: slides_dir/final/)")

    args = parser.parse_args()

    processed = process_slides(
        slides_dir=args.slides,
        texts=args.texts,
        output_dir=args.output,
    )

    print(f"\nProcessed {len(processed)} slides")

    if not processed:
        sys.exit(1)

    result = {"slides": processed, "count": len(processed)}
    print(f"\nJSON: {json.dumps(result)}")


if __name__ == "__main__":
    main()

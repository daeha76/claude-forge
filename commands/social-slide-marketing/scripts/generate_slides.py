#!/usr/bin/env python3
"""
Gemini 3 Pro 슬라이드쇼 이미지 생성기
6장 세로(9:16) 2K 이미지를 순차 생성합니다.
Scene locking 아키텍처로 일관된 비주얼 스타일 보장.
외부 의존성 없음 (Python urllib만 사용)
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import time
from pathlib import Path
import urllib.request
import urllib.error


# ---------------------------------------------------------------------------
# Category scene defaults (immutable dict)
# ---------------------------------------------------------------------------
CATEGORY_SCENES = {
    "home": {
        "person": "30-year-old Korean woman, shoulder-length brown hair, comfortable cream knit sweater and relaxed pants",
        "environment": "warm modern living room, soft beige sofa, wooden shelves with plants, large window with afternoon sunlight streaming in, cozy minimal decor",
        "camera": "eye-level medium shot",
        "style": "warm inviting digital illustration, soft golden shadows, earthy muted color palette",
    },
    "beauty": {
        "person": "26-year-old Korean woman, long wavy dark hair, elegant off-shoulder top",
        "environment": "bright vanity area, round mirror with soft ring lighting, skincare and makeup products neatly arranged on marble surface, fresh flowers nearby",
        "camera": "eye-level medium shot, slightly angled",
        "style": "bright clean digital illustration, pink and gold accents, glamorous soft diffused lighting",
    },
    "fitness": {
        "person": "25-year-old athletic Korean person, short cropped hair, fitted workout tank top and leggings",
        "environment": "bright modern home gym, exercise mat on light wooden floor, water bottle and towel nearby, morning sunlight through large window",
        "camera": "slightly low angle medium shot",
        "style": "bold vibrant digital illustration, high contrast, energetic warm color palette",
    },
    "productivity": {
        "person": "28-year-old Korean professional, shoulder-length dark hair, white t-shirt and casual blazer",
        "environment": "modern apartment with wooden desk, large window with afternoon natural light, minimal decor, single potted plant",
        "camera": "eye-level medium shot",
        "style": "clean digital illustration, soft shadows, muted professional blue-grey color palette",
    },
    "food": {
        "person": "27-year-old Korean person, tied-back hair, casual apron over simple linen shirt",
        "environment": "bright warm kitchen, wooden countertop with fresh ingredients, copper pots hanging, golden afternoon light, herbs on windowsill",
        "camera": "eye-level medium shot",
        "style": "warm appetizing digital illustration, golden-orange tones, cozy inviting atmosphere",
    },
    "education": {
        "person": "22-year-old Korean student, glasses, comfortable oversized hoodie",
        "environment": "cozy study room, wooden desk with stacked books and open laptop, warm desk lamp glowing, bookshelf in background, sticky notes on wall",
        "camera": "eye-level medium close-up",
        "style": "warm friendly digital illustration, soft pastel accents, inviting studious atmosphere",
    },
    "saas": {
        "person": "32-year-old Korean business professional, neat short hair, crisp button-down shirt with rolled sleeves",
        "environment": "sleek modern office, dual monitor setup on standing desk, whiteboard with diagrams in background, cool ambient LED lighting",
        "camera": "eye-level medium shot",
        "style": "professional tech-forward digital illustration, blue and dark grey tones, sharp clean lines",
    },
    "ecommerce": {
        "person": "24-year-old Korean woman, straight black hair with bangs, trendy casual outfit with cardigan",
        "environment": "stylish apartment, delivery boxes and shopping bags on table, laptop open to shopping page, bright natural light, colorful product packaging visible",
        "camera": "eye-level medium shot",
        "style": "bright colorful digital illustration, cheerful warm tones, playful festive atmosphere",
    },
    "fnb": {
        "person": "29-year-old Korean person, natural wavy hair, casual smart outfit with linen jacket",
        "environment": "cozy modern cafe, wooden table with latte and pastry, exposed brick wall, hanging Edison bulbs, warm ambient lighting through window",
        "camera": "eye-level medium shot, slightly angled",
        "style": "warm atmospheric digital illustration, amber and brown tones, inviting cozy mood",
    },
    "finance": {
        "person": "31-year-old Korean professional, clean-cut hairstyle, smart casual polo shirt",
        "environment": "modern home office, clean desk with single monitor showing charts, bookshelf with business books, green plant accent, soft natural side lighting",
        "camera": "eye-level medium shot",
        "style": "trustworthy professional digital illustration, green and navy blue tones, clean confident atmosphere",
    },
}

NEGATIVE_PROMPT = (
    "Absolutely no text, no letters, no words, no numbers, no writing, "
    "no captions, no watermarks, no logos, no UI elements anywhere in the image."
)

PERSON_CONSTRAINT = (
    "IMPORTANT: A Korean person must always be prominently visible in the image. "
    "The person should be the main subject, clearly shown from at least waist up. "
    "Never generate an image without a person."
)


# ---------------------------------------------------------------------------
# Reference image loading
# ---------------------------------------------------------------------------

def load_reference_images(references_dir: str, max_images: int = 3) -> list:
    """Load reference images from a directory as base64 for multimodal input.

    Args:
        references_dir: Path to directory containing reference images.
        max_images: Maximum number of images to load (to keep payload small).

    Returns:
        List of dicts with 'mime_type' and 'data' (base64 string).
    """
    ref_path = Path(references_dir)
    if not ref_path.is_dir():
        print(f"  References dir not found: {references_dir}")
        return []

    image_extensions = {".png", ".jpg", ".jpeg", ".webp"}
    image_files = sorted(
        [f for f in ref_path.iterdir() if f.suffix.lower() in image_extensions],
        key=lambda f: f.stat().st_size,
        reverse=True,
    )[:max_images]

    if not image_files:
        print(f"  No images found in {references_dir}")
        return []

    mime_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }

    loaded = []
    for img_file in image_files:
        try:
            raw = img_file.read_bytes()
            mime = mime_map.get(img_file.suffix.lower(), "image/jpeg")
            loaded.append({
                "mime_type": mime,
                "data": base64.b64encode(raw).decode(),
            })
        except Exception as e:
            print(f"  Failed to load {img_file.name}: {e}")

    print(f"  Loaded {len(loaded)} reference images")
    return loaded


# ---------------------------------------------------------------------------
# API key & config loading
# ---------------------------------------------------------------------------

def load_api_key() -> str:
    """Load GEMINI_API_KEY from ~/.env"""
    env_path = Path.home() / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("GEMINI_API_KEY="):
                    value = line.split("=", 1)[1]
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    return value
    raise ValueError("GEMINI_API_KEY not found in ~/.env")


def load_config(config_path: str) -> dict:
    """Load config from JSON file"""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Image generation (single slide)
# ---------------------------------------------------------------------------

def generate_single_slide(
    prompt: str,
    output_path: str,
    api_key: str,
    aspect_ratio: str = "9:16",
    image_size: str = "2K",
    max_retries: int = 2,
    timeout: int = 120,
    reference_images: list | None = None,
) -> bool:
    """Generate a single slide image using Gemini 3 Pro.

    Args:
        prompt: Text prompt for image generation.
        output_path: File path to save the generated image.
        api_key: Gemini API key.
        aspect_ratio: Image aspect ratio (default "9:16").
        image_size: Image size (default "2K").
        max_retries: Number of retries on failure.
        timeout: HTTP request timeout in seconds.
        reference_images: Optional list of dicts with 'mime_type' and 'data' (base64)
                         to use as visual references for multimodal generation.
    """
    model = "gemini-3-pro-image-preview"
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    )

    # Build multimodal parts: reference images first, then text prompt
    parts = []
    if reference_images:
        parts.append({"text": (
            "Use the following images as visual style references. "
            "Match the overall mood, color palette, and composition style. "
            "Do NOT copy them directly — create a new original image inspired by them."
        )})
        for ref in reference_images:
            parts.append({
                "inlineData": {
                    "mimeType": ref["mime_type"],
                    "data": ref["data"],
                }
            })
    parts.append({"text": prompt})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect_ratio,
                "imageSize": image_size,
            },
        },
    }

    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    }

    for attempt in range(max_retries + 1):
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode(),
                headers=headers,
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=timeout) as response:
                result = json.loads(response.read())

            saved = _extract_and_save_image(result, output_path)
            if saved:
                return True

            print(f"  No image in response (attempt {attempt + 1})")
            if attempt < max_retries:
                time.sleep(5)

        except urllib.error.HTTPError as e:
            _handle_http_error(e, attempt)
            if attempt < max_retries:
                time.sleep(10)
        except Exception as e:
            print(f"  Error (attempt {attempt + 1}): {e}")
            if attempt < max_retries:
                time.sleep(5)

    return False


def _extract_and_save_image(result: dict, output_path: str) -> bool:
    """Extract image data from API result and save to disk."""
    ext_map = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/webp": ".webp",
    }

    for candidate in result.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            if "inlineData" in part:
                image_data = base64.b64decode(part["inlineData"]["data"])
                mime_type = part["inlineData"].get("mimeType", "image/png")
                expected_ext = ext_map.get(mime_type, ".png")

                output = Path(output_path)
                if output.suffix.lower() not in [".png", ".jpg", ".jpeg", ".webp"]:
                    output = output.with_suffix(expected_ext)

                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(image_data)
                return True
    return False


def _handle_http_error(error: urllib.error.HTTPError, attempt: int) -> None:
    """Log HTTP error details."""
    error_body = error.read().decode()
    print(f"  API Error {error.code} (attempt {attempt + 1})")
    try:
        error_json = json.loads(error_body)
        print(f"  Message: {error_json.get('error', {}).get('message', '')[:200]}")
    except json.JSONDecodeError:
        print(f"  Response: {error_body[:200]}")


# ---------------------------------------------------------------------------
# Scene locking & prompt building
# ---------------------------------------------------------------------------

def build_scene_description(config: dict) -> str:
    """Build a locked scene description from config or auto-generate.

    If config has a non-empty 'sceneDescription' field, use it directly.
    Otherwise auto-generate from the app category using CATEGORY_SCENES.
    """
    scene = config.get("sceneDescription", "").strip()
    if scene:
        return scene

    category = config.get("app", {}).get("category", "productivity").lower()
    defaults = CATEGORY_SCENES.get(category, CATEGORY_SCENES["productivity"])

    scene_parts = [
        f"{defaults['style']}.",
        f"Scene: {defaults['person']},",
        f"in {defaults['environment']}.",
        f"Camera: {defaults['camera']}.",
        "Vertical 9:16 format, high quality, suitable for social media.",
    ]
    return " ".join(scene_parts)


def _build_hook_prompt(scene: str, hook: str) -> str:
    """Slide 1: Hook - stressed/frustrated."""
    return (
        f"{scene} "
        f"Expression: stressed and overwhelmed, furrowed brow, hand on forehead. "
        f"Mood: tense, cluttered desk with scattered papers, muted desaturated colors. "
        f"Represents the frustration of: '{hook}'. "
        f"{PERSON_CONSTRAINT} "
        f"{NEGATIVE_PROMPT}"
    )


def _build_problem_prompt(scene: str, problem: str) -> str:
    """Slide 2: Problem deepens."""
    return (
        f"{scene} "
        f"Expression: exhausted and defeated, slumped posture, tired eyes. "
        f"Mood: heavy atmosphere, even more cluttered surroundings, cool grey tones dominate. "
        f"Represents the pain point: '{problem}'. "
        f"{PERSON_CONSTRAINT} "
        f"{NEGATIVE_PROMPT}"
    )


def _build_discovery_prompt(scene: str, app_name: str) -> str:
    """Slide 3: Discovery moment."""
    return (
        f"{scene} "
        f"Expression: surprised and curious, eyes wide, leaning forward looking at phone screen. "
        f"Mood: a ray of warm light breaking through, slight warm color emerging. "
        f"Represents discovering {app_name}. "
        f"{PERSON_CONSTRAINT} "
        f"{NEGATIVE_PROMPT}"
    )


def _build_transform1_prompt(scene: str, app_name: str, differentiator: str) -> str:
    """Slide 4: Transformation 1 - key benefit."""
    return (
        f"{scene} "
        f"Expression: engaged and focused, slight smile, actively using phone. "
        f"Mood: brighter atmosphere, organized desk, warm balanced colors. "
        f"Represents the key benefit of {app_name}: '{differentiator}'. "
        f"{PERSON_CONSTRAINT} "
        f"{NEGATIVE_PROMPT}"
    )


def _build_transform2_prompt(scene: str, app_name: str) -> str:
    """Slide 5: Transformation 2 - life improved."""
    return (
        f"{scene} "
        f"Expression: genuinely happy, relaxed posture, satisfied smile. "
        f"Mood: bright and airy, everything organized, vibrant warm colors. "
        f"Represents life improved by {app_name}. "
        f"{PERSON_CONSTRAINT} "
        f"{NEGATIVE_PROMPT}"
    )


def _build_cta_prompt(scene: str) -> str:
    """Slide 6: CTA."""
    return (
        f"{scene} "
        f"Expression: confident smile, looking directly at viewer, open welcoming gesture. "
        f"Mood: clean bright background, perfectly organized space, vivid uplifting colors. "
        f"Clean composition with ample space at top 30% for text overlay. "
        f"{PERSON_CONSTRAINT} "
        f"{NEGATIVE_PROMPT}"
    )


def build_slide_prompts(hook: str, config: dict) -> list:
    """Build 6 slide prompts with locked scene architecture.

    Uses the SAME scene description as prefix for ALL prompts,
    only varying emotion/expression and mood/atmosphere per slide.
    """
    app_name = config.get("app", {}).get("name", "the app")
    problem = config.get("app", {}).get("problem", "")
    differentiator = config.get("app", {}).get("differentiator", "")

    scene = build_scene_description(config)

    return [
        _build_hook_prompt(scene, hook),
        _build_problem_prompt(scene, problem),
        _build_discovery_prompt(scene, app_name),
        _build_transform1_prompt(scene, app_name, differentiator),
        _build_transform2_prompt(scene, app_name),
        _build_cta_prompt(scene),
    ]


# ---------------------------------------------------------------------------
# Slide generation orchestrator
# ---------------------------------------------------------------------------

SLIDE_NAMES = (
    "01_hook",
    "02_problem",
    "03_discovery",
    "04_transform1",
    "05_transform2",
    "06_cta",
)


def generate_slides(
    hook: str,
    config: dict,
    output_dir: str,
    test_mode: bool = False,
    references_dir: str | None = None,
) -> list:
    """Generate slide images for a slideshow.

    Args:
        hook: Hook text for the slideshow.
        config: Loaded config dict.
        output_dir: Directory to write images.
        test_mode: If True, generate only slide 1.
        references_dir: Optional directory of reference images for multimodal input.

    Returns:
        List of paths to generated slides.
    """
    api_key = load_api_key()
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    aspect_ratio = config.get("imageGen", {}).get("aspectRatio", "9:16")
    image_size = config.get("imageGen", {}).get("imageSize", "2K")

    # Load reference images if provided
    ref_images = []
    if references_dir:
        ref_images = load_reference_images(references_dir)

    all_prompts = build_slide_prompts(hook, config)

    prompts = [all_prompts[0]] if test_mode else list(all_prompts)
    count = len(prompts)

    if test_mode:
        print("Test mode: generating slide 1 only")

    generated = []

    for i, prompt in enumerate(prompts):
        slide_file = output_path / f"{SLIDE_NAMES[i]}.png"

        # Resume support: skip already generated slides
        if slide_file.exists() and slide_file.stat().st_size > 0:
            print(f"Slide {i + 1}/{count}: Already exists, skipping")
            generated.append(str(slide_file))
            continue

        print(f"Slide {i + 1}/{count}: Generating...")
        success = generate_single_slide(
            prompt=prompt,
            output_path=str(slide_file),
            api_key=api_key,
            aspect_ratio=aspect_ratio,
            image_size=image_size,
            reference_images=ref_images if ref_images else None,
        )

        if success:
            print(f"  Saved: {slide_file}")
            generated.append(str(slide_file))
        else:
            print(f"  FAILED: Slide {i + 1}")

        # Rate limiting: wait between slides
        if i < count - 1:
            time.sleep(3)

    return generated


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate 6-slide slideshow images with Gemini 3 Pro"
    )
    parser.add_argument(
        "--hook", required=True, help="Hook text or topic for the slideshow"
    )
    parser.add_argument(
        "--config", required=True, help="Path to config.json"
    )
    parser.add_argument(
        "--output", default="/tmp/social-slides", help="Output directory"
    )
    parser.add_argument(
        "--test", action="store_true", help="Test mode: generate only slide 1"
    )
    parser.add_argument(
        "--references",
        default=None,
        help="Directory containing reference images for visual style guidance",
    )

    args = parser.parse_args()

    try:
        config = load_config(args.config)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Config error: {e}")
        sys.exit(1)

    # Create timestamped output directory
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_dir = Path(args.output) / timestamp

    generated = generate_slides(
        hook=args.hook,
        config=config,
        output_dir=str(output_dir),
        test_mode=args.test,
        references_dir=args.references,
    )

    print(f"\nGenerated {len(generated)} slides")
    print(f"Output: {output_dir}")

    if not generated:
        sys.exit(1)

    # Output JSON for pipeline use
    result = {
        "slides": generated,
        "output_dir": str(output_dir),
        "count": len(generated),
    }
    print(f"\nJSON: {json.dumps(result)}")


if __name__ == "__main__":
    main()

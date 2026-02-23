#!/usr/bin/env python3
"""
Gemini 3 Pro Image Generator
2K 해상도 이미지 생성
"""

import argparse
import base64
import json
import sys
from pathlib import Path
import urllib.request
import urllib.error


def load_api_key() -> str:
    """Load API key from ~/.env"""
    env_path = Path.home() / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("GEMINI_API_KEY="):
                    value = line.split("=", 1)[1]
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    return value
    raise ValueError("GEMINI_API_KEY not found in ~/.env")


def generate_image(
    prompt: str,
    output_path: str,
    aspect_ratio: str = "16:9"
) -> bool:
    """Generate 2K image using Gemini 3 Pro API"""

    api_key = load_api_key()
    model = "gemini-3-pro-image-preview"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect_ratio,
                "imageSize": "2K"
            }
        }
    }

    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json"
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read())

        # Extract image from response
        for candidate in result.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                if "inlineData" in part:
                    image_data = base64.b64decode(part["inlineData"]["data"])
                    mime_type = part["inlineData"].get("mimeType", "image/png")

                    # Determine extension from mime type
                    ext_map = {
                        "image/png": ".png",
                        "image/jpeg": ".jpg",
                        "image/webp": ".webp"
                    }
                    expected_ext = ext_map.get(mime_type, ".png")

                    output = Path(output_path)
                    # Adjust extension if needed
                    if output.suffix.lower() not in [".png", ".jpg", ".jpeg", ".webp"]:
                        output = output.with_suffix(expected_ext)

                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_bytes(image_data)
                    print(f"Image saved: {output}")
                    print(f"Size: {len(image_data):,} bytes")
                    print(f"Format: {mime_type}")
                    return True

        print("No image in response")
        if "candidates" in result:
            print(f"Response: {json.dumps(result, indent=2)[:500]}")
        return False

    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"API Error: {e.code}")
        try:
            error_json = json.loads(error_body)
            print(f"Message: {error_json.get('error', {}).get('message', error_body)}")
        except json.JSONDecodeError:
            print(f"Response: {error_body[:500]}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate 2K images with Gemini 3 Pro")
    parser.add_argument("prompt", help="Image generation prompt")
    parser.add_argument("-o", "--output", default="generated_image.png", help="Output file path")
    parser.add_argument("-a", "--aspect-ratio", default="16:9",
                       choices=["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"],
                       help="Aspect ratio")

    args = parser.parse_args()

    success = generate_image(
        prompt=args.prompt,
        output_path=args.output,
        aspect_ratio=args.aspect_ratio
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Postiz API 멀티플랫폼 게시
TikTok(초안) + Instagram(캐러셀) 게시를 담당합니다.
외부 의존성 없음 (Python urllib만 사용)
"""

import argparse
import json
import sys
import time
from pathlib import Path
import urllib.request
import urllib.error

POSTIZ_BASE_URL = "https://api.postiz.com/public/v1"


def load_env(key: str) -> str:
    """Load a value from ~/.env"""
    env_path = Path.home() / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{key}="):
                    value = line.split("=", 1)[1]
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    return value
    raise ValueError(f"{key} not found in ~/.env")


def load_config(config_path: str) -> dict:
    """Load config from JSON file"""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {config_path}: {e}") from e


CATEGORY_HASHTAGS = {
    "productivity": "#생산성앱 #업무효율 #시간관리 #직장인꿀팁 #자기계발 #앱추천 #꿀팁",
    "fitness": "#운동앱 #홈트레이닝 #피트니스 #다이어트 #바디프로필 #건강관리 #운동꿀팁",
    "education": "#공부앱 #자기계발 #영어공부 #학습앱 #공부꿀팁 #자격증 #스터디",
    "beauty": "#뷰티앱 #스킨케어 #메이크업 #뷰티꿀팁 #화장법 #피부관리 #뷰티추천",
    "finance": "#재테크 #가계부앱 #금융앱 #투자 #절약 #돈관리 #재테크꿀팁",
    "lifestyle": "#라이프스타일 #일상앱 #생활꿀팁 #추천앱 #꿀정보 #편리한앱 #일상",
    "social": "#소셜앱 #SNS #커뮤니티 #소통 #네트워킹 #앱추천 #꿀팁",
    "travel": "#여행앱 #여행꿀팁 #해외여행 #국내여행 #여행준비 #여행필수앱 #트래블",
}
DEFAULT_HASHTAGS = "#앱추천 #꿀팁 #추천앱 #생활꿀팁 #꿀정보"


def build_instagram_caption(caption: str, config: dict) -> str:
    """Build Instagram-optimized caption (longer, more hashtags, save-focused CTA)."""
    category = config.get("app", {}).get("category", "")

    # Instagram-specific CTA (saves are the strongest signal)
    ig_cta = "나중에 다시 볼 수 있게 저장해두세요"

    # Add more hashtags for Instagram (5-10)
    hashtags = CATEGORY_HASHTAGS.get(category, DEFAULT_HASHTAGS)

    return f"{caption}\n\n{ig_cta}\n\n{hashtags}"


def postiz_request(endpoint: str, api_key: str, method: str = "GET", data: dict = None) -> dict:
    """Make a request to Postiz API"""
    url = f"{POSTIZ_BASE_URL}{endpoint}"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
    }

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Postiz API Error {e.code}")
        try:
            error_json = json.loads(error_body)
            print(f"Message: {json.dumps(error_json, indent=2)[:500]}")
        except json.JSONDecodeError:
            print(f"Response: {error_body[:500]}")
        return {"error": True, "status": e.code}
    except Exception as e:
        print(f"Request error: {e}")
        return {"error": True, "message": str(e)}


def upload_media(api_key: str, file_path: str) -> dict:
    """Upload a media file to Postiz"""
    url = f"{POSTIZ_BASE_URL}/upload"

    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return {}

    image_data = path.read_bytes()

    import mimetypes
    mime_type = mimetypes.guess_type(str(path))[0] or "image/png"

    boundary = f"----PostizBoundary{int(time.time() * 1000)}"

    body_parts = []
    body_parts.append(f"--{boundary}".encode())
    body_parts.append(
        f'Content-Disposition: form-data; name="file"; filename="{path.name}"'.encode()
    )
    body_parts.append(f"Content-Type: {mime_type}".encode())
    body_parts.append(b"")
    body_parts.append(image_data)
    body_parts.append(f"--{boundary}--".encode())

    body = b"\r\n".join(body_parts)

    headers = {
        "Authorization": api_key,
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read())
        return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Upload error {e.code}: {error_body[:300]}")
        return {}
    except Exception as e:
        print(f"Upload error: {e}")
        return {}


def upload_slides(api_key: str, slides_dir: str) -> list:
    """Upload all slide images and return media references"""
    slides_path = Path(slides_dir)
    slide_files = sorted(
        [f for f in slides_path.iterdir() if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")],
        key=lambda f: f.name,
    )

    if not slide_files:
        print(f"No images found in {slides_dir}")
        return []

    uploaded = []
    for i, slide_file in enumerate(slide_files):
        print(f"Uploading slide {i + 1}/{len(slide_files)}: {slide_file.name}")
        result = upload_media(api_key, str(slide_file))

        # Rate limit handling (429)
        if result.get("status") == 429:
            print("  Rate limit hit, waiting 60s...")
            time.sleep(60)
            result = upload_media(api_key, str(slide_file))

        if result and not result.get("error"):
            uploaded.append(result)
            print(f"  Uploaded: {result.get('id', 'ok')}")
        else:
            print(f"  FAILED: {slide_file.name}")
        time.sleep(2)

    return uploaded


def _build_post_payload(config: dict, images: list, caption: str, title: str, platforms: list = None) -> tuple:
    """Build post payload for Postiz API. Returns (payload dict, platforms list)."""
    integration_ids = config.get("postiz", {}).get("integrationIds", {})
    posting_config = config.get("posting", {})
    privacy_level = posting_config.get("privacyLevel", "SELF_ONLY")
    auto_add_music = posting_config.get("autoAddMusic", True)

    resolved_platforms = (
        ["tiktok", *posting_config.get("crossPost", [])]
        if platforms is None
        else list(platforms)
    )

    posts = []

    # TikTok post
    if "tiktok" in resolved_platforms and integration_ids.get("tiktok"):
        posts = [*posts, {
            "integration": {"id": integration_ids["tiktok"]},
            "value": [{"content": caption, "image": images}],
            "settings": {
                "__type": "tiktok",
                "title": title,
                "privacy_level": privacy_level,
                "video_made_with_ai": True,
                "content_posting_method": "DIRECT_POST",
                "duet": False,
                "stitch": False,
                "comment": True,
                "autoAddMusic": auto_add_music,
                "brand_content_toggle": False,
                "brand_organic_toggle": False,
            },
        }]

    # Instagram: carousel with optimized caption
    if "instagram" in resolved_platforms and integration_ids.get("instagram"):
        ig_caption = build_instagram_caption(caption, config)
        posts = [*posts, {
            "integration": {"id": integration_ids["instagram"]},
            "value": [{"content": ig_caption, "image": images}],
            "settings": {"__type": "instagram", "post_type": "post"},
        }]

    payload = {"type": "now", "posts": posts}
    return (payload, resolved_platforms)


def create_post(
    api_key: str,
    config: dict,
    images: list,
    caption: str,
    title: str,
    platforms: list = None,
) -> dict:
    """Create a multi-platform post via Postiz API"""
    payload, resolved_platforms = _build_post_payload(config, images, caption, title, platforms)

    posting_config = config.get("posting", {})
    privacy_level = posting_config.get("privacyLevel", "SELF_ONLY")
    auto_add_music = posting_config.get("autoAddMusic", True)

    # Print platform info
    if "tiktok" in resolved_platforms and config.get("postiz", {}).get("integrationIds", {}).get("tiktok"):
        print(f"TikTok: Added (privacy: {privacy_level}, autoAddMusic: {auto_add_music})")
    if "instagram" in resolved_platforms and config.get("postiz", {}).get("integrationIds", {}).get("instagram"):
        print("Instagram: Added (carousel, save-focused CTA)")

    if not payload["posts"]:
        print("No platforms configured. Check config.json integrationIds.")
        return {"error": True}

    print(f"\nPosting to {len(payload['posts'])} platform(s)...")
    result = postiz_request("/posts", api_key, method="POST", data=payload)

    if result.get("error"):
        print("Post creation failed")
    else:
        print(f"Post created successfully")
        if result.get("id"):
            print(f"Post ID: {result['id']}")

    return result


def post_slideshow(
    config_path: str,
    slides_dir: str,
    caption: str,
    title: str,
    platforms: list = None,
    dry_run: bool = False,
) -> dict:
    """Full pipeline: upload slides + create multi-platform post"""
    config = load_config(config_path)
    api_key = config.get("postiz", {}).get("apiKey", "")

    if not api_key:
        try:
            api_key = load_env("POSTIZ_API_KEY")
        except ValueError:
            if not dry_run:
                print("Postiz API key not found in config or ~/.env")
                return {"error": True}
            api_key = "DRY_RUN_KEY"

    if dry_run:
        return _dry_run_post(config, slides_dir, caption, title, platforms)

    # Step 1: Upload slides
    print("=== Uploading Slides ===\n")
    images = upload_slides(api_key, slides_dir)

    if not images:
        print("No images uploaded. Aborting.")
        return {"error": True}

    print(f"\nUploaded {len(images)} slides\n")

    # Step 2: Create post
    print("=== Creating Post ===\n")
    result = create_post(
        api_key=api_key,
        config=config,
        images=images,
        caption=caption,
        title=title,
        platforms=platforms,
    )

    return result


def _dry_run_post(
    config: dict,
    slides_dir: str,
    caption: str,
    title: str,
    platforms: list = None,
) -> dict:
    """Print what would be posted without making API calls"""
    print("=== DRY RUN (API 호출 없음) ===\n")

    # List slides that would be uploaded
    slides_path = Path(slides_dir)
    slide_files = sorted(
        [f for f in slides_path.iterdir() if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")],
        key=lambda f: f.name,
    ) if slides_path.exists() else []

    print(f"Slides directory: {slides_dir}")
    print(f"Slides found: {len(slide_files)}")
    for f in slide_files:
        print(f"  - {f.name}")

    # Build fake image refs
    fake_images = [{"id": f"dry-run-{i}", "path": str(f)} for i, f in enumerate(slide_files)]

    # Build payload via shared function
    payload, resolved_platforms = _build_post_payload(config, fake_images, caption, title, platforms)

    posting_config = config.get("posting", {})
    privacy_level = posting_config.get("privacyLevel", "SELF_ONLY")
    auto_add_music = posting_config.get("autoAddMusic", True)

    print(f"\n=== Payload Preview ===\n")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    print(f"\n=== Summary ===")
    print(f"Platforms: {', '.join(resolved_platforms)}")
    print(f"Active posts: {len(payload['posts'])}")
    print(f"Caption: {caption[:100]}{'...' if len(caption) > 100 else ''}")
    print(f"Title: {title}")
    print(f"Privacy: {privacy_level}")
    print(f"AutoAddMusic: {auto_add_music}")
    print(f"\nDRY RUN 완료. 실제 게시하려면 --dry-run 없이 실행하세요.")

    return {"dry_run": True, "payload": payload}


def main():
    parser = argparse.ArgumentParser(description="Post slideshow to TikTok/Instagram via Postiz")
    parser.add_argument("--slides", required=True, help="Directory containing final slide images")
    parser.add_argument("--caption", required=True, help="Post caption text")
    parser.add_argument("--title", default="", help="TikTok video title")
    parser.add_argument("--config", default=str(Path.home() / ".social-slide-marketing/config.json"),
                        help="Path to config.json")
    parser.add_argument("--platforms", default="", help="Comma-separated platforms (tiktok,instagram)")
    parser.add_argument("--dry-run", action="store_true", help="Print payload without making API calls")
    parser.add_argument("--cta", default="link_in_bio",
                        choices=["link_in_bio", "comment", "dm", "save", "follow"],
                        help="CTA type for this post")

    args = parser.parse_args()

    platforms = [p.strip() for p in args.platforms.split(",") if p.strip()] if args.platforms else None

    result = post_slideshow(
        config_path=args.config,
        slides_dir=args.slides,
        caption=args.caption,
        title=args.title or args.caption[:50],
        platforms=platforms,
        dry_run=args.dry_run,
    )

    if result.get("error"):
        sys.exit(1)

    # Include CTA type in output for tracking
    output = {**result, "cta_type": args.cta}
    print(f"\nJSON: {json.dumps(output)}")


if __name__ == "__main__":
    main()

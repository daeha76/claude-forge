#!/usr/bin/env python3
"""
Instagram Graph API 포스팅
단일 이미지 또는 캐러셀(다중 이미지) 포스팅을 지원합니다.
외부 의존성 없음 (Python urllib만 사용)
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_BASE = "https://graph.facebook.com/v21.0"


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


def api_request(url: str, params: dict) -> dict:
    """Make a POST request to Instagram Graph API"""
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        try:
            error_json = json.loads(error_body)
            error_msg = error_json.get("error", {}).get("message", error_body)
            error_code = error_json.get("error", {}).get("code", "")
            print(f"API Error {e.code} (code: {error_code}): {error_msg}")
        except json.JSONDecodeError:
            print(f"API Error {e.code}: {error_body[:500]}")
        sys.exit(1)


def check_container_status(container_id: str, access_token: str, max_wait: int = 60) -> bool:
    """Poll container status until ready or failed"""
    url = f"{API_BASE}/{container_id}"
    params = urllib.parse.urlencode({
        "fields": "status_code",
        "access_token": access_token,
    })

    for _ in range(max_wait // 2):
        try:
            req = urllib.request.Request(f"{url}?{params}")
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read())
            status = result.get("status_code", "")
            if status == "FINISHED":
                return True
            if status == "ERROR":
                print(f"Container error: {result}")
                return False
            time.sleep(2)
        except Exception:
            time.sleep(2)

    print("Timeout waiting for container to be ready")
    return False


def create_media_container(
    user_id: str, access_token: str, image_url: str, is_carousel_item: bool = False
) -> str:
    """Create a media container for a single image"""
    url = f"{API_BASE}/{user_id}/media"
    params = {
        "image_url": image_url,
        "access_token": access_token,
    }
    if is_carousel_item:
        params["is_carousel_item"] = "true"

    result = api_request(url, params)
    container_id = result.get("id")
    if not container_id:
        print(f"Failed to create media container: {result}")
        sys.exit(1)
    return container_id


def create_carousel_container(
    user_id: str, access_token: str, children_ids: list, caption: str
) -> str:
    """Create a carousel container from child containers"""
    url = f"{API_BASE}/{user_id}/media"
    params = {
        "media_type": "CAROUSEL",
        "children": ",".join(children_ids),
        "caption": caption,
        "access_token": access_token,
    }

    result = api_request(url, params)
    container_id = result.get("id")
    if not container_id:
        print(f"Failed to create carousel container: {result}")
        sys.exit(1)
    return container_id


def publish_media(user_id: str, access_token: str, container_id: str) -> str:
    """Publish a media container"""
    url = f"{API_BASE}/{user_id}/media_publish"
    params = {
        "creation_id": container_id,
        "access_token": access_token,
    }

    result = api_request(url, params)
    media_id = result.get("id")
    if not media_id:
        print(f"Failed to publish: {result}")
        sys.exit(1)
    return media_id


def post_single(user_id: str, access_token: str, image_url: str, caption: str) -> str:
    """Post a single image to Instagram"""
    print("Creating media container...")
    url = f"{API_BASE}/{user_id}/media"
    params = {
        "image_url": image_url,
        "caption": caption,
        "access_token": access_token,
    }
    result = api_request(url, params)
    container_id = result.get("id")
    if not container_id:
        print(f"Failed to create container: {result}")
        sys.exit(1)

    print("Waiting for container to be ready...")
    if not check_container_status(container_id, access_token):
        sys.exit(1)

    print("Publishing...")
    media_id = publish_media(user_id, access_token, container_id)
    print(f"Published! Media ID: {media_id}")
    print(f"View: https://www.instagram.com/p/{media_id}/")
    return media_id


def post_carousel(
    user_id: str, access_token: str, image_urls: list, caption: str
) -> str:
    """Post a carousel (multiple images) to Instagram"""
    if len(image_urls) < 2:
        print("Carousel requires at least 2 images. Using single post instead.")
        return post_single(user_id, access_token, image_urls[0], caption)

    if len(image_urls) > 10:
        print("Instagram allows max 10 images per carousel. Using first 10.")
        image_urls = image_urls[:10]

    # Step 1: Create child containers
    children_ids = []
    for i, url in enumerate(image_urls):
        print(f"Creating container for image {i + 1}/{len(image_urls)}...")
        child_id = create_media_container(user_id, access_token, url, is_carousel_item=True)
        children_ids.append(child_id)

    # Wait for all children to be ready
    print("Waiting for containers to be ready...")
    for child_id in children_ids:
        if not check_container_status(child_id, access_token):
            print(f"Container {child_id} failed")
            sys.exit(1)

    # Step 2: Create carousel container
    print("Creating carousel container...")
    carousel_id = create_carousel_container(user_id, access_token, children_ids, caption)

    # Wait for carousel container
    print("Waiting for carousel to be ready...")
    if not check_container_status(carousel_id, access_token):
        sys.exit(1)

    # Step 3: Publish
    print("Publishing carousel...")
    media_id = publish_media(user_id, access_token, carousel_id)
    print(f"Published! Media ID: {media_id}")
    print(f"Images: {len(image_urls)}")
    return media_id


def main():
    parser = argparse.ArgumentParser(description="Post to Instagram via Graph API")
    parser.add_argument(
        "--images",
        required=True,
        help="Comma-separated image URLs (public HTTPS URLs)",
    )
    parser.add_argument(
        "--caption", default="", help="Post caption (include hashtags here)"
    )

    args = parser.parse_args()

    user_id = load_env("INSTAGRAM_USER_ID")
    access_token = load_env("INSTAGRAM_ACCESS_TOKEN")

    image_urls = [url.strip() for url in args.images.split(",") if url.strip()]
    if not image_urls:
        print("No image URLs provided")
        sys.exit(1)

    if len(image_urls) == 1:
        post_single(user_id, access_token, image_urls[0], args.caption)
    else:
        post_carousel(user_id, access_token, image_urls, args.caption)


if __name__ == "__main__":
    main()

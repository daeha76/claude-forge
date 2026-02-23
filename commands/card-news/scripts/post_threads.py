#!/usr/bin/env python3
"""
Threads API 포스팅
텍스트 + 이미지 포스팅 (단일 이미지, 캐러셀 지원)
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

API_BASE = "https://graph.threads.net/v1.0"


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


def api_post(url: str, params: dict) -> dict:
    """Make a POST request to Threads API"""
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


def check_status(container_id: str, access_token: str, max_wait: int = 60) -> bool:
    """Poll container status until ready"""
    params = urllib.parse.urlencode({
        "fields": "status",
        "access_token": access_token,
    })

    for _ in range(max_wait // 2):
        try:
            url = f"{API_BASE}/{container_id}?{params}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read())
            status = result.get("status", "")
            if status == "FINISHED":
                return True
            if status == "ERROR":
                print(f"Container error: {result}")
                return False
            time.sleep(2)
        except Exception:
            time.sleep(2)

    print("Timeout waiting for container")
    return False


def post_text(user_id: str, access_token: str, text: str) -> str:
    """Post text-only to Threads"""
    print("Creating text container...")
    url = f"{API_BASE}/{user_id}/threads"
    params = {
        "media_type": "TEXT",
        "text": text,
        "access_token": access_token,
    }

    result = api_post(url, params)
    container_id = result.get("id")
    if not container_id:
        print(f"Failed to create container: {result}")
        sys.exit(1)

    print("Publishing...")
    publish_url = f"{API_BASE}/{user_id}/threads_publish"
    pub_result = api_post(publish_url, {
        "creation_id": container_id,
        "access_token": access_token,
    })

    media_id = pub_result.get("id")
    print(f"Published! Media ID: {media_id}")
    return media_id


def post_single_image(
    user_id: str, access_token: str, image_url: str, text: str
) -> str:
    """Post single image to Threads"""
    print("Creating image container...")
    url = f"{API_BASE}/{user_id}/threads"
    params = {
        "media_type": "IMAGE",
        "image_url": image_url,
        "text": text,
        "access_token": access_token,
    }

    result = api_post(url, params)
    container_id = result.get("id")
    if not container_id:
        print(f"Failed to create container: {result}")
        sys.exit(1)

    print("Waiting for container to be ready...")
    if not check_status(container_id, access_token):
        sys.exit(1)

    print("Publishing...")
    publish_url = f"{API_BASE}/{user_id}/threads_publish"
    pub_result = api_post(publish_url, {
        "creation_id": container_id,
        "access_token": access_token,
    })

    media_id = pub_result.get("id")
    print(f"Published! Media ID: {media_id}")
    return media_id


def post_carousel(
    user_id: str, access_token: str, image_urls: list, text: str
) -> str:
    """Post carousel (multiple images) to Threads"""
    if len(image_urls) < 2:
        return post_single_image(user_id, access_token, image_urls[0], text)

    if len(image_urls) > 10:
        print("Threads allows max 10 items per carousel. Using first 10.")
        image_urls = image_urls[:10]

    # Step 1: Create child containers
    children_ids = []
    for i, img_url in enumerate(image_urls):
        print(f"Creating child container {i + 1}/{len(image_urls)}...")
        url = f"{API_BASE}/{user_id}/threads"
        params = {
            "media_type": "IMAGE",
            "image_url": img_url,
            "is_carousel_item": "true",
            "access_token": access_token,
        }
        result = api_post(url, params)
        child_id = result.get("id")
        if not child_id:
            print(f"Failed to create child container: {result}")
            sys.exit(1)
        children_ids.append(child_id)

    # Wait for all children
    print("Waiting for containers to be ready...")
    for child_id in children_ids:
        if not check_status(child_id, access_token):
            print(f"Container {child_id} failed")
            sys.exit(1)

    # Step 2: Create carousel container
    print("Creating carousel container...")
    url = f"{API_BASE}/{user_id}/threads"
    params = {
        "media_type": "CAROUSEL",
        "children": ",".join(children_ids),
        "text": text,
        "access_token": access_token,
    }
    result = api_post(url, params)
    carousel_id = result.get("id")
    if not carousel_id:
        print(f"Failed to create carousel: {result}")
        sys.exit(1)

    print("Waiting for carousel to be ready...")
    if not check_status(carousel_id, access_token):
        sys.exit(1)

    # Step 3: Publish
    print("Publishing carousel...")
    publish_url = f"{API_BASE}/{user_id}/threads_publish"
    pub_result = api_post(publish_url, {
        "creation_id": carousel_id,
        "access_token": access_token,
    })

    media_id = pub_result.get("id")
    print(f"Published! Media ID: {media_id}")
    print(f"Images: {len(image_urls)}")
    return media_id


def main():
    parser = argparse.ArgumentParser(description="Post to Threads API")
    parser.add_argument("--text", default="", help="Post text content")
    parser.add_argument(
        "--images",
        default="",
        help="Comma-separated image URLs (public HTTPS URLs)",
    )

    args = parser.parse_args()

    user_id = load_env("THREADS_USER_ID")
    access_token = load_env("THREADS_ACCESS_TOKEN")

    image_urls = [url.strip() for url in args.images.split(",") if url.strip()]

    if not image_urls and not args.text:
        print("Provide --text and/or --images")
        sys.exit(1)

    if not image_urls:
        post_text(user_id, access_token, args.text)
    elif len(image_urls) == 1:
        post_single_image(user_id, access_token, image_urls[0], args.text)
    else:
        post_carousel(user_id, access_token, image_urls, args.text)


if __name__ == "__main__":
    main()

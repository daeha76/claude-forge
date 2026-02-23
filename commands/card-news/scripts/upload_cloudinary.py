#!/usr/bin/env python3
"""
Cloudinary 이미지 업로드
로컬 이미지를 Cloudinary에 업로드하고 공개 HTTPS URL을 반환합니다.
외부 의존성 없음 (Python urllib만 사용)
"""

import argparse
import hashlib
import json
import mimetypes
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


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


def generate_signature(params: dict, api_secret: str) -> str:
    """Generate Cloudinary API signature"""
    sorted_params = sorted(params.items())
    to_sign = "&".join(f"{k}={v}" for k, v in sorted_params)
    to_sign += api_secret
    return hashlib.sha1(to_sign.encode()).hexdigest()


def upload_image(file_path: str, folder: str = "card-news") -> str:
    """Upload image to Cloudinary and return public URL"""
    cloud_name = load_env("CLOUDINARY_CLOUD_NAME")
    api_key = load_env("CLOUDINARY_API_KEY")
    api_secret = load_env("CLOUDINARY_API_SECRET")

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    timestamp = str(int(time.time()))
    params = {
        "folder": folder,
        "timestamp": timestamp,
    }
    signature = generate_signature(params, api_secret)

    # Read file
    image_data = path.read_bytes()
    mime_type = mimetypes.guess_type(str(path))[0] or "image/jpeg"

    # Build multipart form data
    boundary = f"----CloudinaryBoundary{int(time.time() * 1000)}"

    body_parts = []
    fields = {
        "api_key": api_key,
        "timestamp": timestamp,
        "signature": signature,
        "folder": folder,
    }
    for field_name, field_value in fields.items():
        body_parts.append(f"--{boundary}".encode())
        body_parts.append(
            f'Content-Disposition: form-data; name="{field_name}"'.encode()
        )
        body_parts.append(b"")
        body_parts.append(field_value.encode())

    # File field
    body_parts.append(f"--{boundary}".encode())
    body_parts.append(
        f'Content-Disposition: form-data; name="file"; filename="{path.name}"'.encode()
    )
    body_parts.append(f"Content-Type: {mime_type}".encode())
    body_parts.append(b"")
    body_parts.append(image_data)
    body_parts.append(f"--{boundary}--".encode())

    body = b"\r\n".join(body_parts)

    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read())
        public_url = result["secure_url"]
        print(f"Uploaded: {public_url}")
        print(f"Public ID: {result.get('public_id', 'N/A')}")
        print(f"Size: {result.get('bytes', 0):,} bytes")
        return public_url
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Upload Error: {e.code}")
        try:
            error_json = json.loads(error_body)
            print(f"Message: {error_json.get('error', {}).get('message', error_body)}")
        except json.JSONDecodeError:
            print(f"Response: {error_body[:500]}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Upload image to Cloudinary")
    parser.add_argument("file", help="Image file path to upload")
    parser.add_argument(
        "--folder",
        default="card-news",
        help="Cloudinary folder (default: card-news)",
    )

    args = parser.parse_args()
    upload_image(args.file, args.folder)


if __name__ == "__main__":
    main()

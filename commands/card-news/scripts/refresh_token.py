#!/usr/bin/env python3
"""
Instagram/Threads 장기 토큰 갱신
장기 토큰은 60일 유효. 만료 전 갱신 필요.
외부 의존성 없음 (Python urllib만 사용)
"""

import argparse
import json
import sys
import urllib.error
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


def update_env(key: str, new_value: str):
    """Update a value in ~/.env"""
    env_path = Path.home() / ".env"
    lines = []
    found = False

    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip().startswith(f"{key}="):
                    lines.append(f'{key}={new_value}\n')
                    found = True
                else:
                    lines.append(line)

    if not found:
        lines.append(f'{key}={new_value}\n')

    with open(env_path, "w") as f:
        f.writelines(lines)


def refresh_instagram_token() -> str:
    """Refresh Instagram long-lived token"""
    current_token = load_env("INSTAGRAM_ACCESS_TOKEN")
    url = (
        f"https://graph.instagram.com/refresh_access_token"
        f"?grant_type=ig_refresh_token"
        f"&access_token={current_token}"
    )

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read())

        new_token = result.get("access_token")
        expires_in = result.get("expires_in", 0)
        days = expires_in // 86400

        if new_token:
            update_env("INSTAGRAM_ACCESS_TOKEN", new_token)
            print(f"Instagram token refreshed!")
            print(f"Expires in: {days} days")
            return new_token
        else:
            print(f"Failed to refresh: {result}")
            sys.exit(1)

    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Error {e.code}: {error_body[:500]}")
        sys.exit(1)


def refresh_threads_token() -> str:
    """Refresh Threads long-lived token"""
    current_token = load_env("THREADS_ACCESS_TOKEN")
    url = (
        f"https://graph.threads.net/refresh_access_token"
        f"?grant_type=th_refresh_token"
        f"&access_token={current_token}"
    )

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read())

        new_token = result.get("access_token")
        expires_in = result.get("expires_in", 0)
        days = expires_in // 86400

        if new_token:
            update_env("THREADS_ACCESS_TOKEN", new_token)
            print(f"Threads token refreshed!")
            print(f"Expires in: {days} days")
            return new_token
        else:
            print(f"Failed to refresh: {result}")
            sys.exit(1)

    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Error {e.code}: {error_body[:500]}")
        sys.exit(1)


def check_token_info(platform: str):
    """Check token expiry info"""
    if platform == "instagram":
        token = load_env("INSTAGRAM_ACCESS_TOKEN")
        url = f"https://graph.instagram.com/me?fields=id,username&access_token={token}"
    else:
        token = load_env("THREADS_ACCESS_TOKEN")
        url = f"https://graph.threads.net/v1.0/me?fields=id,username&access_token={token}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read())
        print(f"{platform.title()} token valid")
        print(f"User: {result.get('username', result.get('id', 'unknown'))}")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"{platform.title()} token invalid or expired")
        print(f"Error: {error_body[:200]}")


def main():
    parser = argparse.ArgumentParser(
        description="Refresh Instagram/Threads long-lived tokens"
    )
    parser.add_argument(
        "platform",
        nargs="?",
        choices=["instagram", "threads", "both", "check"],
        default="both",
        help="Platform to refresh (default: both)",
    )

    args = parser.parse_args()

    if args.platform == "check":
        print("--- Instagram ---")
        check_token_info("instagram")
        print()
        print("--- Threads ---")
        check_token_info("threads")
        return

    if args.platform in ("instagram", "both"):
        print("--- Refreshing Instagram token ---")
        try:
            refresh_instagram_token()
        except ValueError as e:
            print(f"Skip: {e}")

    if args.platform in ("threads", "both"):
        print("--- Refreshing Threads token ---")
        try:
            refresh_threads_token()
        except ValueError as e:
            print(f"Skip: {e}")

    print("\nDone!")


if __name__ == "__main__":
    main()

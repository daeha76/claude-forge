#!/usr/bin/env python3
"""
온보딩 & 설정 관리
설정 파일 초기화, 검증, 업데이트를 담당합니다.
외부 의존성 없음 (Python 표준 라이브러리만 사용)
"""

import argparse
import json
import sys
from pathlib import Path


CONFIG_DIR = Path.home() / ".social-slide-marketing"
CONFIG_PATH = CONFIG_DIR / "config.json"
HOOKS_PATH = CONFIG_DIR / "hooks.json"
HOOK_PERFORMANCE_PATH = CONFIG_DIR / "hook-performance.json"
COMPETITOR_PATH = CONFIG_DIR / "competitors.json"

CONFIG_TEMPLATE = {
    "app": {
        "name": "",
        "description": "",
        "audience": "",
        "problem": "",
        "differentiator": "",
        "url": "",
        "category": "",
        "isMobileApp": False,
    },
    "sceneDescription": "",
    "imageGen": {
        "provider": "gemini",
        "model": "gemini-3-pro-image-preview",
        "aspectRatio": "9:16",
        "imageSize": "2K",
    },
    "postiz": {
        "apiKey": "",
        "integrationIds": {
            "tiktok": "",
            "instagram": "",
        },
    },
    "posting": {
        "privacyLevel": "SELF_ONLY",
        "schedule": ["07:30", "16:30", "21:00"],
        "crossPost": ["instagram"],
        "autoAddMusic": True,
        "timezone": "Asia/Seoul",
        "hookRegister": "diary",
        "ctaType": "link_in_bio",
    },
    "conversion": {
        "enabled": True,
        "trackingMethod": "manual",
        "linkClickSource": "bitly",
        "notes": "",
    },
}


def init_config() -> None:
    """Initialize config directory and files"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # Config file
    if not CONFIG_PATH.exists():
        with open(CONFIG_PATH, "w") as f:
            json.dump(CONFIG_TEMPLATE, f, indent=2, ensure_ascii=False)
        print(f"Created: {CONFIG_PATH}")
    else:
        print(f"Already exists: {CONFIG_PATH}")

    # Hooks library
    if not HOOKS_PATH.exists():
        hooks_template = {
            "hooks": [],
            "register": "diary",  # formal / casual / diary
            "tier1_formulas": [
                # English (unchanged)
                "I found an app that [benefit]",
                "Stop [current behavior], use [app] instead",
                "This app will [transformation] in [timeframe]",
                # Korean diary style
                "[앱이름] 써봤는데 진짜 대박임",
                "[문제] 때문에 고민이었는데 이거 찾음",
                "이거 쓰고 나서 [결과] 됨 ㅋㅋ",
            ],
            "tier2_formulas": [
                "I've been using [app] for [time] and [result]",
                "Why does nobody talk about [app]?",
                "[Number]% of people don't know about [app]",
                # Korean diary style
                "이거 진짜 숨겨진 앱인데 ㄹㅇ 대박",
                "[직업/상황]인 사람은 이거 필수임",
                "3개월째 쓰는데 아직도 신세계임",
            ],
            "tier3_formulas": [
                "The [category] app that changed my [area]",
                "[App] vs [competitor] - here's why I switched",
                "My [timeframe] results using [app]",
                # Korean diary style
                "[경쟁앱] 쓰다가 [앱]으로 갈아탄 이유 ㄹㅇ",
                "댓글에 손 남기면 링크 보내드림",
                "[기간] 동안 써본 후기 정리해봄",
            ],
        }
        with open(HOOKS_PATH, "w") as f:
            json.dump(hooks_template, f, indent=2, ensure_ascii=False)
        print(f"Created: {HOOKS_PATH}")

    # Hook performance tracker
    if not HOOK_PERFORMANCE_PATH.exists():
        with open(HOOK_PERFORMANCE_PATH, "w") as f:
            json.dump({"performances": []}, f, indent=2)
        print(f"Created: {HOOK_PERFORMANCE_PATH}")

    # Competitor data
    if not COMPETITOR_PATH.exists():
        with open(COMPETITOR_PATH, "w") as f:
            json.dump({"competitors": []}, f, indent=2)
        print(f"Created: {COMPETITOR_PATH}")

    print(f"\nConfig directory: {CONFIG_DIR}")
    print("Run --validate to check setup completeness")


def _collect_validation_issues(config: dict) -> tuple:
    """Collect validation issues and warnings from config.

    Returns:
        (issues, warnings, env_vars, pillow_ok) where:
        - issues: list of critical problems
        - warnings: list of non-critical recommendations
        - env_vars: dict of found environment variable names
        - pillow_ok: whether Pillow is importable
    """
    issues = []
    warnings = []

    # Check app info
    app = config.get("app", {})
    required_app_fields = ["name", "description", "audience", "problem"]
    issues = issues + [
        f"app.{field} is empty"
        for field in required_app_fields
        if not app.get(field)
    ]

    optional_app_fields = ["differentiator", "url", "category"]
    warnings = warnings + [
        f"app.{field} is empty (recommended)"
        for field in optional_app_fields
        if not app.get(field)
    ]

    # Check Postiz
    postiz = config.get("postiz", {})
    if not postiz.get("apiKey"):
        issues = [*issues, "postiz.apiKey is empty"]

    integration_ids = postiz.get("integrationIds", {})
    if not integration_ids.get("tiktok"):
        issues = [*issues, "postiz.integrationIds.tiktok is empty"]

    if not integration_ids.get("instagram"):
        warnings = [*warnings, "postiz.integrationIds.instagram is empty (optional)"]

    # Check environment variables
    env_path = Path.home() / ".env"
    env_vars = {}
    if env_path.exists():
        with open(env_path) as f:
            env_vars = {
                line.strip().split("=", 1)[0]: True
                for line in f
                if "=" in line.strip() and not line.strip().startswith("#")
            }

    required_env = ["GEMINI_API_KEY"]
    issues = issues + [
        f"~/.env missing {var}"
        for var in required_env
        if var not in env_vars
    ]

    optional_env = ["CLOUDINARY_CLOUD_NAME", "CLOUDINARY_API_KEY", "CLOUDINARY_API_SECRET"]
    warnings = warnings + [
        f"~/.env missing {var} (needed for Instagram backup)"
        for var in optional_env
        if var not in env_vars
    ]

    # Check Pillow
    try:
        import PIL  # noqa: F401
        pillow_ok = True
    except ImportError:
        pillow_ok = False
        issues = [*issues, "Pillow not installed (pip install Pillow)"]

    return (issues, warnings, env_vars, pillow_ok)


def _print_validation_results(issues: list, warnings: list, env_vars: dict, pillow_ok: bool) -> int:
    """Print validation results and return completion percentage.

    Args:
        issues: list of critical problems
        warnings: list of non-critical recommendations
        env_vars: dict of found environment variable names
        pillow_ok: whether Pillow is importable

    Returns:
        Completion percentage (0-100)
    """
    print("=== Configuration Validation ===\n")

    if not issues:
        print("STATUS: READY")
    else:
        print("STATUS: INCOMPLETE")

    print(f"\nIssues ({len(issues)}):")
    if issues:
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("  None")

    print(f"\nWarnings ({len(warnings)}):")
    if warnings:
        for warning in warnings:
            print(f"  - {warning}")
    else:
        print("  None")

    print(f"\nDependencies:")
    print(f"  Pillow: {'OK' if pillow_ok else 'MISSING'}")
    print(f"  Gemini API Key: {'OK' if 'GEMINI_API_KEY' in env_vars else 'MISSING'}")

    # Completion percentage
    # app(4 required) + postiz(apiKey + tiktok = 2) + env(1 required) + pillow(1) = 8
    required_app_fields = ["name", "description", "audience", "problem"]
    required_env = ["GEMINI_API_KEY"]
    total_checks = len(required_app_fields) + 2 + len(required_env) + 1
    passed = total_checks - len(issues)
    pct = int(passed / total_checks * 100) if total_checks > 0 else 0
    print(f"\nCompletion: {pct}% ({passed}/{total_checks})")

    return pct


def validate_config() -> dict:
    """Validate config completeness and return status"""
    if not CONFIG_PATH.exists():
        print("Config not found. Run --init first.")
        return {"valid": False, "missing": ["config file"]}

    with open(CONFIG_PATH) as f:
        config = json.load(f)

    issues, warnings, env_vars, pillow_ok = _collect_validation_issues(config)
    pct = _print_validation_results(issues, warnings, env_vars, pillow_ok)

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "completion_pct": pct,
    }


def update_config(key: str, value: str) -> None:
    """Update a specific config value using dot notation"""
    if not CONFIG_PATH.exists():
        print("Config not found. Run --init first.")
        sys.exit(1)

    with open(CONFIG_PATH) as f:
        config = json.load(f)

    # Navigate dot notation (e.g., "app.name")
    keys = key.split(".")
    obj = config
    for k in keys[:-1]:
        if k not in obj:
            obj[k] = {}
        obj = obj[k]

    # Parse value type
    if value.lower() == "true":
        parsed_value = True
    elif value.lower() == "false":
        parsed_value = False
    elif value.startswith("[") and value.endswith("]"):
        try:
            parsed_value = json.loads(value)
        except json.JSONDecodeError:
            parsed_value = value
    else:
        parsed_value = value

    obj[keys[-1]] = parsed_value

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"Updated: {key} = {parsed_value}")


def migrate_config() -> None:
    """Migrate existing config to latest structure"""
    if not CONFIG_PATH.exists():
        print("Config not found. Run --init first.")
        return

    with open(CONFIG_PATH) as f:
        config = json.load(f)

    changes = []

    # Remove youtube from integrationIds
    integration_ids = config.get("postiz", {}).get("integrationIds", {})
    if "youtube" in integration_ids:
        del integration_ids["youtube"]
        changes.append("Removed: postiz.integrationIds.youtube")

    # Remove youtube from crossPost
    posting = config.get("posting", {})
    cross_post = posting.get("crossPost", [])
    if "youtube" in cross_post:
        posting["crossPost"] = [p for p in cross_post if p != "youtube"]
        changes.append("Removed: 'youtube' from posting.crossPost")

    # Add autoAddMusic if missing
    if "autoAddMusic" not in posting:
        posting["autoAddMusic"] = True
        changes.append("Added: posting.autoAddMusic = true")

    # Ensure timezone exists
    if "timezone" not in posting:
        posting["timezone"] = "Asia/Seoul"
        changes.append("Added: posting.timezone = Asia/Seoul")

    # Add sceneDescription if missing
    if "sceneDescription" not in config:
        config["sceneDescription"] = ""
        changes.append("Added: sceneDescription = ''")

    # Add posting.hookRegister if missing
    if "hookRegister" not in posting:
        posting["hookRegister"] = "diary"
        changes.append("Added: posting.hookRegister = diary")

    # Add posting.ctaType if missing
    if "ctaType" not in posting:
        posting["ctaType"] = "link_in_bio"
        changes.append("Added: posting.ctaType = link_in_bio")

    # Add conversion section if missing
    if "conversion" not in config:
        config["conversion"] = {
            "enabled": True,
            "trackingMethod": "manual",
            "linkClickSource": "bitly",
            "notes": "",
        }
        changes.append("Added: conversion section (enabled)")
    else:
        conversion = config["conversion"]
        # Ensure conversion is enabled
        if not conversion.get("enabled"):
            conversion["enabled"] = True
            changes.append("Updated: conversion.enabled = true")
        # Add linkClickSource if missing
        if "linkClickSource" not in conversion:
            conversion["linkClickSource"] = "bitly"
            changes.append("Added: conversion.linkClickSource = bitly")

    if not changes:
        print("Config is already up to date. No migration needed.")
        return

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print("=== Config Migration Complete ===\n")
    for change in changes:
        print(f"  {change}")
    print(f"\nUpdated: {CONFIG_PATH}")


def show_status() -> None:
    """Show current config status"""
    if not CONFIG_PATH.exists():
        print("Config not found. Run --init first.")
        return

    with open(CONFIG_PATH) as f:
        config = json.load(f)

    app = config.get("app", {})
    postiz = config.get("postiz", {})
    posting = config.get("posting", {})

    print("=== Social Slide Marketing Status ===\n")
    print(f"App: {app.get('name', '(not set)')}")
    print(f"Description: {app.get('description', '(not set)')}")
    print(f"Category: {app.get('category', '(not set)')}")
    print(f"Audience: {app.get('audience', '(not set)')}")
    print(f"URL: {app.get('url', '(not set)')}")

    print(f"\nPlatforms:")
    ids = postiz.get("integrationIds", {})
    print(f"  TikTok: {'Connected' if ids.get('tiktok') else 'Not connected'}")
    print(f"  Instagram: {'Connected' if ids.get('instagram') else 'Not connected'}")

    print(f"\nPosting:")
    print(f"  Schedule: {posting.get('schedule', [])}")
    print(f"  Privacy: {posting.get('privacyLevel', 'SELF_ONLY')}")
    print(f"  Timezone: {posting.get('timezone', 'Asia/Seoul')}")
    print(f"  Hook Register: {posting.get('hookRegister', 'diary')}")
    print(f"  CTA Type: {posting.get('ctaType', 'link_in_bio')}")

    conversion = config.get("conversion", {})
    print(f"\nConversion:")
    print(f"  Enabled: {conversion.get('enabled', False)}")
    print(f"  Tracking: {conversion.get('trackingMethod', 'manual')}")
    print(f"  Link Source: {conversion.get('linkClickSource', '(not set)')}")

    # Hook stats
    if HOOKS_PATH.exists():
        with open(HOOKS_PATH) as f:
            hooks_data = json.load(f)
        print(f"\nHooks: {len(hooks_data.get('hooks', []))} saved")

    # Performance stats
    if HOOK_PERFORMANCE_PATH.exists():
        with open(HOOK_PERFORMANCE_PATH) as f:
            perf_data = json.load(f)
        print(f"Performance records: {len(perf_data.get('performances', []))}")

    # Competitor stats
    if COMPETITOR_PATH.exists():
        with open(COMPETITOR_PATH) as f:
            comp_data = json.load(f)
        print(f"Competitors tracked: {len(comp_data.get('competitors', []))}")

    print(f"\nConfig: {CONFIG_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Social Slide Marketing - Onboarding & Config")
    parser.add_argument("--init", action="store_true", help="Initialize config directory and files")
    parser.add_argument("--validate", action="store_true", help="Validate config completeness")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--migrate", action="store_true", help="Migrate existing config to latest structure")
    parser.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="Update config value (dot notation)")

    args = parser.parse_args()

    if args.init:
        init_config()
    elif args.validate:
        result = validate_config()
        sys.exit(0 if result["valid"] else 1)
    elif args.migrate:
        migrate_config()
    elif args.status:
        show_status()
    elif args.set:
        update_config(args.set[0], args.set[1])
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

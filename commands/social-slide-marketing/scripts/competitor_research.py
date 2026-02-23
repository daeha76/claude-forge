#!/usr/bin/env python3
"""
경쟁사 데이터 관리
경쟁사 정보를 추가/조회/분석합니다.
외부 의존성 없음 (Python 표준 라이브러리만 사용)
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

CONFIG_DIR = Path.home() / ".social-slide-marketing"
COMPETITOR_PATH = CONFIG_DIR / "competitors.json"


def load_competitors() -> dict:
    """Load competitor data"""
    if not COMPETITOR_PATH.exists():
        return {"competitors": []}
    with open(COMPETITOR_PATH) as f:
        return json.load(f)


def save_competitors(data: dict) -> None:
    """Save competitor data"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(COMPETITOR_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def add_competitor(
    name: str,
    url: str = "",
    tiktok: str = "",
    instagram: str = "",
    notes: str = "",
) -> None:
    """Add or update a competitor"""
    data = load_competitors()

    # Check if already exists
    existing = next(
        (c for c in data["competitors"] if c["name"].lower() == name.lower()),
        None,
    )

    entry = {
        "name": name,
        "url": url,
        "tiktok": tiktok,
        "instagram": instagram,
        "notes": notes,
        "hooks": [],
        "added_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    if existing:
        # Preserve existing hooks
        entry["hooks"] = existing.get("hooks", [])
        entry["added_at"] = existing.get("added_at", entry["added_at"])
        # Update in place
        idx = data["competitors"].index(existing)
        data["competitors"][idx] = entry
        print(f"Updated: {name}")
    else:
        data["competitors"].append(entry)
        print(f"Added: {name}")

    save_competitors(data)


def add_hook(competitor_name: str, hook: str, views: str = "", notes: str = "") -> None:
    """Add a hook observation to a competitor"""
    data = load_competitors()

    competitor = next(
        (c for c in data["competitors"] if c["name"].lower() == competitor_name.lower()),
        None,
    )

    if not competitor:
        print(f"Competitor not found: {competitor_name}")
        print("Available:", ", ".join(c["name"] for c in data["competitors"]))
        sys.exit(1)

    hook_entry = {
        "text": hook,
        "views": views,
        "notes": notes,
        "date": datetime.now().isoformat(),
    }

    competitor.setdefault("hooks", []).append(hook_entry)
    competitor["updated_at"] = datetime.now().isoformat()

    save_competitors(data)
    print(f"Hook added to {competitor_name}: '{hook[:50]}...'")


def list_competitors() -> None:
    """List all tracked competitors"""
    data = load_competitors()
    competitors = data.get("competitors", [])

    if not competitors:
        print("No competitors tracked yet.")
        print("Add with: --action add --name 'CompetitorName' --url 'https://...'")
        return

    print(f"=== Tracked Competitors ({len(competitors)}) ===\n")

    for comp in competitors:
        hooks_count = len(comp.get("hooks", []))
        print(f"Name: {comp['name']}")
        if comp.get("url"):
            print(f"  URL: {comp['url']}")
        if comp.get("tiktok"):
            print(f"  TikTok: {comp['tiktok']}")
        if comp.get("instagram"):
            print(f"  Instagram: {comp['instagram']}")
        if comp.get("notes"):
            print(f"  Notes: {comp['notes']}")
        print(f"  Hooks tracked: {hooks_count}")
        print()


def show_hooks(competitor_name: str = "") -> None:
    """Show hooks for a competitor or all competitors"""
    data = load_competitors()

    if competitor_name:
        competitors = [
            c for c in data["competitors"]
            if c["name"].lower() == competitor_name.lower()
        ]
        if not competitors:
            print(f"Competitor not found: {competitor_name}")
            return
    else:
        competitors = data["competitors"]

    print("=== Competitor Hooks ===\n")

    for comp in competitors:
        hooks = comp.get("hooks", [])
        if not hooks:
            continue

        print(f"--- {comp['name']} ({len(hooks)} hooks) ---")
        for h in hooks:
            views_str = f" ({h['views']} views)" if h.get("views") else ""
            print(f"  - {h['text']}{views_str}")
            if h.get("notes"):
                print(f"    Note: {h['notes']}")
        print()


def analyze_patterns() -> None:
    """Analyze common patterns across competitor hooks"""
    data = load_competitors()
    all_hooks = []

    for comp in data["competitors"]:
        for hook in comp.get("hooks", []):
            all_hooks.append({
                "competitor": comp["name"],
                "text": hook["text"],
                "views": hook.get("views", ""),
            })

    if not all_hooks:
        print("No hooks recorded yet. Add hooks with --action add-hook")
        return

    print(f"=== Hook Pattern Analysis ({len(all_hooks)} hooks) ===\n")

    # Simple pattern detection
    patterns = {
        "question": 0,
        "number": 0,
        "negative": 0,
        "command": 0,
        "discovery": 0,
    }

    for hook in all_hooks:
        text = hook["text"].lower()
        if "?" in text or text.startswith(("why", "how", "what", "when", "왜", "어떻게")):
            patterns["question"] += 1
        if any(c.isdigit() for c in text):
            patterns["number"] += 1
        if any(w in text for w in ["stop", "don't", "never", "하지마", "그만", "절대"]):
            patterns["negative"] += 1
        if any(w in text for w in ["try", "use", "get", "써보", "해보", "다운"]):
            patterns["command"] += 1
        if any(w in text for w in ["found", "discovered", "발견", "찾았"]):
            patterns["discovery"] += 1

    print("Hook type distribution:")
    for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
        pct = round(count / len(all_hooks) * 100) if all_hooks else 0
        bar = "#" * (pct // 5)
        print(f"  {pattern:12s}: {count:3d} ({pct:2d}%) {bar}")

    print(f"\nTotal hooks analyzed: {len(all_hooks)}")
    print(f"Competitors: {len(data['competitors'])}")


def export_data() -> None:
    """Export competitor data as JSON"""
    data = load_competitors()
    print(json.dumps(data, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="Competitor research data management")
    parser.add_argument(
        "--action",
        required=True,
        choices=["add", "add-hook", "list", "hooks", "analyze", "export"],
        help="Action to perform",
    )
    parser.add_argument("--name", default="", help="Competitor name")
    parser.add_argument("--url", default="", help="Competitor website URL")
    parser.add_argument("--tiktok", default="", help="TikTok profile URL")
    parser.add_argument("--instagram", default="", help="Instagram profile URL")
    parser.add_argument("--notes", default="", help="Notes about the competitor")
    parser.add_argument("--hook", default="", help="Hook text to add")
    parser.add_argument("--views", default="", help="View count for the hook")

    args = parser.parse_args()

    if args.action == "add":
        if not args.name:
            print("--name required for add action")
            sys.exit(1)
        add_competitor(
            name=args.name,
            url=args.url,
            tiktok=args.tiktok,
            instagram=args.instagram,
            notes=args.notes,
        )
    elif args.action == "add-hook":
        if not args.name or not args.hook:
            print("--name and --hook required for add-hook action")
            sys.exit(1)
        add_hook(
            competitor_name=args.name,
            hook=args.hook,
            views=args.views,
            notes=args.notes,
        )
    elif args.action == "list":
        list_competitors()
    elif args.action == "hooks":
        show_hooks(args.name)
    elif args.action == "analyze":
        analyze_patterns()
    elif args.action == "export":
        export_data()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Postiz 분석 데이터 수집
포스트별 성과(조회수, 좋아요, 댓글, 공유)를 수집하고 훅 성과를 추적합니다.
외부 의존성 없음 (Python urllib만 사용)
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
import urllib.request
import urllib.error

POSTIZ_BASE_URL = "https://api.postiz.com/public/v1"
CONFIG_DIR = Path.home() / ".social-slide-marketing"
HOOK_PERFORMANCE_PATH = CONFIG_DIR / "hook-performance.json"
HOOK_RANKINGS_PATH = CONFIG_DIR / "hook-rankings.json"
HOOKS_PATH = CONFIG_DIR / "hooks.json"
PLATFORM_SNAPSHOTS_PATH = CONFIG_DIR / "platform-snapshots.json"

HOOK_FORMULA_PATTERNS = {
    "personConflict": ["I found", "찾았", "발견"],
    "discovery": ["Stop", "마세요", "하지마"],
    "pov": ["써봤", "using", "I've been"],
    "command": ["This app", "이 앱", "이거"],
    "socialProof": ["%", "만에", "results"],
}


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


def postiz_get(endpoint: str, api_key: str, params: dict = None) -> dict:
    """Make a GET request to Postiz API"""
    url = f"{POSTIZ_BASE_URL}{endpoint}"
    if params:
        import urllib.parse
        url += "?" + urllib.parse.urlencode(params)

    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
    }

    req = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"API Error {e.code}: {error_body[:300]}")
        return {"error": True, "status": e.code}
    except Exception as e:
        print(f"Request error: {e}")
        return {"error": True, "message": str(e)}


def get_recent_posts(api_key: str, days: int = 3) -> list:
    """Get recent posts from Postiz"""
    result = postiz_get("/posts", api_key)

    if result.get("error"):
        return []

    posts = result.get("data", result.get("posts", []))
    if not isinstance(posts, list):
        posts = [posts] if posts else []

    # Filter by date
    cutoff = datetime.now() - timedelta(days=days)
    recent = []
    for post in posts:
        created = post.get("createdAt", post.get("created_at", ""))
        if created:
            try:
                post_date = datetime.fromisoformat(created.replace("Z", "+00:00"))
                if post_date.replace(tzinfo=None) >= cutoff:
                    recent.append(post)
            except (ValueError, TypeError):
                recent.append(post)
        else:
            recent.append(post)

    return recent


def get_post_analytics(api_key: str, post_id: str) -> dict:
    """Get analytics for a specific post"""
    result = postiz_get(f"/posts/{post_id}/analytics", api_key)

    if result.get("error"):
        # Try alternative endpoint
        result = postiz_get(f"/posts/{post_id}", api_key)

    return result


def collect_analytics(config_path: str, days: int = 3) -> list:
    """Collect analytics for recent posts"""
    config = load_config(config_path)
    api_key = config.get("postiz", {}).get("apiKey", "")

    if not api_key:
        env_path = Path.home() / ".env"
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if line.strip().startswith("POSTIZ_API_KEY="):
                        api_key = line.strip().split("=", 1)[1].strip('"').strip("'")
                        break

    if not api_key:
        print("Postiz API key not found")
        return []

    print(f"Fetching posts from last {days} days...\n")
    posts = get_recent_posts(api_key, days)

    if not posts:
        print("No recent posts found")
        return []

    print(f"Found {len(posts)} posts\n")

    analytics = []
    for i, post in enumerate(posts):
        post_id = post.get("id", "")
        title = post.get("title", post.get("content", ""))[:50]
        print(f"Post {i + 1}: {title}...")

        # Get analytics
        post_analytics = get_post_analytics(api_key, post_id)

        entry = {
            "post_id": post_id,
            "title": title,
            "created_at": post.get("createdAt", ""),
            "platforms": [],
            "metrics": {
                "views": 0,
                "likes": 0,
                "comments": 0,
                "shares": 0,
            },
        }

        # Extract metrics from analytics response
        if not post_analytics.get("error"):
            metrics = post_analytics.get("analytics", post_analytics.get("metrics", {}))
            if isinstance(metrics, dict):
                entry["metrics"]["views"] = metrics.get("views", metrics.get("impressions", 0))
                entry["metrics"]["likes"] = metrics.get("likes", metrics.get("reactions", 0))
                entry["metrics"]["comments"] = metrics.get("comments", 0)
                entry["metrics"]["shares"] = metrics.get("shares", metrics.get("reposts", 0))

            # Extract platform info
            integrations = post.get("integrations", post.get("posts", []))
            if isinstance(integrations, list):
                for integration in integrations:
                    platform = integration.get("type", integration.get("platform", "unknown"))
                    entry["platforms"].append(platform)

        analytics.append(entry)
        print(f"  Views: {entry['metrics']['views']:,} | Likes: {entry['metrics']['likes']:,} | "
              f"Comments: {entry['metrics']['comments']:,} | Shares: {entry['metrics']['shares']:,}")

    return analytics


def update_hook_performance(analytics: list) -> None:
    """Update hook performance tracking file"""
    if not HOOK_PERFORMANCE_PATH.exists():
        perf_data = {"performances": []}
    else:
        with open(HOOK_PERFORMANCE_PATH) as f:
            perf_data = json.load(f)

    for entry in analytics:
        perf_entry = {
            "post_id": entry["post_id"],
            "hook": entry["title"],
            "date": entry.get("created_at", datetime.now().isoformat()),
            "views": entry["metrics"]["views"],
            "likes": entry["metrics"]["likes"],
            "comments": entry["metrics"]["comments"],
            "shares": entry["metrics"]["shares"],
            "engagement_rate": 0,
        }

        views = entry["metrics"]["views"]
        if views > 0:
            total_engagement = (
                entry["metrics"]["likes"]
                + entry["metrics"]["comments"]
                + entry["metrics"]["shares"]
            )
            perf_entry["engagement_rate"] = round(total_engagement / views * 100, 2)

        # Update or add (immutable rebuild)
        updated_performances = []
        found = False
        for p in perf_data["performances"]:
            if p["post_id"] == entry["post_id"]:
                updated_performances.append(perf_entry)
                found = True
            else:
                updated_performances.append(p)
        if not found:
            updated_performances.append(perf_entry)
        perf_data = {**perf_data, "performances": updated_performances}

    with open(HOOK_PERFORMANCE_PATH, "w") as f:
        json.dump(perf_data, f, indent=2, ensure_ascii=False)

    print(f"\nHook performance updated: {HOOK_PERFORMANCE_PATH}")


def detect_hook_formula(hook_text: str) -> str:
    """Detect hook formula pattern from hook text using keyword matching"""
    if not hook_text or not isinstance(hook_text, str):
        return "unknown"

    for formula, keywords in HOOK_FORMULA_PATTERNS.items():
        for keyword in keywords:
            if keyword in hook_text:
                return formula

    return "unknown"


def _compute_formula_stats(performances: list) -> tuple:
    """Group performances by formula and compute per-formula stats.
    Returns (formula_groups dict, global_avg_views, global_avg_engagement).
    """
    if not performances:
        return {}, 0, 0.0

    total_views = sum(p.get("views", 0) for p in performances)
    total_engagement = sum(p.get("engagement_rate", 0) for p in performances)
    count = len(performances)
    global_avg_views = total_views / count if count > 0 else 0
    global_avg_engagement = round(total_engagement / count, 2) if count > 0 else 0.0

    groups = {}
    for perf in performances:
        formula = detect_hook_formula(perf.get("hook", ""))
        existing = groups.get(formula, {"views_sum": 0, "engagement_sum": 0.0, "count": 0})
        groups[formula] = {
            "views_sum": existing["views_sum"] + perf.get("views", 0),
            "engagement_sum": existing["engagement_sum"] + perf.get("engagement_rate", 0),
            "count": existing["count"] + 1,
        }

    return groups, global_avg_views, global_avg_engagement


def _apply_tier_changes(formula_name: str, stats: dict, global_avg_views: float, current_tier: str) -> str:
    """Determine tier for a formula based on performance vs global average."""
    avg_views = stats.get("avg_views", 0)
    count = stats.get("count", 0)

    if avg_views > global_avg_views and count >= 3:
        if current_tier == "tier3":
            return "tier2"
        if current_tier == "tier2":
            return "tier1"
    if avg_views < global_avg_views * 0.5 and count >= 5:
        if current_tier == "tier1":
            return "tier2"
        if current_tier == "tier2":
            return "tier3"

    return current_tier


def _load_current_tiers(hooks_data: dict) -> dict:
    """Build a formula->tier mapping from current hooks.json data."""
    tiers = {}
    for formula_text in hooks_data.get("tier1_formulas", []):
        key = detect_hook_formula(formula_text)
        if key != "unknown":
            tiers[key] = "tier1"
    for formula_text in hooks_data.get("tier2_formulas", []):
        key = detect_hook_formula(formula_text)
        if key != "unknown":
            tiers[key] = "tier2"
    for formula_text in hooks_data.get("tier3_formulas", []):
        key = detect_hook_formula(formula_text)
        if key != "unknown":
            tiers[key] = "tier3"
    return tiers


def _update_hooks_tiers(hooks_data: dict, formula_results: dict) -> dict:
    """Return new hooks.json data with formulas moved between tiers."""
    tier1 = list(hooks_data.get("tier1_formulas", []))
    tier2 = list(hooks_data.get("tier2_formulas", []))
    tier3 = list(hooks_data.get("tier3_formulas", []))

    for formula_name, info in formula_results.items():
        target_tier = info.get("tier", "tier2")
        for formula_text in tier1 + tier2 + tier3:
            if detect_hook_formula(formula_text) == formula_name:
                # Remove from all tiers
                tier1 = [t for t in tier1 if t != formula_text]
                tier2 = [t for t in tier2 if t != formula_text]
                tier3 = [t for t in tier3 if t != formula_text]
                # Add to correct tier
                if target_tier == "tier1":
                    tier1.append(formula_text)
                elif target_tier == "tier3":
                    tier3.append(formula_text)
                else:
                    tier2.append(formula_text)

    return {
        **hooks_data,
        "tier1_formulas": tier1,
        "tier2_formulas": tier2,
        "tier3_formulas": tier3,
    }


def rank_hook_formulas() -> dict:
    """Rank hook formulas by performance, auto-promote/demote, and save rankings."""
    try:
        perf_data = {}
        if HOOK_PERFORMANCE_PATH.exists():
            with open(HOOK_PERFORMANCE_PATH) as f:
                perf_data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error loading hook performance: {e}")
        return {}

    performances = perf_data.get("performances", [])
    if not performances:
        print("No hook performance data found")
        return {}

    groups, global_avg_views, global_avg_engagement = _compute_formula_stats(performances)

    # Load current tier assignments
    hooks_data = {}
    try:
        if HOOKS_PATH.exists():
            with open(HOOKS_PATH) as f:
                hooks_data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error loading hooks: {e}")

    current_tiers = _load_current_tiers(hooks_data)

    # Build formula results with tier changes
    formula_results = {}
    promotions = []
    demotions = []

    for formula, group in groups.items():
        avg_views = group["views_sum"] / group["count"] if group["count"] > 0 else 0
        avg_engagement = round(group["engagement_sum"] / group["count"], 2) if group["count"] > 0 else 0.0
        current_tier = current_tiers.get(formula, "tier2")

        stats = {"avg_views": avg_views, "avg_engagement": avg_engagement, "count": group["count"]}
        new_tier = _apply_tier_changes(formula, stats, global_avg_views, current_tier)

        if new_tier != current_tier:
            tier_rank = {"tier1": 1, "tier2": 2, "tier3": 3}
            is_promotion = tier_rank.get(new_tier, 2) < tier_rank.get(current_tier, 2)
            direction = "promoted" if is_promotion else "demoted"
            change_str = f"{formula} {direction} {current_tier}\u2192{new_tier}"
            if is_promotion:
                promotions.append(change_str)
            else:
                demotions.append(change_str)

        formula_results[formula] = {
            "avg_views": round(avg_views),
            "avg_engagement": avg_engagement,
            "count": group["count"],
            "tier": new_tier,
        }

    rankings = {
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "global_avg_views": round(global_avg_views),
        "global_avg_engagement": global_avg_engagement,
        "formulas": formula_results,
        "promotions": promotions,
        "demotions": demotions,
    }

    # Save rankings
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(HOOK_RANKINGS_PATH, "w") as f:
            json.dump(rankings, f, indent=2, ensure_ascii=False)
        print(f"Hook rankings saved: {HOOK_RANKINGS_PATH}")
    except OSError as e:
        print(f"Error saving rankings: {e}")

    # Update hooks.json tiers
    if hooks_data:
        try:
            updated_hooks = _update_hooks_tiers(hooks_data, formula_results)
            with open(HOOKS_PATH, "w") as f:
                json.dump(updated_hooks, f, indent=2, ensure_ascii=False)
            print(f"Hooks tiers updated: {HOOKS_PATH}")
        except OSError as e:
            print(f"Error updating hooks: {e}")

    return rankings


def track_platform_deltas(api_key: str) -> dict:
    """Track platform-level deltas by comparing snapshots over time."""
    if not api_key:
        print("API key required for platform delta tracking")
        return {}

    # Fetch current integration stats
    current_stats = postiz_get("/integrations", api_key)
    if current_stats.get("error"):
        print("Failed to fetch integration stats")
        return {}

    now = datetime.now().isoformat(timespec="seconds")
    snapshot = {"timestamp": now, "integrations": current_stats}

    # Load previous snapshots
    previous_snapshots = []
    try:
        if PLATFORM_SNAPSHOTS_PATH.exists():
            with open(PLATFORM_SNAPSHOTS_PATH) as f:
                previous_snapshots = json.load(f).get("snapshots", [])
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error loading snapshots: {e}")

    # Calculate deltas against last snapshot
    deltas = _compute_platform_deltas(previous_snapshots, current_stats)

    # Save updated snapshots (keep last 30)
    updated_snapshots = list(previous_snapshots) + [snapshot]
    if len(updated_snapshots) > 30:
        updated_snapshots = updated_snapshots[-30:]

    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(PLATFORM_SNAPSHOTS_PATH, "w") as f:
            json.dump({"snapshots": updated_snapshots}, f, indent=2, ensure_ascii=False)
        print(f"Platform snapshot saved: {PLATFORM_SNAPSHOTS_PATH}")
    except OSError as e:
        print(f"Error saving snapshot: {e}")

    return deltas


def _compute_platform_deltas(previous_snapshots: list, current_stats: dict) -> dict:
    """Compute follower and view deltas between current and last snapshot."""
    if not previous_snapshots:
        return {"first_snapshot": True, "deltas": {}}

    last = previous_snapshots[-1].get("integrations", {})
    deltas = {}

    current_items = current_stats if isinstance(current_stats, list) else current_stats.get("data", [])
    last_items = last if isinstance(last, list) else last.get("data", [])

    if not isinstance(current_items, list) or not isinstance(last_items, list):
        return {"deltas": {}}

    last_by_id = {item.get("id", ""): item for item in last_items}

    for item in current_items:
        item_id = item.get("id", "")
        platform = item.get("type", item.get("platform", "unknown"))
        current_followers = item.get("followers", item.get("followerCount", 0))
        current_views = item.get("views", item.get("totalViews", 0))

        prev = last_by_id.get(item_id, {})
        prev_followers = prev.get("followers", prev.get("followerCount", 0))
        prev_views = prev.get("views", prev.get("totalViews", 0))

        deltas[platform] = {
            "follower_change": current_followers - prev_followers,
            "views_change": current_views - prev_views,
            "current_followers": current_followers,
            "current_views": current_views,
        }

    return {"deltas": deltas}


def diagnose_post(metrics: dict) -> dict:
    """Apply diagnostic framework to a post"""
    views = metrics.get("views", 0)
    engagement = metrics.get("likes", 0) + metrics.get("comments", 0) + metrics.get("shares", 0)

    high_views = views >= 50000
    medium_views = views >= 10000

    engagement_rate = (engagement / views * 100) if views > 0 else 0
    high_engagement = engagement_rate >= 3.0

    if high_views and high_engagement:
        return {
            "diagnosis": "SCALE IT",
            "action": "동일 훅으로 변형 3개 제작. 예산 투입 고려.",
            "priority": "high",
        }
    elif high_views and not high_engagement:
        return {
            "diagnosis": "FIX CTA",
            "action": "CTA 슬라이드/캡션 변경. 바이오 링크 최적화.",
            "priority": "medium",
        }
    elif medium_views and high_engagement:
        return {
            "diagnosis": "BOOST",
            "action": "유료 프로모션 집행. 리포스트/듀엣 유도. 게시 시간 최적화.",
            "priority": "medium",
        }
    elif not high_views and not medium_views and high_engagement:
        return {
            "diagnosis": "FIX HOOKS",
            "action": "훅 교체. 첫 장 이미지 변경. 게시 시간 최적화.",
            "priority": "medium",
        }
    elif medium_views:
        return {
            "diagnosis": "OPTIMIZE",
            "action": "훅과 CTA 소폭 조정. A/B 테스트 실행.",
            "priority": "low",
        }
    else:
        return {
            "diagnosis": "FULL RESET",
            "action": "새 앵글 시도. 경쟁사 재분석. 타겟 재정의.",
            "priority": "high",
        }


def main():
    parser = argparse.ArgumentParser(description="Collect and analyze Postiz post analytics")
    parser.add_argument("--config", default=str(CONFIG_DIR / "config.json"), help="Path to config.json")
    parser.add_argument("--days", type=int, default=3, help="Number of days to look back")
    parser.add_argument("--update-performance", action="store_true", help="Update hook performance file")
    parser.add_argument("--rank-formulas", action="store_true", help="Rank hook formulas by performance")

    args = parser.parse_args()

    if args.rank_formulas:
        rankings = rank_hook_formulas()
        if rankings:
            print(f"\n{json.dumps(rankings, indent=2, ensure_ascii=False)}")
        return

    analytics = collect_analytics(args.config, args.days)

    if not analytics:
        sys.exit(1)

    # Diagnose each post
    print("\n=== Diagnostics ===\n")
    for entry in analytics:
        diagnosis = diagnose_post(entry["metrics"])
        entry = {**entry, "diagnosis": diagnosis}
        print(f"{entry['title'][:40]}...")
        print(f"  {diagnosis['diagnosis']}: {diagnosis['action']}")
        print()

    if args.update_performance:
        update_hook_performance(analytics)
        print("\nRanking hook formulas...")
        rankings = rank_hook_formulas()
        if rankings.get("promotions") or rankings.get("demotions"):
            print("\n=== Tier Changes ===")
            for p in rankings.get("promotions", []):
                print(f"  [UP] {p}")
            for d in rankings.get("demotions", []):
                print(f"  [DOWN] {d}")

    # Output JSON
    print(f"\nJSON: {json.dumps(analytics, ensure_ascii=False)}")


if __name__ == "__main__":
    main()

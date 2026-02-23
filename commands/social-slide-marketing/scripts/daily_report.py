#!/usr/bin/env python3
"""
일일 분석 리포트
Postiz 분석 데이터를 기반으로 진단 프레임워크를 적용하고 리포트를 생성합니다.
외부 의존성 없음 (Python 표준 라이브러리만 사용)
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

CONFIG_DIR = Path.home() / ".social-slide-marketing"
CONFIG_PATH = CONFIG_DIR / "config.json"
HOOK_PERFORMANCE_PATH = CONFIG_DIR / "hook-performance.json"
HOOKS_PATH = CONFIG_DIR / "hooks.json"
HOOK_RANKINGS_PATH = CONFIG_DIR / "hook-rankings.json"
LEARNINGS_PATH = CONFIG_DIR / "learnings.json"

# Funnel thresholds
VIEWS_HIGH = 50000
VIEWS_MEDIUM = 10000
CTR_GOOD = 2.0
CTR_BAD = 1.0
CONVERSION_GOOD = 5.0
CONVERSION_BAD = 2.0


def load_json(path: Path) -> dict:
    """Load JSON file safely"""
    if not path.exists():
        return {}
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error loading {path}: {e}")
        return {}


def get_analytics_data(config_path: str, days: int = 3) -> list:
    """Collect analytics via check_analytics module"""
    scripts_dir = Path(__file__).parent
    check_analytics_path = scripts_dir / "check_analytics.py"

    if not check_analytics_path.exists():
        print("check_analytics.py not found")
        return []

    # Import and use check_analytics
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("check_analytics", str(check_analytics_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.collect_analytics(config_path, days)
    except Exception as e:
        print(f"Failed to load check_analytics module: {e}")
        return []


def analyze_hook_performance() -> dict:
    """Analyze historical hook performance"""
    perf_data = load_json(HOOK_PERFORMANCE_PATH)
    performances = perf_data.get("performances", [])

    if not performances:
        return {"top_hooks": [], "worst_hooks": [], "avg_views": 0, "avg_engagement": 0}

    # Sort by views
    sorted_by_views = sorted(performances, key=lambda p: p.get("views", 0), reverse=True)

    # Calculate averages
    total_views = sum(p.get("views", 0) for p in performances)
    total_engagement = sum(p.get("engagement_rate", 0) for p in performances)
    count = len(performances)

    avg_views = total_views // count if count > 0 else 0
    avg_engagement = round(total_engagement / count, 2) if count > 0 else 0

    return {
        "top_hooks": sorted_by_views[:3],
        "worst_hooks": sorted_by_views[-3:] if len(sorted_by_views) > 3 else [],
        "avg_views": avg_views,
        "avg_engagement": avg_engagement,
        "total_posts": count,
    }


def suggest_cta_rotation(analytics: list) -> list:
    """Suggest CTA rotations based on performance"""
    cta_options = [
        {"cta": "Link in bio", "ko": "바이오 링크 클릭", "best_for": "direct traffic"},
        {"cta": "Comment [keyword]", "ko": "댓글에 [키워드] 남기세요", "best_for": "engagement boost"},
        {"cta": "DM me [keyword]", "ko": "DM으로 [키워드] 보내주세요", "best_for": "lead gen"},
        {"cta": "Follow for more", "ko": "팔로우하면 더 알려드려요", "best_for": "follower growth"},
        {"cta": "Save this for later", "ko": "나중에 볼 수 있게 저장하세요", "best_for": "saves/bookmarks"},
    ]

    suggestions = []
    for entry in analytics:
        diagnosis = entry.get("diagnosis", {})
        diag_type = diagnosis.get("diagnosis", "")

        if diag_type == "FIX CTA":
            suggestions.append({
                "post": entry.get("title", "")[:40],
                "current_issue": "높은 조회수, 낮은 전환",
                "try_next": [cta_options[1], cta_options[2]],
            })
        elif diag_type == "SCALE IT":
            suggestions.append({
                "post": entry.get("title", "")[:40],
                "current_issue": "잘 되고 있음",
                "try_next": [cta_options[0]],
            })

    return suggestions


def suggest_new_hooks(hook_analysis: dict) -> list:
    """Suggest new hooks based on performance data"""
    hooks_data = load_json(HOOKS_PATH)
    top_hooks = hook_analysis.get("top_hooks", [])

    suggestions = []

    if top_hooks:
        best_hook = top_hooks[0].get("hook", "")
        suggestions.append({
            "type": "variation",
            "reason": f"Best performer: '{best_hook[:30]}...'",
            "suggestion": f"이 훅의 변형 3개를 만들어보세요",
        })

    # Suggest from formulas
    tier1 = hooks_data.get("tier1_formulas", [])
    if tier1:
        suggestions.append({
            "type": "formula",
            "reason": "검증된 Tier 1 공식",
            "suggestion": f"다음 공식 시도: '{tier1[0]}'",
        })

    avg_views = hook_analysis.get("avg_views", 0)
    if avg_views < 10000:
        suggestions.append({
            "type": "reset",
            "reason": f"평균 조회수 {avg_views:,}회로 낮음",
            "suggestion": "완전히 새로운 앵글로 접근. 경쟁사 최신 트렌드 재분석.",
        })

    return suggestions


def diagnose_funnel(total_views: int, link_clicks: int, conversions: int) -> dict:
    """3-layer funnel diagnosis: Views -> Clicks -> Conversions."""
    ctr = (link_clicks / total_views * 100) if total_views > 0 else 0.0
    conv_rate = (conversions / link_clicks * 100) if link_clicks > 0 else 0.0

    if total_views < VIEWS_MEDIUM:
        diagnosis = "도달이 부족. 훅 교체, 게시 시간 최적화, 해시태그 전략 재검토."
        bottleneck = "views"
    elif ctr < CTR_BAD:
        diagnosis = "훅은 좋지만 CTA가 약함. CTA 슬라이드와 캡션 개선 필요."
        bottleneck = "cta"
    elif link_clicks > 0 and conv_rate < CONVERSION_BAD:
        diagnosis = "트래픽은 오지만 랜딩/앱에서 이탈. 랜딩 페이지 또는 앱 온보딩 개선 필요."
        bottleneck = "landing"
    else:
        diagnosis = "퍼널 건강. 현재 전략 유지하면서 볼륨 확대."
        bottleneck = "none"

    return {
        "diagnosis": diagnosis,
        "bottleneck": bottleneck,
        "metrics": {
            "total_views": total_views,
            "link_clicks": link_clicks,
            "conversions": conversions,
            "ctr": round(ctr, 2),
            "conversion_rate": round(conv_rate, 2),
        },
    }


def _get_funnel_totals(performances: list, input_clicks: int, input_conversions: int) -> tuple:
    """Sum funnel metrics from performances, with optional manual overrides."""
    total_views = sum(p.get("views", 0) for p in performances)
    total_clicks = sum(p.get("link_clicks", 0) for p in performances)
    total_conversions = sum(p.get("conversions", 0) for p in performances)

    if input_clicks > 0:
        total_clicks = input_clicks
    if input_conversions > 0:
        total_conversions = input_conversions

    return total_views, total_clicks, total_conversions


def auto_generate_hook_variations(hook_text: str) -> list:
    """Generate 3 concrete hook text variations from a top performer."""
    if not hook_text or not isinstance(hook_text, str):
        return []

    variations = []

    # Variation 1: Swap benefit/result with timeframe
    variation1 = _swap_benefit_timeframe(hook_text)
    variations.append(variation1)

    # Variation 2: Change the outcome
    variation2 = _change_outcome(hook_text)
    variations.append(variation2)

    # Variation 3: Change perspective (1st → 3rd person)
    variation3 = _change_perspective(hook_text)
    variations.append(variation3)

    return variations


def _swap_benefit_timeframe(hook_text: str) -> str:
    """Create variation by adding/changing a timeframe element."""
    timeframes = ["3개월", "일주일", "2주", "한 달"]
    for tf in timeframes:
        if tf in hook_text:
            continue
        # Insert timeframe before key verb patterns
        for verb in ["써봤", "using", "사용", "해봤"]:
            if verb in hook_text:
                return hook_text.replace(verb, f"{tf} {verb}", 1)
        # Fallback: prepend timeframe
        return f"{timeframes[0]} {hook_text}"
    return f"{timeframes[1]} 동안 {hook_text}"


def _change_outcome(hook_text: str) -> str:
    """Create variation by swapping the outcome/result phrase."""
    outcome_swaps = {
        "인생 바뀜": "야근이 사라짐",
        "대박": "미쳤음",
        "바뀜": "달라짐",
        "changed my life": "saved me hours",
        "대박임": "효율 200% 올라감",
        "진짜": "ㄹㅇ",
        "좋음": "대박임",
    }
    result = hook_text
    for old, new in outcome_swaps.items():
        if old in result:
            return result.replace(old, new, 1)
    # Fallback: append an outcome
    return f"{hook_text} ㄹㅇ 대박"


def _change_perspective(hook_text: str) -> str:
    """Create variation by switching 1st person to 3rd person."""
    perspective_swaps = {
        "내가": "친구가",
        "나는": "동료가",
        "I found": "My friend found",
        "I've been": "Everyone's been",
        "써봤는데": "추천해줬는데",
        "찾았": "알려줬",
    }
    result = hook_text
    for old, new in perspective_swaps.items():
        if old in result:
            return result.replace(old, new, 1)
    # Fallback: prepend third-person frame
    return f"친구가 {hook_text.lstrip('나는 내가 ')}"


def _analyze_hook_length_pattern(performances: list) -> dict:
    """Analyze short vs long hook performance."""
    short_hooks = [p for p in performances if len(p.get("hook", "").split()) <= 4]
    long_hooks = [p for p in performances if len(p.get("hook", "").split()) > 6]

    short_avg = sum(p.get("views", 0) for p in short_hooks) / len(short_hooks) if short_hooks else 0
    long_avg = sum(p.get("views", 0) for p in long_hooks) / len(long_hooks) if long_hooks else 0

    if short_avg > 0 and long_avg > 0:
        ratio = round(short_avg / long_avg, 1) if long_avg > 0 else 0
        return {"short_avg": round(short_avg), "long_avg": round(long_avg), "ratio": ratio}
    return {}


def _analyze_language_pattern(performances: list) -> dict:
    """Analyze Korean vs English hook performance."""
    korean = [p for p in performances if any('\uac00' <= c <= '\ud7a3' for c in p.get("hook", ""))]
    english = [p for p in performances if not any('\uac00' <= c <= '\ud7a3' for c in p.get("hook", ""))]

    ko_avg = sum(p.get("views", 0) for p in korean) / len(korean) if korean else 0
    en_avg = sum(p.get("views", 0) for p in english) / len(english) if english else 0

    return {"korean_avg_views": round(ko_avg), "english_avg_views": round(en_avg)}


def record_learning(performances: list) -> list:
    """Analyze worst hooks and record failure patterns to learnings.json."""
    if not performances or len(performances) < 3:
        return []

    sorted_perfs = sorted(performances, key=lambda p: p.get("views", 0))
    worst = sorted_perfs[:3]
    new_learnings = []

    # Length pattern analysis
    length_stats = _analyze_hook_length_pattern(performances)
    if length_stats.get("ratio", 0) > 1.5:
        new_learnings.append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "hook_failure",
            "pattern": "command formula with long text",
            "lesson": f"4단어 이하 훅이 6단어 이상보다 평균 {length_stats['ratio']}배 조회수 높음",
            "source_posts": [p.get("post_id", "") for p in worst],
        })

    # Language pattern analysis
    lang_stats = _analyze_language_pattern(performances)
    if lang_stats["korean_avg_views"] > 0 and lang_stats["english_avg_views"] > 0:
        better = "한국어" if lang_stats["korean_avg_views"] > lang_stats["english_avg_views"] else "영어"
        new_learnings.append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "language_pattern",
            "pattern": "korean vs english hooks",
            "lesson": f"{better} 훅이 더 높은 조회수 (KO: {lang_stats['korean_avg_views']:,}, EN: {lang_stats['english_avg_views']:,})",
            "source_posts": [p.get("post_id", "") for p in worst],
        })

    # Question vs statement pattern
    questions = [p for p in performances if "?" in p.get("hook", "")]
    statements = [p for p in performances if "?" not in p.get("hook", "")]
    if questions and statements:
        q_avg = sum(p.get("views", 0) for p in questions) / len(questions)
        s_avg = sum(p.get("views", 0) for p in statements) / len(statements)
        if abs(q_avg - s_avg) > 5000:
            better_type = "질문형" if q_avg > s_avg else "서술형"
            new_learnings.append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "type": "hook_style",
                "pattern": "question vs statement",
                "lesson": f"{better_type} 훅이 평균 {abs(round(q_avg - s_avg)):,}회 더 높은 조회수",
                "source_posts": [p.get("post_id", "") for p in worst[:2]],
            })

    # Save learnings
    _save_learnings(new_learnings)

    return new_learnings


def _save_learnings(new_learnings: list) -> None:
    """Append new learnings to learnings.json without mutating existing data."""
    if not new_learnings:
        return

    existing = {"learnings": []}
    try:
        if LEARNINGS_PATH.exists():
            with open(LEARNINGS_PATH) as f:
                existing = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error loading learnings: {e}")

    updated = {**existing, "learnings": list(existing.get("learnings", [])) + new_learnings}

    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LEARNINGS_PATH, "w") as f:
            json.dump(updated, f, indent=2, ensure_ascii=False)
        print(f"Learnings saved: {LEARNINGS_PATH}")
    except OSError as e:
        print(f"Error saving learnings: {e}")


def _build_funnel_section(funnel_result: dict) -> list:
    """Build report lines for funnel diagnosis section."""
    lines = [
        "## 퍼널 진단",
        "",
    ]
    metrics = funnel_result.get("metrics", {})
    lines.append(f"- 총 조회수: {metrics.get('total_views', 0):,}")
    lines.append(f"- 링크 클릭: {metrics.get('link_clicks', 0):,} (CTR: {metrics.get('ctr', 0)}%)")
    lines.append(f"- 전환: {metrics.get('conversions', 0):,} (전환율: {metrics.get('conversion_rate', 0)}%)")
    lines.append(f"- 병목: **{funnel_result.get('bottleneck', 'N/A')}**")
    lines.append(f"- 진단: {funnel_result.get('diagnosis', 'N/A')}")
    lines.append("")
    return lines


def _build_rankings_section() -> list:
    """Build report lines for hook formula rankings section."""
    lines = ["## 훅 공식 랭킹", ""]

    try:
        if not HOOK_RANKINGS_PATH.exists():
            lines.append("랭킹 데이터 없음 (check_analytics.py --rank-formulas 실행 필요)")
            lines.append("")
            return lines

        with open(HOOK_RANKINGS_PATH) as f:
            rankings = json.load(f)
    except (json.JSONDecodeError, OSError):
        lines.append("랭킹 데이터 로드 실패")
        lines.append("")
        return lines

    lines.append(f"글로벌 평균 조회수: {rankings.get('global_avg_views', 0):,}")
    lines.append(f"글로벌 평균 참여율: {rankings.get('global_avg_engagement', 0)}%")
    lines.append("")
    lines.append("| 공식 | 평균 조회수 | 평균 참여율 | 포스트 수 | 티어 |")
    lines.append("|------|-----------|-----------|----------|------|")

    for formula, info in rankings.get("formulas", {}).items():
        lines.append(
            f"| {formula} | {info.get('avg_views', 0):,} "
            f"| {info.get('avg_engagement', 0)}% "
            f"| {info.get('count', 0)} "
            f"| {info.get('tier', 'N/A')} |"
        )
    lines.append("")

    for change in rankings.get("promotions", []):
        lines.append(f"- [UP] {change}")
    for change in rankings.get("demotions", []):
        lines.append(f"- [DOWN] {change}")
    if rankings.get("promotions") or rankings.get("demotions"):
        lines.append("")

    return lines


def _build_hook_variations_section(top_hooks: list) -> list:
    """Build report lines for auto-generated hook variations."""
    lines = ["## 자동 생성 훅 변형", ""]

    if not top_hooks:
        lines.append("탑 훅 데이터 없음")
        lines.append("")
        return lines

    best_hook = top_hooks[0].get("hook", "")
    if not best_hook:
        lines.append("훅 텍스트 없음")
        lines.append("")
        return lines

    lines.append(f"**원본 (Best):** {best_hook}")
    lines.append("")

    variations = auto_generate_hook_variations(best_hook)
    for i, var in enumerate(variations, 1):
        lines.append(f"{i}. {var}")
    lines.append("")

    return lines


def _build_learnings_section() -> list:
    """Build report lines for recent learnings."""
    lines = ["## 학습 기록", ""]

    try:
        if not LEARNINGS_PATH.exists():
            lines.append("학습 기록 없음")
            lines.append("")
            return lines

        with open(LEARNINGS_PATH) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        lines.append("학습 기록 로드 실패")
        lines.append("")
        return lines

    learnings = data.get("learnings", [])
    recent = learnings[-5:] if len(learnings) > 5 else learnings

    if not recent:
        lines.append("학습 기록 없음")
        lines.append("")
        return lines

    for entry in recent:
        lines.append(f"- **[{entry.get('date', '')}] {entry.get('type', '')}**: {entry.get('lesson', '')}")
    lines.append("")

    return lines


def _store_manual_funnel_inputs(input_clicks: int, input_conversions: int) -> None:
    """Store manual click/conversion inputs in the latest performance records."""
    if input_clicks <= 0 and input_conversions <= 0:
        return

    try:
        if not HOOK_PERFORMANCE_PATH.exists():
            return

        with open(HOOK_PERFORMANCE_PATH) as f:
            perf_data = json.load(f)

        performances = perf_data.get("performances", [])
        if not performances:
            return

        # Update latest entry immutably
        latest = performances[-1]
        updated_latest = {**latest}
        if input_clicks > 0:
            updated_latest["link_clicks"] = input_clicks
        if input_conversions > 0:
            updated_latest["conversions"] = input_conversions

        updated_performances = list(performances[:-1]) + [updated_latest]
        updated_data = {**perf_data, "performances": updated_performances}

        with open(HOOK_PERFORMANCE_PATH, "w") as f:
            json.dump(updated_data, f, indent=2, ensure_ascii=False)
        print(f"Manual funnel inputs stored (clicks={input_clicks}, conversions={input_conversions})")
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error storing manual inputs: {e}")


def _collect_report_data(config_path: str, report_days: int,
                         input_clicks: int, input_conversions: int) -> dict:
    """Collect all data needed for the report without side effects on report content.

    Returns a dict with keys:
        analytics, hook_analysis, cta_suggestions, hook_suggestions,
        funnel_result, new_learnings
    """
    # Store manual funnel inputs if provided
    _store_manual_funnel_inputs(input_clicks, input_conversions)

    # Collect analytics data
    print(f"Collecting analytics data ({report_days} days)...\n")
    analytics = get_analytics_data(config_path, report_days)

    # Enrich analytics with diagnose_post from check_analytics
    scripts_dir = Path(__file__).parent
    check_analytics_path = scripts_dir / "check_analytics.py"
    if check_analytics_path.exists():
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("check_analytics", str(check_analytics_path))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            analytics = [
                {**entry, "diagnosis": module.diagnose_post(entry.get("metrics", {}))}
                for entry in analytics
            ]
        except Exception as e:
            print(f"Failed to load check_analytics for diagnostics: {e}")

    hook_analysis = analyze_hook_performance()
    cta_suggestions = suggest_cta_rotation(analytics)
    hook_suggestions = suggest_new_hooks(hook_analysis)

    # Funnel diagnosis
    perf_data = load_json(HOOK_PERFORMANCE_PATH)
    performances = perf_data.get("performances", [])
    total_views, total_clicks, total_conversions = _get_funnel_totals(
        performances, input_clicks, input_conversions
    )
    funnel_result = diagnose_funnel(total_views, total_clicks, total_conversions)

    # Record learnings
    new_learnings = record_learning(performances)

    return {
        "analytics": analytics,
        "hook_analysis": hook_analysis,
        "cta_suggestions": cta_suggestions,
        "hook_suggestions": hook_suggestions,
        "funnel_result": funnel_result,
        "new_learnings": new_learnings,
    }


def _build_report_lines(report_type: str, report_days: int, data: dict) -> list:
    """Build all report lines from collected data.

    Args:
        report_type: "주간" or "일일"
        report_days: number of days covered by the report
        data: dict returned by _collect_report_data

    Returns:
        list of strings (report lines)
    """
    analytics = data["analytics"]
    hook_analysis = data["hook_analysis"]
    cta_suggestions = data["cta_suggestions"]
    hook_suggestions = data["hook_suggestions"]
    funnel_result = data["funnel_result"]

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Header
    lines = [
        f"# Social Slide Marketing {report_type} 리포트",
        f"생성: {now}",
        f"기간: 최근 {report_days}일",
        "",
        "---",
        "",
        "## 포스트별 성과",
        "",
    ]

    # Post table
    if analytics:
        lines = lines + [
            "| 포스트 | 조회수 | 좋아요 | 댓글 | 공유 | 진단 |",
            "|--------|--------|--------|------|------|------|",
        ]
        for entry in analytics:
            m = entry.get("metrics", {})
            d = entry.get("diagnosis", {})
            lines = lines + [
                f"| {entry.get('title', '')[:25]}... "
                f"| {m.get('views', 0):,} "
                f"| {m.get('likes', 0):,} "
                f"| {m.get('comments', 0):,} "
                f"| {m.get('shares', 0):,} "
                f"| {d.get('diagnosis', 'N/A')} |"
            ]
        lines = lines + [""]
    else:
        lines = lines + ["데이터 없음 (Postiz API 연결 확인 필요)", ""]

    # Diagnostics
    diag_lines = ["## 진단 & 조치", ""]
    for entry in analytics:
        d = entry.get("diagnosis", {})
        if d:
            diag_lines = diag_lines + [
                f"**{entry.get('title', '')[:30]}...**",
                f"- 진단: {d.get('diagnosis', 'N/A')}",
                f"- 조치: {d.get('action', 'N/A')}",
                "",
            ]
    lines = lines + diag_lines

    # Funnel diagnosis section
    lines = lines + _build_funnel_section(funnel_result)

    # Hook performance summary
    lines = lines + [
        "## 훅 성과 요약",
        "",
        f"- 총 포스트: {hook_analysis.get('total_posts', 0)}개",
        f"- 평균 조회수: {hook_analysis.get('avg_views', 0):,}",
        f"- 평균 참여율: {hook_analysis.get('avg_engagement', 0)}%",
        "",
    ]

    if hook_analysis.get("top_hooks"):
        top_hook_lines = ["**Top 3 훅:**"]
        for h in hook_analysis["top_hooks"]:
            top_hook_lines = top_hook_lines + [
                f"- {h.get('hook', '')[:40]}... ({h.get('views', 0):,} views)"
            ]
        lines = lines + top_hook_lines + [""]

    # Hook formula rankings section
    lines = lines + _build_rankings_section()

    # Auto-generated hook variations section
    lines = lines + _build_hook_variations_section(hook_analysis.get("top_hooks", []))

    # CTA suggestions
    if cta_suggestions:
        cta_lines = ["## CTA 로테이션 추천", ""]
        for s in cta_suggestions:
            cta_entry = [
                f"**{s['post']}**",
                f"- 이슈: {s['current_issue']}",
            ]
            for cta in s.get("try_next", []):
                cta_entry = cta_entry + [f"- 추천: {cta['ko']} ({cta['best_for']})"]
            cta_lines = cta_lines + cta_entry + [""]
        lines = lines + cta_lines

    # Hook suggestions
    if hook_suggestions:
        hook_lines = ["## 새 훅 추천", ""]
        for s in hook_suggestions:
            hook_lines = hook_lines + [
                f"- **{s['type']}**: {s['suggestion']}",
                f"  이유: {s['reason']}",
            ]
        lines = lines + hook_lines + [""]

    # Learnings section
    lines = lines + _build_learnings_section()

    # Footer
    lines = lines + [
        "---",
        f"_Generated by social-slide-marketing at {now}_",
    ]

    return lines


def generate_report(config_path: str, days: int = 3, weekly: bool = False,
                    input_clicks: int = 0, input_conversions: int = 0) -> str:
    """Generate a daily/weekly analytics report.

    Orchestrates data collection, report building, and file saving.
    """
    report_days = 7 if weekly else days
    report_type = "주간" if weekly else "일일"

    # Collect all report data
    data = _collect_report_data(config_path, report_days, input_clicks, input_conversions)

    # Build report lines
    lines = _build_report_lines(report_type, report_days, data)
    report = "\n".join(lines)

    # Save report
    reports_dir = CONFIG_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_file = reports_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_file, "w") as f:
        f.write(report)

    print(f"\nReport saved: {report_file}")
    return report


def main():
    parser = argparse.ArgumentParser(description="Generate daily/weekly analytics report")
    parser.add_argument("--config", default=str(CONFIG_PATH), help="Path to config.json")
    parser.add_argument("--days", type=int, default=3, help="Number of days to analyze")
    parser.add_argument("--weekly", action="store_true", help="Generate weekly report (7 days)")
    parser.add_argument("--input-clicks", type=int, default=0, help="Manual link click count for funnel diagnosis")
    parser.add_argument("--input-conversions", type=int, default=0, help="Manual conversion count for funnel diagnosis")

    args = parser.parse_args()

    report = generate_report(
        config_path=args.config,
        days=args.days,
        weekly=args.weekly,
        input_clicks=args.input_clicks,
        input_conversions=args.input_conversions,
    )

    print("\n" + report)


if __name__ == "__main__":
    main()

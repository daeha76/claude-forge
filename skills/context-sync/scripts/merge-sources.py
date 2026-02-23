#!/usr/bin/env python3
"""
merge-sources.py - context-sync 소스 결과를 병합하여 브리핑 문서 생성

Usage:
  python3 merge-sources.py --sources-dir /tmp/context-sync/sources --output /tmp/context-sync/briefing_2026-02-22.md

입력: /tmp/context-sync/sources/*.json (각 소스별 수집 결과)
출력: 브리핑 마크다운 파일
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def load_sources(sources_dir: str) -> list[dict]:
    """소스 디렉토리에서 모든 JSON 파일을 로드한다."""
    results = []
    source_path = Path(sources_dir)

    if not source_path.exists():
        return results

    for json_file in sorted(source_path.glob("*.json")):
        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)
                results.append(data)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: {json_file.name} 로드 실패 - {e}", file=sys.stderr)

    return results


def extract_highlights(sources: list[dict]) -> list[dict]:
    """high priority 또는 action_required 항목을 추출한다."""
    highlights = []

    for source_data in sources:
        source_name = source_data.get("source", "unknown")
        for item in source_data.get("items", []):
            if item.get("priority") == "high" or item.get("action_required"):
                highlights.append({
                    **item,
                    "source_tag": source_name,
                })

    # 시간순 정렬 (최신 먼저)
    highlights.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return highlights[:10]


def extract_actions(sources: list[dict]) -> list[dict]:
    """action_required 항목을 추출한다."""
    actions = []

    for source_data in sources:
        source_name = source_data.get("source", "unknown")
        for item in source_data.get("items", []):
            if item.get("action_required") and item.get("action_description"):
                actions.append({
                    "description": item["action_description"],
                    "source": source_name,
                    "priority": item.get("priority", "medium"),
                    "timestamp": item.get("timestamp", ""),
                })

    actions.sort(key=lambda x: (
        {"high": 0, "medium": 1, "low": 2}.get(x["priority"], 1),
        x["timestamp"],
    ))
    return actions


def build_timeline(sources: list[dict]) -> list[dict]:
    """모든 소스의 items를 시간순으로 합쳐 타임라인을 생성한다."""
    timeline = []

    for source_data in sources:
        source_name = source_data.get("source", "unknown")
        for item in source_data.get("items", []):
            timeline.append({
                "timestamp": item.get("timestamp", ""),
                "source": source_name,
                "title": item.get("title", ""),
            })

    timeline.sort(key=lambda x: x.get("timestamp", ""))
    return timeline[:20]


def format_time(timestamp: str) -> str:
    """타임스탬프에서 HH:MM만 추출한다."""
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime("%H:%M")
    except (ValueError, AttributeError):
        return "??:??"


def generate_briefing(
    sources: list[dict],
    start_time: str,
    end_time: str,
    active_sources: list[str],
) -> str:
    """브리핑 마크다운을 생성한다."""
    today = datetime.now().strftime("%Y-%m-%d")
    highlights = extract_highlights(sources)
    actions = extract_actions(sources)
    timeline = build_timeline(sources)

    lines = []

    # 헤더
    lines.append(f"# Context Sync Briefing - {today}")
    lines.append("")
    lines.append(f"> 수집 기간: {start_time} ~ {end_time}")
    lines.append(f"> 소스: {', '.join(active_sources)}")
    lines.append(f"> 생성: {end_time}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 하이라이트
    lines.append("## 하이라이트")
    lines.append("")
    if highlights:
        lines.append("| # | 소스 | 항목 | 우선순위 |")
        lines.append("|---|------|------|---------|")
        for i, h in enumerate(highlights, 1):
            lines.append(
                f"| {i} | [{h['source_tag']}] | {h.get('title', '')} | {h.get('priority', 'medium')} |"
            )
    else:
        lines.append("하이라이트 항목이 없습니다.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 소스별 상세
    lines.append("## 소스별 상세")
    lines.append("")

    source_names = {"slack": "Slack", "gmail": "Gmail", "calendar": "Calendar", "github": "GitHub", "work": "Work Sessions"}

    for source_data in sources:
        source_key = source_data.get("source", "unknown")
        display_name = source_names.get(source_key, source_key)
        items = source_data.get("items", [])
        lines.append(f"### {display_name} ({len(items)}건)")
        lines.append("")

        if items:
            for item in items:
                time_str = format_time(item.get("timestamp", ""))
                title = item.get("title", "")
                content = item.get("content", "")
                lines.append(f"- **{time_str}** {title}")
                if content:
                    lines.append(f"  {content}")
        else:
            lines.append("해당 기간에 활동 없음")

        lines.append("")

    lines.append("---")
    lines.append("")

    # 액션 아이템
    lines.append("## 액션 아이템")
    lines.append("")
    if actions:
        for action in actions:
            lines.append(
                f"- [ ] {action['description']} -- 소스: {action['source']}, 우선순위: {action['priority']}"
            )
    else:
        lines.append("액션 아이템이 없습니다.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 타임라인
    lines.append("## 타임라인")
    lines.append("")
    if timeline:
        lines.append("| 시간 | 소스 | 이벤트 |")
        lines.append("|------|------|--------|")
        for t in timeline:
            time_str = format_time(t.get("timestamp", ""))
            lines.append(f"| {time_str} | [{t['source']}] | {t.get('title', '')} |")
    else:
        lines.append("타임라인 이벤트가 없습니다.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 통계
    lines.append("## 통계")
    lines.append("")
    lines.append("| 소스 | 총 건수 | 중요 | 액션 필요 |")
    lines.append("|------|--------|------|----------|")

    total_count = 0
    total_high = 0
    total_action = 0

    for source_data in sources:
        stats = source_data.get("stats", {})
        source_key = source_data.get("source", "unknown")
        display_name = source_names.get(source_key, source_key)
        count = stats.get("total_count", 0)
        high = stats.get("high_priority", 0)
        action_req = stats.get("action_required", 0)
        total_count += count
        total_high += high
        total_action += action_req
        lines.append(f"| {display_name} | {count} | {high} | {action_req} |")

    lines.append(f"| **합계** | **{total_count}** | **{total_high}** | **{total_action}** |")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="context-sync 소스 병합 및 브리핑 생성")
    parser.add_argument("--sources-dir", required=True, help="소스 JSON 디렉토리")
    parser.add_argument("--output", required=True, help="브리핑 파일 출력 경로")
    parser.add_argument("--start-time", default="", help="수집 시작 시간 (ISO 8601)")
    parser.add_argument("--end-time", default="", help="수집 종료 시간 (ISO 8601)")
    parser.add_argument("--active-sources", default="all", help="활성 소스 (쉼표 구분)")
    args = parser.parse_args()

    sources = load_sources(args.sources_dir)

    if not sources:
        print("수집 가능한 데이터가 없습니다.", file=sys.stderr)
        sys.exit(0)

    end_time = args.end_time or datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    start_time = args.start_time or "N/A"
    active_sources_list = (
        [s.get("source", "unknown") for s in sources]
        if args.active_sources == "all"
        else args.active_sources.split(",")
    )

    briefing = generate_briefing(sources, start_time, end_time, active_sources_list)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(briefing)

    print(f"브리핑 생성 완료: {output_path}")

    # 축약본 터미널 출력
    highlights = extract_highlights(sources)
    actions = extract_actions(sources)
    print(f"\n하이라이트 {len(highlights)}건 | 액션 아이템 {len(actions)}건")


if __name__ == "__main__":
    main()

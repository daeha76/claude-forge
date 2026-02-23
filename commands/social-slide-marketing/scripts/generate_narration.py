#!/usr/bin/env python3
"""
SlideShow 나레이션 생성 스크립트

6장 슬라이드 각각에 대해 ElevenLabs V3 TTS로 나레이션 오디오를 생성하고,
Remotion에서 사용할 매니페스트 JSON을 출력한다.

Usage:
    python3 generate_narration.py \
        --texts "슬라이드1 나레이션||슬라이드2||...||슬라이드6" \
        --output /tmp/social-slides/audio/ \
        --voice korean_professional \
        --copy-to ~/marketing-caw/remotion-video/public/audio/
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

# elevenlabs_tts.py import path
TTS_MODULE = Path.home() / "marketing-caw/.claude/skills/video_gen"
sys.path.insert(0, str(TTS_MODULE))

try:
    from dotenv import load_dotenv
    load_dotenv(Path.home() / ".env")
except ImportError:
    pass

import os

if not os.getenv("ELEVENLABS_API_KEY"):
    print("ERROR: ELEVENLABS_API_KEY 환경변수가 설정되지 않았습니다.")
    print("~/.env 파일에 ELEVENLABS_API_KEY=your_key 를 추가하세요.")
    sys.exit(1)

from elevenlabs_tts import ElevenLabsTTS


def parse_args():
    parser = argparse.ArgumentParser(
        description="SlideShow 나레이션 생성 (ElevenLabs V3)"
    )
    parser.add_argument(
        "--texts",
        required=True,
        help='슬라이드별 나레이션 텍스트 ("||"로 구분)',
    )
    parser.add_argument(
        "--output",
        required=True,
        help="오디오 파일 출력 디렉토리",
    )
    parser.add_argument(
        "--voice",
        default="korean_professional",
        help="음성 프리셋 (default: korean_professional)",
    )
    parser.add_argument(
        "--copy-to",
        dest="copy_to",
        default=None,
        help="Remotion public/audio/ 경로 (오디오 파일 복사)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    texts = [t.strip() for t in args.texts.split("||")]
    if not texts:
        print("ERROR: 나레이션 텍스트가 비어있습니다.")
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    tts = ElevenLabsTTS()

    slides = []
    total_duration = 0.0

    for i, text in enumerate(texts):
        idx = i + 1
        filename = f"narration_{idx:02d}"
        print(f"[{idx}/{len(texts)}] 생성 중: {text[:40]}...")

        result = tts.generate(
            text=text,
            voice=args.voice,
            output_dir=str(output_dir),
            filename=filename,
        )

        if result.get("status") != "success":
            print(f"  ERROR: {result.get('error', 'unknown')}")
            sys.exit(1)

        duration = result.get("duration", 0.0)
        total_duration += duration

        slides.append({
            "index": i,
            "audio": f"audio/{filename}.mp3",
            "duration_sec": round(duration, 2),
            "text": text,
        })

        print(f"  OK: {duration:.1f}s -> {result['audio_path']}")

    # 매니페스트 생성
    fps = 30
    manifest = {
        "slides": slides,
        "total_duration_sec": round(total_duration, 2),
        "recommended_fps": fps,
        "recommended_duration_frames": round(total_duration * fps),
    }

    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\nManifest: {manifest_path}")
    print(f"Total: {total_duration:.1f}s ({manifest['recommended_duration_frames']} frames)")

    # Remotion public/audio/로 복사
    if args.copy_to:
        dest = Path(args.copy_to)
        dest.mkdir(parents=True, exist_ok=True)
        for slide in slides:
            src = output_dir / f"{Path(slide['audio']).name}"
            dst = dest / Path(slide["audio"]).name
            shutil.copy2(src, dst)
            print(f"Copied: {dst}")

    # stdout에 JSON 출력 (파이프라인 연동용)
    print("\n--- MANIFEST JSON ---")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

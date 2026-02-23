#!/bin/bash
# Data Research 도구 설치 스크립트

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$HOME/.claude/scripts/data-research"

echo "=== Data Research 도구 설치 ==="
echo "설치 경로: $VENV_DIR"
echo ""

# Python 버전 확인
if ! command -v python3 &> /dev/null; then
    echo "오류: python3이 설치되어 있지 않습니다."
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "Python: $PYTHON_VERSION"

# 가상환경 생성
echo ""
echo "가상환경 생성 중..."
mkdir -p "$VENV_DIR"
python3 -m venv "$VENV_DIR/venv"

# 가상환경 활성화 및 패키지 설치
echo "패키지 설치 중..."
source "$VENV_DIR/venv/bin/activate"
pip install --upgrade pip
pip install -r "$SCRIPT_DIR/requirements.txt"

echo ""
echo "=== 설치 완료 ==="
echo ""
echo "사용법:"
echo "  source $VENV_DIR/venv/bin/activate"
echo "  python $SCRIPT_DIR/data_fetcher.py"
echo ""
echo "또는 Claude Code에서:"
echo '  /data-research "한국 GDP 성장률 분석"'

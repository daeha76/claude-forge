---
description: 마크다운 파일을 스타일된 DOCX로 변환
argument-hint: <파일.md 또는 폴더> [--pattern "패턴"] [--output-dir 경로] [--branding "텍스트"]
allowed-tools: Bash(*), Read, Glob
---

# MD to DOCX 변환

마크다운 파일을 브랜딩이 적용된 Word 문서로 변환합니다.

## 사용법

```
/md-to-docx file.md                      # 단일 파일
/md-to-docx folder/                      # 폴더 내 모든 .md
/md-to-docx folder/ --pattern "1차_*"    # 패턴 지정
/md-to-docx file.md --output-dir output/ # 출력 폴더 지정
/md-to-docx file.md --branding "MyBrand" # 커스텀 브랜딩
```

## 기능

- Indigo 브랜드 컬러 적용
- Apple SD Gothic Neo 폰트
- 헤더 배너 (브랜딩 + 문서 유형)
- 스타일된 테이블 (헤더 강조, 줄무늬 행)
- 코드 블록 (Monaco 폰트, 회색 배경)
- 인용 블록 (파란 배경)
- 푸터 (customizable)

## 실행

$ARGUMENTS가 비어있으면 도움말을 표시합니다.

1. 가상환경이 없으면 설치 스크립트 실행
2. 변환 스크립트 실행
3. 결과 출력

```bash
# 설치 확인 및 실행
SCRIPT_DIR="$HOME/.claude/scripts/md-to-docx"

if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "가상환경이 없습니다. 설치를 진행합니다..."
    bash "$SCRIPT_DIR/install.sh"
fi

source "$SCRIPT_DIR/venv/bin/activate"
python "$SCRIPT_DIR/convert.py" $ARGUMENTS
```

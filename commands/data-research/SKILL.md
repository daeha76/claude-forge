---
name: data-research
description: 공공데이터(KOSIS, ECOS)·국제경제데이터(World Bank, OECD, FRED)를 수집·분석하여 차트 포함 종합 리서치 리포트 생성. 마크다운 + Python 차트(PNG) + DOCX 변환 지원.
allowed-tools: Read, Write, Edit, Bash(*)
argument-hint: <리서치 주제> [--sources fred,ecos,worldbank] [--period 2015-2025] [--output-dir 경로]
---

# Data Research — 종합 데이터 리서치 리포트 생성

## Overview

공공데이터(KOSIS, ECOS)와 국제경제데이터(World Bank, OECD, FRED)를 통합 수집·분석하여 차트가 포함된 종합 리서치 리포트를 생성합니다.

**주요 기능**:
- 5개 데이터 소스 통합 조회 (FRED, ECOS, KOSIS, World Bank, OECD)
- matplotlib/seaborn 차트 자동 생성 (PNG)
- 마크다운(.md) 리포트 자동 작성
- `/md-to-docx` 연계 DOCX 변환 지원
- Brand 색상 팔레트 적용

**적합한 작업**:
- 경제 지표 트렌드 분석 (GDP 성장률, 물가, 실업률 등)
- 국가 간 비교 분석 (한국 vs OECD, G7, G20)
- 산업 동향 데이터 리포트
- 사업 근거 자료 (시장 규모, 성장률 데이터)
- 투자 검토용 거시경제 리서치

## Quick Start

```bash
# 기본 사용
/data-research "한국 GDP 성장률 10년 추이 분석"

# 데이터 소스 지정
/data-research "한국 vs OECD 주요국 GDP 비교" --sources worldbank,oecd --period 2015-2024

# 출력 경로 지정
/data-research "한국은행 기준금리와 환율 상관관계" --sources ecos,fred --output-dir ~/research/
```

**사용 예시**:
- `"World Bank 기준 한국 vs G7 GDP per capita 비교 (2010-2023)"`
- `"FRED 기준 미국 기준금리와 실업률 상관관계 분석"`
- `"한국 소비자물가지수(CPI) 추이와 기준금리 관계"`

## Data Sources Overview

| 소스 | 설명 | API 키 필요 | 주요 지표 |
|------|------|------------|-----------|
| **FRED** | 미국 연방준비은행 경제 데이터 | O (FRED_API_KEY) | GDP, 실업률, CPI, 기준금리, 국채수익률 |
| **ECOS** | 한국은행 경제통계시스템 | O (ECOS_API_KEY) | 기준금리(722Y001), 환율(731Y004), GDP(200Y001), CPI(901Y009) |
| **KOSIS** | 통계청 국가통계포털 | O (KOSIS_API_KEY) | 인구(DT_1B040A3), 산업활동(DT_1K52A01), 경제활동인구 |
| **World Bank** | 세계은행 오픈 데이터 | X | GDP(NY.GDP.MKTP.CD), 인구(SP.POP.TOTL), 1인당 GDP, 물가상승률 |
| **OECD** | OECD 통계 데이터 | X | QNA(국민계정), MEI(주요경제지표), SNA_TABLE1(GDP) |

### FRED 주요 시리즈

| Series ID | 설명 | 주기 |
|-----------|------|------|
| GDP | 명목 GDP | 분기 |
| GDPC1 | 실질 GDP | 분기 |
| UNRATE | 실업률 | 월 |
| CPIAUCSL | 소비자물가지수 | 월 |
| FEDFUNDS | 연방기금금리 | 월 |
| DGS10 | 10년 국채수익률 | 일 |

### ECOS 주요 통계표 코드

| 통계표코드 | 설명 | 항목코드 |
|-----------|------|---------|
| 722Y001 | 한국은행 기준금리 | 0101000 |
| 731Y004 | 원/달러 환율 | 0000001 |
| 200Y001 | 국내총생산(GDP) | 10101 |
| 901Y009 | 소비자물가지수 | — |

### World Bank 주요 지표

| 지표코드 | 설명 |
|---------|------|
| NY.GDP.MKTP.CD | GDP (current US$) |
| NY.GDP.PCAP.CD | GDP per capita (current US$) |
| SP.POP.TOTL | Total population |
| FP.CPI.TOTL.ZG | Inflation, consumer prices (annual %) |
| SL.UEM.TOTL.ZS | Unemployment (% of total labor force) |

## Workflow

하이브리드 워크플로우: 자동 진행 + 핵심 의사결정만 사용자 확인

### Phase 1: 주제 분석 및 데이터 소스 추천

사용자의 리서치 주제를 분석하여 적합한 데이터 소스와 지표를 자동 추천합니다.

**자동 처리**:
1. 주제에서 키워드 추출 (국가, 지표, 기간, 비교 대상)
2. `--sources` 옵션이 없으면 주제에 맞는 소스 자동 선택
3. `--period` 옵션이 없으면 최근 10년 기본 설정

**[확인 1] 데이터 소스 선택 확인**:
```
AskUserQuestion을 사용하여 추천된 데이터 소스와 지표 목록을 사용자에게 확인합니다.
- 추천 소스: [FRED, World Bank, ...]
- 수집할 지표: [GDP, CPI, ...]
- 분석 기간: 2015-2024
```

### Phase 2: 리포트 구조 설계

주제 유형에 맞는 리포트 구조를 자동 설계합니다.

**리포트 유형 자동 선택**:
- 시계열 키워드 ("추이", "트렌드", "변화") → 트렌드 분석 리포트
- 비교 키워드 ("비교", "vs", "대비") → 국가 비교 리포트
- 산업 키워드 ("산업", "섹터", "업종") → 산업 분석 리포트
- 사업 키워드 ("시장", "사업", "근거") → 사업 근거 리포트

**[확인 2] 리포트 구조 확인**:
```
AskUserQuestion을 사용하여 리포트 구조(섹션 목록)를 사용자에게 확인합니다.
```

### Phase 3: 데이터 수집 (자동)

Python 스크립트를 사용하여 데이터를 자동 수집합니다.

```bash
# venv 활성화
source ~/.claude/scripts/data-research/venv/bin/activate

# data_fetcher.py의 각 Fetcher 클래스를 사용
python3 -c "
from data_fetcher import WorldBankFetcher
wb = WorldBankFetcher()
df = wb.fetch('NY.GDP.MKTP.CD', 'KR', 2015, 2024)
print(df.to_string())
"
```

**스크립트 실행 시 주의사항**:
- venv가 없으면 먼저 `bash ~/.claude/commands/data-research/scripts/install.sh` 실행
- PYTHONPATH에 scripts 디렉토리 추가: `cd ~/.claude/commands/data-research/scripts && python3 -c "..."`
- API 키 필요 소스는 환경변수 확인

### Phase 4: 분석 및 차트 생성 (자동)

수집된 데이터를 분석하고 chart_generator.py로 차트를 생성합니다.

```python
from chart_generator import create_line_chart, create_bar_chart, create_heatmap

# 시계열 차트
create_line_chart(df, 'date', ['gdp'], 'GDP 추이', './charts/gdp_trend.png')

# 비교 차트
create_bar_chart(df, 'country', 'gdp', '국가별 GDP 비교', './charts/gdp_compare.png')

# 상관관계 히트맵
create_heatmap(corr_df, '경제지표 상관관계', './charts/correlation.png')
```

**차트 설정**:
- Brand 색상 자동 적용
- 한글 폰트 자동 감지 (AppleGothic)
- 300 DPI, PNG 형식
- 출력 경로: `{output_dir}/charts/`

### Phase 5: 리포트 작성 (자동)

report_builder.py를 사용하여 마크다운 리포트를 조립합니다.

```python
from report_builder import ReportBuilder

report = (
    ReportBuilder()
    .add_header("한국 GDP 성장률 분석", sources=["FRED", "World Bank"])
    .add_summary("본 보고서는 ...")
    .add_data_overview("2015-2024", ["FRED", "World Bank"], ["GDP 성장률"])
    .add_trend_analysis("GDP 추이", "./charts/gdp_trend.png", "해석 텍스트...")
    .add_insights(["인사이트 1", "인사이트 2"])
    .add_conclusion("결론 텍스트...")
    .build("./report.md")
)
```

### Phase 6: DOCX 변환 (선택)

**[확인 3] DOCX 변환 여부**:
```
AskUserQuestion: "리포트를 DOCX 파일로도 변환할까요?"
→ Yes: /md-to-docx 실행
→ No: 마크다운 파일만 유지
```

## API Key Setup

### FRED API Key
```bash
# 발급: https://fredaccount.stlouisfed.org
export FRED_API_KEY="your_32_character_key_here"
```

### ECOS API Key (한국은행)
```bash
# 발급: https://ecos.bok.or.kr/api/#/ → 인증키 신청
export ECOS_API_KEY="your_ecos_key_here"
```

### KOSIS API Key (통계청)
```bash
# 발급: https://kosis.kr/openapi/ → 회원가입 → API 키 발급
export KOSIS_API_KEY="your_kosis_key_here"
```

**참고**: World Bank, OECD는 API 키 없이 사용 가능합니다.

## Installation

```bash
# 설치 스크립트 실행 (venv + 패키지 자동 설치)
bash ~/.claude/commands/data-research/scripts/install.sh

# 수동 설치
mkdir -p ~/.claude/scripts/data-research
python3 -m venv ~/.claude/scripts/data-research/venv
source ~/.claude/scripts/data-research/venv/bin/activate
pip install -r ~/.claude/commands/data-research/scripts/requirements.txt
```

**설치 확인**:
```bash
source ~/.claude/scripts/data-research/venv/bin/activate
python3 -c "import pandas, matplotlib, plotly, seaborn, requests; print('All packages OK')"
```

## Data Collection Patterns

### FRED 데이터 수집
```python
from data_fetcher import FREDFetcher

fred = FREDFetcher()  # FRED_API_KEY 환경변수 사용
gdp = fred.fetch("GDP", start_date="2015-01-01", end_date="2024-12-31")
unrate = fred.fetch("UNRATE", start_date="2015-01-01")
```

### ECOS 데이터 수집
```python
from data_fetcher import ECOSFetcher

ecos = ECOSFetcher()  # ECOS_API_KEY 환경변수 사용
# 기준금리 (월별, 2015-2024)
rate = ecos.fetch("722Y001", "M", "201501", "202412", "0101000")
# 원/달러 환율
exchange = ecos.fetch("731Y004", "M", "201501", "202412", "0000001")
```

### World Bank 데이터 수집 (API 키 불필요)
```python
from data_fetcher import WorldBankFetcher

wb = WorldBankFetcher()
# 한국 GDP
korea_gdp = wb.fetch("NY.GDP.MKTP.CD", "KR", 2015, 2024)
# 미국 1인당 GDP
us_gdp_pc = wb.fetch("NY.GDP.PCAP.CD", "US", 2015, 2024)
```

### 다중 데이터 병합
```python
from data_fetcher import merge_dataframes, WorldBankFetcher

wb = WorldBankFetcher()
korea = wb.fetch("NY.GDP.MKTP.CD", "KR", 2015, 2024)
japan = wb.fetch("NY.GDP.MKTP.CD", "JP", 2015, 2024)
merged = merge_dataframes([korea, japan])
```

## Chart Generation Patterns

### 시계열 라인 차트
```python
from chart_generator import create_line_chart
create_line_chart(df, "date", ["gdp", "cpi"], "GDP vs CPI", "./charts/trend.png",
                  labels={"gdp": "GDP 성장률", "cpi": "소비자물가"})
```

### 비교 막대 차트
```python
from chart_generator import create_bar_chart
create_bar_chart(df, "country", "gdp_per_capita", "국가별 1인당 GDP", "./charts/compare.png")
```

### 상관관계 히트맵
```python
from chart_generator import create_heatmap
corr = df[["gdp", "cpi", "unemployment", "interest_rate"]].corr()
create_heatmap(corr, "경제지표 상관관계", "./charts/heatmap.png")
```

### 다중 시리즈 차트
```python
from chart_generator import create_multi_line_chart
data = {
    "한국": (years, korea_gdp),
    "일본": (years, japan_gdp),
    "미국": (years, us_gdp),
}
create_multi_line_chart(data, "GDP 비교", "./charts/multi.png", "연도", "GDP (USD)")
```

## Report Structure Template

표준 리포트 구조:

```
# 제목
  작성일, 데이터 출처

## Executive Summary
  핵심 발견 요약 (3-5문장)

## 분석 개요
  분석 기간, 데이터 출처, 주요 지표

## 트렌드 분석 (또는 비교 분석)
  ### 지표 1: [차트] + 해석
  ### 지표 2: [차트] + 해석

## 상관관계 분석 (선택)
  [히트맵] + 해석

## 주요 인사이트
  번호 매겨진 핵심 발견 목록

## 결론
  종합 요약 및 시사점

## 분석 방법론
  사용된 데이터 및 분석 기법
```

## Integration

### DOCX 변환 (/md-to-docx)
```bash
/md-to-docx ./report.md
```
Brand이 적용된 DOCX 파일로 자동 변환됩니다.

### Plotly 인터랙티브 차트
고급 인터랙티브 차트가 필요할 경우 `/plotly` 스킬을 함께 활용할 수 있습니다.

## Troubleshooting

### venv를 찾을 수 없음
```bash
# install.sh 재실행
bash ~/.claude/commands/data-research/scripts/install.sh
```

### API 키 오류
```bash
# 환경변수 확인
echo $FRED_API_KEY
echo $ECOS_API_KEY
echo $KOSIS_API_KEY
```

### 한글 폰트 깨짐
macOS에서 AppleGothic 폰트를 사용합니다. 폰트가 없으면 sans-serif로 fallback됩니다.
```python
# matplotlib 폰트 캐시 초기화
import matplotlib
matplotlib.font_manager._load_fontmanager(try_read_cache=False)
```

### World Bank / OECD 데이터 로딩 느림
네트워크 상태에 따라 수십 초 소요될 수 있습니다. timeout 에러 시 재시도하세요.

### import 에러
```bash
# scripts 디렉토리에서 실행
cd ~/.claude/commands/data-research/scripts
source ~/.claude/scripts/data-research/venv/bin/activate
python3 -c "from data_fetcher import WorldBankFetcher; print('OK')"
```

## Reference

상세 참고 문서:
- `references/data_sources.md` — 데이터 소스별 API 상세 가이드
- `references/chart_patterns.md` — 차트 유형별 코드 템플릿
- `references/report_templates.md` — 리포트 유형별 마크다운 템플릿
- `references/analysis_frameworks.md` — 분석 기법 (이동평균, 상관분석, 성장률 등)

## Skill Invocation Instructions

이 스킬이 호출되면 다음 순서로 실행합니다:

1. **환경 확인**: venv 존재 여부 확인 (`~/.claude/scripts/data-research/venv/`). 없으면 사용자에게 install.sh 실행 제안.

2. **주제 파싱**: 사용자 인풋에서 주제, 소스, 기간, 출력 경로를 파싱합니다.
   - `--sources` 옵션: 쉼표로 구분된 소스 목록 (fred, ecos, kosis, worldbank, oecd)
   - `--period` 옵션: YYYY-YYYY 형식
   - `--output-dir` 옵션: 출력 디렉토리 (기본값: `~/Downloads/data-research/{주제_slug}/`)

3. **Phase 1-2 실행**: 데이터 소스 추천 → AskUserQuestion으로 확인 → 리포트 구조 설계 → AskUserQuestion으로 확인

4. **Phase 3-5 실행**:
   - `cd ~/.claude/commands/data-research/scripts && source ~/.claude/scripts/data-research/venv/bin/activate`
   - Python 인라인 또는 스크립트로 data_fetcher, chart_generator, report_builder 사용
   - 차트는 `{output_dir}/charts/` 에 저장
   - 리포트는 `{output_dir}/report.md` 로 저장

5. **Phase 6**: AskUserQuestion으로 DOCX 변환 여부 확인 → `/md-to-docx` 실행

6. **완료 보고**: 생성된 파일 목록과 경로를 사용자에게 안내

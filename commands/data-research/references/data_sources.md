# Data Sources API Guide

데이터 리서치 스킬에서 사용하는 주요 데이터 소스 API 가이드.

---

## 1. FRED (Federal Reserve Economic Data)

### 개요

미국 연방준비은행(세인트루이스) 제공 경제 데이터베이스.
미국 및 글로벌 거시경제 지표 81만+ 시계열 데이터 보유.

### API Endpoint

```
Base URL: https://api.stlouisfed.org/fred
```

| Endpoint | 설명 |
|----------|------|
| `/series/observations` | 시계열 데이터 조회 |
| `/series` | 시리즈 메타데이터 |
| `/series/search` | 시리즈 검색 |
| `/releases` | 데이터 릴리스 목록 |

### 인증

1. https://fredaccount.stlouisfed.org 에서 계정 생성
2. API Key 발급 (My Account → API Keys)
3. 환경 변수 설정: `FRED_API_KEY`

### 주요 시리즈 코드

| 코드 | 지표 | 주기 | 단위 |
|------|------|------|------|
| `GDP` | 명목 GDP | 분기 | Billions of Dollars |
| `GDPC1` | 실질 GDP | 분기 | Billions of Chained 2017 Dollars |
| `UNRATE` | 실업률 | 월간 | Percent |
| `CPIAUCSL` | 소비자물가지수 (CPI) | 월간 | Index 1982-84=100 |
| `FEDFUNDS` | 연방기금금리 | 월간 | Percent |
| `DGS10` | 10년 국채 수익률 | 일간 | Percent |
| `HOUST` | 주택착공건수 | 월간 | Thousands of Units |
| `PAYEMS` | 비농업 고용 | 월간 | Thousands of Persons |
| `M2SL` | M2 통화량 | 월간 | Billions of Dollars |
| `DEXKOUS` | 원/달러 환율 | 일간 | Korean Won per USD |

### Python 코드 예시

```python
import os
import requests
import pandas as pd

FRED_API_KEY = os.environ.get('FRED_API_KEY')
BASE_URL = 'https://api.stlouisfed.org/fred'

def fetch_fred_series(series_id: str, start_date: str = '2015-01-01', end_date: str = '2025-12-31') -> pd.DataFrame:
    """FRED 시리즈 데이터를 DataFrame으로 반환"""
    url = f'{BASE_URL}/series/observations'
    params = {
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'observation_start': start_date,
        'observation_end': end_date,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data['observations'])
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df = df[['date', 'value']].dropna()
    df = df.set_index('date')
    return df

# 사용 예시: 미국 GDP 조회
gdp = fetch_fred_series('GDP', '2015-01-01', '2025-12-31')
print(gdp.tail())
```

### MCP 도구 사용

```
mcp__fred__fred_search: 시리즈 검색
mcp__fred__fred_get_series: 시리즈 데이터 조회
mcp__fred__fred_browse: 카테고리 탐색
```

---

## 2. ECOS (한국은행 경제통계시스템)

### 개요

한국은행 제공 국내 경제통계 데이터베이스.
금리, 환율, 통화, GDP 등 국내 핵심 거시경제 지표 제공.

### API Endpoint

```
https://ecos.bok.or.kr/api/{서비스명}/{API_KEY}/{요청유형}/{언어}/{시작}/{끝}/{통계표코드}/{주기}/{검색시작일}/{검색종료일}/{통계항목코드1}/{통계항목코드2}
```

| URL 파라미터 | 설명 | 예시 |
|-------------|------|------|
| 서비스명 | StatisticSearch | StatisticSearch |
| API_KEY | 발급받은 API 키 | - |
| 요청유형 | json / xml | json |
| 언어 | kr / en | kr |
| 시작 / 끝 | 페이징 (1-based) | 1 / 1000 |
| 통계표코드 | 통계표 식별 코드 | 722Y001 |
| 주기 | D(일)/M(월)/Q(분기)/A(연) | M |
| 검색시작일 | YYYYMMDD 또는 YYYY | 20200101 |
| 검색종료일 | YYYYMMDD 또는 YYYY | 20251231 |
| 통계항목코드 | 세부 항목 코드 | 0101000 |

### 인증

1. https://ecos.bok.or.kr 에서 회원가입
2. 인증키 신청 (로그인 → 개발자 센터 → 인증키 신청)
3. 환경 변수 설정: `ECOS_API_KEY`

### 주요 통계표 코드

| 통계표코드 | 항목코드 | 지표 | 주기 |
|-----------|----------|------|------|
| `722Y001` | `0101000` | 한국은행 기준금리 | 일 |
| `731Y004` | `0000001` | 원/달러 환율 (매매기준율) | 일 |
| `731Y004` | `0000002` | 엔/달러 환율 | 일 |
| `200Y001` | `10101` | 국내총생산(GDP, 명목) | 분기 |
| `200Y001` | `10111` | 국내총생산(GDP, 실질) | 분기 |
| `901Y009` | `0` | 소비자물가지수 (총지수) | 월 |
| `901Y009` | `AA` | 소비자물가지수 (식료품) | 월 |
| `028Y015` | `BBHS00` | 전국 주택매매가격지수 | 월 |
| `104Y016` | `010000` | 수출금액 (총계) | 월 |
| `104Y016` | `020000` | 수입금액 (총계) | 월 |

### Python 코드 예시

```python
import os
import requests
import pandas as pd

ECOS_API_KEY = os.environ.get('ECOS_API_KEY')

def fetch_ecos(stat_code: str, item_code1: str, period: str = 'M',
               start_date: str = '20200101', end_date: str = '20251231',
               item_code2: str = ' ') -> pd.DataFrame:
    """ECOS 통계 데이터를 DataFrame으로 반환"""
    url = (
        f'https://ecos.bok.or.kr/api/StatisticSearch/'
        f'{ECOS_API_KEY}/json/kr/1/1000/'
        f'{stat_code}/{period}/{start_date}/{end_date}/'
        f'{item_code1}/{item_code2}'
    )

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    if 'StatisticSearch' not in data:
        raise ValueError(f"API 오류: {data.get('RESULT', {}).get('MESSAGE', '알 수 없는 오류')}")

    rows = data['StatisticSearch']['row']
    df = pd.DataFrame(rows)
    df['TIME'] = pd.to_datetime(df['TIME'], format='%Y%m', errors='coerce')
    df['DATA_VALUE'] = pd.to_numeric(df['DATA_VALUE'], errors='coerce')
    df = df[['TIME', 'DATA_VALUE', 'STAT_NAME', 'ITEM_NAME1']].dropna(subset=['TIME'])
    df = df.rename(columns={'TIME': 'date', 'DATA_VALUE': 'value'})
    df = df.set_index('date')
    return df

# 사용 예시: 한국은행 기준금리 조회
base_rate = fetch_ecos('722Y001', '0101000', 'M', '20200101', '20251231')
print(base_rate.tail())
```

---

## 3. KOSIS (국가통계포털)

### 개요

통계청 운영 국가승인통계 통합 제공 포털.
인구, 고용, 산업, 가계 등 국내 통계청 관할 통계 데이터 제공.

### API Endpoint

```
https://kosis.kr/openapi/Param/statisticsParameterData.do
```

| 파라미터 | 설명 | 필수 |
|---------|------|------|
| `method` | getList | Y |
| `apiKey` | 발급받은 API 키 | Y |
| `itmId` | 항목 ID | Y |
| `objL1` | 분류1 코드 | Y |
| `objL2` ~ `objL8` | 분류2~8 코드 | N |
| `format` | json / xml | Y |
| `jsonVD` | 수록정보 구분 (Y/N) | N |
| `prdSe` | 수록주기 (M/Q/Y) | Y |
| `startPrdDe` | 시작 시점 | Y |
| `endPrdDe` | 종료 시점 | Y |
| `orgId` | 기관 ID | Y |
| `tblId` | 통계표 ID | Y |

### 인증

1. https://kosis.kr 에서 회원가입
2. 오픈 API → API 인증키 발급
3. 환경 변수 설정: `KOSIS_API_KEY`

### 주요 통계표 코드

| 기관(orgId) | 통계표(tblId) | 지표 | 주기 |
|------------|--------------|------|------|
| `101` | `DT_1B040A3` | 인구총조사 (성/연령별) | 연 |
| `101` | `DT_1K52A01` | 산업활동동향 (광공업생산) | 월 |
| `101` | `DT_2KAA408` | 경제활동인구 | 월 |
| `101` | `DT_1J22112` | 고용동향 (취업자 수) | 월 |
| `101` | `DT_1B8000G` | 출생/사망 통계 | 연 |
| `101` | `DT_1YL21121E` | 가계동향조사 (소득) | 분기 |
| `301` | `DT_512Y001` | 국제수지 (BOP) | 월 |

### Python 코드 예시

```python
import os
import requests
import pandas as pd

KOSIS_API_KEY = os.environ.get('KOSIS_API_KEY')

def fetch_kosis(org_id: str, tbl_id: str, itm_id: str, obj_l1: str,
                prd_se: str = 'M', start: str = '202001', end: str = '202512',
                obj_l2: str = '') -> pd.DataFrame:
    """KOSIS 통계 데이터를 DataFrame으로 반환"""
    url = 'https://kosis.kr/openapi/Param/statisticsParameterData.do'
    params = {
        'method': 'getList',
        'apiKey': KOSIS_API_KEY,
        'itmId': itm_id,
        'objL1': obj_l1,
        'objL2': obj_l2,
        'format': 'json',
        'jsonVD': 'Y',
        'prdSe': prd_se,
        'startPrdDe': start,
        'endPrdDe': end,
        'orgId': org_id,
        'tblId': tbl_id,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    if isinstance(data, dict) and 'err' in data:
        raise ValueError(f"KOSIS API 오류: {data['err']}")

    df = pd.DataFrame(data)
    df['PRD_DE'] = df['PRD_DE'].astype(str)
    df['DT'] = pd.to_numeric(df['DT'], errors='coerce')
    df = df.rename(columns={'PRD_DE': 'period', 'DT': 'value', 'C1_NM': 'category'})
    return df[['period', 'value', 'category']].dropna(subset=['value'])

# 사용 예시: 산업활동동향 (광공업 생산지수)
industry = fetch_kosis('101', 'DT_1K52A01', 'T1', 'ALL', 'M', '202001', '202512')
print(industry.head())
```

---

## 4. World Bank Open Data

### 개요

세계은행 제공 글로벌 개발 지표 데이터베이스.
217개국, 1,600+ 지표, 50년+ 시계열 데이터 보유.
국가 간 비교 분석에 최적.

### 라이브러리

```bash
pip install wbdata
```

### 주요 지표 코드

| 코드 | 지표 | 단위 |
|------|------|------|
| `NY.GDP.MKTP.CD` | GDP (current USD) | US Dollars |
| `NY.GDP.MKTP.KD.ZG` | GDP 성장률 | % |
| `NY.GDP.PCAP.CD` | 1인당 GDP (current USD) | US Dollars |
| `SP.POP.TOTL` | 총인구 | Persons |
| `SP.POP.GROW` | 인구증가율 | % |
| `FP.CPI.TOTL.ZG` | 인플레이션 (CPI) | % |
| `SL.UEM.TOTL.ZS` | 실업률 (ILO 기준) | % |
| `NE.EXP.GNFS.ZS` | 수출 비중 (GDP 대비) | % |
| `BX.KLT.DINV.WD.GD.ZS` | FDI 유입 (GDP 대비) | % |
| `SE.XPD.TOTL.GD.ZS` | 교육지출 (GDP 대비) | % |

### 주요 국가 코드

| 코드 | 국가 | 코드 | 국가 |
|------|------|------|------|
| `KOR` | 한국 | `USA` | 미국 |
| `JPN` | 일본 | `CHN` | 중국 |
| `DEU` | 독일 | `GBR` | 영국 |
| `FRA` | 프랑스 | `IND` | 인도 |
| `BRA` | 브라질 | `AUS` | 호주 |

### Python 코드 예시

```python
import wbdata
import pandas as pd
from datetime import datetime

def fetch_worldbank(indicator: str, countries: list[str],
                    start_year: int = 2015, end_year: int = 2024) -> pd.DataFrame:
    """World Bank 지표를 국가별로 조회하여 DataFrame으로 반환"""
    data = wbdata.get_dataframe(
        {indicator: 'value'},
        country=countries,
        date=(datetime(start_year, 1, 1), datetime(end_year, 12, 31)),
    )

    df = data.reset_index()
    df = df.rename(columns={'date': 'year', 'country': 'country_name'})
    df['year'] = df['year'].astype(str).str[:4].astype(int)
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df = df.dropna(subset=['value'])
    return df.sort_values(['country_name', 'year'])

# 사용 예시: 한국/미국/일본 GDP 성장률 비교
countries = ['KOR', 'USA', 'JPN']
gdp_growth = fetch_worldbank('NY.GDP.MKTP.KD.ZG', countries, 2015, 2024)
print(gdp_growth.tail(10))

# 복수 지표 동시 조회
def fetch_multi_indicators(indicators: dict[str, str], countries: list[str],
                           start_year: int = 2015, end_year: int = 2024) -> pd.DataFrame:
    """복수 지표를 동시에 조회"""
    data = wbdata.get_dataframe(
        indicators,
        country=countries,
        date=(datetime(start_year, 1, 1), datetime(end_year, 12, 31)),
    )
    return data.reset_index()

# 사용 예시: GDP + 인구 + 인플레이션 동시 조회
indicators = {
    'NY.GDP.MKTP.CD': 'GDP_USD',
    'SP.POP.TOTL': 'Population',
    'FP.CPI.TOTL.ZG': 'Inflation',
}
multi = fetch_multi_indicators(indicators, ['KOR', 'USA'], 2018, 2024)
print(multi.head())
```

---

## 5. OECD Data

### 개요

OECD(경제협력개발기구) 제공 회원국 통계 데이터.
38개 회원국의 경제, 사회, 환경 지표 제공.
국제 비교 분석에 적합.

### 라이브러리

```bash
pip install pandasdmx
```

### 주요 데이터셋

| 코드 | 데이터셋 | 내용 |
|------|---------|------|
| `QNA` | Quarterly National Accounts | 분기별 국민소득계정 (GDP 등) |
| `MEI` | Main Economic Indicators | 주요 경제지표 (CPI, 생산, 고용 등) |
| `SNA_TABLE1` | GDP (expenditure approach) | 지출 기준 GDP |
| `STLABOUR` | Short-term Labour Market | 단기 고용 통계 |
| `PRICES_CPI` | Consumer Price Index | 소비자물가지수 |
| `FIN_IND_FBS` | Financial Indicators | 금융지표 (금리, 환율 등) |
| `EO` | Economic Outlook | 경제 전망 |

### 주요 OECD 국가 코드

`KOR`, `USA`, `JPN`, `DEU`, `GBR`, `FRA`, `CAN`, `AUS`, `OECD` (OECD 평균)

### Python 코드 예시

```python
import pandasdmx as sdmx
import pandas as pd

oecd = sdmx.Request('OECD')

def fetch_oecd(dataset: str, params: dict) -> pd.DataFrame:
    """OECD 데이터셋에서 데이터를 조회하여 DataFrame으로 반환"""
    try:
        data = oecd.data(dataset, key=params)
        df = data.to_pandas()

        if isinstance(df, pd.Series):
            df = df.reset_index()
            df.columns = [*df.columns[:-1], 'value']
        return df
    except Exception as e:
        raise ValueError(f"OECD API 오류: {e}")

# 사용 예시: 한국/미국/일본 분기별 GDP 성장률
params = {
    'LOCATION': 'KOR+USA+JPN',
    'SUBJECT': 'B1_GE',
    'MEASURE': 'GYSA',
    'FREQUENCY': 'Q',
}
gdp = fetch_oecd('QNA', params)
print(gdp.tail(10))

# 사용 예시: CPI (소비자물가지수) 비교
cpi_params = {
    'LOCATION': 'KOR+USA+JPN+DEU+OECD',
    'SUBJECT': 'CPALTT01',
    'MEASURE': 'GY',
    'FREQUENCY': 'M',
}
cpi = fetch_oecd('PRICES_CPI', cpi_params)
print(cpi.tail(10))

# pandasdmx 대안: 직접 REST API 호출
def fetch_oecd_rest(dataset: str, filter_str: str) -> pd.DataFrame:
    """OECD REST API로 직접 조회 (pandasdmx 불안정 시 대안)"""
    import requests

    url = f'https://stats.oecd.org/SDMX-JSON/data/{dataset}/{filter_str}/all'
    params = {'startTime': '2015-Q1', 'endTime': '2025-Q4'}

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    # SDMX-JSON 파싱
    series_list = data['dataSets'][0]['series']
    dims = data['structure']['dimensions']

    rows = []
    for key, series in series_list.items():
        dim_indices = key.split(':')
        obs = series['observations']
        for time_idx, values in obs.items():
            rows.append({
                'location': dims['series'][0]['values'][int(dim_indices[0])]['id'],
                'time': dims['observation'][0]['values'][int(time_idx)]['id'],
                'value': values[0],
            })

    return pd.DataFrame(rows)

# 사용 예시: REST API로 GDP 조회
gdp_rest = fetch_oecd_rest('QNA', 'KOR+USA+JPN.B1_GE.GYSA.Q')
print(gdp_rest.head())
```

---

## API 키 환경변수 요약

```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
export FRED_API_KEY="your_fred_api_key"
export ECOS_API_KEY="your_ecos_api_key"
export KOSIS_API_KEY="your_kosis_api_key"
# World Bank, OECD는 API 키 불필요
```

## 데이터 소스 선택 가이드

| 분석 목적 | 추천 소스 | 이유 |
|----------|----------|------|
| 미국 경제 분석 | FRED | 최대 커버리지, 빠른 업데이트 |
| 한국 거시경제 | ECOS | 한은 공식 데이터, 정확성 |
| 한국 인구/산업 | KOSIS | 통계청 관할 국가통계 |
| 국가 간 비교 | World Bank | 표준화된 국제 지표 |
| OECD 비교 | OECD | 선진국 그룹 상세 지표 |
| 종합 분석 | 복수 조합 | ECOS + World Bank 등 |

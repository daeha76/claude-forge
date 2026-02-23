# Analysis Frameworks

데이터 리서치에서 사용하는 분석 기법 레퍼런스. 각 기법별 개념 설명과 Python 코드 예시 포함.

---

## 1. 기본 분석

### 이동평균 (Moving Average)

단기 변동을 완화하여 장기 추세를 파악하는 기법.

```python
import pandas as pd

# 단순 이동평균 (SMA)
df['MA_3'] = df['value'].rolling(window=3).mean()    # 3개월 이동평균
df['MA_12'] = df['value'].rolling(window=12).mean()   # 12개월 이동평균

# 지수 이동평균 (EMA) - 최근 데이터에 더 큰 가중치
df['EMA_12'] = df['value'].ewm(span=12, adjust=False).mean()
```

**사용 시점**: 월간 데이터의 노이즈 제거, 추세 방향 확인
**윈도우 선택**: 월간 → 3/6/12개월, 분기 → 4분기, 일간 → 20/60/120일

### 성장률 계산

```python
import pandas as pd
import numpy as np

# YoY (전년 동기 대비) - 계절성 제거에 유용
df['yoy'] = df['value'].pct_change(periods=12) * 100  # 월간 데이터 기준

# QoQ (전분기 대비)
df['qoq'] = df['value'].pct_change(periods=1) * 100   # 분기 데이터 기준

# MoM (전월 대비)
df['mom'] = df['value'].pct_change(periods=1) * 100    # 월간 데이터 기준

# CAGR (연평균 복합 성장률)
def calc_cagr(start_value: float, end_value: float, years: float) -> float:
    """CAGR 계산 (%)"""
    return ((end_value / start_value) ** (1 / years) - 1) * 100

# 사용 예시
start = df['value'].iloc[0]
end = df['value'].iloc[-1]
years = len(df) / 12  # 월간 데이터 기준
cagr = calc_cagr(start, end, years)
print(f'CAGR: {cagr:.1f}%')
```

**사용 시점**:
- YoY: 계절성 있는 지표 비교 (GDP, 소매판매, 관광객 등)
- QoQ/MoM: 최근 변화 방향 파악
- CAGR: 장기 성장률 요약 (리포트 핵심 수치)

### 기간별 통계

```python
import pandas as pd

def period_stats(df: pd.DataFrame, value_col: str = 'value') -> pd.DataFrame:
    """기간별 기술통계 계산"""
    stats = {
        '평균': df[value_col].mean(),
        '중앙값': df[value_col].median(),
        '표준편차': df[value_col].std(),
        '최솟값': df[value_col].min(),
        '최댓값': df[value_col].max(),
        '범위': df[value_col].max() - df[value_col].min(),
    }
    return pd.Series(stats)

# 연도별 통계
yearly_stats = df.groupby(df.index.year).apply(period_stats)
print(yearly_stats)

# 특정 기간 비교
pre_covid = df[df.index < '2020-01-01']['value'].describe()
post_covid = df[df.index >= '2020-01-01']['value'].describe()
```

---

## 2. 비교 분석

### 정규화 (Base Year Indexing)

서로 다른 단위/스케일의 지표를 동일 기준으로 변환하여 비교.

```python
import pandas as pd

def normalize_to_base(df: pd.DataFrame, base_date: str,
                      value_col: str = 'value') -> pd.DataFrame:
    """기준 시점 = 100으로 정규화"""
    base_value = df.loc[base_date, value_col]
    result = df.copy()
    result['indexed'] = (result[value_col] / base_value) * 100
    return result

# 사용 예시: 2020년 1월 = 100 기준
df_korea = normalize_to_base(df_korea, '2020-01-01')
df_usa = normalize_to_base(df_usa, '2020-01-01')

# 국가별 정규화 비교 (다수 국가)
def normalize_multi(dataframes: dict[str, pd.DataFrame], base_date: str,
                    value_col: str = 'value') -> dict[str, pd.DataFrame]:
    """복수 DataFrame을 동일 기준으로 정규화"""
    return {
        name: normalize_to_base(df, base_date, value_col)
        for name, df in dataframes.items()
    }
```

**사용 시점**: GDP(달러) vs 인구(명) 등 단위가 다른 지표 추이 비교
**기준 시점 선택**: 비교 시작점 (예: 2020-01=100, 코로나 이전=100)

### 기간별 비교

특정 이벤트(정책, 위기) 전후 비교.

```python
import pandas as pd

def before_after_comparison(df: pd.DataFrame, event_date: str,
                            value_col: str = 'value') -> dict:
    """이벤트 전후 비교 통계"""
    before = df[df.index < event_date][value_col]
    after = df[df.index >= event_date][value_col]

    return {
        'before_mean': before.mean(),
        'after_mean': after.mean(),
        'change': after.mean() - before.mean(),
        'change_pct': ((after.mean() / before.mean()) - 1) * 100,
        'before_std': before.std(),
        'after_std': after.std(),
    }

# 사용 예시: 코로나 전후 비교
result = before_after_comparison(df, '2020-03-01')
print(f"평균 변화: {result['change_pct']:.1f}%")
```

### 순위 분석

```python
import pandas as pd

def rank_countries(data: dict[str, float], ascending: bool = False) -> pd.DataFrame:
    """국가별 순위 산출"""
    df = pd.DataFrame([
        {'country': k, 'value': v}
        for k, v in data.items()
    ])
    df['rank'] = df['value'].rank(ascending=ascending, method='min').astype(int)
    return df.sort_values('rank')

# 사용 예시
gdp_per_capita = {'한국': 35000, '미국': 76000, '일본': 34000, '독일': 51000}
ranking = rank_countries(gdp_per_capita, ascending=False)
print(ranking)
```

---

## 3. 상관관계 분석

### Pearson 상관분석

두 변수 간 선형 관계의 강도와 방향 측정.

```python
import pandas as pd

# 단일 상관계수
corr = df['GDP'].corr(df['Employment'])
print(f'상관계수: {corr:.3f}')

# 상관관계 매트릭스
indicators = df[['GDP', 'CPI', 'Interest_Rate', 'Unemployment', 'Exchange_Rate']]
corr_matrix = indicators.corr()
print(corr_matrix)
```

**해석 기준**:

| 상관계수 (절댓값) | 해석 |
|-----------------|------|
| 0.8 ~ 1.0 | 매우 강한 상관 |
| 0.6 ~ 0.8 | 강한 상관 |
| 0.4 ~ 0.6 | 중간 상관 |
| 0.2 ~ 0.4 | 약한 상관 |
| 0.0 ~ 0.2 | 거의 무상관 |

**주의**: 상관관계는 인과관계가 아님. 해석 시 경제적 논리가 뒷받침되어야 함.

### 시차 상관 (Lag Correlation)

한 변수가 다른 변수에 시차를 두고 영향을 미치는 관계 분석.

```python
import pandas as pd

def lag_correlation(series_a: pd.Series, series_b: pd.Series,
                    max_lag: int = 12) -> pd.DataFrame:
    """시차별 상관계수 계산 (series_b를 lag만큼 이동)"""
    results = []
    for lag in range(-max_lag, max_lag + 1):
        if lag >= 0:
            corr = series_a.corr(series_b.shift(lag))
        else:
            corr = series_a.shift(-lag).corr(series_b)
        results.append({'lag': lag, 'correlation': corr})

    df = pd.DataFrame(results)
    return df

# 사용 예시: 금리 변경이 GDP에 미치는 시차 효과
lag_result = lag_correlation(df['GDP_growth'], df['Interest_Rate'], max_lag=8)
best_lag = lag_result.loc[lag_result['correlation'].abs().idxmax()]
print(f"최대 상관: lag={best_lag['lag']}에서 r={best_lag['correlation']:.3f}")
```

**해석**: lag=3에서 최대 상관이면 → 금리 변경 3개월 후 GDP에 가장 큰 영향

### 상관관계 히트맵 생성

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def correlation_analysis(df: pd.DataFrame, columns: list[str],
                         title: str, save_path: str) -> pd.DataFrame:
    """상관관계 분석 + 히트맵 생성"""
    plt.rcParams['font.family'] = 'AppleGothic'
    plt.rcParams['axes.unicode_minus'] = False

    corr = df[columns].corr()

    fig, ax = plt.subplots(figsize=(10, 8), dpi=150)
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                vmin=-1, vmax=1, square=True, linewidths=0.5, ax=ax)
    ax.set_title(title, fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight', facecolor='white')
    plt.close()

    return corr
```

---

## 4. 예측 분석

### 선형 추세 (Linear Trend)

단순 선형 회귀로 추세선 및 미래 예측.

```python
import numpy as np
import pandas as pd

def linear_trend(df: pd.DataFrame, value_col: str = 'value',
                 forecast_periods: int = 12) -> tuple[pd.DataFrame, dict]:
    """선형 추세 분석 및 예측"""
    y = df[value_col].values
    x = np.arange(len(y))

    # 선형 회귀
    slope, intercept = np.polyfit(x, y, 1)
    trend_line = slope * x + intercept

    # R-squared
    ss_res = np.sum((y - trend_line) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)

    # 예측
    future_x = np.arange(len(y), len(y) + forecast_periods)
    forecast = slope * future_x + intercept

    result = df.copy()
    result['trend'] = trend_line

    stats = {
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_squared,
        'monthly_change': slope,
        'annual_change': slope * 12,
        'forecast': forecast,
    }

    return result, stats

# 사용 예시
result, stats = linear_trend(df, 'value', forecast_periods=12)
print(f"월간 변화: {stats['monthly_change']:.2f}")
print(f"연간 변화: {stats['annual_change']:.2f}")
print(f"R²: {stats['r_squared']:.3f}")
```

**사용 시점**: 안정적 성장세를 보이는 지표의 단기 예측
**한계**: 비선형 패턴, 구조적 변화, 계절성 반영 불가

### CAGR 기반 전망

과거 성장률을 기반으로 미래 규모 추정.

```python
import numpy as np

def cagr_projection(current_value: float, cagr_pct: float,
                    years: int) -> list[dict]:
    """CAGR 기반 미래 전망"""
    rate = cagr_pct / 100
    projections = []
    for year in range(1, years + 1):
        projected = current_value * ((1 + rate) ** year)
        projections.append({
            'year_ahead': year,
            'projected_value': projected,
        })
    return projections

# 사용 예시: 현재 100조 원, CAGR 5.5%, 5년 전망
projections = cagr_projection(100, 5.5, 5)
for p in projections:
    print(f"+{p['year_ahead']}년: {p['projected_value']:.1f}조 원")
```

**사용 시점**: 시장 규모 전망, 사업 근거 리포트에서 활용
**한계**: 과거 성장률이 지속된다는 가정. 시나리오 분석과 함께 사용 권장

### 계절성 분해 (개념)

시계열을 추세(Trend), 계절성(Seasonal), 잔차(Residual)로 분리.

```python
from statsmodels.tsa.seasonal import seasonal_decompose
import pandas as pd

def decompose_series(df: pd.DataFrame, value_col: str = 'value',
                     period: int = 12, model: str = 'additive') -> object:
    """계절성 분해"""
    result = seasonal_decompose(df[value_col], model=model, period=period)

    # 각 구성 요소 접근
    trend = result.trend        # 장기 추세
    seasonal = result.seasonal  # 계절 패턴
    residual = result.resid     # 잔차 (불규칙 변동)

    return result

# 사용 예시
# decomposition = decompose_series(df, 'value', period=12)
# decomposition.plot()
```

**구성 요소**:
- **Trend**: 장기적 상승/하락 방향
- **Seasonal**: 매년 반복되는 패턴 (예: 12월 소비 증가)
- **Residual**: 추세와 계절성으로 설명되지 않는 변동

**model 선택**:
- `additive`: 계절 변동폭이 일정할 때
- `multiplicative`: 계절 변동폭이 추세에 비례하여 커질 때

---

## 5. 유틸리티 함수

### 데이터 전처리

```python
import pandas as pd

def clean_economic_data(df: pd.DataFrame, date_col: str, value_col: str,
                        date_format: str = '%Y-%m-%d') -> pd.DataFrame:
    """경제 데이터 공통 전처리"""
    result = df.copy()
    result[date_col] = pd.to_datetime(result[date_col], format=date_format, errors='coerce')
    result[value_col] = pd.to_numeric(result[value_col], errors='coerce')
    result = result.dropna(subset=[date_col, value_col])
    result = result.set_index(date_col).sort_index()
    result = result[~result.index.duplicated(keep='last')]
    return result
```

### 복수 지표 병합

```python
import pandas as pd

def merge_indicators(dataframes: dict[str, pd.DataFrame],
                     value_col: str = 'value') -> pd.DataFrame:
    """복수 지표를 하나의 DataFrame으로 병합"""
    merged = pd.DataFrame()
    for name, df in dataframes.items():
        merged[name] = df[value_col]
    return merged

# 사용 예시
indicators = {
    'GDP': gdp_df,
    'CPI': cpi_df,
    'Interest_Rate': rate_df,
}
combined = merge_indicators(indicators)
corr = combined.corr()
```

### 분석 결과 요약 생성

```python
def generate_summary(df: pd.DataFrame, indicator_name: str,
                     value_col: str = 'value') -> str:
    """분석 결과를 텍스트 요약으로 생성"""
    latest = df[value_col].iloc[-1]
    first = df[value_col].iloc[0]
    total_change = ((latest / first) - 1) * 100
    period_years = (df.index[-1] - df.index[0]).days / 365.25

    yoy = df[value_col].pct_change(12).iloc[-1] * 100 if len(df) > 12 else None

    lines = [
        f"**{indicator_name}** 분석 요약:",
        f"- 분석 기간: {df.index[0].strftime('%Y-%m')} ~ {df.index[-1].strftime('%Y-%m')} ({period_years:.1f}년)",
        f"- 현재 수준: {latest:,.1f}",
        f"- 기간 변화: {first:,.1f} → {latest:,.1f} ({total_change:+.1f}%)",
        f"- 평균: {df[value_col].mean():,.1f}, 표준편차: {df[value_col].std():,.1f}",
    ]

    if yoy is not None:
        lines.append(f"- 최근 YoY 변화율: {yoy:+.1f}%")

    return '\n'.join(lines)
```

---

## 분석 기법 선택 가이드

| 분석 목적 | 기법 | 주요 함수 |
|----------|------|----------|
| 추세 파악 | 이동평균, 선형 추세 | `rolling()`, `polyfit()` |
| 성장률 계산 | YoY, QoQ, CAGR | `pct_change()`, `calc_cagr()` |
| 국가/항목 비교 | 정규화, 순위 | `normalize_to_base()`, `rank()` |
| 이벤트 효과 분석 | 전후 비교 | `before_after_comparison()` |
| 변수 간 관계 | 상관분석 | `corr()`, `lag_correlation()` |
| 미래 전망 | CAGR 전망, 선형 추세 | `cagr_projection()`, `linear_trend()` |
| 계절성 확인 | 계절성 분해 | `seasonal_decompose()` |

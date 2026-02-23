# Chart Code Templates

데이터 리서치 스킬에서 사용하는 차트 코드 템플릿 모음.

---

## 한글 폰트 설정

모든 차트에 적용할 기본 한글 폰트 설정.

```python
import matplotlib.pyplot as plt
import matplotlib

# macOS 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

# 기본 스타일 설정
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['figure.dpi'] = 150
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3
```

---

## Brand Color Palette

```python
BRAND_COLORS = [
    '#4F46E5',  # Indigo (primary)
    '#10B981',  # Emerald (positive/growth)
    '#F59E0B',  # Amber (warning/neutral)
    '#EF4444',  # Red (negative/decline)
    '#8B5CF6',  # Violet
    '#06B6D4',  # Cyan
    '#F97316',  # Orange
]

# 단일 색상 사용 시
BRAND_PRIMARY = '#4F46E5'
BRAND_POSITIVE = '#10B981'
BRAND_NEGATIVE = '#EF4444'
BRAND_NEUTRAL = '#F59E0B'
```

---

## 1. 라인 차트 (시계열)

시간에 따른 추이 비교에 사용. 경제 지표 트렌드 분석의 기본 차트.

```python
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

BRAND_COLORS = ['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4', '#F97316']

def line_chart(data: dict[str, pd.DataFrame], title: str, ylabel: str,
               save_path: str = 'line_chart.png') -> str:
    """
    시계열 라인 차트 생성.
    data: {'라벨': DataFrame(index=date, columns=[value])} 형태
    """
    plt.rcParams['font.family'] = 'AppleGothic'
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(12, 6), dpi=150)

    for i, (label, df) in enumerate(data.items()):
        color = BRAND_COLORS[i % len(BRAND_COLORS)]
        ax.plot(df.index, df['value'], label=label, color=color, linewidth=2)

    ax.set_title(title, fontsize=16, fontweight='bold', pad=15)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.legend(fontsize=11, loc='best', framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    fig.autofmt_xdate()

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight', facecolor='white')
    plt.close()
    return save_path
```

---

## 2. 막대 차트 (비교)

항목 간 비교에 사용. 국가별, 기간별 비교에 적합.

### 세로 막대 차트

```python
import matplotlib.pyplot as plt
import numpy as np

BRAND_COLORS = ['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4', '#F97316']

def bar_chart(categories: list[str], values: list[float], title: str,
              ylabel: str, save_path: str = 'bar_chart.png') -> str:
    """세로 막대 차트 생성"""
    plt.rcParams['font.family'] = 'AppleGothic'
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(12, 6), dpi=150)

    colors = [BRAND_COLORS[i % len(BRAND_COLORS)] for i in range(len(categories))]
    bars = ax.bar(categories, values, color=colors, width=0.6, edgecolor='white')

    # 값 라벨 추가
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(values) * 0.01,
                f'{val:,.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_title(title, fontsize=16, fontweight='bold', pad=15)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight', facecolor='white')
    plt.close()
    return save_path
```

### 가로 막대 차트

```python
def horizontal_bar_chart(categories: list[str], values: list[float], title: str,
                         xlabel: str, save_path: str = 'hbar_chart.png') -> str:
    """가로 막대 차트 생성 (순위 표시에 적합)"""
    plt.rcParams['font.family'] = 'AppleGothic'
    plt.rcParams['axes.unicode_minus'] = False

    # 값 기준 정렬
    sorted_pairs = sorted(zip(categories, values), key=lambda x: x[1])
    cats, vals = zip(*sorted_pairs)

    fig, ax = plt.subplots(figsize=(10, max(6, len(cats) * 0.5)), dpi=150)

    colors = [BRAND_COLORS[i % len(BRAND_COLORS)] for i in range(len(cats))]
    bars = ax.barh(cats, vals, color=colors, height=0.6, edgecolor='white')

    for bar, val in zip(bars, vals):
        ax.text(val + max(vals) * 0.01, bar.get_y() + bar.get_height() / 2,
                f'{val:,.1f}', va='center', fontsize=10, fontweight='bold')

    ax.set_title(title, fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.grid(axis='x', alpha=0.3)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight', facecolor='white')
    plt.close()
    return save_path
```

---

## 3. 히트맵 (상관관계)

변수 간 상관관계 시각화. 복수 경제 지표 간 관계 분석에 사용.

```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def heatmap(corr_matrix: pd.DataFrame, title: str,
            save_path: str = 'heatmap.png') -> str:
    """상관관계 히트맵 생성"""
    plt.rcParams['font.family'] = 'AppleGothic'
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(10, 8), dpi=150)

    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt='.2f',
        cmap='RdBu_r',
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=0.5,
        cbar_kws={'shrink': 0.8, 'label': '상관계수'},
        ax=ax,
    )

    ax.set_title(title, fontsize=16, fontweight='bold', pad=15)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight', facecolor='white')
    plt.close()
    return save_path
```

---

## 4. 산점도 (관계 분석)

두 변수 간 관계 시각화. 추세선 및 그룹 구분 가능.

```python
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BRAND_COLORS = ['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4', '#F97316']

def scatter_plot(df: pd.DataFrame, x_col: str, y_col: str, title: str,
                 group_col: str = None, trend: bool = True,
                 save_path: str = 'scatter.png') -> str:
    """산점도 생성 (그룹별 색상, 추세선 옵션)"""
    plt.rcParams['font.family'] = 'AppleGothic'
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(10, 8), dpi=150)

    if group_col and group_col in df.columns:
        groups = df[group_col].unique()
        for i, group in enumerate(groups):
            mask = df[group_col] == group
            color = BRAND_COLORS[i % len(BRAND_COLORS)]
            ax.scatter(df.loc[mask, x_col], df.loc[mask, y_col],
                       label=group, color=color, s=80, alpha=0.7, edgecolors='white')
    else:
        ax.scatter(df[x_col], df[y_col], color=BRAND_COLORS[0], s=80, alpha=0.7, edgecolors='white')

    if trend:
        x_vals = df[x_col].dropna().values
        y_vals = df[y_col].dropna().values
        mask = ~(np.isnan(x_vals) | np.isnan(y_vals))
        if mask.sum() > 1:
            z = np.polyfit(x_vals[mask], y_vals[mask], 1)
            p = np.poly1d(z)
            x_line = np.linspace(x_vals[mask].min(), x_vals[mask].max(), 100)
            ax.plot(x_line, p(x_line), '--', color='gray', alpha=0.8, linewidth=1.5, label='추세선')

    ax.set_title(title, fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel(x_col, fontsize=12)
    ax.set_ylabel(y_col, fontsize=12)
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight', facecolor='white')
    plt.close()
    return save_path
```

---

## 5. 이중 축 차트 (다른 스케일)

서로 다른 단위의 지표를 하나의 차트에 표시. 예: GDP와 금리.

```python
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

def dual_axis_chart(df1: pd.DataFrame, df2: pd.DataFrame,
                    label1: str, label2: str, ylabel1: str, ylabel2: str,
                    title: str, save_path: str = 'dual_axis.png') -> str:
    """이중 축 차트 생성 (좌: df1, 우: df2)"""
    plt.rcParams['font.family'] = 'AppleGothic'
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax1 = plt.subplots(figsize=(12, 6), dpi=150)
    ax2 = ax1.twinx()

    line1 = ax1.plot(df1.index, df1['value'], color='#4F46E5', linewidth=2, label=label1)
    line2 = ax2.plot(df2.index, df2['value'], color='#EF4444', linewidth=2, label=label2, linestyle='--')

    ax1.set_ylabel(ylabel1, fontsize=12, color='#4F46E5')
    ax2.set_ylabel(ylabel2, fontsize=12, color='#EF4444')
    ax1.tick_params(axis='y', labelcolor='#4F46E5')
    ax2.tick_params(axis='y', labelcolor='#EF4444')

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, fontsize=11, loc='upper left', framealpha=0.9)

    ax1.set_title(title, fontsize=16, fontweight='bold', pad=15)
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    fig.autofmt_xdate()

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight', facecolor='white')
    plt.close()
    return save_path
```

---

## 6. Plotly 차트 (PNG 내보내기)

인터랙티브 차트를 정적 PNG로 내보내기. kaleido 엔진 사용.

```python
import plotly.graph_objects as go
import pandas as pd

BRAND_COLORS = ['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4', '#F97316']

def plotly_line_chart(data: dict[str, pd.DataFrame], title: str, ylabel: str,
                      save_path: str = 'plotly_chart.png') -> str:
    """Plotly 라인 차트를 PNG로 내보내기"""
    fig = go.Figure()

    for i, (label, df) in enumerate(data.items()):
        color = BRAND_COLORS[i % len(BRAND_COLORS)]
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['value'],
            name=label,
            mode='lines',
            line=dict(color=color, width=2.5),
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        yaxis_title=ylabel,
        template='plotly_white',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        width=1200,
        height=600,
        margin=dict(l=60, r=30, t=80, b=60),
        font=dict(family='AppleGothic, Arial', size=12),
    )

    fig.update_xaxes(gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(gridcolor='rgba(0,0,0,0.1)')

    # PNG 내보내기 (kaleido 필요: pip install kaleido)
    fig.write_image(save_path, scale=2)
    return save_path
```

---

## 차트 유형 선택 가이드

| 분석 목적 | 추천 차트 | 함수 |
|----------|----------|------|
| 시간에 따른 추이 | 라인 차트 | `line_chart()` |
| 항목 간 비교 (크기) | 세로 막대 차트 | `bar_chart()` |
| 순위 비교 | 가로 막대 차트 | `horizontal_bar_chart()` |
| 변수 간 상관관계 | 히트맵 | `heatmap()` |
| 두 변수 관계 | 산점도 | `scatter_plot()` |
| 다른 단위 비교 | 이중 축 차트 | `dual_axis_chart()` |
| 고품질 내보내기 | Plotly PNG | `plotly_line_chart()` |

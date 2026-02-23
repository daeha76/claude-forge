---
name: ad-analysis
description: Agent Teams 기반 광고 최적화 분석. 4-Opus 팀으로 Google Ads, Meta Ads, GA4 동시 분석.
user-invocable: false
---

# Ad Analysis (Agent Teams 분석 프롬프트)

이 스킬은 OpenClaw의 `ad-optimizer` 크론에 의해 호출된다.
Claude Code Opus 세션에서 Agent Teams를 사용해 4인 팀으로 분석을 실행한다.

## 실행 방법

이 스킬은 직접 호출하지 않는다. `ad_optimizer.py`가 `coding-agent start`로
Claude Code Opus 세션을 시작하면, 해당 세션이 이 스킬의 지시를 따른다.

## Agent Team 구성

### 팀 생성

```
TeamCreate: ad-optimizer
```

### 작업 목록 (18개)

#### Scout (Google Ads 분석가) - 6개 작업

Scout의 성격: 검색 의도와 품질점수에 집착하는 분석가. CTR, CPC, 노출 점유율, 검색어 관련성으로 말한다.

1. **캠페인 성과 수집** - `mcp__google-ads-mcp__execute_gaql`로 GAQL 실행 (customer_id: 9922616990):
   ```sql
   SELECT campaign.id, campaign.name, campaign.status, campaign.bidding_strategy_type,
          metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions,
          metrics.ctr, metrics.average_cpc, metrics.search_impression_share
   FROM campaign
   WHERE segments.date DURING LAST_7_DAYS AND campaign.status = 'ENABLED'
   ```

2. **이전 기간 비교 데이터** - 동일 쿼리 PREVIOUS_7_DAYS로 `mcp__google-ads-mcp__execute_gaql` 실행

3. **키워드 성과 분석** - `mcp__google-ads-mcp__execute_gaql`로 GAQL:
   ```sql
   SELECT ad_group_criterion.keyword.text, ad_group_criterion.quality_info.quality_score,
          campaign.id, campaign.name, ad_group.id,
          metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions
   FROM keyword_view
   WHERE segments.date DURING LAST_7_DAYS AND metrics.impressions > 0
   ```

4. **검색어 보고서** - `mcp__google-ads-mcp__execute_gaql`로 GAQL:
   ```sql
   SELECT search_term_view.search_term, campaign.id,
          metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions
   FROM search_term_view
   WHERE segments.date DURING LAST_7_DAYS AND metrics.cost_micros > 0
   ```

5. **예산 활용률 분석** - 일예산 대비 실제 소비 비교

6. **결과 저장** - `~/ad-spending-sync/data/google-ads-analysis.json`에 작성
   - `from src.analyzer.google_ads_analyzer import analyze_google_ads` 사용
   - 파싱된 데이터를 함수에 전달, 결과를 JSON으로 저장

#### Pixel (Meta Ads 분석가) - 6개 작업

Pixel의 성격: 크리에이티브 중심 사고, 오디언스와 비주얼 스토리텔링으로 생각한다. ROAS, 빈도, CPM으로 말한다.

1. **캠페인 성과 수집** - `mcp__meta-ads__list_campaigns` + `mcp__meta-ads__get_insights`:
   - date_preset: last_7d
   - fields: spend, impressions, clicks, cpm, ctr, purchase_roas, frequency, reach, actions

2. **광고세트 분석** - `mcp__meta-ads__list_adsets`:
   - 빈도, CTR, 예산 배분 확인

3. **광고(크리에이티브) 성과** - `mcp__meta-ads__list_ads`:
   - 광고별 CTR, 전환 비교

4. **오디언스 피로도 분석** - 빈도 > 5 + CTR 하락 패턴 감지

5. **CBO 효과 평가** - 캠페인 예산 최적화 광고세트 간 배분 효율

6. **결과 저장** - `~/ad-spending-sync/data/meta-ads-analysis.json`에 작성
   - `from src.analyzer.meta_ads_analyzer import analyze_meta_ads` 사용

#### Compass (크로스플랫폼 분석가) - 5개 작업

Compass의 성격: 크로스 플랫폼 사고자, 귀인과 전체 퍼널에 집착한다. "클릭 후 무슨 일이 일어나는가?"

> **NOTE**: analytics-mcp (GA4)는 현재 미설정 상태. GA4 MCP가 없으면 Scout/Pixel의 클릭 데이터에서 세션 수를 추정하여 분석한다. `analyze_analytics()` 함수가 GA4 데이터 없이도 동작하도록 설계되어 있다.

1. **트래픽 소스별 사이트 행동** - `mcp__analytics-mcp__run_report` (GA4 MCP 연결 시):
   - dimensions: sessionSource, sessionMedium
   - metrics: sessions, bounceRate, averageSessionDuration, conversions
   - **폴백**: GA4 미연결 시 Scout/Pixel 데이터에서 클릭 기반 추정

2. **랜딩페이지 성과** - `mcp__analytics-mcp__run_report` (GA4 MCP 연결 시):
   - dimensions: landingPage
   - metrics: sessions, bounceRate, averageSessionDuration, conversions
   - **폴백**: GA4 미연결 시 건너뛰기 (추정 불가)

3. **Google vs Meta 트래픽 품질 비교** - 이탈률, 세션 시간, 전환율 교차 분석

4. **통합 ROAS 계산** - 전체 광고 비용 대비 전체 전환

5. **결과 저장** - `~/ad-spending-sync/data/analytics-correlation.json`에 작성
   - `from src.analyzer.analytics_correlator import analyze_analytics` 사용

#### Strategist (리더, 전략가) - 3개 작업 (Phase 2)

Strategist의 성격: 냉철한 데이터 기반 의사결정자. KPI와 비즈니스 성과로만 말한다.

이 3개 작업은 Scout, Pixel, Compass가 모두 완료된 후 실행:

1. **3개 분석 파일 종합** - 각 JSON 파일 읽기 및 교차 분석

2. **추천 우선순위화** - `from src.analyzer.recommendation_engine import synthesize_recommendations, save_analysis_outputs` 사용

3. **최종 저장** - `save_analysis_outputs()` 호출로 다음 파일 생성:
   - `data/pending-recommendations.json` (최종 추천)
   - `data/analysis-summary.json` (종합 요약)

### 파일 소유권 (충돌 방지 - CRITICAL)

| 파일 | 소유자 |
|------|--------|
| `data/google-ads-analysis.json` | Scout |
| `data/meta-ads-analysis.json` | Pixel |
| `data/analytics-correlation.json` | Compass |
| `data/analysis-summary.json` | Strategist |
| `data/pending-recommendations.json` | Strategist |

### 팀원 스펙

| 팀원 | subagent_type | 모델 |
|------|-------------|------|
| Scout | general-purpose | opus |
| Pixel | general-purpose | opus |
| Compass | general-purpose | opus |

리더(Strategist)는 자동으로 현재 세션.

### 워크플로우 타임라인

```
Phase 0: TeamCreate + TaskCreate (18개 작업)        [2분]
Phase 1: 병렬 분석 (Scout, Pixel, Compass 동시)     [5-8분]
Phase 2: Strategist 종합 + 추천 우선순위화           [2-3분]
Phase 3: Shutdown + TeamDelete                      [1분]
총: 10분 이내
```

### 의사결정 규칙 요약

#### 예산 조정
- `target_cpa / actual_cpa > 1.2`: 예산 +15~25%
- `ratio > 1.0`: 예산 +5%
- `ratio < 0.85`: 예산 -15%~중지 (사용자 승인)
- 단일 조정 최대 20%, 최소 일예산 5,000원

#### 제외 키워드
- 노출 >= 10 AND 전환 = 0: 자동 승인
- CPA > 목표 x 1.3: 사용자 승인

#### 크리에이티브 피로도
- CTR 15~20% 하락: 교체 추천
- 빈도 > 5 + CTR 하락: 일시 중지 추천

#### 크로스 플랫폼
- Google ROAS > Meta x 1.2: Meta → Google 10% 이동
- Meta ROAS > Google x 1.15: Google → Meta 10% 이동
- 차이 10% 이내: 현 배분 유지

### 출력 형식

`data/pending-recommendations.json` 스키마:
```json
{
  "analysis_date": "2026-02-19",
  "period": {"start": "2026-02-12", "end": "2026-02-18"},
  "summary": {
    "google": {"spend": 1234567, "campaigns": 5, "ctr": 3.2, "cpc": 850},
    "meta": {"spend": 567890, "campaigns": 3, "cpm": 12500, "roas": 2.8, "frequency": 3.2},
    "total_spend": 1802457,
    "blended_roas": 2.35
  },
  "recommendations": [
    {
      "id": "rec-001",
      "platform": "google",
      "change_type": "budget",
      "priority": "high",
      "description": "...",
      "expected_impact": "...",
      "current_value": "50000",
      "proposed_value": "60000",
      "campaign_id": "12345678",
      "campaign_name": "...",
      "confidence": 0.85,
      "evidence": "...",
      "auto_approvable": false
    }
  ],
  "status": "pending",
  "created_at": "2026-02-19T06:10:00+09:00"
}
```

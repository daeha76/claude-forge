---
description: 리드 발굴 + 콜드메일 작성 (v2.1 버그 수정)
allowed-tools: Read, Write, Edit, mcp__hyperbrowser__*, Bash(python3:*), Bash(mkdir:*), Bash(cat:*), Bash(cp:*), Bash(diff:*), Bash(ls:*), Bash(wc:*), Bash(grep:*), Bash(echo:*)
argument-hint: <타겟 산업/키워드>
---

# 리드 발굴 에이전트

## CRITICAL EXECUTION RULES

```
┌─────────────────────────────────────────────────────────────┐
│ 절대 규칙 - 위반 시 버그 발생                               │
├─────────────────────────────────────────────────────────────┤
│ 1. Claude는 품질 점수를 직접 계산하지 않는다               │
│ 2. 반드시 python3 score_engine.py 실행 결과만 사용한다     │
│ 3. 스크립트 미실행 상태에서 PASS/FAIL 판정 금지            │
│ 4. coldmail_v1.md = final.md 동일하면 버그 (Refiner 미실행)│
│ 5. 첫 리뷰는 점수 무관하게 반드시 Refiner 1회 실행         │
└─────────────────────────────────────────────────────────────┘
```

## 입력

**타겟**: $ARGUMENTS

**컨텍스트**:
- CLAUDE.md: !`head -100 CLAUDE.md`
- 체크리스트: !`cat quality/checklists/coldmail.json 2>/dev/null || echo "체크리스트 없음"`
- Hyperbrowser MCP 필수

## 출력 폴더 생성

!`mkdir -p output/$(date +%Y%m%d)_leads/coldmails && echo "출력 폴더: output/$(date +%Y%m%d)_leads"`

---

## Step 1: Research Agent

### 실행
1. Hyperbrowser MCP로 타겟 기업 검색
2. LinkedIn, 회사 사이트에서 의사결정자 정보 수집
3. 기업 정보, 연락처, 담당자 이름/직책 수집

### 출력
`output/[날짜]_leads/leads_raw.csv` 저장

CSV 형식:
```csv
company,website,contact_name,title,email,linkedin,industry,size,notes
```

### 검증
!`ls output/*/leads_raw.csv 2>/dev/null && wc -l output/*/leads_raw.csv || echo "❌ leads_raw.csv 없음"`

---

## Step 2: 분석 & 우선순위

### 실행
1. 기업 규모, 산업, 니즈 분석
2. 리드 점수화 (1-10)
3. 우선순위 정렬

### 출력
`output/[날짜]_leads/leads_scored.csv` 저장

CSV 형식 (추가 컬럼):
```csv
company,...,lead_score,priority,reason
```

### 검증
!`ls output/*/leads_scored.csv 2>/dev/null && wc -l output/*/leads_scored.csv || echo "❌ leads_scored.csv 없음"`

---

## Step 3: Writer Agent - 콜드메일 작성

### 실행
1. 각 리드별 개인화된 콜드메일 작성
2. 대표 템플릿 먼저 작성

### 콜드메일 구조 (필수 항목 표시)
| 항목 | 필수 최소 점수 |
|------|---------------|
| 개인화 (personal) | **70%** |
| 가치 제안 (value) | **70%** |
| CTA (cta) | - |
| 간결성 (concise) | - |
| 제목 (subject) | - |

### 출력
- `output/[날짜]_leads/coldmail_template_v1.md` (대표 템플릿)
- `output/[날짜]_leads/coldmails/[company].md` (개별 콜드메일)

### 검증
!`ls output/*/coldmail_template_v1.md 2>/dev/null && wc -l output/*/coldmail_template_v1.md || echo "❌ coldmail_template_v1.md 없음"`

---

## Step 4: Reviewer Agent (CRITICAL - 스크립트 강제 실행)

### 절대 규칙
- Claude는 점수를 직접 계산하지 않는다
- 아래 스크립트 실행 결과만 사용한다

### 4.1 스크립트 실행 (필수)

**이 명령을 반드시 실행하고 결과를 파싱해야 함:**
!`TEMPLATE=$(ls output/*_leads/coldmail_template_v1.md 2>/dev/null | head -1) && python3 quality/score_engine.py "$TEMPLATE" coldmail --json 2>&1`

**실행 결과 예시**:
```json
{
  "final_score": 65.0,
  "passed": false,
  "needs_refinement": true,
  "threshold": 85,
  "iteration": 1,
  "required_check": {"passed": false, "failed_items": ["개인화 (60% < 70%)"]}
}
```

### 4.2 결과 저장

!`TEMPLATE=$(ls output/*_leads/coldmail_template_v1.md 2>/dev/null | head -1) && DIR=$(dirname "$TEMPLATE") && python3 quality/score_engine.py "$TEMPLATE" coldmail > "$DIR/review_report.md" 2>&1 && echo "✅ review_report.md 저장됨 ($DIR)"`

### 4.3 분기 결정

**스크립트 출력에서 `needs_refinement` 값 확인:**

- `needs_refinement: true` → **Step 5 (Refiner) 실행**
- `needs_refinement: false` → Step 6 (완료)으로 이동

**v2.0 정책**: iteration=1이면 점수 무관하게 `needs_refinement=true`

### 4.4 검증

!`grep -E "final_score|needs_refinement|threshold" output/*/review_report.md 2>/dev/null || echo "❌ 리뷰 리포트 형식 오류"`

**반드시 확인**:
- threshold가 85인가? (80이면 v1.0 버그)
- iteration=1에서 needs_refinement=true인가?

---

## Step 5: Refiner Agent (CRITICAL - v2.0 정책)

### v2.0 정책
```
ALWAYS_REFINE_ONCE = True
→ 첫 번째 리뷰(iteration=1)는 점수 무관하게 Refiner 반드시 실행
```

### 5.1 조건 확인

Step 4의 JSON 결과에서 `needs_refinement` 값 확인:
- `true` → 이 단계 실행
- `false` → Step 6으로 이동

### 5.2 피드백 추출

review_report.md 또는 JSON 결과의 `improvement_feedback` 분석

### 5.3 개선 실행

1. coldmail_template_v1.md 로드
2. 피드백 반영:
   - **필수 항목 미달 → 우선 수정** (personal 70%, value 70%)
   - 개인화 강화 (이름, 회사, 역할 구체화)
   - 가치 제안 명확화
   - CTA 단일화
3. `output/[날짜]_leads/coldmail_template_v2.md` 저장

### 5.4 개별 콜드메일 재생성

수정된 템플릿으로 `output/[날짜]_leads/coldmails/` 갱신

### 5.5 재검증 (iteration=2)

**coldmail_template_v2.md 저장 후 실행:**
!`TEMPLATE2=$(ls output/*_leads/coldmail_template_v2.md 2>/dev/null | head -1); [ -n "$TEMPLATE2" ] && DIR=$(dirname "$TEMPLATE2") && python3 quality/score_engine.py "$TEMPLATE2" coldmail --iteration 2 --json 2>&1 && python3 quality/score_engine.py "$TEMPLATE2" coldmail --iteration 2 > "$DIR/review_report_v2.md" 2>&1 || echo "⚠️ coldmail_template_v2.md 저장 후 다시 실행"`

### 5.6 반복 (최대 5회)

- `needs_refinement: false` → Step 6으로 이동
- `needs_refinement: true` && iteration < 5 → coldmail_template_v3.md 생성, 재검증
- iteration >= 5 → "⚠️ 최대 반복 도달, 수동 검토 필요" 출력 후 진행

### 5.7 검증 (CRITICAL)

!`ls output/*/coldmail_template_v*.md 2>/dev/null | wc -l`

**결과가 2 이상이어야 함** (v1, v2 최소)
coldmail_template_v1.md만 있으면 Refiner 미실행 버그!

---

## Step 6: 최종 정리

### 6.1 최종본 결정

가장 최신 통과한 템플릿을 final로 복사:
!`LATEST=$(ls -t output/*_leads/coldmail_template_v*.md 2>/dev/null | head -1) && DIR=$(dirname "$LATEST") && cp "$LATEST" "$DIR/final_coldmail_template.md" && echo "최종본: $LATEST → $DIR/final_coldmail_template.md"`

### 6.2 산출물 확인

!`echo "=== 리드 파일 ===" && ls -la output/*/leads_*.csv 2>/dev/null`
!`echo "=== 콜드메일 파일 ===" && ls -la output/*/coldmail*.md output/*/coldmails/*.md 2>/dev/null | head -10`

---

## 완료 검증 (필수 체크)

### 자동 검증 스크립트

!`echo "╔══════════════════════════════════════════════════════════╗" && \
echo "║         /leads 실행 결과 검증                            ║" && \
echo "╠══════════════════════════════════════════════════════════╣" && \
if grep -q "threshold.*85\|통과 기준: 85" output/*/review_report*.md 2>/dev/null; then echo "║ ✅ 1. PASS 기준 85%"; else echo "║ ❌ 1. PASS 기준 오류 (85% 아님)"; fi && \
TEMPLATE_COUNT=$(ls output/*/coldmail_template_v*.md 2>/dev/null | wc -l | tr -d ' ') && \
if [ "$TEMPLATE_COUNT" -ge 2 ]; then echo "║ ✅ 2. Refiner 실행됨 (템플릿 ${TEMPLATE_COUNT}개)"; else echo "║ ❌ 2. Refiner 미실행 (템플릿 ${TEMPLATE_COUNT}개)"; fi && \
if ! diff -q output/*/coldmail_template_v1.md output/*/final_coldmail_template.md > /dev/null 2>&1; then echo "║ ✅ 3. template_v1 ≠ final (정상)"; else echo "║ ❌ 3. template_v1 = final (버그! Refiner 미실행)"; fi && \
LEADS_COUNT=$(wc -l < output/*/leads_scored.csv 2>/dev/null || echo 0) && \
echo "║ ℹ️ 4. 리드 수: ${LEADS_COUNT}개" && \
echo "╚══════════════════════════════════════════════════════════╝"`

---

## 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| review_report.md에 81.50% | 스크립트 미실행, Claude 자체 판단 | `python3 quality/score_engine.py` 직접 실행 |
| threshold: 80 | v1.0 스크립트 사용 | score_engine.py의 PASS_THRESHOLD=85 확인 |
| template_v1 = final | Refiner 미실행 | needs_refinement 값 확인, Step 5 강제 실행 |
| Hyperbrowser 오류 | MCP 연결 실패 | `/mcp` 명령으로 상태 확인 |

---

## 산출물 체크리스트

- [ ] output/[날짜]_leads/leads_raw.csv
- [ ] output/[날짜]_leads/leads_scored.csv
- [ ] output/[날짜]_leads/coldmail_template_v1.md
- [ ] output/[날짜]_leads/review_report.md
- [ ] output/[날짜]_leads/coldmail_template_v2.md (Refiner 실행 시)
- [ ] output/[날짜]_leads/final_coldmail_template.md
- [ ] output/[날짜]_leads/coldmails/*.md (개별 콜드메일)

**완료 시 출력**: "리드 발굴 완료"

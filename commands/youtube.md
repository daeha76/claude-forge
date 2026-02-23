---
description: 유튜브 영상 기획 (PPT + 스크립트 + 썸네일) (v2.1 버그 수정)
allowed-tools: Read, Write, Edit, Bash(python3:*), Bash(mmdc:*), Bash(mkdir:*), Bash(cat:*), Bash(cp:*), Bash(diff:*), Bash(ls:*), Bash(wc:*), Bash(grep:*), Bash(echo:*), mcp__hyperbrowser__*
argument-hint: <영상 주제>
---

# 유튜브 기획 에이전트

## CRITICAL EXECUTION RULES

```
┌─────────────────────────────────────────────────────────────┐
│ 절대 규칙 - 위반 시 버그 발생                               │
├─────────────────────────────────────────────────────────────┤
│ 1. Claude는 품질 점수를 직접 계산하지 않는다               │
│ 2. 반드시 python3 score_engine.py 실행 결과만 사용한다     │
│ 3. 스크립트 미실행 상태에서 PASS/FAIL 판정 금지            │
│ 4. draft_v1.md = final.md 동일하면 버그 (Refiner 미실행)   │
│ 5. 첫 리뷰는 점수 무관하게 반드시 Refiner 1회 실행         │
└─────────────────────────────────────────────────────────────┘
```

## 입력

**주제**: $ARGUMENTS

**컨텍스트**:
- CLAUDE.md: !`head -100 CLAUDE.md`
- 템플릿: !`cat templates/youtube/template.md 2>/dev/null || echo "템플릿 없음"`
- 체크리스트: !`cat quality/checklists/youtube.json 2>/dev/null || echo "체크리스트 없음"`

## 출력 폴더 생성

!`mkdir -p output/$(date +%Y%m%d)_youtube && echo "출력 폴더: output/$(date +%Y%m%d)_youtube"`

---

## Step 1: Research Agent

### 실행
1. input/ 폴더 확인: !`ls input/ 2>/dev/null | head -5 || echo "input 폴더 비어있음"`
2. 유사 인기 영상 분석 (Hyperbrowser MCP 활용)
3. 키워드/트렌드 조사
4. 타겟 시청자 분석

### 출력
`output/[날짜]_youtube/research_notes.md` 저장

### 검증
!`ls output/*/research_notes.md 2>/dev/null && echo "✅ research_notes.md 생성됨" || echo "⚠️ research_notes.md 미생성 - 직접 작성 필요"`

---

## Step 2: Writer Agent

### 실행
1. templates/youtube/template.md 로드 (있으면)
2. research_notes.md 참조
3. 영상 기획서 작성

### 산출물 구조 (필수 항목 표시)
| 항목 | 필수 최소 점수 |
|------|---------------|
| 후킹 (hook) - 첫 5초 | **75%** |
| 구조 (struct) | - |
| 시청자 가치 (value) | **70%** |
| SEO 최적화 (seo) | - |
| 썸네일 (thumb) | - |
| CTA (cta) | - |
| 적정 길이 (length) | - |

### 출력 파일
- `output/[날짜]_youtube/youtube_script_v1.md` (나레이션 스크립트)
- `output/[날짜]_youtube/youtube_ppt.md` (슬라이드별 구성)
- `output/[날짜]_youtube/youtube_thumbnail.md` (썸네일 전략)
- `output/[날짜]_youtube/youtube_seo.md` (제목, 설명, 태그, 해시태그)

### 검증
!`ls output/*/youtube_script_v1.md 2>/dev/null && wc -l output/*/youtube_script_v1.md || echo "❌ youtube_script_v1.md 없음"`

---

## Step 3: Reviewer Agent (CRITICAL - 스크립트 강제 실행)

### 절대 규칙
- Claude는 점수를 직접 계산하지 않는다
- 아래 스크립트 실행 결과만 사용한다

### 3.1 스크립트 실행 (필수)

**이 명령을 반드시 실행하고 결과를 파싱해야 함:**
!`SCRIPT=$(ls output/*_youtube/youtube_script_v1.md 2>/dev/null | head -1) && python3 quality/score_engine.py "$SCRIPT" youtube --json 2>&1`

**실행 결과 예시**:
```json
{
  "final_score": 68.5,
  "passed": false,
  "needs_refinement": true,
  "threshold": 85,
  "iteration": 1,
  "required_check": {"passed": false, "failed_items": ["후킹 (70% < 75%)"]}
}
```

### 3.2 결과 저장

!`SCRIPT=$(ls output/*_youtube/youtube_script_v1.md 2>/dev/null | head -1) && DIR=$(dirname "$SCRIPT") && python3 quality/score_engine.py "$SCRIPT" youtube > "$DIR/review_report.md" 2>&1 && echo "✅ review_report.md 저장됨 ($DIR)"`

### 3.3 분기 결정

**스크립트 출력에서 `needs_refinement` 값 확인:**

- `needs_refinement: true` → **Step 4 (Refiner) 실행**
- `needs_refinement: false` → Step 5 (Formatter)로 이동

**v2.0 정책**: iteration=1이면 점수 무관하게 `needs_refinement=true`

### 3.4 검증

!`grep -E "final_score|needs_refinement|threshold" output/*/review_report.md 2>/dev/null || echo "❌ 리뷰 리포트 형식 오류"`

**반드시 확인**:
- threshold가 85인가? (80이면 v1.0 버그)
- iteration=1에서 needs_refinement=true인가?

---

## Step 4: Refiner Agent (CRITICAL - v2.0 정책)

### v2.0 정책
```
ALWAYS_REFINE_ONCE = True
→ 첫 번째 리뷰(iteration=1)는 점수 무관하게 Refiner 반드시 실행
```

### 4.1 조건 확인

Step 3의 JSON 결과에서 `needs_refinement` 값 확인:
- `true` → 이 단계 실행
- `false` → Step 5로 이동

### 4.2 피드백 추출

review_report.md 또는 JSON 결과의 `improvement_feedback` 분석

### 4.3 개선 실행

1. youtube_script_v1.md 로드
2. 피드백 반영:
   - **필수 항목 미달 → 우선 수정** (hook 75%, value 70%)
   - 후킹 강화 (첫 5초 임팩트)
   - 시청자 가치 명확화
   - CTA 개선
3. 수정본 저장:
   - `output/[날짜]_youtube/youtube_script_v2.md`
   - `output/[날짜]_youtube/youtube_ppt_v2.md` (필요시)

### 4.4 재검증 (iteration=2)

**youtube_script_v2.md 저장 후 실행:**
!`SCRIPT2=$(ls output/*_youtube/youtube_script_v2.md 2>/dev/null | head -1); [ -n "$SCRIPT2" ] && DIR=$(dirname "$SCRIPT2") && python3 quality/score_engine.py "$SCRIPT2" youtube --iteration 2 --json 2>&1 && python3 quality/score_engine.py "$SCRIPT2" youtube --iteration 2 > "$DIR/review_report_v2.md" 2>&1 || echo "⚠️ youtube_script_v2.md 저장 후 다시 실행"`

### 4.5 반복 (최대 5회)

- `needs_refinement: false` → Step 5로 이동
- `needs_refinement: true` && iteration < 5 → youtube_script_v3.md 생성, 재검증
- iteration >= 5 → "⚠️ 최대 반복 도달, 수동 검토 필요" 출력 후 진행

### 4.6 검증 (CRITICAL)

!`ls output/*/youtube_script_v*.md 2>/dev/null | wc -l`

**결과가 2 이상이어야 함** (v1, v2 최소)
youtube_script_v1.md만 있으면 Refiner 미실행 버그!

---

## Step 5: Formatter Agent

### 공식 문서 스킬 참조
> **Anthropic document-skills 활용 가능** (설치됨)
> - PPTX 생성: `~/.claude/plugins/marketplaces/anthropic-agent-skills/skills/pptx/SKILL.md`
> - html2pptx: HTML → PPTX 정밀 변환
> - 템플릿 편집: inventory.py, replace.py 스크립트
> - 썸네일 검증: thumbnail.py로 시각적 확인

### 5.1 최종본 결정

가장 최신 통과한 스크립트 파일을 final로 복사:
!`LATEST=$(ls -t output/*_youtube/youtube_script_v*.md 2>/dev/null | head -1) && DIR=$(dirname "$LATEST") && cp "$LATEST" "$DIR/final_youtube_script.md" && echo "최종본: $LATEST → $DIR/final_youtube_script.md"`

### 5.2 PPTX 변환

!`PPT=$(ls output/*_youtube/youtube_ppt.md 2>/dev/null | head -1) && python3 agents/formatter_agent.py "$PPT" pptx 2>&1 || echo "⚠️ PPTX 변환 실패"`

### 5.3 Mermaid 렌더링 (있는 경우)

!`FINAL=$(ls output/*_youtube/final_youtube_script.md 2>/dev/null | head -1) && python3 agents/formatter_agent.py "$FINAL" mermaid 2>&1 || echo "⚠️ Mermaid 렌더링 실패"`

### 5.4 출력 파일 확인

!`ls -la output/*/{final_youtube_script.md,youtube_ppt.md,youtube_thumbnail.md,*.pptx,*.png} 2>/dev/null | head -10 || echo "⚠️ 일부 출력 파일 없음"`

---

## 완료 검증 (필수 체크)

### 자동 검증 스크립트

!`echo "╔══════════════════════════════════════════════════════════╗" && \
echo "║         /youtube 실행 결과 검증                          ║" && \
echo "╠══════════════════════════════════════════════════════════╣" && \
if grep -q "threshold.*85\|통과 기준: 85" output/*/review_report*.md 2>/dev/null; then echo "║ ✅ 1. PASS 기준 85%"; else echo "║ ❌ 1. PASS 기준 오류 (85% 아님)"; fi && \
DRAFT_COUNT=$(ls output/*/youtube_script_v*.md 2>/dev/null | wc -l | tr -d ' ') && \
if [ "$DRAFT_COUNT" -ge 2 ]; then echo "║ ✅ 2. Refiner 실행됨 (script 파일 ${DRAFT_COUNT}개)"; else echo "║ ❌ 2. Refiner 미실행 (script 파일 ${DRAFT_COUNT}개)"; fi && \
if ! diff -q output/*/youtube_script_v1.md output/*/final_youtube_script.md > /dev/null 2>&1; then echo "║ ✅ 3. script_v1 ≠ final (정상)"; else echo "║ ❌ 3. script_v1 = final (버그! Refiner 미실행)"; fi && \
echo "╚══════════════════════════════════════════════════════════╝"`

---

## 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| review_report.md에 81.50% | 스크립트 미실행, Claude 자체 판단 | `python3 quality/score_engine.py` 직접 실행 |
| threshold: 80 | v1.0 스크립트 사용 | score_engine.py의 PASS_THRESHOLD=85 확인 |
| script_v1 = final | Refiner 미실행 | needs_refinement 값 확인, Step 4 강제 실행 |
| PPTX 변환 실패 | python-pptx 미설치 | `pip3 install python-pptx` |

---

## 산출물 체크리스트

- [ ] output/[날짜]_youtube/research_notes.md
- [ ] output/[날짜]_youtube/youtube_script_v1.md
- [ ] output/[날짜]_youtube/youtube_ppt.md
- [ ] output/[날짜]_youtube/youtube_thumbnail.md
- [ ] output/[날짜]_youtube/youtube_seo.md
- [ ] output/[날짜]_youtube/review_report.md
- [ ] output/[날짜]_youtube/youtube_script_v2.md (Refiner 실행 시)
- [ ] output/[날짜]_youtube/final_youtube_script.md
- [ ] output/[날짜]_youtube/presentation_*.pptx

**완료 시 출력**: "유튜브 기획 완료"

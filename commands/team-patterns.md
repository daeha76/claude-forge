# 팀 워크플로우 패턴

## 전제조건

Agent Teams 사용 전 반드시 활성화:
```json
// settings.json
{ "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }
```

## 공통 규칙
- 최대 팀원 수: 리더 1 + 팀원 3 (4명)
- 파일 소유권 분리 필수 (같은 파일 2명 편집 금지)
- 팀원당 5-6개 태스크 배정
- 팀원은 리더 대화 기록 미상속 → 생성 프롬프트에 충분한 컨텍스트 제공
- CLAUDE.md는 팀원에게 자동 적용됨
- broadcast는 비용이 팀 크기에 비례 → 긴급 시에만 사용

## 패턴 1: 풀스택 기능 구현

### 팀 구성
| 역할 | subagent_type | 모델 | 담당 |
|------|--------------|------|------|
| Frontend Dev | general-purpose | sonnet | UI 구현, 컴포넌트 |
| Backend Dev | general-purpose | sonnet | API, DB, 로직 |
| QA Engineer | general-purpose | sonnet | 테스트, E2E |

### MCP 분배
- Frontend: playwright (E2E), stitch (UI 목업)
- Backend: memory (캐싱), desktop-commander (프로세스)
- QA: playwright (E2E), analytics-mcp (성능)

### 추천 스킬
- Frontend: frontend-patterns, react-verify, cache-components
- Backend: backend-patterns, postgres-patterns, orpc-contract-first
- QA: e2e, frontend-testing, tdd

### 태스크 분해 예시
Frontend (5개): UI 컴포넌트 구현, 스타일링, 클라이언트 상태, 폼 유효성, 반응형
Backend (5개): API 엔드포인트, DB 스키마, 비즈니스 로직, 인증/인가, 에러 핸들링
QA (6개): 단위 테스트, 통합 테스트, E2E 시나리오, 성능 테스트, 접근성, 크로스 브라우저

## 패턴 2: 콘텐츠 제작 & 배포

### 팀 구성
| 역할 | subagent_type | 모델 | 담당 |
|------|--------------|------|------|
| Writer | general-purpose | sonnet | 콘텐츠 작성 |
| Designer | general-purpose | sonnet | 디자인/영상 |
| Distributor | general-purpose | haiku | 배포/알림 |

### MCP 분배
- Writer: exa (리서치), youtube-transcript (참고)
- Designer: stitch (디자인), remotion (영상)
- Distributor: gmail (발송), google-calendar (스케줄)

### 추천 스킬
- Writer: content-creator, copywriting, seo-review
- Designer: remotion-best-practices, video-frames, youtube
- Distributor: leads, content-creator

### 태스크 분해 예시
Writer (5개): 주제 리서치, 아웃라인, 초안 작성, 편집/교정, SEO 최적화
Designer (5개): 브랜드 가이드 확인, 썸네일, 영상 편집, 시각 자료, 최종 렌더링
Distributor (5개): 채널별 포맷, 스케줄 설정, 이메일 캠페인, 소셜 포스팅, 성과 추적

## 패턴 3: 마케팅 캠페인

### 팀 구성
| 역할 | subagent_type | 모델 | 담당 |
|------|--------------|------|------|
| Analyst | general-purpose | sonnet | 데이터 분석 |
| Creative | general-purpose | sonnet | 광고 소재 제작 |
| Automation | general-purpose | haiku | 워크플로우 설정 |

### MCP 분배
- Analyst: analytics-mcp, google-ads-mcp, meta-ads
- Creative: stitch (랜딩), remotion (영상 광고)
- Automation: n8n-mcp, gmail

### 추천 스킬
- Analyst: data-storytelling, paid-ads, market-research-reports
- Creative: content-creator, competitive-ads-extractor, copywriting
- Automation: suggest-automation

### 태스크 분해 예시
Analyst (5개): 현황 분석, 경쟁사 벤치마크, 타겟 세그먼트, KPI 설정, 보고서
Creative (5개): 메시지 전략, 카피 작성, 비주얼 제작, A/B 변형, 랜딩 페이지
Automation (5개): 캠페인 구조, 자동 규칙, 리드 파이프라인, 리타겟팅, 알림 설정

## 패턴 4: 리서치 & 리포트

### 팀 구성
| 역할 | subagent_type | 모델 | 담당 |
|------|--------------|------|------|
| Researcher 1 | Explore | sonnet | 1차 자료 수집 |
| Researcher 2 | Explore | sonnet | 2차 자료 수집 |
| Synthesizer | general-purpose | sonnet | 종합/보고서 작성 |

### MCP 분배
- Researcher 1: exa (웹 검색), hyperbrowser (스크래핑)
- Researcher 2: youtube-transcript, context7, data-go-*
- Synthesizer: memory (지식 저장), gmail (보고서 발송)

### 추천 스킬
- Researchers: data-research, explore, summarize
- Synthesizer: data-storytelling, market-research-reports, plotly

## 패턴 5: 버그 조사 & 수정

### 팀 구성
| 역할 | subagent_type | 모델 | 담당 |
|------|--------------|------|------|
| Investigator 1 | Explore | sonnet | 코드 분석 |
| Investigator 2 | Explore | sonnet | 로그/환경 분석 |
| Fixer | general-purpose | sonnet | 수정 구현 |

### MCP 분배
- Investigator 1: context7 (문서 확인)
- Investigator 2: playwright (재현 테스트), desktop-commander (로그)
- Fixer: context7 (해결책 참조), playwright (수정 검증)

### 추천 스킬
- Investigators: systematic-debugging, explore
- Fixer: tdd, fix, build-fix

## 패턴 6: 리팩토링 & 코드 품질

### 팀 구성
| 역할 | subagent_type | 모델 | 담당 |
|------|--------------|------|------|
| Analyzer | Explore | sonnet | 코드 분석/계획 |
| Implementer | general-purpose | sonnet | 리팩토링 실행 |
| Verifier | general-purpose | sonnet | 테스트/검증 |

### MCP 분배
- Analyzer: context7 (패턴 참조)
- Implementer: memory (리팩토링 결정 기록)
- Verifier: playwright (E2E 회귀 테스트)

### 추천 스킬
- Analyzer: coding-standards, explore
- Implementer: refactor-clean, component-refactoring
- Verifier: tdd, e2e, frontend-testing

## 패턴 7: E2E 테스트 스위트

### 팀 구성
| 역할 | subagent_type | 모델 | 담당 |
|------|--------------|------|------|
| Test Designer | general-purpose | sonnet | 테스트 시나리오 설계 |
| Test Writer 1 | general-purpose | sonnet | 핵심 플로우 테스트 |
| Test Writer 2 | general-purpose | sonnet | 엣지 케이스 테스트 |

### MCP 분배
- 전원: playwright (브라우저 자동화)
- Test Designer: hyperbrowser (경쟁사 UX 참고)

### 추천 스킬
- e2e, frontend-testing, react-verify, tdd

## 패턴 8: 사업 기획

### 팀 구성
| 역할 | subagent_type | 모델 | 담당 |
|------|--------------|------|------|
| Market Analyst | general-purpose | sonnet | 시장/경쟁 분석 |
| Business Planner | general-purpose | sonnet | 사업계획서 |
| Financial Modeler | general-purpose | sonnet | 재무 모델링 |

### MCP 분배
- Market Analyst: exa (시장 리서치), analytics-mcp (트래픽), meta-ads (경쟁사 광고)
- Business Planner: memory (기존 전략 참조), sequential-thinking
- Financial Modeler: data-go-fsc (재무 벤치마크), data-go-nps (사업장 정보)

### 추천 스킬
- Market Analyst: market-research-reports, market-sizing-analysis, competitive-ads-extractor
- Business Planner: bizmodel, brainstorming, ceo-advisor
- Financial Modeler: financial-analysis, startup-financial-modeling, risk-metrics-calculation

## 패턴 9: 보안 감사

### 팀 구성
| 역할 | subagent_type | 모델 | 담당 |
|------|--------------|------|------|
| Code Auditor | Explore | sonnet | 소스 코드 취약점 |
| Infra Auditor | general-purpose | sonnet | 인프라/설정 검사 |
| Reporter | general-purpose | sonnet | 보고서/수정 |

### MCP 분배
- Code Auditor: context7 (보안 라이브러리 문서), exa (CVE 검색)
- Infra Auditor: desktop-commander (서버 설정 확인)
- Reporter: gmail (보안 보고서 발송), memory (취약점 기록)

### 추천 스킬
- Code Auditor: security-review, stride-analysis-patterns
- Infra Auditor: security-compliance
- Reporter: data-storytelling

## 패턴 10: 데이터 분석 & 시각화

### 팀 구성
| 역할 | subagent_type | 모델 | 담당 |
|------|--------------|------|------|
| Data Collector | general-purpose | sonnet | 데이터 수집 |
| Data Analyst | general-purpose | sonnet | 분석/모델링 |
| Visualizer | general-purpose | sonnet | 시각화/보고서 |

### MCP 분배
- Data Collector: exa, hyperbrowser (스크래핑), data-go-* (공공데이터)
- Data Analyst: analytics-mcp, sequential-thinking
- Visualizer: stitch (차트 디자인), gmail (보고서 발송)

### 추천 스킬
- Data Collector: data-research, explore, extract-errors
- Data Analyst: data-storytelling, financial-analysis
- Visualizer: plotly, market-research-reports

## 공통 에러 복구 패턴

### MCP 타임아웃
1. 재시도 (1회)
2. 실패 시 대안 MCP 사용 (예: hyperbrowser -> exa)
3. 대안 없으면 리더에게 보고

### 팀원 파일 충돌
1. 리더가 충돌 감지
2. 한 팀원에게 해당 파일 소유권 위임
3. 다른 팀원은 대기 후 진행

### MCP 레이트 리밋
1. 60초 대기 후 재시도
2. 다른 태스크 먼저 진행
3. 지속되면 리더에게 보고

### 팀원 무응답
1. SendMessage로 상태 확인
2. 5분 초과 시 태스크 재배정
3. 필요시 새 팀원 생성

### 팀원이 나타나지 않음
1. In-process: Shift+Down으로 활성 팀원 순환
2. 분할 창: `which tmux`로 설치 확인
3. iTerm2: `it2` CLI + Python API 활성화 확인

### 작업 상태 지연
1. 팀원이 완료 표시 누락 → 종속 작업 차단
2. 수동으로 작업 상태 업데이트 또는 리더가 팀원에게 확인 요청

## 패턴 11: 웹 디자인 & 프론트엔드 개발

### 팀 구성
| 역할 | subagent_type | 모델 | 담당 |
|------|--------------|------|------|
| Designer | general-purpose | sonnet | 디자인 레퍼런스, v0.app 프롬프트, 컴포넌트 선택 |
| Frontend Dev | general-purpose | sonnet | UI 구현, 반응형, 기능 연동 |
| QA Engineer | general-purpose | haiku | 반응형 테스트, 접근성, 성능 |

### MCP 분배
- Designer: stitch (UI 목업), hyperbrowser (레퍼런스 스크래핑), exa (트렌드 검색)
- Frontend Dev: context7 (shadcn/ui 문서), memory (디자인 결정 기록)
- QA: playwright (반응형 스크린샷, E2E 테스트)

### 추천 스킬
- Designer: ui-ux-pro-max, content-creator
- Frontend Dev: frontend-patterns, react-verify, cache-components
- QA: e2e, frontend-testing, frontend-code-review

### 태스크 분해 예시
Designer (5개): 레퍼런스 수집, 디자인 시스템 생성, v0.app 프롬프트 작성, 컴포넌트 라이브러리 선택, 브랜드 가이드 적용
Frontend Dev (6개): shadcn/ui 설정, 레이아웃 구현, 섹션별 컴포넌트 구현, 상태 관리/API 연동, 반응형 세부 조정, 다크모드
QA (5개): 반응형 4해상도 테스트, 접근성 WCAG AA 검사, 성능 Lighthouse 90+, 크로스 브라우저, E2E 핵심 플로우

### 한국 시장 특화 변형
Designer 추가 태스크: DBCUT/GDWEB 한국 레퍼런스 수집, Pretendard 폰트 적용
Frontend Dev 추가 태스크: 카카오/네이버 소셜 로그인, 한글 폰트 line-height 1.7+ 적용
QA 추가 태스크: 카카오톡 공유 OG 태그 확인, 네이버 서치어드바이저 확인

## 제한사항 요약

전체 제한사항은 `~/.claude/rules/agents-v2.md`의 "제한사항" 섹션 참조.

핵심 제한:
- 세션 재개 시 팀원 복원 불가
- 중첩 팀 불가 (팀원이 하위 팀 생성 불가)
- 리더 고정 (리더십 이전 불가)
- 분할 창은 tmux/iTerm2 필요 (VS Code, Ghostty 미지원)

# MCP 자동화 레시피

## 사용법
각 레시피는 MCP 도구 조합으로 특정 작업을 자동화합니다.
ToolSearch로 필요한 MCP 도구를 로드한 후 순서대로 실행하세요.

---

## 카테고리 1: 마케팅 & 분석

### 레시피 1: 주간 마케팅 리포트
**MCP 조합**: analytics-mcp + google-ads-mcp + meta-ads + gmail
**실행 순서**:
1. analytics-mcp -> run_report (주간 트래픽, 전환율, 유입 경로)
2. google-ads-mcp -> search (Google Ads 주간 성과)
3. meta-ads -> get_insights (Meta 광고 주간 성과)
4. 데이터 종합 및 인사이트 도출
5. gmail -> send_email (이해관계자에게 보고서 발송)
**기대 결과**: 주간 마케팅 성과 종합 보고서 이메일

### 레시피 2: 경쟁사 광고 분석
**MCP 조합**: meta-ads + exa + hyperbrowser
**실행 순서**:
1. meta-ads -> list_campaigns (자사 캠페인 현황)
2. exa -> web_search_exa (경쟁사 광고 전략 검색)
3. hyperbrowser -> scrape_webpage (경쟁사 랜딩 페이지 분석)
4. 비교 분석 및 개선점 도출
**기대 결과**: 경쟁사 대비 광고 전략 분석 보고서

### 레시피 3: 실시간 캠페인 모니터링
**MCP 조합**: analytics-mcp + meta-ads + gmail
**실행 순서**:
1. analytics-mcp -> run_realtime_report (실시간 트래픽)
2. meta-ads -> get_campaign_performance (진행 중 캠페인)
3. 이상 징후 감지 시 gmail -> send_email (알림)
**기대 결과**: 캠페인 이상 시 즉시 이메일 알림

### 레시피 4: A/B 테스트 결과 분석
**MCP 조합**: analytics-mcp + meta-ads
**실행 순서**:
1. meta-ads -> setup_ab_test (테스트 설정 확인)
2. analytics-mcp -> run_report (변형별 전환 데이터)
3. meta-ads -> compare_performance (성과 비교)
4. 통계적 유의성 판단 및 권장 사항 도출
**기대 결과**: A/B 테스트 승자 및 인사이트

---

## 카테고리 2: 지식 관리

### 레시피 5: 지식 그래프 유지보수
**MCP 조합**: memory + exa + youtube-transcript
**실행 순서**:
1. memory -> read_graph (현재 지식 그래프 상태)
2. exa -> web_search_exa (최신 정보 검색)
3. youtube-transcript -> get_transcript (관련 영상 정보)
4. memory -> add_observations (기존 엔티티 업데이트)
5. memory -> create_entities (새 지식 추가)
**기대 결과**: 최신 정보로 업데이트된 지식 그래프

### 레시피 6: 기술 문서 학습
**MCP 조합**: context7 + memory
**실행 순서**:
1. context7 -> resolve-library-id (라이브러리 식별)
2. context7 -> query-docs (핵심 문서 조회)
3. memory -> create_entities (핵심 개념 저장)
4. memory -> create_relations (개념 간 관계 매핑)
**기대 결과**: 라이브러리 핵심 지식이 그래프에 저장됨

### 레시피 7: 유튜브 영상 요약 & 저장
**MCP 조합**: youtube-transcript + memory
**실행 순서**:
1. youtube-transcript -> get_transcript (스크립트 추출)
2. 핵심 내용 요약
3. memory -> create_entities (주요 개념 저장)
4. memory -> add_observations (상세 내용 추가)
**기대 결과**: 영상 핵심 내용이 지식 그래프에 누적

---

## 카테고리 3: 커뮤니케이션 & 일정

### 레시피 8: PR 배포 알림 파이프라인
**MCP 조합**: gmail + google-calendar + n8n-mcp
**실행 순서**:
1. gmail -> send_email (PR 머지 알림, 변경 내용 요약)
2. google-calendar -> create-event (배포 기록 이벤트)
3. n8n-mcp -> n8n_test_workflow (슬랙/디스코드 알림 트리거)
**기대 결과**: 모든 채널에 배포 알림 발송

### 레시피 9: 주간 미팅 자동 준비
**MCP 조합**: google-calendar + gmail + analytics-mcp
**실행 순서**:
1. google-calendar -> list-events (이번 주 미팅 확인)
2. analytics-mcp -> run_report (주간 데이터 수집)
3. 미팅 안건 및 데이터 요약 작성
4. gmail -> send_email (참석자에게 사전 자료 발송)
**기대 결과**: 미팅 전 참석자에게 데이터 기반 안건 공유

### 레시피 10: 고객 이메일 자동 분류
**MCP 조합**: gmail + n8n-mcp
**실행 순서**:
1. gmail -> search_emails (미분류 이메일 검색)
2. 내용 분석 및 카테고리 판단
3. gmail -> modify_email (라벨 적용)
4. n8n-mcp -> n8n_create_workflow (자동 분류 워크플로우 설정)
**기대 결과**: 이메일 자동 분류 워크플로우

---

## 카테고리 4: 사업 & 공공데이터

### 레시피 11: 사업자 검증 파이프라인
**MCP 조합**: data-go-nts + data-go-nps
**실행 순서**:
1. data-go-nts -> validate_business (사업자등록번호 유효성)
2. data-go-nts -> check_business_status (사업 상태 확인)
3. data-go-nps -> search_business (국민연금 가입 정보)
4. data-go-nps -> get_business_detail (상세 정보)
**기대 결과**: 거래처 사업자 종합 검증 결과

### 레시피 12: 대량 사업자 검증
**MCP 조합**: data-go-nts
**실행 순서**:
1. 사업자번호 목록 준비
2. data-go-nts -> batch_validate_businesses (대량 검증)
3. 결과 정리 (정상/폐업/휴업 분류)
**기대 결과**: 대량 거래처 유효성 검증 결과표

### 레시피 13: 재무 벤치마크 분석
**MCP 조합**: data-go-fsc + exa
**실행 순서**:
1. data-go-fsc -> search_company_financial_info (기업 검색)
2. data-go-fsc -> get_summary_financial_statement (요약 재무제표)
3. data-go-fsc -> get_balance_sheet (대차대조표)
4. data-go-fsc -> get_income_statement (손익계산서)
5. exa -> web_search_exa (업계 평균 데이터)
6. 벤치마크 비교 분석
**기대 결과**: 업계 대비 재무 건전성 분석

### 레시피 14: 입찰 기회 모니터링
**MCP 조합**: data-go-pps + gmail
**실행 순서**:
1. data-go-pps -> search_bid_announcements (입찰 공고 검색)
2. 키워드/금액 기준 필터링
3. 관련 입찰 상세 조회 (get_bid_detail)
4. gmail -> send_email (관련 입찰 알림 발송)
**기대 결과**: 조건에 맞는 입찰 공고 이메일 알림

---

## 카테고리 5: 개발 & 테스트

### 레시피 15: E2E 테스트 자동화
**MCP 조합**: playwright
**실행 순서**:
1. playwright -> browser_navigate (대상 페이지)
2. playwright -> browser_snapshot (현재 상태 캡처)
3. playwright -> browser_fill_form (폼 입력)
4. playwright -> browser_click (제출)
5. playwright -> browser_take_screenshot (결과 스크린샷)
**기대 결과**: 사용자 플로우 E2E 테스트 완료

### 레시피 16: 웹 스크래핑 & 데이터 수집
**MCP 조합**: hyperbrowser + memory
**실행 순서**:
1. hyperbrowser -> scrape_webpage (대상 페이지 스크래핑)
2. 데이터 파싱 및 정제
3. memory -> create_entities (수집 데이터 저장)
**기대 결과**: 웹 데이터가 지식 그래프에 저장됨

### 레시피 17: 라이브러리 마이그레이션 가이드
**MCP 조합**: context7 + exa + memory
**실행 순서**:
1. context7 -> resolve-library-id (현재 버전 문서)
2. context7 -> query-docs (마이그레이션 가이드)
3. exa -> web_search_exa (커뮤니티 마이그레이션 경험)
4. memory -> create_entities (마이그레이션 체크리스트 저장)
**기대 결과**: 단계별 마이그레이션 가이드

---

## 카테고리 6: 콘텐츠 제작

### 레시피 18: 유튜브 콘텐츠 기획
**MCP 조합**: youtube-transcript + exa + stitch + remotion
**실행 순서**:
1. youtube-transcript -> get_transcript (벤치마크 영상 분석)
2. exa -> web_search_exa (트렌드 리서치)
3. 기획서 작성 (제목, 구성, 스크립트)
4. stitch -> generate_screen_from_text (썸네일 목업)
5. remotion (영상 구성 참고)
**기대 결과**: 유튜브 영상 기획 패키지 (기획서 + 썸네일 목업)

### 레시피 19: SNS 콘텐츠 캘린더
**MCP 조합**: exa + google-calendar + gmail
**실행 순서**:
1. exa -> web_search_exa (트렌드/기념일 검색)
2. 월간 콘텐츠 캘린더 작성
3. google-calendar -> create-event (게시 일정 등록)
4. gmail -> send_email (팀에 캘린더 공유)
**기대 결과**: 월간 SNS 콘텐츠 캘린더

### 레시피 20: 블로그 SEO 최적화
**MCP 조합**: exa + context7 + analytics-mcp
**실행 순서**:
1. exa -> web_search_exa (키워드 경쟁 분석)
2. analytics-mcp -> run_report (기존 블로그 성과)
3. context7 (SEO 프레임워크 참조)
4. SEO 최적화 권장 사항 도출
**기대 결과**: 블로그별 SEO 개선 액션 아이템

---

## 카테고리 7: N8N 워크플로우

### 레시피 21: N8N 워크플로우 템플릿 배포
**MCP 조합**: n8n-mcp
**실행 순서**:
1. n8n-mcp -> search_templates (적합한 템플릿 검색)
2. n8n-mcp -> get_template (템플릿 상세 확인)
3. n8n-mcp -> n8n_deploy_template (템플릿 배포)
4. n8n-mcp -> n8n_test_workflow (테스트 실행)
**기대 결과**: 즉시 사용 가능한 워크플로우

### 레시피 22: N8N 워크플로우 건강 체크
**MCP 조합**: n8n-mcp
**실행 순서**:
1. n8n-mcp -> n8n_health_check (시스템 상태)
2. n8n-mcp -> n8n_list_workflows (전체 워크플로우)
3. n8n-mcp -> n8n_executions (최근 실행 이력)
4. 실패 워크플로우 식별 및 원인 분석
5. n8n-mcp -> n8n_autofix_workflow (자동 수정 시도)
**기대 결과**: 워크플로우 건강 상태 보고서 + 자동 수정

---

## 카테고리 8: 화학물질 안전

### 레시피 23: 화학물질 안전 보고서
**MCP 조합**: data-go-msds + gmail
**실행 순서**:
1. data-go-msds -> search_chemicals (물질 검색)
2. data-go-msds -> get_complete_msds (전체 MSDS)
3. data-go-msds -> get_chemical_handling_info (취급 정보)
4. data-go-msds -> get_chemical_regulatory_info (규제 정보)
5. 안전 보고서 작성
6. gmail -> send_email (관련 부서에 발송)
**기대 결과**: 화학물질 종합 안전 보고서

---

## 레시피 조합 팁

### 비용 최적화
- 고비용 MCP (hyperbrowser AI agent)는 레시피 내 1회만 사용
- 반복 검색은 exa로 먼저, 필요시만 hyperbrowser
- 결과 캐싱: memory에 저장 후 재조회 방지

### 에러 처리
- MCP 호출 실패 시 대안 도구 사용 (예: hyperbrowser -> exa)
- 타임아웃 시 작은 단위로 분할 요청
- 레이트 리밋 시 60초 대기 후 재시도

### 확장
- 레시피 조합 가능 (예: 레시피 1 + 레시피 8 = 주간 리포트 + 배포 알림)
- n8n-mcp로 레시피 자체를 워크플로우화 가능

---

## 카테고리 9: 웹 디자인 & UI

### 레시피 24: 웹 디자인 레퍼런스 수집
**MCP 조합**: hyperbrowser + exa + memory
**실행 순서**:
1. exa -> web_search_exa ("web design trends 2026 [industry]")
2. hyperbrowser -> scrape_webpage (Awwwards/Godly/DBCUT 레퍼런스 페이지)
3. 레이아웃 패턴, 색상, 타이포그래피 분석
4. memory -> create_entities (레퍼런스 인사이트 저장)
5. memory -> add_observations (스타일 패턴, 컴포넌트 구조 기록)
**기대 결과**: 프로젝트에 맞는 디자인 레퍼런스 3+개 수집 및 지식 그래프 저장

### 레시피 25: 디자인 QA 자동화
**MCP 조합**: playwright
**실행 순서**:
1. playwright -> browser_navigate (대상 페이지)
2. playwright -> browser_resize (375px 모바일) -> browser_take_screenshot
3. playwright -> browser_resize (768px 태블릿) -> browser_take_screenshot
4. playwright -> browser_resize (1024px 데스크톱) -> browser_take_screenshot
5. playwright -> browser_resize (1440px 와이드) -> browser_take_screenshot
6. 각 해상도별 레이아웃 깨짐, 오버플로우, 텍스트 가독성 확인
7. playwright -> browser_evaluate (접근성 기본 체크: alt text, labels, contrast)
**기대 결과**: 4개 해상도 스크린샷 + 반응형/접근성 QA 리포트

### 레시피 26: 컴포넌트 라이브러리 문서 조회
**MCP 조합**: context7
**실행 순서**:
1. context7 -> resolve-library-id ("shadcn/ui" 또는 "tailwindcss")
2. context7 -> query-docs ("button component usage" 등 필요한 컴포넌트)
3. 최신 API, props, 사용 예시 확인
4. 프로젝트에 맞는 구현 패턴 생성
**기대 결과**: 최신 문서 기반의 정확한 컴포넌트 구현 가이드

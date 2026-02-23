---
paths:
  - "**/*.sql"
  - "**/supabase/**"
  - "**/migrations/**"
---

# Supabase MCP (CRITICAL)

## 절대 규칙

Supabase 데이터베이스 작업은 **반드시** MCP 도구를 사용하라. CLI(`supabase db`, `psql`) 사용 금지.

## MCP 도구 매핑

| 작업 | MCP 도구 | CLI 금지 |
|------|----------|----------|
| SQL 실행 (SELECT/INSERT/UPDATE/DELETE) | `mcp__supabase__execute_sql` | `supabase db`, `psql`, Bash SQL |
| 마이그레이션 적용 | `mcp__supabase__apply_migration` | `supabase db push`, `supabase migration up` |
| 테이블 목록 조회 | `mcp__supabase__list_tables` | `\dt`, `SELECT FROM pg_tables` |
| 마이그레이션 목록 | `mcp__supabase__list_migrations` | `supabase migration list` |
| Edge Function 배포 | `mcp__supabase__deploy_edge_function` | `supabase functions deploy` |
| Edge Function 조회 | `mcp__supabase__list_edge_functions` / `get_edge_function` | `supabase functions list` |
| 로그 조회 | `mcp__supabase__get_logs` | `supabase logs` |
| DB 브랜치 관리 | `mcp__supabase__create_branch` / `list_branches` / `delete_branch` / `merge_branch` / `reset_branch` / `rebase_branch` | `supabase branches` |
| 타입 생성 | `mcp__supabase__generate_typescript_types` | `supabase gen types` |
| 문서 검색 | `mcp__supabase__search_docs` | 웹 검색 |
| 프로젝트 URL | `mcp__supabase__get_project_url` | 하드코딩 |
| 공개 키 조회 | `mcp__supabase__get_publishable_keys` | 하드코딩 |
| DB 어드바이저 | `mcp__supabase__get_advisors` | N/A |
| 확장 목록 | `mcp__supabase__list_extensions` | `\dx` |

## 사용 패턴

### 데이터 조회
```
mcp__supabase__execute_sql로 SELECT 쿼리 실행
```

### 데이터 변경 (INSERT/UPDATE/DELETE)
```
1. mcp__supabase__execute_sql로 현재 상태 확인
2. mcp__supabase__execute_sql로 변경 실행
3. mcp__supabase__execute_sql로 결과 검증
```

### 마이그레이션
```
1. mcp__supabase__list_tables로 연결 확인
2. mcp__supabase__execute_sql로 사전 상태 확인
3. mcp__supabase__apply_migration 또는 execute_sql로 적용
4. mcp__supabase__execute_sql로 적용 후 검증
```

### 스키마 확인
```
mcp__supabase__list_tables로 테이블 목록 조회
mcp__supabase__execute_sql로 컬럼/인덱스/트리거 상세 조회
```

## 프로젝트 참조

| 프로젝트 | ID | 용도 |
|----------|-----|------|
| your-project | `your-project-id` | Production |

## 예외

- MCP 서버 연결 실패 시 사용자에게 알리고 대안 확인
- 로컬 개발용 `supabase start`/`supabase stop`은 MCP 대상이 아님
- `supabase init`, `supabase link` 등 프로젝트 설정 CLI는 허용

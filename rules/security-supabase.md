---
name: security-supabase
description: Supabase 인가·키 관리 — RLS 기본 활성, 서버 전용 키 격리 (CRITICAL)
load: conditional
audience: team
sensitivity: L1
category: security
critical: true
paths:
  - "supabase/**"
  - "**/migrations/**"
  - "**/*.sql"
---

# Supabase 보안 (CRITICAL)

> 비유: RLS는 도어락이고 서버 라우트 검사는 경비원이다. **둘 중 하나는 반드시 있어야 하고,
> 어느 쪽인지를 팀이 알아야 한다.** 모르는 채로 두면 아무도 안 잠근 문이 생긴다.

Supabase는 클라이언트가 DB에 직접 연결될 수 있다. 그래서 **인가를 어디서 하는지**가
아키텍처 결정이고, 그 결정을 문서에 적지 않으면 테이블마다 다르게 새어나간다.

## 1. 인가 경로를 하나 고르고 명시한다

| 경로 | 방식 | 필수 조건 |
|---|---|---|
| **RLS 기반** | 클라이언트가 anon 키로 직접 접근, 정책이 막는다 | 모든 비즈니스 테이블에 RLS + 정책 |
| **서버 라우트 기반** | 서버만 DB에 접근, 라우트에서 인가 | anon 키가 비즈니스 테이블에 **닿지 않음**을 보장 |

- 프로젝트 `.claude/rules/` 또는 도메인 문서에 **어느 경로인지 한 줄로 적는다**
- 혼용하면 그 경계를 명시한다 (예: "인증은 RLS, 비즈니스 데이터는 서버 라우트")
- **적지 않은 상태가 가장 위험하다** — 새 테이블을 추가하는 사람이 무엇을 해야 할지 모른다

## 2. RLS 기본 활성

- 비즈니스 테이블은 `ENABLE ROW LEVEL SECURITY` 를 **기본으로 켠다**
- 끄는 경우 마이그레이션에 **왜 껐는지 주석**을 남긴다 (공개 참조 테이블 등)
- **RLS만 켜고 정책이 없으면 전면 차단**이다 — 켰으면 정책도 같은 마이그레이션에
- 새 테이블 추가 PR은 RLS·정책을 **같은 PR에** 포함한다. 나중으로 미루면 잊는다

## 3. 정책 표현식은 `(SELECT auth.uid())` 로 감싼다

```sql
-- 느림: 행마다 평가
USING (auth.uid() = user_id)

-- 빠름: initplan 으로 1회 평가
USING ((SELECT auth.uid()) = user_id)
```

정책 **표현식**에만 해당한다. 헬퍼 함수 본문 안의 `auth.uid()` 는 대상이 아니다.
RLS 판정에 쓰는 컬럼(`user_id`, `company_id` 등)에는 **인덱스를 건다**.

## 4. 키 격리 (CRITICAL)

| 키 | 노출 범위 |
|---|---|
| `anon` / publishable | 클라이언트 OK — **RLS가 유일한 방어선**이라는 뜻 |
| `service_role` / secret | **서버 전용. RLS를 통째로 우회한다** |

- `service_role` 키가 클라이언트 번들·`NEXT_PUBLIC_*` 환경변수에 들어가면 **DB 전체 유출**이다
- 서버 전용 키는 `.server.ts` 경계 또는 서버 액션 안에서만 읽는다
- 유출 시: 즉시 로테이션 → 접근 로그 확인 → 영향 범위 보고

## 5. 배포 전 확인

```sql
-- RLS 미설정 public 테이블 목록
select tablename from pg_tables
where schemaname = 'public' and rowsecurity = false;

-- RLS 는 켜졌는데 정책이 없는 테이블 (전면 차단 상태)
select t.tablename from pg_tables t
left join pg_policies p on p.tablename = t.tablename
where t.schemaname = 'public' and t.rowsecurity and p.policyname is null;
```

두 쿼리 결과가 **의도한 목록과 일치하는지** 확인한다. 빈 목록이 목표가 아니라 *설명 가능한* 목록이 목표다.

## 관련

- 심층 리뷰(인덱스·N+1·EXPLAIN)는 `database-reviewer` 에이전트
- 공급자 무관 보안 원칙은 `security.md`

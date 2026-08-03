---
name: architecture-ts
description: TypeScript/JavaScript 언어 관용구 — architecture.md 판단 기준의 언어별 각론
load: conditional
audience: team
sensitivity: L1
category: coding
critical: false
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
---

# Architecture (TypeScript) — 언어 관용구

> 비유: `architecture.md`가 "장을 어떻게 나누나"라면, 이 문서는 "이 언어에서 그걸 어떤 문장으로 쓰나"다.

**판단 기준은 여기 없다.** 왜 그렇게 나누는지는 `architecture.md`를 따르고,
이 문서는 그걸 TypeScript에서 **어떻게 실현하는가**만 담는다.

## 1. 의존성 방향을 타입으로 강제한다 (→ architecture.md §1)

도메인 폴더는 프레임워크·DB·HTTP 클라이언트를 **`import type`으로도** 가져오지 않는다.
타입만 가져와도 그 타입이 바뀌면 도메인이 따라 바뀐다 — 방향은 이미 뒤집힌 것이다.

```ts
// 나쁨 — 도메인이 바깥 타입을 안다
import type { PostgrestError } from '@supabase/supabase-js'
export function settleOrder(...): PostgrestError | Order { ... }

// 좋음 — 포트는 도메인에, 구현은 바깥에
// domain/ports.ts
export interface OrderStore {
  findById(id: OrderId): Promise<Order | null>
}
// infra/supabase-order-store.ts
export class SupabaseOrderStore implements OrderStore { ... }
```

**기계로 강제하기**: ESLint `import/no-restricted-paths`(eslint-plugin-import)로
`domain/ → infra/` 방향 import를 에러로 막는다. 규칙이 문서에만 있으면 반드시 새어나간다.

**판정법**: 도메인 테스트 파일에서 `@supabase/*`·`next/*`를 import 하고 있다면 실패다.

## 2. 경계에서만 검증하고, 안쪽은 이미 안전하다고 믿는다 (→ golden-principles #6)

바깥에서 들어온 값은 **`unknown`으로 받아** zod 통과 후에만 도메인 타입이 된다.
한 번 통과한 뒤로는 안쪽에서 다시 검사하지 않는다.

```ts
// 좋음 — 경계 한 곳에서만
const body: unknown = await req.json()
const input = CreateOrderSchema.parse(body)   // 여기부터 CreateOrderInput
```

- **`as` 캐스팅은 검증을 건너뛴 신호다.** 모양만 맞추고 싶으면 `satisfies`를 쓴다
- `as unknown as T` 이중 캐스팅은 타입 시스템을 끈 것이다. 남기려면 이유를 주석으로

## 3. `process.env`는 시작 지점 한 곳에서만 읽는다 (→ architecture.md §4)

여기저기서 `process.env.X`를 읽으면 테스트가 환경에 묶이고, 오타가 런타임까지 살아남는다.

```ts
// config/env.ts — 앱 시작 시 1회, 실패하면 여기서 죽는다
const EnvSchema = z.object({ DATABASE_URL: z.string().url() })
export const env = EnvSchema.parse(process.env)
```

같은 이유로 `new Date()`·`Math.random()`도 함수 안에서 직접 부르지 않는다.
기준 시각·난수원은 **인자로 받는다** — 호출부가 실제 값을, 테스트가 고정값을 넘긴다.

## 4. 서버 전용 코드에 경계선을 긋는다 (Next.js) (→ security.md)

`NEXT_PUBLIC_*`은 빌드 타임에 클라이언트 번들로 인라인된다.
**서버 키를 여기 두면 정적 파일로 배포된다.**

- 서버 전용 모듈 맨 위에 `import 'server-only'` — 클라이언트에서 import 하면 **빌드가 깨진다**
- 서버 키는 `.server.ts`·서버 액션·Route Handler 안에서만 읽는다
- 리뷰 체크: `grep -rn "NEXT_PUBLIC_" src/` 결과에 키·시크릿·URL 외의 것이 있는가

## 5. barrel export(`index.ts`)는 공개 경계에서만

폴더마다 `index.ts`를 만드는 습관은 **순환 의존성**과 번들 비대의 주된 원인이다.
A가 `feature/index.ts`를 import 하면, 그 안의 B·C·D를 전부 끌고 온다.

- 만든다: 패키지·모듈의 **바깥 공개 API** 한 곳
- 만들지 않는다: 내부 폴더마다. 내부는 파일을 직접 경로로 import 한다
- 순환이 의심되면 `madge --circular src/`로 확인한다

## 6. 불변성은 타입으로 못박는다 (→ golden-principles #1)

```ts
type Order = {
  readonly id: OrderId
  readonly items: readonly OrderItem[]
}
const STATUSES = ['draft', 'paid'] as const
```

- 새 객체는 spread로 만든다. `push`·`sort`·`splice`는 원본을 바꾼다 — `toSorted`·`toSpliced` 사용
- 깊은 불변이 필요할 만큼 객체가 크다면, 라이브러리를 찾기 전에 **구조를 의심한다**

## 7. 실패는 예상 가능한지로 나눈다

- **예상 가능한 실패**(재고 부족, 검증 실패)는 **반환값**으로 표현한다 — 호출부가 처리를 강제당한다
- **예외**(DB 연결 끊김, 버그)만 `throw` 한다

```ts
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E }
```

`catch (e)`의 `e`는 `unknown`이다. `e.message`를 바로 읽지 말고 좁힌 뒤 쓴다.
도메인 에러를 그대로 응답에 실으면 내부 구조가 새어나간다 — 경계에서 사용자 메시지로 변환한다.

## 라우팅

| 필요 | 위치 |
|---|---|
| 설계 판단 기준 (의존성 방향·공통화·패턴 선택) | `rules/architecture.md` |
| 크기·명명·에러 처리 체크리스트 | `rules/coding-style.md` |
| Supabase RLS·키 격리 | `rules/security-supabase.md` |
| 순환 의존성 탐지·데드 코드 제거 실행 | `/refactor-clean`, `/simplify` |

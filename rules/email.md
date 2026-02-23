---
paths:
  - "**/email/**"
  - "**/gmail/**"
  - "**/mail/**"
  - "**/newsletter/**"
---

# Email Rules

## 인사말 (CRITICAL)

이메일 작성 시 (send_email, draft_email) 본문은 **반드시** "안녕하세요"로 시작해야 한다.

### 형식

```
안녕하세요,

[본문 내용]
```

### 예시

```
안녕하세요,

요청하신 자료 보내드립니다.

감사합니다.
[서명]
```

### 적용 범위

- Gmail send_email
- Gmail draft_email
- 모든 이메일 관련 도구

### 예외

- 사용자가 명시적으로 다른 인사말을 요청한 경우
- 영문 이메일을 명시적으로 요청한 경우

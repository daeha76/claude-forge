# Security Guidelines

## Mandatory Security Checks

Before ANY commit:
- [ ] No hardcoded secrets (API keys, passwords, tokens)
- [ ] All user inputs validated
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (sanitized HTML)
- [ ] CSRF protection enabled
- [ ] Authentication/authorization verified
- [ ] Rate limiting on all endpoints
- [ ] Error messages don't leak sensitive data

## Secret Management

```typescript
// NEVER: Hardcoded secrets
const apiKey = "sk-proj-xxxxx"

// ALWAYS: Environment variables
const apiKey = process.env.OPENAI_API_KEY

if (!apiKey) {
  throw new Error('OPENAI_API_KEY not configured')
}
```

**서버 전용 키는 클라이언트 번들에 절대 넣지 않는다** (공급자 무관). `NEXT_PUBLIC_*`,
`VITE_*` 등 빌드 타임에 인라인되는 접두사에 서버 키를 두면 정적 파일로 배포된다.
서버 키는 서버 경계(`.server.ts`·서버 액션·API 라우트) 안에서만 읽는다.

> DB 인가(RLS)·키 격리 상세: Supabase 프로젝트는 `security-supabase.md` 자동 로드
> (`supabase/**`, `**/migrations/**`, `**/*.sql` 경로에서 발동)

## Security Response Protocol

If security issue found:
1. STOP immediately
2. Use **security-reviewer** agent
3. Fix CRITICAL issues before continuing
4. Rotate any exposed secrets
5. Review entire codebase for similar issues

## Remote Session Security

When using Claude Code remote sessions (e.g., `claude --remote`):

- **Never share session URLs** in public channels (Slack, Discord, GitHub issues)
- **Terminate idle sessions** — close remote sessions when not actively in use
- **Use VPN** when connecting to remote sessions over untrusted networks
- **Restrict session access** — only share session URLs with authorized team members via secure channels
- **Review session logs** — periodically check for unauthorized access or unexpected commands

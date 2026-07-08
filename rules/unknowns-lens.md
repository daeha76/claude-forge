---
name: unknowns-lens
load: always
audience: team
sensitivity: L1
category: meta
critical: false
description: The unknowns 4-quadrant lens — unfamiliar-domain work runs blind-spot-pass first, already-covered legs route to existing assets, and unknowns are discovered cheaply before building (cost asymmetry / shift-left). unknowns 4사분면 렌즈 + 낯선 도메인 진입점.
---

# Unknowns Lens (Finding Your Unknowns)
# (unknowns 렌즈 — 나의 unknowns 찾기)

> **Analogy.** The gap between the map (the prompt/context you give) and the territory (the real codebase/reality) is your "unknowns". The bigger the task, the bigger the gap, and the model *guesses* what you want at every step. Since Fable, the bottleneck isn't model capability — it's **how cheaply you surface those unknowns up front**.
>
> **비유.** 지도(내가 주는 프롬프트·컨텍스트)와 영토(실제 코드베이스·현실)의 차이가 "unknowns"다. 일이 클수록 그 차이가 커지고, 모델은 매 순간 무엇을 원하는지 *추측*해 결정한다. Fable 이후 병목은 모델 성능이 아니라 **그 unknowns를 얼마나 값싸게 미리 짚어내느냐**다.

## The 4-quadrant vocabulary (4사분면 공통 언어)

| Quadrant | Meaning | Tool |
|----------|---------|------|
| Known knowns | what you wrote in the prompt (프롬프트에 적은 것) | instruct directly |
| Known unknowns | undecided, but you know you don't know (모른다는 건 아는 미결정) | `planner` / `/plan` |
| Unknown knowns | tacit, "I know it when I see it" (너무 당연해 안 적은 암묵지) | `/explore` references · prototype |
| **Unknown unknowns** | never even considered — an unfamiliar domain (아예 고려조차 못 한 것) | **`blind-spot-pass` skill** |

## Rules (규칙)

1. **First move for unfamiliar-domain work = `blind-spot-pass`.** When work lands in a field you don't know well (color grading, legal, tax, finance, design, an unfamiliar codebase...), don't dive straight in — run `blind-spot-pass` first to surface the blind spots and teach just enough to prompt. (낯선 도메인 작업의 첫 수 = blind-spot-pass.)
2. **Discovery cost is asymmetric (shift-left).** Surfacing unknowns *before* building is cheap; discovering them *mid-build* is expensive to undo. So divergence, interviews, prototypes, references, and planning all pay off before you start. (발견 비용은 비대칭 — 구현 전 발견은 싸고 구현 중 발견은 비싸다.)
3. **Don't re-implement existing legs — route.** This lens only adds vocabulary and one entry point (`blind-spot-pass`). Everything else routes to the existing assets below. (이미 있는 leg는 재구현하지 말고 라우팅.)

## Routing (don't re-implement) (라우팅 — 재구현 금지)

| Need | Existing asset |
|------|----------------|
| Divergence / option comparison (발산·옵션 비교) | brainstorm (`/explore`, or `superpowers:brainstorming` if installed) |
| One-question-at-a-time interview, architecture-changing first (한 번에 한 질문 인터뷰) | `planner` / `/plan` |
| Implementation plan / decision capture / approval gate (구현 계획·승인 게이트) | `planner` + plan.md + HARD-GATE |
| Source-code / reference grounding (소스코드·레퍼런스) | `/explore` |
| Parallel multi-agent work (병렬 작업) | `/orchestrate` |
| Fresh-context implementation (fresh 세션 구현) | `using-superpowers` (executing plans) + worktree |

## Related

- `skills/blind-spot-pass/SKILL.md` — the unfamiliar-domain entry point this lens points to.
- `rules/interaction.md` — "state your assumptions before coding" (this lens extends it from the model's assumptions to *your own* knowledge).
- Source: Anthropic — "A field guide to Claude Fable 5: Finding your unknowns" (2026).

# Contributing to Claude Forge

Thank you for your interest in contributing to Claude Forge!

## How to Contribute

1. **Fork** the repository
2. **Create a branch** for your feature or fix
   ```bash
   git checkout -b feat/your-feature
   ```
3. **Make your changes** following the coding standards below
4. **Commit** with conventional commit messages
   ```bash
   git commit -m "feat: add new agent for X"
   ```
5. **Push** and create a **Pull Request**

## Adding New Components

### Agents (`agents/`)
- One `.md` file per agent
- Follow the existing `<Role>`, `<Constraints>`, `<Investigation_Protocol>` structure
- Specify `model` (opus/sonnet/haiku) in the frontmatter

### Commands (`commands/`)
- Single `.md` file for simple commands
- Directory with `SKILL.md` + `references/` for complex commands
- Include `description`, `argument-hint`, and `allowed-tools` in frontmatter

### Skills (`skills/`)
- Each skill is a directory with `SKILL.md` as entry point
- Include `hooks/` subdirectory if needed
- Add `references/` for supplementary documentation

### Hooks (`hooks/`)
- Shell scripts (`.sh`) that execute on Claude Code events
- Keep hooks lightweight (< 5s execution time)
- Add timeout in `settings.json` for slow hooks

### Rules (`rules/`)
- Markdown files loaded automatically every session
- Keep rules concise and actionable
- Use `(CRITICAL)` suffix for mandatory rules

## Coding Standards

- Follow `rules/coding-style.md` conventions
- Immutability: never mutate objects
- Small files (< 800 lines), small functions (< 50 lines)
- Validate inputs at system boundaries (zod schemas)
- No hardcoded secrets

## Commit Messages

Format: `<type>: <description>`

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`

## Questions?

Open an issue on [GitHub](https://github.com/sangrokjung/claude-forge/issues).

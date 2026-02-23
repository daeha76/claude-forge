---
name: react-tools
description: React development toolkit - lint/format (fix), verification (react-verify), Flow type checking, feature flags, and test runner. Use when working on React core codebase.
---

# React Development Tools

Unified toolkit for React core development. Combines fix, verify, flow, flags, and test commands.

## Commands

| Command | Purpose |
|---------|---------|
| `/react-tools fix` | Fix lint + formatting |
| `/react-tools verify [pattern]` | Full verification (format + lint + flow + test) |
| `/react-tools flow [renderer]` | Flow type checking |
| `/react-tools flags [options]` | Feature flag inspection |
| `/react-tools test [channel] [pattern]` | Run tests |

---

## fix - Lint & Formatting

1. Run `yarn prettier` to fix formatting
2. Run `yarn linc` to check for remaining lint issues
3. Report any remaining manual fixes needed

**Common Mistakes:**
- `yarn prettier` only formats changed files
- `yarn linc` errors will fail CI - fix before committing

---

## verify - Full Verification

Arguments: `$ARGUMENTS` - Test pattern for the test step

Run these first in sequence:
1. Run `yarn prettier` - format code (stop if fails)
2. Run `yarn linc` - lint changed files (stop if fails)

Then run these with subagents in parallel:
1. Flow type check (stop if fails)
2. Test changes in source (stop if fails)
3. Test changes in www (stop if fails)

If all pass, show success summary. On failure, stop immediately and report the issue with suggested fixes.

---

## flow - Flow Type Checking

Arguments: `$ARGUMENTS` - Renderer to check (default: `dom-node`)

| Renderer | When to Use |
|----------|-------------|
| `dom-node` | Default, recommended for most changes |
| `dom-browser` | Browser-specific DOM code |
| `native` | React Native |
| `fabric` | React Native Fabric |

1. Run `yarn flow $ARGUMENTS` (use `dom-node` if no argument)
2. Report type errors with file locations
3. For comprehensive checking (slow), use `yarn flow-ci`

**Common Mistakes:**
- Always specify a renderer or use default `dom-node`
- Check if `$FlowFixMe` comments are masking real issues
- Ensure types are imported from the correct package

---

## flags - Feature Flags

Arguments: `$ARGUMENTS` - Optional flags

| Option | Purpose |
|--------|---------|
| (none) | Show all flags across all channels |
| `--diff <ch1> <ch2>` | Compare flags between channels |
| `--cleanup` | Show flags grouped by cleanup status |
| `--csv` | Output in CSV format |

### Channels
- `www`, `www-modern` - Meta internal
- `canary`, `next`, `experimental` - OSS channels
- `rn`, `rn-fb`, `rn-next` - React Native

### Legend
- ✅ enabled, ❌ disabled, 🧪 `__VARIANT__`, 📊 profiling-only

1. Run `yarn flags $ARGUMENTS`
2. Explain the output to the user
3. For `--diff`, highlight meaningful differences

**Common Mistakes:**
- `__VARIANT__` flags are tested both ways in www; check both variants
- Use `--diff` to see exact differences between channels

---

## test - Run Tests

Arguments: `$ARGUMENTS` - Channel, flags, and test pattern

### Usage Examples
- `/react-tools test ReactFiberHooks` - Source channel (default)
- `/react-tools test experimental ReactFiberHooks` - Experimental channel
- `/react-tools test www ReactFiberHooks` - www-modern channel
- `/react-tools test www variant false ReactFiberHooks` - __VARIANT__=false
- `/react-tools test stable ReactFiberHooks` - Stable channel
- `/react-tools test classic ReactFiberHooks` - www-classic channel
- `/react-tools test watch ReactFiberHooks` - Watch mode (TDD)

### Release Channels
| Channel | Command | Description |
|---------|---------|-------------|
| (default) | `yarn test --silent --no-watchman <pattern>` | Source/canary channel |
| experimental | `yarn test -r=experimental --silent --no-watchman <pattern>` | Experimental flags enabled |
| stable | `yarn test-stable --silent --no-watchman <pattern>` | What ships to npm |
| classic | `yarn test-classic --silent --no-watchman <pattern>` | Legacy www-classic |
| www | `yarn test-www --silent --no-watchman <pattern>` | www-modern (__VARIANT__=true) |
| www variant false | `yarn test-www --variant=false --silent --no-watchman <pattern>` | www (__VARIANT__=false) |

### Hard Rules
1. **Use `--silent`** to limit output to failures only
2. **Use `--no-watchman`** to avoid sandboxing failures

**Common Mistakes:**
- Running without a pattern runs ALL tests (very slow) - always specify a pattern
- Test both `www` AND `www variant false` for `__VARIANT__` flags
- If test skipped unexpectedly, check for `@gate` pragma; see `feature-flags` skill

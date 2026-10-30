---
name: diagnosing-bugs
description: "Debug hard-to-reproduce bugs, performance regressions, and cascading failures through a reproducible feedback loop, falsifiable hypotheses, a minimal fix, and regression coverage."
---

# Diagnosing Bugs

Follow the target project's interaction and artifact languages from [language policy](../_agents/language-policy.md); pass both to delegates.

## When to use

- The user reports broken behavior, errors, failures, or slowdowns.
- Fixing one area breaks another.
- A bug is intermittent or difficult to reproduce.

## Core disciplines

1. **Build the feedback loop first.** Do not advance without a loop that can reproduce failure.
2. **Make hypotheses falsifiable.** State what changing Y would do if X were the cause.
3. **Change one variable at a time**, in both instrumentation and fixes.
4. **Add regression coverage before fixing** so the bug stays fixed.

## Six phases

### Phase 1: Build the feedback loop

Build a tight, deterministic loop that can reproduce the user's exact symptom and go red.

Prefer, in order:
1. A failing test at an appropriate seam.
2. A curl/HTTP script.
3. A CLI call with fixture input.
4. A headless browser script using Playwright/Puppeteer.
5. Replay of captured requests/events.
6. A minimal harness: one service and mocked dependencies.
7. Property tests or fuzzing to expose failure patterns.
8. An automated git-bisect harness.
9. A differential loop comparing old and new versions.
10. A structured human-in-the-loop script.

Tighten speed by caching setup and reducing scope; assert the specific symptom rather than merely avoiding a crash; fix time/seeds and isolate the environment.

Completion criteria:
- Reproduces the **exact reported symptom**.
- Produces consistent results.
- Runs in seconds rather than minutes.
- Can run automatically.

Without a failure-capable loop, **stop** rather than jumping to hypotheses.

### Phase 2: Reproduce and minimize

Run the loop and observe failure. Confirm that it is the reported bug, not a nearby one, and that repeated runs reproduce it. For intermittent bugs, raise the reproduction rate enough to debug.

Remove inputs, callers, configuration, data, and steps one at a time, rerunning after every removal. Each remaining element must be necessary: removing it makes the loop green.

### Phase 3: Rank hypotheses

Generate **3–5 ranked hypotheses** before testing them. Each must predict a falsifiable result: if X causes the bug, changing Y should remove it or changing Z should worsen it.

Example:

```
1. 如果 CSV 转义逻辑没处理引号，那么输入包含 " 的数据会失败
2. 如果数据库查询超时，那么减少数据量会让它成功
3. 如果缓存键冲突，那么清除缓存会暂时修复
```

Show the ranked list to the user; their domain knowledge may eliminate candidates immediately.

### Phase 4: Instrument

Each probe tests a specific Phase 3 prediction. Change **one variable at a time**.

Prefer a debugger/REPL, then focused boundary logging. Avoid logging everything and grepping it afterward. Tag debug logs `[DEBUG-xxxx]` for cleanup.

For performance bugs, measure a baseline before bisecting or fixing.

### Phase 5: Fix with regression coverage

At an appropriate seam, add regression coverage **before the fix**. Reuse an existing failing case or extend the matching test file and fixtures with the minimized reproduction. Parameterize related inputs instead of creating a file per hypothesis. Put exploratory harnesses, replays, and probes in system temporary storage; retain useful regression coverage in the maintained suite.

The seam must reproduce the **actual failure pattern**:
1. Add the minimized reproduction to existing tests, or reuse an accurate existing case.
2. Observe failure.
3. Apply the fix.
4. Observe success.
5. Rerun the original, unminimized Phase 1 loop.

If no suitable seam exists, record that architectural limitation as a finding.

### Phase 6: Clean up

Before finishing, verify:
- The original symptom no longer occurs in the Phase 1 loop.
- Regression tests pass.
- All `[DEBUG-...]` logs are removed.
- Temporary prototypes are removed or identified.
- The verified hypothesis is documented for the commit/PR message.

## Outputs

- A reproducible loop retained as regression coverage.
- The fix.
- The verified cause documented for the commit message.

## Boundaries

| Appropriate | Inappropriate |
|-------------|---------------|
| Reproducible bugs | Production incidents with no usable reproduction |
| Existing test infrastructure | Untested legacy code before establishing tests |
| Performance regressions with profiling evidence | A misunderstanding of requirements |

## Related stages

- Prevent recurrence through `/implement` and its TDD coverage.
- If an external endpoint changes, update the affected `/to-api-contract` fragment.

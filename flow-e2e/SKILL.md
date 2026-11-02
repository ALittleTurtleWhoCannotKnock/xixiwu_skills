---
name: flow-e2e
description: "Manually create maintained browser E2E coverage for a feature. Discover and reuse the project framework, fixtures, and CI conventions; require stable selectors, deterministic waits, and local headless success."
---

# Flow E2E

Follow the target project's interaction and artifact languages from [language policy](../_agents/language-policy.md); pass both to delegates.

Produce maintained browser E2E tests suitable for CI, not disposable verification scripts. **Manually triggered.**

## When to use

- The user requests browser E2E tests for a feature, page, or flow.
- A completed feature needs persistent browser regression coverage.

## Core disciplines

1. **Discover the stack.** Read the existing framework, directories, and commands. If none exists, recommend a default and wait for confirmation.
2. **Follow project conventions** for fixtures, naming, structure, and style.
3. **Require stable selectors** to prevent flaky tests.
4. **Wait for conditions**, using framework auto-waiting or explicit waits, never fixed sleeps.
5. **Run before delivery.** Tests that have not passed locally are unfinished.

## Workflow

### Step 1: Discover the E2E setup

The main session may use scout for read-only discovery. Inspect:
- `package.json` devDependencies/scripts for `@playwright/test`, `cypress`, `webdriverio`, or no framework.
- Existing directories/examples (`e2e/`, `tests/e2e/`, `*.spec.ts`), naming, fixtures/setup, baseURL, and page-object conventions.
- `.github/workflows/` or equivalent CI configuration: triggers, dev-server startup, and commands.

Scout returns file discoveries; the main session determines the setup and status.

If there is no E2E setup, explain that, recommend Playwright Test with `e2e/` and a separate `playwright.config`, and **wait for confirmation before setting it up**. Do not install dependencies or select a framework unilaterally. Present the discovered setup for confirmation before continuing.

### Step 2: Confirm scope

Do not assume full coverage. Ask which user path to test (golden path first), which essential edge cases are required (empty/error/permission/boundary states), and which pages/routes are involved.

### Step 3: Write tests

Follow `docs/agents/execution-mode.md`: normally delegate to an implementer; in inline mode the main session writes them.

Reuse the discovered framework, directories, fixtures, and style. Extend existing tests for the same page/path and parameterize repeated data dimensions. Create a file only for an independent path or existing split convention, explaining why. Do not create a file per ticket/assertion or remove existing coverage merely to reduce file count.

**Selector priority:**
1. `data-testid` attributes.
2. Semantic role/label locators (`getByRole`, `getByLabel`).
3. Never fragile CSS classes, deep XPath, or structure-coupled `nth-child` selectors.

If stable test IDs are missing, list the application locations needing them as accompanying changes; disclose changes to the tested code.

**Waiting:** Use framework auto-waiting or explicit conditions (`waitFor`, visibility/interactivity assertions). Do not use fixed `sleep(ms)` or hard-coded timeout durations.

**Debugging versus delivery:**

Headless is the delivery/CI standard. During selector development, a real browser may help inspect DOM rather than guessing:

| Context | Mode | Tools |
|---------|------|-------|
| Local selector development/debugging | Headed is allowed | `playwright test --headed`, `--debug`, `--ui`, screenshots, traces, or video |
| Delivered tests / CI | Headless required | Framework defaults; headed mode must not become a prerequisite |

Tests must pass headlessly. A selector that works only headed or remains flaky headlessly needs more work.

### Step 4: Run locally

The same executor starts the dev server using the discovered project command and runs the tests **headlessly**. Finish only after they pass. Fix test code until it passes; if the application itself is buggy, stop and report instead of changing business logic without authorization. Run repeatedly to establish deterministic behavior.

Unrun tests are unfinished; do not deliver them as verified.

### Step 5: Report

Summarize changed test files and added test IDs, actual commands/results/stability, and CI integration guidance: the relevant workflow, server startup, and command. Follow existing CI steps; if CI lacks E2E integration, recommend changes without editing configuration unilaterally.

## Outputs

- Maintained E2E tests following project conventions, stable selectors, and deterministic waits.
- Actual local verification results.
- CI integration guidance, not an unsolicited CI change.

## Boundaries

| Appropriate | Inappropriate |
|-------------|---------------|
| Persistent feature regression coverage with an existing or agreed new setup | Disposable agent self-checks, which belong to implementation-time verification |
| End-to-end frontend user paths | Pure logic/API tests that need no browser |
| Adapting to the project's framework | Forcing one framework across projects |

Application bugs belong to a separately authorized repair flow. Confirm new framework dependencies or CI changes before applying them.

## Related stages

- Manually triggered for maintained browser coverage. `/flow-do` may run required existing E2E tests or temporary browser checks, without creating a suite for every ticket.
- Scout may discover test/CI files in Step 1.
- An implementer may write tests in Step 3 under execution-mode and its minimal-change/validation rules.
- Repair discovered product bugs through `/flow-debug` or `/flow-do` when authorized.

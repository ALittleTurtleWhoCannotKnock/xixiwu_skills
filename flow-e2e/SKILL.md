---
name: flow-e2e
description: "Start or reuse a local app and verify the just-completed feature through real browser actions. Use after /flow-do for a browser test pass; create maintained E2E tests only when explicitly requested."
---

# Flow E2E

Follow the target project's interaction and artifact languages from [language policy](../_agents/language-policy.md); pass both to delegates.

Default to **running a local browser verification pass**. For example, `/flow-e2e 你可以先本地启动测试一轮` asks you to start the app, exercise the completed feature, and report observed results. It does not request permanent test files or a new E2E framework. Manually triggered; `/flow-do` does not automatically invoke this skill after every Todo.

If the user explicitly asks to add maintained regression tests or set up an E2E suite, also read [maintained tests](references/maintained-tests.md). A request to run existing tests does not by itself request new ones.

## Workflow

### Step 1: Recover the feature and test scope

Read the recent `/flow-do` handoff, completed Todo, and relevant current Plan/Spec. Reuse their routes, criteria, agreed checks, and authorization. For “test locally once” after Do, default to the just-completed feature's main user path and relevant failure/boundary states, not the entire product.

Briefly state the selected paths and assumptions, then proceed. Do not ask the user to repeat known scope or approve routine startup and browser actions already requested. Ask only for missing information that prevents a meaningful or permitted check, such as an unresolved target, required login, or ambiguous product behavior. Preserve explicitly required checks; incomplete engineering checks cannot be replaced by a browser smoke pass.

Follow `docs/agents/execution-mode.md` for execution. The executor must have the needed browser capability and own its browser/server handles; do not delegate browser work to an agent without that capability. Keep scope decisions and user questions in the main session.

### Step 2: Discover and start the local app

- Read repository instructions, startup documentation, scripts, environment requirements, and the frontend/backend routes involved. Use the declared project setup and commands.
- Check the effective backend/data destinations and project restrictions before startup or data-changing actions. A localhost frontend can still use remote data. Use permitted test accounts/data; do not run migrations, destructive seeds, or external sends merely to unblock a browser check.
- Reuse a running service only after identifying it as this project's intended environment. Otherwise start the needed services, record the local URL and owned process handles, and wait for actual readiness. Do not kill an unrelated process to free a port.
- Discover available browser tools or an existing project browser-test runner. Missing E2E configuration is not a reason to scaffold a suite or block an otherwise available browser check. Do not introduce frameworks, dependency/lockfile changes, or CI configuration for the default pass.

If startup, credentials, a permitted data target, or browser capability is unavailable, report the exact blocker and affected unrun paths. Perform independent checks that remain possible, without presenting HTTP/build/unit checks as a completed browser test.

### Step 3: Exercise the user paths in a real browser

Open the verified URL and inspect the current page/DOM before acting. Use supported browser-tool instructions or the project's existing runner. Both headed and headless execution are valid for this pass; report the actual method. Existing relevant E2E tests may supply coverage when their executed paths and assertions match the requested checks.

- Perform the selected user actions: navigation, input, submission, and the feature's relevant results. Verify observable outcomes, such as saved state, validation feedback, a downloaded file, or persistence after refresh where required. A page opening or screenshot alone is not a feature pass.
- Use stable role/label locators or existing test IDs based on the actual page. Use condition-based waits for readiness, visibility, requests, or results; avoid fixed sleeps. Default verification does not require adding test IDs or changing application code.
- Reuse fixtures and disposable permitted data. Inspect relevant console/network failures, especially on failed paths. Capture useful screenshots, traces, or downloaded artifacts when available, keeping evidence outside maintained test directories unless requested.
- Record each checked path's actions, expected result, observed result, and pass/fail. Mark blocked or unrun paths explicitly; do not silently omit them from the result.

Do not mock away the changed behavior and call it end-to-end success. If an external dependency must be simulated, identify the simulated boundary and the real integration checks still unverified.

### Step 4: Handle failures and finish the session

For a failure, retain a reproducible path, expected/actual behavior, and relevant evidence. Retry only when a concrete readiness, selector, or environment correction justifies it; stop after the same unresolved failure repeats rather than looping until green.

Honor existing repair authorization. A verification-only request produces findings; product fixes proceed through `/flow-debug` or `/flow-do` when authorized. After an authorized fix, rerun the failing path and affected checks. Do not weaken criteria or change business logic solely to make the test pass.

Clean up only disposable data and sessions/processes created for this pass when no longer needed. Preserve user-owned services and sessions. If a service is left running for continued review, report its URL and how to stop the owned process.

### Step 5: Report observed results

Report in the conversation unless a saved report is requested or required by the project:

- Tested feature/version or working-tree scope, local URL, startup commands, and actual browser method/mode.
- Paths exercised, expected/observed results, and passed/failed/blocked/unrun counts. Link real evidence where available.
- Reproducible failures, environmental limits, simulated boundaries, and remaining checks.
- Files/data changed, cleanup performed, and services still running, as applicable. Do not generate test files, screenshots, or a report file just to satisfy a fixed artifact count.

A successful browser pass is engineering evidence. Human functional acceptance remains with the user at Plan/Spec under the [shared contract](../_agents/workflow-contract.md#功能验收与票级关闭); do not infer `Acceptance: accepted`, close the acceptance issue, or commit/push from test success alone.

## Outputs and related stages

- **Default:** Actual local browser verification and an evidence-based result, without mandatory new test files.
- **Explicit maintained-test request:** Reused/extended regression coverage plus actual execution results under the conditional guide.
- `/flow-do` performs the Todo's required engineering checks; this skill provides a focused browser pass when requested. Neither replaces required verification with unrun claims.
- Pure logic/API checks without a browser belong to the project's normal validation or `/flow-do`; report them separately from browser coverage.

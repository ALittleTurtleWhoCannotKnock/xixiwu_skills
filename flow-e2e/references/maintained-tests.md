# Maintained browser regression tests

Read this only when the user asks to add/extend lasting E2E coverage or set up a suite. Keep the entrypoint's environment, authorization, failure-reporting, and acceptance boundaries.

## Discover and agree on setup

Inspect the project's dependencies/scripts, test directories, configuration, fixtures, base URL, dev-server setup, and CI conventions. Reuse the existing framework and style. Present only unresolved setup choices; reuse explicit choices and permissions already given.

If no framework exists, propose a minimal project-appropriate setup and obtain approval before introducing dependencies or configuration, unless the user already explicitly authorized that setup. Creating CI jobs is separate from writing tests; edit CI only within existing authorization.

## Write useful regression coverage

- Start with the agreed user path and necessary failure/boundary cases; do not infer full-product coverage.
- Extend existing tests for the same path, reuse fixtures, and parameterize related inputs. A new file needs an independent path or an established split convention, not a Todo/assertion count. Preserve existing useful coverage.
- Use selectors grounded in the actual DOM: stable roles/labels or existing test IDs, following project conventions. Add missing test IDs only where necessary and disclose the application changes. Avoid fragile structure-dependent selectors.
- Wait for observable conditions using the framework's supported waiting/assertion behavior, not fixed sleeps.
- Keep headed inspection/debugging available. Tests intended for CI must also pass locally in headless mode; headed success alone does not satisfy that requirement.

## Run and report

Use the discovered startup and test commands. Run the actual tests and report commands, results, and any unavailable checks. Repeat execution when needed to investigate flaky behavior, not as an unbounded attempt to obtain a green result. Unrun or failing required tests remain unfinished.

Distinguish test defects from product defects, repairing only within the user's authorization. After a repair, rerun affected tests. Do not hide a product failure by weakening assertions.

Report maintained test files, accompanying test IDs or configuration changes, actual local results, and relevant CI startup/command guidance. Do not claim CI success without running it or add CI changes merely because a suite was requested.

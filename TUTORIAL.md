# Dev Flow Skills User Guide

**English** | [简体中文](./TUTORIAL.zh-CN.md)

A development workflow you control: initialize → clarify requirements → define the Spec → plan → split Todos → implement and verify, with supporting skills for debugging, cleanup, API contracts, and session export. Works across Pi, Codex, and Claude Code.

> This guide is a narrative walkthrough. Each skill's **authoritative definition** is its `SKILL.md`; execution sub-agents follow the **execution logic** in `_agents/*.prompt.md`.

---

## Installation and updates

Obtain the complete repository in a separate directory and review its source. Preview with `./install.sh all --dry-run`, then run `./install.sh all` after review. Replace `all` with `pi`, `claude-code`, or `codex` to select one CLI. For Git updates, review incoming changes before `git pull --ff-only`, then preview and rerun the installer. See the [README](./README.md#installation-and-updates) for installation paths, backups, and legacy migration.

Skills and shared prompts link to the same checkout. Existing model selections and other agent frontmatter are preserved. After installation, run `/flow-init` in your own project to choose its base model and other settings; installation does not replace that step.

## Workflow at a glance

```
/flow-init       Initialize the workflow, or fill missing settings
    ↓
/flow-clarify    Align requirements
    ↓
/flow-spec       Define the product Spec
    ↓
/flow-plan       Plan the implementation, with human review
    ↓
/flow-todo       Split work into Todos
    ↓
/flow-do         Implement and verify
    └─ Backend endpoints involved → /flow-api (extract API contracts)
```

Supporting skills: `/flow-amend` for changes to an implemented Spec, `/flow-debug` for debugging, `/flow-simplify` for cleanup before committing, `/flow-export` for session export, and `/flow-api` for API contracts.

### Stage reference

| Your situation | Command | Output |
|----------------|---------|--------|
| Let a Bot advance the whole feature | `/flow-run` | Engineering delivery after Spec confirmation, with resumable progress |
| Set up a new repository or fill missing languages | `/flow-init` | Four settings: tracker, commit strategy, execution mode/model, and languages |
| Requirements are still informal or might be misunderstood | `/flow-clarify` | Aligned requirements and CONTEXT.md |
| Requirements are aligned and need a reviewable document | `/flow-spec` | Spec with seam analysis and Mermaid diagrams, saved to the tracker |
| Spec is confirmed and needs an implementation approach | `/flow-plan` | Technical decisions, packages, change anchors, and validation strategy, with user approval |
| Plan is approved and needs execution work | `/flow-todo` | Todos and dependencies; a small single Todo may explicitly omit a Plan |
| Todos are confirmed and coding can start | `/flow-do` | Working code and tests |
| Do is complete and you want a local test pass | `/flow-e2e` | Real browser actions and pass/fail/untested results; no new test files by default |
| An implemented Spec changes | `/flow-amend` | spec-v(N+1), updated INDEX, and follow-on Todos |
| Check current progress | `/flow-status` | Read-only stage, Status, blocker, and next-action snapshot |
| A backend Todo involves endpoints | `/flow-api`, triggered by /flow-do | API contract fragments |
| Prepare a commit | `/flow-simplify`, triggered by /flow-do | Cleaned-up code and a human checkpoint |
| Investigate a difficult bug | `/flow-debug` | A fix and regression coverage |
| Preserve a session | `/flow-export` | session.md and session.jsonl |

---

## Stage 0: Initialize — `/flow-init`

**Run once for a new repository; missing settings can be filled separately.** The agent discovers the tracker, confirms commit/execution/language preferences, and saves them under `docs/agents/`.

### Four settings

| Setting | File | Choice | How it is selected |
|---------|------|--------|--------------------|
| Tracker | `issue-tracker.md` | GitHub, GitLab, or local `.scratch` | Discover git remote, gh/glab CLI, and existing .scratch |
| Commit strategy | `commit-strategy.md` | per-ticket or squash | Inspect git log and confirm with you |
| Execution mode and base model | `execution-mode.md` | subagent or inline; model used for dispatch | Ask for mode; in subagent mode, list actual models and let you choose an ID or inherit |
| Interaction and artifact languages | `language.md` | Two independent choices; they may match or differ | Confirm proposed languages, reuse explicit choices, and never save guesses |

### Run

```
/flow-init
```

The agent reports its findings, for example:

```
Discovery:
- git remote: none
- .scratch/: absent
- git log: mostly large commits (suggests squash)

Proposed setup:
- Tracker: local, because there is no remote
- Commit strategy: squash? Please confirm.
- Execution: delegate by default? (A: sub-agent / B: inline main session)
- Languages: choose interaction and artifact languages separately.
  For example, Chinese conversation and English documents; please confirm.
```

If you choose delegation, the agent lists models actually available in the current tool, or lets you explicitly inherit the main session's model with `inherit`. It saves the choice in the base-model field (`基础模型`) of `execution-mode.md`. Templates contain no preselected model. Pi reads that project configuration when generating agents; other tools apply the choice in their supported dispatch format. A model that has not actually been called is reported as unverified at runtime.

Languages are confirmed and saved before generating subsequent documents, using the fixed keys `interaction_language` and `artifact_language`. With Chinese interaction and English artifacts, questions, review summaries, and `/flow-status` explanations use Chinese, while Spec/Plan/Todo prose uses English. Protocol fields and state values are not translated. A temporary override affects only the requested channel for that task. Original session exports are never translated because an artifact-language preference changed.

### Output

```
docs/agents/
├── issue-tracker.md    # Tracker: one source of truth
├── commit-strategy.md  # Commit strategy and /flow-simplify timing
├── execution-mode.md   # Execution mode and confirmed base model
└── language.md         # Confirmed interaction and artifact languages
.scratch/README.md      # Local tracker only
AGENTS.md               # Root pointers for developers and agents
```

**Preferences are defaults with task-specific overrides.** A small Todo can run inline even when the project defaults to delegation. Asking for a Chinese Plan this time does not change the project's English artifact default. Filling missing languages in an older project preserves models and other settings and does not translate existing documents.

---

## Stage 1: Clarify requirements — `/flow-clarify`

### When to enter

- You have a feature or change to make.
- Requirements exist only in your head or chat history.
- You want to avoid misunderstandings.

### Run

```
/flow-clarify
```

The agent asks focused follow-up questions, exploring unresolved branches after each answer until the requirements are clear.

**Example conversation:**

```
You: I want to add comments to the blog.

Agent: A few questions:
1. Must commenters sign in?
2. Are nested replies supported?
3. Do comments need sensitive-word filtering?
4. How should comments be sorted?

You: Require sign-in, support nesting and filtering, newest first.

Agent: Understood. What is the nesting-depth limit?
```

### Output

- An unambiguous requirements description.
- An updated root `CONTEXT.md` domain glossary, created if absent.

**This is interactive and stays in the main session.** It needs a conversation with you rather than an isolated sub-agent.

---

## Stage 2: Define the Spec — `/flow-spec`

### When to enter

- Requirements from Stage 1 are aligned.
- You need a reviewable, traceable product document.

### Run

```
/flow-spec
```

First choose whether this invocation should also generate an HTML Spec reading view. Reuse an explicit choice already in the request. Without an answer, do not save a guessed preference or generate HTML. The choice is for this invocation only, never a project/global default.

The agent reads `docs/agents/issue-tracker.md`, then:

1. **Analyzes test seams:** prefer the highest existing boundary and confirm it with you.
2. Writes a **four-section Spec:** problem, non-goals, approach (functional flow, seams, and key decisions), and written module impact. A sequence diagram explains interactions between participants.
3. Saves it to the declared tracker:
   - Local: `.scratch/<feature-slug>/spec.md`.
   - GitHub/GitLab: a Spec issue.

If an Epic is specified, it owns the Spec; otherwise the Spec is the feature entry. Local mode creates `INDEX.md` and `.scratch/README.md` navigation from this stage onward. GitHub uses native parent/sub-issue relationships and type labels.

When HTML is requested, generate it from the saved Spec. Local output is usually `spec.html` beside the source, or `spec-v2.html` for a versioned Spec. Preserve the four sections, source, version, generation time, and chosen language, with collapsible technical details. Without a request, do not load the HTML template or create a reading file or entry point.

For a remote tracker, the complete Spec stays in its issue; local HTML is a reading snapshot. Add an online link only when an authorized publishing channel exists and its address is verified. Otherwise deliver the local file without presenting a machine path as a shared URL or automatically committing, enabling Pages, or deploying. If an old view is not refreshed after a Spec change, mark it stale or remove its current-reading link while retaining the historical file.

**This is interactive and stays in the main session.**

### Output

- A Spec in the tracker, including a functional flowchart, agreed test seams, and a call sequence diagram.
- An additional HTML reading view only when explicitly requested, with actual verification results. Opening the page does not approve the Spec.

---

## Stage 2.5: Plan the implementation — `/flow-plan`

After Spec confirmation, settle technical choices, implementation paths, and risks in Plans before splitting execution Todos.

```
/flow-plan
```

Reuse existing code context and decide whether the Spec needs one or several independent Plans. User-specified counts/groupings take precedence. Each Plan must be implementable and verifiable from the existing baseline, then split into simple engineering Todos. Frontend/backend/testing phases and P1/P2 packages do not establish independent Plans. Explain and ask about an actual count/independence conflict. This example uses the compatible singleton path `.scratch/<feature>/plan.md`; new peer scopes use `plans/<scope>.md`, with one remote Plan issue per scope. Each body contains:

- Technical decisions: options, choice, and rationale.
- P1..Pn packages: deliverables, implementation paths, reuse, and risks.
- Change anchors: distinguish existing attachment points from target-state symbols and identify which stage creates each target.
- Overall validation strategy and approach-approval status.

Verify existing attachment points before starting. Verify target-state symbols after their owning Todo/prerequisite creates them. Review and approve the approach before ticketing, reusing valid session authorization. Maintain each Plan in place; do not copy method anchors into Todos.

Each Plan records its applicable version and owned scope through Spec:/Scope:. The Spec lists all actual references under Plans:, with legacy singleton Plan: supported. Each Plan lists only its own Todos and maintains separate technical approval and scoped acceptance. Comments are not the current blueprint, and native open/closed state is not approval. Reuse the same body per scope without a second local master for a remote Plan.

A Plan's `Parent:` points to its Spec. Locally, update the same INDEX; on GitHub, establish and verify native sub-issues. Use an explicitly configured Project and its View → Show hierarchy option when available. Without a Project, ordinary Issues still work.

Track human functional acceptance separately as `Acceptance: pending / accepted / changes-requested`. Approach approval is not functional acceptance. Engineering Todos may close while upper acceptance remains pending. Record accepted only after the user's actual functional acceptance. When a Plan is intentionally omitted, the Spec owns this state instead; do not duplicate it.

---

## Stage 3: Split Todos — `/flow-todo`

### When to enter

- Stage 2.5 is complete and the Plan is approved, or a confirmed small Todo explicitly omits a Plan.
- The work exceeds a single session's capacity.

### Run

```
/flow-todo
```

The agent:

1. **Identifies useful prefactoring:** make the change easy, then make the easy change.
2. Splits each Plan into **simple, bounded, verifiable engineering Todos** with known inputs, results, boundaries, and completion checks. A Todo need not span every layer; related small Todos may share execution and tests.
3. Records direct ownership in `Parent:`, the Spec version and actual Plan/package in `Spec:` / `Plan:`, and dependencies in `Blocked by:`.
4. Confirms granularity and dependencies, then saves to the tracker:
   - Local: `.scratch/<feature-slug>/issues/<NN>-<slug>.md`. Number feature-wide from 01, continue after the highest existing number, and put blockers first. Never merge all records into one file.
   - GitHub/GitLab: one issue per Todo.

Remote Todos use `Spec: <Spec version reference>` and `Plan: <independent Plan issue> / P<N>`, then backlink from their owning Plan. Locally, `plans/<scope>.md#P<N>` identifies the actual Plan; legacy `plan.md#P<N>` remains valid.

New titles use `[Todo]`, with the default GitHub type label `todo`. Local titles, Plan lists, INDEX, and `/flow-status` groups use the same naming. Discover and reuse legacy `[Ticket]`/`ticket` aliases too; a naming difference is not a reason to recreate work.

The parent is the Plan, not a blocker or historical Todo being continued. Add actual local links to INDEX; on GitHub, synchronize native sub-issues, type labels, and the configured Project. Report unsupported capabilities, missing permissions, and parent conflicts rather than creating replacement issues to bypass them.

**This is interactive and stays in the main session.**

### Output

```
.scratch/blog-comments/
├── INDEX.md                 # Current Spec, Plan, and Todo hierarchy
├── spec.md
├── plan.md
└── issues/
    ├── 01-prefactor-extract-content.md
    ├── 02-comment-model-api.md
    └── 03-nested-replies.md
```

**Small single-Todo changes:** use `Plan: none (single-Todo change)` and, when appropriate, `Spec: none (reason)`. The confirmed Todo carries the necessary technical decisions, product boundaries, test seam, and criteria. Downstream stages do not request intentionally omitted documents. See the shared [fields and state semantics](./_agents/workflow-contract.md).

---

## Stage 4: Implement and verify — `/flow-do`

This stage has the most orchestration and demonstrates the separation of coordination and execution.

### When to enter

- Stage 3 is complete and the Todos are confirmed.
- At least one Todo is executable, with its blockers satisfied.

### Run

```
/flow-do
```

**The main session coordinates; execution follows execution-mode:**

```
Main session                              Sub-agent (execution-mode=subagent)
  │                                          │
  ├─ 1. Select an unblocked Todo              │
  │     For versioned features, read INDEX    │
  │     and verify applicable Spec/Plan scope │
  ├─ 2. Choose checks and existing test seam  │
  ├─ 3. Delegate ──────────────────────────→ implementer
  │                                          │ · Verify blockers
  │                                          │ · Reuse tests; implement and check
  │                                          │ · Review Standards + Spec, P0/P1/P2
  │                                          │ · Return a structured report
  ├─ 3.5 Correct direction errors             │
  │     ├─ Inspect actual architecture        │
  │     ├─ Correct the Todo and classify      │
  │     ├─ Update Spec if understanding changed│
  │     └─ Redispatch; stop after two consecutive errors
  ├─ 4. Inspect report ←──────────────────────┘
  │     Are criteria met and checks passing?
  │     ├─ Endpoints → produce this Todo's required contract
  │     ├─ Engineering checks/review pass → resolved; close and release dependencies
  │     └─ Human functional items → Plan, otherwise Spec
  ├─ 5. Commit checkpoint, following commit-strategy
  │     ├─ Delegate /flow-simplify
  │     ├─ Human checkpoint: your confirmation
  │     └─ Commit
  └─ 6. Plan/Spec functional acceptance
        Actual user acceptance → accepted; close the acceptance issue
```

**Key boundaries:**

- **Sub-agents do not commit or invoke /flow-simplify.** The main session owns those steps at the commit checkpoint, with your confirmation.
- **An uncovered decision stops execution and is reported.** The worker does not guess or expand scope; the product and execution decisions should already be settled.
- **A direction error triggers Step 3.5.** If the proposed approach does not fit the architecture, the main session inspects it, corrects the Todo, decides whether the Spec must change, and redispatches. Stop for human alignment after two consecutive direction errors on the same Todo.
- **Never commit proactively.** Passing all checks does not replace the human checkpoint.
- **Engineering completion, functional acceptance, and Git are separate.** Once its implementation, required engineering checks, and review pass, a Todo becomes `resolved`, closes automatically, and releases downstream work. Under squash, upstream Todos need not be committed first. Plan/Spec Acceptance owns human functional review; neither an uncommitted tree nor pending acceptance delays a qualified engineering Todo.
- **In inline mode**, the main session follows `_agents/implementer.prompt.md` directly, with the same implementation and verification rules and no new sub-process.

Choose verification before implementing. For behavior and bugs, first reproduce failure in existing tests; for pure refactors, run before/after regression; for documents, configuration, and styles, use applicable checks. Reuse test files, fixtures, and parameterization for scenarios at the same seam rather than adding one file per Todo. Put temporary probes in a system temp directory and retain meaningful regression coverage. Failed or unrun required checks cannot be reported as complete.

### Output

- Working code with tests.
- Reviewed changes; cleanup and a commit only at the explicitly authorized checkpoint. Otherwise leave changes in the working tree.
- Updated Todo states.

---

## Supporting skills

### `/flow-run` — Bot/main-agent coordination

```text
/flow-run Implement order filtering and export. Confirm the Spec with me, then choose the technical approach and Todo split, and continue through development and verification.
```

The main agent reads existing settings, authoritative artifacts, and new messages, then resumes at the first unmet stage. It asks about substantive requirement ambiguity and presents the saved Spec for your confirmation. After confirmation, it reviews technical Plans, splits/reuses Todos, executes Do by dependency, and uses `/flow-e2e` for real browser verification of web features. Engineering Todos close automatically; human Plan/Spec acceptance remains separate. Commits, pushes, and deployment need their own authorization.

With dedicated agents, the Flow Agent remains the user-facing owner and dispatches under the [generic team contract](./flow-run/references/team-mode.md). Requirements handles Clarify + Spec; Planning handles Plan + Todo; Development handles Do/Debug/API; Verification handles applicable checks. Workers return artifacts, questions, and evidence to Flow rather than contacting you or triggering the next specialist. Flow relays your full answer and verifies the current project/version before advancing. Host adapters map concrete tool names; those APIs do not belong in the stage skills.

For this default run policy, explicitly choose no additional HTML for the `/flow-spec` invocation unless the request asks for it. Review test boundaries together with the Spec. Record delegated technical review and Todo splitting as authorized automatic planning, never as human review. Changed confirmed product scope returns to Spec confirmation. Required checks cannot be skipped.

Local `.scratch/<feature>/run.md` holds only source references, last action/evidence, pending questions, failed attempts, and the last processed message position. Actual progress comes from Spec/Plan/Todo records. With a remote tracker, it is a rebuildable coordination cache, not another local master. The host must wake the Bot on replies/resume and supply the complete message; the skill does not run as a persistent process. Use the [Bot setup policy](./flow-run/references/bot-setup.md).

For PI Desktop's [PI-Bot](https://github.com/vsd269/PI-Bot), see its [adapter guide](./flow-run/references/pi-bot.md). Choose a Bot with execution capability and let it read the complete skills checkout at a fixed location. Confirm the Spec through an `ask_user` card; the answer arrives as a new assignment. Skill imports are split into independent resource directories, so this repository's cross-directory references cannot be copied directly. A host task marked `completed` is not engineering evidence. The existing `install.sh pi` target installs for Pi CLI and does not configure the PI-Bot plugin.

### `/flow-e2e` — Local browser verification

After Do, you can say:

```text
/flow-e2e Start the app locally and run a test pass.
```

The agent derives scope from the latest Do, Todo, and Plan/Spec, starts or reuses the local service, and operates the completed feature in a real browser. It checks the main path and relevant exceptions, then reports actual outcomes, reproduction steps, and untested areas. It reuses known scope and asks only when the target, login, or required environment is unresolved. Verify the actual backend/data destination before startup and honor project read/write restrictions.

Use available browser tools or an existing project runner by default. A new E2E framework or maintained test files are not prerequisites. Opening a page is not proof the feature passes, and browser results do not replace human Plan/Spec acceptance. To retain regression coverage, explicitly ask to add maintained E2E tests for the flow, then follow the [maintained-test guide](./flow-e2e/references/maintained-tests.md), reuse or add tests, and actually run them.

### `/flow-simplify` — Code cleanup

**The main session sets scope from commit-strategy and delegates cleanup to `simplifier`.**

| Strategy | Trigger | Scope |
|----------|---------|-------|
| per-ticket | Before each Todo's commit | That Todo's diff |
| squash | Before the combined commit | Accumulated diff |

The sub-agent reviews and fixes reuse, quality, and efficiency issues, **without committing**, then reports. The main session shows the report and **waits for your confirmation** before committing.

### `/flow-api` — API contract extraction

**Triggered by `/flow-do` when a backend Todo involves public endpoints; it may also be invoked manually.**

The main session confirms the Todo's endpoints and delegates to `contract-writer`, which extracts code/test-backed contracts into `.scratch/<feature>/contracts/<ticket>.md`. Every field must be traceable to code, with no invented details. Frontend agents use the result for integration.

### `/flow-amend` — Requirement changes

**Use when an implemented Spec changes, without restarting the whole workflow.**

Clarify only the increment → assess depth within affected scopes → save the Spec version and current Plan registry → update affected Plans in place → add their simple Todos. Preserve unchanged Plans' implementation, approvals, acceptance, and historical Todos with explicit scope-applicability evidence. A new independent scope may add a Plan; do not copy an existing scope into a plan-vN document. Update only changed business flows and module impact.

Synchronize Parent/Spec navigation only with verified same-feature identity, a fresh read, and applicable authorization. Reference changes do not reset unrelated scopes. Historical Todos retain their version and state. INDEX/Spec lists all applicable Plans and their own Todos. `/flow-status` reports each Plan's engineering, closure sync, and acceptance read-only before summarizing the whole Spec; one Plan's state is not the feature's entire state.

### `/flow-export` — Session export

**The main session identifies the tool and confirms issue binding, then delegates conversion to `exporter`.**

Supports Claude Code, Codex, and Pi local JSONL storage, plus Cursor SQLite. Write both `session.md` (readable) and `session.jsonl` (raw archive) under `sessions/<project>-<issue>-<date>/`. This is faithful format conversion, not summarization.

### `/flow-debug` — Debugging

**Interactive; stays in the main session.** Six phases: build a feedback loop → reproduce/minimize → hypothesize → instrument → fix/regress → clean up. Establish a loop that can demonstrate failure before discussing a fix.

---

## End-to-end walkthrough: blog comments

```
Day 1 AM           Day 1 PM           Day 2 AM           Day 2 PM           Day 3 AM
    │                  │                  │                  │                  │
    ▼                  ▼                  ▼                  ▼                  ▼
/flow-init         /flow-clarify      /flow-spec         /flow-plan         /flow-todo
    │                  │                  │                  │                  │
    ▼                  ▼                  ▼                  ▼                  ▼
Four settings:     Requirements:      Product Spec:      Blueprint:         Split Todos:
- local tracker    - sign-in          - four sections    - decision table   - 01 prefactor
- squash commits   - max depth 3      - HTTP API seam    - packages P1..Pn  - 02 model/API
- sub-agent mode   - word filtering   - .scratch/        - risks            - 03 nesting
                   update CONTEXT.md    .../spec.md      (human review)     (dependencies/P)

Day 4
    │
    ▼
/flow-do for each Todo
    │
    ├─ Todo 01: red/green/refactor → engineering checks/review → resolved; release Todo 02
    │     Squash strategy: leave uncommitted; human functional items stay in Plan.
    ├─ Todo 02: same process; produce endpoint contracts immediately when required.
    ├─ Todo 03: same process; use preceding code and contracts.
    │
    ▼ All engineering Todos resolved; feature is engineering-complete, acceptance pending.
  Delegate /flow-simplify over the accumulated diff → fixes and report.
    │
    ▼ Human checkpoint: you confirm.
  Commit together only with explicit authorization. Deferring Git does not reopen Todos.
    │
    ▼ Functional acceptance in Plan, otherwise Spec.
  Actual user confirmation → Acceptance: accepted; close that acceptance issue.
  Closed Todos alone are not functional acceptance.
```

### Output tree

```
project/
├── AGENTS.md                              # Stage 0 pointers
├── CONTEXT.md                             # Stage 1 glossary
├── docs/
│   └── agents/
│       ├── issue-tracker.md               # Stage 0
│       ├── commit-strategy.md             # Stage 0
│       ├── execution-mode.md              # Stage 0
│       └── language.md                    # Interaction and artifact languages
├── .scratch/
│   └── blog-comments/
│       ├── spec.md                        # Stage 2
│       ├── plan.md                        # Stage 2.5, reviewed blueprint
│       ├── issues/                        # Stage 3
│       │   ├── 01-prefactor-extract-content.md
│       │   ├── 02-comment-model-api.md
│       │   └── 03-nested-replies.md
│       └── contracts/                     # /flow-api
│           ├── 02-comment-model-api.md
│           └── 03-nested-replies.md
└── src/                                   # Stage 4 implementation
```

---

## Key constraints

| Constraint | Meaning |
|------------|---------|
| Initialize first | Without `docs/agents/*.md`, flow-spec/flow-todo/flow-do ask for `/flow-init` |
| Stage order | Normal features: clarify → spec → approved plan → todo → do; small changes use explicit shared omissions |
| Artifacts drive execution | Spec → Plan → Todo → code; simplified Todos carry decisions from omitted documents |
| Settle decisions upstream | Product boundaries in Spec, technical approach in Plan, engineering criteria in Todo; human acceptance in Plan/Spec |
| State and Git | Passing Todo engineering work resolves/closes it; functional Acceptance and Git authority are separate and do not delay completion |
| Sub-agent boundaries | No commits or /flow-simplify; stop/report uncovered decisions; direction errors trigger Step 3.5 |
| Never commit proactively | Every stage/agent leaves changes in the working tree without your explicit instruction |
| Overrides | Four settings are project defaults; an explicit task request may override the relevant setting |
| Interactive work stays in the main session | flow-clarify/flow-debug/flow-spec/flow-plan/flow-todo need a user conversation rather than isolated execution |

---

## Authoritative sources

- Skill definitions: each `<skill>/SKILL.md`.
- Execution logic: `_agents/*.prompt.md`.
- Shared fields and state semantics: `_agents/workflow-contract.md`; the target tracker's declaration owns its actual state vocabulary.
- Cross-tool adapters: `adapters/build.sh` generates agent files for each tool.

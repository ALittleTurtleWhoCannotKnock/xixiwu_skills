# Dev Flow Skills

**English** | [简体中文](./README.zh-CN.md)

A five-stage development workflow plus debugging skills, shared across Pi, Codex, and Claude Code.

[User guide](./TUTORIAL.md) · [Architecture](./architecture.md) · [Contributing](./CONTRIBUTING.md)

Break complex requirements into **Spec → independent Plans → simple Todos**. The AI chooses the number of Plans from functional boundaries and coupling; a simple requirement may need only one. Explicit user counts or groupings take precedence. Each Plan can be implemented and verified independently, then split into engineering Todos with clear inputs, results, boundaries, and checks. Related small Todos may share an execution batch, while completion is assessed separately for each Todo.

> **Global rule: never commit or push proactively.** Unless the user explicitly asks to commit or push, every stage and agent, including the main session and sub-agents, leaves changes in the working tree. Committing always requires a human checkpoint.

## Safety and trust

These skills let an AI agent execute shell commands and read or write files on your machine. Before installing:

- **Install only versions from this repository's `main` branch.** Forks, mirrors, and redistributed copies may have been modified; do not install them.
- The `main` branch is protected. All changes must go through a PR and line-by-line maintainer review before merging.
- Reject PRs that introduce remote script download/execution, system configuration changes unrelated to the workflow instructions, or access to and exfiltration of local credentials.
- The `install.sh` installer writes to the selected CLI's configuration directories. Use `--dry-run` to inspect the proposed changes first.

Report problems in an issue rather than submitting a PR that changes default behavior on someone else's machine.

## Installation and updates

Review the source on this repository's `main` branch before installing or updating, then use the local `install.sh` entry point. For the initial checkout, see [Install from source](#install-from-source-cli).

### Multica: one package plus one role

Multica workspace skills and runtime-local skills are separate installation locations. Log in to the Multica CLI, select the correct workspace, and run these commands from this repository:

```bash
# Preview first; use an actual agent ID rather than guessing by name.
./install.sh multica --agent-id <agent-id> --role flow --dry-run

# Import one dev-flow package, add its binding, and save the Flow role instructions.
./install.sh multica --agent-id <agent-id> --role flow
```

The installer reads the current CLI workspace by default. For a target in another workspace, pass `--workspace-id <workspace-id>`. It verifies the agent's workspace and scopes subsequent calls to it without changing the default workspace. To replace a package you previously imported under the same name, explicitly pass `--on-conflict overwrite`; conflicts stop the installation by default. Omit both `--agent-id` and `--role` to import only the skill, without configuring a role.

The unified package is built deterministically from the maintained `flow-*` skills, shared rules, resources, and role documents. Building it does not modify those sources. Internal entry points become ordinary documents to support hosts that discard nested `SKILL.md` files. Only one `dev-flow` workspace Skill is needed; stage instructions are still loaded on demand. To import through Multica's local-file interface, first build the archive with `python3 -B adapters/package_bundle.py --output dist/dev-flow.skill`.

Available roles are `flow`, `requirements`, `planning`, `development`, and `verification`: [Flow](./roles/flow.md), [Requirements](./roles/requirements.md), [Planning](./roles/planning.md), [Development](./roles/development.md), and [Verification](./roles/verification.md). These persistent role instructions are in Chinese; stage-instruction language and the target project's artifact-language settings remain independent. The Flow role coordinates and reviews evidence; missing specialists do not authorize it to implement business code. The installer backs up existing instructions, preserves content outside the managed role markers, updates only that block, and adds the skill binding. It does not change models, runtimes, Access, environment variables, or tool permissions. Reinstallation updates the same role block. Resolve any conflicting custom instructions outside that block yourself.

**Descriptions, skills, and permissions serve different purposes.** Multica's Description is display metadata; Instructions are injected into runs. Attaching a skill alone does not turn a coding runtime into a read-only coordinator. Role instructions define behavior; enforcement of file, command, or network restrictions belongs to the host, runtime, or operating system. Multica Access controls who can invoke an agent, rather than that agent's tool permissions. An agent's self-description or prompt compliance is not proof of permission isolation. See the [official Multica role guide](https://github.com/multica-ai/multica/blob/3c5c8b245359b9b8e913a47f97211f2a3426f149/apps/docs/content/docs/agents-create.zh.mdx) and [runtime security model](https://github.com/multica-ai/multica/blob/3c5c8b245359b9b8e913a47f97211f2a3426f149/apps/docs/content/docs/security-model.zh.mdx).

A workspace package is an import-time snapshot. Updating the local checkout does not refresh the copy stored in Multica; import it again. The installer adds a binding while preserving other capabilities. It does not remove old `flow-run`/`flow-status` bindings or inherited local skills. Once the unified package works, you can disable obsolete bindings in the UI.

### Install from source (CLI)

Requires Bash and Python 3.9+. Keep the repository in a permanent, separate directory, then choose the target CLI:

```bash
git clone https://github.com/ALittleTurtleWhoCannotKnock/xixiwu_skills.git
cd xixiwu_skills
```

Review `install.sh`, `adapters/`, and the skills you intend to install. After review, preview the changes and run the local installer:

```bash
./install.sh all --dry-run
./install.sh all

# Or install for a single CLI.
./install.sh pi
./install.sh claude-code
./install.sh codex
```

The same entry point handles installation and updates. In the original checkout, inspect incoming changes first:

```bash
git fetch origin main
git diff HEAD..origin/main
```

After reviewing the changes, update the checkout, preview, and install:

```bash
git pull --ff-only
./install.sh all --dry-run
./install.sh all
```

The installer links the skills and `_agents/` to this checkout. Adapters generate the Pi and Claude Code agent files. Keep the checkout at the same location so the symlinks remain valid. If the source is inside a skill-discovery directory, move it to a separate directory first.

| Target | Skills and shared files | Generated agents |
|--------|-------------------------|------------------|
| `pi` | `~/.pi/agent/skills/` | `~/.pi/agent/agents/` |
| `claude-code` | `~/.claude/skills/` | `~/.claude/agents/` |
| `codex` | `~/.agents/skills/` | Reads the shared prompt when delegating |

Codex and Claude Code local skill directories support symlinks; see the [OpenAI documentation](https://learn.chatgpt.com/docs/build-skills) and [Claude Code documentation](https://code.claude.com/docs/en/skills#choose-where-skills-load). Pi skill discovery is described in the [Pi documentation](https://pi.dev/docs/latest/skills).

Updates preserve the YAML frontmatter of existing agents, including model, tool lists, and other custom fields, and replace only the body. New agents have no model binding by default. Run `/flow-init` in the target project to select its base model, or pass `--project-root /path/to/project` during installation so new Pi agents can read that project's existing choice. Existing agent configuration takes precedence. The installer does not rewrite the project's tracker, execution-mode, or model configuration.

Old directories and symlinks with managed names, and agent files being updated, are first moved to `~/.local/share/dev-flow-skills/backups/<timestamp>/`, preserving their directory structure. Backups are outside skill-discovery directories. Old whole-bundle copies and matching managed entries under Codex's legacy `~/.codex/skills/` directory are also moved out to prevent stale discovery. Other skills and CC Switch source files are preserved. To restore an item, replace its installed path with the corresponding backup. Repeating an unchanged installation creates no backup.

Skill commands use the `flow-*` names. When upgrading older versions, the installer backs up and removes old-name links pointing to this repository, copies identified by their skill declarations, and old whole-bundle directories, then installs the new names. Personal skills with the same name are preserved. Use the commands below in new sessions; existing project settings, Todo fields, and artifact paths stay intact.

Use `--home /tmp/dev-flow-home` for an isolated installation. Reopen the CLI session after installation. With managers such as CC Switch, use this checkout as the source for future updates to avoid restoring an old copy.

## Main workflow

Use [`/flow-run`](./flow-run/SKILL.md) to let a Bot or main agent coordinate the feature: prepare a Spec, obtain your confirmation, then plan, create Todos, implement, and run applicable local browser verification. It reuses the stage skills below and preserves their standalone interactions. Technical planning and task splitting follow the actual delegation; human functional acceptance and Git/deployment authorization remain separate. On restart, it recovers from authoritative artifacts and a small checkpoint. The host is responsible for waking the Bot and retaining sessions. See [Bot setup](./flow-run/references/bot-setup.md).

With dedicated agents, the Flow Agent is the sole user-facing owner. It routes Requirements, Planning (Plan + Todo), Development, and Verification to bound workers, reviews their questions and evidence, and advances the workflow. See the [generic team contract](./flow-run/references/team-mode.md) for roles, assignments, and results. Host adapters own the dispatch APIs; stage skills remain independently reusable.

The Flow Agent may directly maintain evidence-backed coordination status, confirmation records, and navigation links. Group Todos by workload, shared context, dependencies, and change scope. Small related Todos can share a session and applicable checks; independent groups can use separate sessions when supported by the host and directory isolation. Assess each Todo's completion from its actual coverage and engineering evidence. Stage skills retain their business rules.

```
/flow-init       Initialize the workflow for a repository, or fill missing settings
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

An implemented Spec changed? → /flow-amend
    Increment the Spec version, update affected Plans in place, and add follow-on Todos.
```

## Supporting skills

```
/flow-amend
    Clarify only changes to an implemented Spec, assess increment vs. redesign,
    then create spec-v(N+1), update INDEX, and add follow-on Todos.

/flow-debug
    Debug systematically: feedback loop → minimize → hypothesize → instrument → fix → regress.

/flow-export
    Export the original session transcript as Markdown.
    Supports Claude Code, Codex, Pi, and Cursor.

/flow-api
    Extract API contract fragments after a backend Todo for frontend integration.
    Useful for Node.js projects without generated API documentation.
```

## Skill catalog

| Stage | Command | Purpose | Delegation |
|-------|---------|---------|------------|
| Coordination | `/flow-run` | Plan, split, implement, verify, and resume after human Spec confirmation | Main agent coordinates; execution follows project mode |
| 0. Initialize | `/flow-init` | Discover the tracker and write declarations for a new repository | — |
| 1. Clarify | `/flow-clarify` | Align requirements through questions and maintain CONTEXT.md | Interactive; stays in the main session |
| 2. Specify | `/flow-spec` | Four-section product Spec with boundaries and seam analysis | Interactive; stays in the main session |
| 2.5. Plan | `/flow-plan` | Independent Plan scopes, decisions, packages, and risks; applicable approval precedes ticketing | Interactive; stays in the main session |
| 3. Split Todos | `/flow-todo` | Simple, verifiable engineering Todos under each actual Plan | Interactive; stays in the main session |
| 4. Implement | `/flow-do` | Choose checks by change type, reuse tests, and review | ✅ `implementer` executes an assigned Todo |
| Support | `/flow-status` | Read-only feature, stage, Todo, blocker, and next-action snapshot | Main session interprets; scout may discover files |
| Support | `/flow-amend` | Incremental changes to an implemented Spec, with a redesign gate | Interactive; stays in the main session |
| Support | `/flow-simplify` | Cleanup before committing: reuse, quality, and efficiency | ✅ `simplifier` |
| Support | `/flow-debug` | Systematic debugging loop | Interactive; stays in the main session |
| Support | `/flow-e2e` | Start locally and verify in a real browser; retain regression tests only when requested | Follows execution-mode; worker needs browser capability |
| Support | `/flow-export` | Export the original session transcript as Markdown | ✅ `exporter` |
| Support | `/flow-api` | Produce a Todo's API contract for frontend agents | ✅ `contract-writer` |

**Tracker artifacts:** A Spec may reference one or several Plans. Its `Plans:` list records actual references and scopes; legacy singleton `Plan:` and `plan.md` remain supported. New local peer scopes use `plans/<scope>.md`; remotely, each Plan is an independent issue with its own Scope, approval, acceptance, and Todos. `P1/P2` are packages inside one Plan, not separate Plans. `/flow-amend` updates affected Plans in place, preserving unchanged scopes without creating plan-vN. See the [shared contract](./_agents/workflow-contract.md#Spec与多个Plan).

**Optional Spec HTML:** At the start of `/flow-spec`, choose whether this invocation should also produce an HTML reading view. Reuse an explicit choice in the request; otherwise wait for the answer. The choice applies only to that invocation. The Markdown file or Spec issue stays authoritative. HTML is a snapshot with source, version, and generation time; no separate requirements-clarification page is created. GitHub retains the readable Spec body. Add an online reading link only when an authorized publishing channel exists and access has been verified. Otherwise deliver the local file without automatically committing or deploying it. See the [HTML reading-view contract](./flow-spec/references/html-review.md).

## Hierarchy and progress

New Todos use the `[Todo]` title prefix and, on GitHub, the default `todo` type label. Local titles, Plan lists, INDEX navigation, and progress reports also use Todo. Legacy `[Ticket]`/`ticket` items remain discoverable and reusable; renaming does not justify duplicate issues or bulk changes to historical titles and labels.

The default hierarchy is **Spec → Plans (1:N) → each Plan's Todos (1:N)**, with an existing Epic above the Spec when specified. Each Plan declares its Scope. A Todo's Parent/Plan identifies one actual owner and package; Spec identifies the applicable version, while Blocked by records execution dependencies. New hard dependencies between peer Plans contradict independence. If a requested count cannot satisfy independence and coverage, explain the conflict and ask rather than inventing empty scopes or silently changing the count.

| Tracker | Hierarchy and navigation |
|---------|--------------------------|
| GitHub | Native parent/sub-issue relationships; titles and type labels distinguish Spec, Plan, and Todo. Configured Projects tables can enable View → Show hierarchy. |
| Local Markdown | `.scratch/README.md` lists feature entries. Each feature's `INDEX.md` links the current Spec, applicable Plans, Todos, and evolution history. `/flow-status` reads source files to display a status tree. |
| GitLab | Keep the same logical fields and use actual platform capabilities for native relationships; report unsupported display features. |

Keep one file per Todo and continue numbering across the feature. Do not move an existing plan.md. A multi-Plan example:

```text
.scratch/
├── README.md                 # Feature entries
└── export/
    ├── INDEX.md              # Clickable Spec/Plan/Todo hierarchy
    ├── spec.md               # Historical Spec retained
    ├── spec-v2.md            # Current Spec, selected by INDEX
    ├── plans/
    │   ├── import.md         # Independent scope, updated in place
    │   └── export.md         # Independent scope, updated in place
    └── issues/
        ├── 01-csv.md         # Historical Todo for Spec v1
        └── 04-json.md        # Current Todo for Spec v2
```

INDEX holds navigation, current-version provenance, and evolution history, rather than copies of Plan bodies, Todo states, or approvals. Synchronize links when creating or updating artifacts. Read-only `/flow-status` reports missing, conflicting, or broken references without repairing them. Projects is optional. Child progress proves neither Plan approval nor functional acceptance. See [ownership and navigation](./_agents/workflow-contract.md#归属层级与列表展示).

## Execution sub-agents

Execution stages may delegate to isolated sub-agents: clear inputs → execute → write artifacts → report, without an intermediate user conversation.

**One prompt source, with tool adapters:**

```
_agents/                # Tool-independent prompts; edit execution logic here
├── exporter.prompt.md
├── simplifier.prompt.md
├── contract-writer.prompt.md
├── implementer.prompt.md
├── scout.prompt.md
└── diagram-guide.md     # Mermaid conventions, not a separate agent

adapters/               # Tool-specific thinking levels and tool allowlists
├── build.sh            # Generate agent files: ./adapters/build.sh all
└── codex/README.md
```

| Agent | Responsibility | Thinking | Autonomy |
|-------|----------------|----------|----------|
| `exporter` | Session format conversion | low | Autonomous |
| `simplifier` | Cleanup before committing | medium | Autonomous; does not commit |
| `contract-writer` | API contract extraction | medium | Autonomous |
| `implementer` | An assigned Todo's implementation and verification | high | Autonomous; does not commit or invoke /flow-simplify |
| `scout` | Code reconnaissance → context.md | low | Autonomous |

**Design principles:**

- **Settle decisions upstream.** Spec owns product decisions, Plan technical decisions, and Todo execution details. An execution agent stops and reports an uncovered decision instead of guessing or expanding scope. It does not rely on an intermediate question channel to the main agent, allowing the same logic across Pi, Claude Code, and Codex.
- **Clear boundaries.** Sub-agents neither commit nor invoke /flow-simplify. The main session owns those steps at the commit checkpoint, with human authorization.
- **Automatic engineering completion.** Claim a Todo as `claimed`; once implementation, required engineering checks, and review pass, mark it `resolved`. Synchronize remote closure; locally, the state update is closure. Human functional acceptance and Git authorization do not delay a qualified engineering Todo. Acceptance belongs to Plan, otherwise Spec. `/flow-status` shows engineering and acceptance separately; `code-complete` is legacy compatibility only. See [state semantics](./_agents/workflow-contract.md#状态与依赖).
- **Small-change path.** A confirmed small Todo may explicitly omit Spec/Plan and carry the necessary decisions, test boundaries, and criteria itself. Downstream stages respect that omission.
- **Test organization.** Reuse test files and fixtures, parameterizing related inputs. Use behavior tests for behavior/bug changes, before/after regression for pure refactoring, and applicable checks for docs, configuration, and styles. Required verification must pass; do not generate test files per Todo. See [validation conventions](./_agents/workflow-contract.md#验证方式与测试组织).
- **Read-only progress.** `/flow-status` aggregates without changing state. Scout handles complex file discovery only; the main session interprets status.
- **Interactive stages stay in the main session.** `/flow-clarify`, `/flow-debug`, `/flow-spec`, `/flow-plan`, and `/flow-todo` need user interaction and are unsuitable for isolated execution.

**Generate agent files directly (low-level adapter):** Use root `install.sh` for normal installation and updates so existing agent configuration is preserved. `build.sh` generates complete files from templates:

```bash
./adapters/build.sh all --project-root /path/to/project

# Preview generated files in a separate directory.
./adapters/build.sh all --project-root /path/to/project --output-dir /tmp/dev-flow-preview
```

**Users select the base model during initialization.** `/flow-init` offers the current tool's actual available models or explicit `inherit`, then saves the choice to `docs/agents/execution-mode.md`. Templates hard-code neither model nor provider.

For Pi builds, precedence is the one-off `DEV_FLOW_MODEL` override, then the target project's base-model field (`基础模型`). Without an explicit setting, omit `model` and use the tool's native defaults. Other tools apply the project choice through their supported dispatch parameters.

`--project-root` explicitly selects the project whose configuration is read. If omitted, it always defaults to the skill repository root, regardless of the invoking directory.

`--output-dir` writes Pi and Claude Code files to its `pi/` and `claude-code/` subdirectories for previews and isolated tests. Without it, output goes to each tool's user-level agents directory. The `codex` target prints usage guidance and writes no files.

**Delegation is configurable.** `/flow-init` asks for the default execution mode and stores it in `docs/agents/execution-mode.md`:

- `subagent` (recommended default): delegate execution stages to isolated sub-agents.
- `inline`: the main session follows the same `_agents/*.prompt.md` directly.

Either choice allows an explicit one-off override, such as asking to handle a small Todo inline. `_agents/*.prompt.md` remains the single source for execution logic; only the executor differs.

**Initialization also confirms interaction and artifact languages independently.** `/flow-init` saves both to the target project's `docs/agents/language.md`. For example, Chinese interaction with English Spec/Plan/Todos; this is an example, not a template default:

```markdown
# Workflow language
interaction_language: zh-CN
artifact_language: en
```

An explicit task language overrides only that task's corresponding setting. On an older project, initialization can fill only missing languages while preserving tracker, commit strategy, execution mode, and base model. Never save guessed preferences as confirmed. Ordinary work with missing settings may temporarily follow the conversation or existing artifact language, without blocking or initializing on the user's behalf.

Skills and generated execution agents follow the [language policy](./_agents/language-policy.md). Internal instruction language is independent from user-output language. Artifact titles, prose, and diagram labels follow project settings; protocol fields, state values, references, code/API identifiers, and original transcripts stay intact. Changing a default does not bulk-translate history. Pass both languages and the target project on delegation rather than baking a project's preferences into global agents.

## Sharing with other teams or repositories

Distribute the complete repository or archive. Recipients keep it in a permanent, separate directory and use the same installer:

```bash
cd /path/to/xixiwu_skills
./install.sh all
```

Each user runs `/flow-init` in their own project to configure the tracker, commit strategy, execution mode, base model, and languages. Templates need no prefilled model or language preference. Archive users update by replacing the complete checkout at the same location and rerunning `install.sh`.

## Diagrams: flows, architecture, sequences, and swimlanes

Key stages generate **Mermaid diagrams**, using semantic conventions derived from archify. Mermaid source is plain text suitable for git diff, rendered as diagrams by supported GitHub, Feishu, and VS Code viewers. Agents read structured text; people see diagrams. The conventions live in `_agents/diagram-guide.md`.

**Choose a diagram type by meaning:**

| Scenario | Type | Purpose |
|----------|------|---------|
| Stages, decisions, loops, and swimlane grouping | `flowchart` | Project architecture and feature flows |
| Call order, sync/async behavior, returns, and security boundaries | `sequenceDiagram` | A Spec's end-to-end interactions |

- **Project architecture:** `/flow-init` generates `.scratch/architecture.md` for an existing codebase, using `flowchart` and `subgraph` swimlanes to orient agents. See this repository's [architecture example](./architecture.md).
- **Functional flow:** the Spec's approach contains a `flowchart` of entry points, user actions, branches, and outcomes. Keep module impact as a written list.
- **End-to-end sequence:** the Spec uses `sequenceDiagram`, with `->>` for synchronous calls, `-->>` for returns, and `-)` for asynchronous messages.

**Variants carry meaning.** Diagram types, arrows, and decisions are semantic rather than decorative. Labels are data; do not remove them to adjust layout.

## Usage

1. Run `./install.sh <pi|claude-code|codex|all>` to install skills and adapters.
2. **Run `/flow-init` first in a new repository** to choose the tracker, commit strategy, execution mode/base model, and both languages.
3. Invoke stages in order with `/command`. Execution stages delegate or run inline according to execution-mode.
4. Use `/flow-debug` for difficult bugs.
5. After a backend Todo involving public endpoints, use `/flow-api` to produce the contract for frontend integration.

## Repository layout

```
dev-flow-skills/
├── README.md                 # English project overview
├── README.zh-CN.md           # Chinese project overview
├── install.sh                # Unified installation and update entry point
├── TUTORIAL.md               # English user guide
├── TUTORIAL.zh-CN.md          # Chinese user guide
├── architecture.md           # English architecture example (Mermaid)
├── architecture.zh-CN.md     # Chinese architecture example (Mermaid)
├── CONTRIBUTING.md           # English contribution guide
├── CONTRIBUTING.zh-CN.md     # Chinese contribution guide
├── _agents/                  # Source prompts for execution sub-agents
│   ├── README.md
│   ├── workflow-contract.md  # Shared fields, states, and small-change rules
│   ├── language-policy.md    # Interaction/artifact languages for all roles
│   ├── diagram-guide.md      # Diagram conventions, not a separate agent
│   ├── exporter.prompt.md
│   ├── simplifier.prompt.md
│   ├── contract-writer.prompt.md
│   ├── implementer.prompt.md
│   └── scout.prompt.md
├── adapters/                 # Cross-tool adapters
│   ├── build.sh
│   ├── install.py            # Installation, backups, and agent-config preservation
│   ├── package_bundle.py     # Build one dev-flow.skill from maintained sources
│   ├── multica.py            # Workspace import, additive binding, and managed roles
│   └── codex/README.md
├── roles/                    # Five Chinese role instructions; not tool permissions
├── tests/                    # Adapter checks and workflow scenarios
├── flow-run/
│   ├── SKILL.md
│   └── references/bot-setup.md
├── flow-init/
│   └── SKILL.md
├── flow-clarify/
│   └── SKILL.md
├── flow-spec/
│   └── SKILL.md
├── flow-plan/
│   └── SKILL.md
├── flow-todo/
│   └── SKILL.md
├── flow-do/
│   └── SKILL.md
├── flow-status/
│   └── SKILL.md
├── flow-amend/
│   └── SKILL.md
├── flow-debug/
│   └── SKILL.md
├── flow-e2e/
│   └── SKILL.md
├── flow-simplify/
│   └── SKILL.md
├── flow-export/
│   └── SKILL.md
└── flow-api/
    └── SKILL.md
```

## Validation

```bash
bash -n install.sh adapters/build.sh
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```

Automated tests use temporary directories and a temporary HOME to verify generation and installation: target arguments, model precedence, inclusion of language policy without binding a project's choices, initial installation, repeated updates, legacy migration, backups, configuration preservation, dry runs, and source-checkout protection. They do not write to real user-level directories. See [`tests/workflow-scenarios.md`](./tests/workflow-scenarios.md) for behavioral skill evaluations; keyword checks do not replace actual execution.

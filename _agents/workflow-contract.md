# Shared Workflow Contract

Workflow skills and the implementer share these field formats/default semantics. The target repository's `docs/agents/issue-tracker.md` declares its actual state vocabulary.

Resolve interaction/artifact preferences from the target repository's language.md using the supervisor-supplied or adapter-appended policy (`_agents/language-policy.md`). Ordinary work may use a temporary fallback for missing preferences, without saving inferred defaults.

<a name="执行任务与Todo"></a>
## Prepare simple Todos before dispatch

The main decomposition is **Spec → one or more independent Plans → simple Todos**. A Plan owns an independently deliverable scope; each Todo owns one clear engineering result within that Plan. A Todo need not deliver every application layer or a complete user-facing feature on its own. If it still mixes several difficult results, refine it into simpler Todos instead of leaving the main decomposition to the executor. Ordinary coding steps remain inside a Todo, and related small Todos may share an assignment/session; no extra task-document layer is required.

Before dispatch, the planning owner or stage supervisor prepares enough detail for the executor to identify:
- the concrete result it must produce, including the part of the parent Todo it covers;
- the available inputs, settled rules, prerequisites and relevant current code/Plan references;
- the permitted change boundary and what remains outside this task;
- the checks or examples that establish this task's completion.

The executor still chooses routine local coding details. It should not receive an undivided feature goal that requires it to clarify product policy, choose the architecture, decompose the work and implement everything in the same assignment. If an unknown can change the task's inputs, approach or scope, first assign a focused investigation, then have the appropriate decision owner settle it before dependent implementation. Routine source lookup within a settled task stays with the executor.

Split until the next action and result are clear, not to a fixed number of tasks, files or functions. Ready related tasks may execute together without returning to the Flow Agent after every internal step; independent groups still require actual host/working-directory support for parallelism. Completing an execution task proves only its assigned scope. Resolve a Todo only after its full engineering criteria, required checks, review and deliverables pass.

<a name="Spec与多个Plan"></a>
## Spec to independent Plans

- When a Plan is needed, choose one or more peer Plans from the confirmed Spec's functional boundaries, coupling, change scope and independent verification. Keep a simple/coupled requirement in one Plan; split a complex requirement when it has independently deliverable scopes. Explain the chosen count and boundaries briefly, without adding a separate count-approval round.
- An explicit user count or grouping takes precedence over the AI's preferred split. Produce that many actual Plan artifacts, not one Plan containing that many P<N> packages. If the count/grouping conflicts with complete coverage, nonempty scopes or independence, explain the concrete conflict and ask before choosing an alternative; do not silently change the number, omit work or create empty Plans.
- Peer Plans collectively cover the confirmed implementation scope without duplicate ownership. Each must be implementable and verifiable from the agreed baseline/stable existing contracts, without another new peer Plan's output as a prerequisite. Do not split frontend/backend/testing phases into nominally independent Plans. Resolve shared-contract changes and overlapping mutable boundaries before claiming independence; do not hide cross-Plan coupling in Todo blockers. Independence does not bypass runtime locks, shared-file conflicts or Git permissions.
- Each Plan records `Parent:` (the Spec), `Spec:` (its applicable version), and `Scope:` (the owned requirement/acceptance subset, using actual criteria or section references). It owns its technical review, Todos and scoped functional acceptance. A legacy singleton without Scope may cover the whole Spec when unambiguous. P<N> is internal to one Plan; always qualify it with the Plan file/issue.
- The Spec lists current Plan references and scopes under `Plans:`; legacy singleton `Plan:` remains valid. Read both forms and deduplicate by actual identity; conflicting listings require reconciliation. Reuse an existing Plan by its Spec identity and scope, not only by title/count. Re-running planning does not create duplicates; a requested repartition must account for existing scopes, claims and completed work before changing ownership.
- When Plan writers run separately, each owns its scoped body; designate one coordinator to merge the Spec/INDEX Plan list from fresh sources without losing peer references. Do not let concurrent writers replace the registry with only their own Plan.
- Change only affected Plan decisions, approval/acceptance and Todos. An unaffected Plan may retain an earlier Spec binding when the current confirmed change record explicitly proves its scope/contracts remain unchanged; an older version alone is neither invalid nor sufficient evidence of validity. Navigation-only reference updates do not reset review or acceptance. Historical Todo versions/states are not rewritten merely because another Plan changed.

<a name="基础模型"></a>
## Base model

- Initialization guides the user through the current tool's actual available models or explicit `inherit`, saved in `docs/agents/execution-mode.md` under `基础模型`. Templates hard-code neither a model nor provider.
- Dispatch passes that confirmed ID through the tool's supported parameter. `inherit` uses native inheritance; inline keeps the main-session model.
- Without a configured selection, use tool defaults and complete selection guidance on initialization, never silently choose. Report unsupported IDs and incompatibility rather than substituting a model.
- Pi builds read the explicit `--project-root`; `DEV_FLOW_MODEL` can override once. Without an explicit choice, omit `model`.

<a name="tracker-产物与-plan-引用"></a>
## Tracker artifacts and Plan references

Read the tracker declaration. Each artifact has one current authoritative store:

| Artifact | Local tracker | GitHub/GitLab tracker |
|----------|---------------|----------------------|
| Spec | `.scratch/<feature>/spec.md` or version file | Spec issue under the declared version convention |
| Plans | Existing singleton `plan.md`; new peer scopes use `.scratch/<feature>/plans/<scope-slug>.md` | One independent issue per Plan/scope, current approach in its body |
| Todo | `.scratch/<feature>/issues/<NN>-<slug>.md` | One independent issue each |

Execution artifacts are **Todos (待办)**. Use `Todo`/`Todos` in new titles, document headings, Plan lists, INDEX navigation, and status reports. Internal references to a “ticket” mean this same artifact; existing paths, protocol fields, state values, and `per-ticket` configuration remain unchanged.

Legacy `[Ticket]` titles, `ticket` type labels, and Ticket-based tracker examples remain readable aliases, not the naming for new Todos. Match existing work by provenance and scope, including both `todo` and legacy `ticket` results when filtering by type and deduplicating by issue identity. Reuse matching items without bulk-renaming/relabeling history or recreating issues to adopt the new name.

- Remote titles may use `[Plan] <Feature> — <Scope> 实施蓝图`. Each Plan's `Spec:` identifies its applicable version; the Spec backlinks all current Plans, and each Plan lists only its own Todos. Reuse the same artifact for the same scope rather than duplicating it.
- Tickets separate Spec version from qualified Plan/package identity. Local examples: `Plan: plans/import.md#P1` or legacy `plan.md#P2`; remotely `Plan: #101 / P1`, with full URLs across repositories. P1 in another Plan is a different package, not the same execution source.
- Keep the remote current plan out of Spec comments and avoid a second local master. Comments hold discussion, approval evidence, and change reasons; the body holds the approach and `**状态**: 待 review` or `**状态**: 已批准（日期）`.
- Native open/closed does not establish plan approval or remove execution restrictions. Read the stamp and actual authorization.
- `/flow-amend` updates the same affected Plan artifacts, not plan-vN, preserving unaffected scopes. A confirmed new independent scope may add a Plan under the count/grouping rules. Retain the Spec-version convention; issue numbers do not determine versions.
- When continuing an old comment-only plan, migrate its current content into an independent issue, retain history/evidence, and update touched references. Read-only queries only recommend migration.

Optional Spec HTML is a derived reading snapshot; `/flow-spec` asks per invocation and generates it only when requested. The Markdown file or remote issue remains authoritative, including approval/acceptance. Link only actual files or verified, authorized deployed pages, and keep source/version provenance. If a touched Spec changes, refresh HTML only when the request includes it, or mark/remove its current-reading link as stale while preserving the historical file. Existing HTML alone is not consent for new generation or publication.

<a name="归属层级与列表展示"></a>
## Ownership and navigation

Default hierarchy: **Spec → Plans (1:N) → Todos (1:N per Plan)**. Link an explicitly identified Epic above the Spec, without manufacturing an extra parent. Parent identifies direct ownership, Spec the applicable version, Plan the specific approach/package, and Blocked by execution dependencies; they are distinct. Each Todo has one direct Plan owner, not every Plan in the feature.

| Artifact | Parent reference |
|----------|------------------|
| Spec | Explicit user/tracker Epic, otherwise none |
| Plan | Current Spec file/issue |
| Todo | Plan file/issue without P<N>; if omitted, use Spec, then an explicitly given Epic, otherwise `none (单票小改动)` |

Infer missing legacy Parent only from explicit Plan/Spec and label the inference, never from similar titles/numbers/directories. Fill ownership in touched artifacts rather than bulk-rewriting history. A historical ticket continued by a new version is not its ownership parent.

### Local files

- Retain flat spec*.md, existing plan.md and issues/<NN>-<slug>.md. New peer scopes may use plans/<scope-slug>.md; do not move old artifacts or create P<N> package directories merely to mimic the tree. Metadata paths remain feature-relative; Markdown links resolve from their containing file.
- Create/update feature INDEX when the first Spec or Todo is saved, then synchronize touched relationships. List every current Plan with its own nested Todos and applicable Spec provenance, preserving history. Continue Todo numbering across the feature to avoid per-Plan collisions. P<N> is internal grouping, not another parent or a substitute for a separate Plan.
- INDEX Markdown links are relative to INDEX and must locate real files. Missing/intentionally omitted artifacts use none/reason rather than placeholders or broken links. Label historical versions/tickets; all tickets on one Plan are not necessarily the current execution layer.
- INDEX is navigation/current-version provenance, not copied plan text, ticket Status, or approval. Read state from originals. Reread relevant references before writes and report concurrent conflicts rather than overwriting.
- Root `.scratch/README.md` links features to their INDEX, preserving other notes. Legacy work without INDEX may link its directory. Queries do not create indexes.

Example containing actual existing artifacts only:

```markdown
# Feature: export
**当前版本**: [spec-v2.md](spec-v2.md)
Plan: [plan.md](plan.md)

## 层级
- [Spec v2](spec-v2.md)（当前）
  - [Plan](plan.md)
    - [Todo 04 JSON 导出](issues/04-json.md) — P2 / Spec v2
    - [Todo 01 CSV 导出](issues/01-csv.md) — P1 / Spec v1（历史）

## 演进
- [v1](spec.md)：CSV 导出
- [v2](spec-v2.md)：增加 JSON 格式
```

### GitHub

- Create/verify native parent/sub-issue relationships matching Parent. Reuse the same parent and issue on retries. Retain body references; Markdown backlinks alone are not native synchronization.
- Titles use `[Spec]`, `[Plan]`, `[Todo]`; type-label defaults are `spec`, `plan`, `todo` (Epic only when it exists). Reuse explicitly configured equivalent type labels, except legacy `ticket` is only a compatibility alias for existing work. Create needed missing labels when permitted; otherwise retain title classification and report unsynchronized labels, without recreating issues.
- Inspect actual CLI create/edit/view help. If hierarchy flags are absent, use gh api or an available connector for the [Sub-issues API](https://docs.github.com/en/rest/issues/sub-issues). `sub_issue_id` is the actual numeric issue **id**, not its issue number.
- Read the child parent and destination child list before adding. Authentication errors, 403, or unexplained 404 are not no-parent evidence. Do not force-replace a foreign parent; report expected/actual. Only the verified same-feature Spec migration below may reparent. After a failed write, read actual results and report the unsynchronized relationship/cause; do not loop or duplicate issues.
- Projects is optional. Use the specified/configured Project; otherwise do not create one or block ordinary Issues work. Table **View → Show hierarchy** can show Parent issue/Sub-issue progress. Repository Issues remains the classification/filtering view; do not promise the same tree. See [hierarchy view](https://github.blog/changelog/2026-03-19-hierarchy-view-in-github-projects-is-now-generally-available/).
- GitLab retains logical fields and its own conventions. Discover actual platform/tool permissions; do not apply GitHub endpoints blindly. Report unsupported native display while keeping body provenance.

### Version evolution and state

`/flow-amend` preserves each existing Plan's identity and changes only affected scopes. The current Spec/INDEX lists all applicable Plans, including explicitly unchanged scopes. Update affected Plan Spec/Parent references; navigation-only updates to other Plans are allowed when needed but do not reset their decisions, approval, acceptance or completed work. Preserve historical Todo versions/states and attach new Todos to their actual owning Plan.

If Spec versions share one issue, native Plan parenting is unchanged. If a version gets a new Spec issue, migrate current Plan navigation only after verifying each old parent equals the prior Spec of this same feature, the move is authorized, and a fresh read shows no concurrent change. Historical Todos keep their owner/version. An explicitly unchanged Plan may retain its earlier binding with current-scope provenance; report the actual native relationship rather than pretending every parent migrated.

Tree shape, child-close ratios, and folder layout prove neither approach approval nor functional acceptance. Do not close parents, promote state, or release dependencies on that basis. `/flow-status` reports actual version/state/relationship conflicts without repairing them.

<a name="ticket-字段"></a>
## Todo fields

One file/issue per ticket. Minimal template:

```markdown
## [Todo] 02: 评论数据模型与基础 API
Status: ready
Parent: plan.md
Spec: spec.md
Plan: plan.md#P2
Blocked by: 01-prefactor

**描述**: 创建和查询评论
**测试 seam**: HTTP API
**验证方式**: 在已有 API 测试文件中补充行为用例，复用 fixtures，先复现失败再实现
**测试用例**: 创建成功、查询列表、未登录返回 401
**验收标准**:
- 创建和查询接口符合约定
```

- Parent is direct ownership, not a blocker; an absent Plan does not force creating one.
- Spec identifies its version. Local paths are feature-relative; remote references identify the authoritative version.
- Plan identifies the file/issue plus package, independently of Spec provenance.
- Blocked by lists ticket numbers/names/issue references, or none, including explicit external conditions.
- Small changes may declare Spec/Plan none with reasons. Put omitted boundaries, technical decisions, seams, and criteria in the confirmed ticket rather than requesting nonexistent documents.
- `**验证方式**` records strategy, existing test locations, or commands. For old tickets choose/record applicable validation; non-runtime changes may mark the seam inapplicable with a reason.
- Read legacy `**来源**: plan P<N>` / `**来源**: spec-vN`, `**依赖**:`, and `**阻塞**:` by meaning. Report conflicting repeated fields rather than guessing or ignoring blockers. Normalize only touched fields in new work.

<a name="验证方式与测试组织"></a>
## Validation and test organization

Discover the framework, commands, matching seams/tests, and fixtures before selecting checks by change semantics, not just extension. Preserve checks explicitly required by the Spec/plan/ticket/user; failure, missing setup, or file-count concerns do not justify downgrading them.

| Change | Default validation |
|--------|--------------------|
| Behavior, API contracts, bugs | Reuse/extend meaningful behavior tests at the agreed seam; observe failure before implementation, reusing an accurate existing failure |
| Pure refactor | Relevant regression before/after; add characterization if coverage is insufficient, not artificial failures |
| Pure docs/comments/wording without contract changes | Check links, formatting, rendering, commands, or content; no source-keyword self-tests |
| Config/build/dependencies | Applicable parse/type/build/controlled smoke checks; add behavioral regression for actual logic or defects |
| Styles/layout only | Actual required viewports/states and existing visual coverage; behavior changes still need behavior checks |

Skill instructions or workflow documents that change decisions need observable behavior validation, such as isolated scenarios. Markdown extension alone does not make keyword checks sufficient.

**Test organization:** Reuse test files and fixtures, parameterizing/subtesting related cases. New files need a missing independent boundary or project convention, with a reason; impose neither a file-count ceiling nor one giant file. Reuse coverage that already demonstrates acceptance. Additional unit/service/API/E2E layers should cover distinct risks rather than duplicate each other. Assert observable behavior/contracts, not implementation copies or string presence; fewer files must not weaken checks.

**Regression versus probes:** Keep valuable regressions in the maintained suite. Put one-off probes/harnesses in system temp storage and record results. Remove only this run's temporary artifacts, not preexisting tests. When moving a probe into maintained tests, establish equivalent coverage first. Report chosen strategy, reused/new locations, actual commands/results, and justified exclusions; failed/unrun mandatory checks remain blockers.

<a name="状态与依赖"></a>
## States and dependencies

New trackers default to ready/claimed/resolved/parked and `ready → claimed → resolved`:

| State | Meaning | Releases ticket dependencies |
|-------|---------|-------------------------------|
| ready | Available | No |
| claimed | Executing, or required checks failed/unrun | No |
| resolved | Implementation, required engineering checks, review, and deliverables pass; auto-close without human functional acceptance or Git confirmation | Yes |
| parked | Awaiting an external condition/decision | No |

- The main session checks evidence and resolves automatically; executing children only report. Keep failed/unrun checks, incomplete scope, or blocking review findings claimed (or declared parked for an external block). Do not transfer engineering failures into upper acceptance to justify closing.
- Locally Status resolved plus evidence is closure. Remotely synchronize the body, close, and reread state. GitHub may use [`gh issue close <引用> --reason completed`](https://cli.github.com/manual/gh_issue_close) or a supported equivalent. On permission/network failure, distinguish engineering complete from native closure unsynchronized; never claim success, reimplement passed code, or retry indefinitely.
- Resolved releases ticket dependencies, but explicit external validation/publication/delivery conditions remain separate. Deferred commits do not block closure; record branch/worktree and committed/uncommitted facts rather than calling closure publication.
- Code-complete is legacy compatibility only. Preserve its declared dependency semantics and require evidence. Before adopting this flow, align the current repository's completion declaration; then verify this ticket and finish it. Do not bulk-migrate history or close from the old value alone. `/flow-status` never writes.
- Commit/push still needs explicit authorization; its checkpoint is not a ticket-closure gate. A later cleanup/regression may reopen affected engineering tickets with reasons and dependency review, not merely because human functional acceptance is pending.

<a name="功能验收与票级关闭"></a>
## Functional acceptance and ticket closure

- Human acceptance for a Todo belongs to its owning Plan's scope, otherwise the current Spec. Multiple Plans own separate acceptance subsets and may be reviewed/accepted independently; one blocked Plan does not undo another's accepted scope. Each acceptance item has one mutable owner. The Spec links these entries and derives overall coverage; retain genuinely Spec-wide integration/acceptance items there without duplicating Plan-owned states. When both are intentionally omitted, keep human follow-up in an existing feature record/report.
- Each owner records `Acceptance: pending / accepted / changes-requested`, its scoped items, Todo links and actual user evidence. Technical approval, a requested Plan count and Git authorization are not functional acceptance. Transfer only the corresponding Spec-owned items when a Plan takes ownership; preserve records and leave links, not duplicate independent states. A user review may cover several Plans explicitly without requiring a separate conversation per Plan.
- Hand off human experience/functional-device checks with their source tickets and unverified facts. Do not move failed/unrun automated, integration, or explicitly required engineering-device checks upward under another name. Report engineering and human acceptance independently.
- For each Plan, its own Todos resolved means scoped engineering completion, not automatic acceptance or peer/Spec closure. Only actual user functional acceptance plus relevant engineering completion records accepted at that owner. Close/verify that scoped acceptance issue separately; the whole Spec still needs full coverage, distinct global checks and applicable user/closure authority.
- User-reported issues record changes-requested at the affected scope. Add scoped follow-on work or reopen a specific regression, not all historical Todos. /flow-amend resets only changed acceptance scope while retaining prior evidence; verify unchanged-scope provenance before carrying other Plans forward. Counts or all child issues closing do not alone authorize closing the whole Spec.
- `/flow-status` reports engineering progress, native closure sync, and acceptance separately. Missing Acceptance/evidence remains unknown; child counts, approach approval, Git activity, or closed parents do not prove user acceptance. INDEX remains navigation only.

<a name="改动规模与输入"></a>
## Change size and inputs

Regular features use Spec for product boundaries, approved plan for technical approach, and tickets for execution/engineering criteria. A confirmed small ticket may intentionally omit Spec/Plan and contain those decisions itself; skip absent plan-anchor checks but preserve required validation. Tiny unticketed work still leaves an existing-document/changelog record rather than requiring the full pipeline.

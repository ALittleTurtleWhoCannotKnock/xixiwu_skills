# PI-Bot integration

This guide is based on [vsd269/PI-Bot](https://github.com/vsd269/PI-Bot), source revision `da54ae7f1cab7739691a3c4fc638101fa01fe120` (manifest 0.3.93). It is a **PI Desktop plugin**, not the Pi coding CLI targeted by `install.sh pi`. CLI installation does not import skills or register worker roles inside PI Desktop.

## Five-Bot project team

For stage specialists, use the [importable team template](../assets/pi-bot-team.template.json). It contains five ordinary `Worker` Bots: Flow, Requirements, Planning (Plan plus Todo), Development, and Verification. They use private chats, with no group or schedule created. The default Chief, if present, can stay; it is not a sixth required workflow role. Even the Flow Bot stays an execution-capable Worker so it can read project state, save its checkpoint and ask the user without planner-only restrictions.

1. Replace `__PROJECT_KEY__` throughout a copy of the JSON with one unique project prefix such as `A`. Keep another prefix for another project. Do not insert absolute paths into the import file: PI-Bot sanitizes them during template parsing.
2. Open Settings → About PI Bot → PI extensions → Backup and restore → Team configuration template. Select the JSON, preview the five names/instructions, then explicitly confirm creation. Depending on the installed UI, Backup and restore may also be a direct settings entry.
3. After import, open each Bot's name/details → Edit conversation. Set all five working directories to the same actual project repository, and choose the user's available model/default model. The import intentionally leaves model account, directory, permissions and attached capabilities unset. It does not start tasks.
4. In the Flow Bot's instructions, replace `__PROJECT_ROOT__` with that repository and `__SKILLS_ROOT__` with the full skill checkout path. Do this **after import**; importing filled local paths would redact them. Stage workers receive both source paths in their assignments and need native read access to them.
5. Keep these collaborating Bots out of PI-Bot's **Private Bot privacy mode**: that feature blocks automatic cross-Bot messaging/results. Ordinary private chats are different from the privacy flag. Do not change existing privacy settings automatically; use appropriately configured members.
6. Verify one actual member per team marker/role, its exact name/ID and directory. A repeated import adds new Bots and may rename duplicates; it does not update the old team or repair textual role bindings. Resolve duplicates before dispatching work.
7. Complete missing project workflow settings through flow-init, then send new work only to the Flow Bot. Its native tools must actually be allowed to read/write the required project artifacts, execute necessary commands, and access a supported browser for browser verification. Use applicable PI approval, not a blanket permission change.

The Skill names in `skillReferences` are informational import references; PI-Bot does not automatically attach the Skill library. These instructions deliberately read the complete original source checkout to preserve resources. The JSON is a PI-Bot adapter artifact; [team-mode.md](team-mode.md) remains the host-neutral protocol.

Before assigning a real feature, ask the Flow Bot to perform a **read-only readiness check**: identify its four actual teammates, inspect visible directory settings, read the main/team and stage source entries, check the project tracker/language/model setup and actual browser capability, and list missing settings. The current `list_bots` result does not expose saved working-directory fields; report those as unverified unless observed through another supported mechanism. If the user explicitly requests it, bounded read-only worker checks can establish each actual session directory/source access. Do not infer readiness from names or instructions alone. The check must not start a feature, run migrations, change Bot settings or manufacture Spec approval.

Source references: [team template parser/creation](https://github.com/vsd269/PI-Bot/blob/da54ae7f1cab7739691a3c4fc638101fa01fe120/src/team-templates.js), [template UI](https://github.com/vsd269/PI-Bot/blob/da54ae7f1cab7739691a3c4fc638101fa01fe120/renderer/work-settings.mjs), [Bot editing](https://github.com/vsd269/PI-Bot/blob/da54ae7f1cab7739691a3c4fc638101fa01fe120/renderer/app.mjs), and [privacy restrictions](https://github.com/vsd269/PI-Bot/blob/da54ae7f1cab7739691a3c4fc638101fa01fe120/src/privacy.js).

## Start with one execution-capable Bot

This section is the inline starting option. For the requested specialist setup, use the host-neutral [team protocol](team-mode.md) and bind its roles to actual PI-Bot members. Keep this file as a host adapter reference; it does not define the workflow or require the same role topology on other platforms.

Use a Worker, or an Administrator in private chat with `agentMode: agent`, and set its working directory to the actual target project through the host UI while idle. Keep the configured model and PI permissions. An Administrator in planner mode cannot execute tools, and a group administrator cannot act as its own group execution worker; putting flow-run in that planner alone will not implement a feature.

For the first integration, explicitly select inline execution for this run. Keep the project's existing default unchanged. PI-Bot's `message_bot` teammates and the CLI-generated `_agents` registrations are different mechanisms; do not assume the CLI roles already exist as PI-Bot members.

See the actual routing in [team.js](https://github.com/vsd269/PI-Bot/blob/da54ae7f1cab7739691a3c4fc638101fa01fe120/src/team.js).

## Preserve the skill source layout

Keep a full checkout of this skill repository at a stable absolute path readable under the Bot's native PI permissions. The target project and skill checkout may be separate directories; verify access to both rather than copying project preferences or widening permissions automatically.

PI-Bot's importer creates a separate bundle ID/directory for each discovered `SKILL.md`. It includes resources below that skill root, not sibling skills or the repository-level `_agents` directory. Consequently, importing our workflow skills as separate capabilities does not preserve links such as `../flow-plan/SKILL.md` and `../_agents/workflow-contract.md`. Importing only the flow-run folder also omits its dependencies. The importer rejects resource paths containing `..`; a capability pack groups assignments, not shared filesystem roots. See [skill-import.js](https://github.com/vsd269/PI-Bot/blob/da54ae7f1cab7739691a3c4fc638101fa01fe120/src/skill-import.js) and [capabilities.js](https://github.com/vsd269/PI-Bot/blob/da54ae7f1cab7739691a3c4fc638101fa01fe120/src/capabilities.js).

Use the Bot's instructions as a source entry point first. Replace both placeholders below with the real absolute paths, and combine this with the [user-authorized operating policy](bot-setup.md):

```text
Target project: <absolute-project-directory>
Skill source checkout: <absolute-skills-directory>
For a feature request or execution continuation, first use the native file tool to read
<absolute-skills-directory>/flow-run/SKILL.md in full, then follow its referenced skills.
Resolve each relative resource reference from the source file containing it, not from
the Bot's working directory or an imported capability's UUID directory.
Use inline execution for this run; do not alter the project's saved execution mode.
If source files are inaccessible, report the exact access problem; do not guess their rules.
Obtain human Spec confirmation; after that, Plan review and Todo splitting are delegated
within the confirmed Spec, followed by implementation and applicable verification.
```

If a capability-library entry is desired later, import a small launcher containing this source-entry instruction and assign it to the executing Bot. It must still read the full source checkout through an allowed native file tool; a truncated capability summary is not the workflow. This guide does not create or install that launcher or a flattened export bundle.

## Bind Spec confirmation to an actual reply

At the Spec gate, save the source reference/version and pending question in run.md. Use the available `ask_user` tool with the Spec reference and a self-contained confirmation question; use its detail/options fields for the review summary or requested changes. Displaying a static HTML card alone does not request approval.

Save the returned question reference and end the dependent work. PI-Bot returns the answer as a new assignment, not as a blocking call result. On that assignment, read the complete answer and the current source/checkpoint; verify that it confirms the pending Spec content. A request for changes revises the Spec and returns to confirmation. A dismissed question, a finished turn, or the host merely resuming is not approval.

For a missing conversation reference, use the Bot's own chat/history tools within their visibility limits. Do not infer user approval from another worker's report. Tool schemas and availability should be discovered in the installed version; see [tools.js](https://github.com/vsd269/PI-Bot/blob/da54ae7f1cab7739691a3c4fc638101fa01fe120/src/tools.js) and [questions.js](https://github.com/vsd269/PI-Bot/blob/da54ae7f1cab7739691a3c4fc638101fa01fe120/src/questions.js).

## Separate host execution from engineering evidence

PI-Bot's native job `completed` means the turn ended, including a turn that asked a Spec question. It is not the workflow Todo's `Status: resolved` or the Plan's human `Acceptance: accepted`. Read actual artifacts and validation results before advancing. The run.md checkpoint is coordination data; PI-Bot job/session records remain host execution data, not another Spec/Plan/Todo tracker.

For interrupted or uncertain work, inspect the native session, job/receipt, artifacts, and previous outputs before any retry. The recovery center's continue/retry operations require host confirmation and may repeat earlier side effects. The skill cannot waive this host approval or promise tool-level exactly-once recovery. Prefer resuming the existing Bot conversation after a normal Spec reply. See [recovery.js](https://github.com/vsd269/PI-Bot/blob/da54ae7f1cab7739691a3c4fc638101fa01fe120/src/recovery.js) and the [execution architecture](https://github.com/vsd269/PI-Bot/blob/da54ae7f1cab7739691a3c4fc638101fa01fe120/docs/EXECUTION_ENGINE_ARCHITECTURE.md).

If later using multiple Bots, keep one workflow owner and delegate only concrete, self-contained work to existing capable workers. Use stable request IDs for the same dispatch, receive the automatic return, and inspect outputs; do not poll `check_delegation` in a loop or treat an accepted dispatch as tested completion. Do not change group membership, permissions, models, schedules, or other Bot instructions just to run flow-run.

## Browser and host limits

Discover the actual granted browser tool before flow-e2e. PI-Bot exposes `bot_browser` with page reads and node-based interactions, not necessarily the locator API available in another CLI. Inspect fresh elements and follow that tool's schema; keep the user-path outcomes and required checks unchanged.

At the pinned source revision, the isolated browser executable search uses Windows Edge/Chrome paths. Do not assume it works on macOS merely because PI Desktop runs there. Use an actually available native browser or an explicitly configured MCP when permitted; otherwise mark browser verification blocked/unrun. The [browser implementation](https://github.com/vsd269/PI-Bot/blob/da54ae7f1cab7739691a3c4fc638101fa01fe120/src/bot-browser.js) and [registered tool schema](https://github.com/vsd269/PI-Bot/blob/da54ae7f1cab7739691a3c4fc638101fa01fe120/src/tools.js) are the reference.

Keep PI Desktop running and the plugin enabled for host schedules/replies. Unchanged blockers must not become a periodic retry loop. This is a source-based integration guide; actual PI Desktop model/tool approvals, user reply delivery, project writes, and browser execution still require a real host smoke test. Reading source or passing an importer probe is not proof of that live integration.

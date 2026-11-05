# Multica adapter

Source baseline: [multica-ai/multica](https://github.com/multica-ai/multica), revision `3c5c8b245359b9b8e913a47f97211f2a3426f149`. This is optional host guidance; logical roles and stage methods remain host-neutral.

## Install methods and bind identity separately

Use the self-contained `dev-flow.skill` distribution with `multica skill import --file`, then add its returned skill ID to the actual agent. A local `npx skills add` or CLI skill symlink is not a Multica workspace import. Workspace packages are snapshots; source updates do not refresh archive imports automatically.

The display description does not enter the execution prompt. Put the selected role in the agent's persistent **Instructions** field. The repository's Multica install target imports one package, adds that binding without deleting other skills, and maintains a marked role-instructions block while preserving custom instructions outside it. Review old custom rules for contradictions; never claim the package alone reconfigured the agent.

The `flow` role is coordinator-only even when the method library includes implementation guides. Missing specialists do not enable inline coding. Other profiles are Requirements, Planning, Development and Verification. Agent Access is an invocation allowlist, not a command/filesystem permission boundary. The official [configuration guide](https://github.com/multica-ai/multica/blob/3c5c8b245359b9b8e913a47f97211f2a3426f149/apps/docs/content/docs/agents-create.zh.mdx) and [security model](https://github.com/multica-ai/multica/blob/3c5c8b245359b9b8e913a47f97211f2a3426f149/apps/docs/content/docs/security-model.zh.mdx) describe these different layers.

## Use the actual host dispatch and return contract

For a five-role squad, use the [Chinese squad policy template](../assets/multica-squad.instructions.zh-CN.md). Replace its five role placeholders with actual, verified workspace members and select the Flow Agent as leader. Create only the intended squad, add the four specialists with descriptive roster roles, save the rendered instructions, and read back leader/membership/instructions before assigning work. The leader normally becomes a member automatically; verify this rather than adding duplicates. The template configures routing and confirmation policy, not tool permissions or scheduled execution.

Read Multica's injected runtime brief and actual CLI help. During a managed run, use the executable supplied in `MULTICA_CLI_PATH` as instructed by that brief rather than choosing a possibly older CLI from PATH. Use the current project/workspace and actual agent/squad IDs; do not apply PI-Bot's message_bot or ask_user APIs here.

For persistent multi-agent issue workflows, a configured Multica Squad supplies a native coordinator path: designate the Flow agent as leader and bind the specialists as members. The leader delegates with the exact mention links provided by the squad roster, records its squad activity, and follows the host's re-triggering protocol when members report. Plain `@name` text is not sufficient. Do not create a squad, change Access, or add members merely because the method library is installed; ask for missing bindings or use an already authorized team.

Choose one dispatch trigger for a unit of work: a delegation mention on the parent issue **or** assignment of its child issue. Combining both can launch the same work twice. Stage parking/promotion and dependency checks must follow the actual tracker and host protocol, not assumed local status values. Human Spec confirmation stays with the Flow agent; a squad/member update cannot supply it.

Generic background tool handles have a different lifetime: Multica's ordinary top-level run ends when its turn exits and does not provide a background-completion wakeup. Do not launch run-owned work in the background and yield while claiming its result will resume you. Use a supported foreground call that actually collects results, or an explicitly configured persistent issue wakeup/native Squad mechanism. Follow host-required recovery and activity/status rules; a generic skill cannot waive them.

These behaviors are described in the [Squad guide](https://github.com/multica-ai/multica/blob/3c5c8b245359b9b8e913a47f97211f2a3426f149/apps/docs/content/docs/squads.mdx) and [runtime brief](https://github.com/multica-ai/multica/blob/3c5c8b245359b9b8e913a47f97211f2a3426f149/server/internal/daemon/execenv/runtime_config_sections.go). Inspect actual artifacts and check results regardless of task/issue completion messages. A private capability-introduction chat is not evidence that a Squad or tool restriction is configured.

## Environment boundary

Role instructions constrain intended behavior; they do not remove coding tools from the underlying harness. Multica's documented default runtime grants the daemon user's filesystem privileges and does not promise a filesystem sandbox. If a deployment needs a coordinator that cannot write application code even if instructions are ignored, arrange an actual host/runtime/OS boundary and verify it independently. Do not describe prompt compliance, disabled Skill discovery, or Access settings as that boundary.

This repository does not silently change sandbox, approval, model, token, MCP or OS settings. Source review, archive validation and simulated CLI tests do not prove a live workspace's enforcement or end-to-end Squad operation.

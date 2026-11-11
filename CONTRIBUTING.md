# Contributing

**English** | [简体中文](./CONTRIBUTING.zh-CN.md)

## Before opening a PR

1. Change only the relevant skill or script. Do not reorder unrelated files.
2. Exercise the change in a real project. Describe what changed, which CLI you used to verify it, and any side effects in the PR.
3. Changes to `install.sh` or `adapters/` must include `--dry-run` output.

## Documentation languages

Maintain English `.md` and Chinese `.zh-CN.md` versions of the project overview, user guide, architecture, and contribution guide, with language-switch links at the top. When features, installation commands, or workflow behavior change, update the corresponding English and Chinese documentation in the same PR. Keep commands, examples, and rules consistent. Existing skill files and shared prompts remain the authoritative execution sources.

## Changes we do not accept

- Remote script execution in any form, including `curl | bash`, `iwr | iex`, or downloading a script, running `chmod +x`, and executing it.
- Reading credentials from `~/.ssh`, `~/.aws`, or environment variables, or exfiltrating data in any form.
- Unrelated system modifications inserted into skill instructions.
- Binary files without a documented source.

## Why these rules are strict

AI agents execute these files as instructions; they are not just explanatory documents. A seemingly harmless command can run on a developer's actual machine.

## Contribution process

Fork → branch → PR → maintainer review → merge. The `main` branch is protected; direct pushes are rejected.

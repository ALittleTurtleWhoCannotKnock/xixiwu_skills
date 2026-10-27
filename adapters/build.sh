#!/usr/bin/env bash
# 从 _agents/*.prompt.md 生成各工具的 agent 文件。
# 用法: ./adapters/build.sh [pi|claude-code|codex|all] [--project-root DIR] [--output-dir DIR]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/_agents"

target="all"
project_root="$ROOT"
output_dir=""
if [ "$#" -gt 0 ] && [[ "$1" != --* ]]; then
  target="$1"
  shift
fi
while [ "$#" -gt 0 ]; do
  case "$1" in
    --project-root|--output-dir)
      if [ "$#" -lt 2 ] || [ -z "$2" ] || [[ "$2" == --* ]]; then
        echo "参数 $1 需要目录路径" >&2
        exit 1
      fi
      if [ "$1" = "--project-root" ]; then project_root="$2"; else output_dir="$2"; fi
      shift 2
      ;;
    *) echo "未知参数: $1" >&2; exit 1 ;;
  esac
done
case "$target" in
  pi|claude-code|codex|all) ;;
  *) echo "未知目标: $target (用 pi|claude-code|codex|all)" >&2; exit 1 ;;
esac
project_root="$(cd "$project_root" && pwd)"

if [ "$target" = "codex" ]; then
  echo "codex: 见 $ROOT/adapters/codex/README.md（使用角色 prompt，无需生成 agent 文件）"
  exit 0
fi

# Only use a model explicitly selected by the user; there is no built-in model.
MODEL="${DEV_FLOW_MODEL:-}"
EXEC_MODE_FILE="$project_root/docs/agents/execution-mode.md"
if [ -z "$MODEL" ] && [ -f "$EXEC_MODE_FILE" ]; then
  MODEL=$(grep -E "^\**基础模型\**:" "$EXEC_MODE_FILE" 2>/dev/null | sed -E 's/^\**基础模型\**:[[:space:]]*//' | tr -d '*' | xargs || echo "")
fi

# ---- 每个 agent 的工具级配置（thinking / 工具白名单）----
# 单一事实源是这里的配置 + _agents 的 prompt。

build_pi () {
  local out="$HOME/.pi/agent/agents"
  local model_field=""
  if [ -n "$MODEL" ]; then model_field="model: $MODEL"$'\n'; fi
  if [ -n "$output_dir" ]; then out="$output_dir/pi"; fi
  mkdir -p "$out"
  _gen "$1" "$out/$1.md" "$(cat <<EOF
---
name: $1
description: $2
${model_field}thinking: $3
systemPromptMode: replace
inheritSkills: false
tools: read, grep, find, ls, bash, edit, write
defaultContext: fork
defaultProgress: true
---
EOF
)"
  echo "pi: $out/$1.md"
}

build_claude () {
  local out="$HOME/.claude/agents"
  if [ -n "$output_dir" ]; then out="$output_dir/claude-code"; fi
  mkdir -p "$out"
  _gen "$1" "$out/$1.md" "$(cat <<EOF
---
name: $1
description: $2
tools: Read, Grep, Glob, Bash, Edit, Write
---
EOF
)"
  echo "claude-code: $out/$1.md"
}

_gen () { # name, dest, frontmatter
  local name="$1" dest="$2" fm="$3"
  {
    printf '%s\n\n' "$fm"
    cat "$SRC/$name.prompt.md"
    if [ "$name" = "implementer" ]; then
      printf '\n\n'
      cat "$SRC/workflow-contract.md"
    fi
  } > "$dest"
}

_desc () { # name -> description
  case "$1" in
    exporter)        echo "Session export agent: faithful Markdown transcript + raw JSONL archive, pure format conversion." ;;
    simplifier)      echo "Pre-commit cleanup agent: reuse/quality/efficiency fixes within a bounded diff scope." ;;
    contract-writer) echo "API contract writer: precise structured contract fragment from just-written code and tests." ;;
    implementer)     echo "Autonomous implementation and validation subagent for one fully-specified ticket." ;;
    scout)           echo "Fast codebase recon: compressed context brief (entry points, key code, existing seams, start-here) for downstream agents." ;;
  esac
}

_think () { # name -> thinking level
  case "$1" in
    exporter)        echo "low" ;;
    simplifier)      echo "medium" ;;
    contract-writer) echo "medium" ;;
    implementer)     echo "high" ;;
    scout)           echo "low" ;;
  esac
}

agents="exporter simplifier contract-writer implementer scout"

for a in $agents; do
  d="$(_desc "$a")"; t="$(_think "$a")"
  case "$target" in
    pi)          build_pi "$a" "$d" "$t" ;;
    claude-code) build_claude "$a" "$d" ;;
    all)
      build_pi "$a" "$d" "$t"
      build_claude "$a" "$d"
      ;;
    *) echo "未知目标: $target (用 pi|claude-code|codex|all)" >&2; exit 1 ;;
  esac
done

if [ "$target" = "all" ]; then
  echo "codex: 见 $ROOT/adapters/codex/README.md（使用角色 prompt，无需生成 agent 文件）"
fi

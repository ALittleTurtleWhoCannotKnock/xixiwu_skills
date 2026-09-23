#!/usr/bin/env bash
# 从 _agents/*.prompt.md 生成各工具的 agent 文件。
# 用法: ./adapters/build.sh [pi|claude-code|codex|all]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/_agents"

# ---- 模型配置（优先级：环境变量 > execution-mode.md > 默认值）----
# 1. 环境变量 DEV_FLOW_MODEL（最高优先级，用于 CI/临时覆盖）
# 2. docs/agents/execution-mode.md 中的"基础模型"字段（初始化时配置）
# 3. 默认值 anthropic/claude-sonnet-4

DEFAULT_MODEL="anthropic/claude-sonnet-4"

# 尝试从 execution-mode.md 读取基础模型
EXEC_MODE_FILE="docs/agents/execution-mode.md"
if [ -f "$EXEC_MODE_FILE" ]; then
  # 提取"基础模型": xxx 或 **基础模型**: xxx 后的模型名
  CONFIG_MODEL=$(grep -E "^\**基础模型\**:" "$EXEC_MODE_FILE" 2>/dev/null | sed -E 's/^\**基础模型\**:[[:space:]]*//' | tr -d '*' | xargs || echo "")
  if [ -n "$CONFIG_MODEL" ]; then
    DEFAULT_MODEL="$CONFIG_MODEL"
  fi
fi

MODEL="${DEV_FLOW_MODEL:-$DEFAULT_MODEL}"

# ---- 每个 agent 的工具级配置（模型 / thinking / 工具白名单）----
# 单一事实源是这里的配置 + _agents 的 prompt。

target="${1:-all}"

build_pi () {
  local out="$HOME/.pi/agent/agents"
  mkdir -p "$out"
  _gen "$1" "$out/$1.md" "$(cat <<EOF
---
name: $1
description: $2
model: $MODEL
thinking: $3
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
  { printf '%s\n\n' "$fm"; cat "$SRC/$name.prompt.md"; } > "$dest"
}

_desc () { # name -> description
  case "$1" in
    exporter)        echo "Session export agent: faithful Markdown transcript + raw JSONL archive, pure format conversion." ;;
    simplifier)      echo "Pre-commit cleanup agent: reuse/quality/efficiency fixes within a bounded diff scope." ;;
    contract-writer) echo "API contract writer: precise structured contract fragment from just-written code and tests." ;;
    implementer)     echo "Autonomous TDD execution subagent for one fully-specified ticket." ;;
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

if [ "$target" = "codex" ] || [ "$target" = "all" ]; then
  echo "codex: 见 adapters/codex/README.md（Codex 无独立 agent 文件，走 AGENTS.md + dispatch）"
fi

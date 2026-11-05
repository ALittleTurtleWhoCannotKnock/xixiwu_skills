"""Import one workspace Skill and explicitly bind a permanent agent role."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

from package_bundle import ROOT, build_bundle

BEGIN = "<!-- dev-flow-role:begin -->"
END = "<!-- dev-flow-role:end -->"
ROLES = ("flow", "requirements", "planning", "development", "verification")


def role_instructions(existing, role):
    block = BEGIN + "\n" + (ROOT / "roles" / (role + ".md")).read_text().strip() + "\n" + END
    if BEGIN in existing or END in existing:
        if existing.count(BEGIN) != 1 or existing.count(END) != 1 or existing.index(BEGIN) > existing.index(END):
            raise ValueError("现有角色区块不完整，未覆盖指令；请先整理 dev-flow-role 标记。")
        start, end = existing.index(BEGIN), existing.index(END) + len(END)
        return existing[:start] + block + existing[end:]
    return existing + ("\n\n" if existing else "") + block


def cli(args, workspace=None):
    command = ["multica", *(["--workspace-id", workspace] if workspace else []), *args, "--output", "json"]
    run = subprocess.run(command, capture_output=True, text=True, check=False)
    if run.returncode:
        raise ValueError(f"Multica 命令失败（{' '.join(args[:3])}）：{run.stderr.strip() or '请检查 CLI 登录与工作区。'}")
    return json.loads(run.stdout)


def main():
    parser = argparse.ArgumentParser(description="导入统一技能包；指定智能体时绑定独立的角色指令。")
    parser.add_argument("--agent-id", help="要配置的实际智能体 ID；不会按名称猜测或创建智能体")
    parser.add_argument("--role", choices=ROLES)
    parser.add_argument("--workspace-id", help="只导入技能时的工作区；配置智能体时必须匹配该智能体")
    parser.add_argument("--on-conflict", choices=("fail", "overwrite"), default="fail",
                        help="角色按 dev-flow 定位统一技能；仅支持保留该名称的导入策略")
    parser.add_argument("--dry-run", action="store_true", help="构建并预览，不导入、不绑定、不改指令")
    args = parser.parse_args()
    if bool(args.agent_id) != bool(args.role):
        parser.error("--agent-id 与 --role 必须一起提供；省略两者时只导入统一技能。")
    agent = cli(["agent", "get", args.agent_id], args.workspace_id) if args.agent_id else None
    workspace = agent.get("workspace_id") if agent else args.workspace_id
    if agent and (not workspace or args.workspace_id and args.workspace_id != workspace):
        parser.error("智能体工作区缺失或与 --workspace-id 不一致，未修改配置。")
    existing = (agent.get("instructions") or "") if agent else ""
    instructions = role_instructions(existing, args.role) if agent else None
    with tempfile.TemporaryDirectory(prefix="dev-flow-multica-") as temp:
        bundle = build_bundle(Path(temp) / "dev-flow.skill")
        print(f"统一技能：dev-flow；归档大小 {bundle.stat().st_size} 字节")
        if agent:
            print(f"目标智能体：{agent.get('name', args.agent_id)}；角色：{args.role}；工作区：{workspace}")
        if args.dry_run:
            print("预览：导入一个自包含 Skill。" + ("追加绑定，保留其他技能；只更新托管角色指令区块。" if agent else "未指定智能体，不改任何角色配置。"))
            if instructions:
                print((ROOT / "roles" / (args.role + ".md")).read_text())
            print("未写入 Multica；角色指令不等于工具或文件系统权限限制。")
            return
        result = cli(["skill", "import", "--file", str(bundle), "--on-conflict", args.on_conflict], workspace)
        if result.get("status") not in ("created", "updated") or not result.get("skill", {}).get("id"):
            raise ValueError(f"技能未完成导入：{result.get('status', 'unknown')}；未绑定或改角色。")
        skill_id = result["skill"]["id"]
        print(f"技能已导入：{skill_id}")
        if not agent:
            return
        cli(["agent", "skills", "add", args.agent_id, "--skill-ids", skill_id], workspace)
        attached = cli(["agent", "skills", "list", args.agent_id], workspace)
        if not any(item.get("id") == skill_id or item.get("skill_id") == skill_id for item in attached):
            raise ValueError("技能绑定未核实，未修改角色指令。")
        current = cli(["agent", "get", args.agent_id], workspace)
        if (current.get("instructions") or "") != existing:
            raise ValueError("智能体指令在安装期间已变化；技能已绑定，角色未覆盖，请重新预览。")
        if instructions != existing:
            backup_root = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share"))) / "dev-flow-skills/backups"
            backup_root.mkdir(parents=True, exist_ok=True)
            handle, backup = tempfile.mkstemp(prefix="multica-instructions-", suffix=".json", dir=backup_root)
            with os.fdopen(handle, "w") as stream:
                json.dump({"agent_id": args.agent_id, "workspace_id": workspace, "instructions": existing}, stream, ensure_ascii=False)
            print(f"原指令备份：{backup}")
            cli(["agent", "update", args.agent_id, "--instructions", instructions], workspace)
        actual = cli(["agent", "get", args.agent_id], workspace)
        if actual.get("instructions") != instructions:
            raise ValueError("角色指令未核实；请在 Multica 检查实际配置。")
        print("统一技能与角色指令均已核实；模型、运行时、Access、环境变量和工具权限未由本安装器修改。")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        raise SystemExit(f"安装失败：{error}")

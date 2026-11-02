"""Link skills to one checkout and refresh agents without replacing user settings."""

import argparse
from datetime import datetime
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
LOCATIONS = {"pi": ".pi/agent", "claude-code": ".claude", "codex": ".agents"}
RENAMED_SKILLS = {
    "init-dev-flow": "flow-init", "grill-with-docs": "flow-clarify",
    "to-spec": "flow-spec", "to-plan": "flow-plan", "to-tickets": "flow-todo",
    "implement": "flow-do", "find": "flow-status", "amend": "flow-amend",
    "simplify": "flow-simplify", "diagnosing-bugs": "flow-debug",
    "e2e-test": "flow-e2e", "to-api-contract": "flow-api", "export-session": "flow-export",
}


def frontmatter(data, path):
    lines = data.splitlines(keepends=True)
    if lines and lines[0].rstrip(b"\r\n") == b"---":
        offset = len(lines[0])
        for line in lines[1:]:
            offset += len(line)
            if line.rstrip(b"\r\n") == b"---":
                body = data[offset:]
                if body.startswith(b"\r\n"):
                    body = body[2:]
                elif body.startswith(b"\n"):
                    body = body[1:]
                return data[:offset], body
    raise ValueError(f"{path}: 缺少完整 YAML frontmatter，无法安全保留配置；请先整理该文件。")


def exists(path):
    return path.exists() or path.is_symlink()


def is_previous_skill(path, old, new):
    if path.is_symlink() and path.resolve() in (ROOT / old, ROOT / new):
        return True
    installed = path / "SKILL.md"
    current = ROOT / new / "SKILL.md"
    if not installed.is_file() or not current.is_file():
        return False
    header, _ = frontmatter(current.read_bytes(), current)
    previous_header = header.replace(f"\nname: {new}\n".encode(), f"\nname: {old}\n".encode(), 1)
    for old_command, new_command in RENAMED_SKILLS.items():
        previous_header = previous_header.replace(f"/{new_command}".encode(), f"/{old_command}".encode())
    return installed.read_bytes().replace(b"\r\n", b"\n").startswith(previous_header)


def main():
    parser = argparse.ArgumentParser(prog="install.sh", description="安装或更新 Dev Flow Skills，保留已有 agent 配置。")
    parser.add_argument("target", choices=[*LOCATIONS, "all"], help="选择目标 CLI")
    parser.add_argument("--home", type=Path, default=Path.home(), help="安装所用的用户目录（默认当前 HOME）")
    parser.add_argument("--project-root", type=Path, default=ROOT,
                        help="新 agent 读取基础模型的项目；已有 agent 保留原配置")
    parser.add_argument("--dry-run", action="store_true", help="预览变更，不修改安装目录")
    args = parser.parse_args()
    home = args.home.expanduser().resolve()
    project = args.project_root.expanduser().resolve()
    if not project.is_dir():
        parser.error(f"项目目录不存在：{project}")
    targets = list(LOCATIONS) if args.target == "all" else [args.target]
    skills = sorted(path.parent for path in ROOT.glob("*/SKILL.md"))
    if not skills:
        raise ValueError(f"{ROOT}: 未找到技能，请从完整仓库运行安装入口。")

    links = {}
    writes = {}
    retire = []
    skill_directories = []
    for target in targets:
        directory = home / LOCATIONS[target] / "skills"
        if directory.resolve() == ROOT or directory.resolve() in ROOT.parents:
            raise ValueError(f"仓库位于技能扫描目录内：{ROOT}；请移至独立目录后再安装。")
        for source in [*skills, ROOT / "_agents"]:
            destination = directory / source.name
            if not (destination.is_symlink() and destination.resolve() == source):
                links[destination] = source
        skill_directories.append(directory)

    if "codex" in targets:
        legacy = home / ".codex/skills"
        current = home / LOCATIONS["codex"] / "skills"
        if legacy.resolve() != current.resolve():
            retire.extend(legacy / name for name in [*(skill.name for skill in skills), "_agents"]
                          if exists(legacy / name))
            skill_directories.append(legacy)

    # Retire identifiable old names and whole bundles without taking unrelated personal skills.
    for directory in skill_directories:
        if directory.is_dir():
            for old, new in RENAMED_SKILLS.items():
                path = directory / old
                if exists(path) and is_previous_skill(path, old, new):
                    retire.append(path)
            for old in directory.iterdir():
                if ((old / "_agents").is_dir()
                        and any(all((old / name / "SKILL.md").is_file() for name in names)
                                for names in ([skill.name for skill in skills], RENAMED_SKILLS))):
                    retire.append(old)

    # Generate into an isolated directory, then validate every existing header before writing.
    with tempfile.TemporaryDirectory(prefix="dev-flow-agents-") as staging:
        for target in targets:
            if target == "codex":
                continue
            subprocess.run(["bash", str(ROOT / "adapters/build.sh"), target,
                            "--project-root", str(project), "--output-dir", staging],
                           check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for source in sorted((Path(staging) / target).glob("*.md")):
                destination = home / LOCATIONS[target] / "agents" / source.name
                content = source.read_bytes()
                mode = None
                if exists(destination):
                    header, _ = frontmatter(destination.read_bytes(), destination)
                    _, body = frontmatter(content, source)
                    content = header + b"\n" + body
                    mode = stat.S_IMODE(destination.stat().st_mode)
                    if content == destination.read_bytes():
                        continue
                writes[destination] = (content, mode)

    paths = [*retire, *links, *writes]
    backup_directory = home / ".local/share/dev-flow-skills/backups"
    if any(exists(path) for path in paths):
        if backup_directory.is_symlink():
            raise ValueError(f"备份目录是软链接：{backup_directory}；请先整理目录，避免改写其目标。")
        paths.append(backup_directory)
    for path in paths:
        if not path.is_symlink() and (path.resolve() == ROOT or path.resolve() in ROOT.parents
                                      or ROOT in path.resolve().parents):
            raise ValueError(f"不能替换源仓库或其上级目录：{path}；请将仓库移至独立目录。")
        parent = path.parent
        for ancestor in path.parents:
            if ancestor == home:
                break
            if ancestor.is_symlink():
                raise ValueError(f"安装父目录是软链接：{ancestor}；请先整理目录，避免改写其目标。")
        while not exists(parent):
            parent = parent.parent
        if not parent.is_dir():
            raise ValueError(f"安装路径的父级不是目录：{parent}")

    prefix = "[预览] " if args.dry_run else ""
    print(f"{prefix}技能来源：{ROOT}")
    backup_root = None

    def backup(path):
        nonlocal backup_root
        if not exists(path):
            return
        if backup_root is None:
            backup_directory.mkdir(parents=True, exist_ok=True)
            backup_root = Path(tempfile.mkdtemp(prefix=datetime.now().strftime("%Y%m%d-%H%M%S-"),
                                               dir=backup_directory))
            print(f"旧文件备份位置：{backup_root}")
        destination = backup_root / path.relative_to(home)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(destination))

    for path in retire:
        print(f"{prefix}迁出旧副本：{path}")
        if not args.dry_run:
            backup(path)
    for destination, source in links.items():
        print(f"{prefix}链接：{destination} -> {source}")
        if not args.dry_run:
            backup(destination)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.symlink_to(source, target_is_directory=True)
    for destination, (content, mode) in writes.items():
        print(f"{prefix}更新 agent（已有配置保留）：{destination}")
        if not args.dry_run:
            backup(destination)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
            if mode is not None:
                destination.chmod(mode)
    if not links and not writes and not retire:
        print("安装内容已是当前版本。")
    print(f"{prefix}在目标项目运行 flow-init，引导配置执行模式与基础模型；已有项目配置保持原样。")
    print(f"{prefix}重新打开 CLI 会话以加载技能和 agent。后续 git pull --ff-only 后重跑相同安装命令即可更新。")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        print(f"生成 agent 失败：{error.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    except (OSError, ValueError) as error:
        print(f"安装失败：{error}", file=sys.stderr)
        sys.exit(1)

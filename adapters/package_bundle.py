"""Build a self-contained, single-Skill distribution without changing source skills."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def read_resource(source, root):
    if source.is_symlink() or root not in source.resolve().parents:
        raise ValueError(f"统一包不接受软链接或源码目录外的资源：{source}")
    if source.stat().st_size > 1 << 20:
        raise ValueError(f"统一包存在超过 1 MiB 的资源：{source}")
    data = source.read_bytes()
    if b"\0" in data:
        raise ValueError(f"统一包仅支持文本资源：{source}")
    return data.decode("utf-8")


def bundle_files(root=ROOT):
    root = Path(root).resolve()
    skills = sorted(root.glob("*/SKILL.md"))
    if not skills:
        raise ValueError(f"源码目录中没有技能：{root}")
    sources = {}
    for directory in [*(p.parent for p in skills), root / "_agents", root / "roles"]:
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError(f"资源目录缺失或为软链接：{directory}")
        for source in sorted(directory.rglob("*")):
            relative = source.relative_to(root)
            if any(part.startswith(".") or part == "__pycache__" for part in relative.parts):
                continue
            if source.is_symlink():
                raise ValueError(f"统一包不接受软链接资源：{source}")
            if source.is_file():
                name = relative.as_posix()
                if source.name == "SKILL.md":
                    name = str(relative.with_name("INSTRUCTIONS.md")).replace("\\", "/")
                sources[source] = name
    if len(sources) + 1 > 512:
        raise ValueError("统一包超过宿主支持的资源上限。")
    targets = {p.resolve(): name for p, name in sources.items()}
    files = {}
    resource_size = 0
    for source, name in sources.items():
        if name in files:
            raise ValueError(f"资源重命名后发生冲突：{name}")
        text = read_resource(source, root)
        if source.suffix == ".md":
            def rewrite(match):
                reference = match.group(1)
                path, separator, fragment = reference.partition("#")
                if path and not re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", path):
                    resolved = (source.parent / path).resolve()
                    if resolved in targets and resolved.name == "SKILL.md":
                        reference = path.rsplit("/", 1)[0] + "/INSTRUCTIONS.md" if "/" in path else "INSTRUCTIONS.md"
                        reference += separator + fragment
                return "](" + reference + ")"
            text = re.sub(r"\]\(([^)\s]+)\)", rewrite, text)
        files[name] = text.encode("utf-8")
        resource_size += len(files[name])
        if resource_size > 8 << 20:
            raise ValueError("统一包超过宿主支持的资源上限。")
    links = "\n".join(f"- [{p.parent.name}]({p.parent.name}/INSTRUCTIONS.md)" for p in skills)
    files["SKILL.md"] = read_resource(root / "adapters/bundle-entry.md", root).replace("{{STAGE_LINKS}}", links).encode("utf-8")
    manifest = {"format": "dev-flow-bundle", "version": 1, "stages": [p.parent.name for p in skills],
                "sha256": {name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())}}
    files["bundle-manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    if resource_size + len(files["bundle-manifest.json"]) > 8 << 20:
        raise ValueError("统一包超过宿主支持的资源上限。")
    if any(len(data) > 1 << 20 for data in files.values()):
        raise ValueError("统一包存在超过 1 MiB 的资源。")
    return files


def build_bundle(output, root=ROOT):
    files = bundle_files(root)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成自包含 dev-flow.skill，不修改原有技能。")
    parser.add_argument("--output", type=Path, default=ROOT / "dist/dev-flow.skill")
    args = parser.parse_args()
    try:
        print(build_bundle(args.output))
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(1, f"打包失败：{error}\n")

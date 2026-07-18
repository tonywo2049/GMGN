#!/usr/bin/env python3
from pathlib import Path
import json
import re
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
CLAUDE_MANIFEST = ROOT / ".claude-plugin" / "plugin.json"
CODEX_MANIFEST = ROOT / ".codex-plugin" / "plugin.json"
CODEX_MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
CODEX_AGENTS = ROOT / ".codex" / "agents"

REQUIRED_OPENAI_INTERFACE_FIELDS = ("display_name", "short_description", "default_prompt")
REQUIRED_ROLE_FILES = ("coder.toml", "critic.toml", "reviewer.toml")

EXPECTED_TRIGGERS = {
    "gmgn": ["按流程", "下一步", "GMGN", "workflow", "修 bug", "PRD", "上线"],
    "brainstorm": ["想法", "问题", "机会", "脑暴", "头脑风暴", "调研", "可行性研究"],
    "roadmap": ["路线图", "里程碑", "版本规划", "优先级", "回填"],
    "write-goal": ["启动", "开工", "立项", "Goal", "目标拆解"],
    "write-requirement": ["需求分析", "PRD", "产品需求文档", "需求池", "验收标准", "AC", "变更"],
    "write-design": ["设计", "系统方案", "技术设计", "技术方案", "实现方案", "架构", "Design"],
    "write-task": ["拆任务", "任务卡", "拆卡", "工作项", "实施计划", "待办", "Task"],
    "run-task": ["写代码", "实现任务", "开始编码", "开做", "coding"],
    "close-milestone": ["关账", "收尾", "验收", "发版", "回归", "E2E", "上线", "里程碑", "阶段", "版本"],
}

FORBIDDEN_TRIGGER_OVERLAPS = {
    "run-task": ["里程碑完成", "阶段完成", "版本完成"],
    "close-milestone": ["完成任务卡", "把任务做完"],
}

CHAIN = [
    "brainstorm",
    "roadmap",
    "write-goal",
    "write-requirement",
    "write-design",
    "write-task",
    "run-task",
    "close-milestone",
]


def parse_skill(path: Path) -> tuple[str, str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not match:
        raise AssertionError(f"{path}: frontmatter 缺失")
    frontmatter, body = match.groups()
    name = re.search(r"^name:\s*(.+)$", frontmatter, re.M)
    description = re.search(r"^description:\s*(.+)$", frontmatter, re.M)
    if not name or not description:
        raise AssertionError(f"{path}: name/description 缺失")
    return name.group(1).strip(), description.group(1).strip(), body


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise AssertionError(f"{path}: JSON 无效或缺失 ({exc})") from exc


def parse_openai_yaml(path: Path) -> dict[str, str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as exc:
        raise AssertionError(f"{path}: 缺失") from exc
    if not lines or lines[0] != "interface:":
        raise AssertionError(f"{path}: interface 结构无效")
    metadata: dict[str, str] = {}
    for line in lines[1:]:
        if not line.strip():
            continue
        match = re.fullmatch(r"  (display_name|short_description|default_prompt):\s*(.+)", line)
        if not match or match.group(1) in metadata:
            raise AssertionError(f"{path}: interface 字段无效")
        try:
            value = json.loads(match.group(2))
        except json.JSONDecodeError as exc:
            raise AssertionError(f"{path}: YAML 标量无效 ({exc})") from exc
        if not isinstance(value, str) or not value:
            raise AssertionError(f"{path}: interface 值必须是非空字符串")
        metadata[match.group(1)] = value
    return metadata


def validate_release_metadata(errors: list[str], skill_names: set[str]) -> None:
    try:
        claude_manifest = load_json(CLAUDE_MANIFEST)
        codex_manifest = load_json(CODEX_MANIFEST)
    except AssertionError as exc:
        errors.append(str(exc))
        return

    for field in ("name", "version"):
        if claude_manifest.get(field) != codex_manifest.get(field):
            errors.append(f"双 manifest {field} 不一致")

    skills_path = codex_manifest.get("skills")
    if skills_path not in ("./skills", "./skills/"):
        errors.append("Codex manifest skills 必须指向 ./skills/")

    try:
        marketplace = load_json(CODEX_MARKETPLACE)
    except AssertionError as exc:
        errors.append(str(exc))
    else:
        entries = marketplace.get("plugins", [])
        if not any(
            entry.get("name") == codex_manifest.get("name")
            and entry.get("version") == codex_manifest.get("version")
            for entry in entries
        ):
            errors.append("Codex marketplace 缺少与 manifest 一致的插件条目")

    for name in skill_names:
        path = SKILLS / name / "agents" / "openai.yaml"
        try:
            metadata = parse_openai_yaml(path)
        except AssertionError as exc:
            errors.append(str(exc))
            continue
        missing = [field for field in REQUIRED_OPENAI_INTERFACE_FIELDS if not metadata.get(field)]
        if missing:
            errors.append(f"{path}: 缺字段 {missing}")
        elif f"${name}" not in metadata["default_prompt"]:
            errors.append(f"{path}: default_prompt 未引用 ${name}")

    for filename in REQUIRED_ROLE_FILES:
        path = CODEX_AGENTS / filename
        try:
            role = tomllib.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"{path}: TOML 无效或缺失 ({exc})")
            continue
        for field in ("name", "description", "sandbox_mode", "developer_instructions"):
            value = role.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{path}: {field} 字段类型无效或为空")
        if role.get("sandbox_mode") not in {"read-only", "workspace-write", "danger-full-access"}:
            errors.append(f"{path}: sandbox_mode 无效")

    forbidden_branding = ("METHODOLOGY.md", "Methodology")
    release_text_files = [ROOT / filename for filename in ("README.md", "GMGN.md")]
    for directory in (ROOT / ".claude-plugin", ROOT / ".codex-plugin", SKILLS):
        release_text_files.extend(path for path in directory.rglob("*") if path.is_file())
    for path in release_text_files:
        if path.suffix not in {".md", ".json", ".yaml", ".toml"}:
            continue
        text = path.read_text(encoding="utf-8")
        for branding in forbidden_branding:
            if branding in text:
                errors.append(f"{path}: 残留旧品牌字面 {branding}")


def main() -> int:
    errors: list[str] = []
    parsed: dict[str, tuple[str, str]] = {}

    for directory in sorted(SKILLS.iterdir()):
        if not directory.is_dir():
            continue
        skill_file = directory / "SKILL.md"
        try:
            name, description, body = parse_skill(skill_file)
        except (AssertionError, FileNotFoundError) as exc:
            errors.append(str(exc))
            continue
        if name != directory.name:
            errors.append(f"{skill_file}: name={name}, 目录={directory.name}")
        parsed[name] = (description, body)

    validate_release_metadata(errors, set(parsed))

    for name, triggers in EXPECTED_TRIGGERS.items():
        if name not in parsed:
            errors.append(f"缺少 skill: {name}")
            continue
        description, _ = parsed[name]
        missing = [trigger for trigger in triggers if trigger.lower() not in description.lower()]
        if missing:
            errors.append(f"{name}: description 缺触发词 {missing}")

    for name, forbidden in FORBIDDEN_TRIGGER_OVERLAPS.items():
        if name not in parsed:
            continue
        description, _ = parsed[name]
        overlaps = [phrase for phrase in forbidden if phrase.lower() in description.lower()]
        if overlaps:
            errors.append(f"{name}: description 含相邻工序冲突词 {overlaps}")

    for name in CHAIN:
        if name not in parsed:
            continue
        _, body = parsed[name]
        if "HARD-GATE" not in body:
            errors.append(f"{name}: 缺 HARD-GATE")
        if "Reflection" not in body:
            errors.append(f"{name}: 缺 Reflection")

    for current, following in zip(CHAIN, CHAIN[1:]):
        if current in parsed and following not in parsed[current][1]:
            errors.append(f"{current}: 未指向下一环 {following}")

    if "close-milestone" in parsed and "roadmap" not in parsed["close-milestone"][1]:
        errors.append("close-milestone 后未回到 roadmap 维护态")

    if "run-task" in parsed:
        _, run_task_body = parsed["run-task"]
        close_step = re.search(
            r"^6\. \*\*卡关账\*\*:(.*?)(?=^## |\Z)",
            run_task_body,
            re.M | re.S,
        )
        stale_assertion_requirements = (
            "Task.md",
            "过期断言",
            "待执行",
            "未创建",
            "未运行",
            "待确认",
            "机械刷新",
            "git diff --check",
        )
        if not close_step or any(
            requirement not in close_step.group(1)
            for requirement in stale_assertion_requirements
        ):
            errors.append("run-task: 卡关账前缺少过期断言扫描")

    if "close-milestone" in parsed:
        _, close_body = parsed["close-milestone"]
        machine_gate = re.search(
            r"^## 机检与核对\n(.*?)(?=^## |\Z)", close_body, re.M | re.S
        )
        handoff_gate = re.search(
            r"^## 呈报与收尾\n(.*?)(?=^## |\Z)", close_body, re.M | re.S
        )
        if (
            not machine_gate
            or "classification_complete" not in machine_gate.group(1)
            or "退出码" not in machine_gate.group(1)
            or "非零 finding 就是红灯" not in machine_gate.group(1)
            or not handoff_gate
            or "Handoff" not in handoff_gate.group(1)
            or "性质=记述" not in handoff_gate.group(1)
            or "类型必须复用或登记到项目分类映射" not in handoff_gate.group(1)
        ):
            errors.append("close-milestone: DocStar 或 Handoff 关账门禁缺失")

    if errors:
        print("GMGN skill 校验失败:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"GMGN skill 校验通过: {len(parsed)} 个 skill, {len(CHAIN)} 个链上 HARD-GATE")
    return 0


if __name__ == "__main__":
    sys.exit(main())

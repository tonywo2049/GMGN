#!/usr/bin/env python3
"""Validate GMGN skills, bilingual contracts, platform metadata, and DocStar adapter."""

from pathlib import Path
import json
import re
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
REFERENCES = SKILLS / "gmgn" / "references"
CLAUDE_MANIFEST = ROOT / ".claude-plugin" / "plugin.json"
CODEX_MANIFEST = ROOT / ".codex-plugin" / "plugin.json"
CODEX_MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
CODEX_AGENTS = ROOT / ".codex" / "agents"
DOCSTAR_CONVENTIONS = ROOT / ".docstar" / "conventions" / "conventions.json"

REQUIRED_OPENAI_INTERFACE_FIELDS = ("display_name", "short_description", "default_prompt")
REQUIRED_ROLE_FILES = ("coder.toml", "critic.toml", "reviewer.toml")
CANONICAL_FRONTMATTER = {"locale", "purpose", "upstream", "downstream", "status", "type", "nature"}
LEGACY_FRONTMATTER = {"语言", "目标", "上游", "下游", "状态", "类型", "性质"}
MACHINE_TOKENS = (
    "locale", "purpose", "upstream", "downstream", "status", "type", "nature",
    "draft", "pending-approval", "approved", "closed", "normative", "descriptive",
    "not-started", "initiated", "in-progress", "spec anchor", "prerequisite", "failing test",
)

EXPECTED_TRIGGERS = {
    "gmgn": ("workflow", "bug", "按流程", "下一步"),
    "brainstorm": ("idea", "feasibility", "想法", "可行性研究"),
    "roadmap": ("roadmap", "milestone", "路线图", "里程碑"),
    "write-goal": ("initiate", "Goal.md", "立项", "启动"),
    "write-requirement": ("requirements", "acceptance criteria", "需求", "验收标准"),
    "write-design": ("system design", "architecture", "设计", "架构"),
    "write-task": ("task cards", "implementation", "拆任务", "任务卡"),
    "run-task": ("bug fix", "code", "修 bug", "写代码"),
    "close-milestone": ("full regression", "closure", "关账", "回归"),
}

FORBIDDEN_TRIGGER_OVERLAPS = {
    "run-task": ("里程碑完成", "阶段完成", "版本完成"),
    "close-milestone": ("完成任务卡", "把任务做完"),
}

CHAIN = [
    "brainstorm", "roadmap", "write-goal", "write-requirement", "write-design",
    "write-task", "run-task", "close-milestone",
]


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not match:
        raise AssertionError(f"{path}: frontmatter 缺失")
    raw, body = match.groups()
    fields: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            raise AssertionError(f"{path}: frontmatter 行无冒号: {line!r}")
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"')
    return fields, body


def parse_skill(path: Path) -> tuple[str, str, str]:
    fields, body = parse_frontmatter(path)
    name, description = fields.get("name"), fields.get("description")
    if not name or not description:
        raise AssertionError(f"{path}: name/description 缺失")
    return name, description, body


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


def has_ascii_and_cjk(value: str) -> bool:
    return bool(re.search(r"[A-Za-z]", value) and re.search(r"[\u4e00-\u9fff]", value))


def validate_release_metadata(errors: list[str], skill_names: set[str]) -> None:
    try:
        claude_manifest = load_json(CLAUDE_MANIFEST)
        codex_manifest = load_json(CODEX_MANIFEST)
        marketplace = load_json(CODEX_MARKETPLACE)
    except AssertionError as exc:
        errors.append(str(exc))
        return

    for field in ("name", "version"):
        if claude_manifest.get(field) != codex_manifest.get(field):
            errors.append(f"双 manifest {field} 不一致")
    if codex_manifest.get("skills") not in ("./skills", "./skills/"):
        errors.append("Codex manifest skills 必须指向 ./skills/")
    if not has_ascii_and_cjk(codex_manifest.get("description", "")):
        errors.append("Codex manifest description 必须同时提供英文和中文")
    if not has_ascii_and_cjk(claude_manifest.get("description", "")):
        errors.append("Claude manifest description 必须同时提供英文和中文")

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
        for field in REQUIRED_OPENAI_INTERFACE_FIELDS:
            if field in metadata and not has_ascii_and_cjk(metadata[field]):
                errors.append(f"{path}: {field} 必须同时含英文和中文")

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


def validate_document_pairs(errors: list[str]) -> None:
    root_pairs = ((ROOT / "README.md", ROOT / "README.zh-CN.md"),
                  (ROOT / "GMGN.md", ROOT / "GMGN.zh-CN.md"))
    for en_path, zh_path in root_pairs:
        try:
            en_meta, en_body = parse_frontmatter(en_path)
            zh_meta, zh_body = parse_frontmatter(zh_path)
        except (AssertionError, FileNotFoundError) as exc:
            errors.append(str(exc))
            continue
        if en_meta.get("locale") != "en" or zh_meta.get("locale") != "zh-CN":
            errors.append(f"{en_path.name}/{zh_path.name}: locale 必须为 en/zh-CN")
        if zh_path.name not in en_body or en_path.name not in zh_body:
            errors.append(f"{en_path.name}/{zh_path.name}: 中英文文档必须互链")

    try:
        readme_meta, readme = parse_frontmatter(ROOT / "README.md")
        method_meta, method = parse_frontmatter(ROOT / "GMGN.md")
    except AssertionError as exc:
        errors.append(str(exc))
    else:
        if readme_meta.get("nature") != "descriptive" or method_meta.get("nature") != "normative":
            errors.append("README 必须是 descriptive，GMGN.md 必须是 normative")
        if "installation" not in readme.lower() or "## 1. Two primary risks" not in method:
            errors.append("README/GMGN.md 分工失真：前者应管安装，后者应管完整方法")
        if "README" not in method or "GMGN.md" not in readme:
            errors.append("README 与 GMGN.md 必须互相说明分工")

    en_dir, zh_dir = REFERENCES / "en", REFERENCES / "zh-CN"
    en_names = {path.name for path in en_dir.glob("*.md")}
    zh_names = {path.name for path in zh_dir.glob("*.md")}
    if en_names != zh_names:
        errors.append(f"references 中英文文件名不一致: en-only={sorted(en_names-zh_names)}, zh-only={sorted(zh_names-en_names)}")
    if not en_names:
        errors.append("references 双语模板为空")

    for name in sorted(en_names & zh_names):
        en_path, zh_path = en_dir / name, zh_dir / name
        try:
            en_meta, en_body = parse_frontmatter(en_path)
            zh_meta, zh_body = parse_frontmatter(zh_path)
        except AssertionError as exc:
            errors.append(str(exc))
            continue
        if set(en_meta) != CANONICAL_FRONTMATTER or set(zh_meta) != CANONICAL_FRONTMATTER:
            errors.append(f"references/{name}: frontmatter 必须恰为 canonical 七键")
        if en_meta.get("locale") != "en" or zh_meta.get("locale") != "zh-CN":
            errors.append(f"references/{name}: locale 必须为 en/zh-CN")
        if en_body.count("```") != zh_body.count("```"):
            errors.append(f"references/{name}: 中英文代码块数量不一致")
        if f"../zh-CN/{name}" not in en_body or f"../en/{name}" not in zh_body:
            errors.append(f"references/{name}: 中英文镜像必须互链")
        raw = en_path.read_text(encoding="utf-8") + zh_path.read_text(encoding="utf-8")
        if any(re.search(rf"^{key}:", raw, re.M) for key in LEGACY_FRONTMATTER):
            errors.append(f"references/{name}: 残留旧中文机器字段")

    for locale in ("en", "zh-CN"):
        path = REFERENCES / locale / "writing-contract.md"
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            missing = [token for token in MACHINE_TOKENS if token not in text]
            if missing:
                errors.append(f"{path}: 缺机器契约 token {missing}")

    legacy_files = [path for path in REFERENCES.glob("*.md")]
    if legacy_files:
        errors.append(f"references 根目录残留旧模板: {[p.name for p in legacy_files]}")


def validate_docstar_adapter(errors: list[str]) -> None:
    try:
        conv = load_json(DOCSTAR_CONVENTIONS)
    except AssertionError as exc:
        errors.append(str(exc))
        return
    expected_columns = {
        "spec": "spec anchor", "prereq": "prerequisite",
        "red": "failing test", "status": "status",
    }
    if conv.get("version") != "1" or conv.get("task_columns") != expected_columns:
        errors.append("DocStar conventions 的 version 或固定英文任务表头无效")
    pairs = conv.get("edges", {}).get("directed_pairs", [])
    if ["upstream", "downstream"] not in pairs or ["上游", "下游"] not in pairs:
        errors.append("DocStar conventions 必须同时接受英文 canonical 键和旧中文输入别名")
    rules = conv.get("required_edges", [])
    if not any(rule.get("rule") == "gmgn-ac-has-task" for rule in rules):
        errors.append("DocStar conventions 缺 GMGN AC→Task 覆盖规则")
    exclusions = {"参数", "测试", "专名", "文档", "节条目", "里程碑"}
    if set(conv.get("uncovered_kind_exclusions", [])) != exclusions:
        errors.append("DocStar conventions 未正确排除 GMGN 辅助 kind")
    if any(row and row[0] == "需求AC" for row in conv.get("type_sections", [])):
        errors.append("DocStar conventions 不得把普通 Requirements 小节整体当成需求 AC")


def extract_section(text: str, heading: str) -> str | None:
    match = re.search(
        rf"^{re.escape(heading)}\n(.*?)(?=^## |\Z)",
        text,
        re.M | re.S,
    )
    return match.group(1) if match else None


def require_section_tokens(
    errors: list[str], text: str, heading: str, tokens: tuple[str, ...], label: str
) -> None:
    section = extract_section(text, heading)
    normalized = "" if section is None else re.sub(r"\s+", " ", section)
    compact = re.sub(r"\s+", "", normalized)
    missing = [
        token for token in tokens
        if re.sub(r"\s+", " ", token) not in normalized
        and re.sub(r"\s+", "", token) not in compact
    ]
    if missing:
        errors.append(f"{label}: 受控变更规则缺失 {missing}")


def validate_controlled_change_protocol(
    errors: list[str], parsed: dict[str, tuple[str, str]]
) -> None:
    try:
        method_en = (ROOT / "GMGN.md").read_text(encoding="utf-8")
        method_zh = (ROOT / "GMGN.zh-CN.md").read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        errors.append(str(exc))
    else:
        require_section_tokens(
            errors,
            method_en,
            "## 3. Approval and change semantics",
            (
                "Place changes by authority; review them by impact",
                "impact cone",
                "does not restart the complete workflow",
                "old approval remains attached to the old version anchor",
                "file-content change does not by itself require approval",
                "Mechanical renames",
                "explicit equivalence record",
                "this is not a new approval",
            ),
            "GMGN.md",
        )
        require_section_tokens(
            errors,
            method_zh,
            "## 第 3 章 确认语义",
            (
                "变更按归属落位、按影响复核",
                "影响范围",
                "不等于重走完整流程",
                "旧批准继续指向旧版本锚",
                "不能只看文件内容是否变化",
                "机械变更",
                "语义等价",
                "不构成一次新批准",
            ),
            "GMGN.zh-CN.md",
        )

    router = parsed.get("gmgn", ("", ""))[1]
    require_section_tokens(
        errors,
        router,
        "## Controlled-change routing",
        (
            "| WhitePaper problem, goal, scope, harm order, invariant, or interpretation | `brainstorm` revision mode |",
            "| ROADMAP sequencing, milestone allocation, dependency, or qualitative completion picture | `roadmap` maintenance mode |",
            "| Goal objective, boundary, slice, non-goal, or completion picture | `write-goal` revision mode |",
            "| Requirement, constraint, parameter authority, or acceptance criterion | `write-requirement` revision mode |",
            "| Design structure, interface, data, failure path, or R-AC mapping | `write-design` revision mode |",
            "| Task card, dependency, execution order, test anchor, or traceability mapping | `write-task` revision mode |",
            "Old approval remains attached to the old anchor",
            "do not rerun unrelated stages",
            "mechanical changes use same-batch refresh and machine checks without reapproval",
            "equivalence record",
            "this is not a new approval",
        ),
        "gmgn 路由",
    )

    brainstorm = parsed.get("brainstorm", ("", ""))[1]
    require_section_tokens(
        errors,
        brainstorm,
        "## Revision mode",
        (
            "handles the change delta; it is not a new brainstorm",
            "approved old anchor",
            "impact cone",
            "owner approve the semantic delta at a new version anchor",
            "Do not rerun unaffected stages",
            "without entering revision mode or seeking reapproval",
        ),
        "brainstorm 修订态",
    )

    stage_tokens = {
        "write-goal": ("`brainstorm` revision mode", "`roadmap` maintenance mode"),
        "write-requirement": ("WhitePaper to `brainstorm`", "Goal to `write-goal`"),
        "write-design": (
            "WhitePaper to `brainstorm`",
            "Requirement or R-AC meaning to `write-requirement`",
        ),
        "write-task": ("WhitePaper to `brainstorm`", "design intent to `write-design`"),
    }
    common = (
        "old anchor",
        "affected",
        "new anchor",
        "Old review remains attached to the old anchor",
        "impact cone only",
        "mechanical changes",
        "without reapproval",
    )
    for name, routes in stage_tokens.items():
        body = parsed.get(name, ("", ""))[1]
        require_section_tokens(
            errors,
            body,
            "## Controlled revision",
            common + routes,
            f"{name} 修订态",
        )

    contract_rules = (
        (
            REFERENCES / "en" / "writing-contract.md",
            "### 3.1 Controlled changes after approval",
            (
                "single authority",
                "semantic change",
                "mechanical change",
                "File-content change alone does not require reapproval",
                "semantic equivalence",
                "this is not a new approval",
                "impact cone",
                "change record",
                "old anchor",
                "new anchor and checks",
            ),
        ),
        (
            REFERENCES / "zh-CN" / "writing-contract.md",
            "### 3.1 已批准文档的受控变更",
            (
                "唯一权威文档",
                "语义变更",
                "机械变更",
                "不能只因文件内容变化就要求重新批准",
                "语义等价",
                "不构成一次新批准",
                "影响范围",
                "变更记录",
                "旧版本锚",
                "新版本锚与检查",
            ),
        ),
    )
    for path, heading, tokens in contract_rules:
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            errors.append(str(exc))
            continue
        require_section_tokens(errors, text, heading, tokens, str(path))

    execution_sections = (
        (
            "run-task",
            "## Upstream change during execution",
            (
                "old authority anchor",
                "impact cone",
                "Route WhitePaper",
                "new anchor",
                "do not restart unrelated work",
                "without reapproval",
            ),
        ),
        (
            "close-milestone",
            "## Upstream change during closure",
            (
                "old anchor",
                "impact cone",
                "controlled-change route",
                "full-regression",
                "Do not repeat unrelated authoring stages",
                "without reapproval",
            ),
        ),
    )
    for name, heading, tokens in execution_sections:
        require_section_tokens(
            errors,
            parsed.get(name, ("", ""))[1],
            heading,
            tokens,
            f"{name} 上游变更处理",
        )


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
        if not has_ascii_and_cjk(description):
            errors.append(f"{skill_file}: description 必须同时含英文和中文触发语料")
        parsed[name] = (description, body)

    validate_release_metadata(errors, set(parsed))
    validate_document_pairs(errors)
    validate_docstar_adapter(errors)
    validate_controlled_change_protocol(errors, parsed)

    for name, triggers in EXPECTED_TRIGGERS.items():
        if name not in parsed:
            errors.append(f"缺少 skill: {name}")
            continue
        description, body = parsed[name]
        missing = [trigger for trigger in triggers if trigger.lower() not in description.lower()]
        if missing:
            errors.append(f"{name}: description 缺触发词 {missing}")
        if "HARD-GATE" not in body:
            errors.append(f"{name}: 缺 HARD-GATE")
        if "Reflection" not in body:
            errors.append(f"{name}: 缺 Reflection")

    for name, forbidden in FORBIDDEN_TRIGGER_OVERLAPS.items():
        if name in parsed:
            overlaps = [phrase for phrase in forbidden if phrase in parsed[name][0]]
            if overlaps:
                errors.append(f"{name}: description 含相邻工序冲突词 {overlaps}")

    for current, following in zip(CHAIN, CHAIN[1:]):
        if current in parsed and following not in parsed[current][1]:
            errors.append(f"{current}: 未指向下一环 {following}")
    if "close-milestone" in parsed and "roadmap" not in parsed["close-milestone"][1]:
        errors.append("close-milestone 后未回到 roadmap 维护态")

    if "write-task" in parsed:
        task_body = parsed["write-task"][1]
        header = "| # | task | spec anchor | prerequisite | failing test | status |"
        if header not in task_body:
            errors.append("write-task: 缺固定英文任务表头")

    if "run-task" in parsed:
        body = parsed["run-task"][1]
        close_step = re.search(r"^6\. \*\*Card close\*\*(.*?)(?=^## |\Z)", body, re.M | re.S)
        required = ("Task.md", "stale assertions", "not-started", "not created", "not run",
                    "awaiting confirmation", "Mechanically refresh", "git diff --check")
        if not close_step or any(token not in close_step.group(1) for token in required):
            errors.append("run-task: 卡关账前缺少过期断言扫描")

    if "close-milestone" in parsed:
        body = parsed["close-milestone"][1]
        machine = re.search(r"^## Machine checks and checklist\n(.*?)(?=^## |\Z)", body, re.M | re.S)
        presentation = re.search(r"^## Presentation and close\n(.*?)(?=^## |\Z)", body, re.M | re.S)
        if (
            not machine or "classification_complete" not in machine.group(1)
            or "non-zero gate finding" not in machine.group(1)
            or not presentation or "Handoff" not in presentation.group(1)
            or "nature: descriptive" not in presentation.group(1)
            or "type: handoff" not in presentation.group(1)
            or "reuse a registered type/token" not in presentation.group(1)
        ):
            errors.append("close-milestone: DocStar 或 Handoff 关账门禁缺失")

    forbidden_branding = ("METHODOLOGY.md", "Methodology")
    release_files = [ROOT / name for name in ("README.md", "README.zh-CN.md", "GMGN.md", "GMGN.zh-CN.md")]
    for directory in (ROOT / ".claude-plugin", ROOT / ".codex-plugin", SKILLS):
        release_files.extend(path for path in directory.rglob("*") if path.is_file())
    for path in release_files:
        if path.suffix not in {".md", ".json", ".yaml", ".toml"}:
            continue
        text = path.read_text(encoding="utf-8")
        for branding in forbidden_branding:
            if branding in text:
                errors.append(f"{path}: 残留旧品牌字面 {branding}")

    if errors:
        print("GMGN skill 校验失败:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"GMGN skill 校验通过: {len(parsed)} skills, {len(CHAIN)} gated transitions, "
        f"{len(list((REFERENCES / 'en').glob('*.md')))} bilingual references"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

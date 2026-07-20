#!/usr/bin/env python3
"""Validate GMGN skills, bilingual contracts, platform metadata, and DocStar adapter."""

from pathlib import Path
import ast
import json
import re
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_release import release_metadata


SKILLS = ROOT / "skills"
REFERENCES = SKILLS / "gmgn" / "references"
CODEX_AGENTS = ROOT / ".codex" / "agents"
CLAUDE_AGENTS = ROOT / "agents"
DOCSTAR_CONVENTIONS = ROOT / ".docstar" / "conventions" / "conventions.json"
LANE_REGISTRY = SKILLS / "run-task" / "scripts" / "lane_registry.py"

REQUIRED_OPENAI_INTERFACE_FIELDS = ("display_name", "short_description", "default_prompt")
ROLE_NAMES = ("author", "coder", "critic", "reviewer", "verifier", "integrator")
REQUIRED_CODEX_ROLE_FILES = tuple(f"{name}.toml" for name in ROLE_NAMES)
REQUIRED_CLAUDE_ROLE_FILES = tuple(f"{name}.md" for name in ROLE_NAMES)
CANONICAL_FRONTMATTER = {"locale", "purpose", "upstream", "downstream", "status", "type", "nature"}
LEGACY_FRONTMATTER = {"语言", "目标", "上游", "下游", "状态", "类型", "性质"}
MACHINE_TOKENS = (
    "locale", "purpose", "upstream", "downstream", "status", "type", "nature",
    "draft", "pending-approval", "approved", "closed", "normative", "descriptive",
    "not-started", "initiated", "in-progress", "spec anchor", "prerequisite", "failing test",
)
REFERENCE_NAMES = {
    "writing-contract.md", "dispatch-and-handoff.md", "code-review.md",
    "preflight-checklist.md", "pre-merge-checklist.md", "pre-close-checklist.md",
}
REMOVED_TEMPLATE_REFERENCES = {
    "allocation-ledger.md", "coder-brief.md", "critic-brief.md",
    "decision-log.md", "trust-surface-register.md",
}
DOCUMENT_NODE_SKILLS = (
    "brainstorm", "roadmap", "write-goal", "write-requirement", "write-design", "write-task",
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
        metadata = release_metadata(ROOT)
    except ValueError as exc:
        errors.append(f"发布版本门禁失败: {exc}")
        return
    claude_manifest = metadata["claude_manifest"]
    codex_manifest = metadata["codex_manifest"]

    if claude_manifest.get("name") != codex_manifest.get("name"):
        errors.append("双 manifest name 不一致")
    if codex_manifest.get("skills") not in ("./skills", "./skills/"):
        errors.append("Codex manifest skills 必须指向 ./skills/")
    if not has_ascii_and_cjk(codex_manifest.get("description", "")):
        errors.append("Codex manifest description 必须同时提供英文和中文")
    if not has_ascii_and_cjk(claude_manifest.get("description", "")):
        errors.append("Claude manifest description 必须同时提供英文和中文")

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

    for filename in REQUIRED_CODEX_ROLE_FILES:
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

    for filename in REQUIRED_CLAUDE_ROLE_FILES:
        path = CLAUDE_AGENTS / filename
        try:
            fields, body = parse_frontmatter(path)
        except (AssertionError, FileNotFoundError) as exc:
            errors.append(str(exc))
            continue
        if fields.get("name") != path.stem:
            errors.append(f"{path}: name 必须与文件名一致")
        if not has_ascii_and_cjk(fields.get("description", "")):
            errors.append(f"{path}: description 必须同时含英文和中文")
        if not body.strip():
            errors.append(f"{path}: agent 指令为空")
        if path.stem in {"critic", "reviewer", "verifier"}:
            denied = fields.get("disallowedTools", "")
            if "Write" not in denied or "Edit" not in denied:
                errors.append(f"{path}: 只读角色必须禁用 Write/Edit")
        if path.stem in {"author", "coder"} and fields.get("isolation") != "worktree":
            errors.append(f"{path}: writer 必须显式 isolation: worktree")
        if path.stem in {"reviewer", "verifier", "integrator"} and "isolation" in fields:
            errors.append(f"{path}: 非 writer 不得盲目新建 worktree")


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
        errors.append("references 双语契约为空")
    if en_names != REFERENCE_NAMES:
        errors.append(
            f"references 必须只保留契约与核对单: missing={sorted(REFERENCE_NAMES-en_names)}, "
            f"extra={sorted(en_names-REFERENCE_NAMES)}"
        )

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
            skeleton_markers = (
                "## 5. G-R-D-T templates", "## 5. G-R-D-T 模板",
                "### Goal.md", "# M1 Goal", "## Traceability matrix", "## 追踪矩阵",
            )
            hits = [marker for marker in skeleton_markers if marker in text]
            if hits:
                errors.append(f"{path}: 残留可复制文档骨架 {hits}")

    legacy_files = [path for path in REFERENCES.glob("*.md")]
    if legacy_files:
        errors.append(f"references 根目录残留旧文件: {[p.name for p in legacy_files]}")

    release_markdown = [ROOT / name for name in ("README.md", "README.zh-CN.md", "GMGN.md", "GMGN.zh-CN.md")]
    release_markdown.extend(path for path in SKILLS.rglob("*.md"))
    for path in release_markdown:
        text = path.read_text(encoding="utf-8")
        stale = sorted(name for name in REMOVED_TEMPLATE_REFERENCES if name in text)
        if stale:
            errors.append(f"{path}: 引用了已删除模板 {stale}")


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


def validate_lane_registry(errors: list[str]) -> None:
    try:
        text = LANE_REGISTRY.read_text(encoding="utf-8")
        tree = ast.parse(text, filename=str(LANE_REGISTRY))
    except (FileNotFoundError, SyntaxError) as exc:
        errors.append(f"{LANE_REGISTRY}: 缺失或语法无效 ({exc})")
        return

    allowed_imports = {
        "__future__", "argparse", "hashlib", "json", "subprocess", "sys",
        "copy", "datetime", "pathlib", "typing",
    }
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".", 1)[0])
    unexpected = sorted(imported - allowed_imports)
    if unexpected:
        errors.append(f"{LANE_REGISTRY}: lane registry 只能依赖 Python stdlib，发现 {unexpected}")

    require_tokens(
        errors,
        text,
        (
            'REGISTRY_REF = "refs/gmgn/lane-registry"',
            '"hash-object", "-w", "--stdin"',
            '"update-ref", REGISTRY_REF, new_object_id, expected',
            "project_scope_id", "lane_key", "run_id", "owner_thread_id", "owner_run_id",
            "ownership_epoch", "coder_ref", "worktree_path", "repository_identity",
            "git_common_dir", "git_dir", "device", "inode", "object_format",
            "baseline_missing", "candidate_anchor", "assert_bound_identity",
            '"claim": claim', '"bind-coder": bind_coder', '"status": status',
            '"verify": verify', '"anchor": anchor', '"release": release',
            '"cancel-unbound": cancel_unbound', 'lane["state"] = "released"',
            'lane["state"] = "cancelled-unbound"',
            'parser.add_argument("--coder-ref", required=True)', "canonical_directory",
        ),
        str(LANE_REGISTRY),
    )


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


def validate_milestone_scope_protocol(
    errors: list[str], parsed: dict[str, tuple[str, str]]
) -> None:
    def contract(text: str, tokens: tuple[str, ...], error: str) -> None:
        normalized = " ".join(text.split())
        compact = re.sub(r"\s+", "", text)
        if any(
            " ".join(token.split()) not in normalized
            and re.sub(r"\s+", "", token) not in compact
            for token in tokens
        ):
            errors.append(error)

    def hard_gate(text: str, tokens: tuple[str, ...], error: str) -> None:
        match = re.search(r"<HARD-GATE>(.*?)</HARD-GATE>", text, re.S)
        contract("" if match is None else match.group(1), tokens, error)

    method_en = (ROOT / "GMGN.md").read_text(encoding="utf-8")
    method_zh = (ROOT / "GMGN.zh-CN.md").read_text(encoding="utf-8")
    router = parsed.get("gmgn", ("", ""))[1]
    roadmap = parsed.get("roadmap", ("", ""))[1]
    write_task = parsed.get("write-task", ("", ""))[1]
    run_task = parsed.get("run-task", ("", ""))[1]
    close = parsed.get("close-milestone", ("", ""))[1]

    require_section_tokens(
        errors,
        method_en,
        "### 2.4 Milestone ownership and closure boundary",
        (
            "from `write-goal` through `close-milestone`", "do not invent this ID",
            "exactly one owning Milestone", "never expands the set automatically",
            "already planned upstream Milestone", "non-blocking TODO/Handoff",
            "Milestone closure is scoped to the target", "remains the semantic authority",
            "Do not reopen M0", "current Milestone owns the change", "supersedes",
        ),
        "GMGN.md target Milestone 边界",
    )
    require_section_tokens(
        errors,
        method_zh,
        "### 2.C 结构与规则",
        (
            "从 `write-goal` 到 `close-milestone`", "不虚构该 ID",
            "每张任务卡只有一个 owning Milestone", "不能自动扩张执行集",
            "外部强前置只能指向已经规划的上游 Milestone", "非阻塞 TODO/Handoff",
            "关账门禁只看目标 Milestone", "继续拥有该内容的语义", "不重开 M0",
            "当前 Milestone 的自有卡承担变更、实现与验证", "supersedes",
        ),
        "GMGN.zh-CN.md target Milestone 边界",
    )
    require_section_tokens(
        errors,
        router,
        "## Route by observable state",
        (
            "Before `write-goal`", "Do not invent this ID", "never expands the execution set",
            "keep one separately owned execution set",
        ),
        "gmgn 路由 target Milestone 边界",
    )
    require_section_tokens(
        errors,
        router,
        "## Controlled-change routing",
        (
            "remains the semantic authority", "change card owned by the current Milestone",
            "do not reopen M0", "current Milestone owns the change, implementation, and verification work",
        ),
        "gmgn 路由 M0 历史关账",
    )
    require_section_tokens(
        errors,
        roadmap,
        "## Create",
        (
            "independently decidable from work owned by that Milestone",
            "must not be an earlier Milestone's completion criterion",
        ),
        "roadmap Milestone 独立完成景象",
    )
    require_section_tokens(
        errors,
        roadmap,
        "## Controlled revision",
        (
            "remains semantic authority", "old closure anchor closed",
            "current Milestone's change card", "supersedes", "reopening or rerunning M0",
        ),
        "roadmap M0 历史关账",
    )
    require_section_tokens(
        errors,
        write_task,
        "## Author content and self-check",
        (
            "exactly one owning Milestone", "already planned upstream Milestone",
            "ROADMAP dependency relationship, not by Milestone ID or numeric order",
            "must not depend on downstream", "spike or verification card owned by that target Milestone",
            "non-blocking TODO or Handoff", "no reverse dependency points to a downstream Milestone",
        ),
        "write-task 跨 Milestone 依赖方向",
    )
    hard_gate(
        run_task,
        (
            "recorded `target_milestone_id`",
            "Cross-milestone references never expand this set automatically",
        ),
        "run-task target Milestone 执行集",
    )
    require_section_tokens(
        errors,
        run_task,
        "## 1. Build and continuously refill the ready set",
        (
            "only from confirmed cards owned by that target Milestone's Task authority",
            "create separate execution sets", "upstream prerequisite may gate readiness",
            "downstream reverse dependency", "does not start downstream work",
        ),
        "run-task target Milestone 执行集",
    )
    require_section_tokens(
        errors,
        run_task,
        "## Exit",
        ("owned by `target_milestone_id`", "Downstream execution sets and lanes have separate lifecycle decisions"),
        "run-task target Milestone Exit",
    )
    hard_gate(
        close,
        (
            "Every hard gate is scoped to the recorded `target_milestone_id`",
            "no lane owned by it may be active", "Downstream work, lanes, documents",
            "do not block unless they prove",
        ),
        "close-milestone target Milestone 关账范围",
    )
    require_section_tokens(
        errors,
        close,
        "## Three closure disciplines",
        (
            "completed with evidence", "removed or reassigned by a controlled semantic change",
            "new authority anchor", "Requirement, Task, and matrix synchronized",
            "A `deferred` label, TODO, or Handoff alone never waives an AC",
            "does not alter semantic closure eligibility",
        ),
        "close-milestone target AC 完成语义",
    )
    require_section_tokens(
        errors,
        close,
        "## Machine checks and checklist",
        (
            "do not treat it as proof that GMGN semantic scope classification is complete",
            "every finding with evidence and exactly one GMGN classification",
            "target-scoped | candidate-introduced-or-polluted | external-pre-existing",
            "first two classes blocks", "predates the closing candidate",
            "If evidence cannot prove `external-pre-existing`, scope classification is incomplete and closure is blocked",
        ),
        "close-milestone DocStar finding 范围",
    )
    require_section_tokens(
        errors,
        method_en,
        "## 3. Approval and change semantics",
        (
            "completed with evidence", "controlled semantic change at a new authority anchor",
            "Requirement, Task, and matrix synchronized", "`deferred` label or TODO alone never waives",
        ),
        "GMGN.md target AC 完成语义",
    )
    require_section_tokens(
        errors,
        method_en,
        "## 6. Tool and automation boundaries",
        (
            "does not establish GMGN semantic scope classification",
            "Record every finding, its evidence, and exactly one classification",
            "target-scoped | candidate-introduced-or-polluted | external-pre-existing",
            "If that proof is missing, scope classification is incomplete and closure is blocked",
        ),
        "GMGN.md DocStar finding 范围",
    )
    require_section_tokens(
        errors,
        method_zh,
        "## 第 3 章 确认语义",
        (
            "完成证据", "新权威锚生效的受控删除/重新分配记录",
            "同步 Requirement、Task 与矩阵", "不能豁免仍在目标范围内的 AC",
        ),
        "GMGN.zh-CN.md target AC 完成语义",
    )
    require_section_tokens(
        errors,
        method_zh,
        "## 第 6 章 工具与自动化边界",
        (
            "classification_complete` 也不等于 GMGN 已完成语义归属",
            "每条 finding 都要连同证据归入且只能归入",
            "target-scoped | candidate-introduced-or-polluted | external-pre-existing",
            "不能证明时，scope classification incomplete，阻断关账",
        ),
        "GMGN.zh-CN.md DocStar finding 范围",
    )

    forbidden_zh = ("回选型与架构线复议", "一律回归选型与架构线续开")
    found_zh = [phrase for phrase in forbidden_zh if phrase in method_zh]
    if found_zh:
        errors.append(f"GMGN.zh-CN.md: 残留重开 M0/续开选型线语义 {found_zh}")
    forbidden_deferred = ("implemented, explicitly deferred", "deferred explicitly")
    deferred_hits = [
        phrase for phrase in forbidden_deferred if phrase in method_en or phrase in close
    ]
    if deferred_hits:
        errors.append(f"关账语义仍允许仅 deferred 的 target AC {deferred_hits}")

    for locale, tokens in (
        (
            "en",
            ("Target boundary", "target_milestone_id", "still-in-scope AC mislabeled `deferred`",
             "exactly one GMGN classification", "scope classification incomplete and closure blocked",
             "classification_complete` alone does not"),
        ),
        (
            "zh-CN",
            ("目标边界", "target_milestone_id", "仍在目标范围内的 AC 是否被错误标成 `deferred`",
             "归入且只归入", "scope classification incomplete 并阻断",
             "classification_complete` 本身不能"),
        ),
    ):
        text = (REFERENCES / locale / "pre-close-checklist.md").read_text(encoding="utf-8")
        contract(text, tokens, f"pre-close-checklist({locale}): target Milestone 契约缺失")


def require_tokens(errors: list[str], text: str, tokens: tuple[str, ...], label: str) -> None:
    normalized_text = " ".join(text.split())
    missing = [
        token for token in tokens
        if " ".join(token.split()) not in normalized_text
    ]
    if missing:
        errors.append(f"{label}: 缺 agent 生命周期约束 {missing}")


def validate_agent_lifecycle(
    errors: list[str], parsed: dict[str, tuple[str, str]]
) -> None:
    dispatch_paths = (
        REFERENCES / "en" / "dispatch-and-handoff.md",
        REFERENCES / "zh-CN" / "dispatch-and-handoff.md",
    )
    runtime_states = (
        "blocked-prerequisite", "awaiting-owner-input", "ready-to-dispatch",
        "workspace-prepared", "author-active", "author-returned", "author-rework", "candidate-anchored",
        "critic-active", "critic-returned", "author-revising", "critic-rechecking",
        "upstream-change-pending", "acceptance-ready", "accepted", "integration-queued", "integrating",
        "integration-conflict", "rebase-required", "post-integration-verifying",
        "node-complete", "agent-unavailable", "coder-active", "coder-returned",
        "coder-revising", "reviewer-active", "reviewer-returned", "reviewer-rechecking",
        "verifier-active", "verifier-returned", "owner-unreachable",
        "candidate-awaiting-anchor", "review-authorized", "worker-create-requested",
        "worker-queued", "worker-resolved", "worker-bootstrap-returned", "worker-activated",
    )
    role_tokens = (
        "author | coder | critic | reviewer | verifier | researcher | integrator",
        "author_ref", "critic_ref", "coder_ref", "reviewer_ref", "verifier_ref",
        "integrator_ref",
    )
    lane_fields = (
        "project_scope_id", "lane_key", "owner_thread_id", "owner_run_id",
        "ownership_epoch", "run_id", "card_id", "workspace_mode", "worktree_path",
        "branch_ref", "baseline_anchor", "candidate_anchor", "write_set",
        "conflict_domains", "runtime_locks", "integration_queue_ref",
        "shared_baseline_anchor", "repository_identity",
    )
    for path in dispatch_paths:
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            errors.append(str(exc))
            continue
        require_tokens(errors, text, runtime_states + role_tokens + lane_fields, str(path))
        isolation_tokens = (
            ("git rev-parse --show-toplevel", "absolute", "does not resolve", "same branch", "proposal")
            if path.parent.name == "en"
            else ("git rev-parse --show-toplevel", "绝对", "不消除", "同一分支", "proposal")
        )
        require_tokens(errors, text, isolation_tokens, str(path))
        baseline_tokens = (
            ("git rev-parse HEAD", "${baseline_anchor}^{commit}", "content hash",
             "rebuild the worktree", "candidate_anchor", "old `baseline_anchor`")
            if path.parent.name == "en"
            else ("git rev-parse HEAD", "${baseline_anchor}^{commit}", "内容 hash",
                  "重建 worktree", "candidate_anchor", "旧 `baseline_anchor`")
        )
        require_tokens(errors, text, baseline_tokens, f"{path} workspace-prepared 基线锁")
        if "```" in text:
            errors.append(f"{path}: 派发契约不得退回填空模板")

    adapter_tokens = {
        dispatch_paths[0]: (
            "ordinary subagents share", "isolation: worktree", "Agent Teams",
            "do not automatically create worktrees", "never relies on automatic merge",
            "fresh/origin default", "baseline_anchor", "WorktreeCreate", "current dispatch path",
            "scheduler DAG", "named `Agent`", "waits for any", "general-purpose",
            "SendMessage", "Explore", "Plan", "experimental", "/resume",
            "actual platform capacity", "environment-variable default",
            "Author, Critic, Coder, Reviewer, Verifier, and Integrator",
            "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1", "does not require adopting Agent Teams",
            "agent-unavailable", "do not claim a targeted recheck", "same Verifier",
            "same Integrator", "cross-task fan-out", "create_thread", "list_threads",
            "read_thread", "wait_threads", "send_message_to_thread", "read-only",
            "exactly one card", "recursively create main tasks", "run-scoped authorization",
            "clientThreadId", "threadId", "hostId", "first blocking wait", "timeoutMs: 0",
            "only static execution authority", "parent conversation history", "fork_turns",
            "fork_context", "not a per-agent `Handoff`", "only in chat", "write-task",
        ),
        dispatch_paths[1]: (
            "普通 subagent 默认共享", "isolation: worktree", "Agent Teams", "不自动创建 worktree",
            "不依赖自动 merge", "fresh/origin default", "baseline_anchor", "WorktreeCreate",
            "当前派发", "调度 DAG", "具名 `Agent`", "任一 agent 完成", "general-purpose",
            "SendMessage", "Explore", "Plan", "实验性", "/resume", "实际平台容量",
            "环境变量默认值", "Author、Critic、Coder、Reviewer、Verifier、Integrator",
            "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1", "不等于必须采用", "agent-unavailable",
            "不能声称做原身份的定向复核", "同一 Verifier", "同一 Integrator",
            "跨任务", "create_thread", "list_threads", "read_thread", "wait_threads",
            "send_message_to_thread", "只读", "一张卡", "递归创建主任务",
            "本轮授权", "clientThreadId", "threadId", "hostId", "第一次阻塞等待",
            "timeoutMs: 0",
            "唯一静态执行权威", "父会话历史", "fork_turns", "fork_context",
            "不是逐 agent 的 `Handoff`", "只存在于聊天", "write-task",
        ),
    }
    for path, tokens in adapter_tokens.items():
        require_tokens(errors, path.read_text(encoding="utf-8"), tokens, str(path))

    require_tokens(
        errors,
        parsed.get("gmgn", ("", ""))[1],
        (
            "author-active", "author-returned", "candidate-anchored", "critic-active",
            "critic-returned", "author-revising", "critic-rechecking", "author_ref",
            "critic_ref", "agent-unavailable", "Integrator", "node-complete",
            "lane_key = project_scope_id + card_id", "owner_thread_id", "owner_run_id",
            "ownership_epoch", "owner-unreachable", "claim/bind/verify",
            "cross-task fan-out", "worker main task", "read-only bootstrap",
            "recursively create main tasks", "clientThreadId", "threadId + hostId",
            "candidate-awaiting-anchor", "review-authorized",
        ),
        "gmgn 路由",
    )

    for name in DOCUMENT_NODE_SKILLS:
        require_tokens(
            errors,
            parsed.get(name, ("", ""))[1],
            (
                "author_ref", "author-returned", "candidate-anchored", "critic-returned",
                "same Author", "critic-rechecking", "Integrator", "node-complete",
            ),
            name,
        )

    require_tokens(
        errors,
        parsed.get("run-task", ("", ""))[1],
        (
            "coder_ref", "coder-returned", "same Coder", "reviewer_ref", "same Reviewer",
            "reviewer-rechecking", "verifier-active", "verifier-returned", "Integrator",
            "project_scope_id", "lane_key", "owner_thread_id", "owner_run_id",
            "ownership_epoch", "owner-unreachable", "run_id", "card_id", "workspace_mode",
            "worktree_path", "branch_ref",
            "write_set", "conflict_domains", "runtime_locks", "integration_queue_ref",
            "shared_baseline_anchor", "repository_identity", "workspace-prepared", "integration-queued",
            "integration-conflict", "rebase-required", "post-integration-verifying",
            "git rev-parse --show-toplevel", "does not resolve", "same branch",
            "Recompute the ready set", "instead of waiting for a card or wave to close",
            "does not write implementation", "scripts/lane_registry.py", "update-ref",
            "node-complete", "cancel-unbound", "candidate-awaiting-anchor",
            "review-authorized", "clientThreadId", "threadId", "hostId", "timeoutMs: 0",
        ),
        "run-task",
    )

    run_task = parsed.get("run-task", ("", ""))[1]
    require_section_tokens(
        errors,
        run_task,
        "## Dispatch context for every lane",
        (
            "critic-reviewed `Task.md` card", "only static execution authority",
            "parent conversation history", '`fork_turns="none"`', "`fork_context=false`",
            '`fork_turns="all"`', "`fork_context=true`", "minimal runtime dispatch",
            "authority repository or corpus", "not a new `Handoff` artifact",
            "only in chat", "return to `write-task`", "same agent's own history",
        ),
        "run-task 派发上下文",
    )
    require_section_tokens(
        errors,
        run_task,
        "## 2. Provision one isolated workspace per card",
        (
            "git rev-parse --show-toplevel", "${baseline_anchor}^{commit}",
            "git rev-parse HEAD", "rebuild the worktree", "workspace-prepared",
            "candidate_anchor", "old `baseline_anchor`",
        ),
        "run-task 工作区基线锁",
    )
    require_section_tokens(
        errors,
        run_task,
        "## 1. Build and continuously refill the ready set",
        (
            "after every agent return, integration, conflict, or block",
            "instead of waiting for a card or wave to close",
            "does not stop unrelated lanes",
            "actual subagent capacity", "explicitly authorized it for this run",
            "create_thread", "list_threads", "read_thread", "wait_threads",
            "send_message_to_thread", "create_thread` request before the scheduler's first blocking wait",
            "read-only", "independent Codex worktree", "claim → bind-coder → verify",
            "sole owner of the global ready set", "recursively create main tasks",
            "clientThreadId", "threadId", "hostId", "timeoutMs: 0",
            "do not infer or hard-code a subagent or wait-target limit",
        ),
        "run-task 滚动补槽",
    )
    require_section_tokens(
        errors,
        run_task,
        "## 2. Provision one isolated workspace per card",
        (
            "lane_key", "project_scope_id + card_id", "run_id", "owner_thread_id",
            "owner_run_id", "ownership_epoch", "scripts/lane_registry.py",
            "refs/gmgn/lane-registry", "Git common metadata", "different Git repository",
            "update-ref", "compare-and-swap", "atomically `claim`", "canonical `worktree_path`",
            "Thread-local agent absence", "never prove vacancy", "owner-unreachable",
            "do not expire, steal, or recreate it automatically", "tombstone",
            "claim` never accepts `coder_ref", "cancel-unbound", "repository identity",
            "Git object format", "baseline_anchor` still exists",
        ),
        "run-task 全局 lane claim",
    )
    require_section_tokens(
        errors,
        run_task,
        "## 3. Run each card lane independently",
        (
            "stages and commits only this card's `write_set`",
            "detached `HEAD`", "unique `branch_ref`", "parseable local commit SHA",
            "immutable `candidate_anchor`", "without any remote write",
            "registry `anchor`", "registry `verify`", "stale `ownership_epoch`",
            "rejected before review or integration", "read-only agents",
            "second writer lane", "candidate-awaiting-anchor", "review-authorized",
            "missing/wrong `coder_ref`", "write_set",
        ),
        "run-task 候选锚责任",
    )
    require_section_tokens(
        errors,
        run_task,
        "## 4. Serialize integration, then close the card",
        (
            "Integration is two-phase", "isolated temporary combination workspace",
            "without advancing the shared anchor", "does not by itself require a rebase",
            "dependency or specification meaning", "current `workspace_mode`",
            "current `worktree_path`", "current `branch_ref`", "same `verifier_ref`",
            "abort the Git operation", "discard the temporary combination workspace",
            "leave the original `shared_baseline_anchor` unchanged", "git status --short",
            "atomically advance `shared_baseline_anchor`",
            "Never expose an unverified temporary combination as the shared baseline",
        ),
        "run-task 两阶段集成",
    )
    require_tokens(
        errors,
        parsed.get("close-milestone", ("", ""))[1],
        (
            "verifier-active", "verifier-returned", "author_ref", "same closure Author",
            "same Critic/Reviewer", "acceptance-ready", "Integrator", "owner acceptance",
            "node-complete", "shared_baseline_anchor", "integration queue must be empty",
            "rebase-required", "integration-conflict",
        ),
        "close-milestone",
    )

    write_task = parsed.get("write-task", ("", ""))[1]
    require_tokens(
        errors,
        write_task,
        ("depends_on", "write_set", "conflict_domains", "runtime_locks", "semantic owner",
         "six parser-facing columns unchanged", "rolling ready set"),
        "write-task",
    )

    for path, tokens in (
        (
            ROOT / "GMGN.md",
            (
                "lane_key", "project_scope_id", "card_id", "run_id", "owner_thread_id",
                "owner_run_id", "ownership_epoch", "atomic compare-and-swap claim",
                "canonical `worktree_path`", "Cross-task thread scans", "owner-unreachable",
                "read-only agents", "cross-task fan-out for this run", "worker",
                "only owner of the global ready set", "create more main tasks",
                "clientThreadId", "threadId + hostId", "first blocking wait",
                "never hard-code", "candidate-awaiting-anchor", "review-authorized",
                "only static execution authority", "parent conversation history",
                "minimal runtime dispatch", "not a per-agent Handoff",
            ),
        ),
        (
            ROOT / "GMGN.zh-CN.md",
            (
                "lane_key", "project_scope_id", "card_id", "run_id", "owner_thread_id",
                "owner_run_id", "ownership_epoch", "原子 compare-and-swap claim",
                "canonical `worktree_path`", "跨任务扫描", "owner-unreachable",
                "只读共存", "本轮跨任务", "worker", "全局 ready set",
                "创建主任务", "clientThreadId", "threadId + hostId",
                "第一次阻塞等待", "不得写死", "candidate-awaiting-anchor",
                "review-authorized",
                "唯一静态执行权威", "父会话历史", "最小运行态派发",
                "不是逐 agent Handoff",
            ),
        ),
        (
            REFERENCES / "en" / "preflight-checklist.md",
            (
                "Global writer claim", "lane_key = project_scope_id + card_id",
                "owner_thread_id", "owner_run_id", "ownership_epoch", "coder_ref",
                "canonical `worktree_path`", "claim → bind-coder → verify", "only diagnostic",
                "owner-unreachable", "repository_identity", "baseline_anchor",
            ),
        ),
        (
            REFERENCES / "zh-CN" / "preflight-checklist.md",
            (
                "全局 writer claim", "lane_key = project_scope_id + card_id",
                "owner_thread_id", "owner_run_id", "ownership_epoch", "coder_ref",
                "canonical `worktree_path`", "claim → bind-coder → verify", "只是一项诊断",
                "owner-unreachable", "repository_identity", "baseline_anchor",
            ),
        ),
        (
            REFERENCES / "en" / "pre-merge-checklist.md",
            (
                "Ownership freshness", "project_scope_id", "lane_key", "owner_thread_id",
                "owner_run_id", "ownership_epoch", "coder_ref", "atomic `anchor`",
                "candidate-awaiting-anchor", "review-authorized", "missing/wrong Coder",
                "replaced repository rejected before review and integration",
            ),
        ),
        (
            REFERENCES / "zh-CN" / "pre-merge-checklist.md",
            (
                "所有权新鲜度", "project_scope_id", "lane_key", "owner_thread_id",
                "owner_run_id", "ownership_epoch", "coder_ref", "原子 `anchor`",
                "candidate-awaiting-anchor", "review-authorized", "缺失/错误 Coder",
                "被替换仓库是否在审查、集成前被拒绝",
            ),
        ),
    ):
        require_tokens(errors, path.read_text(encoding="utf-8"), tokens, str(path))

    forbidden_serial = (
        "Execute one task card at a time",
        "continue `run-task` only after the next card is confirmed",
        "Implement one task card",
        "单卡收卡后再进入下一卡",
    )
    serial_files = (ROOT / "GMGN.md", ROOT / "GMGN.zh-CN.md", SKILLS / "run-task" / "SKILL.md")
    for path in serial_files:
        text = path.read_text(encoding="utf-8")
        found = [phrase for phrase in forbidden_serial if phrase in text]
        if found:
            errors.append(f"{path}: 残留 milestone-wide 单卡串行屏障 {found}")

    false_worktree_claims = (
        "worktree resolves merge conflicts", "worktree eliminates merge conflicts",
        "Worktree 解决冲突", "worktree 消除冲突",
    )
    for path in (ROOT / "GMGN.md", ROOT / "GMGN.zh-CN.md", *dispatch_paths):
        text = path.read_text(encoding="utf-8")
        found = [claim for claim in false_worktree_claims if claim in text]
        if found:
            errors.append(f"{path}: 把 worktree 误写成冲突解决机制 {found}")

    unconditional_rebase = (
        "baseline advanced, enter `rebase-required`",
        "shared_baseline_anchor` advanced; the same Coder",
        "shared_baseline_anchor 前移时标 rebase-required",
        "共享基线前移用 `rebase-required`",
    )
    protocol_files = (
        ROOT / "GMGN.md", ROOT / "GMGN.zh-CN.md", SKILLS / "run-task" / "SKILL.md",
        *dispatch_paths, CLAUDE_AGENTS / "integrator.md", CODEX_AGENTS / "integrator.toml",
    )
    for path in protocol_files:
        text = path.read_text(encoding="utf-8")
        found = [claim for claim in unconditional_rebase if claim in text]
        if found:
            errors.append(f"{path}: 基线前移被错误升级为无条件 rebase {found}")

    general_role_tokens = {
        "author": (("write-*", "close-milestone", "current dispatch"),
                   ("write-*", "close-milestone", "当前派发")),
        "reviewer": (("run-task", "close-milestone", "current dispatch"),
                     ("run-task", "close-milestone", "当前派发")),
        "verifier": (("run-task", "close-milestone", "current dispatch", "same `verifier_ref`"),
                     ("run-task", "close-milestone", "当前派发", "同一 verifier_ref")),
        "integrator": (("write-*", "close-milestone", "run-task", "temporary"),
                       ("write-*", "close-milestone", "run-task", "临时")),
    }
    for name, (claude_tokens, codex_tokens) in general_role_tokens.items():
        for path, tokens in (
            (CLAUDE_AGENTS / f"{name}.md", claude_tokens),
            (CODEX_AGENTS / f"{name}.toml", codex_tokens),
        ):
            try:
                text = path.read_text(encoding="utf-8")
            except FileNotFoundError:
                continue
            require_tokens(errors, text, tokens, str(path))

    for path in (
        CLAUDE_AGENTS / "author.md", CLAUDE_AGENTS / "coder.md",
        CODEX_AGENTS / "author.toml", CODEX_AGENTS / "coder.toml",
    ):
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            errors.append(str(exc))
            continue
        require_tokens(
            errors,
            text,
            ("git rev-parse HEAD", "baseline_anchor", "candidate_anchor"),
            f"{path} writer 基线锁",
        )

    for path, tokens in (
        (
            ROOT / "GMGN.md",
            ("Node runtime lifecycle", "same Author", "same Critic", "agent-unavailable"),
        ),
        (
            ROOT / "GMGN.zh-CN.md",
            ("节点运行态与 agent 身份", "同一 Author", "同一 Critic", "agent-unavailable"),
        ),
    ):
        require_tokens(errors, path.read_text(encoding="utf-8"), tokens, str(path))


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
    validate_lane_registry(errors)
    validate_controlled_change_protocol(errors, parsed)
    validate_milestone_scope_protocol(errors, parsed)
    validate_agent_lifecycle(errors, parsed)

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
        close_step = re.search(
            r"^## 4\. Serialize integration, then close the card\n(.*?)(?=^## |\Z)",
            body,
            re.M | re.S,
        )
        required = (
            "Move an accepted lane", "integration-queued", "post-integration-verifying",
            "node-complete",
            "same Integrator", "same Verifier", "shared_baseline_anchor", "Task.md",
            "stale assertions", "not-started", "not created", "not run",
            "awaiting confirmation", "Mechanically refresh", "git diff --check",
            "Only now set the card work status to `closed`",
        )
        if not close_step or any(token not in close_step.group(1) for token in required):
            errors.append("run-task: 卡关账前缺少过期断言扫描")

    for path in (
        REFERENCES / "en" / "writing-contract.md",
        REFERENCES / "zh-CN" / "writing-contract.md",
    ):
        text = path.read_text(encoding="utf-8")
        required = (
            ("runtime candidate `accepted`", "never makes the task `closed`",
             "shared_baseline_anchor", "post-integration verification")
            if path.parent.name == "en"
            else ("运行时候选进入 `accepted`", "不能把任务标成 `closed`",
                  "shared_baseline_anchor", "集成后验证")
        )
        if any(token not in text for token in required):
            errors.append(f"{path}: 缺分支接受与任务关账边界")

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
    for directory in (ROOT / ".claude-plugin", ROOT / ".codex-plugin", CLAUDE_AGENTS, SKILLS):
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

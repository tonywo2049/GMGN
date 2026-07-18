#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_VALIDATOR="${SKILL_VALIDATOR:-$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py}"
PLUGIN_VALIDATOR="${PLUGIN_VALIDATOR:-$HOME/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py}"

python3 "$ROOT/tests/validate_skills.py"

if [[ -f "$SKILL_VALIDATOR" ]] && python3 -c 'import yaml' >/dev/null 2>&1; then
  for skill in "$ROOT"/skills/*; do
    python3 "$SKILL_VALIDATOR" "$skill"
  done
fi

python3 -m json.tool "$ROOT/.claude-plugin/plugin.json" >/dev/null
python3 -m json.tool "$ROOT/.claude-plugin/marketplace.json" >/dev/null
python3 -m json.tool "$ROOT/.codex-plugin/plugin.json" >/dev/null
python3 -m json.tool "$ROOT/.agents/plugins/marketplace.json" >/dev/null

if [[ -f "$PLUGIN_VALIDATOR" ]] && python3 -c 'import yaml' >/dev/null 2>&1; then
  python3 "$PLUGIN_VALIDATOR" "$ROOT"
fi

if command -v claude >/dev/null 2>&1; then
  claude plugin validate "$ROOT"
fi

echo "GMGN 发布前静态校验通过"

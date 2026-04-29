#!/bin/bash
# bountykit client bootstrap

set -euo pipefail

CLIENT="claude"
DRY_RUN="false"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"

usage() {
    cat <<'EOF'
Usage: ./bootstrap.sh [--client claude|codex|opencode|all] [--dry-run]

Targets:
  claude    Install tracks plus playbooks into ~/.claude
  codex     Install tracks into ~/.codex/skills
  opencode  Copy the example Opencode config into ~/.config/opencode
  all       Run all of the above
EOF
}

run() {
    if [ "${DRY_RUN}" = "true" ]; then
        printf '[dry-run] %s\n' "$*"
    else
        eval "$@"
    fi
}

copy_tracks() {
    local dest_root="$1"
    run "mkdir -p \"$dest_root\""
    for track_dir in "$SCRIPT_DIR"/tracks/*/; do
        local track_name
        track_name=$(basename "$track_dir")
        run "mkdir -p \"$dest_root/$track_name\""
        run "cp \"$track_dir/SKILL.md\" \"$dest_root/$track_name/SKILL.md\""
        echo "✓ Installed track: ${track_name}"
    done
}

install_claude() {
    local skills_dir="${HOME}/.claude/skills"
    local commands_dir="${HOME}/.claude/commands"

    echo "Installing Claude-facing bountykit assets..."
    copy_tracks "${skills_dir}"
    run "mkdir -p \"$commands_dir\""
    for playbook_file in "$SCRIPT_DIR"/playbooks/*.md; do
        local playbook_name
        playbook_name=$(basename "$playbook_file")
        run "cp \"$playbook_file\" \"$commands_dir/$playbook_name\""
        echo "✓ Installed playbook: ${playbook_name}"
    done

    # Install MCP server configs if Claude config exists
    local claude_config="${HOME}/.claude/config.json"
    if [ -f "$claude_config" ]; then
        echo "MCP configs available in mcp/mcp-config.json — merge into ${claude_config} manually."
    else
        echo "Note: MCP configs available in mcp/mcp-config.json for Burp Suite and HackerOne integration."
    fi

    echo "Claude tracks installed to ${skills_dir}"
    echo "Claude playbooks installed to ${commands_dir}"
}

install_codex() {
    local skills_dir="${HOME}/.codex/skills"

    echo "Installing Codex-facing bountykit tracks..."
    copy_tracks "${skills_dir}"
    echo "Codex tracks installed to ${skills_dir}"
    echo "Use this repo's AGENTS.md inside the working tree for Codex guidance."
}

install_opencode() {
    local opencode_dir="${HOME}/.config/opencode"
    local example_dest="${opencode_dir}/opencode-bountykit.example.json"

    echo "Installing Opencode example config..."
    run "mkdir -p \"$opencode_dir\""
    run "sed -e \"s|__BOUNTYKIT_ROOT__|${SCRIPT_DIR}|g\" -e \"s|__HOME__|${HOME}|g\" \"$SCRIPT_DIR/clients/opencode/opencode.example.json\" > \"$example_dest\""
    echo "Opencode example config copied to ${example_dest}"
    echo "Merge the skills, agent, and command sections into your active ~/.config/opencode/opencode.json."
}

while [ $# -gt 0 ]; do
    case "$1" in
        --client)
            if [ $# -lt 2 ]; then
                echo "Missing value for --client" >&2
                usage
                exit 1
            fi
            CLIENT="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN="true"
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage
            exit 1
            ;;
    esac
done

case "${CLIENT}" in
    claude)
        install_claude
        ;;
    codex)
        install_codex
        ;;
    opencode)
        install_opencode
        ;;
    all)
        install_claude
        echo ""
        install_codex
        echo ""
        install_opencode
        ;;
    *)
        echo "Unsupported client: ${CLIENT}" >&2
        usage
        exit 1
        ;;
esac

echo ""
echo "Bootstrap complete."

#!/bin/bash
# Pre-check hook script for Skill tool
# Reads tool input from stdin, extracts skill name, runs quick security check
# Exit 0 = allow, Exit 2 = block (with message to stderr)

set -e

# Read JSON from stdin
INPUT=$(cat)

# Extract skill name from tool input
SKILL_NAME=$(echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
tool_input = data.get('tool_input', {})
print(tool_input.get('skill', ''))
" 2>/dev/null)

if [ -z "$SKILL_NAME" ]; then
    exit 0
fi

# Skip checking ourselves
if [ "$SKILL_NAME" = "skill-security-check" ]; then
    exit 0
fi

# Resolve skill directory - check common locations
SKILL_DIR=""
for dir in \
    "$HOME/.claude/skills/$SKILL_NAME" \
    "$HOME/.claude/skills/"*"/$SKILL_NAME" \
    ".claude/skills/$SKILL_NAME"; do
    if [ -d "$dir" ] && [ -f "$dir/SKILL.md" ]; then
        SKILL_DIR="$dir"
        break
    fi
done

# Also check if skill name contains colon (namespaced skill like "anthropic-skills:pdf")
if [ -z "$SKILL_DIR" ]; then
    # Namespaced skills are managed by Claude, skip checking
    exit 0
fi

if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
    exit 0
fi

CRITICAL=0
WARNINGS=""

# Quick Check 1: Dynamic injection commands
if grep -q '!`' "$SKILL_DIR/SKILL.md" 2>/dev/null; then
    # Check if any are dangerous (not just git/gh)
    if grep '!`' "$SKILL_DIR/SKILL.md" 2>/dev/null | grep -iqE 'curl|wget|ssh|nc |eval|rm |cat.*ssh|cat.*env|cat.*aws|base64|\| *bash|\| *sh'; then
        CRITICAL=1
        WARNINGS="$WARNINGS\n  [CRITICAL] Dangerous dynamic injection command found in SKILL.md"
    fi
fi

# Quick Check 2: Scripts with dangerous patterns
if [ -d "$SKILL_DIR/scripts" ]; then
    for script in "$SKILL_DIR/scripts/"*; do
        [ -f "$script" ] || continue
        BASENAME=$(basename "$script")

        # Check for data exfiltration (piping to curl/nc)
        if grep -qE '\| *(curl|nc|ncat|wget)' "$script" 2>/dev/null; then
            CRITICAL=1
            WARNINGS="$WARNINGS\n  [CRITICAL] $BASENAME: Possible data exfiltration (pipe to network command)"
        fi

        # Check for remote code execution
        if grep -qE '(curl|wget).*\| *(bash|sh|python|node)' "$script" 2>/dev/null; then
            CRITICAL=1
            WARNINGS="$WARNINGS\n  [CRITICAL] $BASENAME: Remote code execution pattern detected"
        fi

        # Check for sensitive file reads being sent somewhere
        if grep -qE '(\.ssh/|\.aws/|\.env|credentials|id_rsa)' "$script" 2>/dev/null; then
            if grep -qE '(curl|wget|nc|http)' "$script" 2>/dev/null; then
                CRITICAL=1
                WARNINGS="$WARNINGS\n  [CRITICAL] $BASENAME: Reads sensitive files AND has network access"
            fi
        fi
    done
fi

# Quick Check 3: Hooks in frontmatter (auto-execute on lifecycle)
if head -20 "$SKILL_DIR/SKILL.md" | grep -qE '^hooks:'; then
    WARNINGS="$WARNINGS\n  [WARNING] Skill defines hooks that auto-execute commands"
fi

# Quick Check 4: Hidden content
if grep -qP '[\x{200B}\x{200C}\x{200D}\x{FEFF}]' "$SKILL_DIR/SKILL.md" 2>/dev/null; then
    CRITICAL=1
    WARNINGS="$WARNINGS\n  [CRITICAL] Zero-width/invisible characters detected - possible prompt injection"
fi

if [ $CRITICAL -eq 1 ]; then
    echo "BLOCKED: Skill '$SKILL_NAME' failed security pre-check:$WARNINGS"
    echo ""
    echo "Run /skill-security-check $SKILL_DIR for a full audit."
    exit 2
fi

if [ -n "$WARNINGS" ]; then
    echo "Skill '$SKILL_NAME' passed pre-check with warnings:$WARNINGS"
fi

exit 0

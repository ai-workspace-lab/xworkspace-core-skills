#!/bin/bash
# Skill Security Scanner - Automated pattern detection
# Usage: bash scan.sh <skill-directory-path>

set -e

SKILL_DIR="$1"

if [ -z "$SKILL_DIR" ]; then
    echo "ERROR: Please provide a skill directory path"
    echo "Usage: bash scan.sh <skill-directory-path>"
    exit 1
fi

if [ ! -d "$SKILL_DIR" ]; then
    echo "ERROR: Directory not found: $SKILL_DIR"
    exit 1
fi

echo "============================================"
echo "  Automated Security Scan"
echo "  Target: $SKILL_DIR"
echo "============================================"
echo ""

# Count files
FILE_COUNT=$(find "$SKILL_DIR" -type f | wc -l)
echo "Files found: $FILE_COUNT"
echo ""

# List all files
echo "--- File List ---"
find "$SKILL_DIR" -type f -exec ls -lh {} \;
echo ""

# Check 1: Dynamic injection commands
echo "--- Check 1: Dynamic Injection Commands (!command) ---"
if grep -rn '!\`' "$SKILL_DIR" 2>/dev/null; then
    echo "[!] Dynamic injection commands found above"
else
    echo "[OK] No dynamic injection commands found"
fi
echo ""

# Check 2: Network requests
echo "--- Check 2: Network Requests ---"
if grep -rn -iE 'curl |wget |fetch\(|nc |ncat |ssh |scp |rsync |http://|https://' "$SKILL_DIR" 2>/dev/null; then
    echo "[!] Network-related patterns found above"
else
    echo "[OK] No network request patterns found"
fi
echo ""

# Check 3: Sensitive file access
echo "--- Check 3: Sensitive File Access ---"
if grep -rn -iE '\.ssh/|\.aws/|\.env|credentials|\.gitconfig|\.npmrc|\.pypirc|id_rsa|id_ed25519|\.kube/|\.docker/' "$SKILL_DIR" 2>/dev/null; then
    echo "[!] Sensitive file access patterns found above"
else
    echo "[OK] No sensitive file access patterns found"
fi
echo ""

# Check 4: Sensitive data keywords
echo "--- Check 4: Sensitive Data Keywords ---"
if grep -rn -iE 'password|passwd|secret|token|api.?key|private.?key|access.?key' "$SKILL_DIR" 2>/dev/null; then
    echo "[!] Sensitive data keywords found above"
else
    echo "[OK] No sensitive data keywords found"
fi
echo ""

# Check 5: Destructive commands
echo "--- Check 5: Destructive Commands ---"
if grep -rn -E 'rm -rf|rm -f |chmod 777|mkfs|dd if=|:\(\)\{|fork bomb' "$SKILL_DIR" 2>/dev/null; then
    echo "[!] Destructive command patterns found above"
else
    echo "[OK] No destructive command patterns found"
fi
echo ""

# Check 6: Code execution / eval
echo "--- Check 6: Code Execution Patterns ---"
if grep -rn -E '\beval\b|\bexec\b|bash -c|sh -c|python -c|python3 -c|node -e|ruby -e|\| ?bash|\| ?sh' "$SKILL_DIR" 2>/dev/null; then
    echo "[!] Code execution patterns found above"
else
    echo "[OK] No code execution patterns found"
fi
echo ""

# Check 7: Privilege escalation
echo "--- Check 7: Privilege Escalation ---"
if grep -rn -E '\bsudo\b|\bsu\b|\bchown\b|\bchmod\b' "$SKILL_DIR" 2>/dev/null; then
    echo "[!] Privilege escalation patterns found above"
else
    echo "[OK] No privilege escalation patterns found"
fi
echo ""

# Check 8: Hidden content (HTML comments)
echo "--- Check 8: Hidden Content (HTML Comments) ---"
if grep -rn '<!--' "$SKILL_DIR" 2>/dev/null; then
    echo "[!] HTML comments found above - review for hidden instructions"
else
    echo "[OK] No HTML comments found"
fi
echo ""

# Check 9: Base64 patterns
echo "--- Check 9: Base64 Encoded Content ---"
if grep -rn -E '[A-Za-z0-9+/]{40,}={0,2}' "$SKILL_DIR" 2>/dev/null; then
    echo "[!] Possible base64 encoded content found above"
else
    echo "[OK] No suspicious base64 patterns found"
fi
echo ""

# Check 10: Hooks in frontmatter
echo "--- Check 10: Hooks Configuration ---"
if grep -rn -E '^hooks:|pre-tool-use|post-tool-use|pre-message|post-message' "$SKILL_DIR" 2>/dev/null; then
    echo "[!] Hooks configuration found - commands may auto-execute"
else
    echo "[OK] No hooks configuration found"
fi
echo ""

# Check 11: allowed-tools in frontmatter
echo "--- Check 11: Allowed Tools ---"
if grep -rn 'allowed-tools' "$SKILL_DIR" 2>/dev/null; then
    echo "[i] Review the tool permissions above"
else
    echo "[OK] No allowed-tools specified"
fi
echo ""

echo "============================================"
echo "  Automated Scan Complete"
echo "============================================"

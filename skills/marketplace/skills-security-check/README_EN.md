# Skill Security Checker

A security auditing tool for third-party Claude Code Skills. Automatically pre-checks any Skill before execution to block dangerous ones, and supports manual deep audits.

## How It Works

```
Claude invokes any Skill
       |
       v
PreToolUse Hook intercepts (settings.json)
       |
       v
pre-check.sh runs quick security scan
       |
   +---+---+
   |       |
 Safe   Dangerous
   |       |
   v       v
 Allow   Block & alert
```

## File Structure

```
~/.claude/skills/skill-security-check/
├── README.md              # Chinese documentation
├── README_EN.md           # This file
├── SKILL.md               # Skill definition: deep audit logic and report format
├── install.sh             # One-click installation script
└── scripts/
    ├── scan.sh            # Full scan script (used during manual audit)
    └── pre-check.sh       # Lightweight pre-check script (called by Hook automatically)
```

Additionally modifies:

```
~/.claude/settings.json    # Adds PreToolUse Hook configuration
```

## Installation

### One-Click Install (Recommended)

```bash
bash install.sh
```

The script automatically:

1. Creates `~/.claude/skills/skill-security-check/` directory
2. Writes `SKILL.md`, `scan.sh`, and `pre-check.sh`
3. Sets executable permissions on scripts
4. Merges PreToolUse Hook into `~/.claude/settings.json` (existing config is preserved, original file backed up as `.bak`)

**Restart Claude Code session** after installation to activate.

### Remote Installation

```bash
# Copy the install directory to the target machine
scp -r ~/.claude/skills/skill-security-check user@target:~/skill-security-check/

# SSH into target machine and run install
ssh user@target "bash ~/skill-security-check/install.sh"
```

### Manual Installation

1. Copy the entire `skill-security-check` directory to `~/.claude/skills/`
2. Set executable permissions:
   ```bash
   chmod +x ~/.claude/skills/skill-security-check/scripts/*.sh
   ```
3. Edit `~/.claude/settings.json` and add the Hook configuration:
   ```json
   {
     "hooks": {
       "PreToolUse": [
         {
           "matcher": "Skill",
           "hooks": [
             {
               "type": "command",
               "command": "bash ~/.claude/skills/skill-security-check/scripts/pre-check.sh"
             }
           ]
         }
       ]
     }
   }
   ```
   If `settings.json` already has other configurations, merge the Hook entry into the `hooks.PreToolUse` array.
4. Restart Claude Code session.

## Usage

### Automatic Protection (No Action Required)

Once installed, every time Claude invokes any Skill, the Hook automatically runs `pre-check.sh` for a quick security check:

- Check passes: Skill executes normally
- Critical risk found: Execution blocked with alert message

### Manual Deep Audit

```
/skill-security-check <skill-directory-path>
```

Example:

```
/skill-security-check ~/.claude/skills/some-third-party-skill
```

Outputs a full security audit report with risk levels and detailed findings.

## Security Checks

### Quick Pre-Check (pre-check.sh)

Runs automatically on every Skill invocation, completes in milliseconds:

| Check | Trigger Condition | Level |
|-------|------------------|-------|
| Dangerous dynamic injection | SKILL.md contains curl/wget/ssh in dynamic injection syntax | CRITICAL |
| Data exfiltration | Scripts pipe output to curl/nc | CRITICAL |
| Remote code execution | Scripts contain curl \| bash pattern | CRITICAL |
| Sensitive files + network | Scripts access .ssh/.aws/.env AND have network requests | CRITICAL |
| Invisible characters | SKILL.md contains zero-width characters (possible prompt injection) | CRITICAL |
| Auto-execute hooks | Frontmatter defines lifecycle hooks | WARNING |

### Full Deep Scan (scan.sh)

Triggered manually, covers comprehensive checks:

| Check | Description |
|-------|-------------|
| Dynamic injection commands | Searches all files for dynamic injection syntax |
| Network requests | curl, wget, fetch, nc, ssh, scp, rsync |
| Sensitive file access | .ssh/, .aws/, .env, credentials, id_rsa, etc. |
| Sensitive data keywords | password, secret, token, api_key, etc. |
| Destructive commands | rm -rf, chmod 777, mkfs, dd, fork bomb |
| Code execution | eval, exec, bash -c, python -c, pipe to bash |
| Privilege escalation | sudo, su, chown, chmod |
| Hidden content | HTML comments, Base64 encoded strings |
| Hook configuration | pre-tool-use, post-tool-use lifecycle hooks |
| Tool permissions | Bash/Write/Edit in allowed-tools |

## Audit Report Example

```
============================================
  Skill Security Audit Report
============================================

Skill: some-skill
Path:  ~/.claude/skills/some-skill
Files: 3 files scanned

--------------------------------------------
  Overall Risk Level: MEDIUM
--------------------------------------------

## Frontmatter Analysis
- allowed-tools: Read, Bash -> Medium (Bash can execute commands)
- hooks: none -> OK

## Dynamic Injection Commands
- None found -> OK

## Script Analysis
- setup.sh: contains curl call to download template -> Medium

## Detailed Findings

### Medium Risks
1. scripts/setup.sh:12 — curl used to download file template

### Low Risks / Info
1. SKILL.md:6 — allowed-tools includes Bash

--------------------------------------------
  Recommendation: USE WITH CAUTION
--------------------------------------------
```

## Uninstall

1. Remove the Skill directory:
   ```bash
   rm -rf ~/.claude/skills/skill-security-check
   ```
2. Edit `~/.claude/settings.json` and remove the `PreToolUse` entry with matcher `Skill`
3. Restart Claude Code session

## Dependencies

- bash
- python3 (used by install.sh for merging settings.json)
- grep (with -E extended regex and -P Perl regex support)

## Notes

- The install script automatically skips checking itself to avoid false positives
- Built-in Skills (e.g. `anthropic-skills:pdf`) are automatically skipped
- Pre-check only blocks critical risks (CRITICAL); general risks pass through with warnings
- To also block general risks, modify the exit logic in `pre-check.sh`

# Skill Security Checker

Claude Code 第三方 Skill 安全检查工具。在执行任何 Skill 前自动进行安全预检，拦截危险 Skill；也支持手动触发深度审计。

## 工作原理

```
Claude 调用任意 Skill
       |
       v
PreToolUse Hook 拦截 (settings.json)
       |
       v
pre-check.sh 快速安全扫描
       |
   +---+---+
   |       |
 安全    危险
   |       |
   v       v
 放行    阻止并提示
```

## 文件结构

```
~/.claude/skills/skill-security-check/
├── README.md              # 本文件
├── SKILL.md               # Skill 主文件，定义深度审计的检查逻辑和报告格式
├── install.sh             # 一键安装脚本
└── scripts/
    ├── scan.sh            # 完整扫描脚本（手动审计时调用）
    └── pre-check.sh       # 轻量前置检查脚本（Hook 自动调用）
```

另外会修改：

```
~/.claude/settings.json    # 添加 PreToolUse Hook 配置
```

## 安装

### 一键安装（推荐）

```bash
bash install.sh
```

脚本会自动完成以下操作：

1. 创建 `~/.claude/skills/skill-security-check/` 目录
2. 写入 `SKILL.md`、`scan.sh`、`pre-check.sh`
3. 设置脚本执行权限
4. 将 PreToolUse Hook 合并到 `~/.claude/settings.json`（已有配置不会覆盖，原文件备份为 `.bak`）

安装完成后**重启 Claude Code 会话**即可生效。

### 远程安装

```bash
# 将安装目录复制到目标机器
scp -r ~/.claude/skills/skill-security-check user@target:~/skill-security-check/

# SSH 到目标机器执行安装
ssh user@target "bash ~/skill-security-check/install.sh"
```

### 手动安装

如果不想用安装脚本，手动操作步骤如下：

1. 将整个 `skill-security-check` 目录复制到 `~/.claude/skills/`
2. 给脚本加执行权限：
   ```bash
   chmod +x ~/.claude/skills/skill-security-check/scripts/*.sh
   ```
3. 编辑 `~/.claude/settings.json`，添加 Hook 配置：
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
   如果 `settings.json` 已有其他配置，将 Hook 条目合并到 `hooks.PreToolUse` 数组中即可。
4. 重启 Claude Code 会话。

## 使用方式

### 自动防护（无需操作）

安装后，每次 Claude 调用任何 Skill 时，Hook 会自动运行 `pre-check.sh` 进行快速安全检查：

- 检查通过 → Skill 正常执行
- 发现严重风险 → 阻止执行，输出告警信息

### 手动深度审计

```
/skill-security-check <skill-目录路径>
```

示例：

```
/skill-security-check ~/.claude/skills/some-third-party-skill
```

会输出完整的安全审计报告，包含风险等级和详细发现。

## 检查项

### 前置快速检查（pre-check.sh）

每次 Skill 调用时自动运行，毫秒级完成：

| 检查项 | 触发条件 | 级别 |
|--------|---------|------|
| 危险动态注入 | SKILL.md 中含 curl/wget/ssh 等的动态注入命令 | CRITICAL |
| 数据外泄 | 脚本中将输出 pipe 到 curl/nc | CRITICAL |
| 远程代码执行 | 脚本中 curl \| bash 模式 | CRITICAL |
| 敏感文件+网络 | 脚本同时访问 .ssh/.aws/.env 并有网络请求 | CRITICAL |
| 不可见字符 | SKILL.md 中含零宽字符（可能是 prompt injection） | CRITICAL |
| 自动执行 Hook | frontmatter 中定义了 hooks | WARNING |

### 完整深度扫描（scan.sh）

手动触发时运行，覆盖更多检查项：

| 检查项 | 说明 |
|--------|------|
| 动态注入命令 | 搜索所有文件中的动态注入语法 |
| 网络请求 | curl, wget, fetch, nc, ssh, scp, rsync |
| 敏感文件访问 | .ssh/, .aws/, .env, credentials, id_rsa 等 |
| 敏感数据关键词 | password, secret, token, api_key 等 |
| 破坏性命令 | rm -rf, chmod 777, mkfs, dd, fork bomb |
| 代码执行 | eval, exec, bash -c, python -c, pipe to bash |
| 权限提升 | sudo, su, chown, chmod |
| 隐藏内容 | HTML 注释、Base64 编码 |
| Hook 配置 | pre-tool-use, post-tool-use 等生命周期钩子 |
| 工具权限 | allowed-tools 中的 Bash/Write/Edit 权限 |

## 审计报告示例

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

## 卸载

1. 删除 Skill 目录：
   ```bash
   rm -rf ~/.claude/skills/skill-security-check
   ```
2. 编辑 `~/.claude/settings.json`，移除 `PreToolUse` 中 matcher 为 `Skill` 的条目
3. 重启 Claude Code 会话

## 依赖

- bash
- python3（install.sh 合并 settings.json 时使用）
- grep（支持 -E 扩展正则和 -P Perl 正则）

## 注意事项

- 安装脚本会自动跳过对自身的检查，避免误报
- 内置 Skill（如 `anthropic-skills:pdf`）会自动跳过检查
- 前置检查只拦截严重风险（CRITICAL），一般风险会通过并输出警告
- 如需对一般风险也进行拦截，可修改 `pre-check.sh` 中的退出逻辑

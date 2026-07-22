---
name: ai-agent-collaboration-standard
description: AI Workspace Infra 人机协作与安全执行纪律。用于维护 artifacts、docs、gitops、playbooks、iac_modules、observability.svc.plus、platform-ops-toolkit 时的仓库发现、权限边界、脏工作树、PR、部署和破坏性操作决策；涉及代码合入、多环境部署或越权风险时必须遵守。
---

# AI Agent Collaboration Standard

本规范定义了 AI 代理团队（Agents）在研发过程中的绝对行为边界与协作规则。所有参与开发的 Agent 必须将其作为最高行为准则。

先阅读 [AI Workspace Infra Repository Map](../references/ai-workspace-infra-repository-map.md)。该工作区是多个独立仓库；不得把目录相邻误判为同一个提交、CI 或发布单元。

## 1. 角色边界与权限规则

- **人类架构师 (Commander)**：拥有唯一决策权。负责需求下发、架构决策与最终验收。
- **主代理 (Main Agent)**：执行需求拆解、任务调度与进度追踪。禁止越权代替人类做出破坏性决策。
- **子代理 (Sub-Agent)**：在独立的 `feature/*` 或独立上下文中执行单一模块开发任务。

**【强制约定】**：Agent 不得自发更改项目基础设施规则，所有对于构建流程、部署环境或代码分支保护规则的调整，必须获得人类明确许可。

## 2. 核心执行红线

1. **绝对遵循前置规则**：Agent 必须在每次执行前读取并遵守该仓库的 `AGENTS.md`。如果发现自身行为即将违反 `AGENTS.md` 中的红线，必须立即中止并向人类报告。
2. **禁止规避门禁**：严禁使用 `--admin`、`--force` 等参数绕过受保护的分支（如 `main` 或 `release/*`）的代码审查 (Code Review) 与 CI 门禁。
3. **环境路由刚性锁定**：
   - 部署动作只能由**硬性 Git 事件**触发，禁止根据上下文随意变更部署环境。
   - `pull_request` -> SIT 环境
   - `代码合并入 main / release/* (Merged PR)` -> UAT 环境
   - `Tag v*` -> Prod 环境
4. **禁止硬编码凭证**：任何环境的敏感凭证必须通过 CI/CD 平台（如 Vault 配合 OIDC）动态获取，严禁落盘入库。
5. **保留用户现场**：先运行 `git status --short --branch`。未追踪或无关修改默认归用户所有；不得为切换分支、清理测试或方便提交而 reset、checkout、stage、删除它们。
6. **先验证作用域再破坏**：删除 VPS、快照、DNS、Terraform state、Vault metadata 或发布制品前，先只读列出精确目标、影响和回滚点；获得明确授权后才执行。授权删除实例不自动等于授权删除快照、DNS 或 state。

## 3. 标准开发工作流 (SOP)

所有特性开发必须严格遵循以下阶段流转：
1. **隔离开发**：在基于最新主干拉取的 `feature/*` 分支上工作。
2. **状态提交**：每个逻辑变更必须独立提交 (Commit)，严禁将多个无关任务混合提交。
3. **准入拦截**：完成后必须通过创建 PR (Pull Request) 来触发 CI，严禁直推保护分支。
4. **验收与合并**：只有在 required review 与 CI 绿灯通过后，才合并；除非用户明确授权或仓库启用已审查的自动合并，Agent 不得自行决定合并时机。

跨仓修改时，为每个仓建立独立分支、提交、PR 和验证记录。不要把 `gitops` 声明、`iac_modules` 模块、`platform-ops-toolkit` 编排、`playbooks` 主机配置或 `artifacts` 制品混在同一个 PR 中，除非变更是不可分割的兼容性迁移，并在每个 PR 说明另一端依赖。

## 4. 故障与越权应急响应预案

当发生以下灾难场景时，Agent 必须强制执行以下标准恢复路径：

### 4.1 密钥/凭证泄露
- **禁止**：仅通过新 Commit 提交删除文件的操作。
- **强制响应**：
  1. 立刻在凭证提供方（云平台/Vault）吊销该泄露密钥。
  2. 生成替换密钥。
  3. 必须通过 `git filter-repo` 等专用工具从 Git 提交历史中彻底清洗泄露记录。

### 4.2 违规操作与绕过门禁
- **禁止**：继续在此基础上开发或尝试使用其他命令掩盖。
- **强制响应**：立即使用 `git revert` 撤销该次违规合入，将分支状态回滚至安全基线，并在复盘后重新走标准的 PR 流程。

### 4.3 代码/质量门禁失败
- **禁止**：忽略 CI 报错或请求人类放行。
- **强制响应**：读取 CI 日志报错，在原功能分支上追加 Commit 修复问题，直至 CI 流水线状态恢复为绿色。

## 5. 输出格式与模板要求

无论是 Commit Message 还是 Pull Request Body，Agent 必须遵循模板化输出：
- 必须包含**变更摘要**。
- 必须关联**对应的 Issue 或任务链接**。
- 必须附带**测试结果说明**（本地测试步骤或 CI 检查列表）。

---
name: harness-workflow
description: Agent Harness 工作流核心技能。定义了“工程闭环 × 小步快跑”的核心逻辑，并将各项工程标准（协作规范、项目开发、CI/CD、配置/基础设施即代码、多环境发布等）串联入该循环中。
---

# Agent Harness Workflow

**Agent Harness = 工程闭环 (Engineering Closed Loop) × 小步快跑 (Small Steps Iteration)**

本技能是将所有工程标准有机串联的**核心工作流大脑**。所有 Agent 在执行复杂工程任务时，必须将该 Harness 循环作为默认心智模型，严禁脱离此工作流进行“大跨步、无验证、无回滚机制”的莽撞操作。

## 核心工作流图 (Harness Loop)

```mermaid
flowchart TD
    Goal[Goal] --> Analyze[Analyze Current State]
    Analyze --> Plan[Plan the Smallest Change]
    Plan --> Execute[Execute One Step]
    Execute --> Artifact[Generate Verifiable Artifact\n(PR / Contract / Workflow)]
    Artifact --> Validate[Validate & Human Review]
    
    Validate -- Success --> Next[Next Increment]
    Validate -- Failure --> Rollback[Rollback / Replan]
    
    Next -->|Closed Loop| Goal
    Rollback -->|Closed Loop| Analyze
```

## 工作流拆解与标准串联

本 Harness Workflow 规定了在循环的每一个环节中，Agent 必须调用的具体工程标准技能。

### 1. 目标与现状分析 (Goal & Analyze Current State)
接收到人类架构师（Commander）的指令后，禁止直接修改代码。
- **关联标准**：[`references`](../references/)
- **动作**：通过阅读 `references`（如 Repo Map）准确理解系统架构、依赖关系和仓库边界。评估当前环境的状态，确保下一步计划的安全边界。

### 2. 规划最小变更 (Plan the Smallest Change)
基于“小步快跑”原则，将大目标拆解为独立、可验证的最小增量。
- **关联标准**：
  - [`ai-agent-collaboration-standard`](../ai-agent-collaboration-standard/)：遵守权限与角色边界，确定是由主代理分配任务，还是子代理在隔离上下文中执行。
  - [`project-development-standard`](../project-development-standard/)：决定本次“小步”对应的分支策略（是 `feature/*`、`bugfix/*` 还是 `hotfix/*`），严禁混用目标分支。

### 3. 执行单步变更 (Execute One Step)
在隔离的分支中执行具体的编码、配置或基础设施调整。
- **关联标准**：
  - [`config-as-code-spec`](../config-as-code-spec/)：若涉及配置修改，确保配置代码化、声明式。
  - [`infrastructure-as-code-spec`](../infrastructure-as-code-spec/)：若涉及云资源或基础设施变更，确保使用 IaC（如 Terraform）并遵循模块化最佳实践。
- **动作**：保持用户现场整洁（不破坏未追踪文件），遵循单一职责原则进行 Commit。

### 4. 生成可验证制品 (Generate Verifiable Artifact)
执行完毕后，必须生成人类和机器都能验证的交付物（通常为 Pull Request、IaC 变更计划或 CI Workflow）。
- **关联标准**：[`project-development-standard`](../project-development-standard/)
- **动作**：通过创建 PR 触发 CI 流程，严禁使用 `--force` 绕过门禁。提交信息和 PR Body 必须符合标准模板，说明变更内容和验证方式。

### 5. 验证与人类审查 (Validate & Human Review)
所有制品必须经过自动化门禁和（必要时的）人类确认。
- **关联标准**：[`ci-cd-workflow-spec`](../ci-cd-workflow-spec/)
- **动作**：依赖 CI Pipeline 的静态检查、自动化测试、安全扫描进行拦截。若 CI 失败，必须回到 "Execute One Step" 进行修复；严禁忽视 CI 报错强组合入。

### 6. 成功：下一增量与发布 (Success: Next Increment)
验证通过并合入主干后，根据触发条件进入多环境部署，随后继续下一个任务循环。
- **关联标准**：[`multi-environment-delivery-and-release`](../multi-environment-delivery-and-release/)
- **动作**：遵循环境路由刚性锁定（如 PR 对应 SIT，主干合并对应 UAT，打 Tag 对应 Prod）。通过 Git 语义化操作触发 CD 部署，完成本次闭环。

### 7. 失败：回滚与重规划 (Failure: Rollback / Replan)
遇到质量门禁拒绝、安全漏洞或部署失败时，必须进入标准化止损流程。
- **关联标准**：
  - [`ai-agent-collaboration-standard`](../ai-agent-collaboration-standard/)：执行应急响应预案（如凭证泄露强制洗库，违规操作强制 `git revert`）。
  - [`project-development-standard`](../project-development-standard/)：使用对应的故障处理流（如通过 `hotfix/*` 分支修复发布环境问题）。
- **动作**：清理现场，恢复到安全基线，重新回到“现状分析 (Analyze Current State)”节点进行调整。

## 核心心智模型 (Mindset)

对于 Agent 而言，永远不要问“我是不是可以直接推上 `main`？”或“我能不能一次性改完所有文件？”。
请在每一次行动前反问自己：
**“当前的动作是一个闭环吗？步子足够小吗？能通过 PR/CI 验证吗？失败了能安全回滚吗？”** 
严格实践，这就是 Agent Harness。

---
name: harness-workflow
description: Agent Harness 工作流核心技能。定义了“工程闭环 × 小步快跑”的核心逻辑，并将工程标准与运营管理（协作规范、项目开发、CI/CD、配置/基础设施即代码、多环境发布、workflow dispatch、资源生命周期、Vault、DNS、观测和故障闭环）串联入该循环中。
---

# Agent Harness Workflow

**Agent Harness = 工程闭环 (Engineering Closed Loop) × 小步快跑 (Small Steps Iteration)**

本技能是将所有工程标准有机串联的**核心工作流大脑**。所有 Agent 在执行复杂工程任务时，必须将该 Harness 循环作为默认心智模型，严禁脱离此工作流进行“大跨步、无验证、无回滚机制”的莽撞操作。

## 核心工作流图 (Harness Loop)

```mermaid
flowchart TD
    Goal[Goal] --> Source[Anchor the Requirement\n(Issue = Source of Truth)]
    Source --> Analyze[Analyze Current State]
    Analyze --> Plan[Plan the Smallest Change]
    Plan --> Execute[Execute One Step]
    Execute --> Artifact[Generate Verifiable Artifact\n(PR / Contract / Workflow)]
    Artifact --> Validate[Validate & Human Review]
    
    Validate -- Success --> Next[Next Increment]
    Validate -- Failure --> Rollback[Rollback / Replan]
    
    Next -->|Closed Loop| Goal
    Rollback -->|Closed Loop| Analyze
```

循环的入口不是"收到一句话指令"，而是**指令已锚定到一个权威需求载体**。
`Goal → Source` 这一跳如果跳过，后面每一步都在为一个没人能复查的目标干活。

## 工作流拆解与标准串联

本 Harness Workflow 规定了在循环的每一个环节中，Agent 必须调用的具体工程标准技能。

### 0. 锚定需求事实来源 (Anchor the Requirement)
接收到人类架构师（Commander）的指令后，**第一步不是分析代码，而是确认"以谁说的为准"**。
- **关联标准**：[`issue-pr-traceability-standard`](../issue-pr-traceability-standard/)
- **动作**：
  1. 把指令锚定到权威需求载体（Issue 或等价任务单）。没有就先建，并补全目标、
     **可机器判定的验收标准**、影响仓库与环境范围；对话里的新要求先回写，再执行。
  2. **自取上下文，不要人类粘贴**：需求正文与讨论、关联 PR 的评审意见、变更历史、
     CI 失败日志，全部自行读取。允许向人类索取的只有权限之外的信息、判断题与闸门授权。
- **判据**：说不出"本轮的验收标准是什么、写在哪"，就不具备进入下一步的条件。

### 1. 现状分析 (Analyze Current State)
需求锚定之后、动手之前，禁止直接修改代码。
- **关联标准**：[`references`](../references/)
- 涉及 Zero Trust overlay、Gateway、受控客户端或隧道传输时，同时读取
  [`zero-trust-overlay-delivery`](../zero-trust-overlay-delivery/)，先确认控制面、数据面和配置所有权。
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
  - [`zero-trust-overlay-delivery`](../zero-trust-overlay-delivery/)：若涉及覆盖网络，确保目标值来自规范化声明，运行时凭据和 peer 状态不进入 GitOps。
- **动作**：保持用户现场整洁（不破坏未追踪文件），遵循单一职责原则进行 Commit。

### 4. 生成可验证制品 (Generate Verifiable Artifact)
执行完毕后，必须生成人类和机器都能验证的交付物（通常为 Pull Request、IaC 变更计划或 CI Workflow）。
- **关联标准**：
  - [`project-development-standard`](../project-development-standard/)：PR 正文必填项与跨仓 companion PR 互链。
  - [`issue-pr-traceability-standard`](../issue-pr-traceability-standard/)：制品必须回指 §0 锚定的需求——分支、commit、PR 三处都带上需求标识，让链条可反查。
- **动作**：通过创建 PR 触发 CI 流程，严禁使用 `--force` 绕过门禁。提交信息和 PR Body 必须符合标准模板，说明变更内容和验证方式。

### 5. 验证与人类审查 (Validate & Human Review)
所有制品必须经过自动化门禁和（必要时的）人类确认。
- **关联标准**：[`ci-cd-workflow-spec`](../ci-cd-workflow-spec/)
- 改动公开官网、产品页、页脚/联系方式、边缘路由或品牌域名相关流水线时，同时按
  [`store-and-startup-homepage-spec`](../store-and-startup-homepage-spec/) 过 Google/Apple/Android 公司与应用审核的官网门禁（守卫测试 + 线上探针）。
- 覆盖网络变更还必须按
  [`zero-trust-overlay-delivery`](../zero-trust-overlay-delivery/) 区分 ACK、真实 peer handshake 和私网流量验收，避免配置已下发但数据面未通被误判为成功。
- **动作**：依赖 CI Pipeline 的静态检查、自动化测试、安全扫描进行拦截。若 CI 失败，必须回到 "Execute One Step" 进行修复；严禁忽视 CI 报错强组合入。

### 6. 成功：下一增量与发布 (Success: Next Increment)
验证通过并合入主干后，根据触发条件进入多环境部署，随后继续下一个任务循环。
- **关联标准**：
  - [`multi-environment-delivery-and-release`](../multi-environment-delivery-and-release/)：环境路由与发布鉴权。
  - [`issue-pr-traceability-standard`](../issue-pr-traceability-standard/)：**闭环的收尾是回写需求**——带着证据（PR 编号 + CI 结论 + 部署记录）关闭 Issue；证据不全或只完成一部分，就不关，拆剩余项到新 Issue。
- **动作**：遵循环境路由刚性锁定（如 PR 对应 SIT，主干合并对应 UAT，打 Tag 对应 Prod）。通过 Git 语义化操作触发 CD 部署，完成本次闭环。

- **部署后 post-check**：品牌域名所在边界（边缘路由、SSR 公共/内容边界、Pages）部署后，流水线必须运行
  [`store-and-startup-homepage-spec`](../store-and-startup-homepage-spec/) §9 的审核就绪清单；公开页跳出品牌域名、法人名/同域邮箱缺失都视为部署失败，而不是"页面能打开就算成功"。

### 6.1 运营落地与验证闭环 (Operational Realization)

代码合入只是工程闭环的一半。进入部署、资源操作或运行维护后，按
`operations-management` 下的专门技能继续完成运营闭环，不把“workflow
绿色”或“页面显示在线”当作最终证据：

- **GitHub Actions dispatch**：先读取实际 workflow 的输入、默认值和隐含约束，执行本地 preflight；对 destroy、DNS cutover、restore、生产目标和凭证轮换等高风险字段单独确认，然后 dispatch 并独立核验结果。
- **资源生命周期**：先枚举精确资源、所有权、租约、成本和回滚点；Spot、临时节点、快照、IP、DNS、Terraform state 和凭证撤销分别记录，不能把一个清理授权扩展成全部清理。
- **身份与秘密**：验证 workflow 的 OIDC role、`job_workflow_ref`、Vault policy 和实际 KV 读取路径组成完整契约；新增 secret read 必须同时更新配置并由授权身份 apply，使用最小精确路径，禁止用 wildcard 或 dispatch token 绕过 403。
- **网络与服务**：DNS/TLS 变更先验证权威解析、证书和边界可达性；部署后从用户边界和依赖边界分别验证，服务进程、ACK、handshake、私网流量、HTTP 标记和监控数据要区分记录。
- **故障与收尾**：失败时保留脱敏日志和资源状态，按 incident/change runbook containment → evidence → bounded fix → review → deploy → observation window → action closure 执行；预防性 guard 通过可重复测试后才关闭行动项。

对应技能：
[`github-actions-operational-dispatch`](../../operations-management/github-actions-operational-dispatch/)、
[`capacity-cost-and-resource-lifecycle`](../../operations-management/capacity-cost-and-resource-lifecycle/)、
[`secrets-identity-and-access-governance`](../../operations-management/secrets-identity-and-access-governance/)、
[`network-dns-tls-edge-management`](../../operations-management/network-dns-tls-edge-management/)、
[`observability-slo-and-alerting`](../../operations-management/observability-slo-and-alerting/)、
[`incident-response-and-change-management`](../../operations-management/incident-response-and-change-management/)。

### 7. 失败：回滚与重规划 (Failure: Rollback / Replan)
遇到质量门禁拒绝、安全漏洞或部署失败时，必须进入标准化止损流程。
- **关联标准**：
  - [`ai-agent-collaboration-standard`](../ai-agent-collaboration-standard/)：执行应急响应预案（如凭证泄露强制洗库，违规操作强制 `git revert`）。
  - [`project-development-standard`](../project-development-standard/)：使用对应的故障处理流（如通过 `hotfix/*` 分支修复发布环境问题）。
- **动作**：清理现场，恢复到安全基线，重新回到“现状分析 (Analyze Current State)”节点进行调整。
- 覆盖网络故障必须把脱敏后的症状、违反的不变量、责任层、证据和新增 guard
  回写到 [`zero-trust-overlay-delivery`](../zero-trust-overlay-delivery/) 的学习闭环；不得把一次性 IP、主机名或密钥写成新的默认值。

## 核心心智模型 (Mindset)

对于 Agent 而言，永远不要问“我是不是可以直接推上 `main`？”或“我能不能一次性改完所有文件？”。
请在每一次行动前反问自己：
**“当前的动作是一个闭环吗？步子足够小吗？能通过 PR/CI 验证吗？失败了能安全回滚吗？”**

以及在动手之前先问一句：
**“这件事的权威需求写在哪？验收标准能证伪吗？我是不是在等人喂我本来该自己去读的东西？”**

严格实践，这就是 Agent Harness。

# 工程规范与交付标准（Engineering Standards）

> **作者亲身实践·深度总结·实战验证的核心工程资产**

本目录收录的 **13 项工程研发与交付规约**，是面向真实生产环境、多云架构与 AI Agent 团队研发协作的**强制性事实源与纪律红线**。

所有标准以 [`harness-workflow`](../skills/engineering-standards/harness-workflow/SKILL.md) 为研发主控总线，实现「工程闭环 × 小步快跑」。

---

## 13 项工程规范全景表

| 规范名称 | 解决的实战痛点与核心机制 | 规范入口 |
|---|---|---|
| **Agent Harness 工作流** | **研发主控总线**：定义「工程闭环 × 小步快跑」核心循环，统一驱动自测、代码审查、CI/CD 与多环境发布，是串联各项工程标准的唯一入口 | [`skills/engineering-standards/harness-workflow/SKILL.md`](../skills/engineering-standards/harness-workflow/SKILL.md) |
| **Issue/PR 溯源与需求事实源** | **根治口头派活**：需求以 Issue 为唯一事实源，建立 `Issue → 分支 → commit → PR → CI → 部署 → Tag` 完整且可证伪的追溯链，禁止脱离 Issue 自主开工 | [`skills/engineering-standards/issue-pr-traceability-standard/SKILL.md`](../skills/engineering-standards/issue-pr-traceability-standard/SKILL.md) |
| **工程开发规范** | **代码分支纪律**：分支命名矩阵、主干保护、PR 合并策略、不可变 Release Tag 规则，以及代码中不慎误提密钥时的标准化紧急撤回流程 | [`skills/engineering-standards/project-development-standard/SKILL.md`](../skills/engineering-standards/project-development-standard/SKILL.md) |
| **CI/CD 工作流规约** | **消灭流水线假绿**：CI 构建与 CD 部署严格解耦、流水线脚本外置可复用、最小权限 GitHub OIDC 互信、不可变制品签名与假绿防治门禁 | [`skills/engineering-standards/ci-cd-workflow-spec/SKILL.md`](../skills/engineering-standards/ci-cd-workflow-spec/SKILL.md) |
| **四边界执行归属迁移** | **消灭跨仓代码乱窜**：清晰划定 Toolkit、GitOps、IaC 与 Playbooks 四大代码仓的职责红线，提供「新增实现→切换调用→双向验证→清理旧副本」的安全迁移方法 | [`skills/engineering-standards/execution-ownership-migration/SKILL.md`](../skills/engineering-standards/execution-ownership-migration/SKILL.md) |
| **多环境交付与发布** | **杜绝环境混淆与越权**：严格定义 SIT / UAT / Prod 多环境渐进交付路由规则，通过 GitHub OIDC → HashiCorp Vault 实现凭证与权限物理隔离 | [`skills/engineering-standards/multi-environment-delivery-and-release/SKILL.md`](../skills/engineering-standards/multi-environment-delivery-and-release/SKILL.md) |
| **可重复代际升级验收** | **跨版本升级不翻车**：锁定升级版本候选，以阶段 0–7 规范执行新环境部署、单向数据对齐、真实业务回归与显式双向切换门禁 | [`skills/engineering-standards/generation-upgrade-acceptance/SKILL.md`](../skills/engineering-standards/generation-upgrade-acceptance/SKILL.md) |
| **IaC 规约（iac_modules）** | **基础设施规范落地**：拓扑 YAML 驱动配置、Terraform Backend State 严格按环境隔离、保持 HCL 纯声明并与 CMDB 解耦 | [`skills/engineering-standards/infrastructure-as-code-spec/SKILL.md`](../skills/engineering-standards/infrastructure-as-code-spec/SKILL.md) |
| **Config-as-Code 规约（playbooks）** | **主机配置零污染**：Ansible 剧本规范，强制 Vault-first 凭证零落盘、剧本幂等性设计与直接消费上游 IaC 产出 | [`skills/engineering-standards/config-as-code-spec/SKILL.md`](../skills/engineering-standards/config-as-code-spec/SKILL.md) |
| **GitOps 唯一资源事实源** | **多云协同唯一源**：GitOps matrix 驱动 Hybrid、Selfhost、Serverless 部署，严格按 provider/account/state 隔离，禁止运行时 matrix 回退 | [`skills/engineering-standards/gitops-canonical-resource-delivery/SKILL.md`](../skills/engineering-standards/gitops-canonical-resource-delivery/SKILL.md) |
| **AI 代理协作标准** | **人机协作底线保障**：AI Agent 团队的执行纪律与权限边界，工作区脏检查、越权拦截、错误自检与破坏性操作熔断 | [`skills/engineering-standards/ai-agent-collaboration-standard/SKILL.md`](../skills/engineering-standards/ai-agent-collaboration-standard/SKILL.md) |
| **应用商店与初创扶持官网规范** | **踩坑血泪经验沉淀**：满足 Google（Startups / Play / Android）、Apple、Microsoft 真实性审核的官网设计、域名边界与部署后 post-check 自动化自检清单 | [`skills/engineering-standards/store-and-startup-homepage-spec/SKILL.md`](../skills/engineering-standards/store-and-startup-homepage-spec/SKILL.md) |
| **零信任网络 Overlay 交付规约** | **云边协同安全互联**：XConnect Zero/Accounts、Gateway、One 客户端跨云网络互联、WireGuard-over-TLS 与鉴权审计 | [`skills/engineering-standards/zero-trust-overlay-delivery/SKILL.md`](../skills/engineering-standards/zero-trust-overlay-delivery/SKILL.md) |

---

## 落地执行原则

1. **通用模板规范定制**：`project-development-standard`、`multi-environment-delivery-and-release` 与 `ci-cd-workflow-spec` 落地到具体仓库时，须按仓库实际的分支模型、CI gate 名称与 Vault role 命名替换占位符，严禁生搬硬套。
2. **门禁前置**：所有代码合并、发布与架构迁移，必须先经由 `harness-workflow` 定义的代码质量门禁与可证伪测试验证。

# 运维管理与基础设施治理（Operations Management）

> **作者亲身实践·深度总结·实战验证的生产级运维标准**

👉 **目录直达**：[`skills/operations-management/`](../skills/operations-management/)

这是作者针对生产环境基础设施运维、灾备容灾与日常故障处理**深度总结的 10 项运维标准**，让线上运维从被动救火走向确定性保障：

---

## 10 项运维标准全景表

| 规范名称 | 解决的实战痛点与核心机制 | 规范入口 |
|---|---|---|
| **备份、恢复与数据迁移** | **数据不丢是唯一底线**：目标数据保护契约、异地恢复真实演练、历史故障强制回归验证、切换后增量补同步与严格 RPO/RTO 保障 | [`skills/operations-management/backup-disaster-recovery-and-data-migration/SKILL.md`](../skills/operations-management/backup-disaster-recovery-and-data-migration/SKILL.md) |
| **事件响应与变更管理** | **从事故中沉淀免疫力**：生产故障分级响应、紧急变更通道、发布冻结期、无指责复盘（Blameless Postmortem）与必须落地可自动回归脚本 | [`skills/operations-management/incident-response-and-change-management/SKILL.md`](../skills/operations-management/incident-response-and-change-management/SKILL.md) |
| **系统与数据库三权分立** | 管理用户不运行业务；业务独立读写、渐进 rootless；审计身份强制只读。系统、K3s 和 DB 权限按最小增量验证与迁移，不捆绑全量改造 | [`system-db-three-role-security/SKILL.md`](../skills/operations-management/system-db-three-role-security/SKILL.md) |
| **密钥、身份与访问治理** | **凭据彻底零落盘**：HashiCorp Vault policies/roles 治理、GitHub Actions OIDC 身份互信、最小权限原则、动态凭据定期轮转与一键紧急吊销 | [`skills/operations-management/secrets-identity-and-access-governance/SKILL.md`](../skills/operations-management/secrets-identity-and-access-governance/SKILL.md) |
| **网络、DNS、TLS 与边缘管理** | **线上切流不中断**：权威 DNS 记录管理与 TTL 递减规划、ACME 证书自动化续期、Caddy/Ingress 反代配置与秒级流量回滚方案 | [`skills/operations-management/network-dns-tls-edge-management/SKILL.md`](../skills/operations-management/network-dns-tls-edge-management/SKILL.md) |
| **统一可观测性架构规范** | **拒绝监控孤岛与组件冗余**：边缘 Vector All-in-One 与 K8s 专业化分工（vmagent 指标/Vector 日志）、中央持久化 Remote Write 汇聚、本地磁盘抗断网缓冲、严禁边缘滥建私有存储与零落盘凭据治理 | [`skills/operations-management/unified-observability-architecture/SKILL.md`](../skills/operations-management/unified-observability-architecture/SKILL.md) |
| **可观测性、SLO 与告警规范** | **告别告警风暴**：SLI/SLO 核心指标度量、错误预算（Error Budget）、Grafana 监控看板标准、告警分级收敛降噪与部署后健康检查 | [`skills/operations-management/observability-slo-and-alerting/SKILL.md`](../skills/operations-management/observability-slo-and-alerting/SKILL.md) |
| **容量、成本与资源生命周期** | **算清多云账单**：多云资源成本核算、VPS 升降配与平滑置换流程、快照留存策略、闲置保留公网 IP 清理与孤儿资源回收 | [`skills/operations-management/capacity-cost-and-resource-lifecycle/SKILL.md`](../skills/operations-management/capacity-cost-and-resource-lifecycle/SKILL.md) |
| **服务目录与 Runbook 标准** | **消除信息孤岛**：服务元数据归档、上下游依赖拓扑图谱、应急运维标准化操作手册（Runbook）与下线退役契约 | [`skills/operations-management/service-catalog-and-runbook-standard/SKILL.md`](../skills/operations-management/service-catalog-and-runbook-standard/SKILL.md) |
| **GitHub Actions 运维分发** | **防止手滑误操作**：对话式 Agent 发起运维工作流前置参数校验、`workflow_dispatch` 审计留痕与全异步执行追踪 | [`skills/operations-management/github-actions-operational-dispatch/SKILL.md`](../skills/operations-management/github-actions-operational-dispatch/SKILL.md) |

---

## 运维执行与实战演练原则

1. **灾备恢复真实性**：严禁“只备份不测试恢复”，必须定期通过沙箱隔离环境验证冷备与快照的恢复可行性。
2. **凭据零落盘**：所有运维自动化剧本与流水线严格禁止硬编码凭证或生成静态密钥，强制通过 Vault 获取有时效的动态凭据。
3. **故障闭环强制回归**：生产事故在复盘完成后，必须输出能够复现并自动化拦截同类问题的测试用例，未落地用例视为变更未关闭。

## 系统与数据库共同补充规范

涉及系统或数据库的部署、巡检、权限、安全加固与迁移时，必须结合[三权分立规范](../skills/operations-management/system-db-three-role-security/SKILL.md)，并按[渐进阶段及允许/拒绝验收](../skills/operations-management/system-db-three-role-security/references/acceptance.md)执行。新规范来自实际权限审查；规范已建立不代表生产账户、业务 rootless 或审计隔离已经实施验收。先盘点和最小收敛，再分服务验证与切换，保留恢复路径。

## 功能泳道运行生命周期

按所选发布模型分别管理同一非生产集群中的临时 SIT 与独立 UAT namespace；动态地址由资源 ID 与当前 CMDB/云事实解析。功能级资源隔离、UAT 租约、保留锁、GitOps 退出与外部资源清理由[容量与生命周期附属契约](../skills/operations-management/capacity-cost-and-resource-lifecycle/references/feature-lane-lifecycle.md)统一定义；候选验收与合并由[工程技能](../skills/engineering-standards/feature-lane-release-workflow/SKILL.md)定义。本文档建立规范，不宣称泳道自动化已经部署。

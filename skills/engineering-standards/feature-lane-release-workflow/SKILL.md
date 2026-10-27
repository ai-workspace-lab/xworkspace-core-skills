---
name: feature-lane-release-workflow
description: >-
  Design and operate feature-scoped, multi-repository PR preview releases.
  Support default postmerge-uat (PR to SIT, merge, UAT) and explicitly requested premerge-uat.
  Manage decoupled candidate, deployment and verification records, shared UAT leases,
  concurrency guards and retired environments. Use for feature acceptance and release workflows;
  generation migrations require their own recovery and writer-handoff process.
---

# 功能泳道发布工作流

以功能关联多个 PR，按用户选择的发布模型部署与验收；严格区分基础设施就绪、应用部署与业务验收。IaC 创建完成或节点 Ready 只证明底层资源具备条件，不证明功能通过。

工程侧拥有候选清单、SIT/UAT 验证与合并契约；运维侧拥有环境拓扑、租约锁、并发执行及分阶段回收契约。执行细节见附件契约。

## 范围与发现

先判断任务是架构设计、流水线实现还是某一阶段的具体执行；只在授权范围内操作。读取仓库规范，检查工作区、现行 CI 环境路由、身份绑定、部署 owner 和可用平台。已有授权可继续使用，不反复索取同一许可。技能本身不授权自动合并 main、生产放量或未经审计的数据删除。

流程默认沿用现行工业界与团队通行的双模型选择，未明确指定时默认采用合并后 UAT：

- `postmerge-uat`（默认）：功能规划 → 关联 PR → 临时 SIT namespace/功能域名 → 自动化与组合基线验证 → 按已有授权及门禁合并 main → 核对合并构件 → 触发独立 UAT 运行环境部署 → UAT 业务验收 → 签发生产晋级放行。
- `premerge-uat`（用户明确要求）：功能规划 → 关联 PR → 临时 SIT → 冻结候选 → 独立 UAT 端到端验收与组合验证 → 授权及门禁合并 main → 合并后构件一致性复核 → 生产晋级。

记录所选模型、阶段顺序、SIT/UAT 运行平台、资源生命周期和构件来源。用户将功能闭环限定到合并 main 时，合并后 UAT 作为独立交付与验收记录，不把 UAT 强加为该 PR 闭环终点。现行环境保护、OIDC/Vault 与部署规则不支持所选模型时，报告具体差异并交付必要变更；不通过改名、借用生产身份或绕过门禁实现目标。

## 最小架构

优先复用现有部署栈。SIT 环境主机职责严格专一，只承载基于 GitHub Issues / Projects 登记的 feature ID 关联的任务，执行明确闭环：**关联多仓库 PR → 临时 SIT Namespace ＋ 特性域名 → 自动化测试 → 门禁合并 main**。

Kubernetes 场景复用非生产基础平台、关联功能域名、完整必要调用链及独立测试数据。SIT/UAT 采用分层平台模型：SIT 环境主机的临时 namespace 为每个特性泳道分配独立 Database，**允许重建最新 SQL schema version、允许从零初始化全新测试 DB 与种子数据**，合并后随环境即用即弃；UAT 则采用基于 `platform-ops-toolkit/.github/workflows/serverless-orchestrator.yml` 编排的持久保存 Serverless UAT（或独立持久 namespace），保持稳定的环境、域名与数据基线，严格按不可变版本与向前兼容迁移更新。SIT/UAT 不默认各建集群。生产隔离方式按已有边界和风险选取，不因使用本技能新增集群。

轻量 Next.js/Go/PG 可采用 Helm＋既有 GitOps 控制器＋Service DNS，非生产 PG 每泳道 database/角色。泳道内复用未改动镜像，写入服务及必要依赖独立运行。仅有明确收益时才增加共享基线染色或网格；独立调用链不能宣称已经实现逐跳 Header 染色。

用户选择“完整栈泳道”时，SIT 部署完整应用栈；适用的 UAT 在其选定的平台部署完整应用栈，不能只创建 Namespace 或只部署本次改动的服务。跨仓库 PR 决定变更组件的构件，未改组件也从可追溯基线固定构件；分别核对入口、内部服务地址、数据库、会话、任务与外部回调，避免跨环境调用。临时 SIT 跟随明确的 feature/PR 候选修订；稳定 UAT 可由 main 更新触发其独立部署流水线，经构建验证后更新不可变构件，逐次记录完整组合，不能用浮动镜像标签代替 main 到 digest 的映射。一次 UAT 验收绑定一个固定组合；后续更新须记录旧验收失效范围，冻结验收时暂缓自动晋级，不能静默换版。

核心执行规范下沉至三个自包含附件契约：
- 结构化四层记录与配置定义：[功能发布候选模板](assets/feature-release.template.yaml)（附件 1）
- 双模型阶段流转、门禁与失效规则：[双模型阶段与证据失效表](references/stages-and-evidence.md)（附件 2）
- 共享 UAT 租约、三权分立与回收保护：[环境租约与回收契约](references/environment-lease-and-lifecycle.md)（附件 3）
运维端执行基线可结合[系统与数据库三权分立](../../operations-management/system-db-three-role-security/SKILL.md)与[容量与生命周期](../../operations-management/capacity-cost-and-resource-lifecycle/references/feature-lane-lifecycle.md)。

## 必须保持的发布语义

- **解耦四类核心记录与生命周期追踪**：以 feature ID 关联多仓库 PR，将功能定义 (Feature)、候选身份 (Candidate)、环境部署 (Deployment) 与阶段验收 (Verification) 拆分为独立记录。PR 集合中单个 PR 关闭不触发整条泳道回收；**feature ID、关联 PR、构建指纹与测试回执必须归档保存，永久可追溯**。
- **三层指纹与多架构对账**：区分声明摘要（specDigest）、完整候选指纹（candidateFingerprint）与实际运行对账（runtimeDigestMap）。声明 hash 不代替完整构件清单；节点实际运行容器 `imageID` 与声明 digest 比对支持 OCI 多架构 Index Digest 与平台 Manifest Digest 的对应映射核验。
- **CI 构建与部署特权分离**：PR 构建仅输出经签名的不可变镜像与摘要，受信任部署编排器按白名单参数接收部署，PR 代码不得直接持有或注入云平台/集群管理凭据。
- **证据复用六维严格边界**：仅在候选构件一致、目标环境配置等价、依赖基线匹配、数据前提未变、用例边界适用（纯业务/算法可复用；网络入口、运行身份绑定、DB 鉴权隔离及第三方沙箱禁止复用）且在 TTL 内方可复用，并显式记录来源 run ID 与理由；旧 SIT 运行对账绝对不能替代 UAT 运行对账。
- **组合验证基线与合并瞬间核对**：组合验证必须绑定验证开始时锁定的目标基线 SHA（`targetBaseSha`），验证对象为 PR 与基线的合成模拟结果；合并瞬间必须核对目标分支最新 HEAD，若已被推进则标记证据失效并重新评估；跨仓库合并依 DB 迁移先行→后端核心→前端门户拓扑推进，部分失败立即 Stop Point 阻断并由责任人止损。
- **合并后 UAT 失败硬性闭环**：`postmerge-uat` 验收失败立即硬性阻断向生产环境晋级；自动加注排查保留锁并持久化脱敏证据；按缺陷定级选择正向修复 PR（重走 SIT 验证后合入）或受控 Revert PR；**严禁将 UAT 失败自动解释为数据库逆向回滚（Down migration）授权**，已执行 DDL 保持向前兼容，脏数据走人工审批订正流程。
- **UAT 共享租约与防抢占机制**：明确支持独占 UAT、共享槽位与组合候选三类拓扑；共享槽位必须落地占用租约（Lease Token / 心跳）、候选锁（`LOCKED_VERIFYING`）与晋级排队队列，验收期间严禁后续 main 合并自动抢占覆盖，必须出具结论并显式释放后方可出队部署。组合发版归属于组合发布候选指纹。
- **数据库三权分立与环境差异授权**：落实每服务业务身份（仅限 CRUD，严禁 DDL 与跨库）、受控迁移身份与独立审计只读身份。**SIT 临时泳道环境允许重建最新 SQL schema version、允许从零初始化全新测试 DB 与种子数据**，合并后随临时 namespace 一并彻底回收；**UAT 持久保存环境则严格走受控向前兼容迁移与基线采纳**，严禁推倒重建或执行破坏性逆向回滚。常规 Schema 变更遵循 Expand-Contract 原则，具备幂等保护与失败阻断。
- **feature ID 归档与宿主保存分层**：**feature ID 与发版证据永久归档保存**。完成测试与合并后，**临时 SIT Namespace 与特性域名按策略释放**；而 **K3S - Dev V5 主机环境默认保存**（长期稳定在线），除非收到显式关停指令，严禁因泳道回收影响宿主基础设施；UAT 持久保存环境仅释放候选锁；引入 Lease Version / CAS 并发锁防止清理竞态。
- **阶段独立性与不可篡改性**：PR 验收、合并后候选验收、预发与生产发布为彼此独立的审计回执，不得倒推或冒名追认；证据脱敏存储于泳道外。

## 交付与关闭

设计任务输出选型、部署边界、阶段门禁、待验证项；实现任务输出所属仓库的配置/PR 与针对性验证；执行任务输出候选指纹、阶段状态、证据和阻断。

状态使用 PASS/FAIL/BLOCKED/NOT_RUN，适用性排除需有理由。必需项缺条件即阻断该阶段，不阻止独立工作继续。证据保存于泳道外且脱敏。合并与回收授权分别核对，清理失败保留可重试状态。

源调研：[功能环境与全链路泳道白皮书 PR](https://github.com/ai-workspace-services/knowledge/pull/231)。该来源解释设计背景，不证明任何目标当前已部署或验收通过。

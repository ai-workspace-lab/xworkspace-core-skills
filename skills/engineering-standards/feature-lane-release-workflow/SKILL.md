---
name: feature-lane-release-workflow
description: >-
  Design and operate feature-scoped, multi-repository PR preview releases.
  Select PR-to-SIT and post-merge UAT or explicitly requested pre-merge UAT,
  freeze candidates, validate integration, merge and retire environments. Use for feature acceptance and release workflows;
  generation migrations require their own recovery and writer-handoff process.
---

# 功能泳道发布工作流

以功能关联多个 PR，按用户选择的发布模型部署与验收；先区分基础设施就绪、应用部署与业务验收。IaC 创建完成或节点 Ready 只证明对应基础设施条件，不证明功能通过。

工程侧拥有候选、SIT/UAT 和合并契约；运维侧拥有资源隔离、租约、执行及回收契约。实际运行须结合[系统与数据库三权分立](../../operations-management/system-db-three-role-security/SKILL.md)。

## 范围与发现

先判断任务是设计、实现工作流还是执行某一阶段；只执行已授权范围。读取仓库规范，检查工作区、现行 CI 环境路由、身份绑定、部署 owner 和可用平台。已有授权可继续使用，不反复索取同一许可。技能本身不授权合并、生产放量或数据删除。

先采用用户明确选择的模型；未指定时沿用现行受支持路由，不要求改为合并前 UAT：

- `postmerge-uat`：功能规划 → 关联 PR → 临时 SIT namespace/功能域名 → 自动化与组合验证 → 按已有授权及门禁合并 main → 核对合并构件 → 更新独立 UAT namespace → UAT 业务验收。
- `premerge-uat`：用户明确要求时，SIT 后冻结候选 → 合并前 UAT/组合验证 → 授权及门禁合并 → 合并后复核。

记录所选模型、阶段顺序、namespace 生命周期和构件来源。现行环境保护、OIDC/Vault 与部署规则不支持所选模型时，报告具体差异并交付必要变更；不通过改名、借用生产身份或绕过门禁实现目标。

## 最小架构

优先复用现有部署栈。Kubernetes 场景复用非生产基础平台、关联功能域名、完整必要调用链及独立测试数据。SIT/UAT 可在同一 Dev 节点/集群使用独立 namespace：临时 SIT 承载 PR 候选；UAT 按所选模型承载合并后的固定候选，或合并前冻结的候选；分别记录数据、配额、身份与清理范围。用户选择同一 namespace 阶段晋级时才采用该模型，不把它强加给独立 namespace 设计。SIT/UAT 不默认各建集群。生产隔离方式按已有边界和风险选取，不因使用本技能新增集群。

轻量 Next.js/Go/PG 可采用 Helm＋既有 GitOps 控制器＋Service DNS，非生产 PG 每泳道 database/角色。泳道内复用未改动镜像，写入服务及必要依赖独立运行。仅有明确收益时才增加共享基线染色或网格；独立调用链不能宣称已经实现逐跳 Header 染色。

用户选择“完整栈泳道”时，SIT 与 UAT 各部署完整应用栈，不能只创建 Namespace 或只部署本次改动的服务。跨仓库 PR 决定变更组件的构件，未改组件也从可追溯基线固定构件；分别核对入口、内部服务地址、数据库、会话、任务与外部回调，避免跨环境调用。临时 SIT 跟随明确的 feature/PR 候选修订；稳定 UAT 可持续 watch main，经构建验证后更新不可变构件，逐次记录完整组合，不能用浮动镜像标签代替 main 到 digest 的映射。一次 UAT 验收绑定一个固定组合；后续更新须记录旧验收失效范围，冻结验收时暂缓自动晋级，不能静默换版。

规划时使用 [功能候选模板](assets/feature-release.template.yaml)；它是待适配契约，不是已有 CRD 或可直接部署的清单。运行阶段与变更失效规则见 [阶段与证据](references/stages-and-evidence.md)。实际创建和回收前阅读 [执行与回收](../../operations-management/capacity-cost-and-resource-lifecycle/references/feature-lane-lifecycle.md)。

## 必须保持的发布语义

- feature ID 是生命周期单位；PR 集合中的单个 PR 关闭，不触发整条泳道回收。
- 固定每仓库 PR/head SHA、完整镜像 digest、Chart/配置版本、数据基线和目标分支基线；声明文件的 hash 只标识声明内容，不代替完整候选清单、实际运行 imageID 对账与内容指纹。缺构件时记录未齐备，不用候选名称充当完整冻结。
- CI 构建与有凭据的部署分离。受信任编排器只接受经校验的构件与允许参数，不直接用管理凭据执行 PR 提供的代码或任意清单。
- SIT 与 UAT 追溯同一功能候选链。若构件完全不变可沿用仍有效证据；合并产生新构件、配置或数据基线变化则生成新 revision，核对 merge SHA/digest 并按依赖影响重验，不能继承旧 PASS。
- 组合验证绑定最新目标分支与全部必需 PR 的固定组合。分支变化或分批合并后重新评估；跨仓库合并不是原子事务。
- 已合并业务的复验只能记录为合并后固定候选验收，不能倒推曾经通过合并前 SIT/UAT。PR 验收、合并后候选、生产发布是独立结果。合并后构件变化执行相应回归；生产构件仍满足现行稳定版本和授权门禁。
- 请求路由与数据隔离分别验证。测试写入不进入生产；消息、定时任务、缓存、会话与外部副作用有明确边界。
- 普通更新默认原生滚动；精确人群切换/蓝绿按需求增加。百分比金丝雀需路由支持和有效样本，不用 Pod 比例冒充请求比例。
- 应用回滚不撤销数据库变化；代际迁移、PG 大版本与生产单写入者交接转入专门方案。

## 交付与关闭

设计任务输出选型、部署边界、阶段门禁、待验证项；实现任务输出所属仓库的配置/PR 与针对性验证；执行任务输出候选指纹、阶段状态、证据和阻断。

状态使用 PASS/FAIL/BLOCKED/NOT_RUN，适用性排除需有理由。必需项缺条件即阻断该阶段，不阻止独立工作继续。证据保存于泳道外且脱敏。合并与回收授权分别核对，清理失败保留可重试状态。

源调研：[功能环境与全链路泳道白皮书 PR](https://github.com/ai-workspace-services/knowledge/pull/231)。该来源解释设计背景，不证明任何目标当前已部署或验收通过。

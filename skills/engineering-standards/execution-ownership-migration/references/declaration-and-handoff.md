# 声明消费与五仓交接细则

适用于通用 bootstrap、初始化、配置交付、执行迁移和相关审查。字段名沿用已有 schema；以下列举必须表达的语义，不要求另建一套重复 schema。没有字段支撑时应修正 owner 契约和消费者，不能用代码常量补齐环境事实。

## 1. 三种输入与两种输出

| 类型 | 权威来源 | 消费规则 |
| --- | --- | --- |
| 期望配置 | GitOps 本次 commit 的声明 | 环境、批次、集群、节点逻辑名、namespace、Flux 根/source/path、依赖、RBAC、策略与非敏感 Vault 引用在这里声明；按 schema 消费，不从目录/名称猜测行为 |
| 云资源事实 | IaC CMDB 和关联资源回执 | Provider、账号、区域、实例/卷 ID、IP、实际附着关系与 state 标识需可追溯到 IaC 运行；声明和事实冲突时停止 |
| 秘密与运行身份 | 受控 Vault 身份及运行时生成 | 只传身份和精确路径/字段引用，不把 token、私钥、密码、DSN 注入声明、CMDB 或公开回执 |
| 主机/集群执行结果 | Playbooks owner 回执 | 记录实际主机、实例、hostname、集群 UID、执行阶段、真实检查结果及失败原因；云字段不可反写或伪造 |
| 制品身份 | Artifacts 发布元数据 | 制品版本、digest、架构、来源 commit 和校验和；GitOps 选择要部署的版本，Orchestrator 验证存在性并交接 |

允许 IaC 为云资源创建读取运行时 Vault 凭据，允许 Artifacts 为发布读取 Registry 凭据；只有被授权的执行 owner 能使用对应权限。控制面不持有或转发跨 owner 的管理员万能 token。

## 2. 禁止硬编码与允许常量

| 情况 | 判定与正确做法 |
| --- | --- |
| `if root_name == <某一批次>`、按节点后缀选择流程、固定账号分支 | 禁止；使用明确的通用能力/运行模式字段，未知值报错 |
| 固定 `services/<某批次>/...`、`terraform/<某环境>/...`、固定 TLS/ESO 对象清单 | 禁止在执行器中保存；从 GitOps 资源引用或 IaC 已解析 state 契约消费 |
| 在 Role 默认值中提供生产域名、节点、Vault 管理 role 或账号 | 禁止；必填输入及非敏感引用由声明和调用方提供，缺失时失败 |
| 从 CMDB `host_vars` 覆盖一份本地 topology，或仅白名单旧字段导致新增声明静默丢失 | 禁止；明确 schema、所支持字段和版本，未支持字段给可定位的错误；声明到 inventory 的映射需要契约验证 |
| 运行中每个阶段自行读取最新 main | 禁止；开始时选择 ref、解析一次 commit，后续用同一运行候选；用户要求更新时创建下一次运行 |
| GitOps 环境目录中的具体批次、节点、namespace、域名与资源引用 | 正常声明；不可因为出现版本字符串就删掉实际目标或历史持久资源身份 |
| 本次运行解析的 SHA、发布 digest、只读历史回执 | 正常追溯；不得变成下一次运行的写死默认或自动兜底 |
| 协议 API 版本、资源 kind、schema 字段、标准端口、工具目录 | 可以是通用常量；必须有稳定的协议或工具含义，不暗含某个环境 |
| 测试中多个环境/任意根名称和路径 | 可以是 fixture；应覆盖名称变化、拒绝不一致和越界；fixture 不得被运行时代码消费 |

本细则不要求任意执行器接受所有输入；有意限定支持范围应通过 schema/能力声明表达，并清晰拒绝不支持配置，不能假装通用但只支持一个批次。

## 3. 跨仓交接最小语义

- **来源**：每个基础仓库的 requested ref 与 resolved commit；GitOps 声明路径和校验和；业务制品版本与 digest。
- **目标**：environment、cluster、batch、node 各自标识；provider/account/region、IaC target、state namespace/key，以及实际实例与卷的对应关系。
- **运行**：父/子 run ID、attempt、correlation ID、operation、owner/caller 来源 SHA；重跑不得误消费上一轮 artifact。
- **授权**：本次操作和允许副作用、Vault auth/role 及字段引用、目标范围；禁止把秘密值写进交接产物。
- **结果**：阶段范围、是否发生变更、验证项目的 PASS/FAIL/SKIPPED/NOT_RUN、脱敏错误、产物 checksum/digest 和实际资源身份。

消费者校验来源、目标、operation、commit、校验和与预期一致。只要父运行、实例、声明或候选变化，就重新确认相关证据；不得复用旧节点的 common 验收。

可使用临时 inventory、JSON API payload 和运行回执。它们是本次运行派生物，不能提交为第二套长期环境配置；GitOps 非敏感配置沿用 YAML，Vault ACL 的 HCL/JSON 等 API 格式在运行时生成。

## 4. K3s bootstrap 与身份

1. CMDB 选择精确节点并绑定实例、卷与已核验 SSH 主机身份；不能用业务 DNS 别名替代节点逻辑名。
2. Playbooks common 检查已有集群和 PV 身份，再设置运行时/持久 hostname 与本地解析；相同身份的重复执行应幂等，有现存状态且目标身份不一致时停止，不强制重命名或重绑卷。
3. OS 管理、运行和审计三账户及组、SSH 密钥来源和安全基线是独立检查项。声明要求的服务必须实际配置并验证，不能仅因账号存在就输出完整 common PASS。
4. K3s master 初始化后读取真实 cluster UID，节点生成独立密钥、客户端证书与私有 kubeconfig，验证信任链，再通过受控身份写入声明的 Vault 路径；CA 私钥留在 master。禁止要求新集群预置尚不存在的 UID 或把 CA 私钥经 CMDB 传送。
5. 身份参数和 RBAC 来自 GitOps；明确 RBAC 在首次凭据验证前由哪个已授权阶段应用、等待到什么状态。不得产生“等待身份验证才能创建其 RBAC”的循环依赖。`root`、`operator`、`auditor` 是职责映射，各层凭据独立，不继承其他层的管理权限。
6. 主体认证和 RBAC 用真实凭据验证允许及拒绝范围；管理员 impersonation 不能替代真实身份验收。输入与 Vault 权限应在能够判断的最早阶段检查，避免安装结束后才发现必填配置被丢弃。
7. Flux 根名称、集群名称、节点 hostname、批次目录与 source path 分别声明；不得要求它们同名。source/root/child Kustomization/HelmRelease 的 path、namespace、版本引用及 `dependsOn` 由 GitOps 决定。
8. Flux 接管后由声明图调谐；不得为某批次维护第二份 TLS/ESO 对象清单或手动分阶段资源图。API/CRD 未就绪由声明依赖表达，不能借此默认暂停整个环境。

Vault 首次初始化/unseal、数据迁移、真实支付启用、DNS 切换和旧资源退役按已有授权独立处理。主机/集群/服务/数据验收分别记录；本次 bootstrap 不能证明未执行的业务能力。

## 5. 五仓审查问题

| 仓库 | 必查内容 |
| --- | --- |
| Platform-Orchestrator | workflow/action 是否只做输入、授权、DAG、派发、等待与回执；是否直接 SSH、执行云/数据库/主机命令；是否复制环境图或绕过 owner |
| IaC | 是否只操作云资源、DNS、State 并生成 CMDB；是否混入 Ansible、systemd、数据库执行；既有持久资源是否仍可追踪 |
| GitOps | 是否只声明期望状态与非敏感引用；是否含执行脚本、秘密或云事实；根/source/path/依赖是否完整；是否复制相同环境为第二配置源 |
| Artifacts | 是否只构建、验证、发布制品；通用默认值是否注入环境专属域名、凭据或资源身份；是否混入部署/DNS/State 操作 |
| Playbooks | 是否以通用 role 执行实际主机/服务动作；目标来自 CMDB、配置来自 GitOps、秘密来自 Vault；是否丢弃字段、推断根名称/批次或创建云事实 |

对每个问题记录具体文件、入口 caller、实际副作用、正确 owner、替代入口及验证证据。旧测试若只强制一个批次的形状，应改为验证参数变化后的契约；不得通过删除负向检查或制造 PASS 降低保护。

## 6. 旧代码退出的完成条件

owner 已具备能力、caller 已消费受审查来源、相关运行与拒绝路径已验证、旧入口/常量/测试期待和过期文档已清理。跨仓变更列出合并顺序；尚未发生的运行验收标为未完成。

“不保留兼容路径”约束新实现和最终状态，不授权提前删除仍被调用的实现、历史凭据、账号或持久资源。历史对象可以只读保留；执行器不得通过它们悄悄回退。

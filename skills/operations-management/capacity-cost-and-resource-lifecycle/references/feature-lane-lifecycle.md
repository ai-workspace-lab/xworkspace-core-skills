# 功能泳道执行、租约与回收

工程阶段与候选契约以[功能泳道发布工作流](../../../engineering-standards/feature-lane-release-workflow/SKILL.md)为准。本文拥有运维运行生命周期契约，与工程侧[环境租约与回收契约](../../../engineering-standards/feature-lane-release-workflow/references/environment-lease-and-lifecycle.md)保持严格对账。涉及系统/数据库操作遵循[三权分立](../../system-db-three-role-security/SKILL.md)。

每条泳道记录所选发布模型、SIT/UAT 各自运行平台与 namespace/生命周期、feature ID、集群/节点身份、域名、资源 ID、数据库与三权角色、owner、配额、租约/过期时间、排查保留锁、删除授权来源和证据位置。多个必需 PR 共用一个生命周期；UAT 活跃租约和故障排查保留锁阻止普通 TTL 清理。

## 部署边界与 UAT 共享模型

发现实际 owner，不建立平行执行路径。通常：应用/构件仓库构建镜像；GitOps 声明目标；IaC 管云资源/DNS；配置执行器管主机和数据库；编排控制面管授权与回执。具体名称可替换。

GitOps 控制器读取受保护的非生产声明范围。若采用专用分支，声明谁可以更新、谁校验、控制器能管理哪些资源。业务 PR 无需合并 main，但不允许 PR 任意创建集群级角色、修改 Secret 来源或部署特权 Pod。外部/fork PR 使用单独信任策略，未经授权不获取秘密。

业务进程使用非 root 与独立业务身份（仅限 CRUD DML，严禁 DDL）；受控迁移身份仅在 CI/CD 迁移阶段短期注入；审计权限强制只读，管理身份不注入业务。调用测试不得通过管理连接池证明业务角色权限。常规 Schema 变更遵循 Expand-Contract 向前兼容规范与幂等执行。

非生产 PG 每泳道独立 database 和角色，验证跨库/对象访问拒绝与连接预算；共享实例仍有资源和故障影响。共享 Vault/观测不等于共享生产凭据。入口认证后设置可信泳道标记；HTTP/gRPC 传播、异步分发、缓存/幂等键与出口约束分别处理。

动态地址按资源 ID 与当前 CMDB/云事实解析，不沿用历史 IP 认领节点。IaC 仅证明资源层就绪，不替代应用或业务验收。同一 Dev 节点可容纳独立 SIT/UAT namespace；回收临时 SIT 不包括活跃 UAT，二者数据、角色与租约分别核对。

UAT 拓扑分为独立独占 UAT、共享槽位排队与组合发布候选三类：
1. **共享槽位排队 (`shared-slot-queue`)**：由编排器维护租约 Token（`leaseToken`）、心跳续约与候选锁（`candidateLock: LOCKED_VERIFYING`）。验收期间严禁后续 main 分支构建自动覆盖正在测试的候选；后续构建自动进入晋级排队队列，待当前验收出具结论并显式释放后方可出队。
2. **多功能组合发版 (`composite-release-candidate`)**：归属于全局组合版本号与组合指纹，不得单方面绑定某一 feature ID。

完整栈 SIT 与长期 UAT 同时运行时，容量评估覆盖两套应用、数据库、迁移及测试任务的同时峰值。UAT 持续跟踪 main 的控制器与数据生命周期独立于 feature 租约；暂停或删除 SIT 的源不得暂停 UAT，不能将稳定 UAT 纳入 feature TTL 或随单个 PR 关闭清理。

## 回收顺序与并发保护

为防止定时清理任务（TTL Reaper）与正在执行的部署操作或人工续租发生竞态，所有环境状态变更引入 `leaseVersion` / CAS 乐观并发保护。状态为 `DEPLOYING` 或 `LOCKED_VERIFYING` 时禁止执行清理。

### 执行顺序
1. 核对全部必需 PR 和功能完成状态；明确取消、延期、排查保留锁及 UAT 租约。
2. 将清单、回执和必要恢复材料保存到泳道外，核对保留期限。
3. 撤销或暂停 GitOps 源目标，核对卸载/prune 策略，避免删后重建。
4. 停止任务和消费者、排空工作，撤销入口与临时身份。
5. 用实际资源 ID 和 owner 核对清理集合。删除外部测试 database/角色、独占 DNS、队列、对象前缀前核实授权。共享实例、通配 DNS、共享 Vault 和观测服务不属于单条泳道。
6. 按策略处理 PVC、PV、快照和云磁盘，再删除 Namespace；Namespace 删除不是外部资源已回收的证明。
7. 回读资源及 GitOps 状态，记录剩余计费资源、失败和下一步。不得强删 finalizer 隐藏清理失败。

TTL 触发到期评估，不默认授权删除保留数据。明确批准的自动回收策略可直接执行，无需每轮重复询问。部分失败幂等重试，未知归属资源保留并报告。PR 重开创建新候选并初始化数据，不依赖残留资源。

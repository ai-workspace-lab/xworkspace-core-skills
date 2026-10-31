---
name: execution-ownership-migration
description: Enforce execution ownership across Platform-Orchestrator, IaC, GitOps, Artifacts and Playbooks. Use when adding or moving workflows, bootstrap scripts, roles, provider actions, environment configuration or cross-repository delivery contracts.
---

# 五仓职责、声明消费与执行迁移规范

先读取[仓库地图](../references/ai-workspace-infra-repository-map.md)、目标仓库当前 `AGENTS.md` 和实际 caller graph。仓库按副作用划分，目录相邻、文件名叫 bootstrap/validator 或已有 workflow 依赖均不改变 owner。规则不自动授权合并、部署、迁移或资源删除。

## 1. 唯一执行 owner

| 仓库 | 允许的职责与副作用 | 不得承载 |
| --- | --- | --- |
| Platform-Orchestrator | 输入、授权、DAG、固定运行候选、派发、等待、回执来源及完整性校验、结果汇总 | Provider、SSH、Ansible、容器、systemd、数据库及 Vault 管理配置的执行实现；第二套环境配置 |
| IaC / iac_modules | 云资源、DNS、State、云资源事实与 CMDB；Registry 基础设施、云端网络与身份资源 | 主机基线、服务配置、SQL、备份恢复、迁移、业务健康检查 |
| GitOps | 环境与资源声明、Flux 资源图、版本引用、RBAC、非敏感 Vault role/policy 和配置引用 | 执行脚本、秘密值、运行时 CMDB 和云事实回写 |
| Artifacts | 构建、镜像、Chart、离线包、制品发布、校验和、digest 与构建来源 | 环境部署、Flux 调谐、实际 DNS/云资源/State 操作；通用制品中的环境专属配置 |
| Playbooks | 主机、服务、身份、数据库、备份恢复、迁移及健康检查执行；受控 Vault 管理配置应用 | 云资源、DNS、State 变更、权威 CMDB 生成；环境选择与全局发布审批 |

`platform-ops-toolkit` 是同类控制面的历史仓库名，适用 Platform-Orchestrator 边界。Pipeline 是控制面的交付层，不增加执行 owner。

云防火墙归 IaC；节点内防火墙归 Playbooks。Registry 创建及云 IAM 归 IaC；镜像/Chart 推送、签名及制品元数据归 Artifacts。OIDC 登录与短期身份选择属于控制面授权；Vault auth mount/role/policy 的管理变更属于 Playbooks 执行，声明归 GitOps。权限范围和环境隔离仍须遵循秘密治理规范。

## 2. 配置、事实、秘密和制品各有来源

```text
workflow_dispatch 输入 / 已审查事件
  → Orchestrator 解析 GitOps、IaC、Playbooks、Orchestrator 来源，记录 commit
  → GitOps 声明提供期望状态和非敏感引用
  → IaC 执行并输出 CMDB / 云资源回执
  → Playbooks 消费同一次运行的声明、CMDB 和受控 Vault 身份
  → Flux 按 GitOps 依赖调谐并消费 Artifacts 的固定制品
  → owner 输出脱敏回执，Orchestrator 校验并汇总
```

基础仓库由参数选择 ref，默认 `main`；每次运行解析一次 commit，后续所有阶段消费该候选。无需为基础仓库额外发布 tag，也不得在运行中反复拉取 main 导致候选漂移。业务制品按发布规则使用不可变版本/digest。记录 commit 或固定 reusable workflow 的来源不属于环境硬编码。

涉及 bootstrap、配置迁移或交接字段时，读取[声明消费与五仓交接细则](references/declaration-and-handoff.md)。该细则同时定义硬编码判定、动态身份生成、回执和验收范围。

## 3. 编码规则

- 目标及云事实来自 IaC CMDB；期望配置来自本次解析并记录 commit 的 GitOps 声明；秘密仅从受控 Vault 身份读取。运行时生成的集群 UID、证书及数据库身份事实由对应 owner 产生和验证。
- 禁止在通用执行代码、role 默认值或 workflow 默认值中固定环境批次、节点、云账号、业务域名、根对象、部署专属 namespace、state 路径和成套环境配置；禁止通过名称、后缀或日期推断特殊执行分支。
- 不复制 GitOps YAML、维护影子 inventory 或把声明翻译为另一套长期配置。允许从本次声明生成临时、可追溯的 owner 输入；不能把渲染产物当新权威来源。
- 重复控制面胶水优先使用已有参数化 action；执行代码仍归 owner。一个脚本有两个资源边界的副作用时必须拆分，移动文件或改名不能代替拆分。
- 简单拼接和调用优先 Shell + YAML，主机状态变更优先 Ansible 模块。确有复杂解析、协议或校验需求才保留对应语言的 owner 实现；不按扩展名机械删除脚本。
- 必填输入缺失、声明/事实不一致或越权时明确失败；不回退到旧批次、管理员、另一套配置、放宽权限或假造回执。

## 4. 清理顺序与无兼容路径要求

1. 盘点 workflow、action、脚本、role、测试、文档和外部调用，记录输入、输出、凭据、owner 与副作用。
2. 在正确 owner 中完成通用入口及参数契约，保留幂等性、真实身份检查和失败传播；配置补入 GitOps，制品补入 Artifacts。
3. 更新调用方、声明、Vault workflow allowlist 和回执消费者，先让已审查 owner 可用，再切换 caller。
4. 运行对应的离线校验、拒绝用例及授权范围内的实际验证，记录目标、SHA、运行 ID 和结果。
5. 同批清理旧实现、旧常量、旧测试期待和旧文档；搜索所有间接引用。验证未完成时如实记录尚未切换，不能声称清理完成。

迁移期间只保留尚未切换的旧入口以维持现有运行，不得新建兼容适配层、版本别名、静默 fallback 或双重执行路径。新入口不接受旧版特殊行为作为隐式默认。删除代码不等于删除账户、DNS、数据盘、Vault 记录或 Terraform state；资源退役单独评估已有授权和恢复证据。

## 5. PR 与检查要求

每仓独立 worktree/PR，保护无关改动。PR 记录 owner 实现、caller 切换、验证结果和旧副本删除结果，关联跨仓 PR 及顺序。历史资源身份、运行证据与测试样例可以保留；不能把它们作为执行分支或永久豁免。

检查覆盖新增和修改路径及其调用链，区分执行代码、声明、文档和 fixture。已有扫描规则的基线不可作为新增越界行为的许可；新增检查应验证副作用和契约，不能只匹配目录名、Python 扩展名或字符串。规则文档不是已实现的自动 CI：PR 必须说明实际已运行的检查和未完成的迁移。

完成、失败、跳过和未运行必须分别记录。构建通过、PR 合并、IaC 成功或 Flux 接管均不能替代服务、数据或身份验收；缺少必需证据不得输出对应 PASS。

有状态升级、备份恢复、写者切换及三身份授权继续读取相应运维规范。本技能不扩大生产授权，也不因清理代码自动触发 apply。

每个受管仓库根 `AGENTS.md` 必须引用本技能并列出本仓边界；链接缺失或相互矛盾时先修正规则来源，不以旧实现作为豁免。

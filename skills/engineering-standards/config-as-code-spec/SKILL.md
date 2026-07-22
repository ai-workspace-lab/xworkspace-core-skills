---
name: config-as-code-spec
description: |
  AI Workspace Infra Config-as-Code and Ansible standards. Use when changing
  playbooks, roles, inventories, variables, templates, scripts, migration/
  restore logic, or CI/CD delivery of Ansible configuration in playbooks,
  platform-ops-toolkit, or observability.svc.plus. Covers CMDB-first delivery,
  Vault/OIDC secrets, idempotency, safe cutovers, and IaC handoff.
---

# Config-as-Code (Playbooks) Specification

本规范适用于 `playbooks/` 下的 Ansible 剧本、角色、inventory、变量、模板、脚本及其 CI/CD 调用方式，也适用于调用这些能力的 `platform-ops-toolkit` 与 `observability.svc.plus`。目标是让配置交付可追溯、可复用、幂等安全、与 IaC 一致并且密钥零落盘。

“MUST/必须”为强制要求；“SHOULD/应当”为默认要求。偏离 MUST 或 SHOULD 时，必须在 PR 中说明原因、风险和补偿措施。

先阅读 [AI Workspace Infra Repository Map](../references/ai-workspace-infra-repository-map.md)，再确认改动属于 playbooks 的执行层、platform-ops-toolkit 的编排层，还是 observability.svc.plus 的独立部署层。不得把主机配置塞进 Terraform、GitOps 或 artifacts 仓库。

## 1. Repository organization and style

- 根目录入口剧本可以保留既有 `deploy_*`、`setup_*`、`infra-*`、`migration/backup/restore` 命名；不得为“统一风格”进行仓库级重命名。
- 入口剧本只负责编排：选择目标、声明角色、少量输入校验和标签。业务实现放入 `roles/`。
- 角色按需使用 `defaults/`、`tasks/`、`handlers/`、`templates/`、`files/`、`vars/`、`meta/`、`README.md`。默认变量放 `defaults/main.yml`；不可被调用方覆盖的内部常量才放 `vars/main.yml`。
- 新增或实质修改的角色 MUST 有 README，说明用途、输入变量、依赖、目标组、执行示例和回滚方式。
- 保留相邻文件的 YAML、Jinja、Shell 和 Markdown 风格；只格式化涉及的文件，不做无关全仓重排。

## 2. Inventory and IaC boundary

### 2.1 CMDB is the delivery source of truth

- IaC 驱动的交付 MUST 使用 `inventory/terraform_cmdb.py`，其数据来自 Terraform 输出的 `cmdb.json`。
- 新建、替换、扩容、缩容或迁移后的主机，MUST 先更新 Terraform 输出，再执行 Ansible。
- Ansible 剧本、角色、模板和变量文件不得硬编码公有主机 IP、主机名、云实例 ID 或环境节点列表。loopback、监听地址、容器网段和协议默认端口等非目标身份配置可以保留，但必须语义明确。
- 静态 inventory 只用于明确标记的 `legacy` 或 `manual` 路径，不得作为 CI/CD 或常规交付默认清单。

### 2.2 Connect-time preflight

新机或资源变更后的交付 MUST 在连接前执行并记录：

```bash
ansible-inventory -i inventory/terraform_cmdb.py --host <hostname>
ansible-inventory -i inventory/terraform_cmdb.py --graph
ansible -i inventory/terraform_cmdb.py <hostname> -m ping
```

检查 `ansible_host` 是否来自当前 Terraform 输出、业务组/环境组是否正确、`cmdb_instance_id` 是否匹配云侧实例、所需 `host_vars` 是否完整，以及目标选择器是否只包含预期主机。CMDB 缺失、为空、字段不完整或目标不存在时，动态 inventory MUST 失败退出，不得静默返回空 inventory。

### 2.3 Responsibilities

- Terraform 负责云主机、网络、安全组、负载均衡、DNS 基础资源及状态输出。
- Ansible 负责操作系统配置、软件安装、服务部署、运行时配置和应用级验证。
- IaC 与 Playbooks 间的敏感状态 MUST 经 Vault 传递；禁止通过 Git、产物文件、环境快照或临时文件交接。

## 3. Credentials and Vault

- 禁止将密码、Token、私钥、数据库连接串或 Vault password file 提交仓库、写入 GitHub Secret、落入日志或生成到临时文件。
- CI/CD MUST 使用 GitHub OIDC 向 Vault 换取环境专属短期凭证；Vault role 按环境隔离，例如 `github-actions-<repo>-sit`、`-uat`、`-prod`。
- 变量优先级为：运行时环境变量 → Vault 查询 → 非敏感默认值。凭证、目标主机、环境路径和生产域名等必填值缺失时 MUST 通过 `assert` 或 `fail` 明确失败，不得提供危险 fallback。
- 涉及敏感变量的任务使用 `no_log: true`，但不得因此隐藏安全的控制流诊断；应暴露状态码、服务状态和失败前置条件，并遮蔽秘密值。
- 发现泄露时 MUST 先吊销并轮换，再用 `git filter-repo` 清理历史并记录影响范围；只删除文件不算完成处置。

## 4. Playbook and role implementation

- 优先使用幂等 Ansible 模块；超过三行、包含条件/循环/状态判断或业务逻辑的 Shell/Python MUST 放在角色 `files/` 的可执行脚本中，或实现为 Ansible module，不得内嵌在 task/workflow 中。
- 外部脚本 MUST 有明确输入、失败退出码、可重复执行语义和最小权限。
- 可能中断的操作 SHOULD 支持 tags，至少区分 `install`、`configure`、`validate`，必要时增加 `rollback`。
- 服务配置变更 MUST 使用 handler 重启或 reload，禁止无条件重启；生成配置后先做语法/健康检查，再触发服务重载。
- 对必填变量在 role 开始处使用可读的 `assert` 校验；变量名以角色或领域前缀命名，避免泛化的 `port`、`host`、`token`。
- 模板通过变量表达环境差异；多主机配置从 `groups` 与 `hostvars` 派生，不维护第二份静态节点清单。
- 使用 `ansible.builtin.*` 全限定模块、显式 `changed_when`/`failed_when`，并保持迁移/备份/恢复可重复和可重启。

删除、清库、覆盖配置、重建集群、DNS 切换和源机清理等破坏性操作 MUST：使用显式布尔确认变量；任务名标明影响；先做范围断言和备份/快照检查；默认不可执行。

## 5. Resize, migration, and recovery handoff

replacement VPS 的交付顺序 MUST 为：备份或逻辑迁移 → 新主机容量与健康检查 → Terraform state 接管 → 刷新 `cmdb.json`/inventory → Ansible 部署 → 服务健康检查。DNS 切换和旧机删除是最后的独立确认阶段。

当目标磁盘小于源盘时，整机快照恢复不可行；应使用经过验证的数据库、Vault 和业务文件级备份/恢复，不得反复执行必然失败的快照恢复。迁移剧本应保持 source/target 阶段边界，恢复失败时保留回滚点。

## 6. CI/CD and environment routing

环境只能由 Git 事件决定：

| Git event | Environment |
| --- | --- |
| `pull_request` | `sit` |
| push to `main` or `release/*` | `uat` |
| `vMAJOR.MINOR.PATCH` tag | `prod` |

- workflow 不得内嵌复杂 Shell/Python；逻辑放在 `.github/scripts/` 的可执行脚本中。
- workflow MUST 显式指定 `inventory/terraform_cmdb.py`，不得依赖 runner 的默认 `ansible.cfg` 或静态生产 inventory。
- 部署前执行 inventory 校验与 `ansible-playbook --syntax-check`；部署后执行服务健康检查。
- 执行记录关联提交、目标环境、目标主机、CMDB instance ID 和验证结果。

## 7. Quality gates and PR minimum

合并前 MUST 通过：YAML 语法与 Ansible `--syntax-check`；修改角色的 README 和变量说明同步更新；新增目标选择器的 CMDB 验证；明文凭证、静态生产节点地址和 Vault password file 检查；legacy/manual inventory 回归确认。服务变更至少有一次可验证 health check；破坏性/迁移变更提供备份、回滚和演练说明。

PR 描述 MUST 包含交付结果与影响范围、Issue/变更单或基础设施变更链接、目标环境与 CMDB 主机/组选择方式、验证命令和结果、回滚方式，以及任何偏离本规范的原因、风险和补偿措施。

## 8. Forbidden patterns

- CI/CD 默认使用 `inventory.ini` 或其他静态生产 inventory。
- 剧本中写死云主机 IP、实例 ID 或外部节点列表。
- Ansible 创建 Terraform 职责内的云网络、负载均衡或安全组。
- 在 task 或 workflow 中内嵌复杂脚本。
- 使用 `.vault_pass.txt`、长期 Vault Token 或 GitHub Secret 保存业务凭证。
- 未经显式确认执行删除、覆盖、清库或迁移切换。
- 为统一风格进行无业务价值的全仓重命名。

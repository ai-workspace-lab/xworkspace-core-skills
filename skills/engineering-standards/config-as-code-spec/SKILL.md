---
name: config-as-code-spec
description: |
  AI Workspace Infra Config-as-Code and Ansible standards. Use when changing playbooks, roles, inventories, migration/restore logic, or observability deployment configuration in platform-ops-toolkit, observability.svc.plus, or related delivery repositories. Covers Vault-first secrets, CMDB-driven inventory, idempotency, and IaC handoff.
---

# Config-as-Code (Playbooks) 规范指南

本规范专门用于指导在 `playbooks` 仓库中进行配置即代码（Ansible）建设的最佳实践与红线原则。当 AI 帮助建立、修改应用的自动化部署逻辑时，必须严格遵守以下守则，并以“清晰、复用、可维护”作为设计基础原则。

先阅读 [AI Workspace Infra Repository Map](../references/ai-workspace-infra-repository-map.md)，并确认当前目标是 `platform-ops-toolkit` 的编排层、`observability.svc.plus` 的角色/入口剧本，还是独立 playbooks 仓。不要把主机软件配置塞进 Terraform、GitOps 声明或 artifacts 制品仓。

## 1. 凭证无落盘设计 (Vault + OIDC JWT)
**原则**: 彻底告别包含密码、Key 或 Token 的本地明文临时文件，所有环境强要求使用零信任数据流。
- **环境隔离**: 每个环境在 Vault 中都有严格的隔离树（如 `kv/data/sit/*` 与 `kv/data/prod/*`）。在配置变量时，必须支持通过前缀变量 `VAULT_ENV_PATH` 提取正确的环境路径。
- **动态 OIDC JWT**: 部署流水线只允许通过 GitHub OIDC 颁发的针对该环境（如 `github-actions-platform-ops-toolkit-[env]`）专属的短期 JWT 前往 Vault 动态授权取密。
- **缺失即失败**: 凭证、目标主机、环境路径和域名不是可安全回退的变量。优先从运行时环境或 Vault 获取；若必需值不存在，使用明确断言失败。不得为密码、Token、生产域名、目标 IP 提供 fallback 默认值。

## 2. 剧本代码纯净度与内嵌脚本限制
**原则**: Config-as-Code 应是幂等的、声明式的组合，而不是巨大的 Bash 容器。
- **禁止内嵌复杂脚本**: **绝对禁止**在 Playbook 的 Task（如 `shell`, `command`, `script` 模块）中硬编码内嵌大段复杂的、带有复杂控制逻辑的 `bash` 或 `python` 代码！
- **可复用抽象**: 任何超过三行的 shell 命令、涉及到业务状态判定与分支流转的逻辑，必须被抽象为单独的脚本文件并放置于 `files/`，或更优地，用 Python 编写为自定义的 Ansible Module（存放于 `library/` 下）。

## 3. 互操作性设计 (Config-as-Code ↔ IaC)
**原则**: 明确边界，解耦职责，接受并信任上游（IaC）供给的静态配置与状态锚点。
- **职责边界**: Ansible Playbooks 仅负责软件环境的建置（如安装 Docker，部署配置 SaaS）。绝对不允许 Ansible 去执行“创建公有云负载均衡、创建云端网络安全组”等属于 IaC 范畴的事情。
- **握手介质 (CMDB)**: Playbooks 的 Inventory 源一律来自上游 Terraform 的输出。无论是 IP、Hostnames 还是网络区域划分，必须设计为从 `cmdb.json` （或类似清单格式）中解析获取，不能在 Ansible 的代码中再硬编码节点地址。
- **信任锚点 (Vault State Bridge)**: 跨阶段的数据传递（如 IaC 生成的初始数据库密码，需交由 Playbooks 读取配置应用），必须且唯一地通过 Vault Secret 引擎作为中间纽带实现跨阶段解耦流转，Ansible 会从 Vault 中拉取并信任该数据事实。

## 4. AI Workspace Infra 交付规则

- `platform-ops-toolkit` 必须在本次 Terraform 生成的 CMDB/inventory 上运行 Ansible；不得回退到手写 inventory、旧 artifact 或硬编码 IP。
- VPS replacement/resize 的顺序必须是：备份或逻辑迁移 → 新主机健康检查 → Terraform state 接管 → 刷新 CMDB/inventory → Ansible 部署。DNS 切换和源机清理必须是单独确认的最后阶段。
- 当目标磁盘小于源盘时，整机快照恢复不可行；改用经过验证的应用级备份/恢复（数据库、Vault、业务文件），不要反复创建必然失败的快照。
- 对 `observability.svc.plus` 的公网 HTTPS 变更，先验证 A/AAAA DNS 记录与目标 IP；ACME 的 NXDOMAIN 不是可通过重试部署解决的问题。
- 对变更过的 playbook 使用 `ansible-playbook --syntax-check`；对 mutating playbook 先确认 inventory 中目标非空且可达，再宣称部署成功。

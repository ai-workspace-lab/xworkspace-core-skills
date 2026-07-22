---
name: config-as-code-Spec
description: |
  Config-as-Code and Playbooks Standards. 
  Dictates how AI should design Ansible Playbooks, enforce Vault-first secret lifecycles, maintain code purity, and interoperate with IaC outputs.
---

# Config-as-Code (Playbooks) 规范指南

本规范专门用于指导在 `playbooks` 仓库中进行配置即代码（Ansible）建设的最佳实践与红线原则。当 AI 帮助建立、修改应用的自动化部署逻辑时，必须严格遵守以下守则，并以“清晰、复用、可维护”作为设计基础原则。

## 1. 凭证无落盘设计 (Vault + OIDC JWT)
**原则**: 彻底告别包含密码、Key 或 Token 的本地明文临时文件，所有环境强要求使用零信任数据流。
- **环境隔离**: 每个环境在 Vault 中都有严格的隔离树（如 `kv/data/sit/*` 与 `kv/data/prod/*`）。在配置变量时，必须支持通过前缀变量 `VAULT_ENV_PATH` 提取正确的环境路径。
- **动态 OIDC JWT**: 部署流水线只允许通过 GitHub OIDC 颁发的针对该环境（如 `github-actions-platform-ops-toolkit-[env]`）专属的短期 JWT 前往 Vault 动态授权取密。
- **优雅降级原则**: 在编写 Ansible Role 的 `defaults` 或 `vars` 时，务必按照如下顺序提取凭证：优先从运行时的环境变量 `lookup('ansible.builtin.env', ...)` 获取；若不存在则调用 `community.hashi_vault.vault_kv2_get` 获取；最后再提供 Fallback 默认值（参考现有的 `vault-secrets-dataflow-design` 最佳实践）。

## 2. 剧本代码纯净度与内嵌脚本限制
**原则**: Config-as-Code 应是幂等的、声明式的组合，而不是巨大的 Bash 容器。
- **禁止内嵌复杂脚本**: **绝对禁止**在 Playbook 的 Task（如 `shell`, `command`, `script` 模块）中硬编码内嵌大段复杂的、带有复杂控制逻辑的 `bash` 或 `python` 代码！
- **可复用抽象**: 任何超过三行的 shell 命令、涉及到业务状态判定与分支流转的逻辑，必须被抽象为单独的脚本文件并放置于 `files/`，或更优地，用 Python 编写为自定义的 Ansible Module（存放于 `library/` 下）。

## 3. 互操作性设计 (Config-as-Code ↔ IaC)
**原则**: 明确边界，解耦职责，接受并信任上游（IaC）供给的静态配置与状态锚点。
- **职责边界**: Ansible Playbooks 仅负责软件环境的建置（如安装 Docker，部署配置 SaaS）。绝对不允许 Ansible 去执行“创建公有云负载均衡、创建云端网络安全组”等属于 IaC 范畴的事情。
- **握手介质 (CMDB)**: Playbooks 的 Inventory 源一律来自上游 Terraform 的输出。无论是 IP、Hostnames 还是网络区域划分，必须设计为从 `cmdb.json` （或类似清单格式）中解析获取，不能在 Ansible 的代码中再硬编码节点地址。
- **信任锚点 (Vault State Bridge)**: 跨阶段的数据传递（如 IaC 生成的初始数据库密码，需交由 Playbooks 读取配置应用），必须且唯一地通过 Vault Secret 引擎作为中间纽带实现跨阶段解耦流转，Ansible 会从 Vault 中拉取并信任该数据事实。

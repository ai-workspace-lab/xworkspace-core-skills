---
name: execution-ownership-migration
description: Enforce the four-repository execution boundary between platform-ops-toolkit, gitops, iac_modules, and playbooks. Use for new workflows, scripts, roles, provider changes, migration work, or moving execution logic.
---

# 四边界执行归属规范（强制）

这份 skill 是四个基础设施仓库的共同判定源。仓库根目录的 `AGENTS.md` 必须引用它；
如果 skill 未被当前 Agent 加载，根 `AGENTS.md` 仍然有效，不能以“没有加载 skill”为例外。

## 1. 先按动作判定，不按目录名判定

判定对象是代码实际触碰的资源和副作用，不是文件所在目录、调用方仓库或变量名称。
按以下顺序询问，第一项为“是”即确定 owner：

1. 是否创建、修改、查询或删除云资源、DNS、Registry、OS Login、临时防火墙、Terraform state，或产出云资源事实/CMDB？→ **IaC Modules**。
2. 是否通过 SSH、Ansible、Docker、systemd、包管理器、主机文件、Caddy/Xray，或 PostgreSQL/备份/恢复/服务健康检查操作主机和服务？→ **Playbooks Roles**。
3. 是否只是声明目标拓扑、资源参数、版本、域名、非敏感配置引用？→ **GitOps**。
4. 是否只做入口、审批、环境/目标选择、Vault/OIDC 授权、阶段编排、固定 SHA 派发、证据校验和最终放行？→ **Toolkit**。

若一个文件命中两个 owner，必须拆成 owner 实现 + 薄调用方；不得用“诊断”“bootstrap”或
“validator”改名掩盖执行副作用。目录名不能改变 owner。

## 2. 四个仓库的硬边界

| 仓库 | 允许 | 禁止新增 |
| --- | --- | --- |
| `platform-ops-toolkit` | GitHub Actions 入口、输入校验、审批、Vault/OIDC、固定 SHA reusable-workflow dispatch、运行关联、证据/清单校验、最终门禁 | `ssh`、`ansible*`、`docker`、`systemctl`、`apt-get`、`psql`、`pg_dump/restore`、`terraform`、`gcloud/aws/wrangler/cloudflare` 变更、DNS/主机/服务/数据库执行 |
| `gitops` | YAML/JSON/HCL 等声明式资源、拓扑、版本、域名、非敏感配置引用 | shell/Python/Ruby 执行脚本、Ansible role/playbook、运行时 IP/CMDB、Vault 值、provider API、DNS/主机/数据库操作 |
| `iac_modules` | Terraform/provider 模块、云资源/DNS/Registry/OS Login/临时防火墙/state 操作、plan/apply/read、运行时云事实和 CMDB 产出 | SSH/Ansible/Docker/systemd、服务安装/证书恢复/健康检查、数据库迁移/备份/恢复、业务数据操作 |
| `playbooks` | Ansible Roles/Playbooks、主机基线、服务部署、Caddy/证书、Observability 服务、数据库迁移/备份/恢复、服务诊断和健康检查 | Terraform/provider API、云资源/DNS/Registry/state 变更、CMDB 生成和云资源生命周期管理 |

Playbooks 可以消费 IaC 生成的 CMDB，但不得反向生成或修改 CMDB 权威事实；Toolkit 可以验证
CMDB 证据，但不执行云或主机动作。

## 3. 标准数据流

```text
GitOps 声明
  → Toolkit 选择/审批/授权/固定版本
  → IaC Modules 云资源操作并产出 CMDB
  → Toolkit 校验 CMDB 与证据
  → Playbooks Roles 使用 CMDB 执行主机/服务/数据库操作
  → Toolkit 汇总证据并最终放行
```

跨仓库调用必须是：**新增 owner Role/Workflow → 切换 Toolkit 调用方 → 离线/契约/UAT 验证
→ 删除旧副本**。切换前不得删除旧实现；切换后不得保留两份可执行 owner。

## 4. 强制判定和门禁

- 新增文件先在 PR 描述填写 `owner`、`caller`、`副作用资源`、`输入/输出证据`；owner 必须与上表一致。
- 仅测试、只读 schema/CMDB/manifest 校验不自动改变 owner；命令最终是否造成副作用必须审查。
- Toolkit 的历史遗留执行脚本只能保持冻结字节，不能继续扩展；迁移必须先建立 owner 实现。
- `gitops` 中出现可执行脚本或运行时 CMDB；`iac_modules` 中出现主机/数据库服务动作；`playbooks` 中出现 provider/DNS/state 动作；Toolkit 中出现执行命令，均为阻断级违规。
- 跨边界任务必须拆 PR 或在 PR 中提供四段证据：owner 实现、caller diff、验证结果、旧副本删除结果。
- 任何 owner 不明确、调用方仍指向旧副本、验证只覆盖本地未覆盖 UAT、或存在双重执行路径时，停止合并和发布。

## 5. Agent 执行要求

开始任务前必须读取当前仓库根 `AGENTS.md` 和本 skill；发现引用路径不存在、规则互相冲突或工作区有未授权脏改动时，先报告并停止越界修改。
规则不能只写在 README 或聊天上下文中；必须有根 `AGENTS.md`、可执行门禁或明确的 PR 阻断检查。

# Vault + GitHub Actions 配置记录

记录日期：2026-06-06

本记录只保留流程、路径和配置原则，不包含任何 token、私钥、证书内容或其他敏感值。

## 目标

把 XWorkspace 相关仓库的 GitHub Actions 统一切换到 Vault OIDC 登录，并按仓库隔离读取权限。

## Vault 侧配置

- 已启用 `jwt` auth mount
- 已信任 GitHub Actions OIDC issuer
  - `oidc_discovery_url = https://token.actions.githubusercontent.com`
  - `bound_issuer = https://token.actions.githubusercontent.com`
- 已为每个仓库创建独立 policy 和 role
  - `github-actions-openclaw-multi-session-plugins`
  - `github-actions-xworkmate-bridge`
  - `github-actions-xworkmate-app`
  - `github-actions-xworkspace-core-skills`
- 已采用统一 KV 读路径
  - `kv/data/github-actions/<repo>`

## 权限模型

每个 role 仅绑定本仓库对应的 GitHub OIDC 身份：

- `repository = ai-workspace-lab/<repo>`
- `sub = repo:ai-workspace-lab/<repo>:*`
- `bound_audiences = ["vault"]`

每个 policy 仅允许读取自己的 KV 路径。

## GitHub Actions 统一接入方式

所有接入 Vault 的 workflow 都使用相同模式：

1. 在 job 中加入 `id-token: write`
2. 使用 `hashicorp/vault-action`
3. `method = jwt`
4. `role = github-actions-<repo>`
5. `jwtGithubAudience = vault`
6. 从 `kv/data/github-actions/<repo>` 读取对应密钥

## 已更新的仓库

### openclaw-multi-session-plugins

- `publish.yml` 改为通过 Vault 读取 `NPM_TOKEN`
- `deploy.yml` 改为通过 Vault 读取 SSH 相关密钥
- `deploy.yml` 已补充 SSH 私钥 `*_B64` 优先读取与多行私钥回退
- git/source 安装后的版本校验改为读取全局安装目录的 `package.json.version`
- 仍保留原有发布和安装逻辑
- 已通过 deploy workflow 验收

### xworkmate-bridge

- `pipeline.yml` 改为通过 Vault 读取：
  - `INTERNAL_SERVICE_TOKEN`
  - `GHCR_TOKEN`
  - `WORKSPACE_REPO_TOKEN`
  - `SINGLE_NODE_VPS_SSH_PRIVATE_KEY`
  - `SINGLE_NODE_VPS_SSH_PRIVATE_KEY_B64`
  - `SSH_KNOWN_HOSTS`
- 保留原有 `workflow_dispatch` 的手动 token 覆盖路径
- `prepare-ssh.sh` 已改为优先解码 `SINGLE_NODE_VPS_SSH_PRIVATE_KEY_B64`，再回退到原始私钥
- 补充了 deploy 前置校验：`BRIDGE_AUTH_TOKEN` 必须由 `workflow_dispatch` 输入或 Vault `INTERNAL_SERVICE_TOKEN` 注入，为空时在 GitHub Actions 中提前失败并输出非敏感错误说明
- 已修复 `Validate OpenClaw session contract` 的 smoke 行为：当 OpenClaw session 已启动但 `xworkmate.tasks.get` 返回 `no_native_task_record` 时，按“会话启动合同通过、无 native task record 可轮询”处理，避免 deploy 后置验证无意义等待到超时

#### xworkmate-bridge 补充验收记录

- 失败 run：`https://github.com/ai-workspace-lab/xworkmate-bridge/actions/runs/27060129810`
  - 失败点：Ansible `Assert xworkmate-bridge auth token is provided`
  - 原因：GitHub Actions deploy job 中 `BRIDGE_AUTH_TOKEN` / `INTERNAL_SERVICE_TOKEN` 为空
- 修复提交：
  - `6db48ee fix(ci): require bridge auth token before deploy`
  - `919addf fix(ci): accept OpenClaw session without native task record`
- 验收 run：`https://github.com/ai-workspace-lab/xworkmate-bridge/actions/runs/27060962558`
  - `Production State`: success
  - `Prep`: success
  - `Build`: success
  - `Deploy`: success
  - `Validate`: success
  - `Publish GitHub Release`: success
- 验收要点：
  - `Load Vault secrets` 成功读取仓库专用 KV 路径
  - `Validate deploy secrets` 成功确认 `BRIDGE_AUTH_TOKEN` 已注入
  - `Prepare runner SSH access` 成功验证 SSH deploy key
  - `Run Ansible deploy playbook` 成功通过原失败的 auth token assert
  - `Validate OpenClaw session contract` 成功通过，不再因 `no_native_task_record` 超时

### xworkmate-app

- `build-and-release.yml` 改为通过 Vault 读取：
  - `REVIEW_ACCOUNT_LOGIN_PASSWORD`
  - 各平台签名与打包密钥
- 对 `pull_request` 保留仓库归属判断，避免把 Vault 访问扩大到不可信上下文

### xworkspace-core-skills

- 当前仓库内未发现 `.github/workflows`，因此没有可改的 GitHub Actions 文件
- 相关 Vault role/policy 已预先创建，方便后续新增 workflow 时直接接入

## 备注

- 本次未在文档中记录任何敏感值
- SSH deploy key 统一采用 `*_B64` 优先、原始多行 key 回退的模式，详见 `vault-github-actions-ssh-deploy-runbook.md`
- 若后续新增仓库，只需补：
  - 一条 policy
  - 一条 role
  - 对应的 `kv/data/github-actions/<repo>` 路径
  - workflow 中的 `vault-action` 接入步骤

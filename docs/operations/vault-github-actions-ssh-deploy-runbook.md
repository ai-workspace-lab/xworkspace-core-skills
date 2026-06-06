# Vault + GitHub Actions SSH Deploy Runbook

记录日期：2026-06-06

本文档记录 GitHub Actions 通过 Vault OIDC 读取 SSH deploy key 的标准模式。文档只记录流程和字段名，不包含任何敏感值。

## 适用范围

适用于需要从 GitHub Actions SSH 到部署主机的 workflow，例如：

- `openclaw-multi-session-plugins/.github/workflows/deploy.yml`
- `xworkmate-bridge/.github/workflows/pipeline.yml`

不需要 SSH 的发布或构建 workflow 仍按普通 Vault secret 读取模式处理。

## Vault 字段约定

每个仓库从自己的路径读取：

```text
kv/data/github-actions/<repo>
```

SSH deploy key 至少保留两个字段：

```text
SINGLE_NODE_VPS_SSH_PRIVATE_KEY
SINGLE_NODE_VPS_SSH_PRIVATE_KEY_B64
```

如果仓库有专用别名，也可以同时保留：

```text
OPENCLAW_SSH_KEY
OPENCLAW_SSH_KEY_B64
```

`*_B64` 是私钥文件内容的 base64 单行编码，GitHub Actions 应优先使用该字段，再回退到原始多行私钥字段。

## GitHub Actions 模式

workflow 需要：

- `permissions.id-token: write`
- 使用 `hashicorp/vault-action`
- `method: jwt`
- `jwtGithubAudience: vault`
- `role: github-actions-<repo>`
- 在 `secrets` 中读取原始 key 和 `*_B64` key

落盘时优先解码 `*_B64`：

```bash
SSH_KEY=""
if [ -n "${SINGLE_NODE_VPS_SSH_PRIVATE_KEY_B64:-}" ]; then
  SSH_KEY="$(printf '%s' "${SINGLE_NODE_VPS_SSH_PRIVATE_KEY_B64}" | base64 -d)"
elif [ -n "${SINGLE_NODE_VPS_SSH_PRIVATE_KEY:-}" ]; then
  SSH_KEY="${SINGLE_NODE_VPS_SSH_PRIVATE_KEY}"
fi

printf '%s\n' "${SSH_KEY}" > ~/.ssh/id_rsa
chmod 600 ~/.ssh/id_rsa
ssh-keygen -y -f ~/.ssh/id_rsa >/dev/null
```

## 验收步骤

1. 触发 deploy workflow。
2. 确认 `Load Vault secrets` 成功。
3. 对需要应用层 auth token 的仓库，确认 workflow 有非敏感的必填校验步骤，例如 `Validate deploy secrets`。
4. 确认 `Verify SSH connectivity` 或 `Prepare runner SSH access` 成功。
5. 确认远端安装步骤成功。
6. 确认 Ansible 或部署脚本的业务必填项 assert 通过。
7. 如果需要验证安装版本，优先读取安装目录中的 `package.json.version`，不要直接解析 `npm ls -g` 的整行输出。

## 故障处理

- `Load key ... error in libcrypto`：优先检查 workflow 是否读取并解码了 `*_B64` 字段。
- `Permission denied (publickey)`：本地用同一把私钥先执行 SSH 验证，再更新 Vault。
- `vault-action` 报 `valid path and key`：检查 `secrets` 每一行之间是否用 `;` 分隔。
- git/source 安装后版本校验误判：读取 package manifest 的 `version` 字段。
- Ansible 报业务 token assert 失败：检查 workflow 是否把 Vault 字段写入实际部署变量，例如 `INTERNAL_SERVICE_TOKEN` -> `BRIDGE_AUTH_TOKEN`。
- OpenClaw session smoke 超时：先区分会话启动失败和轮询无 native task record。若 `session.start` 已返回 OpenClaw run handle，而 `xworkmate.tasks.get` 返回 `no_native_task_record`，可按“session 启动合同通过、无 native task record 可轮询”处理，不应让 deploy 验收等待到超时。

## 已验证记录

- `openclaw-multi-session-plugins` deploy run 已通过。
- `xworkmate-bridge` 已补齐 workflow 与 Vault 字段，并通过 apply deploy run 验收：
  - `https://github.com/ai-workspace-lab/xworkmate-bridge/actions/runs/27060962558`

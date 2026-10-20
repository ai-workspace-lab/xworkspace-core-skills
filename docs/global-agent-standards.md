# 本机 Agent 的版本化全局规范

工程标准和运维管理保留在本仓库维护；本机只发现固定 commit 快照的目录链接。不会随开发工作区修改或 main 前进而静默更新。

Codex 支持用户级 `~/.agents/skills` 及技能目录 symlink，见[官方技能文档](https://learn.chatgpt.com/docs/build-skills)。其他 Agent 仅在支持相同目录或显式配置该技能根时共享；本工具不改未知 Agent 的配置，也不覆盖现有技能。

## 安装、检查与回退

在仓库根目录选定已检查的完整 commit SHA。默认只预览，加 `--apply` 才修改本机：

```sh
python3 scripts/bind_global_standards.py --ref <完整commit-SHA>
python3 scripts/bind_global_standards.py --ref <完整commit-SHA> --apply
python3 scripts/bind_global_standards.py --check
```

覆盖两个域下含 SKILL.md 的技能目录，包含跨目录参考。使用 Git detached worktree 保存完整版本，避免扁平复制破坏相对链接。默认路径：

- `~/.agents/skills/<skill-name>`：Agent 发现入口，目录链接。
- `~/.agents/skill-sources/xworkspace-core-skills/versions/<SHA>`：固定 Git 快照。
- 同目录 `current`：一次切换活动版本的指针。
- 同目录 `lock.json`：仓库、commit、快照及受管链接清单。
- 同目录 `history/`：以前的锁记录，供显式回退。

升级和回退都使用相同命令，传入新的或历史完整 SHA；保留旧快照，不自动清理。`--check` 验证实际 HEAD、规范目录内容漂移、版本指针和技能链接。

发现非本工具管理的同名目录/链接则先停止，不覆盖。迁移已有独立技能时先核实内容并移到扫描目录外备份，再安装，避免同名技能并存。不把未经审核的工作区内容纳入全局快照。

新技能通常会自动被发现；当前会话未更新时，新开会话或重启 Agent。文件和链接检查通过不等于每种 Agent 的运行加载验收；使用下一轮技能列表核实。

## 维护规则

修改在本仓库经定向测试、技能结构和引用检查后提交；本机快照锁定 commit，未经显式安装不会变化。任务可在证据中记录本机锁的 commit，实现跨机器复现。不要修改 versions 下文件，修改应回到仓库分支；快照漂移时停止更新并人工检查。

安装工具只执行本地 Git worktree/技能目录操作，不运行任何部署、云 API、DNS、主机或数据库命令，不提供生产变更权限。

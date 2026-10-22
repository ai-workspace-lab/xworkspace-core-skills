# 质量验证与工程支持（Quality & Engineering Support）

本仓库配备了完备的自动化测试、分支合规门禁、产物隔离规范与示例工程模板，确保核心规范与工具链的生产级质量。

---

## 1. 单元测试保障

仓库包含针对视频构建流水线与全局规范绑定引擎的完整单元测试套件：

```bash
# 运行全量单元测试（10 项测试全部通过）
python3 -m unittest discover tests
```

测试范围包括：
- `tests/test_bind_global_standards.py`：测试 Git Detached Worktree 不可变快照生成、软链一致性校验、漂移检测与历史版本回滚。
- `tests/test_build_it_infra_video.py`：测试长图 manifest 解析、音频对齐、HyperFrames 配置生成与视频渲染验收。

---

## 2. Release 分支门禁规范

流水线 [`.github/workflows/validate-release-pr.yml`](../.github/workflows/validate-release-pr.yml) 对所有以 `release/*` 为基准分支的 PR 进行自动化发布策略检查：

- 仅放行来自 `hotfix/*` 分支的紧急修复 PR。
- 仅放行打上 `cherry-pick` 或 `backport` 标签的已验证功能 PR。
- 严禁从 `main` 或 `feature/*` 直接全量合入发布分支。

---

## 3. 产物隔离契约（Artifact Ignore）

遵循 [`skills/artifact-ignore.md`](../skills/artifact-ignore.md) 规则：

- **允许忽略**：`.cache/`、`tmp/`、`scratch/`、浏览器截图临时文件、模型下载缓存索引与渲染中间片段。
- **严禁忽略**：最终交付物、manifest、`DELIVERY.md`、`reports/`、`exports/` 与 `renders/*.mp4`。
- **状态透明**：严禁用 ignore 规则遮掩构建失败、单测未通过或阶段验收异常。

---

## 4. 示例工程模板

轻量级 HyperFrames 工程模版请参考：[`example/it-infra-evolution-video/`](../example/it-infra-evolution-video/)。
包含标准 HTML、动效配置、脚本与占位结构，供多模态视频生产作为脚手架快速复用。

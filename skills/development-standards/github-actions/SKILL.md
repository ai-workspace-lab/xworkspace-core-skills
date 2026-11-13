---
name: github-actions
description: 开发或评审 GitHub Actions 工作流、reusable workflow 和 composite action 的代码结构、复用边界、输入输出及结果判定。
---

# GitHub Actions 开发规范

- 先读[CI/CD 工程规范](../../engineering-standards/ci-cd-workflow-spec/SKILL.md)，追踪实际触发器、调用链、脚本、权限和最终门禁。Workflow 定义触发、依赖、目标、权限、并发与结果，具体执行逻辑委托给对应 owner 的脚本或原有入口。
- 整组作业共享同一执行契约时用 reusable workflow。重复的同作业步骤且依赖相同 runner 上下文时用 composite action。需要本地执行和测试的逻辑放入独立脚本。仅在输入、权限、副作用和失败处理一致时复用，保留清晰的责任边界。
- 为 inputs、outputs、secrets 和制品声明最小契约，验证必填和目标标识。明确调用链的凭据范围与外部依赖固定方式。事件输入先作为数据传递，再由脚本验证，避免把未验证输入插入可执行脚本文本。
- 运行之间存在并发冲突时，按实际写入资源定义并发范围。检查取消是否会留下部分变更。汇总结果区分失败、跳过、取消和成功，验证所需 job 实际运行且结果对应当前目标与制品。
- 使用仓库已有 workflow 检查工具及脚本验证。核对发布所需的业务回归命令在哪条 workflow 实际执行。对已有失败运行，从首个失败步骤定位依赖、授权、测试、打包或部署问题，再检查汇总状态是否正确。修改触发、权限、输出或门禁时，检查对应的事件和失败路径，记录实际验证范围。真实构建、发布和运维派发沿用既有工程与运维入口。

工作流文件、输入和输出的命名按[清单](../programming-paradigms/references/naming-and-clarity.md)执行。YAML 保持短小可读：触发、权限和依赖写在 workflow 里，逻辑放进所属仓的脚本。不把复杂判断写成难以审查的表达式密集体。

参考 [GitHub 复用工作流](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)及[范式与模式选择](../programming-paradigms/SKILL.md)。

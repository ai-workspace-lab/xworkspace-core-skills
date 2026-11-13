---
name: python-shell
description: 开发或评审 Python CLI、Shell 脚本及 YAML 配置与渲染，覆盖输入契约、解析、重试、错误和退出码。
---

# Python / Shell / YAML 开发规范

- Shell 用于串联已有命令、传递参数与简单条件。结构化解析、复杂校验、可独立测试的决策和多步恢复优先 Python。主机收敛优先 Ansible 模块。先查现有 CLI、脚本和调用链，复用所属仓库的实现。
- 入口参数明确目标、路径与模式。保留现有 CLI 参数、输出格式和退出码契约。机器可读结果输出到 stdout，诊断输出到 stderr。副作用脚本应区分成功、无需变更、失败及部分完成，具体表达沿用调用方契约。
- Shell 选择实际支持的解释器，正确引用参数，按解释器能力传递参数列表。检查命令与管道失败，避免通过 `eval` 拼装命令。Python 用结构化解析和参数数组调用子进程，显式处理退出状态与超时。
- 分离解析、业务决策与副作用。渲染文件先验证再写入，需避免半写时在同文件系统内原子替换。涉及共享状态时，明确互斥、幂等或恢复点。只重试暂时性且可安全重试的操作，保留首个可定位的失败原因。
- 用脚本实际入口验证成功和至少一个受影响的失败路径。按需覆盖空输入、特殊字符、重复执行、部分失败及错误传播到调用方。沿用仓库现有格式化、ShellCheck 或 Python 测试入口。

## YAML 与渲染

- YAML 描述结构化输入，Python 负责解析和契约校验，Shell 负责调用。按实际消费者确认单文档或多文档格式、标量类型、空值及默认值。GitHub Actions 和 Ansible 的框架语义使用各自解析器验证。
- 对部署拓扑、访问策略等会影响实际目标的声明，在消费边界拒绝重复键和无效引用。用合成样本验证解析器行为，覆盖最后一个值覆盖前值的情形。跨文件的唯一性按资源类型和作用域验证，允许契约明确的覆盖。
- 验证解析后的数据和下游渲染结果。生成的 JSON、HCL 或 inventory 由权威声明派生。临时产物不承担环境事实源职责。

命名与可读性按[清单](../programming-paradigms/references/naming-and-clarity.md)执行：Python 与 Shell 函数用 snake_case，常量 UPPER_SNAKE_CASE，YAML 键与 Ansible 变量用下划线。脚本文件名跟随所在目录已有的下划线或连字符风格，不引入第三种写法。避免晦涩的一行条件和 `eval`；复杂逻辑写成可测试的小函数。

工作流或 Playbook 调用分别参考 [GitHub Actions](../github-actions/SKILL.md)及 [Ansible Playbook](../ansible-playbook/SKILL.md)。涉及语言选择或复用边界时，读取[范式与模式选择](../programming-paradigms/SKILL.md)。

---
name: gin-go
description: 开发或评审 Go 服务与 Gin HTTP API。用于路由、鉴权边界、业务用例、服务接口、错误映射、事务调用及并发处理。
---

# Gin / Go 开发规范

- 先追踪路由、middleware、服务和数据访问，查找已有业务能力及其调用方。沿用当前模块结构和具体实现。Accounts 的 GORM 和 Billing 的 pgx 可按各仓已有数据访问方式演进。
- Handler 负责请求绑定、身份提取和响应映射。业务用例负责授权决策、业务规则和事务边界。存储代码负责查询和持久化。简单 CRUD 保持短调用链，出现独立策略、依赖替换或事务编排时再提取边界。
- HTTP 输入、领域对象和持久化模型按各自变更需要建模。通过已有绑定、校验和错误映射返回稳定的 HTTP 状态与业务错误码。兼容现有客户端对空值、零值、省略字段、分页和错误的约定。存在 OpenAPI 或其他生成契约时，修改权威来源并验证客户端产物。
- 对同一业务操作集中维护授权与状态转换。不同入口可以共享用例，分别负责协议和身份转换。使用调用方所需的小接口，优先复用已有具体实现，接口应表达真实的替换或隔离需求。
- 从请求传递 `context.Context` 到查询和外部调用，保留错误因果并集中映射。多步数据库操作通过同一事务句柄。后台任务由明确的生命周期管理，限制并发并处理取消、超时和结束。
- 用 `gofmt` 和仓库现有 Go 检查验证。按影响选择 handler 测试、事务集成测试和并发场景。真实 PostgreSQL 语义按[数据库开发规范](../postgresql-development/SKILL.md)验证。

遇到行为回归时，先核对用例名称、业务契约和断言方向。重启、重复同步和重放测试应直接验证副作用次数。测试断言错误时优先修复断言，并用确实产生多余副作用的反例验证它会失败。

命名与可读性按[清单](../programming-paradigms/references/naming-and-clarity.md)执行：包名短小全小写，文件名 snake_case，导出符号 PascalCase，未导出 camelCase。方法用业务动词命名。只在真实替换或测试隔离时才加接口，不提前拆层。通过 `gofmt`。

参考 [Gin 请求绑定](https://gin-gonic.com/en/docs/binding/binding-and-validation/)及 [Go 事务](https://go.dev/doc/database/execute-transactions)。涉及模块分层或复用设计时，读取[范式与模式选择](../programming-paradigms/SKILL.md)。

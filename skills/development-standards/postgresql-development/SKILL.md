---
name: postgresql-development
description: 开发或评审 PostgreSQL schema、查询、索引、约束、事务和版本化迁移代码。涉及数据库身份、实际部署或数据迁移时同时读取相应运维规范。
---

# PostgreSQL 开发规范

- 每组业务数据明确写入服务及 schema 迁移入口。共享实例中通过已定义的服务契约或专用读取接口访问其他服务拥有的数据。沿用各仓的版本化迁移工具和 SQL、pgx 或 ORM 入口。
- 用数据库约束保护持久化不变量。根据业务语义选择主键、外键、唯一性、非空及检查约束。参数化查询值，动态列名或排序项来自允许列表。明确金额精度、时间和时区、空值以及分页顺序在数据库和 API 的表达。
- 事务覆盖需要原子提交的读写，尽量缩短锁持有时间。防止重复和竞态时，优先考虑唯一约束、条件更新等原子操作，再按需求选择行锁或更高隔离级别。仅对可安全重试的事务重试完整操作，外部副作用单独保证幂等或按需使用 Outbox。
- 已应用的迁移保持可重放历史，后续变更新增版本。滚动发布存在新旧应用共存时，先扩展 schema，再发布兼容读写、回填并核对数据，最后按实际消费者退出情况收缩。逐项核对锁、表重写、索引创建与迁移器的事务模式。
- 在目标主版本或等价 PostgreSQL 上验证空库初始化、从代表性旧版本升级、关键查询和兼容窗口。涉及锁、执行计划或并发的变更，使用代表性数据量和隔离环境验证。分别记录应用回退、schema 修复和数据恢复路径。依赖真实数据库的测试被跳过时，记录缺少的 fixture 与未覆盖的行为。测试和本地启动可保留既有自动建表模式，受管环境需核对实际模式、独立迁移入口和应用身份的有效权限。
- 涉及迁移执行、授权或数据库安全审查时，先读[系统与数据库三权分立](../../operations-management/system-db-three-role-security/SKILL.md)。涉及有状态恢复时按[备份与恢复规范](../../operations-management/backup-disaster-recovery-and-data-migration/SKILL.md)执行。

Schema、表、列和约束名使用稳定的 snake_case，并与所属服务的代码符号可互相对上。避免用难以阅读的动态 SQL 拼接列名或排序项；标识符来自允许列表。更完整的命名原则见[清单](../programming-paradigms/references/naming-and-clarity.md)。

参考 [PostgreSQL ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html)及[范式与模式选择](../programming-paradigms/SKILL.md)。

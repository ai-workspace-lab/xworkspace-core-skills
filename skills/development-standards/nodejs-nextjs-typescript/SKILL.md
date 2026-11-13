---
name: nodejs-nextjs-typescript
description: 开发或评审 Node.js、Next.js 和 TypeScript 应用。用于页面、业务模块、Server Component、Route Handler、Server Action、服务端 API 客户端及运行时输入校验。
---

# Node.js / Next.js / TypeScript 开发规范

- 先读路由结构、运行目标、锁文件和已有调用链。沿用现有 App Router 或 Pages Router、包管理器和测试入口。项目同时支持 Node.js、Worker 或静态构建时，按实际运行目标检查模块、环境变量和服务器能力。
- 页面和布局负责路由组装。业务功能尽量就近组织，例如 Portal 的 `src/modules`。服务端模块持有 API 客户端、会话和私有配置。跨模块共享前确认行为与维护方一致。
- App Router 中默认在服务端渲染和取数，交互、浏览器 API 与本地状态放在最小的 Client Component 边界。Server Component 直接调用现有服务端客户端或数据访问入口。Route Handler 与 Server Action 用于明确的 HTTP、浏览器或表单入口，入口各自验证授权。
- 对请求、环境配置和上游响应做适当的运行时验证。用 TS 表达验证后的形状、可空性和错误分支。API 提供方维护权威契约，沿用已有客户端或类型生成流程。客户端展示服务端的业务判断，UI 校验用于即时反馈。
- 明确每份数据的缓存范围、失效时机与身份边界。用户或租户数据只有在隔离键与失效机制明确时才共享缓存。提交后按实际读取路径验证刷新、错误与空状态。
- 通过仓库已有 lint、类型检查及相关测试验证。变更跨服务器与浏览器边界、缓存或运行目标时，覆盖对应构建与用户路径。涉及环境路由时，测试注入固定的合成上游地址，并验证路径、参数和转发行为。涉及框架配置时验证语义，避免用引号、缩进等源码拼写替代行为断言。发现两个 UI 实现时先追踪真实路由、动态加载和消费者，再决定合并或移除。构建流程参见[工程规范](../../engineering-standards/project-development-standard/SKILL.md)。

参考 [Next.js 服务端与客户端组件](https://nextjs.org/docs/app/getting-started/server-and-client-components)及 [BFF 指南](https://nextjs.org/docs/app/guides/backend-for-frontend)。涉及模块分层或复用设计时，读取[范式与模式选择](../programming-paradigms/SKILL.md)。

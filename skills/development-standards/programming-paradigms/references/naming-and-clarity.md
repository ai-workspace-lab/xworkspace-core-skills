# 命名、可读性与轻量扩展

新增或评审代码时，先沿用所在目录已经在用的命名和结构。本页把各技术栈里已经写进仓库约定、或在实际目录中反复出现的写法收成一份可检查的清单。不把历史目录一次性改名，也不为“看起来更统一”而扩大改动范围。

清单整理自 `portal`（含 `AGENTS.md` / `mcp/conventions.md`）、`accounts`、`Infrastructure-MCP-Server`、`playbooks` 与 `iac_modules/terraform-hcl-standard`。这些是开发时的对照来源，不证明历史文件已经全部一致。

## 共同原则

1. 名称表达业务含义，不表达设计模式身份。用 `load_cmdb`、`build_inventory`、`stripeCheckout` 这样能对上用例的名字，不要用 `XxxManagerFacade`。
2. 文件名、函数名、类型名、YAML 键和 HCL 资源名应能互相指认。一个名字只代表一种东西。
3. 写清楚，而不是写得短。避免把多层判断、隐式转换和副作用压进一行，或使用所在文件里并不常见的冷僻语法。
4. 先在现有模块、Role、脚本或函数上做最小扩展。只有出现真实的复用、替换或所有权边界时再拆层，不为“以后可能用到”预建框架。
5. 同一目录不要混入第三种文件名风格。历史仓库里同时存在 `snake_case` 与 `kebab-case` 时，新文件跟随最近邻文件。
6. 公共 API、CLI 参数、退出码和配置键保持稳定；内部命名可在本目录惯例内整理。

## JavaScript / TypeScript

对照来源：`portal/AGENTS.md`、`portal/mcp/conventions.md`，以及 `src/modules`、`src/lib`、`frontend-router/src`。

| 对象 | 约定 | 例子 |
| --- | --- | --- |
| 组件文件 | PascalCase | `AccountGettingStarted.tsx`、`UserOverview.tsx` |
| 工具与模块文件 | 文档约定为 kebab-case；若所在目录已是 camelCase，则跟随该目录 | `runtime-loader.ts`、`home-marketing.ts`；`ops/planCatalog.ts` 维持所在目录现状 |
| 变量与函数 | camelCase | `userName` |
| 常量 | UPPER_SNAKE_CASE | `API_BASE_URL` |
| 类型 | PascalCase；泛型参数加 `T` 前缀 | `TUser` |
| 类型写法 | `type` 做别名，`interface` 做对象形状；公开函数写明确返回类型 | |

函数保持短小，避免在 JSX 里堆大型内联对象。仅在需要浏览器能力时加 `'use client'`。Dashboard 全局状态沿用已有 Zustand 边界，不新引入状态库，也不在组件里解析可分享的 URL 状态。业务功能放到 `src/modules` 既有模块附近，不平行再造一套目录。

## Go

对照来源：`accounts` 的 `cmd/`、`api/`、`internal/`，以及 `Infrastructure-MCP-Server` 的 `internal/`。

| 对象 | 约定 | 例子 |
| --- | --- | --- |
| 包名 | 短小、全小写、不加下划线 | `store`、`cmdb`、`billingcatalog`、`dbruntime` |
| 文件名 | snake_case | `referral_campaign.go`、`http_server.go`、`mfa_recovery_codes.go` |
| 导出类型与函数 | PascalCase | `HTTPServer`、`NewHTTPServer`、`TextResult` |
| 未导出类型与函数 | camelCase | `handler`、`authMiddleware`、`isPublicPath` |
| 命令入口 | `cmd/<短名>` | `cmd/accountsvc`、`cmd/migratectl`、`cmd/infrastructure-mcp-server` |

Handler 负责绑定、鉴权和响应映射；业务规则放在用例或 `internal/service`；持久化放在 store。接口只为真实替换或测试隔离而设，不为每个包预置接口。方法名用业务动词，例如 `stripeCheckout`、`claimTaskRun`，避免空泛的 `Handle` / `Process` 堆叠。通过 `gofmt` 和仓库已有检查。

## Python、Shell 与 YAML

对照来源：`playbooks` 的脚本、inventory 与测试，以及 IaC 共享渲染脚本。

| 对象 | 约定 | 例子 |
| --- | --- | --- |
| Python 函数与模块 | snake_case；测试文件 `test_<主题>.py`，用例类 PascalCase | `load_cmdb`、`build_inventory`、`test_service_probes_owner_contract.py` |
| Python 常量 | UPPER_SNAKE_CASE | `CMDB_SCHEMA_VERSION`、`REPO_ROOT` |
| 私有辅助 | 单下划线前缀 | `_from_explicit_file` |
| Shell 函数 | snake_case 动词 | `checkout_release`、`check_root`、`render_server_compose` |
| 脚本文件名 | 跟随所在目录；历史同时有下划线与连字符 | `terraform_cmdb.py`、`bootstrap-pinned-xconnect.sh` |
| YAML 键与 Ansible 变量 | snake_case；GitOps 清单文件多为 kebab-case 短名 | `uat-akamai-web-saas.yaml`、`accounts-migration.schema.yaml` |

Shell 只串联已有命令和简单条件。结构化解析、校验和可独立测试的决策放 Python。参数加引号，检查命令与管道失败，不使用 `eval` 拼装命令。机器可读结果写 stdout，诊断写 stderr。YAML 描述结构，复杂校验在消费边界完成，不把循环和目标选择藏进难以阅读的模板语法。

## HCL

对照来源：`iac_modules/terraform-hcl-standard/AGENTS.md`。

- 资源与模块块名必须是合法、稳定的 HCL 标识符，由渲染器（如 `tf_id`）净化，不手写会漂移的 key。
- 可批量编排的 env 保持扁平显式块：禁止在 env 的 `.tf` 中使用 `for_each`、`count`、`dynamic` 和 `templatefile` 控制结构。循环与条件放在 Python + Jinja2，使 HCL 可审计、diff 友好，并避免 key 漂移导致重建。
- 标准文件名沿用 `main.tf`、`variables.tf`、`outputs.tf`、`versions.tf`、`provider.tf`。生成物不入库。
- 扩展时优先复用既有模块（如 `modules/compute`），不在 env 里重写 provider 资源，也不另起一套渲染入口。提交前执行 `terraform fmt` 与 `validate`。

## 检查

- 不熟悉这段代码的人，能否只靠名字找到入口和结果。
- 新文件是否跟随了最近邻的命名，而不是借机改写整个目录。
- 本次变更是否只在现有边界里增加了最小的一块，而不是多了一层抽象。

---
name: infrastructure-as-code-spec
description: |
  Infrastructure-as-Code YAML Rendering Pattern and Coding Standards for iac_modules.
  Dictates how AI should read/write infrastructure templates, isolate states by environment, and interoperate with configuration layers.
  Covers resource identity vs state space (a name composed from a per-trigger variable over a shared state makes Terraform destroy and recreate the host on every alternation), banning fallback defaults in declarations (a missing topology variable must fail the render, not silently produce a valid-looking production domain), and when topology declarations can be split out of the module repo.
---

# Infrastructure-as-Code (IAC) 规范指南

本规范专门用于指导在 `iac_modules` 仓库中进行自动化与基础设施代码（IaC）建设的最佳实践与红线原则。当 AI 进行任何云原生资源的修改与新增时，必须严格遵守以下守则。

## 1. 声明式 YAML 驱动与渲染隔离
**原则**: 基础设施的拓扑变量、机器规格与具体参数，绝对禁止硬编码于 HCL (Terraform) 文件中。
- **配置分离**: 强调多环境（`sit` / `uat` / `prod`）的具体拓扑必须在对应的 `config/resources/[env]/*.yaml` 中清晰定义。
- **状态隔离**: Backend State 的 key 或者 namespace，强制要求按照环境级目录存放（例如：`uat/databases.tfstate`），绝不可跨环境复用状态空间。
- **构建机制 (IaC + Python Jinja2)**: 目前架构使用 Python 脚本 (`scripts/generate.py render`) 结合 Jinja2 模板解析 YAML 并自动输出 `.tf.json` 形式的配置文件。所有针对具体环境的逻辑修改，应优先考量在 YAML 拓扑或渲染逻辑中完成，而非直接修改基础模块。

## 2. HCL 代码纯净度与限制
**原则**: Terraform HCL 代码仅仅作为最底层的资源“声明书”，应保持极致的简洁和纯粹。
- **弱化分支判断**: 强烈禁止在 HCL 中过度使用复杂的逻辑分支（如多重嵌套的 `count`、复杂的 `dynamic` 块与条件表达式）。如果遇到业务级的条件判断，应将其上浮至 Python Jinja2 的渲染层去决策，使最终生成的 HCL 趋近纯声明式结构。
- **禁止内嵌脚本**: 绝对禁止在 HCL 定义（例如 `local-exec` provisioner 或 `null_resource` 中）内嵌或编写 `shell`、`python` 等执行脚本。

## 3. 互操作性设计 (IaC ↔ Config-as-Code)
**原则**: 明确边界，解耦职责，通过标准的凭证库（Vault）与静态清单进行传递。
- **职责边界 (CMDB)**: IaC (Terraform) 层的唯一职责是分配与建立云上的计算、网络、存储等资源，并在输出阶段（Outputs）自动生成标准化的结构资源清单（如 `cmdb.json`）。IaC 不负责具体的软件系统配置。
- **状态解耦桥梁**: 跨阶段传递的敏感凭证（如 IaC 初始化数据库时随机生成的初始密码），绝对禁止写入本地文件向后传递，而是必须由 IaC 直接推送到 HashiCorp Vault 的 Secret 引擎中；后续 Ansible Playbooks 将仅通过 Vault 去安全提取状态。
- **拓扑声明与模块的归属判据**: 模块（HCL + 模板 + 渲染器）是可复用代码，拓扑声明（`config/resources/**`）是随环境变动的数据，两者变更频率不同，不应被同一个 ref 绑在一起。判断能否分离，看三点：声明里是否引用了模块内部标识（`source =`、模块路径）、渲染器是否把声明路径写死（还是作为 `--resources` 之类的参数传入）、生成产物目录是否签入仓库。三者都为"否"时耦合仅剩数据，可以外移；此时**优先移入唯一消费者仓库**，而不是新开一个仓 —— 独立成仓只在出现第二个消费者、或声明需要不同访问控制（含 SSH 公钥、完整主机拓扑）时才划算。

## 4. 资源标识必须与状态空间一一对应
**原则**: 同一份 state 在任何触发路径下，都必须被要求提供**同一组资源名**。

- **资源名不得由随触发路径变化的变量拼接**。若主机名写作 `console.{{ TARGET_DOMAIN_BASE }}`，而不同触发路径（分支 push / 手工 dispatch / tag）对该变量取值不同，却共用同一个 workspace 与 state key，则 Terraform 会认为"旧名字的资源消失了、新名字的资源出现了"，于是**销毁一台再新建一台**。表现是资源被反复重建、IP 漂移、已部署的服务凭空消失。
- **判据**: 拼进资源名的每个变量，必须在所有能命中该 state 的触发路径上取值一致；做不到就必须把该变量一并纳入 workspace 名与 state key，让不同取值落在不同状态空间。
- **环境区分靠后缀，不靠域名基准**。`sit` / `uat` / `prod` 应通过 `env_suffix` 等后缀区分，而不是让某个环境落在另一套域名（尤其不能落在生产域名下）—— 后者既制造上面的重建问题，又会把非生产记录发布进生产 zone。

## 5. 渲染变量不设默认值
**原则**: 缺失的拓扑变量必须让渲染失败，而不是渲染出一个"看起来对"的值。

- **禁止在声明里写 fallback**。`{{ env.get('TARGET_DOMAIN_BASE', 'svc.plus') }}` 这类写法会在变量缺失时静默产出一个合法但错误的域名；当各文件的 fallback 还互相矛盾（同一环境的不同文件、甚至同一台主机的两个服务域名指向不同基准）时，错误会以"部分正确"的形态存在，极难发现。一律改为 `{{ env['TARGET_DOMAIN_BASE'] }}`。
- **注意 Jinja 默认的 `Undefined` 不抛错**，缺键会渲染成空串，`console-nat.{{ ... }}` 变成 `console-nat.` —— 同样是"看起来已渲染"。因此需要在渲染器入口对必需变量做显式断言，并在报错信息里指名是哪个变量。用具名必需列表即可，不必把整个 Environment 切成 `StrictUndefined`（那会改变模板里所有可选变量的行为）。
- **渲染器的默认参数同样是隐患**。`--resources` / `--workdir` 之类若带默认值，一旦默认指向的文件被移动或删除，命令行少传一个参数就会走向意料之外的目标。拓扑输入应当是必填参数。

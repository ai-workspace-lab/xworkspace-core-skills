---
name: iac-hcl
description: 开发或评审 Terraform 或 OpenTofu HCL 模块、根模块组装、变量输出、资源引用与状态地址变更。
---

# IaC / HCL 开发规范

- 先定位根模块、调用方、Provider、状态空间和当前资源地址。按[工程 IaC 规范](../../engineering-standards/infrastructure-as-code-spec/SKILL.md)读取拓扑与渲染约定。GitOps 管拓扑声明，IaC 模块消费输入并输出资源事实。
- 根模块负责目标绑定和组装。子模块封装有明确生命周期、可复用的资源组合，使用类型明确的输入和最少的必要输出。已有模块契约能表达需求时扩展已有模块。复用条件相同的资源关系，保留不同 Provider 和生命周期的明确边界。
- 用资源引用表达依赖，确有隐式依赖时才用显式依赖。用稳定资源标识维护 state 地址。目标仓要求由 YAML 渲染为显式块时，遵循该约定并验证输出和地址稳定性。模块移动、键变更或资源改名先核对 state 地址及迁移路径，验证实际 plan 中的创建、替换与删除。
- HCL 表达目标状态，环境选择由权威声明驱动。复杂输入校验和渲染按现有工具归属，宿主机操作交给 Playbooks。复用应减少环境配置副本，避免让根模块变成多 Provider、多生命周期的开关集合。
- 使用仓库实际工具执行格式检查、validate 和代表性 plan，核对正确的环境和 state。记录仅静态验证或 plan 的范围。资源变更的授权和执行沿用工程与运维流程。

参考 [Terraform 模块组合](https://developer.hashicorp.com/terraform/language/modules/develop/composition)及[范式与模式选择](../programming-paradigms/SKILL.md)。

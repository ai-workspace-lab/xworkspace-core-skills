---
name: ansible-playbook
description: 开发或评审 Ansible Playbook、Role、任务、变量、模板和 handler，覆盖角色复用、幂等、收敛与失败传播。
---

# Ansible Playbook / Role 开发规范

- 先读[配置即代码规范](../../engineering-standards/config-as-code-spec/SKILL.md)，涉及系统或数据库运维同时先读[三权分立](../../operations-management/system-db-three-role-security/SKILL.md)。定位现有入口、Role 和 CMDB/inventory 来源，核对目标、变量优先级和权限边界。
- Playbook 组织目标、顺序与依赖，Role 封装稳定的主机能力，模板只负责渲染。通过明确参数复用现有 Role，分离共享默认值和环境专属输入。目标、秘密及环境差异沿用权威来源。
- 优先使用 `ansible.builtin.*` 等现有幂等模块。配置确实变更时通过 handler 应用必要的 reload 或 restart。需调用命令时定义实际的 changed/failed 条件，并按仓库约定将复杂逻辑放入独立可测试的脚本或模块。
- 对步骤明确先决条件、变更顺序和失败后的可恢复状态。涉及多个入口时确认同一资源只有一个日常声明负责人，按[执行归属规范](../../engineering-standards/execution-ownership-migration/SKILL.md)划分宿主机、Compose 与 Kubernetes 的职责。
- 执行已有 syntax-check、lint 和受影响的 inventory 校验。check mode 按模块支持范围解读。需要证明收敛时，在授权的隔离目标执行两次，核对第二次实际变化和服务状态。按本次变更覆盖失败、重复执行及 handler 行为。角色契约、模板渲染和 syntax-check 可先验证局部行为。报告另行记录目标机收敛、进程状态及业务探测证据。

参考 [Ansible 检查模式](https://docs.ansible.com/projects/ansible/latest/playbooks_checkmode.html)及[范式与模式选择](../programming-paradigms/SKILL.md)。

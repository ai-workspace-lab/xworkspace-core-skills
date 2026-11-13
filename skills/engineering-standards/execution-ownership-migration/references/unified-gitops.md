# Unified GitOps 多执行器治理

Git 声明期望状态，执行器在各自管理范围内应用变更，可观测性记录运行结果，独立审计把变更和实际结果关联起来。按环境实际运行形态选用执行器。仓库归属沿用[五仓职责](../SKILL.md)。

| 管理范围 | 执行器 | 声明与执行边界 |
| --- | --- | --- |
| Linux、VPS、裸机 | Ansible Pull | GitOps 声明主机基线和非敏感参数，Playbooks 提供幂等 role。管理 OS、软件包、SSH、主机防火墙、systemd、运行时和 K3s 的主机级配置。 |
| Docker Compose、Docker Swarm | Doco CD | 按目标 Docker 实例和项目或 Stack 管理容器服务、镜像、应用环境配置和关联资源。宿主机软件包、运行时守护进程和主机级配置归主机执行器。 |
| Kubernetes、K3s | Flux CD | 通过 Kustomization、HelmRelease 等管理集群内声明，包括工作负载、Operator 及其声明输入。已由 Helm 或 Operator 派生的对象或字段，由对应控制器管理。 |
| 云资源、云网络、云 DNS | OpenTofu / Terraform | GitOps 声明拓扑，IaC 管理资源、State 和 CMDB，供下游执行器定位目标。 |
| 秘密 | Vault 或 SOPS，按环境适配 | 声明引用或经过批准的密文。为每个目标 Secret 或秘密文件指定唯一写入方，并限定读取身份和解密范围。 |
| 指标、日志和审计证据 | vmagent、Vector 或环境现有采集器 | 采集并关联执行结果和服务信号。采集器的安装及配置按运行形态分配执行 owner。 |

## 唯一声明所有权

- 按环境、目标、资源标识记录声明路径和执行 owner。对需要多控制器协作的对象，明确字段边界，例如由 Flux 管理 Deployment 模板，HPA 管理副本数。依赖通过引用或就绪条件交接，避免第二套配置。
- K3s 节点由 Ansible 管理 OS、K3s 安装及节点级配置。Flux 管理集群内应用。移交打包组件时，先处理 K3s 自带控制器或 manifests 的写入路径，再由 Flux 接管。Doco CD 管理的 Compose 应用，其日常发布统一走声明入口，主机 Playbook 负责引导与运行依赖。
- 明确执行器自身安装、更新和恢复的 owner。启用 Doco CD 自更新时，将其 Stack 的日常更新一并移交。手工操作、CI 推送部署和旧定时任务纳入同一所有权盘点。
- 每个交付单元记录实际应用的 Git revision、目标以及固定的制品版本或 digest。应用 Git 目录或 ref 与执行身份按环境限定。能够修改高权限执行器所消费声明的身份，也纳入对应权限审查。

## 收敛语义

- Ansible Pull 由定时器或其他调度器触发，使用互斥避免并发。需要修复无 Git 变更时的漂移，周期运行应执行幂等 Playbook，避免启用仅源码变化才运行的 `--only-if-changed`。[Ansible CLI](https://docs.ansible.com/projects/ansible/latest/cli/ansible-pull.html)
- Doco CD 支持 Git 轮询及 Webhook，部署 Compose 项目或 Swarm Stack。按实际版本和配置核对触发、重试、同 revision 重部署及删除行为。无 Git 变更时的运行时漂移需有明确检测和恢复路径，自动修复能力以目标环境实测为准。[核心概念](https://doco.cd/latest/Core-Concepts/) · [Swarm 模式](https://doco.cd/latest/Advanced/Swarm-Mode/)
- Flux 按控制器及资源配置持续调谐。分别确认 Kustomization 的删除和就绪策略、HelmRelease 的漂移检测模式及例外，以及依赖和健康检查。[Kustomization](https://fluxcd.io/flux/components/kustomize/kustomizations/) · [HelmRelease](https://fluxcd.io/flux/components/helm/helmreleases/)

接管、验收与回退按[运维细则](../../../operations-management/service-catalog-and-runbook-standard/references/unified-gitops-operations.md)执行。

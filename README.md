# Long Horizon Agents

**让 agent 跨会话持续推进项目，并把进度留在项目里。**

一个规划者审查方向，一个执行者落实任务；两者通过简明文档协作，按关键结果和预计终点安排接续。适用于持续数天或更久的研究、软件开发、数据处理等工作。

本仓库提供可复制的角色提示、项目文档、Codex 接入说明和初始化脚本。模型、调度服务和任务运行环境由你选择。

## 工作方式

```mermaid
flowchart LR
    U[用户目标与授权] --> P[规划者]
    P --> D[共享项目文档]
    D --> E[执行者]
    E --> J[普通任务程序]
    J --> R[结果与运行记录]
    R --> D
    D --> P
```

| 角色 | 负责什么 | 主要输出 |
| --- | --- | --- |
| 规划者 | 总览目标、研究问题、证据缺口、优先级和停止条件 | `PLAN.md`、`DECISIONS.md` |
| 执行者 | 实现、分析、排查、任务接续、资源安排与结果交付 | `CURRENT.md`、任务卡、`HISTORY.md` |
| 普通任务程序 | 执行预先确定的步骤，记录真实终态和运行信息 | 日志、退出状态、产物 |

例如可以给规划者选 Astra，给执行者选 GPT‑6.1 Sol。实际模型通过客户端或运行平台设置；仓库中的配置只是可修改的示例。

## 快速开始

需要 Python 3.10+，无需安装 Python 依赖。以下命令可以在 PowerShell、bash 或 zsh 中运行。

**新项目**：在 GitHub 点击 **Use this template → Create a new repository**，克隆生成的仓库后，在其中运行：

```sh
python scripts/init_project.py --target . --name "我的长期项目"
```

**已有项目**：将模板仓库拉到旁边，再指定你的项目目录：

```sh
git clone https://github.com/rose8happy/long-horizon-agents.git
cd long-horizon-agents
python scripts/init_project.py --target ../my-project --name "我的长期项目" --dry-run
python scripts/init_project.py --target ../my-project --name "我的长期项目"
```

私有仓库需要使用有权限的 GitHub 账号。也可以下载仓库 ZIP，解压后运行脚本。

初始化会生成：

```text
my-project/
├── AGENTS.md                       # 仅追加带标记的入口说明
├── .agent/
│   ├── agent.config.example.toml   # 模型与工作区配置示例
│   ├── roles/{planner,executor}.md
│   └── codex/                     # 接入说明与两种唤醒提示
└── docs/agent/
    ├── README.md
    ├── MISSION.md
    ├── PLAN.md
    ├── CURRENT.md
    ├── DECISIONS.md
    ├── HISTORY.md
    └── templates/TASK.md
```

现有文件会保留；再次运行会跳过已存在的模板，不会恢复模板覆盖你的修改。初始化不会创建会话、调用模型、安装依赖、创建 scheduled task 或运行项目任务。

### 启动两个角色

1. 填写 `docs/agent/MISSION.md`：目标、完成判据、授权范围及工作区。
2. 为两个角色打开独立会话，并让它们读取同一个 canonical 工作区。
3. 在规划者会话中发送：

   > 阅读 `.agent/roles/planner.md` 和 `docs/agent/MISSION.md`。建立项目当前计划，优先找出最有价值的未解决问题，并明确执行者可自主推进的范围。

4. 在执行者会话中发送：

   > 阅读 `.agent/roles/executor.md` 和 `docs/agent/` 当前文档。接续当前已授权任务，完成具体交付；只有真正等待依赖时才安排下一次唤醒。

5. 两个角色的 scheduled task 使用 `.agent/codex/` 提示模板。先手动运行一轮，再按项目节奏启用。

远程项目应把上述文件初始化到远端 canonical 仓库，两个角色都通过同一入口读写；本机历史副本不能承担共享状态。

## 五份核心文档

| 文档 | 回答的问题 | 写入负责人 |
| --- | --- | --- |
| `MISSION.md` | 用户要完成什么，什么算完成，授权到哪里？ | 用户；规划者忠实整理 |
| `PLAN.md` | 接下来最值得做什么，为什么，依赖什么？ | 规划者 |
| `CURRENT.md` | 实际进展、下一动作、阻断和下次接续时刻是什么？ | 执行者 |
| `DECISIONS.md` | 为什么选择或停止某个方向，什么证据会改变判断？ | 规划者汇总；执行者提供证据 |
| `HISTORY.md` | 过去哪些重要任务完成了，哪些经验和产物可复用？ | 执行者 |

详细任务使用[任务卡](templates/project/TASK.md)，详细结果和日志留在原位置并链接。无需每次唤醒通读历史，也无需把同一状态复制到多个文件。

## 核心约定

- 用户目标与明确授权优先；agent 生成的计划不能自行缩减目标或新增无依据限制。
- 执行者自主处理已授权范围内的常规实现和恢复，重要方向变化提交证据供规划者判断。
- 规划更新带版本号，在安全边界生效；运行中的任务保持原合同。
- 每个资源只有一个负责发车的执行者；规划者通过文档交接安排。
- 重要任务完成判据包含结果交付，避免把“进程启动”或“某阶段完成”当成整个目标完成。
- 等待一个结果只阻塞它的后继。独立准备和分析继续推进，准备好可执行的接棒任务。
- 真正等待时按预计终点唤醒。没有新信息就保持安静；短步骤由程序接续。
- 身份检查、资源检查和测试服务具体风险；已有证据可复用，费用记录与费用准入分开。
- 历史包含重要成功、负结果和失败。旧结论写明适用范围，可以被新证据修正。

完整约定见 [协作与恢复](docs/protocol.md)，调度见 [Codex 接入](adapters/codex/setup.md)。

## 示例与检查

- [研究项目：新方法与对照的完整比较](examples/research-project/README.md)
- [软件项目：可接续的数据迁移](examples/software-project/README.md)
- [恢复演练与有效性检查](docs/recovery-and-evaluation.md)

运行初始化脚本的测试：

```sh
python -m unittest discover -s tests -v
```

## 范围与后续维护

第一版集中解决职责、共享状态、交接和恢复。真正的训练、迁移、下载程序由项目提供；真实模型调用和调度由平台提供。核心规则可以配合现有 coding skills 使用。

更新模板仓库后，在已接入项目中运行 `--dry-run` 查看缺失文件。现有文件不会自动升级，按需要人工或由 agent 合并具体改进。仓库改动使用可追溯的 Git 提交；重要行为变化写入 [CHANGELOG.md](CHANGELOG.md)。

## 参考

- [Superpowers](https://github.com/obra/superpowers)：可组合的 coding skills 与开发流程。
- [Anthropic：Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)：跨上下文的进度与交接实践。
- [OpenAI 官方 scheduled tasks 文档](https://learn.chatgpt.com/docs/automations)：会话内接续、独立定时任务及平台边界。

本仓库是独立实现。上述项目作为参考链接；示例均为虚构，不包含私人项目数据。

## 许可

[MIT](LICENSE)。

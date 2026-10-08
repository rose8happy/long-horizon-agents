# 软件项目：可恢复的数据迁移

本例完全虚构。服务、表名、数字和路径只用于演示协议，不声称发生过真实迁移。代码描述是任务设计示意，不是可直接上线的生产作业框架。

目标是把旧地址字段迁移为结构化字段，并完成历史回填。项目只需要两个持久角色；迁移与回填仍由普通程序运行。

- `.agent/roles/planner.md`：规划者，维护兼容策略、任务顺序和迁移成功条件。
- `.agent/roles/executor.md`：执行者，落实任务、管理资源、读取检查点并恢复程序。
- `scripts/backfill_addresses.py`：项目普通程序，按记录范围处理数据并保存检查点。
- `docs/agent/`：任务、计划、结果和资源归属的共享入口；记录有冲突时核实原证据，唤醒提示不保存运行快照。

## 最小文档片段

`docs/agent/MISSION.md`：

```yaml
objective: 完成地址字段迁移，使新旧客户端在过渡期均可使用服务
authorization: 用户授权按已批准迁移方案自主修改、部署和回填
constraints:
  - 保留旧字段到明确批准的清理阶段
  - 使用现有服务凭证与资源，不扩展账户权限
  - 破坏性清理需另行取得用户授权
success: 新字段覆盖目标记录，读写兼容，回填可恢复且结果可追溯
```

授权来自这个虚构项目的用户。模板本身不会授予部署、数据修改或破坏性清理权限。

`docs/agent/PLAN.md`：

```yaml
version: 2
direction: 先扩展模式并保持双写，再分批回填，最后切换读取
tasks:
  - add-compatible-schema: completed
  - deploy-dual-write: completed
  - backfill-addresses: ready
  - verify-backfill: blocked_by_backfill-addresses
  - switch-reads: blocked_by_verify-backfill
next_review: 回填完成后依据覆盖率、冲突样本和兼容结果决定读取切换
```

`docs/agent/CURRENT.md`：

```yaml
state: ACTIVE
adopted_plan: 2
active_task: backfill-addresses
task_brief: docs/agent/tasks/backfill-addresses.md
resources:
  writer-slot: {owner: executor, task: backfill-addresses, state: reserved}
  test-worker: {owner: executor, task: null, state: idle}
checkpoint: work/backfill-addresses/checkpoint.json
next_action: 读取任务状态及检查点，从未完成范围恢复普通回填程序
```

资源归属集中由执行者维护。规划者不同时启动第二个写入程序；它可以并行整理后续兼容验收说明。没有必要的独立任务时，不为提高资源利用率制造工作。

## 一个可以直接接手的任务

`docs/agent/tasks/backfill-addresses.md`：

```yaml
name: backfill-addresses
status: ready
plan_version: 2
purpose: 为迁移快照中的旧记录生成结构化地址
dependencies:
  - 兼容模式和双写部署已完成，部署记录可读取
  - 已保存稳定目标记录集合和版本化转换规则
acceptance:
  - 目标集合的每条记录均已转换或有明确的冲突记录
  - 重复执行不覆盖更新的用户数据，不重复应用迁移效果
  - 保存覆盖率、冲突清单及最终检查点，释放写入资源
next_action: 检查 terminal.json 与检查点，再恢复下一个未完成范围
evidence:
  - work/backfill-addresses/input-manifest.json
  - work/backfill-addresses/checkpoint.json
  - results/backfill-addresses/coverage.json
  - results/backfill-addresses/conflicts.jsonl
  - results/backfill-addresses/terminal.json
```

## 重启与重复唤醒

恢复逻辑保持在任务程序和任务状态中：

```text
若有完整终止记录：补齐 CURRENT/HISTORY 引用，释放资源后进入下一任务。
否则获取任务级互斥锁；已有执行者持锁时不启动重复回填。
读取输入清单和检查点，按稳定记录键处理未完成范围。
每条更新检查源记录版本，并使用固定 migration_version 标记。
已应用同一版本则跳过；源版本变化则记录冲突，避免覆盖用户更新。
提交一个批次的更新后，持久化检查点；最后写入完整终止记录。
```

锁由运行环境释放，不能仅凭旧状态文本认定任务仍活跃。崩溃可能发生在更新提交后、检查点保存前；重放依靠记录标记和源版本检查保持安全。完成记录已经写出但文档尚未更新时，下一次唤醒只补齐文档，不重新执行迁移。

这里具体检查重复执行和崩溃恢复，是因为它们可能改变用户数据；不需要给每个普通文档更新另加审查流程。

## 有复用价值的已关闭工作

`docs/agent/HISTORY.md` 的一个虚构条目：

```yaml
task: assess-single-transaction-backfill
status: completed
purpose: 判断单事务回填是否适合目标数据量
result: 在测试副本上出现长锁等待，取消该方案并采用可恢复批次
limits: 测试负载不代表全部生产时段；只否定此次单事务方案
reuse: 保留稳定记录键、版本检查和批次恢复设计，避免重做同一试验
evidence:
  - results/single-transaction-assessment/summary.md
  - results/single-transaction-assessment/lock-observations.csv
cost_observed: {worker_minutes: 24, test_rows: 120000, output_mb: 2}
```

这个条目记录了已关闭的失败方向及其价值。成本用于理解工作量；除用户明确给定上限外，不把数字变成新的启动门槛。

## 计划更新与调度

规划者可能根据实际冲突提出版本 3，通过已授权的消息向执行者说明证据与建议。执行者自主调整常规方法；在批次提交并保存检查点后改变回填步骤，是为了防止重复更新或丢失进度，不是为了遵守预先合同。用户要求停止时优先处理，并记录停止点。若转让写入资源的负责人，须由新负责人明确接受，避免两个角色同时写入。

程序运行时可发出完成事件。仅支持定时唤醒的平台则依据剩余范围与实际吞吐估计 ETA；无可靠 ETA 时，在首个有意义的进度量后校准。唤醒未取得终止信号时按新证据延后并退避；不要按固定短间隔反复查进程。只有等待中的任务结果依赖才阻塞后续工作。

稳定的调度提示示例：

```text
按 .agent/roles/executor.md 恢复本项目。
读取 docs/agent/MISSION.md、PLAN.md、CURRENT.md，相关 HISTORY 按需读取，
再读取当前任务说明和程序持久状态，处理完成、失败及重启恢复。
遵守 .agent/roles/planner.md 所定义的计划协作，在安全边界采纳更新。
执行下一个依赖满足且已授权的任务，记录证据和资源归属。
若只能等待，依事件或当前 ETA 更新同一唤醒安排；
若迁移目标已完成，关闭唤醒。提示中不携带运行状态或进程信息。
```

重复唤醒调用相同入口，读取相同文档和检查点。任务程序保障重放安全，执行者保障单一资源归属；不需要把调度器扩展成另一个项目控制系统。

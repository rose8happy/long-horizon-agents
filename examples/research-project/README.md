# 研究项目：比较一个候选方法

本例完全虚构。方法、数据、数值和路径只用于说明协作方式，不代表真实研究结论，也不提供可直接启动的生产作业框架。

项目目标是判断候选方法是否值得继续投入。两个持久角色配合普通训练与分析程序；无需为了运行一次训练再建立一个持久代理。

- `.agent/roles/planner.md`：研究规划者，维护问题、比较条件、结论与下一步计划。
- `.agent/roles/executor.md`：执行者，落实已授权任务、分配资源、保存结果并恢复中断。
- `scripts/train.py`、`scripts/compare.py`：项目已有普通程序；由执行者启动和检查。
- `docs/agent/`：项目状态的共享入口；发现记录与实际结果矛盾时，核实原证据并修正文档。

## 最小文档片段

`docs/agent/MISSION.md`：

```yaml
objective: 判断候选损失函数是否改善低覆盖样本的预测
authorization: 用户授权在本项目已分配资源内自主训练、分析和迭代
constraints:
  - 使用已批准的数据和划分；不得把测试集用于选参
  - 不复制数据到其他站点，不发布结果，不删除原始数据
success: 提交可追溯的比较、适用范围和继续或停止该方向的建议
```

`docs/agent/PLAN.md`：

```yaml
version: 3
direction: 在同一站点和数据支持条件下比较一组新控制与候选方法
comparison:
  site: example-site
  support: dataset-v2 / split-v1 / preprocessing-v4
  shared: architecture-v2 / seed-17 / evaluation-v3
  varies: baseline-loss 与 candidate-loss
tasks:
  - train-fresh-control: completed
  - train-fresh-candidate: completed
  - compare-fresh-pair: ready
next_review: 完成配对比较后决定是否值得扩展种子与样本范围
```

这里的控制和候选训练都是本轮新生成的结果。旧结果可以帮助形成假设，但不能替代这组比较中的控制。相同配置和一个种子提供初步可比性，不能证明普遍收益。

`docs/agent/CURRENT.md`：

```yaml
state: ACTIVE
adopted_plan: 3
active_task: compare-fresh-pair
resources:
  gpu-0: {owner: executor, task: null, state: idle}
  cpu-analysis: {owner: executor, task: compare-fresh-pair, state: reserved}
signals:
  train-fresh-control: completed / results/fresh-control/terminal.json
  train-fresh-candidate: completed / results/fresh-candidate/terminal.json
cost_observed:
  fresh-control_gpu_hours: 4.2
  fresh-candidate_gpu_hours: 4.4
resource_evidence: results/fresh-pair/resource-summary.json
next_action: 执行配对分析，写入比较表和限制说明
```

执行者独占资源分配权，规划者通过计划提出需求。资源表同时记录归属和释放情况；GPU 空闲并不自动产生新的实验需求。

## 一个可以直接接手的任务

任务合同保存到 `docs/agent/tasks/compare-fresh-pair.md`：

```yaml
name: compare-fresh-pair
status: ready
plan_version: 3
purpose: 判断候选损失函数的初步收益及其适用范围
dependencies:
  - fresh-control 和 fresh-candidate 均有成功终止记录
  - 两者的 support、划分及评估版本符合本轮比较合同
acceptance:
  - 对两个完整结果计算同一组预先规定的总体与分层指标
  - 说明单个种子和低覆盖分层样本量对结论的限制
  - 保存比较表、结论和证据索引，并释放分析资源
next_action: 用项目 compare.py 读取两份完整预测，生成配对比较
evidence:
  - results/fresh-control/manifest.json
  - results/fresh-candidate/manifest.json
  - results/fresh-pair/metrics.tsv
  - results/fresh-pair/conclusion.md
```

执行者只评价已完成的结果。运行中的损失曲线可以用于诊断故障，不能提前当作最终方法比较；失败训练也不能混入成功结果的均值。

## 有复用价值的已关闭工作

`docs/agent/HISTORY.md` 的一个虚构条目：

```yaml
task: inspect-old-normalization
status: completed
purpose: 检查旧归一化是否解释低覆盖分层的偏差
result: 在已完成的旧验证结果上重算后，偏差仍在；关闭这个解释方向
limits: 仅检查旧验证集和两种已保存输出，不能排除其他预处理影响
reuse: 后续比较沿用明确的归一化版本；不要重复这次相同重算
evidence:
  - results/normalization-check/summary.md
  - results/normalization-check/metrics.tsv
cost_observed: {cpu_minutes: 18, gpu_hours: 0, output_mb: 3}
```

负结果完成了原定检验，因此有明确用途。详细日志留在证据目录，历史条目保留目的、结果、限制和可复用信息。成本是已发生的观测，不是代理自行设置的实验准入门槛。

## 计划更新与等待

规划者可以根据新文献或完整结果提出版本 4。执行者把待采纳版本写入状态，在当前任务提交结果、释放资源或形成可恢复检查点后采纳。运行中任务继续遵守原合同；若用户要求立即停止，则按明确指令处理并保存可恢复状态。

若后续训练尚在运行，执行者先完成不依赖其结果的必要工作。没有这种工作时记录 `WAITING` 和下一次决定所需信号。优先等待终止事件；平台只有定时唤醒时，依据 ETA 安排一次唤醒。ETA 未知时按首个有意义的进度量安排校准，未到结果则根据实际进展更新 ETA 并退避，避免密集轮询。

调度提示只保存稳定入口，例如：

```text
按 .agent/roles/executor.md 恢复本项目。
读取 docs/agent/MISSION.md、PLAN.md、CURRENT.md，相关 HISTORY 按需读取；
读取 CURRENT 指向的任务合同与证据，处理到期信号和中断恢复。
在任务安全边界采纳规划者依 .agent/roles/planner.md 提交的计划。
执行下一个已授权且依赖满足的任务；有结果后记录历史与资源归属。
若仍只能等待，按事件或当前 ETA 更新同一唤醒安排并结束本轮；
若目标已完成，关闭唤醒。不要把调度提示当作状态或复制进程信息。
```

唤醒频率随信号变化，而非固定工作时长或凭空设定的预算。是否继续实验取决于科学问题、已有证据、用户授权及实际约束；硬件利用率本身不是研究目标。

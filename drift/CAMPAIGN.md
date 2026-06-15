# 战役 · 九章（探索涌现）

> 由 `games/drift/simulation.py` 按节拍触发。Agent 代玩时对齐此顺序，可即兴措辞。

| 章 | 标题 | 关键事件 |
|----|------|----------|
| 1 | 醒来 | 未知节点，门/终端/目标 |
| 2 | 第一次探索 | RULE SET v1，验证 move/interact |
| 3 | 第一件怪事 | 交互代价 energy→memory |
| 4 | 规则不可信 | 测试表：move 稳 / interact 乱 / door 随机 |
| 5 | 被污染的证据 | 日志残片 |
| 6 | 追踪改规则者 | 解锁 B/C/D，目标变更 |
| 7 | 世界反侦查 | 节点 B · 双查询 |
| 8 | 十二次失败 | 节点 C · 三道谜题 |
| 9 | 规则引擎在门外 | 节点 D · 因果悖论 + **三结局之一** |

跑满默认 = **13 节拍**（含 B/C/D 谜题）。详见 [ENDINGS.md](ENDINGS.md)。

---

## 第二章钩子（interface 专属）

> `python run_drift.py --phase all` · 标杆 [samples/chapter02_hook.md](samples/chapter02_hook.md)

| 章 | 标题 | 关键事件 |
|----|------|----------|
| 10 | 接口待答 | `INTERFACE REQUEST PENDING` 挂起 |
| 11 | 第三次改写 | RULE SET v3 · 移动概率化 · attention |
| 12 | 门槛节点 | 解锁 `interface_threshold` · patch queued |
| 13 | 裂隙回响 | 门外词 **MISSING** · 第二章钩子尽 |

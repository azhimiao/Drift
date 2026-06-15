# 第一章结局 · DRIFT

> 由 simulation 根据探索状态运算。Agent 代玩时对齐此逻辑，可即兴措辞。

---

## 三种收束

| ID | 标题 | 触发（simulation） | 玩家看到什么 |
|----|------|-------------------|--------------|
| **interface** | 接口微光 | 节点 B 谜题解开 + C 深度探索 + 记忆≥0.4 | `INTERFACE REQUEST PENDING`，门外有回应 |
| **loop** | 循环重置 | 节点 B 跟错标牌 / 记忆<0.25 | 回到未知节点，再次醒来 |
| **hold** | 门前静帧 | 节点 C 浅探索（`--shallow-c`）或默认兜底 | `Continue exploration.`，知引擎在门外 |

### CLI 测试

```bash
python run_drift.py                      # interface
python run_drift.py --fail-b             # loop · B 失败
python run_drift.py --low-memory         # loop · 记忆崩
python run_drift.py --shallow-c          # hold
python run_drift.py --phase all          # interface + 第二章钩子
```

---

## 节点谜题（第一章）

### 节点 B

1. **sign_match** — 三次看门牌，找重复数字 `7`
2. **route_code** — 路由面板输入 `7` → 稳定通路
3. （章 7）**反侦查查询** — 同一问题两种答案

### 节点 C

1. **read_xii** — 墙漆下露出 XII
2. **open_slot_12** — 档案槽 12 → 十二实例线索
3. **footstep_echo** — 回声晚半拍

### 节点 D

1. **five_step_paradox** — 五步因果悖论
2. **final_query** — 向引擎终端提问
3. **结局运算** — 见上表

---

## Agent 代玩

- 谜题要**演出来**（走、擦、输入、听），不是报 puzzle_id
- 结局由探索质量涌现；CLI 可强制分支测试（见上表）
- 勿发明 seed / events 中没有的线索

---

*路径：`drift/ENDINGS.md`*

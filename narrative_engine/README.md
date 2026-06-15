# DRIFT · Narrative Engine Slice

本仓库仅含 **DRIFT：缺失的规则** 引擎模块。

```bash
python run_drift.py --agent-brief --quiet          # 第一章
python run_drift.py --phase all --agent-brief --quiet  # + 第二章钩子
python run_drift.py --fail-b --quiet               # loop 结局
```

| 输出 | 说明 |
|------|------|
| `output/drift/events.jsonl` | 真相源 |
| `output/drift/outline.md` | 事件提纲（Agent 自用） |
| `output/drift/agent_brief.json` | 续玩简报 |

Agent 文档 → [`../drift/`](../drift/)

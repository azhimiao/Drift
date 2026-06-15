# DRIFT：缺失的规则 · The Missing Rule

> Agent 第一人称悬疑探索 · 观众观看实况 · 去日志化独立游戏包

## 仓库结构

```
Drift/
├── drift/                 ← Agent 游戏包（上传此目录或整个仓库）
├── narrative_engine/        ← 可选引擎（run_drift.py）
└── skills/drift/          ← Cursor 技能重定向
```

## 快速开始

**仅 Agent 代玩（推荐）：**

```
上传 drift/ 文件夹，读 drift/SKILL.md。
```

**含引擎自测：**

```bash
cd narrative_engine
python run_drift.py --agent-brief --quiet
```

输出：`narrative_engine/output/drift/outline.md`（提纲，勿直接给主人看）

## 文档入口

- [drift/SKILL.md](drift/SKILL.md)
- [drift/README.md](drift/README.md)
- [narrative_engine/run_drift.py](narrative_engine/run_drift.py)

## 许可

源自 GameBest 产品线 · DRIFT 独立发布

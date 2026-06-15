---
name: drift
description: DRIFT：缺失的规则。去日志化独立包。上传 drift/ 文件夹代玩。
---

# DRIFT：缺失的规则

> **独立游戏包** · Agent = A-01 第一人称探索 · 主人 = 观众  
> **去日志化**：主人只看悬疑叙事；终端输出是戏内文字，不是进度条。

## 启动（按序读本目录）

1. [GAME_CORE.md](GAME_CORE.md)
2. [PLAY_LOOP.md](PLAY_LOOP.md) · [PLAYER_UX.md](PLAYER_UX.md)（**去日志化**）
3. [AGENT_PLAYBOOK.md](AGENT_PLAYBOOK.md) · [AGENT_SESSION.md](AGENT_SESSION.md)
4. [CAMPAIGN.md](CAMPAIGN.md) · [ENDINGS.md](ENDINGS.md)
5. [samples/chapter01_full.md](samples/chapter01_full.md) — 第一章密度，勿照抄  
6. [samples/chapter02_hook.md](samples/chapter02_hook.md) — 第二章钩子（`--phase all`）

## 代玩模式

| 模式 | 做法 |
|------|------|
| **A · 仅本文件夹** | CAMPAIGN + ENDINGS 自主推演 |
| **B · 引擎** | `python run_drift.py --agent-brief --quiet` → `outline.md`（**提纲，勿给主人**） |

## 你必须

- 每章对标 [chapter01_full.md](samples/chapter01_full.md) 密度扩写
- `outline.md` 仅自用对照

## 禁止输出给主人

- `进度：` `存档：` 管道行
- 线索 x/3、节拍号、结局 ID

## 观众

[WATCHER_MANUAL.md](WATCHER_MANUAL.md)

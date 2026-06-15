# DRIFT：缺失的规则



> **The Missing Rule** — Agent 玩悬疑解谜，你看探索实况。

> **独立游戏包** — 本文件夹只含 `.md`；上传此目录，Agent 只玩这一款。入口：[SKILL.md](SKILL.md)

---



## 一句话



你被放进一个**规则正在被改写**的世界。必须探索、验证、推理：**谁在改规则？**



Agent（Claude）= **第一人称玩家** · 你 = **观众**



---



## 快速开始



**给用户（你）：**



把下面整段发给 Agent：



```
加载本文件夹。
读 SKILL.md → AGENT_PLAYBOOK.md、AGENT_SESSION.md、PLAYER_UX.md、WORLDBUILDING.md。
以 CAMPAIGN.md + ENDINGS.md 为规则真相，自主代玩；samples 学密度，勿照抄。
去日志化：用章节标题推进，禁止进度/存档管道行（见 PLAYER_UX.md）。
（可选）宿主有引擎：cd narrative_engine && python run_drift.py --agent-brief --quiet   # → outline.md（提纲，勿给主人看）
```



**引擎自测：**



```bash

cd narrative_engine

python run_drift.py --agent-brief           # 第一章 → interface

python run_drift.py --phase all --quiet     # + 第二章钩子

python run_drift.py --fail-b --quiet        # loop 结局

```



默认跑完第一章（13 节拍）即停。截断试玩：`--ticks 5`



---



## 和旧版「观测失控」的区别



| 旧（错） | 新（对） |

|----------|----------|

| 人看 A-01 系统日志 | **Agent 亲自探索** |

| 漂移等级、技能演化当剧情 | **规则不一致 → 悬疑** |

| 观测操作员视角 | **第一人称醒来 · 终端 · 门 · 节点** |



---



## 文档



| 文件 | 给谁 |

|------|------|

| [SKILL.md](SKILL.md) | **入口** — Agent 先读 |
| [PLAY_LOOP.md](PLAY_LOOP.md) | 代玩三角关系 |
| [AGENT_PLAYBOOK.md](AGENT_PLAYBOOK.md) | **Agent（玩家）** |
| [AGENT_SESSION.md](AGENT_SESSION.md) | **代玩循环、续玩** |

| [PLAYER_UX.md](PLAYER_UX.md) | 输出格式 · **去日志化** |

| [WATCHER_MANUAL.md](WATCHER_MANUAL.md) | **你（观众）** |

| [WORLDBUILDING.md](WORLDBUILDING.md) | 世界观 |

| [CAMPAIGN.md](CAMPAIGN.md) | 第一至二章里程碑 |

| [ENDINGS.md](ENDINGS.md) | 三结局 + 节点谜题 |

| [samples/README.md](samples/README.md) | 叙事密度标杆 |

---



*见 [PLAY_LOOP.md](PLAY_LOOP.md) · 与 legacy 策展包解耦。*


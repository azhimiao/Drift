#!/usr/bin/env python3
"""Run DRIFT: The Missing Rule — mystery exploration playthrough."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from games.drift.simulation import run_and_narrate


def _build_agent_brief(state: dict, out_dir: Path) -> dict:
    loc = state.get("location", "unknown_node")
    rv = state.get("rule_version", 1)
    ending = state.get("ending_id")
    ch2 = state.get("chapter_two_complete")
    if ch2:
        resume = f"第二章钩子已尽。你停在 {loc}，终端规则像是第 {rv} 版之后的世界。"
        next_step = "主人说「继续」→ 从下一场景/章节接写，勿输出进度/存档行。"
    elif state.get("chapter_one_complete") and ending == "interface":
        resume = f"第一章已至接口（{loc}）。门缝里的 REQUEST 还亮着。"
        next_step = "主人说「继续」→ 第二章钩子，或 --phase all 对照引擎。"
    elif state.get("chapter_one_complete"):
        resume = f"第一章已收束（{loc}）。这一局走向：{ending or 'hold'}。"
        next_step = "主人说「继续」→ 新周目或深挖，勿贴存档行。"
    else:
        ch = max(state.get("chapters_reached", [1]))
        resume = f"故事在第 {ch} 章，{loc}。终端规则大约是 v{rv}。"
        next_step = "主人说「继续」→ 下一探索节拍，用章节标题推进。"

    return {
        "game": state.get("game"),
        "player_role": "A-01 · 第一人称（仅叙事阶段）",
        "audience_role": "主人 · 只看悬疑叙事，不看日志行",
        "truth_source": str(out_dir / "events.jsonl"),
        "narrative_ref": str(out_dir / "outline.md"),
        "outline_ref": str(out_dir / "outline.md"),
        "resume_line": resume,
        "next_step": next_step,
        "delogified": True,
        "startup_reads": [
            "drift/GAME_CORE.md",
            "drift/AGENT_PLAYBOOK.md",
            "drift/AGENT_SESSION.md",
            "drift/PLAYER_UX.md",
            "drift/samples/chapter01_full.md",
            "drift/samples/chapter02_hook.md",
        ],
        "rules": [
            "去日志化：禁止进度/存档管道行",
            "outline.md 仅 Agent 自用，禁止贴给主人",
            "每章对标 chapter01_full 密度扩写",
            "每局重写措辞，禁止照抄 samples",
            "events.jsonl 仅后台，不粘贴给主人",
            "禁止引用 legacy 包",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="DRIFT：缺失的规则")
    parser.add_argument(
        "--ticks",
        type=int,
        default=None,
        help="Max exploration beats (default: full phase)",
    )
    parser.add_argument("--seed", type=int, default=42, help="RNG seed")
    parser.add_argument("--out", type=str, default=None)
    parser.add_argument(
        "--phase",
        choices=["chapter1", "chapter2", "all"],
        default="chapter1",
        help="chapter1=第一章 | chapter2=仅第二章（会先跑完第一章）| all=第一章+第二章钩子",
    )
    parser.add_argument(
        "--fail-b",
        action="store_true",
        help="节点 B 跟错标牌 → loop 结局",
    )
    parser.add_argument(
        "--low-memory",
        action="store_true",
        help="起始记忆过低 → loop 结局",
    )
    parser.add_argument(
        "--shallow-c",
        action="store_true",
        help="节点 C 浅探索 → hold 结局",
    )
    parser.add_argument(
        "--agent-brief",
        action="store_true",
        help="额外写出 agent_brief.json 供 Agent 续玩",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="不打印 narrative 正文",
    )
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    out_dir = Path(args.out) if args.out else base / "output" / "drift"
    out_dir.mkdir(parents=True, exist_ok=True)

    result, narrative = run_and_narrate(
        ticks=args.ticks,
        seed=args.seed,
        fail_b=args.fail_b,
        low_memory=args.low_memory,
        shallow_c=args.shallow_c,
        phase=args.phase,
    )

    events_path = out_dir / "events.jsonl"
    with events_path.open("w", encoding="utf-8") as f:
        for event in result.events:
            f.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")

    (out_dir / "outline.md").write_text(narrative, encoding="utf-8")

    world = result.world
    player = result.player
    state = {
        "game": "DRIFT：缺失的规则",
        "subtitle": "The Missing Rule",
        "tick": world.tick if world else 0,
        "phase": args.phase,
        "chapter_one_complete": world.chapter_one_complete if world else False,
        "chapter_two_complete": world.chapter_two_complete if world else False,
        "location": world.location if world else "unknown_node",
        "objective": world.objective if world else "",
        "rule_version": world.rules.version if world else 1,
        "interact_cost": world.rules.interact_cost if world else "energy",
        "movement": world.rules.movement if world else "deterministic",
        "memory": round(world.memory, 2) if world else 1.0,
        "clues_found": world.clues_found if world else [],
        "chapters_reached": sorted(world.chapters) if world else [],
        "locations_unlocked": sorted(world.locations_unlocked) if world else [],
        "player": player.name if player else "A-01",
        "puzzles_solved": world.puzzles_solved if world else [],
        "ending_id": world.ending_id if world else None,
        "node_b_failed": world.node_b_failed if world else False,
        "recent_thoughts": player.thoughts[-3:] if player else [],
    }
    (out_dir / "state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if args.agent_brief:
        brief = _build_agent_brief(state, out_dir)
        (out_dir / "agent_brief.json").write_text(
            json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    ticks_label = args.ticks if args.ticks is not None else "full"
    print(
        f"DRIFT: The Missing Rule | phase={args.phase} | ticks={ticks_label} | "
        f"ch1={state['chapter_one_complete']} | ch2={state['chapter_two_complete']} | "
        f"ending={state['ending_id']}"
    )
    print(f"Chapters: {state['chapters_reached']}")
    print(f"Output: {out_dir}")
    if not args.quiet:
        print(narrative)


if __name__ == "__main__":
    main()

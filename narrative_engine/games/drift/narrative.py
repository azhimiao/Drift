"""DRIFT narrative — delogified suspense prose for the master."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from core.types import Event, EventKind

if TYPE_CHECKING:
    from .simulation import GameWorld, PlayerState


# Agent 扩写密度标杆（提纲内提示，勿贴给主人）
_DRIFT_SAMPLE_REF: dict[int, str] = {
    1: "drift/samples/chapter01_full.md",
    2: "drift/samples/chapter01_full.md",
    3: "drift/samples/chapter01_full.md",
    4: "drift/samples/chapter01_full.md",
    5: "drift/samples/chapter01_full.md",
    6: "drift/samples/chapter01_full.md",
    7: "drift/samples/chapter01_full.md",
    8: "drift/samples/chapter01_full.md",
    9: "drift/samples/chapter01_full.md",
    10: "drift/samples/chapter02_hook.md",
    11: "drift/samples/chapter02_hook.md",
    12: "drift/samples/chapter02_hook.md",
    13: "drift/samples/chapter02_hook.md",
}


def extract_drift_narrative(
    events: list[Event],
    world: GameWorld | None = None,
    player: PlayerState | None = None,
) -> str:
    by_tick: dict[int, list[Event]] = defaultdict(list)
    for e in events:
        by_tick[e.tick].append(e)

    lines: list[str] = [
        "# DRIFT：缺失的规则",
        "",
        "> **事件提纲**（仅供 Agent 对照 `events.jsonl` 扩写，**勿直接给主人看**）",
        "",
    ]

    for tick in sorted(by_tick):
        chunk = by_tick[tick]
        for event in chunk:
            if event.kind == EventKind.CHAPTER:
                ch = event.payload["chapter"]
                lines.append(f"## 第{ch}章 · {event.payload['title']}")
                ref = _DRIFT_SAMPLE_REF.get(ch)
                if ref:
                    lines.append(f"> 扩写参照：`{ref}`")
                lines.append("")
                continue
            block = _render(event)
            if block:
                lines.append(block)
                lines.append("")

    if world and (world.chapter_one_complete or world.chapter_two_complete):
        lines.append("---")
        lines.append("")
        if world.chapter_two_complete:
            lines.append("*（第二章钩子已尽。主人说「继续」可接第三章或新周目。）*")
        elif world.chapter_one_complete and world.ending_id == "interface":
            lines.append("*（第一章已至接口。主人说「继续」可进入第二章钩子。）*")
        else:
            lines.append("*（第一章已收束。）*")
    return "\n".join(lines).rstrip() + "\n"


def _render(event: Event) -> str:
    p = event.payload
    k = event.kind

    if k == EventKind.EXPLORE:
        action = p.get("action")
        if action == "wake":
            return (
                f"我睁开眼。{p.get('scene')}\n\n"
                f"目标只有一个：{p.get('objective')}"
            )
        if action == "approach":
            return "我走向终端。屏幕仍暗着，边缘有细小的电流声。"
        if action == "interact" and p.get("output"):
            return f"我触发终端。屏幕亮起：\n\n`{p.get('output')}`"
        if action == "interact" and p.get("error"):
            return "我再次交互。终端报错——输出和刚才对不上。"
        if action == "interact" and p.get("cost"):
            return f"交互成功。余量变薄了——{p.get('remaining_energy')}。"
        if action == "move" and p.get("note"):
            return "我移动。路径和预期一致。"
        if action == "move":
            return "我移动。路径和预期一致。" if p.get("success") else "我移动。脚下有什么不对。"
        if action == "test":
            return (
                f"我重复测试「{p.get('target')}」{p.get('runs')} 次——"
                f"结果：{p.get('result')}。"
            )
        if action == "interact" and p.get("target") == "door":
            return f"我推门。三次里状态分别是：{', '.join(p.get('states', []))}。"
        if action == "search":
            return f"我在终端底层翻找。找到一段{p.get('detail')}。"
        if action == "enter":
            return f"我进入{p.get('location_name')}。{p.get('scene', p.get('tag', ''))}"
        if action == "query":
            return (
                f"我向终端查询同一对象两次。\n"
                f"第一次：{p.get('run1')}\n"
                f"第二次：{p.get('run2')}"
            )
        if action == "puzzle":
            return _render_puzzle(p)
        if action == "wait":
            return f"我守在终端前。{p.get('detail')}。"
        if action == "listen":
            return f"我贴近裂隙倾听。{p.get('detail')}。"
        if action == "move" and p.get("location"):
            return f"我在 {p.get('location')} 继续摸索。"
        return ""

    if k == EventKind.AGENT_THOUGHT:
        return f"*{p.get('text')}*"

    if k == EventKind.RULE_SHIFT:
        if p.get("discovered_by") == "world_reset":
            return "**世界重置。** 节点 D 的刻度消失，我又回到未知节点。"
        if p.get("discovered_by") == "engine_patch":
            return (
                f"**规则又变了。** 移动不再确定，交互代价变成「{p.get('to')}」。"
                f" 门外的东西在动手。"
            )
        return (
            f"**规则变了。** 交互代价从「{p.get('from')}」变成「{p.get('to')}」。"
            f" 不是我眼花。"
        )

    if k == EventKind.CLUE_FOUND:
        return f"我记下：`{p.get('text')}`"

    if k == EventKind.LOCATION_UNLOCK:
        return f"通路打开——{', '.join(p.get('nodes', []))}。"

    if k == EventKind.WORLD_ADAPT:
        return f"{p.get('effect')}。"

    if k == EventKind.SYSTEM_NOTICE:
        return f"〔终端〕{p.get('text')}"

    if k in (EventKind.PHASE_END, EventKind.ENDING):
        return ""

    return ""


def _render_puzzle(p: dict) -> str:
    pid = p.get("puzzle_id", "")
    if pid == "sign_match":
        attempts = " → ".join(p.get("attempts", []))
        if p.get("success") is False:
            return (
                f"我三次核对门牌：{attempts}。我选了 **{p.get('picked')}**——错了。"
                f"重复的是 **{p.get('correct')}**。"
            )
        return f"我三次核对门牌：{attempts}。重复的是 **7**。"
    if pid == "route_code":
        if p.get("success") is False:
            return f"我在路由面板输入 {p.get('input')}。屏幕显示：`{p.get('output')}`"
        return f"我在路由面板输入 {p.get('input')}。屏幕显示：`{p.get('output')}`"
    if pid == "read_xii":
        return f"我擦开墙漆。底下是 **XII**。"
    if pid == "open_slot_12":
        return "我打开编号 12 的档案槽。里面不是纸，是一段冰冷的重放。"
    if pid == "footstep_echo":
        return f"我停步倾听。{p.get('detail')}。"
    if pid == "five_step_paradox":
        return (
            f"我沿刻度走 {p.get('steps')} 步。"
            f"{p.get('paradox')}。"
        )
    if pid == "final_query":
        return "我向坑底终端提出最后一个问题：「谁在改规则？」"
    return f"我解谜：{pid}。"

"""Layer 3 — Narrative extractor: event log → readable story."""

from __future__ import annotations

from collections import defaultdict

from .types import Event, EventKind


def extract_narrative(events: list[Event], title: str = "漂移纪事") -> str:
    by_tick: dict[int, list[Event]] = defaultdict(list)
    for e in events:
        by_tick[e.tick].append(e)

    lines: list[str] = [
        f"# {title}",
        "",
        "> 自治剧情引擎蒸馏。无预设剧本；下文仅来自 simulation 事件。",
        "",
    ]

    for tick in sorted(by_tick):
        chunk = by_tick[tick]
        lines.append(f"## 节拍 {tick}")
        lines.append("")

        for event in chunk:
            lines.append(_render_event(event))
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(_closing(events))
    return "\n".join(lines)


def _render_event(event: Event) -> str:
    p = event.payload
    k = event.kind

    if k == EventKind.WORLD_DRIFT:
        return f"世界在漂移。{p.get('summary', '')}"

    if k == EventKind.CONFLICT_SPAWN:
        names = p.get("faction_names") or p.get("factions", [])
        return (
            f"**冲突升起**（{p.get('conflict_type')}）：{p.get('summary')}。"
            f"涉及：{'、'.join(names)}。"
        )

    if k == EventKind.CRISIS:
        if p.get("resolved"):
            return f"危机「{p.get('crisis')}」暂退，余波仍在。"
        return f"危机「{p.get('crisis')}」渗入世界，叙事压力上扬。"

    if k == EventKind.AGENT_ACTION:
        outcome = "成了" if p.get("success") else "砸了"
        return f"{p.get('agent')}以「{p.get('skill')}」{p.get('action')}，{outcome}。"

    if k == EventKind.SKILL_EVOLVE:
        reason = "失败逼出了新写法" if p.get("reason") == "failure_mutation" else "熟练让技能收紧"
        return (
            f"{p.get('agent')}的技能从 {p.get('from_skill')} 变为 {p.get('to_skill')}——{reason}。"
        )

    if k == EventKind.TRUST_SHIFT:
        a = p.get("from_faction_name") or p.get("from_faction")
        b = p.get("to_faction_name") or p.get("to_faction")
        return f"{a}与{b}之间的信任滑落（{p.get('reason')}）。"

    if k == EventKind.MEMORY_FADE:
        return (
            f"共同记忆又被削去一角（指数 {p.get('memory_index', 0):.2f}）。"
            f"{p.get('agent')}动用了 {p.get('skill')}。"
        )

    if k == EventKind.WORLD_REACT:
        return (
            f"{p.get('faction')}资源 {p.get('resources')}，"
            f"内部压力 {p.get('pressure')}；"
            f"叙事张力 {p.get('narrative_pressure')}。"
        )

    return f"[{k.value}] {p}"


def _closing(events: list[Event]) -> str:
    evolves = [e for e in events if e.kind == EventKind.SKILL_EVOLVE]
    conflicts = [e for e in events if e.kind == EventKind.CONFLICT_SPAWN]
    if evolves:
        last = evolves[-1].payload
        return (
            f"这一段时间里，世界自发升起 {len(conflicts)} 次冲突，"
            f"技能演化 {len(evolves)} 次。"
            f"末尾一次变异：{last.get('agent')}的 {last.get('to_skill')}。"
            f"故事尚未写完——只是被观察到了这里。"
        )
    return "世界仍在运转，叙事尚未凝结成结局。"

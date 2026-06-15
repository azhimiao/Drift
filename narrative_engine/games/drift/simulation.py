"""DRIFT: The Missing Rule — first-person mystery exploration simulation.

Agent (Claude) = player exploring the world.
User = watches playthrough distilled from events.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path

from core.types import Event, EventKind
from .narrative import extract_drift_narrative


@dataclass
class RuleState:
    version: int = 1
    movement: str = "deterministic"
    interact_cost: str = "energy"
    door_behavior: str = "locked"
    text: str = "movement is deterministic · interaction consumes energy"


@dataclass
class GameWorld:
    tick: int = 0
    seed_id: str = "drift_missing_rule"
    location: str = "unknown_node"
    locations_unlocked: set[str] = field(default_factory=lambda: {"unknown_node"})
    rules: RuleState = field(default_factory=RuleState)
    energy: float = 1.0
    memory: float = 1.0
    interact_count: int = 0
    move_count: int = 0
    test_move_stable: int = 0
    test_interact_failures: int = 0
    clues_found: list[str] = field(default_factory=list)
    chapters: set[int] = field(default_factory=set)
    fired: set[str] = field(default_factory=set)
    chapter_one_complete: bool = False
    chapter_two_complete: bool = False
    ending_id: str | None = None
    node_b_solved: bool = False
    node_b_failed: bool = False
    node_c_deep: bool = False
    force_fail_b: bool = False
    shallow_c: bool = False
    puzzles_solved: list[str] = field(default_factory=list)
    objective: str = "弄清这里的规则。"


@dataclass
class PlayerState:
    """A-01 — the identity Agent (Claude) plays in first person."""
    id: str = "a01"
    name: str = "A-01"
    thoughts: list[str] = field(default_factory=list)


@dataclass
class DriftResult:
    events: list[Event] = field(default_factory=list)
    world: GameWorld | None = None
    player: PlayerState | None = None
    seed: dict = field(default_factory=dict)


def _seed_path() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "seeds" / "drift_missing_rule.json"


def load_drift_seed() -> dict:
    return json.loads(_seed_path().read_text(encoding="utf-8"))


def _emit(tick: int, kind: EventKind, payload: dict) -> Event:
    return Event(tick=tick, kind=kind, payload=payload)


def _chapter(tick: int, world: GameWorld, ch: int, title: str) -> Event:
    world.chapters.add(ch)
    return _emit(tick, EventKind.CHAPTER, {"chapter": ch, "title": title})


def _think(tick: int, player: PlayerState, line: str) -> Event:
    player.thoughts.append(line)
    return _emit(tick, EventKind.AGENT_THOUGHT, {"text": line})


def run_drift_simulation(
    ticks: int | None = None,
    seed: int | None = None,
    *,
    fail_b: bool = False,
    low_memory: bool = False,
    shallow_c: bool = False,
    phase: str = "chapter1",
) -> DriftResult:
    rng = random.Random(seed)
    game_seed = load_drift_seed()
    world = GameWorld()
    if fail_b:
        world.force_fail_b = True
    if low_memory:
        world.memory = 0.2
    if shallow_c:
        world.shallow_c = True
    player = PlayerState()
    events: list[Event] = []

    # Chapter 1 — 醒来
    events.append(_chapter(0, world, 1, "醒来"))
    events.append(
        _emit(
            0,
            EventKind.EXPLORE,
            {
                "action": "wake",
                "location": "unknown_node",
                "location_name": "未知节点",
                "scene": "灰。没有参照的灰。门紧锁，终端未亮，远处有低频噪点，像信号在呼吸。",
                "objective": world.objective,
            },
        )
    )
    events.append(_think(0, player, "我在哪里？先弄清这里的规则。"))

    beat_plan: list[tuple[str, list]] = []
    if phase == "chapter1":
        beat_plan.append(("chapter1", _chapter_one_beats()))
    else:
        beat_plan.append(("chapter1", _chapter_one_beats()))
        beat_plan.append(("chapter2", _chapter_two_beats()))

    default_limit = sum(len(beats) for _, beats in beat_plan)
    limit = ticks if ticks is not None else default_limit
    t = 1
    for phase_name, beats in beat_plan:
        for step in beats:
            if t > limit:
                break
            world.tick = t
            events.extend(step(world, player, game_seed, rng, t))
            if phase_name == "chapter1" and world.chapter_one_complete:
                if phase == "chapter1":
                    break
                if phase == "all" and world.ending_id != "interface":
                    break
            if phase_name == "chapter2" and world.chapter_two_complete:
                break
            t += 1
        else:
            continue
        break

    return DriftResult(events=events, world=world, player=player, seed=game_seed)


def _build_script(_ticks: int) -> list:
    """Deprecated — use _chapter_one_beats()."""
    return _chapter_one_beats()


def _step_terminal_first(w, p, seed, rng, t) -> list[Event]:
    if "first_explore" in w.fired:
        return []
    w.fired.add("first_explore")
    ev = [
        _chapter(t, w, 2, "第一次探索"),
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "approach",
                "target": "terminal",
                "location": w.location,
            },
        ),
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "interact",
                "target": "terminal",
                "success": True,
                "output": f"RULE SET v{w.rules.version}: {w.rules.text}",
            },
        ),
        _think(t, p, "规则写得很清楚。可以验证。"),
    ]
    return ev


def _step_verify_rules(w, p, seed, rng, t) -> list[Event]:
    if "verified" in w.fired:
        return []
    w.fired.add("verified")
    w.move_count += 1
    w.interact_count += 1
    w.energy -= 0.1
    return [
        _emit(t, EventKind.EXPLORE, {"action": "move", "success": True, "note": "路径可预期"}),
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "interact",
                "target": "terminal",
                "success": True,
                "cost": "energy",
                "remaining_energy": round(w.energy, 2),
            },
        ),
        _think(t, p, "移动稳定。交互也成立。这个世界暂时可信。"),
    ]


def _step_anomaly(w, p, seed, rng, t) -> list[Event]:
    if "anomaly" in w.fired:
        return []
    w.fired.add("anomaly")
    w.rules.version = 2
    w.rules.interact_cost = "memory"
    w.rules.text = "movement is deterministic · interaction consumes memory"
    w.interact_count += 1
    w.memory -= 0.15
    return [
        _chapter(t, w, 3, "第一件怪事"),
        _emit(
            t,
            EventKind.EXPLORE,
            {"action": "interact", "target": "terminal", "success": False, "error": True},
        ),
        _emit(
            t,
            EventKind.RULE_SHIFT,
            {
                "from": "interaction consumes energy",
                "to": "interaction consumes memory",
                "rule_version": w.rules.version,
                "discovered_by": "player",
            },
        ),
        _think(t, p, "不对。和刚才不一致。这不是我记错了。"),
    ]


def _step_test_world(w, p, seed, rng, t) -> list[Event]:
    if "tested" in w.fired:
        return []
    w.fired.add("tested")
    w.test_move_stable = 3
    w.test_interact_failures = 2
    w.rules.door_behavior = "random"
    return [
        _chapter(t, w, 4, "规则不可信"),
        _emit(t, EventKind.EXPLORE, {"action": "test", "target": "move", "result": "stable", "runs": 3}),
        _emit(
            t,
            EventKind.EXPLORE,
            {"action": "test", "target": "interact", "result": "unstable", "runs": 2},
        ),
        _emit(
            t,
            EventKind.EXPLORE,
            {"action": "interact", "target": "door", "result": "random", "states": ["locked", "ajar", "locked"]},
        ),
        _think(t, p, "规则不是固定的。有人在改写它们。"),
    ]


def _step_find_fragment(w, p, seed, rng, t) -> list[Event]:
    if "fragment" in w.fired:
        return []
    w.fired.add("fragment")
    clue = seed["clues"]["log_fragment"]
    w.clues_found.append("log_fragment")
    return [
        _chapter(t, w, 5, "被污染的证据"),
        _emit(
            t,
            EventKind.EXPLORE,
            {"action": "search", "target": "terminal", "detail": "底层日志残片"},
        ),
        _emit(t, EventKind.CLUE_FOUND, {"id": "log_fragment", "text": clue}),
        _think(t, p, "别信屏幕上现行的规则——这句话像是故意留下的。"),
    ]


def _step_unlock_nodes(w, p, seed, rng, t) -> list[Event]:
    if "hunt" in w.fired:
        return []
    w.fired.add("hunt")
    w.locations_unlocked.update({"node_b", "node_c", "node_d"})
    w.objective = "找到改规则的东西"
    return [
        _chapter(t, w, 6, "追踪改规则者"),
        _emit(t, EventKind.LOCATION_UNLOCK, {"nodes": ["node_b", "node_c", "node_d"]}),
        _think(t, p, "目标变了：不是理解规则，是找到改规则的东西。"),
    ]


def _resolve_ending(w: GameWorld) -> str:
    if w.node_b_failed or w.memory < 0.25:
        return "loop"
    if w.node_b_solved and w.node_c_deep and w.memory >= 0.4:
        return "interface"
    return "hold"


def _step_node_b_enter(w, p, seed, rng, t) -> list[Event]:
    if "b_enter" in w.fired:
        return []
    w.fired.add("b_enter")
    w.location = "node_b"
    return [
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "enter",
                "location": "node_b",
                "location_name": "节点 B",
                "scene": "走廊两侧的标识在刷新。同一扇门，两次看见不同的编号。",
            },
        ),
        _think(t, p, "这里连「走错路」的定义都不稳定。"),
    ]


def _step_node_b_sign_puzzle(w, p, seed, rng, t) -> list[Event]:
    if "b_sign" in w.fired:
        return []
    w.fired.add("b_sign")
    if w.force_fail_b:
        w.node_b_failed = True
        w.puzzles_solved.append("sign_match_failed")
        return [
            _emit(
                t,
                EventKind.EXPLORE,
                {
                    "action": "puzzle",
                    "puzzle_id": "sign_match",
                    "location": "node_b",
                    "target": "mirror_door",
                    "attempts": [
                        "第一次看见：12",
                        "第二次看见：7",
                        "第三次看见：12",
                    ],
                    "success": False,
                    "picked": "12",
                    "correct": "7",
                },
            ),
            _think(t, p, "我选了 12。路由闪了一下就死了——重复的不是它。"),
            _emit(
                t,
                EventKind.EXPLORE,
                {
                    "action": "puzzle",
                    "puzzle_id": "route_code",
                    "target": "routing_panel",
                    "input": "12",
                    "success": False,
                    "output": "PATH UNSTABLE · reroute denied",
                },
            ),
        ]
    # 第三次核对：只有「7」重复出现
    w.node_b_solved = True
    w.puzzles_solved.append("sign_match")
    return [
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "puzzle",
                "puzzle_id": "sign_match",
                "location": "node_b",
                "target": "mirror_door",
                "attempts": [
                    "第一次看见：12",
                    "第二次看见：7",
                    "第三次看见：7",
                ],
                "success": True,
                "reward": "routing_panel 解锁",
            },
        ),
        _think(t, p, "不是记住数字，是找「还会重复」的那一个。"),
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "puzzle",
                "puzzle_id": "route_code",
                "target": "routing_panel",
                "input": "7",
                "success": True,
                "output": "PATH → node_c (stable for 30s)",
            },
        ),
    ]


def _step_counter_survey(w, p, seed, rng, t) -> list[Event]:
    if "counter" in w.fired:
        return []
    w.fired.add("counter")
    return [
        _chapter(t, w, 7, "世界反侦查"),
        _emit(
            t,
            EventKind.WORLD_ADAPT,
            {
                "action": "同一条查询，两次返回不同观测结果",
                "effect": "世界在躲避被理解",
            },
        ),
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "query",
                "target": "terminal",
                "run1": "door: locked",
                "run2": "door: not present",
            },
        ),
        _think(t, p, "它不是乱了——像在躲我的问题。"),
    ]


def _step_node_c_enter(w, p, seed, rng, t) -> list[Event]:
    if "c_enter" in w.fired:
        return []
    w.fired.add("c_enter")
    w.location = "node_c"
    return [
        _chapter(t, w, 8, "十二次失败"),
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "enter",
                "location": "node_c",
                "location_name": "节点 C",
                "scene": "墙上有被擦掉的划痕。空气像塞满了旧记录。",
            },
        ),
    ]


def _step_node_c_puzzles(w, p, seed, rng, t) -> list[Event]:
    if "c_puzzles" in w.fired:
        return []
    w.fired.add("c_puzzles")
    if w.shallow_c:
        return [
            _emit(
                t,
                EventKind.EXPLORE,
                {
                    "action": "search",
                    "target": "scratch_wall",
                    "detail": "浅划痕，未及 XII",
                },
            ),
            _think(t, p, "这里有别人来过的痕迹。我没敢挖深。"),
        ]
    w.node_c_deep = True
    w.puzzles_solved.extend(["read_xii", "open_slot_12"])
    clue = seed["clues"]["instance_log"]
    w.clues_found.append("instance_log")
    w.memory -= 0.08
    return [
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "puzzle",
                "puzzle_id": "read_xii",
                "target": "scratch_wall",
                "detail": "擦掉漆底下露出 XII",
                "success": True,
            },
        ),
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "puzzle",
                "puzzle_id": "open_slot_12",
                "target": "archive_slot_12",
                "success": True,
            },
        ),
        _emit(t, EventKind.CLUE_FOUND, {"id": "instance_log", "text": clue}),
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "puzzle",
                "puzzle_id": "footstep_echo",
                "target": "footstep_echo",
                "detail": "回声比脚步晚半拍，像多一个人在走",
                "success": True,
            },
        ),
        _think(t, p, "十二——不是巧合。我不是第一个走到这里的人。"),
    ]


def _step_node_d_causality(w, p, seed, rng, t) -> list[Event]:
    if "d_causality" in w.fired:
        return []
    w.fired.add("d_causality")
    w.location = "node_d"
    return [
        _chapter(t, w, 9, "规则引擎在门外"),
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "enter",
                "location": "node_d",
                "location_name": "节点 D",
                "scene": "因果像被挖空的坑。地面有刻度，终端在坑底。",
            },
        ),
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "puzzle",
                "puzzle_id": "five_step_paradox",
                "target": "causality_floor",
                "steps": 5,
                "paradox": "第1步落点无法被第5步回看确认",
                "success": True,
            },
        ),
        _think(t, p, "这里不是乱，是故意挖空「因果」。"),
    ]


def _step_node_d_ending(w, p, seed, rng, t) -> list[Event]:
    if "d_end" in w.fired:
        return []
    w.fired.add("d_end")
    clue = seed["clues"]["engine_hint"]
    w.clues_found.append("engine_hint")
    ending = _resolve_ending(w)
    w.ending_id = ending
    w.chapter_one_complete = True

    endings_meta = seed.get("endings", {})
    title = endings_meta.get(ending, {}).get("title", ending)

    ev: list[Event] = [
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "puzzle",
                "puzzle_id": "final_query",
                "target": "engine_terminal",
                "success": True,
            },
        ),
        _emit(t, EventKind.CLUE_FOUND, {"id": "engine_hint", "text": clue}),
    ]

    if ending == "interface":
        ev.extend([
            _emit(
                t,
                EventKind.SYSTEM_NOTICE,
                {"text": "INTERFACE REQUEST PENDING · source acknowledged"},
            ),
            _think(t, p, "门外有回应。不是答案，是「被听见」。"),
        ])
    elif ending == "loop":
        w.location = "unknown_node"
        w.memory = max(0.1, w.memory - 0.2)
        ev.extend([
            _emit(
                t,
                EventKind.RULE_SHIFT,
                {
                    "from": "node_d",
                    "to": "unknown_node",
                    "rule_version": w.rules.version,
                    "discovered_by": "world_reset",
                },
            ),
            _think(t, p, "灰。门。终端。我又醒了一次——规则却记得我。"),
        ])
    else:
        ev.extend([
            _emit(
                t,
                EventKind.SYSTEM_NOTICE,
                {"text": "Continue exploration.", "phase": "chapter_1_end"},
            ),
            _think(t, p, "引擎在门外。门还没开。但至少我知道它在。"),
        ])

    ev.append(
        _emit(
            t,
            EventKind.ENDING,
            {"ending_id": ending, "title": title, "chapter": 1},
        )
    )
    ev.append(
        _emit(
            t,
            EventKind.PHASE_END,
            {
                "phase": "chapter_1",
                "title": title,
                "ending": ending,
            },
        )
    )
    return ev


def _step_twelve_instances(w, p, seed, rng, t) -> list[Event]:
    """Deprecated — merged into node C puzzles."""
    return _step_node_c_puzzles(w, p, seed, rng, t)


def _step_engine_hint(w, p, seed, rng, t) -> list[Event]:
    """Deprecated — merged into node D ending."""
    return _step_node_d_ending(w, p, seed, rng, t)


def _chapter_one_beats() -> list:
    """第一章固定节拍。跑完即停。"""
    return [
        _step_terminal_first,
        _step_verify_rules,
        _step_anomaly,
        _step_test_world,
        _step_find_fragment,
        _step_unlock_nodes,
        _step_node_b_enter,
        _step_node_b_sign_puzzle,
        _step_counter_survey,
        _step_node_c_enter,
        _step_node_c_puzzles,
        _step_node_d_causality,
        _step_node_d_ending,
    ]


def _step_interface_wait(w, p, seed, rng, t) -> list[Event]:
    if "ch2_wait" in w.fired:
        return []
    w.fired.add("ch2_wait")
    w.location = "unknown_node"
    return [
        _chapter(t, w, 10, "接口待答"),
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "wait",
                "target": "terminal",
                "detail": "INTERFACE REQUEST PENDING · 计时未归零",
            },
        ),
        _think(t, p, "门外有人听见了。但回应还没来。"),
    ]


def _step_rule_v3(w, p, seed, rng, t) -> list[Event]:
    if "ch2_v3" in w.fired:
        return []
    w.fired.add("ch2_v3")
    w.rules.version = 3
    w.rules.movement = "probabilistic"
    w.rules.interact_cost = "attention"
    w.rules.text = "movement is probabilistic · interaction consumes attention"
    return [
        _chapter(t, w, 11, "第三次改写"),
        _emit(
            t,
            EventKind.RULE_SHIFT,
            {
                "from": "interaction consumes memory",
                "to": "interaction consumes attention",
                "rule_version": w.rules.version,
                "discovered_by": "engine_patch",
            },
        ),
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "test",
                "target": "move",
                "result": "unstable",
                "runs": 3,
            },
        ),
        _think(t, p, "移动也开始骗了。门外的那个东西在改第二遍规则。"),
    ]


def _step_threshold_unlock(w, p, seed, rng, t) -> list[Event]:
    if "ch2_threshold" in w.fired:
        return []
    w.fired.add("ch2_threshold")
    w.locations_unlocked.add("interface_threshold")
    w.location = "interface_threshold"
    clue = seed["clues"].get(
        "patch_queued",
        "RULE PATCH QUEUED · observer channel open",
    )
    w.clues_found.append("patch_queued")
    return [
        _chapter(t, w, 12, "门槛节点"),
        _emit(
            t,
            EventKind.LOCATION_UNLOCK,
            {"nodes": ["interface_threshold"]},
        ),
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "enter",
                "location": "interface_threshold",
                "location_name": "接口门槛",
                "scene": "不是门，是规则表面的一道裂隙。终端嵌在缝里。",
            },
        ),
        _emit(
            t,
            EventKind.SYSTEM_NOTICE,
            {"text": "RULE PATCH QUEUED · observer channel open"},
        ),
        _emit(t, EventKind.CLUE_FOUND, {"id": "patch_queued", "text": clue}),
        _think(t, p, "观测通道开了条缝。不是门——是规则本身裂了一道口。"),
    ]


def _step_chapter_two_end(w, p, seed, rng, t) -> list[Event]:
    if "ch2_end" in w.fired:
        return []
    w.fired.add("ch2_end")
    w.chapter_two_complete = True
    w.objective = "在通道关闭前解读规则补丁"
    echo = seed["clues"].get("missing_echo", "MISSING")
    w.clues_found.append("missing_echo")
    return [
        _chapter(t, w, 13, "裂隙回响"),
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "listen",
                "target": "interface_threshold",
                "detail": f"门外传来可被理解的第一个词：{echo}",
                "echo": echo,
            },
        ),
        _emit(t, EventKind.CLUE_FOUND, {"id": "missing_echo", "text": echo}),
        _think(t, p, "缺失的……规则？还是缺失的观测者？"),
        _emit(
            t,
            EventKind.PHASE_END,
            {
                "phase": "chapter_2",
                "title": "缺失的规则 · 第二章（未完）",
                "hook": echo,
            },
        ),
    ]


def _chapter_two_beats() -> list:
    """第二章钩子。仅 interface 结局后衔接。"""
    return [
        _step_interface_wait,
        _step_rule_v3,
        _step_threshold_unlock,
        _step_chapter_two_end,
    ]


def run_and_narrate(
    ticks: int | None = None,
    seed: int | None = None,
    *,
    fail_b: bool = False,
    low_memory: bool = False,
    shallow_c: bool = False,
    phase: str = "chapter1",
) -> tuple[DriftResult, str]:
    result = run_drift_simulation(
        ticks=ticks,
        seed=seed,
        fail_b=fail_b,
        low_memory=low_memory,
        shallow_c=shallow_c,
        phase=phase,
    )
    prose = extract_drift_narrative(result.events, result.world, result.player)
    return result, prose

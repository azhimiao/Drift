"""Layer 2 — Autonomous agents."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from .seed import WorldSeed, bootstrap_agents
from .skill import choose_skill, evolve_skill
from .types import AgentState, Event, EventKind, Skill

if TYPE_CHECKING:
    from .world import WorldState


class Agent:
    def __init__(self, state: AgentState, seed: WorldSeed) -> None:
        self.state = state
        self.seed = seed

    def step(self, world: WorldState, rng: random.Random) -> tuple[list[Event], Skill, bool]:
        events: list[Event] = []
        tick = world.tick
        skill = choose_skill(self.state, world, self.seed, rng)
        base = skill.id.split("_")[0]
        verbs = self.seed.skill_verbs.get(base, ["行动", "尝试"])
        action_desc = rng.choice(verbs)

        difficulty = 0.45 + world.veil_density * 0.2 + (1.0 - skill.potency) * 0.15
        if world.active_crises:
            difficulty += 0.1
        success = rng.random() > difficulty

        self.state.last_action = action_desc
        snippet = f"{self.state.name}以「{skill.key}」{action_desc}——{'成功' if success else '失败'}"
        self.state.memory.append(snippet)
        if len(self.state.memory) > 12:
            self.state.memory = self.state.memory[-12:]

        self.state.stress = max(0.0, min(1.0, self.state.stress + (0.05 if not success else -0.02)))

        events.append(
            Event(
                tick=tick,
                kind=EventKind.AGENT_ACTION,
                payload={
                    "agent": self.state.name,
                    "agent_id": self.state.id,
                    "faction": self.state.faction_id,
                    "skill": skill.key,
                    "action": action_desc,
                    "success": success,
                    "difficulty": round(difficulty, 3),
                },
            )
        )

        evolved = evolve_skill(skill, success, rng)
        if evolved.key != skill.key:
            self._replace_skill(skill, evolved)
            events.append(
                Event(
                    tick=tick,
                    kind=EventKind.SKILL_EVOLVE,
                    payload={
                        "agent": self.state.name,
                        "from_skill": skill.key,
                        "to_skill": evolved.key,
                        "reason": "reinforcement" if success else "failure_mutation",
                    },
                )
            )

        return events, skill, success

    def _replace_skill(self, old: Skill, new: Skill) -> None:
        skills = []
        for s in self.state.skills:
            skills.append(new if s.id == old.id and s.version == old.version else s)
        self.state.skills = skills


def create_agents_from_seed(seed: WorldSeed, rng: random.Random) -> list[Agent]:
    return [Agent(state, seed) for state in bootstrap_agents(seed, rng)]

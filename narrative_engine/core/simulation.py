"""Simulation loop — ties world, agents, skills, conflicts."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from pathlib import Path

from .agent import Agent, create_agents_from_seed
from .conflict import maybe_spawn_conflict
from .seed import WorldSeed, bootstrap_world, load_seed
from .types import Event, EventKind
from .world import drift_world, react_to_action


@dataclass
class SimulationResult:
    events: list[Event] = field(default_factory=list)
    world: object = None
    agents: list[Agent] = field(default_factory=list)
    seed: WorldSeed | None = None


def run_simulation(
    ticks: int = 20,
    seed: int | None = None,
    seed_file: Path | None = None,
) -> SimulationResult:
    rng = random.Random(seed)
    world_seed = load_seed(seed_file)
    world = bootstrap_world(world_seed, rng)
    agents = create_agents_from_seed(world_seed, rng)
    all_events: list[Event] = []

    for _ in range(ticks):
        all_events.extend(drift_world(world, rng))
        all_events.extend(maybe_spawn_conflict(world, rng))

        rng.shuffle(agents)
        for agent in agents:
            action_events, skill, success = agent.step(world, rng)
            all_events.extend(action_events)
            all_events.extend(react_to_action(world, agent, skill.key, success, rng))

        if world.active_crises and rng.random() < 0.2:
            resolved = world.active_crises.pop(0)
            all_events.append(
                Event(
                    tick=world.tick,
                    kind=EventKind.CRISIS,
                    payload={"crisis": resolved, "resolved": True},
                )
            )

    return SimulationResult(events=all_events, world=world, agents=agents, seed=world_seed)

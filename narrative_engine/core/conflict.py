"""Conflict generator — if tension is low, manufacture conflict."""

from __future__ import annotations

import random

from .types import Event, EventKind, WorldState


def maybe_spawn_conflict(world: WorldState, rng: random.Random) -> list[Event]:
    events: list[Event] = []
    tick = world.tick
    templates = world.conflict_templates
    if not templates:
        return events

    avg_trust = _average_trust(world)
    tension_low = world.narrative_pressure < 0.45 and avg_trust > 0.55
    if not tension_low and rng.random() > 0.12:
        return events

    template = rng.choice(templates)
    fa, fb = template["pair"]
    if fa in world.factions and fb in world.factions:
        world.factions[fa].trust[fb] = max(
            0.0, world.factions[fa].trust.get(fb, 0.5) + template["trust_delta"]
        )
        world.factions[fb].trust[fa] = max(
            0.0, world.factions[fb].trust.get(fa, 0.5) + template["trust_delta"]
        )
    world.narrative_pressure = min(1.0, world.narrative_pressure + template["pressure"])

    events.append(
        Event(
            tick=tick,
            kind=EventKind.CONFLICT_SPAWN,
            payload={
                "conflict_type": template["type"],
                "summary": template["summary"],
                "factions": list(template["pair"]),
                "faction_names": [
                    world.factions[f].name for f in template["pair"] if f in world.factions
                ],
            },
        )
    )
    return events


def _average_trust(world: WorldState) -> float:
    vals: list[float] = []
    for f in world.factions.values():
        vals.extend(f.trust.values())
    return sum(vals) / len(vals) if vals else 0.5

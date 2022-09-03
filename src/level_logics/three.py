from __future__ import annotations

from typing import TYPE_CHECKING

from common.event import EventType, GameEvent
from common.types import EntityType, QuestName

if TYPE_CHECKING:
    from worlds.world import World

def event_handler(world: World) -> None:
    """
    Logics for some specific events in level 3.
    """
    for e in world.events:
        if e.is_type(EventType.BOSS1_DIE) and e.get_sender_type() == EntityType.SHADOW_BOSS:
            Second_Boss = world.add_entity(EntityType.SHADOW_SUPER_BOSS, 500, 150)

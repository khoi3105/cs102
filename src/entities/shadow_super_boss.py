import logging
import random
from sys import platlibdir

from typing import TYPE_CHECKING, Iterable, List, Optional, Sequence

from common import util
from common.event import EventType, GameEvent
from common.types import ActionType, EntityType
from common.util import now
from config import Color, GameConfig, ShadowSuperBossConfig
from entities.bullet import Bullet
from entities.shadow import Shadow

if TYPE_CHECKING:
    from worlds.world import World

logger = logging.getLogger(__name__)


class ShadowSuperBoss(Shadow):
    """Boss (a large shadow)."""

    HP_BAR_HEIGHT: int = 20
    HP_TEXT_HEIGHT_OFFSET: int = -40

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hp = ShadowSuperBossConfig.INITIAL_HP
        self.is_angry = False
        self.last_angry_t = now()
        self.world: Optional[World] = None
        self.player_x: int = 0
        self.player_y: int = 0  
        self.S_ANGRY_MODE: bool = True
        self.angry_time: int = ShadowSuperBossConfig.ANGRY_INTERVAL_MS

    def update(self, screen, *args, **kwargs) -> None:
        super().update(screen, *args, **kwargs)

        # decide how to attack.
        # because player always hurt by lazer, so just active it when boss on less hp 
        if now() - self.last_angry_t > self.angry_time:
            self.is_angry = True
            self.last_angry_t = now()
            self.set_action(ActionType.ANGRY, duration_ms=ShadowSuperBossConfig.ANGRY_DURATION_MS)

            if (self.hp / ShadowSuperBossConfig.INITIAL_HP * 100) > 50:
                # normal attack
                self.player_x = self.get_player_x()
                self.player_y = self.get_player_y()
                self._move_near_player(self.player_x,self.player_y)

                # logger.info("Boss moved nearby player")
                self._shoot_bullet()
            else:
                # lazer attack
                self._shoot_lazer()

    def _shoot_bullet(self):
        player_x = self.get_player_x()
        for _ in range(7):
            bullet_id = self.world.add_entity(
                EntityType.SHADOW_BULLET,
                self.rect.centerx + random.random() * self.rect.width / 2,
                self.rect.centery + random.random() * self.rect.height / 2,
            )

            bullet: Bullet = self.world.get_entity(bullet_id)
            bullet.move_to_player(player_x)

    def _shoot_lazer(self):
        for _ in range(3):
            lazer_id = self.world.add_entity(
                EntityType.SUPERSHADOWBOSS_BULLET,
                self.rect.centerx + random.random() * self.rect.width / 2,
                self.rect.centery + random.random() * self.rect.height / 2,
            )

            bullet: Bullet = self.world.get_entity(lazer_id)

    def _take_damage(self, damage: int):
        self.hp -= damage
        self.start_hurt(duration_ms=ShadowSuperBossConfig.HURT_DURATION_MS)
        if self.hp <= 0:
            self.die()

    def _handle_get_hit(self):
        bullet: Bullet
        for bullet in self.world.get_entities(EntityType.PLAYER_BULLET):
            if self.collide(bullet):

                # Unlike normal shadow vs. bullet interaction, the boss would absorb the bullet,
                # so we remove the bullet right here.
                self.world.remove_entity(bullet.id)

                self._take_damage(bullet.damage)

    def render(self, screen, *args, **kwargs) -> None:
        super().render(screen, *args, **kwargs)

        # Render boss HP
        if self.hp > 0:
            util.display_text(
                screen,
                f"{self.hp} / {ShadowSuperBossConfig.INITIAL_HP}",
                x=self.rect.x,
                y=self.rect.top + self.HP_TEXT_HEIGHT_OFFSET,
                color=Color.BOSS_HP_BAR,
            )

            util.draw_pct_bar(
                screen,
                fraction=self.hp / ShadowSuperBossConfig.INITIAL_HP,
                x=self.rect.x,
                y=self.rect.y - self.HP_BAR_HEIGHT,
                width=self.rect.width,
                height=self.HP_BAR_HEIGHT,
                color=Color.BOSS_HP_BAR,
                margin=4,
            )

    def __del__(self):
        if self.hp <= 0:
            GameEvent(EventType.VICTORY).post()

    def _move_near_player(self,x,y):
        if x - 100 <= 10:
            self.rect.x = x + 200
        elif x + 100 > GameConfig.WIDTH - 10:
            self.rect.x = x - 200
        else:
            num = random.randint(0,2)
            if num == 0:
                self.rect.x = x - 200
            else:
                self.rect.x = x + 200
        if self.rect.top < 0:
            self.rect.top = 48
        return True

    def get_player_x(self):
        x: int = self.world.player.rect.x 
        return x

    def get_player_y(self):
        y: int = self.world.player.rect.y 
        return y

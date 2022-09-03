from common.types import EntityType
from entities.movable_entity import MovableEntity
from typing import TYPE_CHECKING, Iterable, List, Optional, Sequence

if TYPE_CHECKING:
    from worlds.world import World


class SuperBullet(MovableEntity):
    """
    A special bullet that can move to a specific position
    1. nhan thong so x, y cua ng choi
    2. moi tick thay doi sao cho du x_time giay se bay toi cho ng choi
    """
    def __init__(self, damage, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.damage = damage
        self.world: Optional[World] = None
        self.got_player_rect = False
        self.player_x = 0
        self.dx : int = 100
        self.dy : int = 0
        self.player_y = 0
        self.player_rect = None

    def update(self, screen, *args, **kwargs) -> None:
        super().update(screen, *args, **kwargs)
        if self.got_player_rect == False:
            self.got_player_rect = True
            self.player_rect = self._get_player_rect()
            self.player_x = self.player_rect.x
            self.player_y = self.player_rect.y

            # tinh toan so step de khi tang, x y dat toi player

            self.dx = abs(self.rect.x - self.player_x) / 24
            self.abc = self.dx
            self.dy = abs(self.rect.y - self.player_y) / 30

            if not self.rect.x < self.player_x:
                self.dx = -self.dx
                self.abc = self.dx
            if not self.rect.y < self.player_y:
                self.dy = -self.dy

        if self.rect.y < self.player_rect.top:
            self.dy = 0            

        self.dx = self.abc
        self.rect.x += self.dx
        print(self.dx, self.dy)
        self.rect.y += self.dy

    def _get_player_rect(self):
        return self.world.player.rect


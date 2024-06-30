from .GameCardReader import GameCardReader
from .GamePlayer import GamePlayer
from .ScreenReader import ScreenReader
from .GameEnvironment import GameEnvironment

from gymnasium.envs.registration import register

__all__ = ['GameCardReader', 'GamePlayer', 'ScreenReader', 'GameEnvironment']

register('Regent-v0', entry_point='regent_ai:GameEnvironment')

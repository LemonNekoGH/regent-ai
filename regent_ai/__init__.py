from .GameEnvironment import GameEnvironment
from gymnasium.envs.registration import register

__all__ = ['GameEnvironment']

register('Regent-v0', entry_point='regent_ai:GameEnvironment')

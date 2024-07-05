from typing import TypedDict, Any

import numpy as np
from gymnasium import Env, spaces

from regent_ai.GamePlayer import GamePlayer
from regent_ai.ScreenReader import ScreenReader
from regent_ai.GameCardReader import GameCardReader
from regent_ai.GameValuesReader import GameValuesReader, GameValues
from regent_ai.Transformer import embeddings


class GameState(TypedDict):
    message: str
    values: GameValues


def _calculate_reward(dead: bool) -> int:
    return -10 if dead else 1


class GameEnvironment(Env):
    state: np.ndarray[float, Any]
    state_human_readable: GameState
    screen_reader: ScreenReader
    card_reader: GameCardReader
    game_values_reader: GameValuesReader
    game_player: GamePlayer

    def __init__(self):
        super(GameEnvironment, self).__init__()
        self.action_space = spaces.Discrete(2)  # 0 - slide right, agree; 1 - slide left, disagree
        self.observation_space = spaces.Box(
            low=-1,
            high=1,
            shape=(388,),
            dtype=np.float32
        )  # first 384 is message, last 4 is values

        self.screen_reader = ScreenReader()
        self.card_reader = GameCardReader(self.screen_reader)
        self.game_values_reader = GameValuesReader()
        self.game_player = GamePlayer(self.screen_reader)

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):
        self.game_player.reset()
        self.state = np.concatenate((embeddings('你就是那位年轻的国王吗？'), np.zeros(4, dtype='float32')))

        return self.state, {}

    def render(self, mode='human'):
        print(self.state_human_readable)

    def step(self, action):
        state = self._take_action_and_observe(action)
        reward = _calculate_reward(state['dead'])

        values = [
            state['values']['church'],
            state['values']['people'],
            state['values']['army'],
            state['values']['wealth']
        ]
        self.state = np.concatenate((embeddings(state['message']), values))
        self.state_human_readable = {
            'message': state['message'],
            'values': state['values']
        }

        print(self.state_human_readable)

        return self.state, reward, state['dead'], False, {}

    def _take_action_and_observe(self, action: int):
        self.game_player.select_card(action)
        self.game_player.take_screenshot('screenshots/screenshot.png')
        card_content = self.card_reader.read('screenshots/screenshot.png')
        game_values = self.game_values_reader.read('screenshots/screenshot.png')

        print(game_values)

        return {
            'dead': card_content['dead'],
            'message': card_content['message'],
            'values': game_values
        }

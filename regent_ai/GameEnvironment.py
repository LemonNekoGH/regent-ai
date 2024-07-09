import datetime
from typing import TypedDict, Any, Union

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
    years: str
    character_name: str
    steps: int


class GameEnvironment(Env):
    state: np.ndarray[float, Any]
    state_human_readable: GameState
    screen_reader: ScreenReader
    card_reader: GameCardReader
    game_values_reader: GameValuesReader
    game_player: GamePlayer
    steps: int
    time: Union[float, None]
    game_count: int

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
        self.steps = 0
        self.time = None
        self.game_count = 0

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):
        self.game_count += 1
        new_time = datetime.datetime.now(datetime.UTC).timestamp()
        if self.time is not None:
            print('============================================================')
            print(f'Game over: {self.game_count}, spent: {new_time - self.time}')
        self.time = new_time

        self.game_player.reset()
        self.state = np.concatenate((embeddings('你就是那位年轻的国王吗？'), np.zeros(4, dtype='float32')))

        return self.state, {}

    def render(self, mode='human'):
        print(self.state_human_readable)

    def step(self, action):
        self.steps += 1
        # observe
        state = self._observe()
        if state['dead']:
            return self.state, -10, True, {}, {}
        # take action
        self.game_player.select_card(action)
        # observe again
        state = self._observe()
        # if card contains narration, keep selecting card
        while state['narration'] != '':
            print('Maybe narration: ' + state['narration'])
            self.game_player.select_card(action)
            state = self._observe()

        values = [
            state['values']['church'],
            state['values']['people'],
            state['values']['army'],
            state['values']['wealth']
        ]
        self.state = np.concatenate((embeddings(state['message']), values))
        self.state_human_readable = {
            'steps': self.steps,
            'years': state['years'],
            'values': state['values'],
            'message': state['message'],
            'character_name': state['character_name'],
        }

        print(self.state_human_readable)

        return self.state, 1, False, False, {}

    def _observe(self):
        self.game_player.take_screenshot('screenshots/screenshot.png')
        card_content = self.card_reader.read('screenshots/screenshot.png')
        game_values = self.game_values_reader.read('screenshots/screenshot.png')

        return {
            'dead': card_content['dead'],
            'message': card_content['message'],
            'narration': card_content['narration'],
            'years': card_content['years'],
            'character_name': card_content['character_name'],
            'values': game_values
        }

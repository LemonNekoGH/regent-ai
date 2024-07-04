from typing import TypedDict, Any

from gymnasium import Env, spaces

from regent_ai.GamePlayer import GamePlayer
from regent_ai.ScreenReader import ScreenReader
from regent_ai.GameCardReader import GameCardReader
from regent_ai.GameValuesReader import GameValuesReader, GameValues


class GameState(TypedDict):
    dead: int  # current value
    message: str  # last value
    action: int  # last value
    values: GameValues  # current value


class GameEnvironment(Env):
    last_message: str
    last_action: int

    state: GameState
    screen_reader: ScreenReader
    card_reader: GameCardReader
    game_values_reader: GameValuesReader
    game_player: GamePlayer

    def __init__(self):
        super(GameEnvironment, self).__init__()
        self.action_space = spaces.Discrete(2)  # 0 - slide right, agree; 1 - slide left, disagree
        self.observation_space = spaces.Dict({
            'dead': spaces.Discrete(2),  # 0 - alive, 1 - dead
            'message': spaces.Text(max_length=30, charset='utf-8'),
            'action': spaces.Discrete(2),
            'values': spaces.Dict({
                'church': spaces.Discrete(100),
                'people': spaces.Discrete(100),
                'army': spaces.Discrete(100),
                'wealth': spaces.Discrete(100)
            })
        })

        self.screen_reader = ScreenReader()
        self.card_reader = GameCardReader(self.screen_reader)
        self.game_values_reader = GameValuesReader()
        self.game_player = GamePlayer(self.screen_reader)

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):
        self.game_player.reset()
        self.state = {
            'dead': 0,
            'message': '你就是那位年轻的国王吗？',
            'action': 0,
            'values': {
                'church': 0,
                'people': 0,
                'army': 0,
                'wealth': 0
            }
        }

        # FIXME: state is not in the observation space
        return self.state, {}

    def render(self, mode='human'):
        print(self.state)

    def step(self, action):
        self._take_action_and_observe(action)
        done = self.state['dead'] == 1
        reward = self._calculate_reward()

        # FIXME: state is not in the observation space
        return self.state, reward, done, False, {}

    def _take_action_and_observe(self, action: int):
        self.game_player.select_card(action)
        self.game_player.take_screenshot('screenshots/screenshot.png')
        card_content = self.card_reader.read('screenshots/screenshot.png')
        game_values = self.game_values_reader.read('screenshots/screenshot.png')

        # update current state
        self.state['dead'] = card_content['dead']
        self.state['message'] = self.last_message
        self.state['action'] = self.last_action
        self.state['values'] = game_values

        # update last state
        self.last_action = action
        self.last_message = card_content['message']

    def _calculate_reward(self) -> int:
        if self.state['dead'] == 1:
            reward = -100
        else:
            reward = 1
        return reward

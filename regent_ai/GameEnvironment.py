from collections import deque
from typing import TypedDict, Union, Any

from gymnasium import Env, spaces

from regent_ai import GamePlayer, GameCardReader, ScreenReader


class ActionHistory(TypedDict):
    message: str
    character_name: str
    action: int


class GameState(TypedDict):
    dead: int
    message: str
    character_name: str
    history: deque[ActionHistory]


class GameEnvironment(Env):
    last_state: Union[ActionHistory, None]
    state: Union[GameState, None]
    screen_reader: ScreenReader
    card_reader: GameCardReader
    game_player: GamePlayer

    def __init__(self):
        super(GameEnvironment, self).__init__()
        self.action_space = spaces.Discrete(2)  # 0 - slide right, agree; 1 - slide left, disagree
        self.observation_space = spaces.Dict({
            'dead': spaces.Discrete(2),  # 0 - alive, 1 - dead
            'message': spaces.Text(max_length=20),
            'character_name': spaces.Text(max_length=20),
            'history': spaces.Sequence(spaces.Dict({
                'message': spaces.Text(max_length=20),
                'character_name': spaces.Text(max_length=20),
                'action': spaces.Discrete(2)
            }))
        })

        self.state = None
        self.last_state = None
        self.screen_reader = ScreenReader()
        self.card_reader = GameCardReader(self.screen_reader)
        self.game_player = GamePlayer(self.screen_reader)

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):
        self.game_player.reset()
        self.state = {
            'dead': 0,
            'message': '你就是那位年轻的国王吗？',
            'character_name': '亡者之灵',
            'history': deque(maxlen=10)
        }

        # FIXME: state is not in the observation space
        return self.state, {}

    def render(self, mode='human'):
        print({
            'dead': self.state['dead'],
            'message': self.last_state['message'],
            'character_name': self.last_state['character_name'],
            'action': self.last_state['action']
        })

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

        # push last state to history
        if self.last_state is not None:
            self.last_state['action'] = action
            self.state['history'].append(self.last_state)

        # update current state
        self.state['dead'] = card_content['dead']
        self.state['message'] = card_content['message']
        self.state['character_name'] = card_content['character_name']

        # update last state
        self.last_state = {
            'message': card_content['message'],
            'character_name': card_content['character_name'],
            'action': 0
        }

    def _calculate_reward(self) -> int:
        if self.state['dead'] == 1:
            reward = -100
        else:
            reward = 1
        return reward

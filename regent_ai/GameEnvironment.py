import datetime
import random
import time
from typing import TypedDict, Any, Union

import numpy as np
from gymnasium import Env, spaces

from regent_ai.GamePlayer import GamePlayer
from regent_ai.ScreenReader import ScreenReader
from regent_ai.GameCardReader import GameCardReader
from regent_ai.GameValuesReader import GameValuesReader


class GameState(TypedDict):
    message: str
    values: list[float]
    years: int
    character_name: str
    steps: int


class GameEnvironment:
    state_human_readable: GameState
    screen_reader: ScreenReader
    card_reader: GameCardReader
    game_values_reader: GameValuesReader
    game_player: GamePlayer
    steps: int
    time: Union[float, None]
    game_count: int

    def __init__(self):
        self.screen_reader = ScreenReader()
        self.card_reader = GameCardReader(self.screen_reader)
        self.game_values_reader = GameValuesReader()
        self.game_player = GamePlayer(self.screen_reader)
        self.steps = 0
        self.time = None
        self.game_count = 0
        self.state_human_readable = {
            'steps': 0,
            'years': 0,
            'values': [0, 0, 0, 0],
            'message': '',
            'character_name': '',
        }

    def reset(self):
        self.game_count += 1
        new_time = datetime.datetime.now(datetime.UTC).timestamp()
        if self.time is not None:
            print('============================================================')
            print(f'Game over: {self.game_count}, spent: {new_time - self.time}')
        self.time = new_time

        self.game_player.reset()

        self.state_human_readable = {
            'steps': 0,
            'years': 0,
            'values': [0, 0, 0, 0],
            'message': '',
            'character_name': '',
        }

    def render(self):
        print(self.state_human_readable)

    def step(self, cards):
        self.steps += 1
        state = self._observe()
        # dead
        if (((0 in state['values'] or 1000 in state['values'])
             and state['character_name'] and state['character_name'] != '亡者之灵')
                or state['dead']):
            return True, {}, 0

        action = 1
        # achievement
        while state['narration'] and state['character_name']:
            print('Maybe achievement: ' + state['narration'])
            self.game_player.tap_screen_center()
            time.sleep(1)
            state = self._observe()

        # narration, keep selecting card
        while state['narration'] and not state['character_name']:
            print('Maybe narration: ' + state['narration'])
            self.game_player.select_card(action)
            state = self._observe()

        # take action
        self.state_human_readable = {
            'steps': self.steps,
            'years': state['years'],
            'values': state['values'],
            'message': state['message'],
            'character_name': state['character_name'],
        }
        exists_card = cards.get(state['message'])
        action = self._do_choice(state['values'], exists_card)
        self.game_player.select_card(action)
        state = self._observe()

        effect = [
            state['values'][0] - self.state_human_readable['values'][0],
            state['values'][1] - self.state_human_readable['values'][1],
            state['values'][2] - self.state_human_readable['values'][2],
            state['values'][3] - self.state_human_readable['values'][3]
        ]

        step_info = {
            'message': self.state_human_readable['message'],
            'character_name': self.state_human_readable['character_name'],
            'effect': effect,
            'action': action,
            'steps': self.steps,
            'years': self.state_human_readable['years'],
        }

        print(step_info)

        return False, step_info, action

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

    def _do_choice(self, current_values, card):
        if card is None:
            return 1

        # if another choice not try yet
        if card['effect'][0] is None:
            return 0

        values_if_agree = [
            current_values[0] + card['effect'][1][0],
            current_values[1] + card['effect'][1][1],
            current_values[2] + card['effect'][1][2],
            current_values[3] + card['effect'][1][3]
        ]
        values_if_disagree = [
            current_values[0] + card['effect'][0][0],
            current_values[1] + card['effect'][0][1],
            current_values[2] + card['effect'][0][2],
            current_values[3] + card['effect'][0][3]
        ]

        # check which choice will lead to game over
        game_over_if_agree = max(values_if_agree) > 1000 or min(values_if_agree) < 0
        game_over_if_disagree = max(values_if_disagree) > 1000 or min(values_if_disagree) < 0
        if game_over_if_agree:
            if game_over_if_disagree:
                print('Both choice will lead to game over.')
                return 1

            print('If agree, game over.')
            return 0

        if game_over_if_disagree:
            print('If disagree, game over.')
            return 1

        current_score = sum([abs(500 - v) for v in current_values])
        agree_score = sum([abs(500 - v) for v in values_if_agree])
        disagree_score = sum([abs(500 - v) for v in values_if_disagree])

        if agree_score == disagree_score:
            print(f'Effect equals, agree: {agree_score}, disagree: {disagree_score}, current: {current_score}')
            return random.choice([0, 1])

        if agree_score < disagree_score:
            print(f'Agree is better, agree: {agree_score}, disagree: {disagree_score}, current: {current_score}')

            return 1

        print(f'Disagree is better, agree: {agree_score}, disagree: {disagree_score}, current: {current_score}')
        return 0

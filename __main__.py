import json
import random

import regent_ai
import gymnasium as gym
from typing import TypedDict, Tuple, Dict, List, TextIO

from stable_baselines3 import PPO


class CardInFile(TypedDict):
    message: str
    effect: list[list[int]]  # agree, disagree. church, people, army, wealth.
    character_name: str


class CardInMemory(TypedDict):
    effect: list[list[int]]  # agree, disagree. church, people, army, wealth.
    character_name: str


def write_card_to_file(card_in_memory: Dict[str, CardInMemory]):
    file = open('log-cards.json', 'w+', encoding='utf-8')
    # noinspection PyTypeChecker
    card_in_file: List[CardInFile] = []
    for message, card in card_in_memory.items():
        card_in_file.append({
            'message': message,
            'effect': card['effect'],
            'character_name': card['character_name']
        })

    file.write(json.dumps(card_in_file, indent=2, ensure_ascii=False))
    file.close()


def read_card_from_file() -> Dict[str, CardInMemory]:
    file = open('log-cards.json', 'r', encoding='utf-8')
    file_content = file.read()
    if len(file_content) == 0:
        return {}

    card_in_file: List[CardInFile] = json.loads(file_content)
    card_in_memory: Dict[str, CardInMemory] = {}
    for card in card_in_file:
        card_in_memory[card['message']] = {
            'effect': card['effect'],
            'character_name': card['character_name']
        }

    file.close()
    return card_in_memory


def main():
    cards = read_card_from_file()
    game_env = regent_ai.GameEnvironment()
    # game_env.reset()

    for _ in range(10000):
        done, info, action = game_env.step(cards)
        if done:
            game_env.reset()
            continue

        if info['message'] == '':
            continue

        card = cards.get(info['message'])
        if card is None:
            effect = [None, None]
            effect[action] = info['effect']
            cards[info['message']] = {
                'effect': effect,
                'character_name': info['character_name']
            }
            print('new card:', info['message'], cards[info['message']])
            write_card_to_file(cards)
            continue

        if card['effect'][action] == info['effect']:
            continue

        print(f'card effect changed:', info['message'], 'before:', card['effect'][action], 'after:', info['effect'])
        card['effect'][action] = info['effect']
        cards[info['message']] = card
        write_card_to_file(cards)


if __name__ == '__main__':
    main()

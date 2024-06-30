from typing import TypedDict, List, Tuple
from regent_ai import ScreenReader


class GameCardContent(TypedDict):
    character_name: str
    message: str
    years: str
    dead: int


def extract_card_content(detections: List[Tuple], threshold=0.25) -> GameCardContent:
    message = ''
    character_name = ''
    years = ''
    dead = 0

    print(detections)

    for bbox, text, score in detections:
        if score < threshold:
            continue

        if bbox[0][1] > 600 and bbox[2][1] < 760:
            message += text

        if bbox[0][1] > 1860 and bbox[2][1] < 1960:
            character_name = text

        if bbox[0][0] > 540 and bbox[0][1] > 1960:
            years = text

        if '已死' in text:
            dead = 1

    return {
        'message': message,
        'character_name': character_name,
        'years': years,
        'dead': dead
    }


class GameCardReader:
    screen_reader: ScreenReader

    def __init__(self, screen_reader: ScreenReader):
        self.screen_reader = screen_reader

    def read(self, img_path: str) -> GameCardContent:
        detections = self.screen_reader.read(img_path)
        return extract_card_content(detections)

from typing import TypedDict, List, Tuple

from regent_ai.ScreenReader import ScreenReader


class GameCardContent(TypedDict):
    character_name: str
    message: str
    years: str
    dead: bool
    narration: str


def extract_card_content(detections: List[Tuple], threshold=0.25) -> GameCardContent:
    message = ''
    character_name = ''
    years = ''
    dead = False
    narration = ''

    for bbox, text, score in detections:
        if score < threshold:
            continue

        if bbox[0][1] > 580 and bbox[2][1] < 780:
            message += text

        if bbox[0][1] > 1860 and bbox[2][1] < 1960:
            character_name = text

        if bbox[0][0] > 540 and bbox[0][1] > 1960:
            years = text

        if bbox[0][1] > 850 and bbox[2][1] < 1840:
            narration += text

        # FIXME: '己' is wrong word, should be '已'
        if '己死' in text:
            dead = True

    return {
        'message': message,
        'character_name': character_name,
        'years': years,
        'dead': dead,
        'narration': narration
    }


class GameCardReader:
    screen_reader: ScreenReader

    def __init__(self, screen_reader: ScreenReader):
        self.screen_reader = screen_reader

    def read(self, img_path: str) -> GameCardContent:
        detections = self.screen_reader.read(img_path)
        return extract_card_content(detections)

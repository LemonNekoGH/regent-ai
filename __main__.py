import datetime

import numpy as np
import easyocr
from PIL import Image, ImageDraw, ImageFont
import cv2


class CardContent:
    character_name: str = ''
    message: str = ''
    years: str = ''


class GameCardReader:
    def __init__(self):
        self.font = ImageFont.truetype('./fonts/noto-sans-sc-regular.ttf', 24)
        self.ocr_reader = easyocr.Reader(['ch_sim', 'en'])

    def draw_bounding_boxes(self, img_data, detections, threshold=0.25):
        img = Image.fromarray(img_data)
        draw = ImageDraw.Draw(img)

        for bbox, text, score in detections:
            if score > threshold:
                draw.rectangle([(bbox[0][0], bbox[0][1]), (bbox[2][0], bbox[2][1])], outline='green', width=2)
                draw.text((bbox[0][0], bbox[0][1] - 32), text, fill='green', font=self.font)

        return np.array(img)

    def read_card(self) -> CardContent:
        image = cv2.imread('./screenshots/screenshot.png')
        result = self.ocr_reader.readtext(image)
        image_with_boxes = self.draw_bounding_boxes(image, result)
        now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds')
        cv2.imwrite('./screenshots/screenshot-{0}.png'.format(now), image_with_boxes)
        return self.extract_card_content(result)

    def extract_card_content(self, detections, threshold=0.25) -> CardContent:
        ret: CardContent = CardContent()

        for bbox, text, score in detections:
            if score < threshold:
                continue

            if bbox[0][1] > 600 and bbox[2][1] < 760:
                ret.message += text

            if bbox[0][1] > 1860 and bbox[2][1] < 1960:
                ret.character_name = text

            if bbox[0][0] > 540 and bbox[0][1] > 1960:
                ret.years = text

        return ret

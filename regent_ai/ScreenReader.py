from typing import List, Tuple

import cv2
import easyocr
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont
from easyocr import Reader


class ScreenReader:
    ocr_reader: Reader
    font: FreeTypeFont

    def __init__(self) -> None:
        self.font = ImageFont.truetype('./fonts/noto-sans-sc-regular.ttf', 24)
        self.ocr_reader = easyocr.Reader(['ch_sim', 'en'])

    def _visualize_result(self, img_data: np.ndarray, detections: List[Tuple], threshold=0.25) -> np.ndarray:
        img = Image.fromarray(img_data)
        draw = ImageDraw.Draw(img)

        for bbox, text, score in detections:
            if score > threshold:
                draw.rectangle([(bbox[0][0], bbox[0][1]), (bbox[2][0], bbox[2][1])], outline='green', width=2)
                draw.text((bbox[0][0], bbox[0][1] - 32), text, fill='green', font=self.font)

        return np.array(img)

    def read(self, img_path: str) -> List[Tuple]:
        image = cv2.imread(img_path)
        result = self.ocr_reader.readtext(image)
        marked_image = self._visualize_result(image, result)
        cv2.imwrite(f'{img_path}-marked.png', marked_image)
        return result

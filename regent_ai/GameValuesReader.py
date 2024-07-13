import cv2
import numpy as np

from typing import TypedDict, Tuple, List
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont

church_icon_bound = ((70, 237), (174, 376))
people_icon_bound = ((352, 237), (450, 376))
army_icon_bound = ((647, 237), (710, 376))
wealth_icon_bound = ((920, 237), (992, 376))


class GameValuesReader:
    def crop_icon(self, image: np.ndarray, bound: Tuple[Tuple[int, int], Tuple[int, int]]) -> np.ndarray:
        return image[bound[0][1]:bound[1][1], bound[0][0]:bound[1][0]]

    def percentage_white_height(self, image: np.ndarray) -> int:
        for i in range(len(image)):  # height
            for j in range(len(image[0])):  # width
                if image[i][j] == 255:
                    return 1000 - round(i / len(image) * 1000)  # invert value for human reading

        return 0

    def read(self, img_path: str) -> list[float]:
        image = cv2.imread(img_path)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        _, binary_image = cv2.threshold(gray_image, 122, 255, cv2.THRESH_BINARY)
        cv2.imwrite(f'{img_path}-binary.png', binary_image)
        church_icon_binary = self.crop_icon(binary_image, church_icon_bound)
        people_icon_binary = self.crop_icon(binary_image, people_icon_bound)
        army_icon_binary = self.crop_icon(binary_image, army_icon_bound)
        wealth_icon_binary = self.crop_icon(binary_image, wealth_icon_bound)

        cv2.imwrite('./screenshots/church-icon_binary.png', church_icon_binary)
        cv2.imwrite('./screenshots/people-icon_binary.png', people_icon_binary)
        cv2.imwrite('./screenshots/army-icon_binary.png', army_icon_binary)
        cv2.imwrite('./screenshots/wealth-icon_binary.png', wealth_icon_binary)

        return [
            self.percentage_white_height(church_icon_binary),
            self.percentage_white_height(people_icon_binary),
            self.percentage_white_height(army_icon_binary),
            self.percentage_white_height(wealth_icon_binary)
        ]

# def visualize_game_values(image_data: np.ndarray, game_values: GameValues) -> np.ndarray:
#     image = Image.fromarray(image_data)
#     draw = ImageDraw.Draw(image)
#
#
#     return image

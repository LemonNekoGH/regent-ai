from time import sleep

import ppadb.client as client
from ppadb.client import Client
from ppadb.device import Device

from regent_ai.ScreenReader import ScreenReader


class GamePlayer:
    device: Device
    adb: Client
    screen_reader: ScreenReader
    screenshot_path: str

    def __init__(self, screen_reader: ScreenReader):
        self.adb = client.Client()

        devices = self.adb.devices()
        if len(devices) == 0:
            raise Exception('No devices attached')

        self.device = devices[0]
        self.screenshot_path = './screenshots/screenshot.png'
        self.screen_reader = screen_reader

    def reset(self):
        # Clear data
        self.device.shell('pm clear com.devolver.reigns')
        # Back to reigns app
        self.device.shell('am start -n com.devolver.reigns/.UnityPlayerActivity')
        self.wait_for_text('取消')
        # Tap cancel button on Google Play
        self.tap_until_text_exists_or_not_exists(170, 2175, '取消', should_exists=False)
        # Click to start game
        self.tap_until_text_exists_or_not_exists(540, 1175, '亡者之灵', should_exists=True)
        # Click to stop tutorial
        self.tap_screen_center()

    def tap_until_text_exists_or_not_exists(self, x: int, y: int, text: str, should_exists: bool):
        self.take_screenshot(self.screenshot_path)
        result = self.screen_reader.read(self.screenshot_path)
        target_exists = False
        for _, t, score in result:
            if score > 0.25 and t == text:
                target_exists = True
                break

        if should_exists:
            if target_exists:
                return

            self.device.input_tap(x, y)
            sleep(1)
            self.tap_until_text_exists_or_not_exists(x, y, text, should_exists)

        if not should_exists:
            if not target_exists:
                return

            self.device.input_tap(x, y)
            sleep(1)
            self.tap_until_text_exists_or_not_exists(x, y, text, should_exists)

    def select_card(self, right: int):
        x1 = 270 if right else 810
        x2 = 810 if right else 270
        self.device.input_swipe(x1, 1170, x2, 1170, 1000)
        sleep(2)

    def take_screenshot(self, save_path: str):
        self.device.shell("screencap -p /sdcard/screen.png")
        self.device.pull("/sdcard/screen.png", save_path)

    def tap_screen_center(self):
        self.device.input_tap(540, 1175)

    def wait_for_text(self, text: str, threshold=0.25) -> None:
        self.take_screenshot(self.screenshot_path)
        detections = self.screen_reader.read(self.screenshot_path)
        for _, t, score in detections:
            if score > threshold and t == text:
                return

        sleep(1)
        self.wait_for_text(text, threshold)

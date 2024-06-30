from time import sleep

import ppadb.client as client
from ppadb.client import Client
from ppadb.device import Device

from regent_ai import ScreenReader


class GamePlayer:
    device: Device
    adb: Client
    screen_reader: ScreenReader
    screenshot_path: str

    def __init__(self, screen_reader: ScreenReader):
        self.adb = client.Client()
        self.device = self.adb.devices()[0]
        self.screenshot_path = './screenshots/screenshot.png'
        self.screen_reader = screen_reader

    def reset(self):
        # Stop settings app
        self.device.shell('am stop-app com.android.settings')
        # Go to settings activity
        self.device.shell('am start -a android.settings.APPLICATION_SETTINGS')
        # Find reigns app
        found = False
        position_x = 0
        position_y = 0
        while not found:
            self.take_screenshot(self.screenshot_path)
            result = self.screen_reader.read(self.screenshot_path)
            for bound, text, _ in result:
                if text == 'Reigns':
                    found = True
                    position_x = (bound[0][0] + bound[2][0]) / 2
                    position_y = (bound[0][1] + bound[2][1]) / 2
                    break

            if not found:
                self.device.input_swipe(540, 1755, 540, 585, 1000)
        # Click on reigns app
        self.device.input_tap(position_x, position_y)
        sleep(1)
        # Click on data deletion
        self.device.input_tap(540, 1840)
        sleep(1)
        # Click on delete button
        self.device.input_tap(291, 1145)
        sleep(1)
        # Click on confirm button
        self.device.input_tap(914, 1344)
        sleep(1)
        # Back to reigns app
        self.device.shell('am start -n com.devolver.reigns/.UnityPlayerActivity')
        sleep(5)
        # Click on Google Play Games cancel button
        self.device.input_tap(170, 2175)
        sleep(5)
        # Click to start game
        self.device.input_tap(540, 1175)
        sleep(10)
        # Click to stop tutorial
        self.device.input_tap(540, 1175)

    def select_card(self, right: int):
        x1 = 270 if right else 810
        x2 = 810 if right else 270
        self.device.input_swipe(x1, 1170, x2, 1170, 2500)
        sleep(1)

    def take_screenshot(self, save_path: str):
        self.device.shell("screencap -p /sdcard/screen.png")
        self.device.pull("/sdcard/screen.png", save_path)

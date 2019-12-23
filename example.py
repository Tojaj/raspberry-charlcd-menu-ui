#!/usr/bin/env python3

"""
An example of a menu user interface for LCD shield for Raspberry Pi (16x2 display, 5 buttons).
"""

import time
import subprocess

import Adafruit_CharLCD as LCD

from CharLCDMenu import MainMenu, MenuItem, SELECT, UP, DOWN, LEFT, RIGHT


class HiWorldAction(MenuItem):

    def run(self):
        self._display.print(1, "Hi World! \x02")
        time.sleep(2)
        # Tell the caller that we are done
        return False

    def button_press(self, button):
        pass


class PrintButtonAction(MenuItem):

    def run(self):
        self._display.print(1, "Press buttons..")
        # Tell the caller that we want to get the subsequent button press
        return True

    def button_press(self, button):
        if button == UP:
            self._display.print(2, "Up")
        elif button == DOWN:
            self._display.print(2, "Down")
        elif button == LEFT:
            self._display.print(2, "Left")
        elif button == RIGHT:
            self._display.print(2, "Right")
        elif button == SELECT:
            self._display.print(2, "Select - ENDING")
            time.sleep(2)
            # Tell the caller that we are done
            return False

        # Tell the caller that we want to get the subsequent button press
        return True


class SystemCheckAction(MenuItem):

    def run(self):
        self._display.print(1, "Checking..")
        time.sleep(1)

        # RTL-SDR
        completed = subprocess.run(["uname"])
        if completed.returncode != 0:
            self._display.print(1, f"uname: ERR {completed.returncode}")
        else:
            self._display.print(1, f"uname:      \x02 OK")

        # Tell the caller that we want to get the subsequent button press
        return True

    def button_press(self, button):
        # Any button press will end this action
        return False


class ShutDownAction(MenuItem):
    """Shut down the Raspberry Pi operating system"""

    def run(self):
        self._display.print(1, "Shutting down..")
        time.sleep(0.5)
        completed = subprocess.run(["/sbin/shutdown", "now"])
        if completed.returncode != 0:
            self._display.print(2, f"Failed: {completed.returncode}")
        else:
            self._display.print(2, f"OK: {completed.returncode}")
        time.sleep(3)
        return False

    def button_press(self, button):
        # Any button press will end this action
        return False


def main():

    # Get the LCD object
    lcd = LCD.Adafruit_CharLCDPlate()

    # Create the menu UI
    menu = MainMenu(lcd)
    menu.add_item(HiWorldAction("Say Hi!"))
    menu.add_item(PrintButtonAction("Test buttons"))
    menu.add_item(SystemCheckAction("System check"))
    menu.add_item(ShutDownAction("Shutdown"))

    # Start the UI
    menu.run()


if __name__ == "__main__":
    main()

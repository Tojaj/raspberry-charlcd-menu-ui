import time
import signal

import Adafruit_CharLCD as LCD


# Buttons
SELECT = LCD.SELECT
LEFT = LCD.LEFT
UP = LCD.UP
DOWN = LCD.DOWN
RIGHT = LCD.RIGHT


class Display(object):
    """A class handling LCD display manipulation"""

    CHARS = 16
    LINES = 2

    def __init__(self, lcd):
        self._lcd = lcd
        self._buffer = None

        self._init_buffer()
        self._create_custom_symbols()
        self._lcd.clear()

    def _init_buffer(self):
        """Create an empty buffer"""
        buffer = []
        for x in range(self.LINES):
            line = " "*self.CHARS
            buffer.append(line)
        self._buffer = buffer

    def _create_custom_symbols(self):
        """Define a custom symbols for the display."""

        # Custom symbols
        self._lcd.create_char(1, [2, 3, 2, 2, 14, 30, 12, 0])     # Note
        self._lcd.create_char(2, [0, 1, 3, 22, 28, 8, 0, 0])      # Check mark
        self._lcd.create_char(3, [0, 14, 21, 23, 17, 14, 0, 0])   # Clock
        self._lcd.create_char(4, [31, 17, 10, 4, 10, 17, 31, 0])  # Hourglass
        self._lcd.create_char(5, [8, 12, 10, 9, 10, 12, 8, 0])    # Arrow right
        self._lcd.create_char(6, [2, 6, 10, 18, 10, 6, 2, 0])     # Arrow left
        # Turn off symbol
        self._lcd.create_char(7, [0b00100,
                                  0b00100,
                                  0b01110,
                                  0b10101,
                                  0b10101,
                                  0b10001,
                                  0b01110,
                                  0b00000])

    def clear(self):
        """Clear the display (and the internal buffer)"""
        self._lcd.clear()
        for x in range(self.LINES):
            self._buffer[x] = " " * self.CHARS

    def flush(self):
        """Write the internal buffer out to the display"""
        self._lcd.clear()
        self._lcd.message("\n".join(self._buffer))

    def print(self, line, message, flush=True):
        """Print a message to the display to a specific line"""

        # TODO:
        # * Convert the assert to an exception
        # * Make sure string doesn't contain new line chars

        assert 1 <= line <= self.LINES, "Wrong line number!"

        # Make sure the line has exactly self.chars characters
        self._buffer[line - 1] = f"{message[:self.CHARS]:{self.CHARS}}"
        if flush:
            self.flush()


class Controls(object):
    """A class handling button presses"""

    BUTTONS = (
        SELECT,
        LEFT,
        UP,
        DOWN,
        RIGHT
    )

    def __init__(self, lcd, func):
        """Class for handling button presses.

        :param lcd: An Adafruit_CharLCD.LCD instance.
        :param func: A callback function that will be called when a button is
        pressed. The function takes only one parameter, the button that was
        pressed."""

        self.lcd = lcd
        self.func = func

        self.run = True
        self.announced = set()

        super().__init__()

    def start(self):
        """Pool for button state and report presses in a loop"""

        while self.run:
            for button in self.BUTTONS:
                if self.lcd.is_pressed(button):
                    if button in self.announced:
                        # Report button press only once
                        continue
                    self.announced.add(button)
                    self.func(button)
                else:
                    if button in self.announced:
                        self.announced.remove(button)
            time.sleep(0.1)  # Don't pool too often

    def stop_signal(self, *args):
        """Stop the loop

        The function accepts extra arguments (to make it possible to be used
        as a signal handler) but doesn't use them."""
        self.run = False


class MainMenu(object):
    """Object of the main menu"""

    STATE_INIT = 0
    STATE_READY = 1

    def __init__(self, lcd):
        self._lcd = lcd
        self.display = Display(lcd)
        self.items = []

        self._controls = None
        self._running_child = None

        # State machine
        self._state = self.STATE_INIT
        self._current_item = 0

    def add_item(self, item):
        """Add a menu item"""
        item._set_display(self.display)
        self.items.append(item)

    def _button_press(self, button):
        """ Handle button press

        :return: Return True if you want to be passed by key presses. Return False if you are over."""

        if self._running_child:
            print("Passing to a running child")
            # Pass button press to kids, they can handle it
            keep = self._running_child._button_press(button)
            print(f"button press: {keep}")
            if not keep:
                self._running_child = None
                self._display_menu()
            return

        # Handle button press by myself
        self._change_state(button)

    def _change_state(self, button=None):
        if self._state == self.STATE_INIT:
            self._display_menu()
            self._state = self.STATE_READY
        elif self._state == self.STATE_READY:
            print(button, type(button))
            #assert button is None, "Button not set"
            if button == UP:
                if self._current_item > 0:
                    self._current_item -= 1
                self._display_menu()
            elif button == DOWN:
                if (self._current_item + 1) < len(self.items):
                    self._current_item += 1
                self._display_menu()
            elif button == SELECT:
                self._running_child = self.items[self._current_item]
                keep = self.items[self._current_item]._run()
                print(f"change state KEEP: {keep}")
                if not keep:
                    self._running_child = None
                    self._display_menu()
            else:
                pass

    def _display_menu(self):
        print(f"current_item: {self._current_item}")
        items_to_be_shown = self.items[self._current_item:self._current_item + self.display.LINES]
        self.display.clear()
        for x, item in enumerate(items_to_be_shown):
            if x == 0:
                text = f"\x05 {item.name}"
            else:
                text = f"  {item.name}"
            self.display.print(x+1, text, flush=False)
        self.display.flush()

    def run(self):
        """Start the business"""
        self._controls = Controls(self._lcd, self._button_press)
        self._change_state()
        signal.signal(signal.SIGINT, self._controls.stop_signal)
        self._loop()

    def _loop(self):
        self._controls.start()
        self.display.clear()


class MenuItem(object):
    """Generic menu item"""

    def __init__(self, name):
        self.name = name

        self._display = None
        self._running_child = None

    def _set_display(self, display):
        """Set display object"""
        self._display = display

    def _button_press(self, button):
        """ Handle button press
        :return: Return True if you want to be passed by key presses. Return False if you are over."""

        if self._running_child:
            # Pass button press to kids, they can handle it
            keep = self._running_child._button_press(button)
            if not keep:
                self._running_child = None
                #self._display_menu()
            return keep

        return self.button_press(button)

    def _run(self):
        self._display.clear()
        return self.run()

    def run(self):
        """Code of the action.

        :return: Return False if the action is over and upcoming button
        presses shouldn't be passed to this object. Return True if you
        still want to receive button presses."""
        raise NotImplementedError

    def button_press(self, button):
        """Handle button press here

        :return: Return False if the action is over and upcoming button
        presses shouldn't be passed to this object. Return True if you
        still want to receive button presses."""
        raise NotImplementedError


# TODO:
# * Specialized child classes of MenuItem that can provide nested menu, integer input, etc.
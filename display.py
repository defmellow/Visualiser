import sys
import tkinter
from random import randint
from time import sleep, time


class Display:
    """
    Prints a 2d array of pixels to the console. Each pixel can be on or off, and the display can be set to different modes (on, off, dim).
    Coordinates start at 0,0 in the top left corner

    Initialise by setting mode with set_mode() and print with render().
    """

    def __init__(self, height: int, width: int, display: list[list[bool | None]] | None = None):
        self._height = height
        self._width = width
        self.state = False
        self.symbols = {}
        # 2d array
        # [x, x, x]
        # [x, x, x]

        if display is None:
            display = [[False for _ in range(width)] for _ in range(height)]

        self._display: list[list[bool | None]] = display
        self.set_mode(False)

    def set_mode(self, state: bool, on: str = "#", off: str = "*", dim: str = " "):
        self.symbols = {True: on, False: off, None: dim}
        self.state = state
        if state is True:
            sys.stdout.write("\033[2J\033[?25l")
        else:
            sys.stdout.write("\033[?25h")

    def render(self):
        self.set_mode(True, *self.symbols.values())
        rows = [" ".join(self.symbols[x] for x in row) for row in self._display]
        sys.stdout.write("\033[H" + "\n".join(rows) + "\033[J")
        sys.stdout.flush()

    def count_on(self):
        print(sum(1 for y in self._display for x in y if x is True))

    def pixel(self, x: int, y: int, state: bool):
        if x >= self._width or y >= self._height or y < 0 or x < 0:  # >= because self._width and self._height are counts, while x and y are 0-in dexed
            raise ValueError(f"Coordinates out of bounds with pixel {x}, {y} to {state}")
        self._display[y][x] = state

    def create_line(self, x1: int, y1: int, x2: int, y2: int, state: bool):
        if x1 == x2 or y1 == y2:
            for x in range(min(x1, x2), max(x1, x2) + 1):
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    self.pixel(x, y, state)
        else:
            raise ValueError("Only horizontal or vertical lines are supported")

    def clear(self, state: bool | None = False):
        self._display = [[state for _ in range(self._width)] for _ in range(self._height)]

    def dump(self):
        """Print instance attributes, abbreviating large collections."""
        for name, value in vars(self).items():
            if isinstance(value, list) and value and isinstance(value[0], list):
                print(f"{name} = <{len(value)}x{len(value[0])} grid>")
            else:
                print(f"{name} = {value!r}")


class Visuals(Display):
    def __init__(self, rate: int, width: int = 20) -> None:
        self._height = 10  # 1 indexed
        self._width = width  # 1 indexed

        self._rate = rate
        self._bottom = self._height - 1  # 0 indexed
        self._columns = [0 for _ in range(self._width)]  # 0 indexed
        self._heights = [0 for _ in range(self._width)]  # 0 indexed

        super().__init__(self._height, self._width)

        for i in range(self._width):
            self.create_line(i, self._bottom, i, self._bottom, True)

    def column(self, x: int, height: int):
        self._columns[x] = height

    def random_columns(self, amount: int | None = None):
        if amount is None or not amount <= self._width:
            amount = self._width
        elif amount < 0:
            raise ValueError(f"Amount {amount} must be greater than 0")
        for _ in range(amount):
            column = randint(0, self._width - 1)
            height = randint(0, self._bottom)
            self.column(column, height)

    def render(self):
        self.clear(None)

        for column, height in enumerate(self._heights):
            self._heights[column] = max(self._heights[column] - 1, self._columns[column], 0)
            if self._heights[column] > self._bottom:
                raise ValueError(f"Height {self._heights[column]} is greater than bottom {self._bottom}")

            self.create_line(column, self._bottom, column, self._bottom - height, False)

        for column, height in enumerate(self._columns):
            self._columns[column] = max(self._columns[column] - 2, 0)
            self.create_line(column, self._bottom - height, column, self._bottom, True)

        super().render()


v = Visuals(10)
v.set_mode(False, on="█", off="░", dim=" ")

last_time = time()
while True:
    if input():
        break

    if time() - last_time > 0.1:
        v.random_columns(randint(4, 7))
        last_time = time()
    v.render()
    sleep(0.1)

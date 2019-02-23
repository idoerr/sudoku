
from typing import List
from kivy.graphics import Color, Rectangle
from kivy.uix.gridlayout import GridLayout
import math

from model.cell import Cell
from model.action import *
from gui.texture_util import *


# NOTE: a different parent class may be applicable, but using do_layout method for drawing.
class CellView(GridLayout):

    __cell: Cell = None
    __actions: List[Action] = []

    __black = (0, 0, 0, 1)
    __grey = (0.4, 0.4, 0.4, 1)
    __red = (1, 0, 0, 1)
    __green = (0, 1, 0, 1)

    def __init__(self, max_val: int, x: int, y: int, **kwargs):
        super(CellView, self).__init__(**kwargs)

        self.set_cell(Cell(max_val, x, y))

    def set_cell(self, cell: Cell) -> None:
        if self.__cell is not None and self.__cell.max_val() != cell.max_val():
            raise ValueError("GUICell cannot adapt to different sizes of puzzles!")

        self.__actions.clear()

        if self.__cell == cell:
            return

        self.__cell = cell
        # Trigger a re-draw of the cell
        self._trigger_layout()

    def get_cell(self):
        return self.__cell

    def add_draw_action(self, action):
        self.__actions.append(action)

        self._trigger_layout()

    def __display_text(self, x: int, y: int, width: int, height: int, text: str, draw_color):
        num_texture = get_text_texture(width, height, text)

        # Make sure to center the letter.
        x_offset = (width - num_texture.width) / 2
        y_offset = (height - num_texture.height) / 2
        draw_pos = (x + x_offset, y + y_offset)

        with self.canvas:
            Color(*draw_color)
            Rectangle(pos=draw_pos, size=num_texture.size, texture=num_texture)

    def __draw_possible_val(self, val: int, draw_color):
        sqrt_max = self.__cell.max_sqrt()
        cell_size = math.floor(self.width / sqrt_max)

        # We don't want the lettering to be too small, so don't draw possible values if the space is too small.
        if cell_size < 8:
            return

        row = sqrt_max - 1 - math.floor((val-1) / sqrt_max)
        col = (val-1) % sqrt_max

        draw_x = self.x + cell_size * col
        draw_y = self.y + cell_size * row

        self.__display_text(draw_x, draw_y, cell_size, cell_size, Cell.val_to_chr(val), draw_color)

    def __draw_action(self, action: Action):

        draw_color = self.__green

        if action.__class__ == ClearAction or action.__class__ == ClearPossibleAction:
            draw_color = self.__red

        if action.__class__ == SetPossibleAction or action.__class__ == ClearPossibleAction:
            self.__draw_possible_val(action.value(), draw_color)
        else:
            self.__display_text(self.x, self.y, self.width, self.width, action.value(), draw_color)

    def do_layout(self, *args):
        # Draw a grey background if this is an initial part of the puzzle.
        if self.__cell.is_initial():
            self.canvas.before.clear()
            with self.canvas.before:
                Color(*self.__grey)

                Rectangle(pos=self.pos, size=self.size)

        self.canvas.clear()

        if self.__cell.value() is not None:
            self.__display_text(self.x, self.y, self.width, self.height, self.__cell.display_value(), self.__black)
        else:
            for val in self.__cell.possible_vals():
                self.__draw_possible_val(val, self.__black)

        for action in self.__actions:
            self.__draw_action(action)

        super(CellView, self).do_layout(*args)

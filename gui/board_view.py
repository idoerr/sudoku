
from kivy.graphics import Color, Line
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty

from gui.cell_view import CellView
from model import board as board_func
from typing import List
import math


class BoardView(FloatLayout):

    __board: board_func.Board
    __gui_cells: List[List[CellView]]

    __rows: NumericProperty
    __cols: NumericProperty

    __padding_size: int
    __line_weight: float
    __heavy_weight: float

    def __init__(self, board: board_func.Board, **kwargs):
        super(BoardView, self).__init__(**kwargs)

        self.__padding_size = 2
        self.__line_weight = 1.5
        self.__heavy_weight = 2.5

        self.__board = board
        max_val = self.__board.max_val()

        self.__rows = NumericProperty(max_val)
        self.__cols = NumericProperty(max_val)

        # Initialize the grid of cells.
        self.__gui_cells = []
        for x in range(max_val):
            row_cells = []
            self.__gui_cells.append(row_cells)
            for y in range(max_val):
                gui_cell = CellView(max_val, x, y)
                self.add_widget(gui_cell)
                row_cells.append(gui_cell)

        self.set_board(board)

    def set_board(self, board: board_func.Board) -> None:

        if self.__board.max_val() != board.max_val():
            raise ValueError("GUIBoard cannot adjust to different-sized boards!")

        self.__board = board

        # The GUI board owns the GUI cells
        for x in range(board.max_val()):
            for y in range(board.max_val()):
                board_cell = board.get_cell(x, y)
                self.__gui_cells[x][y].set_cell(board_cell)

    def __get_cell_size(self):
        square_size = (min(self.size) - 2 * self.__padding_size) / self.__board.max_val()

        return square_size

    def on_touch_down(self, touch):

        # This code determines which cell was clicked on.
        top = self.y + self.height - self.__padding_size

        # Note: Kivy counts pixels from bottom-left corner, and we
        # order cells from the top-left, so need to convert coordinates.
        offset_x = touch.x - self.x - self.__padding_size
        offset_y = top - touch.y

        square_size = self.__get_cell_size()

        cell_col = math.floor(offset_x / square_size)
        cell_row = math.floor(offset_y / square_size)

        # Out of bounds checking.
        if cell_col < 0 or cell_col >= self.__board.max_val():
            return

        if cell_row < 0 or cell_row >= self.__board.max_val():
            return

        gui_cell = self.__gui_cells[cell_row][cell_col]
        cell = gui_cell.get_cell()

        # TODO:  Handle press

    def do_layout(self, *args):
        padding_size = 2
        line_weight = 1.5 # Normal cell intersections.
        heavy_weight = 2.5 # For quadrant intersections, and outline.
        square_size = self.__get_cell_size()
        max_square_size = square_size * self.__board.max_val()

        top = self.y + self.height - padding_size
        right = self.x + padding_size + max_square_size

        x_hint = square_size / self.width
        y_hint = square_size / self.height

        # resize and relocate the child cells
        for row, row_cells in enumerate(self.__gui_cells):
            for col, cell in enumerate(row_cells):
                cell.size_hint = (x_hint,y_hint)

                cell.pos = (
                    self.x + padding_size + col * square_size,
                    top - (row + 1) * square_size
                )

        max_sqrt = self.__board.max_sqrt()

        # draw the visible lines
        self.canvas.after.clear()
        with self.canvas.after:
            Color(0, 0, 0, 1)
            for i in range(self.__board.max_val() + 1): # Want to draw a line after the board as well.
                if i % max_sqrt == 0:
                    cur_weight = heavy_weight
                else:
                    cur_weight = line_weight

                # Horizontal Line
                Line(points=[
                    self.x + padding_size,
                    top - i * square_size,
                    right,
                    top - i * square_size
                ], width=cur_weight)

                # Vertical Line
                Line(points=[
                    self.x + padding_size + i * square_size,
                    top,
                    self.x + padding_size + i * square_size,
                    top - max_square_size
                ], width=cur_weight)

        super(BoardView, self).do_layout(*args)


from kivy.graphics import Color, Line
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty

from gui.cell_view import CellView
from model import board as board_func
from typing import List


class BoardView(FloatLayout):

    __board: board_func.Board
    __gui_cells: List[List[CellView]]

    __rows: NumericProperty
    __cols: NumericProperty

    def __init__(self, board: board_func.Board, **kwargs):
        super(BoardView, self).__init__(**kwargs)

        self.__board = board
        max_val = self.__board.max_val()

        self.__rows = NumericProperty(max_val)
        self.__cols = NumericProperty(max_val)

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

        for x in range(board.max_val()):
            for y in range(board.max_val()):
                board_cell = board.get_cell(x, y)
                self.__gui_cells[x][y].set_cell(board_cell)

    def do_layout(self, *args):
        padding_size = 2
        line_weight = 1.5
        heavy_weight = 2.5
        square_size = (min(self.size) - 2 * padding_size) / self.__board.max_val()
        max_square_size = square_size * self.__board.max_val()

        top = self.y + self.height - padding_size
        right = self.x + padding_size + max_square_size

        x_hint = square_size / self.width
        y_hint = square_size / self.height

        # resize the child cells
        for row in range(self.__board.max_val()):
            for col in range(self.__board.max_val()):
                cell = self.__gui_cells[row][col]
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
            for i in range(self.__board.max_val() + 1):
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

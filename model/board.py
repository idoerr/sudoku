
from __future__ import annotations
from typing import List, Set, Tuple
import math


# NOTE:  Pre-declaring the name here to fix circular dependency
class Board:
    pass


from .cell import Cell
from .action import Action, InitialSetAction


class Board:

    __max_val: int = None
    __max_sqrt: int = None
    __board: List[List[Cell]] = None
    __is_locked: bool = True

    def __init__(self, max_val: int, init_board: bool=True):
        if max_val <=1:
            raise ValueError("max_val is <= 1!")
        elif max_val != 2 and not math.sqrt(max_val).is_integer():
            raise ValueError("max_val is not a square integer!")

        self.__max_val = max_val
        self.__max_sqrt = math.floor(math.sqrt(max_val))

        if init_board:
            self.__board = []
            for i in range(max_val):
                cur_row = []
                self.__board.append(cur_row)
                for j in range(max_val):
                    cur_row.append(Cell(max_val, i, j))

    def display_board(self) -> List[List[str]]:

        ret_board = []
        for i in range(self.__max_val):
            ret_row = []
            ret_board.append(ret_row)
            board_row = self.__board[i]

            for j in range(self.__max_val):
                ret_row.append(board_row[j].display_value())

        return ret_board

    def get_cell(self, x: int, y: int) -> Cell:
        return self.__board[x][y]

    def set_cell(self, cell: Cell):
        if self.__is_locked:
            raise PermissionError("Cannot modify a board once it is locked!")

        self.__board[cell.x()][cell.y()] = cell

    def row_cells(self, x: int, filter_filled=False) -> Set[Cell]:
        if filter_filled:
            return set(cell for cell in self.__board[x] if cell.value() is None)
        else:
            return set(self.__board[x])

    def col_cells(self, y: int, filter_filled=False) -> Set[Cell]:
        if filter_filled:
            return set(row[y] for row in self.__board if row[y].value() is None)
        else:
            return set(row[y] for row in self.__board)

    def quadrant_cells(self, x: int, y: int, filter_filled=False) -> Set[Cell]:
        sqrt_max = math.floor(math.sqrt(self.__max_val))

        # Find out the starting indexes for the quadrant
        # since we are zero-indexed, quadrants start at 0, sqrt_max, 2 * sqrt_max, etc.
        # Removing the remainder from the input indexes effectively rounds the numbers.
        row_min = x - x % sqrt_max
        col_min = y - y % sqrt_max

        ret_arr = set()
        for row in range(row_min, row_min + sqrt_max):
            for col in range(col_min, col_min + sqrt_max):
                cell = self.__board[row][col]
                if filter_filled:
                    if cell.value() is None:
                        ret_arr.add(cell)
                else:
                    ret_arr.add(self.__board[row][col])

        return ret_arr

    def linked_cells(self, x: int, y: int, filter_filled=False) -> Set[Cell]:
        return self.row_cells(x, filter_filled)\
            .union(self.col_cells(y, filter_filled))\
            .union(self.quadrant_cells(x, y, filter_filled))

    def all_cells(self, filter_filled: bool = False) -> List[Cell]:
        ret_arr = []

        if filter_filled:
            for row in self.__board:
                for cell in row:
                    if cell.value() is None:
                        ret_arr.add(cell)
        else:
            for row in self.__board:
                ret_arr.extend(row)

        return ret_arr

    def min_poss_cell(self):

        min_cell_poss_count = -1
        min_cell = None

        for row in self.__board:
            for cell in row:
                if cell.value() is None:
                    cell_poss_count = cell.possible_count()

                    if min_cell is None:
                        min_cell = cell
                        min_cell_poss_count = cell_poss_count
                    elif cell_poss_count < min_cell_poss_count:
                        min_cell = cell
                        min_cell_poss_count = cell_poss_count

        return min_cell

    def is_solved(self):
        for row in self.__board:
            for cell in row:
                if cell.value() is None:
                    return False
        return True

    def is_invalid(self):
        for row in self.__board:
            for cell in row:
                if cell.possible_count() == 0:
                    return True

        return False

    def max_val(self) -> int:
        return self.__max_val

    def max_sqrt(self) -> int:
        return self.__max_sqrt

    def apply_actions(self, actions: List[Action]) -> Board:
        ret_board = Board(self.__max_val, False)
        ret_board.__board = [row[:] for row in self.__board]
        ret_board.__is_locked = False

        for act in actions:
            act.apply_action(ret_board)

        ret_board.__is_locked = True

        return ret_board

    def __str__(self):

        result_str = ''

        for row in self.__board:
            for cell in row:
                if cell.value() is None:
                    result_str += '0'
                else:
                    result_str += cell.display_value()
            result_str += ','

        return result_str


def create_board_from_values(max_val: int, board: List[List[int]] = None) -> Tuple[Board, List[InitialSetAction]]:
    empty_board = Board(max_val)
    init_actions = []

    if board is not None:

        for x in range(max_val):
            cur_row = board[x]
            for y in range(max_val):
                cur_cell = cur_row[y]

                if cur_cell is not None:
                    act = InitialSetAction(x, y, cur_cell)
                    init_actions.append(act)

    filled_board = empty_board.apply_actions(init_actions)

    return filled_board, init_actions


def create_board_from_string(board: str) -> Tuple[Board, List[InitialSetAction]]:

    board = board.replace(',', '')

    row_len = math.floor(math.sqrt(len(board)))
    board_arr = []
    cur_row = None

    for i in range(len(board)):
        if i % row_len == 0:
            cur_row = []
            board_arr.append(cur_row)

        letter = board[i]

        cur_row.append(Cell.chr_to_val(letter))

    return create_board_from_values(row_len, board_arr)

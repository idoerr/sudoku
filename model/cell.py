
from __future__ import annotations
import copy
import math
from typing import List, Set

from .board import Board


class Cell:

    __max_val: int = None
    __max_sqrt: int
    __x: int
    __y: int
    __value: int = None
    __poss_vals: Set[int] = None
    __is_initial: bool

    def __init__(self, max_val: int, x: int, y: int, cur_val: int = None, poss_vals: Set[int] = None, is_initial: bool = False):

        # Parameter Validation
        if max_val is None or max_val <= 1:
            raise ValueError("max_val was None or <= 1")
        elif max_val != 2 and not math.sqrt(max_val).is_integer():
            raise ValueError("max_val is not a square integer!")

        if x is None or x < 0 or x >= max_val:
            raise ValueError("x must be set and 0 <= x < max_val.")

        if y is None or y < 0 or y >= max_val:
            raise ValueError("y must be set and 0 <= y < max_val.")

        if cur_val is not None and poss_vals is not None:
            raise ValueError("Only one of cur_val and poss_vals can be set!")

        if is_initial and cur_val is None:
            raise ValueError("If is_initial is set, then cur_val needs to have a value as well!")

        # Basic Set of values
        self.__max_val = max_val
        self.__max_sqrt = math.floor(math.sqrt(max_val))
        self.__x = x
        self.__y = y

        self.__is_initial = is_initial

        if cur_val is not None:
            if cur_val < 1:
                raise ValueError("cur_val is less than 1!")
            elif cur_val > max_val:
                raise ValueError("cur_val is greater than max_val")
            self.__value = cur_val

            return

        if poss_vals is None:
            self.__poss_vals = set(x + 1 for x in range(max_val))
        else:
            for x in poss_vals:
                if x < 1:
                    raise ValueError("poss_vals contained a number less than 1")
                elif x > max_val:
                    raise ValueError("poss_vals contained a number greater than max_val")

            self.__poss_vals = poss_vals

    def value(self) -> int:
        return self.__value

    def x(self) -> int:
        return self.__x

    def y(self) -> int:
        return self.__y

    def max_val(self) -> int:
        return self.__max_val

    def max_sqrt(self) -> int:
        return self.__max_sqrt

    def is_initial(self) -> bool:
        return self.__is_initial

    @staticmethod
    def val_to_chr(value) -> str:
        if value is None:
            return ""
        elif value > 36:
            raise NotImplemented("Values > 36 are currently not supported")
        elif value >= 10:
            return chr(ord('A') + value - 10)
        else:
            return chr(ord('0') + value)

    @staticmethod
    def chr_to_val(char: str) -> int:
        chr_val = ord(char)
        if chr_val == ord('0'):
            return None
        elif ord('0') < chr_val <= ord('9'):
            return chr_val - ord('0')
        elif ord('A') <= chr_val <= ord('Z'):
            return chr_val - ord('A') + 10
        elif ord('a') <= chr_val <= ord('z'):
            return chr_val - ord('a') + 10
        else:
            raise NotImplemented("Values > 36 are currently not supported")

    def display_value(self) -> str:
        return self.val_to_chr(self.__value)

    def possible_vals(self) -> Set[int]:
        return self.__poss_vals.copy()

    def display_possible_vals(self) -> List[str]:
        return [self.val_to_chr(x) for x in self.__poss_vals]

    def possible_count(self) -> int:
        if self.__value is not None:
            return -1

        return len(self.__poss_vals)

    def __repr__(self) -> str:
        ret_str = "Cell(%d): (%d,%d) " % (self.__max_val, self.__x, self.__y)
        if self.__value is not None:
            ret_str += "value: " + str(self.__value)
        else:
            ret_str += "possibilities: " + str(self.__poss_vals)

        return ret_str

    def set_value(self, value: int, is_initial: bool=False) -> Cell:
        if self.__is_initial:
            raise ValueError("Cannot modify an initial Cell!")

        if self.__value == value:
            return self

        return Cell(self.__max_val, self.__x, self.__y, is_initial=is_initial, cur_val=value)

    def clear_value(self, board: Board) -> Cell:
        if self.__is_initial:
            raise ValueError("Cannot modify an initial Cell!")

        new_cell = Cell(self.__max_val, self.__x, self.__y)

        return new_cell.calc_possible_values(board)

    def set_possible_value(self, value: int) -> Cell:
        if self.__is_initial:
            raise ValueError("Cannot modify an initial Cell!")

        if self.__value is not None:
            return self

        if value in self.__poss_vals:
            return self

        new_cell = copy.deepcopy(self)
        new_cell.__poss_vals.add(value)

        return new_cell

    def clear_possible_value(self, value: int) -> Cell:
        if self.__is_initial:
            raise ValueError("Cannot modify an initial Cell!")

        if self.__value is not None:
            return self

        if value not in self.__poss_vals:
            return self

        new_cell = copy.deepcopy(self)
        new_cell.__poss_vals.remove(value)

        return new_cell

    def calc_possible_values(self, board: Board) -> Cell:
        if self.__is_initial:
            raise ValueError("Cannot modify an initial Cell!")

        if self.__value is not None:
            return self

        link_cells = board.linked_cells(self.__x, self.__y)
        link_cells.remove(self)

        new_poss = set(x + 1 for x in range(self.__max_val))

        for cell in link_cells:
            val = cell.value()
            if val is not None:
                new_poss.remove(val)

        new_cell = Cell(self.__max_val, self.__x, self.__y, poss_vals=new_poss)

        return new_cell

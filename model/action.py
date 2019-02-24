
from abc import ABC, abstractmethod
from model.cell import Cell

from model.board import Board


class Action(ABC):

    _x: int
    _y: int
    _value: int

    def __init__(self, x: int, y: int, value: int):
        self._x = x
        self._y = y
        self._value = value

    def x(self):
        return self._x

    def y(self):
        return self._y

    def value(self):
        return self._value

    @abstractmethod
    def apply_action(self, board: Board):
        pass

    def __repr__(self):
        return "%s (%d,%d): %d" % (self.__class__.__name__, self._x, self._y, self._value)


def _clear_possible_action(board: Board, mod_cell: Cell, value: int):
    if mod_cell.is_initial():
        return

    if mod_cell.value() is not None:
        return

    if mod_cell.has_possible_val(value):
        new_cell = mod_cell.clear_possible_value(value)
        board.set_cell(new_cell)


class SetAction(Action):

    _initial: bool

    def __init__(self, x: int, y: int, value: int):
        super().__init__(x, y, value)
        self._initial = False

    def apply_action(self, board: Board):
        mod_cell = board.get_cell(self.x(), self.y())
        if mod_cell.is_initial():
            return

        new_cell = mod_cell.set_value(self._value, self._initial)
        board.set_cell(new_cell)

        link_cells = board.linked_cells(mod_cell.x(), mod_cell.y())
        link_cells.remove(new_cell)

        for cell in link_cells:
            _clear_possible_action(board, cell, self._value)


class InitialSetAction(SetAction):

    def __init__(self, x: int, y: int, value: int):
        super().__init__(x, y, value)
        self._initial = True


class ClearAction(Action):

    def __init__(self, x: int, y: int, value: int):
        super().__init__(x, y, value)

    def apply_action(self, board: Board):
        mod_cell = board.get_cell(self.x(), self.y())
        if mod_cell.is_initial():
            return

        if mod_cell.value() is None:
            return

        new_cell = mod_cell.clear_value(board)

        board.set_cell(new_cell)


class SetPossibleAction(Action):

    def __init__(self, x: int, y: int, value: int):
        super().__init__(x, y, value)

    def apply_action(self, board: Board):
        mod_cell = board.get_cell(self.x(), self.y())
        if mod_cell.is_initial():
            return

        new_cell = mod_cell.set_possible_value(self._value)

        if mod_cell == new_cell:
            return

        board.set_cell(new_cell)

    def __repr__(self) -> str:
        return "SetPossibleAction (%d,%d): %d" % (self._x, self._y, self._value)


class ClearPossibleAction(Action):

    def __init__(self, x: int, y: int, value: int):
        super().__init__(x, y, value)

    def apply_action(self, board: Board):
        mod_cell = board.get_cell(self.x(), self.y())
        if mod_cell.is_initial():
            return

        new_cell = mod_cell.clear_possible_value(self._value)

        board.set_cell(new_cell)

    def __repr__(self) -> str:
        return "ClearPossibleAction (%d,%d): %d" % (self._x, self._y, self._value)

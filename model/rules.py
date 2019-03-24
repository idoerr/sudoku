
import itertools
from typing import List, Set, Tuple

from model.action import *
from model.board import Board
from model.cell import Cell

# Each of these rules are methods of determining which values should be put into
# Cells in a Sudoku board.  The rules are guaranteed to be correct, and unique.
# Rules generate a list of values to be added to the board,
# or a list of possible values to be eliminated from contention.
# Returns ( List of actions to take )


# This rule check for cells that only have one possible value
# NOTE:  There is an issue where invalid puzzles will attempt
# to set two adjacent cells to the same value, because the number
# is the only possible number for both cells.
def rule_one_possible(board: Board) -> List[Action]:

    action_arr = []

    for cell in board.all_cells():
        if cell.possible_count() == 1:
            for result_val in cell.possible_vals():
                action_arr.append(SetAction(cell.x(), cell.y(), result_val))

    return action_arr


# This set of rules checks to see if there is only one possible location
# for a value in a set of cells. IE:  If there is only one spot for 1 to be placed in a row.
# This rule applies for rows, columns, and quadrants.
def _rule_exclusive_set(cell_list: Set[Cell]) -> List[Action]:

    ret_arr = []

    for cell in cell_list:
        cur_cell_poss = cell.possible_vals()

        for poss_cell in cell_list:

            if cell == poss_cell:
                continue

            if len(cur_cell_poss) == 0:
                break

            temp_poss = poss_cell.possible_vals()

            cur_cell_poss = cur_cell_poss.difference(temp_poss)

        if len(cur_cell_poss) == 1:
            for result_val in cur_cell_poss:
                ret_arr.append(SetAction(cell.x(), cell.y(), result_val))

    return ret_arr


def rule_row_exclusive(board: Board) -> List[Action]:

    action_arr = []

    for x in range(board.max_val()):
        cur_row = board.row_cells(x, True)

        action_arr.extend(_rule_exclusive_set(cur_row))

    return action_arr


def rule_col_exclusive(board: Board) -> List[Action]:

    action_arr = []

    for y in range(board.max_val()):
        cur_col = board.col_cells(y, True)

        action_arr.extend(_rule_exclusive_set(cur_col))

    return action_arr


def rule_quadrant_exclusive(board: Board) -> List[Action]:

    action_arr = []

    max_val = board.max_val()
    max_sqrt = board.max_sqrt()

    for quadrant_x in range(0, max_val, max_sqrt):

        for quadrant_y in range(0, max_val, max_sqrt):

            quadrant_cells = board.quadrant_cells(quadrant_x, quadrant_y, True)

            action_arr.extend(_rule_exclusive_set(quadrant_cells))

    return action_arr


def _quadrant_col_cell_elim_helper(quadrant_cells: Set[Cell], col_cells: Set[Cell]) -> List[Action]:

    action_arr = []

    intersection_cells = quadrant_cells.intersection(col_cells)
    quadrant_exclusive_cells = quadrant_cells.difference(col_cells)
    column_exclusive_cells = col_cells.difference(quadrant_cells)

    column_elim = set()
    for cell in intersection_cells:
        column_elim = column_elim.union(cell.possible_vals())

    for cell in quadrant_exclusive_cells:
        column_elim = column_elim.difference(cell.possible_vals())

    for cell in column_exclusive_cells:
        cur_cell_elim = cell.possible_vals().intersection(column_elim)

        for elim_val in cur_cell_elim:
            action_arr.append(ClearPossibleAction(cell.x(), cell.y(), elim_val))

    return action_arr


# This rule is a bit more complicated, and ONLY affects possible values
# Sometimes you get a quadrant filled out like this (X = filled, p = possible)
#
# XXp
# XX
# XXp
#
# What we would like to in this case, is remove the possible value from the other
# quadrants in the p column.  We know this is safe, because the value MUST be in
# one of those two positions outlined, so we can eliminate the possible value from
# the remainder of the column.  This rule attempts to do this for both rows and columns.
def rule_quadrant_col_and_row_elim_possible(board: Board) -> List[Action]:

    action_arr = []

    max_val = board.max_val()
    max_sqrt = board.max_sqrt()

    for quadrant_x in range(0, max_val, max_sqrt):

        for quadrant_y in range(0, max_val, max_sqrt):

            quadrant_cells = board.quadrant_cells(quadrant_x, quadrant_y, True)
            if len(quadrant_cells) == 0:
                continue

            for col_y in range(quadrant_y, quadrant_y + max_sqrt):
                col_cells = board.col_cells(col_y, True)
                if len(col_cells) == 0:
                    continue

                action_arr.extend(_quadrant_col_cell_elim_helper(quadrant_cells, col_cells))

            for row_x in range(quadrant_x, quadrant_x + max_sqrt):
                row_cells = board.row_cells(row_x, True)
                if len(row_cells) == 0:
                    continue

                action_arr.extend(_quadrant_col_cell_elim_helper(quadrant_cells, row_cells))

    return action_arr


# This rule is an extension of the only 1 possible location for a cell rule.
# If two values can only be located in two spots, then we know those cells must exclusively
# contain those two values.  We can use this knowledge to eliminate other possible values within
# these cells.  This principle can be expanded to larger sets of cells.
def _combination_exclusive_rule_helper(cells: Set[Cell]) -> List[Action]:

    action_arr = []

    remove_cells = set()

    for cell_com in itertools.combinations(cells, 2):
        union_poss = set()

        for cell in cell_com:
            union_poss = union_poss.union(cell.possible_vals())

        if len(union_poss) == len(cell_com):
            remove_cells = remove_cells.union(cell_com)
            other_cells = cells.difference(cell_com)

            for mod_cell in other_cells:
                mod_poss = mod_cell.possible_vals()

                for val in union_poss:
                    if val in mod_poss:
                        action_arr.append(ClearPossibleAction(mod_cell.x(), mod_cell.y(), val))

    return action_arr


def combination_exclusive_rowcol_rule(board: Board) -> List[Action]:

    action_arr = []

    for x in range(board.max_val()):
        cur_row = board.row_cells(x, True)

        action_arr.extend(_combination_exclusive_rule_helper(cur_row))

    for y in range(board.max_val()):
        cur_col = board.col_cells(y, True)

        action_arr.extend(_combination_exclusive_rule_helper(cur_col))

    return action_arr


def combination_exclusive_quadrant_rule(board: Board) -> List[Action]:

    action_arr = []

    max_val =  board.max_val()
    max_sqrt = board.max_sqrt()

    for quadrant_x in range(0, max_val, max_sqrt):
        for quadrant_y in range(0, max_val, max_sqrt):
            quadrant_cells = board.quadrant_cells(quadrant_x, quadrant_y, True)

            action_arr.extend(_combination_exclusive_rule_helper(quadrant_cells))

    return action_arr


rule_set = [
    rule_one_possible,
    rule_row_exclusive,
    rule_col_exclusive,
    rule_quadrant_exclusive,
    #rule_quadrant_col_and_row_elim_possible,
    #combination_exclusive_rowcol_rule,
    #combination_exclusive_quadrant_rule
]
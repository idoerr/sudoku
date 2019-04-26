
from __future__ import annotations
from typing import Set, Tuple, List
from enum import Enum
import itertools
import math
from model.cell import Cell
import numpy as np
import scipy.sparse as spsp


class ConstraintType(Enum):
    RowCol = 0  # Constraint that the overlapping row and column numbers have the same value
    RowNum = 1  # Constraint that each row number is unique
    ColNum = 2  # Constraint that each col number is unique
    QuadNum = 3  # Constraint the each number in a quadrant is unique


class DictAlgorithmXBoard:

    def __init__(self, max_val: int, constraint_matrix = None, selected_rows: List[int] = None):

        self.__max_val = max_val
        self.__max_square = max_val * max_val
        self.__max_sqrt = 1 if max_val == 2 else math.sqrt(max_val)

        if constraint_matrix is None:

            row_indexes = np.repeat(range(self.row_count()), 5)
            col_indexes = []
            value_list = []

            ones_list = [1,1,1,1]
            for i in range(1, self.row_count() + 1):
                value_list.append(i)
                value_list.extend(ones_list)

            for row, col, poss_val in itertools.product(range(max_val), range(max_val), range(max_val)):

                col_indexes.append(0)

                # RowCol Constraint
                col_offset = row * max_val + col
                col_index = 1 + ConstraintType.RowCol.value * self.__max_square + col_offset
                col_indexes.append(col_index)

                # RowNum Constraint
                col_offset = row * max_val + poss_val
                col_index = 1 + ConstraintType.RowNum.value * self.__max_square + col_offset
                col_indexes.append(col_index)

                # ColNum Constraint
                col_offset = col * max_val + poss_val
                col_index = 1 + ConstraintType.ColNum.value * self.__max_square + col_offset
                col_indexes.append(col_index)

                # QuadNum Constraint
                quad_num = self.__max_sqrt * (row // self.__max_sqrt) + col // self.__max_sqrt
                col_offset = int(quad_num) * max_val + poss_val
                col_index = 1 + ConstraintType.QuadNum.value * self.__max_square + col_offset
                col_indexes.append(col_index)

            value_list = np.array(value_list, dtype='i')
            constraint_coo = spsp.coo_matrix((value_list, (row_indexes, col_indexes)), dtype='i')
            constraint_csr = spsp.csr_matrix(constraint_coo)

            self.__constraint_matrix = constraint_csr
        else:
            self.__constraint_matrix = constraint_matrix

        if selected_rows is None:
            self.__selected_rows = []
        else:
            self.__selected_rows = selected_rows.copy()

    def row_count(self):
        return self.__max_val ** 3

    def col_count(self):
        return self.__max_val ** 2 * 4

    def row_for_coords(self, x: int, y: int, poss_val: int):
        return self.__max_square * x + self.__max_val * y + poss_val

    def col_for_constraint(self, x: int, y: int, constraint: ConstraintType):
        return self.__max_square * constraint.value + self.__max_sqrt * x + y

    def get_cell(self, x: int, y: int):

        start_index = 1 + self.row_for_coords(x, y, 0)

        for i, cur_index in enumerate(range(start_index, start_index + self.__max_val)):
            if cur_index in self.__selected_rows:
                return Cell(self.__max_val, x, y, i + 1)

        avail_indexes = self.__constraint_matrix.getcol(0).todense()

        end_index = start_index + self.__max_val

        avail_list = np.where((avail_indexes >= start_index) & (avail_indexes < end_index))

        poss_val_list = []
        for val in np.nditer(avail_indexes[avail_list]):
            poss_val_list.append(val - start_index + 1)

        return Cell(self.__max_val, x, y, poss_vals=frozenset(poss_val_list))

    def __str__(self):

        output_arr = []

        for row_num in sorted(self.__selected_rows):

            row_num -= 1

            str_index = row_num // self.__max_val
            while len(output_arr) < str_index:
                output_arr.append('0')

            poss_val = row_num % self.__max_val + 1

            output_arr.append(Cell.val_to_chr(poss_val))

        while len(output_arr) < self.__max_square:
            output_arr.append('0')

        return ''.join(output_arr)

    def set_value(self, x: int, y: int, value: int):

        row_index = self.row_for_coords(x, y, value)
        avail_rows = self.__constraint_matrix.getcol(0).todense()

        matrix_index = np.where(row_index == avail_rows)[0][0]

        self.__selected_rows.append(row_index)

        sub_matrix = _select_row_from_matrix(self.__constraint_matrix, matrix_index)

        self.__constraint_matrix = sub_matrix

    def solve(self):

        solution_generator = _solve_worker(self.__constraint_matrix, self.__selected_rows.copy())

        try:
            base_solution = next(solution_generator)
        except StopIteration:
            raise ValueError("Sudoku puzzle doesn't have a valid solution!")

        return base_solution


def _select_row_from_matrix(mod_matrix, row_to_select: int):

    del_cols = []
    del_rows = set()

    for row_ignore, col_to_delete in zip(*mod_matrix[row_to_select].nonzero()):

        if col_to_delete != 0:
            del_cols.append(col_to_delete)

    for row_to_delete, col_to_ignore in zip(*mod_matrix[:,del_cols].nonzero()):
        del_rows.add(row_to_delete)

    # del_rows = sorted(list(del_rows))

    keep_cols = [i for i in range(mod_matrix.shape[1]) if i not in del_cols]
    keep_rows = [i for i in range(mod_matrix.shape[0]) if i not in del_rows]

    sub_mat = mod_matrix[keep_rows,:][:,keep_cols]
    return sub_mat


def _solve_worker(mod_matrix, solution=[]):
    if mod_matrix.getnnz() == 0:
        yield(solution.copy())
    else:
        col_counts = list(mod_matrix.getnnz(0)[1:])

        min_col = col_counts.index(min(col_counts)) + 1

        for row_to_select, col_ignore in zip(*mod_matrix[:,min_col].nonzero()):

            row_orig_index = mod_matrix[row_to_select, 0]
            solution.append(row_orig_index)

            sub_matrix = _select_row_from_matrix(mod_matrix, row_to_select)

            for s in _solve_worker(sub_matrix, solution):
                yield(s)

            solution.pop()


if __name__ == '__main__':

    import time
    start = time.time()

    max_val = 4
    board = DictAlgorithmXBoard(max_val)

    board.set_value(0, 0, 4)
    board.set_value(2, 0, 2)

    print(board)

    print(board.get_cell(0, 0))
    print(board.get_cell(1, 0))

    solution = board.solve()
    print(len(solution))

    print(time.time() - start)

class Column_Head:

    col: int
    head_node: Node

class Node:

    row: int
    col: int
    colprev: Node
    colnext: Node
    rowprev: Node
    rownext: Node

    def __init__(self, row, col):
        self.row = row
        self.col = col

        self.colprev = None
        self.colnext = None

        self.rowprev = None
        self.rownext = None

    def col_attach(self):
        if self.colprev is None:
            raise RuntimeError("Attempted to attach when not originally linked up!")

        self.colprev.colnext = self
        self.colnext.colprev = self

    def col_deattach(self):
        if self.colprev is None:
            raise RuntimeError("Attempted to deattach when not originally linked up!")

        self.colprev.colnext = self.colnext
        self.colnext.colprev = self.colnext








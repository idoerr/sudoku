
from __future__ import annotations
from typing import Set, Tuple, List
from enum import Enum
import itertools
import math
from model.cell import Cell
import scipy.sparse as spsp

class ConstraintType(Enum):
    RowCol = 0  # Constraint that the overlapping row and column numbers have the same value
    RowNum = 1  # Constraint that each row number is unique
    ColNum = 2  # Constraint that each col number is unique
    QuadNum = 3  # Constraint the each number in a quadrant is unique


class DictAlgorithmXBoard:

    __selected_indexes: List[int]

    #__constraint_matrix: spsp.lilmat

    def row_count(self):
        return self.__max_val ** 3

    def col_count(self):
        return self.__max_val ** 2 * 4

    def row_for_coords(self, x: int, y: int, poss_val: int):
        return self.__max_square * x + self.__max_val * y + poss_val

    def col_for_constraint(self, x: int, y: int, constraint: ConstraintType):
        return self.__max_square * int(constraint) + self.__max_sqrt * x + y

    def get_cell(self, x: int, y: int):

        start_index = self.row_for_coords(x, y, 0)

        for i in range(self.__max_val):
            cur_index = start_index + i



    def __init__(self, max_val: int, constraint_matrix: Set[Tuple[int,int,int,int,int,ConstraintType]] = None, avail_rows: Set[Tuple[int,int,int]] = None, avail_cols: Set[Tuple[int,int,ConstraintType]] = None, selected_rows: Set[Tuple[int,int,int]] = None):

        self.__max_val = max_val
        self.__max_square = max_val * max_val
        self.__max_sqrt = 1 if max_val == 2 else math.sqrt(max_val)

        if constraint_matrix is None:
            constraint_matrix = set()
            self.c = constraint_matrix

            for row, col, poss_val in itertools.product(range(max_val), range(max_val), range(max_val)):
                constraint_matrix.add((row,col,poss_val,row,col, ConstraintType.RowCol))
                constraint_matrix.add((row,col,poss_val,row,poss_val,ConstraintType.RowNum))
                constraint_matrix.add((row,col,poss_val,col,poss_val,ConstraintType.ColNum))

                quad_num = self.__max_sqrt * (row // self.__max_sqrt) + col // self.__max_sqrt
                constraint_matrix.add((row,col,poss_val,quad_num,poss_val,ConstraintType.QuadNum))

        if avail_rows is None:
            avail_rows = set()

            for row,col,poss_val in itertools.product(range(max_val),range(max_val),range(max_val)):
                avail_rows.add((row,col,poss_val))

            self.__avail_rows = avail_rows
        else:
            self.__avail_rows = avail_rows.copy()

        if avail_cols is None:
            avail_cols = set()

            for row,col,constraint in itertools.product(range(max_val), range(max_val), ConstraintType):
                avail_cols.add((row,col,constraint))

            self.__avail_cols = avail_cols
        else:
            self.__avail_cols = avail_cols.copy()

        if selected_rows is None:
            self.__selected_rows = set()
        else:
            self.__selected_rows = selected_rows.copy()

    def get_cell(self, x: int, y: int) -> Cell:

        for poss_val in range(self.__max_val):
            if (x,y,poss_val) in self.__selected_rows:
                return Cell(self.__max_val, x, y, poss_val + 1)

        poss_val_list = []
        for poss_val in range(self.__max_val):
            if (x,y,poss_val) in self.__avail_rows:
                poss_val_list.append(poss_val + 1)

        return Cell(self.__max_val, x, y, poss_vals=frozenset(poss_val_list))


if __name__ == '__main__':

    max_val = 9
    links = DictAlgorithmXBoard(max_val)
    c = links.c

    top_row = "ROW     "
    top_col = "COL     "

    c_col = list(ConstraintType)

    for constraint, row, col in itertools.product([1,2,3,4], range(max_val), range(max_val)):
        if row == 0 and col == 0:
            top_row += "|"
            top_col += "|"

        if col == 0:
            top_row += str(row)
        else:
            top_row += " "

        top_col += str(col)

    print(top_row)
    print(top_col)

    for row,col, poss_val in itertools.product(range(max_val),range(max_val), range(max_val)):
        cur_row = "r" + str(row) +",c" + str(col) + "#" + str(poss_val) + " "
        for constraint,x,y in itertools.product(c_col, range(max_val),range(max_val)):
            if x == 0 and y == 0:
                cur_row += "|"
            if (row,col,poss_val,x,y,constraint) in c:
                cur_row += str(poss_val)
            else:
                cur_row += " "

        if poss_val == 0:
            print(" " * 8 + "_" * (len(c_col) * max_val * max_val + len(c_col)))
        print(cur_row)

    print(links.get_cell(4, 4))




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








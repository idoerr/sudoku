
from typing import Set, Tuple

class DancingBoard:

    # We are attempting to represent the board as a 4-dimensional

    __max_val: int
    __sudoku_hit_matrix: Set[Tuple[int, int, int, str]] # (x, y, poss_val, rule)
    __

    def __init__(self, max_val: int, init_struct: Set[Tuple[int, int, int, str]]=None, selected_rows: Set[Tuple[int, int, int]]=None, selected_cols: Set[Tuple[int, int, str]]=None):

        self.__max_val = max_val

        if init_struct is None:
            init_struct = set()

            for x, y, poss_val in itertools.product(range(max_val), range(max_val), range(max_val)):
                if x == y:
                    init_struct.add( (x,y,poss_val,''))

if __name__ == '__main__':

    DancingBoard(4)
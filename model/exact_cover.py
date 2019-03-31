
from typing import Tuple
import numpy as np

import scipy.sparse as spsp

def solve_lilmat(lil_mat, solution=[]):

    if lil_mat.getnnz() == 0:
        yield(list(solution))
    else:
        col_counts = list(lil_mat.getnnz(0)[1:])

        min_col = col_counts.index(min(col_counts)) + 1

        #print(lil_mat[:,min_col])
        for row_to_select, col_ignore in zip(*lil_mat[:,min_col].nonzero()):

            row_orig_index = lil_mat[row_to_select, 0]
            solution.append(row_orig_index)

            del_cols = []
            del_rows = set()

            for row_ignore, col_to_delete in zip(*lil_mat[row_to_select,:].nonzero()):

                if col_to_delete != 0:
                    del_cols.append(col_to_delete)

            for row_to_delete, col_to_ignore in zip(*lil_mat[:,del_cols].nonzero()):
                del_rows.add(row_to_delete)

            del_rows = sorted(list(del_rows))

            keep_cols = [i for i in range(lil_mat.shape[1]) if i not in del_cols]
            keep_rows = [i for i in range(lil_mat.shape[0]) if i not in del_rows]

            sub_mat = lil_mat[keep_rows,:][:,keep_cols]

            for s in solve_lilmat(sub_mat, solution):
                yield s

            solution.pop()
            #row_num = row_info[0]
            #print(row_num)
        #for row_num in lil_mat[:,min_col]:
        #    print(row_num)



def solve(X, Y, solution=[]):

    if not X:
        yield list(solution)
    else:
        # Each entry in X is a list of relevant rows.
        # Choose the constraint with the least number of rows.
        min_constraint = min(X, key=lambda c: len(X[c]))

        # We are going to modify X[c], so iterate over a copy of it.
        for row_ref in list(X[min_constraint]):

            solution.append(row_ref)
            cols = select(X, Y, row_ref)
            for s in solve(X, Y, solution):
                yield s
            deselect(X, Y, row_ref, cols)
            solution.pop()

def select(X, Y, r):
    cols = []

    for col_constraint in Y[r]:
        for row_ref in X[col_constraint]:
            for k in Y[row_ref]:
                if k != col_constraint:
                    X[k].remove(row_ref)
        cols.append(X.pop(col_constraint))

    return cols

def deselect(X, Y, r, cols):
    for j in reversed(Y[r]):
        X[j] = cols.pop()
        for i in X[j]:
            for k in Y[i]:
                if k != j:
                    X[k].add(i)

def create_indexes( list ):
    indexes = []
    lookup_dict = {}
    for i, x in enumerate(list):
        indexes.append(x)
        lookup_dict[x] = i

    return indexes, lookup_dict


if __name__ == '__main__':

    # This is the list of constraints
    X = {1,2,3,4,5,6,7}

    # This is the list rows, along with the constraints they satisfy.
    Y = {
        'A': [1,4,7],
        'B': [1,4],
        'C': [4,5,7],
        'D': [3,5,6],
        'E': [2,3,6,7],
        'F': [2,7]
    }

    X_indexes, X_dict = create_indexes(X)
    Y_indexes, Y_dict = create_indexes(Y)

    shape = (len(Y_indexes), len(X_indexes))
    mat = spsp.lil_matrix((len(Y_indexes), len(X_indexes) + 1), dtype='i')

    for y_ind, y_val in enumerate(Y_indexes):
        X_list = Y[y_val]
        mat[y_ind, 0] = y_ind + 1

        for x_val in X_list:
            x_ind = X_dict[x_val]

            mat[y_ind, x_ind + 1] = 1

    for x in solve_lilmat(mat):
        lookup_solution = [Y_indexes[i-1] for i in x]
        print(lookup_solution)

    print('---------------------------------')

    # First Initialize X_mod to have a list for each row value
    X_mod = { constraint:set() for constraint in X }

    for row_ref in Y:
        for constraint in Y[row_ref]:
            X_mod[constraint].add(row_ref)

    for x in solve(X_mod, Y):
        print(x)

    # spsp.lil_matrix()



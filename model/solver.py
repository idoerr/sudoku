#from model.action import SetAction
from model.rules import *
from typing import Optional
import random
import time

class Solver:

    __solve_single_step: bool
    __board_steps: List[Tuple[Board, str, List[Action]]]  # List (state, rule, action)
    __cur_board: Board

    def __init__(self, board: Board, initial_actions: List[Action], solve_single_step=True):
        self.__solve_single_step = solve_single_step
        self.__board_steps = [(board, "initial", initial_actions)]

        self.__cur_board = board

    def get_board(self, index: int = None) -> Board:
        if index is None:
            index = len(self.__board_steps) - 1

        board, rule, action = self.__board_steps[index]
        return board

    def get_rule(self, index: int = None) -> str:
        if index is None:
            index = len(self.__board_steps) - 1

        board, rule, action = self.__board_steps[index]
        return rule

    def get_action(self, index: int = None) -> List[Action]:
        if index is None:
            index = len(self.__board_steps) - 1

        board, rule, action = self.__board_steps[index]
        return action

    def __apply_actions(self, rule: str, cur_actions: List[Action]):

        if self.__solve_single_step:
            for act in cur_actions:
                list_act = [act]
                new_board = self.__cur_board.apply_actions(list_act)

                self.__board_steps.append((new_board, rule, list_act))
                self.__cur_board = new_board
        else:
            new_board = self.__cur_board.apply_actions(cur_actions)

            self.__board_steps.append((new_board, rule, cur_actions))
            self.__cur_board = new_board

    def solve(self):

        solve_steps = _solve_helper(self.__cur_board, False)

        for rule, actions in solve_steps:
            self.__apply_actions(rule, actions)

        return self.__cur_board.is_solved()

    def print_taken_steps(self):
        for board, rule, action_list in self.__board_steps:
            print(rule, action_list)


def _get_next_steps(board: Board) -> Tuple[str, List[Action]]:

    for rule in rule_set:
        rule_actions = rule(board)

        if len(rule_actions) > 0:
            return rule.__name__, rule_actions

    return "", []


def _random_initial_val(board: Board) -> InitialSetAction:

    max_val = board.max_val()

    while True:
        x = random.randint(0, max_val - 1)
        y = random.randint(0, max_val - 1)

        cell = board.get_cell(x, y)

        if cell.value() is None:
            poss_vals = list(cell.possible_vals())

            if len(poss_vals) == 1:
                index = 0
            else:
                index = random.randint(0, len(poss_vals) - 1)
            set_val = poss_vals[index]

            return InitialSetAction(x, y, set_val)

def _solve_helper(board: Board, check_unique: bool) -> List[Tuple[str, List[Action]]]:

    rule_action_list : List[Tuple[str, List[Action]]] = []

    start_time = time.time()

    while not board.is_solved():
        rule, next_actions = _get_next_steps(board)

        if len(next_actions) == 0:

            if board.is_invalid():
                return rule_action_list
            else:
                min_cell = board.min_poss_cell()

                poss_vals = min_cell.possible_vals()

                rule = "solver_try_value"
                actions_found = False

                #print(min_cell)

                for x in poss_vals:

                    if time.time() - start_time > 60:
                        break

                    next_action = [SetAction(min_cell.x(), min_cell.y(), x)]

                    next_board = board.apply_actions(next_action)

                    future_steps = _solve_helper(next_board, check_unique)

                    future_actions = []
                    for r, act in future_steps:
                        future_actions.extend(act)

                    future_board = next_board.apply_actions(future_actions)

                    if future_board.is_solved():

                        if check_unique and actions_found:
                            raise ValueError( "Board does not have a unique solution!!!" )

                        rule_action_list.append((rule, next_action))

                        rule_action_list.extend(future_steps)
                        actions_found = True

                        if not check_unique:
                            return rule_action_list

                return rule_action_list

        else:
            board = board.apply_actions(next_actions)

            rule_action_list.append( (rule, next_actions) )

    return rule_action_list


def generate(max_val: int) -> Optional[List[Action]]:

    # Online research suggests that the minimum number of filled spaces for a 9x9 sudoku board is 17.
    # Thus we are going to generate that many spaces before attempting the check for uniqueness.

    genboard = Board(max_val)
    initial_actions = []

    # First fill in 9 spots, before attempting to apply rules between generation.
    for i in range(max_val - 1):
        set_action = _random_initial_val(genboard)

        initial_actions.append(set_action)
        genboard = genboard.apply_actions([set_action])

    # Now generate up to 17 numbers, using rules between each step.
    for i in range(max_val):

        while True:
            rule, rule_actions = _get_next_steps(genboard)

            if len(rule_actions) > 0:
                genboard = genboard.apply_actions(rule_actions)
            else:
                break

        if genboard.is_solved():
            return initial_actions

        set_action = _random_initial_val(genboard)
        initial_actions.append(set_action)
        genboard = genboard.apply_actions([set_action])

    # Now we need to do a uniqueness check before each generation
    while True:

        print(len(initial_actions))
        print(','.join(''.join(x) for x in genboard.display_board()))

        while True:
            rule, rule_actions = _get_next_steps(genboard)

            if len(rule_actions) > 0:
                genboard = genboard.apply_actions(rule_actions)
            else:
                break

        try:
            result_rules = _solve_helper(genboard, True)
            check_board = genboard

            for rule, rule_actions in result_rules:
                check_board = check_board.apply_actions(rule_actions)

            if check_board.is_solved():
                return initial_actions

            if check_board.is_invalid():
                return None

        except ValueError:
            # This means that the puzzle does not have a unique solution
            pass

        set_action = _random_initial_val(genboard)
        initial_actions.append(set_action)
        genboard = genboard.apply_actions([set_action])

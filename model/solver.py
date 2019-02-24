#from model.action import SetAction
from model.rules import *


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

    def __get_next_steps(self, board) -> Tuple[str, List[Action]]:

        for rule in rule_set:
            rule_actions = rule(board)

            if len(rule_actions) > 0:
                return rule.__name__, rule_actions

        return "", []

    def __solve_helper(self, board: Board, check_unique: bool) -> List[Tuple[str, List[Action]]]:

        rule_action_list : List[Tuple[str, List[Action]]] = []

        while not board.is_solved():
            rule, next_actions = self.__get_next_steps(board)

            if len(next_actions) == 0:

                if board.is_invalid():
                    return rule_action_list
                else:
                    min_cell = board.min_poss_cell()

                    poss_vals = min_cell.possible_vals()

                    rule = "solver_try_value"
                    actions_found = False

                    for x in poss_vals:

                        next_action = [SetAction(min_cell.x(), min_cell.y(), x)]

                        next_board = board.apply_actions(next_action)

                        future_steps = self.__solve_helper(next_board, check_unique)

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

        solve_steps = self.__solve_helper(self.__cur_board, False)

        for rule, actions in solve_steps:
            self.__apply_actions(rule, actions)

        return self.__cur_board.is_solved()

    def print_taken_steps(self):
        for board, rule, action_list in self.__board_steps:
            print(rule, action_list)

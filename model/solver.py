from model.rules import *


class Solver:

    __solve_single_step: bool
    __board_steps: List[Tuple[Board, str, List[Action]]]  # List (state, rule, action)
    __cur_board: Board

    def __init__(self, board: Board, initial_actions: List[Action], solve_single_step=True):
        self.__solve_single_step = solve_single_step
        self.__board_steps = [(board, "initial", initial_actions)]

        self.__cur_board = board

    def get_board(self, index: int=None) -> Board:
        if index is None:
            index = len(self.__board_steps) - 1

        board, rule, action = self.__board_steps[index]
        return board

    def get_rule(self, index: int=None) -> str:
        if index is None:
            index = len(self.__board_steps) - 1

        board, rule, action = self.__board_steps[index]
        return rule

    def get_action(self, index: int=None) -> List[Action]:
        if index is None:
            index = len(self.__board_steps) - 1

        board, rule, action = self.__board_steps[index]
        return action

    def __get_next_steps(self) -> Tuple[str, List[Action]]:

        for rule in rule_set:
            rule_actions = rule(self.__cur_board)

            if len(rule_actions) > 0:
                return rule.__name__, rule_actions

        return "", []

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
        while not self.__cur_board.is_solved():
            rule, next_actions = self.__get_next_steps()

            if len(next_actions) == 0:
                return False

            self.__apply_actions(rule, next_actions)

        return True

    def print_taken_steps(self):
        for board, rule, action_list in self.__board_steps:
            print(rule, action_list)

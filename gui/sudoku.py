
from kivy.app import App
import time

from gui.board_view import BoardView
import model.board
from model.solver import Solver


class SudokuApp(App):

    def __init__(self, board_str: str):
        super().__init__()
        self.__board, self.__init_actions = model.board.create_board_from_string(board_str)

    def build(self):

        start = time.time()

        s = Solver(self.__board, self.__init_actions, False)

        #s.solve()

        board = s.get_board()

        end = time.time()

        print(end - start)

        s.print_taken_steps()

        return BoardView(self.__board)

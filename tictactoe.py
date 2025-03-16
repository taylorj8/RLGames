from typing import override
from readchar import readkey
import os
from game import Game


EMPTY = " "

def clear_screen():
    os.system('cls' if os.name=='nt' else 'clear')


class TicTacToe(Game):
    max_moves = 9
    start_instructions = "Welcome to TicTacToe! The game is played using the numpad. The numbers correspond to squares as follows:"

    def __init__(self, player1, player2, visualise):
        super().__init__(player1, player2, visualise)
        self.cells = [EMPTY] * 9
        self.guide = [str(i) for i in range(1, 10)]

    def cell_taken(self, index):
        return True if self.cells[index - 1] != EMPTY else False

    @override
    def place_token(self, index, player):
        self.cells[index - 1] = player
        self.guide[index - 1] = "■"

    @override
    def get_board(self, guide=None):
        c = self.cells if guide is None else guide
        return f"""    ╻   ╻
  {c[6]} ┃ {c[7]} ┃ {c[8]}
╺━━━╋━━━╋━━━╸
  {c[3]} ┃ {c[4]} ┃ {c[5]}
╺━━━╋━━━╋━━━╸
  {c[0]} ┃ {c[1]} ┃ {c[2]}
    ╹   ╹"""

    @override
    def check_win(self):
        def check_subset(subset):
            return subset[0] != EMPTY and all([x == subset[0] for x in subset])

        return check_subset(self.cells[:3]) or check_subset(self.cells[3:6]) or check_subset(self.cells[6:9]) or \
               check_subset([self.cells[0], self.cells[3], self.cells[6]]) or check_subset([self.cells[1], self.cells[4], self.cells[7]]) or \
               check_subset([self.cells[2], self.cells[5], self.cells[8]]) or check_subset([self.cells[0], self.cells[4], self.cells[8]]) or \
               check_subset([self.cells[2], self.cells[4], self.cells[6]])

    @override
    def human_choose_move(self, token):
        while True:
            print(f"Player {token}, choose a cell:\n{self.get_board()}")
            key = readkey()
            if key.isdigit() and key != "0":
                cell = int(key)
                if not self.cell_taken(cell):
                    return cell

            clear_screen()
            print(f"Enter one of the following keys:\n{self.get_board(self.guide)}\nPlease choose an empty cell.")
            readkey()
            clear_screen()

    @override
    def algorithm_choose_move(self, token):
        # TODO
        pass

    @override
    def minimax_choose_move(self, token):
        # TODO
        pass

    @override
    def qlearning_choose_move(self, token):
        # TODO
        pass

    @staticmethod
    @override
    def get_tokens():
        return "X", "O"


if __name__ == "__main__":
    TicTacToe.start()
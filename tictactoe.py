import random
import time
from typing import override
from readchar import readkey
from game import Game, clear_screen

BLANK = " "

def check_subset(subset, token=None):
    if token is None:
        return subset[0] != BLANK and all([x == subset[0] for x in subset])
    return all([x == token for x in subset])


class TicTacToe(Game):
    max_moves = 9
    start_instructions = "Welcome to TicTacToe! The game is played using the numpad. The numbers correspond to squares as follows:"
    winning_subsets = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]

    def __init__(self, player1, player2, visualise, max_depth=9, q_table=None):
        super().__init__(player1, player2, visualise, max_depth, q_table)
        self.cells = [BLANK] * 9
        self.remaining_cells = [i for i in range(1, 10)]

    @override
    def reset(self, initial_token=0):
        self.cells = [BLANK] * 9
        self.remaining_cells = [i for i in range(1, 10)]
        self.current_token = self.get_tokens()[initial_token]

    def get_remaining_moves(self) -> list[int]:
        return [x for x in self.remaining_cells if type(x) == int]

    def cell_taken(self, index):
        return True if self.cells[index - 1] != BLANK else False

    @override
    def place_token(self, index: int, token: str = None):
        if token is None:
            token = self.current_token
        self.cells[index - 1] = token
        self.remaining_cells[index - 1] = "■"

    @override
    def remove_token(self, index):
        self.cells[index - 1] = BLANK
        self.remaining_cells[index - 1] = index

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
    def get_state(self):
        return "".join(self.cells)

    @override
    def check_win(self, token=None) -> bool:
        return any(check_subset([self.cells[i] for i in subset], token) for subset in self.winning_subsets)

    def count_doubles(self, token):
        subsets = map(lambda x: [self.cells[i] for i in x], self.winning_subsets)
        return sum(1 for subset in subsets if subset.count(token) == 2 and subset.count(BLANK) == 1)

    @override
    def evaluate_early(self, player, opponent) -> int:
        good_doubles = self.count_doubles(player)
        bad_doubles = self.count_doubles(opponent)
        return good_doubles - bad_doubles

    @override
    def human_choose_move(self) -> int:
        while True:
            print(f"Choose a cell:\n{self.get_board()}")
            key = readkey()
            if key.isdigit() and key != "0":
                cell = int(key)
                if not self.cell_taken(cell):
                    return cell

            clear_screen()
            print(f"Enter one of the following keys:\n{self.get_board(self.remaining_cells)}\nPlease choose an empty cell.")
            readkey()
            clear_screen()

    @override
    def algorithm_choose_move(self) -> int:
        token = self.current_token
        if self.visualise:
            clear_screen()
            print(f"Player {token}\n{self.get_board()}")
            time.sleep(0.5)

        remaining_cells = self.get_remaining_moves()
        for t in [token, self.get_other(token)]:
            for cell in remaining_cells:
                self.place_token(cell, t)
                win = self.check_win()
                self.remove_token(cell)
                if win:
                    return cell

        highest_count = ([], 0)
        for cell in remaining_cells:
            self.place_token(cell)
            count = self.count_doubles(token)
            self.remove_token(cell)
            if count > highest_count[1]:
                highest_count = ([cell], count)
            elif count == highest_count[1]:
                highest_count[0].append(cell)
        if highest_count[1] > 0:
            return random.choice(highest_count[0])
        return random.choice(remaining_cells)

    @staticmethod
    @override
    def get_tokens():
        return "X", "O"


if __name__ == "__main__":
    TicTacToe.start()
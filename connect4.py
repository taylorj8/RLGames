import random
from typing import override
from readchar import readkey
import sys

from game import Game, clear_screen
from util import param_or_default

BLANK = "  "


class Connect4(Game):
    def __init__(self, player1, player2, visualise, board_size=(7, 6), max_depth=100, q_table=None):
        super().__init__(player1, player2, visualise, max_depth, q_table)
        self.width = board_size[0]
        self.height = board_size[1]
        self.cells = [[BLANK] * self.width for _ in range(self.height)]
        self.cols = [x for x in range(1, self.width + 1)]

        self.max_moves = self.width * self.height
        self.start_instructions = f"Welcome to Connect 4! The game is played using the keyboard with 1-{self.width} corresponding to each column."

    @override
    def reset(self):
        self.cells = [[BLANK] * self.width for _ in range(self.height)]
        self.cols = [x for x in range(1, self.width + 1)]
        self.current_token = self.get_tokens()[0]

    def column_full(self, index):
        return True if self.cells[self.height - 1][index - 1] != BLANK else False

    @override
    def place_token(self, col: int, token: str = None):
        if token is None:
            token = self.current_token
        for i in range(self.height):
            if self.cells[i][col - 1] == BLANK:
                self.cells[i][col - 1] = token
                # if token placed in top row, remove column from available moves
                if i == self.height - 1:
                    self.cols[col - 1] = " "
                return

    @override
    def remove_token(self, col):
        for i in reversed(range(self.height)):
            if self.cells[i][col - 1] != BLANK:
                self.cells[i][col - 1] = BLANK
                self.cols[col - 1] = col
                return

    @override
    def get_remaining_moves(self) -> list[int]:
        return [x for x in self.cols if type(x) == int]

    @override
    def get_board(self, guide=None) -> str:
        board = "╻" + "    ╻" * self.width + "\n"

        for row in reversed(range(self.height)):  # start from top row
            board += "┃ " + " ┃ ".join(self.cells[row][:self.width]) + " ┃\n"
            if row > 0:
                board += "┣" + "━━━━╋" * (self.width - 1) + "━━━━┫\n"

        board += "┗" + "━━━━┻" * (self.width - 1) + "━━━━┛\n"
        board += "  " + "    ".join(map(str, self.cols[:self.width]))  # column guides at the bottom

        return board

    @override
    def get_state(self) -> str:
        def convert_token(x: str):
            match x:
                case "  ":
                    return " "
                case "🔴":
                    return "R"
                case "🔵":
                    return "B"
        return "".join([convert_token(x) for row in self.cells for x in row])

    @override
    def check_win(self, token=None) -> bool:
        for i in range(self.height):
            for j in range(self.width):
                potential_wins = []
                # horizontal
                if j <= self.width - 4:
                    potential_wins.append([self.cells[i][j + k] for k in range(4)])
                # vertical
                if i <= self.height - 4:
                    potential_wins.append([self.cells[i + k][j] for k in range(4)])
                # diagonal (\)
                if i <= self.height - 4 and j <= self.width - 4:
                    potential_wins.append([self.cells[i + k][j + k] for k in range(4)])
                # diagonal (/)
                if i <= self.height - 4 and j >= 3:
                    potential_wins.append([self.cells[i + k][j - k] for k in range(4)])
                # check if any of the potential wins are valid
                if token is None:
                    outcomes = [subset[0] != BLANK and all(x == subset[0] for x in subset) for subset in potential_wins]
                else:
                    outcomes = [all(x == token for x in subset) for subset in potential_wins]
                # if any of the potential wins are valid, return True
                if any(outcomes):
                    return True
        return False

    def count_runs(self, token, threshold):
        c = self.cells
        run_count = 0
        for i in range(self.height):
            for j in range(self.width):
                runs = []
                if j <= self.width - 4:
                    runs.append([c[i][j + k] for k in range(4)])
                if i <= self.height - 4:
                    runs.append([c[i + k][j] for k in range(4)])
                if i <= self.height - 4 and j <= self.width - 4:
                    runs.append([c[i + k][j + k] for k in range(4)])
                if i <= self.height - 4 and j >= 3:
                    runs.append([c[i + k][j - k] for k in range(4)])

                run_count += sum(1 for subset in runs if subset.count(token) == threshold and subset.count(BLANK) == 4 - threshold)
        return run_count

    @override
    # method to evaluate the board before a win
    # returns a score based on the number of runs of 3 and 2 for the player and opponent
    def evaluate_early(self, player, opponent) -> int:
        good_runs_of_three = self.count_runs(player, 3)
        good_runs_of_two = self.count_runs(player, 2)
        bad_runs_of_three = self.count_runs(opponent, 3)
        bad_runs_of_two = self.count_runs(opponent, 2)

        return good_runs_of_three * 2 + good_runs_of_two - bad_runs_of_three * 2 - bad_runs_of_two

    @override
    def human_choose_move(self):
        while True:
            print(f"Player {self.current_token}, choose a column:\n{self.get_board()}")
            key = readkey()
            if key.isdigit():
                column = int(key)
                if 1 <= column <= self.width and not self.column_full(column):
                    return column

            clear_screen()
            print(f"Select a valid column.\n{self.get_board()}\nPress any key to continue.")
            readkey()
            clear_screen()

    # Basic algorithm for playing connect 4 - if a move will result in a win, take it
    # else if a move will result in a win for the opponent, block it
    # else find a move that results in the most runs of 4 with 3 tokens and 1 blank
    # else do the same with 2 tokens and 2 blanks
    # else choose randomly
    @override
    def algorithm_choose_move(self):
        if self.visualise:
            clear_screen()
            print(f"Player {self.current_token}\n{self.get_board()}")

        remaining_columns = self.get_remaining_moves()
        for t in [self.current_token, self.get_other(self.current_token)]:
            for col in remaining_columns:
                self.place_token(col, t)
                win = self.check_win()
                self.remove_token(col)
                if win:
                    return col

        for threshold in [3, 2]:
            baseline = self.count_runs(self.current_token, threshold)
            highest_wins = ([], baseline)
            for col in remaining_columns:
                self.place_token(col)
                wins = self.count_runs(self.current_token, threshold)
                self.remove_token(col)
                if wins > highest_wins[1]:
                    highest_wins = ([col], wins)
                elif wins == highest_wins[1]:
                    highest_wins[0].append(col)
            if highest_wins[1] > baseline:
                return random.choice(highest_wins[0])
        return random.choice(remaining_columns)

    @staticmethod
    @override
    def get_tokens():
        return "🔴", "🔵"


if __name__ == "__main__":
    args = sys.argv
    width = param_or_default(args, "-w", 7)
    height = param_or_default(args, "-h", 6)
    if not (4 <= width <= 9 and 4 <= height <= 9):
        print("Width and height must be between 4 and 9.")
        exit()
    Connect4.start((width, height))

import random
import time
from typing import override
import sys

from game import Game, clear_screen
from util import param_or_default

BLANK = "  "


# inherit from the Game class
# implements the methods specific to the Connect4 game
class Connect4(Game):
    input_name = "column"
    def __init__(self, player1, player2, visualise, board_size=(7, 6), max_depth=100, q_table=None):
        super().__init__(player1, player2, visualise, max_depth, q_table)
        self.width = board_size[0]
        self.height = board_size[1]
        self.columns = [[BLANK] * self.height for _ in range(self.width)]
        self.cols = [x for x in range(1, self.width + 1)]

        self.max_moves = self.width * self.height
        self.start_instructions = f"Welcome to Connect 4! The game is played using the keyboard with 1-{self.width} corresponding to each column."

    # reset the game back to its initial state
    @override
    def reset(self):
        self.columns = [[BLANK] * self.height for _ in range(self.width)]
        self.cols = [x for x in range(1, self.width + 1)]
        self.current_token = self.get_tokens()[0]

    # place a token on top of the column
    @override
    def place_token(self, col: int, token: str = None):
        if token is None:
            token = self.current_token
        for i in range(self.height):
            if self.columns[col - 1][i] == BLANK:
                self.columns[col - 1][i] = token
                # if token placed in top row, remove column from available moves
                if i == self.height - 1:
                    self.cols[col - 1] = " "
                return

    # remove the top token from a column
    @override
    def remove_token(self, col):
        for i in reversed(range(self.height)):
            if self.columns[col - 1][i] != BLANK:
                self.columns[col - 1][i] = BLANK
                self.cols[col - 1] = col
                return

    # get the available moves
    @override
    def get_remaining_moves(self) -> list[int]:
        return [x for x in self.cols if type(x) == int]

    # algorithmically construct the board for display
    # allows the board to be constructed based on the size provided by the user
    @override
    def get_board(self, guide=None) -> str:
        board = "╻" + "    ╻" * self.width + "\n"

        for row in reversed(range(self.height)):  # start from top row
            board += "┃ " + " ┃ ".join(self.columns[col][row] for col in range(self.width)) + " ┃\n"
            if row > 0:
                board += "┣" + "━━━━╋" * (self.width - 1) + "━━━━┫\n"

        board += "┗" + "━━━━┻" * (self.width - 1) + "━━━━┛\n"
        board += "  " + "    ".join(map(str, self.cols[:self.width]))  # column guides at the bottom

        return board

    # get the state of the board as a string
    # convert the tokens to R, B and " "
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
        return "".join([convert_token(self.columns[col][row]) for row in range(self.height) for col in range(self.width)])

    # check for a win by checking all possible winning subsets
    # if a token is provided, check if that token has won
    @override
    def check_win(self, token=None) -> bool:
        for col in range(self.width):
            for row in range(self.height):
                potential_wins = []
                # horizontal
                if col <= self.width - 4:
                    potential_wins.append([self.columns[col + k][row] for k in range(4)])
                # vertical
                if row <= self.height - 4:
                    potential_wins.append([self.columns[col][row + k] for k in range(4)])
                # diagonal (\)
                if col <= self.width - 4 and row <= self.height - 4:
                    potential_wins.append([self.columns[col + k][row + k] for k in range(4)])
                # diagonal (/)
                if col <= self.width - 4 and row >= 3:
                    potential_wins.append([self.columns[col + k][row - k] for k in range(4)])
                # check if any of the potential wins are valid
                if token is None:
                    outcomes = [subset[0] != BLANK and all(x == subset[0] for x in subset) for subset in potential_wins]
                else:
                    outcomes = [all(x == token for x in subset) for subset in potential_wins]
                # if any of the potential wins are valid, return True
                if any(outcomes):
                    return True
        return False

    # count the number of runs of a token of a certain length
    # a run a sequence of 4 tokens containing only the given token and blanks
    # a run of 3 is one move away from winning
    def count_runs(self, token, threshold):
        run_count = 0
        for col in range(self.width):
            for row in range(self.height):
                runs = []
                if col <= self.width - 4:
                    runs.append([self.columns[col + k][row] for k in range(4)])
                if row <= self.height - 4:
                    runs.append([self.columns[col][row + k] for k in range(4)])
                if col <= self.width - 4 and row <= self.height - 4:
                    runs.append([self.columns[col + k][row + k] for k in range(4)])
                if col <= self.width - 4 and row >= 3:
                    runs.append([self.columns[col + k][row - k] for k in range(4)])
                run_count += sum(1 for subset in runs if subset.count(token) == threshold and subset.count(BLANK) == 4 - threshold)
        return run_count

    # evaluate the state of the board for the minimax algorithm
    # used if the depth is too low to reach the terminal state
    @override
    def evaluate_early(self, player, opponent) -> int:
        # count the number of runs of 3 and 2 for the player and opponent
        # return the difference between the two
        good_runs_of_three = self.count_runs(player, 3)
        good_runs_of_two = self.count_runs(player, 2)
        bad_runs_of_three = self.count_runs(opponent, 3)
        bad_runs_of_two = self.count_runs(opponent, 2)

        # runs of 3 are worth 4 times as much as runs of 2
        return good_runs_of_three * 4 + good_runs_of_two - bad_runs_of_three * 4 - bad_runs_of_two

    # algorithmically choose a move
    @override
    def algorithm_choose_move(self):
        if self.visualise:
            clear_screen()
            print(f"Player {self.current_token}\n{self.get_board()}")
            time.sleep(0.2)

        # first check if the player can win in the next move - if so, return that move
        # then check if the opponent can win in the next move - if so, block that move
        remaining_columns = self.get_remaining_moves()
        for t in [self.current_token, self.get_other(self.current_token)]:
            for col in remaining_columns:
                self.place_token(col, t)
                win = self.check_win()
                self.remove_token(col)
                if win:
                    return col

        # if no winning moves, find the move that results in the most runs of 3 - i.e. runs one move away from winning
        # next, find the move that results in the most runs of 2
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
        # if no runs of 3 or 2, choose randomly
        return random.choice(remaining_columns)

    # return the tokens used in the game
    @staticmethod
    @override
    def get_tokens() -> tuple[str, str]:
        return "🔴", "🔵"

# start the game - calls the start method of the Game class
# The board size can be set using the -w and -h flags
if __name__ == "__main__":
    args = sys.argv
    width = param_or_default(args, "-w", 7)
    height = param_or_default(args, "-h", 6)
    if not (4 <= width <= 9 and 4 <= height <= 9):
        print("Width and height must be between 4 and 9.")
        exit()
    Connect4.start((width, height))

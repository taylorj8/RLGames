import random
import time
from typing import override

from readchar import readkey

from game import Game, clear_screen

BLANK = "  "


class Connect4(Game):
    max_moves = 42
    start_instructions = "Welcome to Connect 4! The game is played using the keyboard with 1-7 corresponding to each column."

    def __init__(self, player1, player2, visualise):
        super().__init__(player1, player2, visualise)
        self.cells = [[BLANK] * 7 for _ in range(6)]
        self.cols = [x for x in range(1, 8)]

    @override
    def reset(self):
        self.cells = [[BLANK] * 7 for _ in range(6)]
        self.cols = [x for x in range(1, 8)]

    def column_full(self, index):
        return True if self.cells[5][index - 1] != BLANK else False

    @override
    def place_token(self, col, token):
        for i in range(6):
            if self.cells[i][col - 1] == BLANK:
                self.cells[i][col - 1] = token
                if i == 5:
                    self.cols[col - 1] = " "
                return

    @override
    def remove_token(self, col):
        for i in reversed(range(6)):
            if self.cells[i][col - 1] != BLANK:
                self.cells[i][col - 1] = BLANK
                self.cols[col - 1] = col
                return

    @override
    def get_board(self, guide=None):
        c = self.cells
        n = self.cols
        return f"""╻    ╻    ╻    ╻    ╻    ╻    ╻    ╻
┃ {c[5][0]} ┃ {c[5][1]} ┃ {c[5][2]} ┃ {c[5][3]} ┃ {c[5][4]} ┃ {c[5][5]} ┃ {c[5][6]} ┃
┣━━━━╋━━━━╋━━━━╋━━━━╋━━━━╋━━━━╋━━━━┫
┃ {c[4][0]} ┃ {c[4][1]} ┃ {c[4][2]} ┃ {c[4][3]} ┃ {c[4][4]} ┃ {c[4][5]} ┃ {c[4][6]} ┃
┣━━━━╋━━━━╋━━━━╋━━━━╋━━━━╋━━━━╋━━━━┫
┃ {c[3][0]} ┃ {c[3][1]} ┃ {c[3][2]} ┃ {c[3][3]} ┃ {c[3][4]} ┃ {c[3][5]} ┃ {c[3][6]} ┃
┣━━━━╋━━━━╋━━━━╋━━━━╋━━━━╋━━━━╋━━━━┫
┃ {c[2][0]} ┃ {c[2][1]} ┃ {c[2][2]} ┃ {c[2][3]} ┃ {c[2][4]} ┃ {c[2][5]} ┃ {c[2][6]} ┃
┣━━━━╋━━━━╋━━━━╋━━━━╋━━━━╋━━━━╋━━━━┫
┃ {c[1][0]} ┃ {c[1][1]} ┃ {c[1][2]} ┃ {c[1][3]} ┃ {c[1][4]} ┃ {c[1][5]} ┃ {c[1][6]} ┃
┣━━━━╋━━━━╋━━━━╋━━━━╋━━━━╋━━━━╋━━━━┫
┃ {c[0][0]} ┃ {c[0][1]} ┃ {c[0][2]} ┃ {c[0][3]} ┃ {c[0][4]} ┃ {c[0][5]} ┃ {c[0][6]} ┃
┗━━━━┻━━━━┻━━━━┻━━━━┻━━━━┻━━━━┻━━━━┛
  {n[0]}    {n[1]}    {n[2]}    {n[3]}    {n[4]}    {n[5]}    {n[6]}"""

    @override
    def check_win(self):
        c = self.cells
        for i in range(6):
            for j in range(7):
                potential_wins = []
                if j <= 3:
                    potential_wins.append([c[i][j + k] for k in range(4)])
                if i <= 2:
                    potential_wins.append([c[i + k][j] for k in range(4)])
                if i <= 2 and j <= 3:
                    potential_wins.append([c[i + k][j + k] for k in range(4)])
                if i <= 2 and j >= 3:
                    potential_wins.append([c[i + k][j - k] for k in range(4)])

                outcomes = [subset[0] != BLANK and all([x == subset[0] for x in subset]) for subset in potential_wins]
                if any(outcomes):
                    return True
        return False

    def count_tokens(self, token, threshold):
        c = self.cells
        token_count = 0
        for i in range(6):
            for j in range(7):
                runs = []
                if j <= 3:
                    runs.append([c[i][j + k] for k in range(4)])
                if i <= 2:
                    runs.append([c[i + k][j] for k in range(4)])
                if i <= 2 and j <= 3:
                    runs.append([c[i + k][j + k] for k in range(4)])
                if i <= 2 and j >= 3:
                    runs.append([c[i + k][j - k] for k in range(4)])

                token_count += sum(1 for subset in runs if subset.count(token) == threshold and subset.count(BLANK) == 4 - threshold)
        return token_count

    @override
    def human_choose_move(self, token):
        while True:
            print(f"Player {token}, choose a column:\n{self.get_board()}")
            key = readkey()
            if key.isdigit():
                column = int(key)
                if not self.column_full(column) and 1 <= column <= 7:
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
    def algorithm_choose_move(self, token):
        if self.visualise:
            clear_screen()
            print(f"Player {token}\n{self.get_board()}")
            time.sleep(0.5)

        remaining_columns = [x for x in self.cols if type(x)==int]
        for t in [token, self.get_other(token)]:
            for col in remaining_columns:
                self.place_token(col, t)
                win = self.check_win()
                self.remove_token(col)
                if win:
                    return col

        for threshold in [3, 2]:
            baseline = self.count_tokens(token, threshold)
            highest_wins = ([], baseline)
            for col in remaining_columns:
                self.place_token(col, token)
                wins = self.count_tokens(token, threshold)
                self.remove_token(col)
                if wins > highest_wins[1]:
                    highest_wins = ([col], wins)
                elif wins == highest_wins[1]:
                    highest_wins[0].append(col)
            if highest_wins[1] > baseline:
                return random.choice(highest_wins[0])
        return random.choice(remaining_columns)

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
        return "🔴", "🔵"


if __name__ == "__main__":
    Connect4.start()

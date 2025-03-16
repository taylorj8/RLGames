import random
import sys
import time
from typing import override

from tqdm import trange
from readchar import readkey

from game import Game, clear_screen
from util import get_from_args

BLANK = "  "


class Connect4(Game):
    def __init__(self, player1, player2, visualise):
        super().__init__(player1, player2, visualise)
        self.cells = [[BLANK] * 7 for _ in range(6)]
        self.cols = [x for x in range(1, 8)]

    def column_full(self, index):
        return True if self.cells[5][index - 1] != BLANK else False

    def place_token(self, col, token):
        for i in range(6):
            if self.cells[i][col - 1] == BLANK:
                self.cells[i][col - 1] = token
                if i == 5:
                    self.cols[col - 1] = " "
                return

    def remove_token(self, col):
        for i in reversed(range(6)):
            if self.cells[i][col - 1] != BLANK:
                self.cells[i][col - 1] = BLANK
                self.cols[col - 1] = col
                return

    @override
    def get_board(self):
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
                run = []
                if j <= 3:
                    run.append([c[i][j + k] for k in range(4)])
                if i <= 2:
                    run.append([c[i + k][j] for k in range(4)])
                if i <= 2 and j <= 3:
                    run.append([c[i + k][j + k] for k in range(4)])
                if i <= 2 and j >= 3:
                    run.append([c[i + k][j - k] for k in range(4)])

                token_count += sum(1 for subset in run if subset.count(token) == threshold and subset.count(BLANK) == 4 - threshold)
        return token_count


    @override
    def game_loop(self, players):
        token = ""
        for i in [i for i in range(0, 42)]:
            player, token = players[i % 2]
            col = self.choose_move(player, token)

            self.place_token(col, token)
            if self.check_win():
                break
            if self.visualise:
                clear_screen()
        return token

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
    def ai_choose_move(self, token):
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


def main():
    player1, player2, games = get_from_args(sys.argv)
    player1 = (player1, "🔴")
    player2 = (player2, "🔵")

    stats = {"🔴": 0, "🔵": 0, "Tie": 0}
    for i in trange(games):
        visualise = False if games > 1 and player1 != "human" and player2 != "human" else True
        game = Connect4(player1, player2, visualise)

        winner = game.play(reverse_order=bool(i%2))
        stats[winner] += 1

    clear_screen()
    print(f"Player 1 ({player1}) wins: {stats['🔴']}")
    print(f"Player 2 ({player2}) wins: {stats['🔵']}")
    print(f"Ties: {stats['Tie']}")


if __name__ == "__main__":
    main()

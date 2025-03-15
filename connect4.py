import random
import time

from readchar import readkey
import os

EMPTY = "  "

def clear_screen():
    os.system('cls' if os.name=='nt' else 'clear')


class Connect4:
    def __init__(self, player1, player2):
        self.cells = [[EMPTY] * 7 for _ in range(6)]
        self.cols = [x for x in range(1, 8)]
        self.players = [(player1, "🔴"), (player2, "🔵")]

    def column_full(self, index):
        return True if self.cells[5][index - 1] != EMPTY else False

    def place_token(self, col, token):
        for i in range(6):
            if self.cells[i][col - 1] == EMPTY:
                self.cells[i][col - 1] = token
                if i == 5:
                    self.cols[col - 1] = " "
                return

    def remove_token(self, col):
        for i in reversed(range(6)):
            if self.cells[i][col - 1] != EMPTY:
                self.cells[i][col - 1] = EMPTY
                self.cols[col - 1] = col
                return

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


    def check_win(self, length=4, count=False):
        c = self.cells
        win_count = 0
        for i in range(6):
            for j in range(7):
                win_conditions = []
                if j <= 7 - length:
                    win_conditions.append([c[i][j + k] for k in range(length)])
                if i <= 6 - length:
                    win_conditions.append([c[i + k][j] for k in range(length)])
                if i <= 6 - length and j <= 7 - length:
                    win_conditions.append([c[i + k][j + k] for k in range(length)])
                if i <= 6 - length and j >= length - 1:
                    win_conditions.append([c[i + k][j - k] for k in range(length)])

                wins = list(map(check_subset, win_conditions))
                if any(wins):
                    if not count:
                        return True
                    else:
                        win_count += sum(wins)
        if count:
            return win_count
        return False


    def play(self):
        clear_screen()
        print("Welcome to Connect 4! The game is played using the keyboard with 1-7 corresponding to each column.")
        print(self.get_board())
        print("Press any key to start.")
        readkey()
        clear_screen()

        token = ""
        for i in [i for i in range(0, 42)]:
            player, token = self.players[i % 2]
            _, other_token = self.players[(i+1) % 2]
            col = self.choose_column(player, token, other_token)

            self.place_token(col, token)
            if self.check_win():
                print(self.get_board())
                print(f"Player {token} wins!")
                clear_screen()
                break
            clear_screen()

        if self.check_win():
            print(f"Player {token} won!")
        else:
            print("The game ended in a tie.")
        print(self.get_board())
        readkey()


    def choose_column(self, player, token, other_token):
        column = None
        match player:
            case "Human":
                column = self.human_choose_column(token)
            case "AI":
                column = self.ai_choose_column(token, other_token, True)
        return column


    def human_choose_column(self, token):
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
    # else if a column will result in a win for the opponent, block it
    # else find a move that results in the most runs of 3 - if a tie, choose randomly
    # else do the same with 2
    # else choose randomly
    def ai_choose_column(self, token, other_token, visualise):
        if visualise:
            clear_screen()
            print(f"Player {token}\n{self.get_board()}")
            # time.sleep(0.5)

        remaining_columns = [x for x in self.cols if type(x)==int]
        for col in remaining_columns:
            self.place_token(col, token)
            win = self.check_win()
            self.remove_token(col)
            if win:
                return col

        for col in remaining_columns:
            self.place_token(col, other_token)
            win = self.check_win()
            self.remove_token(col)
            if win:
                return col

        for length in [3, 2]:
            highest_wins = ([], 0)
            for col in remaining_columns:
                self.place_token(col, token)
                wins = self.check_win(length, count=True)
                self.remove_token(col)
                if wins > highest_wins[1]:
                    highest_wins = ([col], wins)
                elif wins == highest_wins[1]:
                    highest_wins[0].append(col)
            if highest_wins[1] > 0:
                return random.choice(highest_wins[0])
        return random.choice(remaining_columns)

def check_subset(subset):
    return subset[0] != EMPTY and all([x == subset[0] for x in subset])


if __name__ == "__main__":
    game = Connect4("Human", "AI")
    game.play()
import random
import sys
import time
from tqdm import trange


from readchar import readkey
import os

BLANK = "  "

def clear_screen():
    os.system('cls' if os.name=='nt' else 'clear')


class Connect4:
    def __init__(self, player1, player2, visualise):
        self.cells = [[BLANK] * 7 for _ in range(6)]
        self.cols = [x for x in range(1, 8)]
        self.players = [(player1, "🔴"), (player2, "🔵")]
        self.visualise = visualise

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

    def print(self, message):
        if self.visualise:
            print(message)

    def await_key(self):
        if self.visualise:
            readkey()

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

                outcomes = [subset[0] != BLANK and all([x == subset[0] for x in subset]) for subset in win_conditions]
                if count:
                    win_count += sum(outcomes)
                elif any(outcomes):
                    return True
        if count:
            return win_count
        return False


    def count_tokens(self, token, threshold):
        c = self.cells
        token_count = 0
        for i in range(6):
            for j in range(7):
                win_conditions = []
                if j <= 3:
                    win_conditions.append([c[i][j + k] for k in range(4)])
                if i <= 2:
                    win_conditions.append([c[i + k][j] for k in range(4)])
                if i <= 2 and j <= 3:
                    win_conditions.append([c[i + k][j + k] for k in range(4)])
                if i <= 2 and j >= 2:
                    win_conditions.append([c[i + k][j - k] for k in range(4)])

                token_count += sum(1 for subset in win_conditions if subset.count(token) == threshold and subset.count(BLANK) == 4 - threshold)
        return token_count


    def play(self, reverse_order=False):
        if self.visualise:
            clear_screen()
            print("Welcome to Connect 4! The game is played using the keyboard with 1-7 corresponding to each column.")
            print(self.get_board())
            print("Press any key to start.")
            readkey()
            clear_screen()

        token = ""
        players = self.players if not reverse_order else list(reversed(self.players))
        for i in [i for i in range(0, 42)]:
            player, token = players[i % 2]
            col = self.choose_column(player, token)

            self.place_token(col, token)
            if self.check_win():
                break
            if self.visualise:
                clear_screen()

        if self.check_win():
            self.print(f"Player {token} wins!")
            winner = token
        else:
            self.print("The game ended in a tie.")
            winner = "Tie"
        self.print(self.get_board())
        self.await_key()
        return winner


    def choose_column(self, player, token):
        column = None
        match player:
            case "human":
                column = self.human_choose_column(token)
            case "ai":
                column = self.ai_choose_column(token)
            case "ai2":
                column = self.ai_choose_column2(token)
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
    def ai_choose_column(self, token):
        if self.visualise:
            clear_screen()
            print(f"Player {token}\n{self.get_board()}")
            time.sleep(0.5)

        remaining_columns = [x for x in self.cols if type(x)==int]
        for t in [token, get_other(token)]:
            for col in remaining_columns:
                self.place_token(col, t)
                win = self.check_win()
                self.remove_token(col)
                if win:
                    return col

        for length in [3, 2]:
            baseline = self.check_win(length, count=True)
            highest_wins = ([], baseline)
            for col in remaining_columns:
                self.place_token(col, token)
                wins = self.check_win(length, count=True)
                self.remove_token(col)
                if wins > highest_wins[1]:
                    highest_wins = ([col], wins)
                elif wins == highest_wins[1]:
                    highest_wins[0].append(col)
            if highest_wins[1] > baseline:
                return random.choice(highest_wins[0])
        return random.choice(remaining_columns)

    def ai_choose_column2(self, token):
        if self.visualise:
            clear_screen()
            print(f"Player {token}\n{self.get_board()}")
            time.sleep(0.5)

        remaining_columns = [x for x in self.cols if type(x)==int]
        for t in [token, get_other(token)]:
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


def get_other(token):
    return "🔴" if token == "🔵" else "🔵"

# get the value of a parameter or return the default value
def param_or_default(args, flag, default):
    if flag in args:
        value = args[args.index(flag) + 1]
        if value.isdigit():
            return int(value)
        return args[args.index(flag) + 1].lower()
    return default

def get_from_args(args):
    try:
        player1 = param_or_default(args, "-p1", "ai")
        player2 = param_or_default(args, "-p2", "ai2")
        games = param_or_default(args, "-g", 1)
    except:
        print("Usage: python connect4.py -p1 <player1> -p2 <player2> -g <number of games>")
        exit()
    return player1, player2, games


def main():
    player1, player2, games = get_from_args(sys.argv)

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

from readchar import readkey
import os

EMPTY = "  "

def clear_screen():
    os.system('cls' if os.name=='nt' else 'clear')


class TicTacToe:
    def __init__(self):
        self.cells = [[EMPTY] * 7 for _ in range(6)]
        self.cols = [x for x in range(1, 8)]

    def column_full(self, index):
        return True if self.cells[5][index - 1] != EMPTY else False

    def place_token(self, col, token):
        for i in range(6):
            if self.cells[i][col - 1] == EMPTY:
                self.cells[i][col - 1] = token
                if i == 5:
                    self.cols[col - 1] = " "
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


    def check_win(self):
        c = self.cells
        for i in range(6):
            for j in range(5):
                win_conditions = []
                if j <= 3:
                    win_conditions.append([c[i][j], c[i][j+1], c[i][j+2], c[i][j+3]])
                if i <= 2:
                    win_conditions.append([c[i][j], c[i+1][j], c[i+2][j], c[i+3][j]])
                if i <= 2 and j <= 3:
                    win_conditions.append([c[i][j], c[i+1][j+1], c[i+2][j+2], c[i+3][j+3]])
                if i <= 2 and j <= 3:
                    win_conditions.append([c[i][j], c[i+1][j-1], c[i+2][j-2], c[i+3][j-3]])

                wins = map(check_subset, win_conditions)
                if any(wins):
                    return True
        return False


    def play(self):
        clear_screen()
        print("Welcome to Connect 4! The game is played using the keyboard with 1-7 corresponding to each column.")
        print(self.get_board())
        print("Press any key to start.")
        readkey()
        clear_screen()

        token = ""
        tokens = ["🔴", "🔵"]
        for i in [i for i in range(0, 42)]:
            token = tokens[i % 2]
            while True:
                print(f"Player {token}, choose a column:")
                print(self.get_board())
                key = readkey()
                if key.isdigit():
                    col = int(key)
                    if not self.column_full(col) and 1 <= col <= 7:
                        break

                clear_screen()
                print("Select a valid column.")
                print(self.get_board())
                print("Press any key to continue.")
                readkey()
                clear_screen()

            col = int(key)
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


def check_subset(subset):
    return subset[0] != EMPTY and all([x == subset[0] for x in subset])


if __name__ == "__main__":
    game = TicTacToe()
    game.play()
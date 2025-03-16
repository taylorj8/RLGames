import sys

from readchar import readkey
import os

from tqdm import trange

from util import get_from_args

EMPTY = " "

def clear_screen():
    os.system('cls' if os.name=='nt' else 'clear')


class TicTacToe:
    def __init__(self):
        self.cells = [EMPTY] * 9
        self.valid_keys = [str(i) for i in range(1, 10)]

    def cell_taken(self, index):
        return True if self.cells[index - 1] != EMPTY else False

    def set_cell(self, index, player):
        self.cells[index - 1] = player
        self.valid_keys[index - 1] = "■"


    def get_board(self, override=None):
        c = self.cells if override is None else override
        return f"""    ╻   ╻
  {c[6]} ┃ {c[7]} ┃ {c[8]}
╺━━━╋━━━╋━━━╸
  {c[3]} ┃ {c[4]} ┃ {c[5]}
╺━━━╋━━━╋━━━╸
  {c[0]} ┃ {c[1]} ┃ {c[2]}
    ╹   ╹"""

    def check_win(self):
        return check_subset(self.cells[:3]) or check_subset(self.cells[3:6]) or check_subset(self.cells[6:9]) or \
               check_subset([self.cells[0], self.cells[3], self.cells[6]]) or check_subset([self.cells[1], self.cells[4], self.cells[7]]) or \
               check_subset([self.cells[2], self.cells[5], self.cells[8]]) or check_subset([self.cells[0], self.cells[4], self.cells[8]]) or \
               check_subset([self.cells[2], self.cells[4], self.cells[6]])


    def play(self):
        clear_screen()
        print("Welcome to TicTacToe! The game is played using the numpad. The numbers correspond to squares as follows:")
        print(self.get_board(self.valid_keys))
        print("Press any key to start.")
        readkey()
        clear_screen()

        player = ""
        players = ["X", "O"]
        for i in [i for i in range(0, 9)]:
            player = players[i % 2]
            while True:
                print(f"Player {player}, choose a cell:")
                print(self.get_board())
                key = readkey()
                if key.isdigit() and key != "0":
                    cell = int(key)
                    if not self.cell_taken(cell):
                        break

                clear_screen()
                print("Enter one of the following keys:")
                print(self.get_board(self.valid_keys))
                print("Press any key to continue.")
                readkey()
                clear_screen()

            cell = int(key)
            self.set_cell(cell, player)
            if self.check_win():
                print(self.get_board())
                print(f"Player {player} wins!")
                clear_screen()
                break
            clear_screen()

        if self.check_win():
            print(f"Player {player} won!")
        else:
            print("The game ended in a tie.")
        print(self.get_board())
        readkey()


def check_subset(subset):
    return subset[0] != EMPTY and all([x == subset[0] for x in subset])


if __name__ == "__main__":
    game = TicTacToe()
    game.play()

def main():
    player1, player2, games = get_from_args(sys.argv)

    stats = {"🔴": 0, "🔵": 0, "Tie": 0}
    for i in trange(games):
        visualise = False if games > 1 and player1 != "human" and player2 != "human" else True
        game = TicTacToe(player1, player2, visualise)

        winner = game.play(reverse_order=bool(i%2))
        stats[winner] += 1

    clear_screen()
    print(f"Player 1 ({player1}) wins: {stats['🔴']}")
    print(f"Player 2 ({player2}) wins: {stats['🔵']}")
    print(f"Ties: {stats['Tie']}")


if __name__ == "__main__":
    main()
import random
import time
from heapq import heappush, heappop
from typing import override
from readchar import readkey
import os
from game import Game
from player import Player

BLANK = " "

def clear_screen():
    os.system('cls' if os.name=='nt' else 'clear')

def check_subset(subset, token=None):
    if token is None:
        return subset[0] != BLANK and all([x == subset[0] for x in subset])
    return all([x == token for x in subset])


class TicTacToe(Game):
    max_moves = 9
    start_instructions = "Welcome to TicTacToe! The game is played using the numpad. The numbers correspond to squares as follows:"
    winning_subsets = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]

    def __init__(self, player1, player2, visualise):
        super().__init__(player1, player2, visualise)
        self.cells = [BLANK] * 9
        self.remaining_cells = [i for i in range(1, 10)]

    @override
    def reset(self):
        self.cells = [BLANK] * 9
        self.remaining_cells = [i for i in range(1, 10)]

    def cell_taken(self, index):
        return True if self.cells[index - 1] != BLANK else False

    @override
    def place_token(self, index, player):
        self.cells[index - 1] = player
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
    def check_win(self, token=None) -> bool:
        return any(check_subset([self.cells[i] for i in subset], token) for subset in self.winning_subsets)

    def count_doubles(self, token):
        subsets = map(lambda x: [self.cells[i] for i in x], self.winning_subsets)
        return sum(1 for subset in subsets if subset.count(token) == 2 and subset.count(BLANK) == 1)

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
            print(f"Enter one of the following keys:\n{self.get_board(self.remaining_cells)}\nPlease choose an empty cell.")
            readkey()
            clear_screen()

    @override
    def algorithm_choose_move(self, token):
        if self.visualise:
            clear_screen()
            print(f"Player {token}\n{self.get_board()}")
            time.sleep(0.5)

        remaining_cells = [x for x in self.remaining_cells if type(x) == int]
        for t in [token, self.get_other(token)]:
            for cell in remaining_cells:
                self.place_token(cell, t)
                win = self.check_win()
                self.remove_token(cell)
                if win:
                    return cell

        highest_count = ([], 0)
        for cell in remaining_cells:
            self.place_token(cell, token)
            count = self.count_doubles(token)
            self.remove_token(cell)
            if count > highest_count[1]:
                highest_count = ([cell], count)
            elif count == highest_count[1]:
                highest_count[0].append(cell)
        if highest_count[1] > 0:
            return random.choice(highest_count[0])
        return random.choice(remaining_cells)

    def minimax_choose_move(self, player: Player):
        moves_queue = []
        other_player = self.get_other_player(player)
        remaining_cells = [x for x in self.remaining_cells if type(x) == int]
        for move in remaining_cells:
            self.place_token(move, player.token)
            score = self.minimax(player, other_player, False)
            heappush(moves_queue, (score, move))
            self.remove_token(move)

        score, move = heappop(moves_queue)
        return move

    def minimax(self, player: Player, opponent: Player, is_maximizing: bool):
        if self.check_win(player.token):  # Maximizing player wins
            return 10
        elif self.check_win(opponent.token):  # Minimizing player wins
            return -10

        remaining_cells = [x for x in self.remaining_cells if type(x) == int]
        if len(remaining_cells) == 0:
            return 0

        moves_queue = []
        other_player = self.get_other_player(player)
        for move in remaining_cells:
            if is_maximizing:
                self.place_token(move, player.token)
            else :
                self.place_token(move, opponent.token)
            score = self.minimax(player, opponent, not is_maximizing)
            # priority queue - score is negated to make it descending
            if is_maximizing:
                score = -score
            heappush(moves_queue, (score, move))
            self.remove_token(move)

        score, move = heappop(moves_queue)
        # negate score again to return it to original value
        if is_maximizing:
            score = -score
        return score


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
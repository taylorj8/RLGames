import random
import time
from typing import override
from game import Game, clear_screen

BLANK = " "


# inherit from the Game class
# implements the methods for specific to TicTacToe game
class TicTacToe(Game):
    max_moves = 9
    start_instructions = "Welcome to TicTacToe! The game is played using the numpad. The numbers correspond to squares as follows:"
    input_name = "cell"
    # the indices of all subsets that could contain a winning run
    winning_subsets = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]

    def __init__(self, player1, player2, visualise, board_size=None, max_depth=9, q_table=None):
        super().__init__(player1, player2, visualise, max_depth, q_table)
        # the board is represented as a list of 9 elements, initially all blank
        self.cells = [BLANK] * 9
        self.remaining_cells = [i for i in range(1, 10)]

    # reset the game back to its initial state
    @override
    def reset(self):
        self.cells = [BLANK] * 9
        self.remaining_cells = [i for i in range(1, 10)]
        self.current_token = self.get_tokens()[0]

    # get the indices the cells that are still blank
    @override
    def get_remaining_moves(self) -> list[int]:
        return [x for x in self.remaining_cells if type(x) == int]

    # place a token in a cell
    # as the game is played with the numpad (keys 1-9), the index is 1 less than the key
    @override
    def place_token(self, index: int, token: str = None):
        if token is None:
            token = self.current_token
        self.cells[index - 1] = token
        self.remaining_cells[index - 1] = "■"

    # remove a token from a cell
    @override
    def remove_token(self, index):
        self.cells[index - 1] = BLANK
        self.remaining_cells[index - 1] = index

    # get the board for display
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

    # get the state of the board as a string
    @override
    def get_state(self):
        return "".join(self.cells)

    # check each of the winning subsets to see if the token has won
    # if token is provided, check if all elements are that token
    @override
    def check_win(self, token=None) -> bool:
        def check_subset(subset, token=None):
            if token is None:
                return subset[0] != BLANK and all([x == subset[0] for x in subset])
            return all([x == token for x in subset])
        return any(check_subset([self.cells[i] for i in subset], token) for subset in self.winning_subsets)

    # count the number of winning subsets that contain 2 of the same token and 1 blank cell
    def count_doubles(self, token):
        subsets = map(lambda x: [self.cells[i] for i in x], self.winning_subsets)
        return sum(1 for subset in subsets if subset.count(token) == 2 and subset.count(BLANK) == 1)

    # evaluate the state of the board for the minimax algorithm
    # used if the depth is too low to reach the terminal state
    @override
    def evaluate_early(self, player, opponent) -> int:
        good_doubles = self.count_doubles(player)
        bad_doubles = self.count_doubles(opponent)
        return good_doubles - bad_doubles

    # algorithmically choose a move
    @override
    def algorithm_choose_move(self) -> int:
        token = self.current_token
        if self.visualise:
            clear_screen()
            print(f"Player {token}\n{self.get_board()}")
            time.sleep(0.2)

        # first check if the player can win in the next move - if so, return that move
        # then check if the opponent can win in the next move - if so, block that move
        remaining_cells = self.get_remaining_moves()
        for t in [token, self.get_other(token)]:
            for cell in remaining_cells:
                self.place_token(cell, t)
                win = self.check_win(t)
                self.remove_token(cell)
                if win:
                    return cell

        # if no winning moves, find the move that results in the most doubles - i.e. runs one move away from winning
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
        # if no doubles, choose randomly
        return random.choice(remaining_cells)

    # return the tokens used in the game
    @staticmethod
    @override
    def get_tokens() -> tuple[str, str]:
        return "X", "O"

# start the game - calls the start method of the Game class
if __name__ == "__main__":
    TicTacToe.start()
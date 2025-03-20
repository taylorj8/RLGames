import random
from abc import ABC, abstractmethod
from typing import Tuple

from readchar import readkey
from tqdm import trange

from qlearner import QLearner
from util import *

BLANK = " "


# abstract class for a game
# TicTacToe and Connect4 inherit from this class, overriding the abstract methods to implement the specific game logic
# allows me to reuse logic for the game loop, player selection, and training
class Game(ABC):
    max_moves = 0
    start_instructions = ""

    def __init__(self, player1: Player, player2: Player, visualise: bool, max_depth: int = 42, q_tables=None):
        self.visualise = visualise
        self.players: Tuple[Player, Player] = (player1, player2)
        self.cells = []
        self.remaining_cells = None
        self.max_depth = max_depth
        self.current_token = self.get_tokens()[0]
        if q_tables is None:
            q_tables = {}
        self.q_tables = q_tables

    # check if the game is over, i.e. a win or a tie
    def game_over(self):
        return self.check_win() or not self.get_remaining_moves()

    # runs the game loop and handles the game end
    def play(self, reverse_order=False) -> int:
        winner_index = self.game_loop(reverse_order)

        # print the win message and the final board state
        if self.visualise:
            clear_screen()
        self.print("The game ended in a tie." if winner_index == 2 else f"Player {winner_index + 1} wins!")
        self.print(self.get_board())
        self.await_key()
        return winner_index

    # the main game loop
    # reverse_order is used to alternate the starting player
    def game_loop(self, reverse_order: bool) -> int:
        offset = 1 if reverse_order else 0
        # repeats until the board is full, at which point the game is a tie
        for i in range(self.max_moves):
            player = self.players[(i + offset) % 2]
            pos = self.choose_move(player)  # get the move based on the player type

            # place the token and check for a win
            self.place_token(pos)
            if self.check_win():
                break
            # if no win, swap the tokens and repeat
            self.swap_tokens()
            self.print(f"Player {self.current_token}\n{self.get_board()}")
        # if the board is full there is no winner, the game is a tie; return 2
        winner_index = self.players.index(player) if self.check_win() else 2
        return winner_index

    # choose a move based on the player type
    def choose_move(self, player: Player) -> int:
        match player.type:
            case "human":
                move = self.human_choose_move()
            case "random":
                move = random.choice(self.get_remaining_moves())
            case "algo":
                move = self.algorithm_choose_move()
            case "minimax":
                move = self.minimax_choose_move()
            case "minimax_ab":
                move = self.minimax_choose_move(float("-inf"), float("inf"))
            case "qlearn":
                move = self.qlearn_choose_move()
            case _:
                print("Invalid player type.")
                exit()
        return move

    # function to print a message if visualisation is enabled
    def print(self, message: str):
        if self.visualise:
            print(message)

    # function to wait for a key press if visualisation is enabled
    def await_key(self):
        if self.visualise:
            readkey()

    # function to swap the current token
    def swap_tokens(self):
        self.current_token = self.get_other(self.current_token)

    # get the other token
    def get_other(self, token: str) -> str:
        return self.get_tokens()[1] if token == self.get_tokens()[0] else self.get_tokens()[0]

    # if a human player is involved, display the instructions
    def start_message(self):
        if self.visualise and self.players[0].type == "human" or self.players[1].type == "human":
            clear_screen()
            print(self.start_instructions)
            print(self.get_board(self.remaining_cells))
            print("Press any key to start.")
            readkey()
            clear_screen()

    # reset the game state
    @abstractmethod
    def reset(self):
        pass

    # get the current board for display
    @abstractmethod
    def get_board(self, override=None) -> str:
        pass

    # get a string representation of the game state
    @abstractmethod
    def get_state(self) -> str:
        pass

    # returns true if a win occurs
    # if a token is provided, checks if that token has won
    @abstractmethod
    def check_win(self, token: str = None) -> bool:
        pass

    # evaluate the board state before a win
    # awards points based on how good the state is for the player
    @abstractmethod
    def evaluate_early(self, player: str, opponent: str) -> int:
        pass

    # place a token on the board
    @abstractmethod
    def place_token(self, pos: int, token: str = None):
        pass

    # remove a token from the board
    # used for the minimax algorithm
    # as it places a token to evaluate the board state
    @abstractmethod
    def remove_token(self, pos):
        pass

    # return the available moves
    @abstractmethod
    def get_remaining_moves(self):
        pass

    # allows the human player to choose a move
    # reads the key pressed and returns the corresponding cell
    # handles invalid input
    def human_choose_move(self) -> int:
        while True:
            clear_screen()
            print(f"Player {self.current_token}, choose a {self.input_name}:\n{self.get_board()}")
            key = readkey()
            if key.isdigit() and key != "0":
                key = int(key)
                if key in self.get_remaining_moves():
                    clear_screen()
                    return key

            clear_screen()
            print(f"Select a valid {self.input_name}.\n{self.get_board(self.remaining_cells)}\nPress any button to continue.")
            readkey()

    # choose a move based on the minimax algorithm
    # this is the same for both games - game specific logic is overridden in the respective classes
    # alpha and beta are used for the alpha-beta pruning optimisation - if they are not provided, pruning is not used
    def minimax_choose_move(self, alpha=None, beta=None) -> int:
        player = self.current_token
        best_score = float("-inf")
        best_move = 0

        opponent = self.get_other(player)
        for move in self.get_remaining_moves():
            # place the token, get the best score for that move, and remove the token
            # repeat this for each move to find the best one
            self.place_token(move, player)
            score = self.minimax(player, opponent, 0, False, self.max_depth, alpha, beta)
            self.remove_token(move)

            if score > best_score:
                best_move = move
                best_score = score
        return best_move

    # the minimax algorithm
    def minimax(self, player: str, opponent: str, depth: int, maxing: bool, max_depth, alpha, beta) -> int:
        # reward the player if they win, penalise if the opponent wins
        # reward is higher if the win is sooner, penalty is higher if the loss is later
        if self.check_win(player):
            return max_depth - depth + 1
        elif self.check_win(opponent):
            return -max_depth + depth - 1

        # if there are no moves left the game is a tie, return neutral reward
        remaining_moves = self.get_remaining_moves()
        if len(remaining_moves) == 0:
            return 0

        # if the max depth is reached and no win occurs, evaluate the board state
        if depth == max_depth:
            return self.evaluate_early(player, opponent)

        # recursively call the minimax algorithm for each move
        # the algorithm alternates between maximising and minimising the score
        if maxing:
            best_score = float("-inf")
            for move in remaining_moves:
                # place the token, get the maximum score for the player, and remove the token
                self.place_token(move, player)
                best_score = max(best_score, self.minimax(player, opponent, depth + 1, not maxing, max_depth, alpha, beta))
                self.remove_token(move)

                # alpha-beta pruning
                # if the beta is less than or equal to the alpha, there can be no better move
                # so the loop can be broken
                if alpha is not None:
                    alpha = max(alpha, best_score)
                    if beta <= alpha:
                        break
        else:
            best_score = float("inf")
            for move in remaining_moves:
                # place the token, get the maximum score for the player, and remove the token
                self.place_token(move, opponent)
                best_score = min(best_score, self.minimax(player, opponent, depth + 1, not maxing, max_depth, alpha, beta))
                self.remove_token(move)

                # alpha-beta pruning
                # if the beta is less than or equal to the alpha, there can be no better move
                # so the loop can be broken
                if beta is not None:
                    beta = min(beta, best_score)
                    if beta <= alpha:
                        break
        return best_score

    # choose a move based on the qlearning algorithm
    def qlearn_choose_move(self) -> int:
        # get the game state and the q-table for the current token
        state = self.get_state()
        q_table = self.q_tables[self.current_token]
        # if the state is in the q-table, get the best move based on the q-values
        # if not, choose randomly from the available moves
        if state in q_table:
            moves = self.get_remaining_moves()
            best_q = max(q_table[state][m] for m in moves)
            best_moves = [m for m in moves if q_table[state][m] == best_q]
            return random.choice(best_moves)
        else:
            return random.choice(self.get_remaining_moves())

    # choose a move based on an algorithm designed for the specific game
    # implemented in each game class
    @abstractmethod
    def algorithm_choose_move(self) -> int:
        pass

    # get the tokens for the game
    # simple way to allow me to use different tokens for different games but still share logic
    @staticmethod
    @abstractmethod
    def get_tokens() -> tuple[str, str]:
        pass

    # sets up the training environment for qlearning
    @classmethod
    def training_setup(cls, board_size=None):
        args = sys.argv
        # get the parameters from the command line arguments
        batches = param_or_default(args, "-train", 10)
        batch_size = param_or_default(args, "-b", 50000)
        seed = param_or_default(args, "-s", random.randint(0, 1000000))
        order = param_or_default(args, "-o", "both")
        # set up the game
        game = cls(Player("qlearn"), Player("algo"), False, board_size)

        # set the parameters for the qlearning agents
        # allows for different parameters depending on the game and whether the agent goes first or second
        # done this way as the strategies for going first and second can be different
        # so different rewards give better/worse results
        if cls.__name__ == "TicTacToe":
            first_parameters = Parameters(True, 20.0, -20.0, 2.0, 0.0, 0.1)
            second_parameters = Parameters(False, 50.0, -100.0, 2.0, 0.0, 0.9)
        else:
            grid_size = board_size[0] * board_size[1]
            first_parameters = Parameters(True, grid_size + 5.0, -grid_size - 5.0, -2.0, 0.25, 0.05)
            second_parameters = Parameters(False, grid_size + 5.0, -grid_size - 5.0, -2.0, 0.3, 0.06)

        # train the agents
        QLearner(game, batches, batch_size, seed).train(first_parameters, second_parameters, order)
        print("Training complete.")
        exit()

    # handles the command line arguments and starts the game
    # if -train is in the arguments, sets up the training environment
    @classmethod
    def start(cls, board_size=None):
        args = sys.argv
        if "-train" in args:
            cls.training_setup(board_size)

        # get the parameters from the command line arguments
        player1, player2, games, max_depth = get_from_args(args)
        visualise = "-v" in args or player1 == "human" or player2 == "human"

        # if either player is a qlearning agent, load the q tables
        q_tables = {}
        if player1 == "qlearn" or player2 == "qlearn":
            size = f"{board_size[0]}x{board_size[1]}_" if cls.__name__ == "Connect4" else ""
            q_tables = load_q_tables(cls.__name__, cls.get_tokens(), size, True)

        # initialise the players
        player1 = Player(player1)
        player2 = Player(player2)

        # play the games, recording the wins/losses/ties
        stats = [0, 0, 0]
        game = cls(player1, player2, visualise, board_size, max_depth, q_tables)
        game.start_message()
        for i in trange(games):
            # the starting player alternates each game
            winner_index = game.play(reverse_order=bool(i % 2))
            stats[winner_index] += 1
            game.reset()

        # print the final stats
        clear_screen()
        print(f"Player 1 ({player1.type}) wins: {stats[0]}")
        print(f"Player 2 ({player2.type}) wins: {stats[1]}")
        print(f"Ties: {stats[2]}")

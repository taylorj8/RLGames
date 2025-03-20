import random
from abc import ABC, abstractmethod
from typing import Tuple

from readchar import readkey
from tqdm import trange

from qlearner import QLearner
from util import *

BLANK = " "


class Game(ABC):
    max_moves = 0
    start_instructions = ""

    def __init__(self, player1: Player, player2: Player, visualise: bool, max_depth: int = 42, q_tables=None):
        if q_tables is None:
            q_tables = {}
        self.visualise = visualise
        self.players: Tuple[Player, Player] = (player1, player2)
        self.cells = []
        self.remaining_cells = None
        self.max_depth = max_depth
        if q_tables is None:
            q_tables = {}
        self.q_tables = q_tables
        self.current_token = self.get_tokens()[0]

    def print(self, message: str):
        if self.visualise:
            print(message)

    def await_key(self):
        if self.visualise:
            readkey()

    def swap_tokens(self):
        self.current_token = self.get_other(self.current_token)

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def get_board(self, override=None):
        pass

    @abstractmethod
    def check_win(self, token: str = None) -> bool:
        pass

    @abstractmethod
    def place_token(self, pos: int, token: str = None):
        pass

    @abstractmethod
    def remove_token(self, pos):
        pass

    @abstractmethod
    def get_remaining_moves(self):
        pass

    @abstractmethod
    def get_state(self):
        pass

    def game_over(self):
        return self.check_win() or not self.get_remaining_moves()

    def play(self, reverse_order=False) -> int:
        winner_index = self.game_loop(reverse_order)

        if self.visualise:
            clear_screen()
        if self.check_win():
            self.print(f"Player {winner_index+1} wins!")
        else:
            self.print("The game ended in a tie.")
            winner_index = 2
        self.print(self.get_board())
        self.await_key()
        return winner_index

    def game_loop(self, reverse_order) -> int:
        offset = 1 if reverse_order else 0
        for i in range(self.max_moves):
            player = self.players[(i + offset) % 2]
            pos = self.choose_move(player)

            self.place_token(pos)
            if self.check_win():
                break
            self.swap_tokens()
            self.print(f"Player {self.current_token}\n{self.get_board()}")
        return self.players.index(player)

    def choose_move(self, player: Player) -> int:
        match player.type:
            case "human":
                clear_screen()
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

    @abstractmethod
    def human_choose_move(self) -> int:
        pass

    @abstractmethod
    def algorithm_choose_move(self) -> int:
        pass

    @abstractmethod
    def evaluate_early(self, player: str, opponent: str) -> int:
        pass

    def minimax_choose_move(self, alpha=None, beta=None):
        player = self.current_token
        best_score = float("-inf")
        best_move = 0

        remaining_moves = self.get_remaining_moves()
        opponent = self.get_other(player)
        for move in remaining_moves:
            self.place_token(move, player)
            score = self.minimax(player, opponent, 0, False, self.max_depth, alpha, beta)
            self.remove_token(move)

            if score > best_score:
                best_move = move
                best_score = score
        return best_move

    def minimax(self, player: str, opponent: str, depth: int, maxing: bool, max_depth, alpha, beta):
        if self.check_win(player):
            return max_depth - depth + 1
        elif self.check_win(opponent):
            return -max_depth + depth - 1

        remaining_moves = self.get_remaining_moves()
        if len(remaining_moves) == 0:
            return 0

        if depth == max_depth:
            return self.evaluate_early(player, opponent)

        if maxing:
            best_score = float("-inf")
            for move in remaining_moves:
                self.place_token(move, player)
                best_score = max(best_score, self.minimax(player, opponent, depth + 1, not maxing, max_depth, alpha, beta))
                self.remove_token(move)

                if alpha is not None:
                    alpha = max(alpha, best_score)
                    if beta <= alpha:
                        break
        else:
            best_score = float("inf")
            for move in remaining_moves:
                self.place_token(move, opponent)
                best_score = min(best_score, self.minimax(player, opponent, depth + 1, not maxing, max_depth, alpha, beta))
                self.remove_token(move)

                if beta is not None:
                    beta = min(beta, best_score)
                    if beta <= alpha:
                        break
        return best_score

    def qlearn_choose_move(self) -> int:
        state = self.get_state()
        q_table = self.q_tables[self.current_token]
        if state in q_table:
            moves = self.get_remaining_moves()
            best_q = max(q_table[state][m] for m in moves)
            best_moves = [m for m in moves if q_table[state][m] == best_q]
            return random.choice(best_moves)
        else:
            return random.choice(self.get_remaining_moves())

    @staticmethod
    @abstractmethod
    def get_tokens():
        pass

    def get_other(self, token: str) -> str:
        return self.get_tokens()[1] if token == self.get_tokens()[0] else self.get_tokens()[0]

    def get_other_player(self, player: Player) -> Player:
        return self.players[1] if player == self.players[0] else self.players[0]

    def start_message(self):
        if self.visualise and self.players[0].type == "human" or self.players[1].type == "human":
            clear_screen()
            print(self.start_instructions)
            print(self.get_board(self.remaining_cells))
            print("Press any key to start.")
            readkey()
            clear_screen()

    @classmethod
    def training_setup(cls, board_size=None):
        args = sys.argv
        batches = param_or_default(args, "-train", 10)
        batch_size = param_or_default(args, "-b", 50000)
        seed = param_or_default(args, "-s", random.randint(0, 1000000))
        game = cls(Player("qlearn"), Player("algo"), False, board_size)

        if cls.__name__ == "TicTacToe":
            first_parameters = Parameters(True, 20.0, -20.0, 2.0, 0.0, 0.05)
            second_parameters = Parameters(False, 20.0, -100.0, 5.0, 0.0, 0.15)
        else:
            grid_size = board_size[0] * board_size[1]
            first_parameters = Parameters(True, grid_size + 5.0, -grid_size - 5.0, -2.0, 0.25, 0.05)
            second_parameters = Parameters(False, grid_size + 5.0, -grid_size - 5.0, -2.0, 0.3, 0.06)

        order = param_or_default(args, "-o", "both")

        QLearner(game, batches, batch_size).train(seed, first_parameters, second_parameters, order)
        print("Training complete.")
        exit()

    @classmethod
    def start(cls, board_size=None):
        args = sys.argv
        if "-train" in args:
            cls.training_setup(board_size)
            return

        player1, player2, games, max_depth = get_from_args(args)
        visualise = "-v" in args or player1 == "human" or player2 == "human"

        q_tables = {}
        if player1 == "qlearn" or player2 == "qlearn":
            size = f"{board_size[0]}x{board_size[1]}_" if cls.__name__ == "Connect4" else ""
            q_tables = load_q_tables(cls.__name__, cls.get_tokens(), size, True)

        player1 = Player(player1)
        player2 = Player(player2)

        stats = [0, 0, 0]
        game = cls(player1, player2, visualise, board_size, max_depth, q_tables)
        game.start_message()
        for i in trange(games):
            winner_index = game.play(reverse_order=bool(i % 2))
            # winner_index = game.play()
            stats[winner_index] += 1
            game.reset()

        clear_screen()
        print(f"Player 1 ({player1.type}) wins: {stats[0]}")
        print(f"Player 2 ({player2.type}) wins: {stats[1]}")
        print(f"Ties: {stats[2]}")

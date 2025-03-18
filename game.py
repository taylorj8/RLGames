import os
import pickle
import random
import sys
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

    def __init__(self, player1: Player, player2: Player, visualise: bool, max_depth: int = 42, q_table=None):
        self.visualise = visualise
        self.players: Tuple[Player, Player] = (player1, player2)
        self.cells = []
        self.remaining_cells = None
        self.max_depth = max_depth
        self.q_table = q_table

    def print(self, message: str):
        if self.visualise:
            print(message)

    def await_key(self):
        if self.visualise:
            readkey()

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
    def place_token(self, pos, token: str):
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

    def play(self, reverse_order=False) -> str:
        if self.visualise:
            clear_screen()
            print(self.start_instructions)
            print(self.get_board(self.remaining_cells))
            print("Press any key to start.")
            # readkey()
            clear_screen()

        players = self.players if not reverse_order else list(reversed(self.players))
        token = self.game_loop(players)

        if self.check_win():
            self.print(f"Player {token} wins!")
            winner = token
        else:
            self.print("The game ended in a tie.")
            winner = "Tie"
        self.print(self.get_board())
        self.await_key()
        return winner

    def game_loop(self, players: Tuple[Player, Player]) -> str:
        for i in range(self.max_moves):
            player = players[i % 2]
            col = self.choose_move(player)
            if self.visualise:
                clear_screen()

            self.place_token(col, player.token)
            if self.check_win():
                break
        return player.token

    def choose_move(self, player: Player) -> int:
        match player.type:
            case "human":
                move = self.human_choose_move(player.token)
            case "random":
                move = random.choice(self.get_remaining_moves())
            case "algo":
                move = self.algorithm_choose_move(player.token)
            case "minimax":
                move = self.minimax_choose_move(player.token)
            case "minimax_ab":
                move = self.minimax_choose_move(player.token, float("-inf"), float("inf"))
            case "qlearn":
                move = self.qlearn_choose_move(player.token)
            case _:
                print("Invalid player type.")
                exit()
        return move

    @abstractmethod
    def human_choose_move(self, token: str):
        pass

    @abstractmethod
    def algorithm_choose_move(self, token: str):
        pass

    @abstractmethod
    def evaluate_early(self, player: str, opponent: str) -> int:
        pass

    def minimax_choose_move(self, player: str, alpha=None, beta=None):
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

    def qlearn_choose_move(self, token):
        state = self.get_state()
        min_or_max = max if token == self.players[0].token else min
        if state in self.q_table:
            moves = self.get_remaining_moves()
            best_q = min_or_max(self.q_table[state][m] for m in moves)
            best_moves = [m for m in moves if self.q_table[state][m] == best_q]
            return random.choice(best_moves)
        else:
            return random.choice(self.get_remaining_moves())

    @staticmethod
    @abstractmethod
    def get_tokens():
        pass

    def get_other(self, token: str) -> str:
        return self.players[1].token if token == self.players[0].token else self.players[0].token

    def get_other_player(self, player: Player) -> Player:
        return self.players[1] if player == self.players[0] else self.players[0]

    @classmethod
    def start(cls):
        args = sys.argv
        token1, token2 = cls.get_tokens()
        if "-train" in args:
            episodes = param_or_default(args, "-train", 10000)
            game = cls(Player("qlearn", token1), Player("algo", token2), False)
            QLearner(game, episodes).train()
            print("Training complete.")
            exit()

        player1, player2, games, max_depth = get_from_args(args)
        visualise = "-v" in args or player1 == "human" or player2 == "human"

        q_table = None
        if player1 == "qlearn" or player2 == "qlearn":
            q_table = load_q_table(cls.__name__)

        player1 = Player(player1, token1)
        player2 = Player(player2, token2)

        stats = {player1.token: 0, player2.token: 0, "Tie": 0}
        for i in trange(games):
            game = cls(player1, player2, visualise, max_depth, q_table)

            # winner = game.play(reverse_order=bool(i % 2))
            winner = game.play()
            stats[winner] += 1

        clear_screen()
        print(f"Player {player1.token} ({player1.type}) wins: {stats[player1.token]}")
        print(f"Player {player2.token} ({player2.type}) wins: {stats[player2.token]}")
        print(f"Ties: {stats['Tie']}")

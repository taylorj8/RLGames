import json
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple

from readchar import readkey
from tqdm import trange

BLANK = " "


def clear_screen():
    os.system('cls' if os.name=='nt' else 'clear')

# get the value of a parameter or return the default value
def param_or_default(args, flag, default):
    if flag in args:
        value = args[args.index(flag) + 1]
        if value.isdigit():
            return int(value)
        return args[args.index(flag) + 1].lower()
    return default

# get the values of the parameters from the command line arguments
def get_from_args(args):
    try:
        player1 = param_or_default(args, "-p1", "minimax")
        player2 = param_or_default(args, "-p2", "algorithm")
        games = param_or_default(args, "-g", 1)
        max_depth = param_or_default(args, "-d", 10)
    except:
        print("Usage: python connect4.py -p1 <player1> -p2 <player2> -g <number of games>")
        exit()
    return player1, player2, games, max_depth


@dataclass
class Player:
    type: str
    token: str

class Game(ABC):
    max_moves = 0
    start_instructions = ""

    def __init__(self, player1: Player, player2: Player, max_depth: int, visualise: bool):
        self.visualise = visualise
        self.players = (player1, player2)
        self.cells = []
        self.max_depth = max_depth
        self.remaining_cells = None

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
            case "algo":
                move = self.algorithm_choose_move(player.token)
            case "minimax":
                move = self.minimax_choose_move(player)
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

    def minimax_choose_move(self, player):
        best_score = float("-inf")
        best_move = 0

        remaining_moves = self.get_remaining_moves()
        opponent = self.get_other(player)
        for move in remaining_moves:
            self.place_token(move, player.token)
            score = self.minimax(player, opponent, 0, False, self.max_depth)
            self.remove_token(move)

            if score > best_score:
                best_move = move
                best_score = score
        return best_move

    def minimax(self, player: str, opponent: str, depth: int, maxing: bool, max_depth):
        if self.check_win(player):
            return 10000 - depth
        elif self.check_win(opponent):
            return -10000 + depth

        remaining_moves = self.get_remaining_moves()
        if len(remaining_moves) == 0:
            return 0

        if depth == max_depth:
            return self.evaluate_early(player, opponent)

        if maxing:
            best_score = float("-inf")
            for move in remaining_moves:
                self.place_token(move, player)
                best_score = max(best_score, self.minimax(player, opponent, depth + 1, not maxing, max_depth))
                self.remove_token(move)
        else:
            best_score = float("inf")
            for move in remaining_moves:
                self.place_token(move, opponent)
                best_score = min(best_score, self.minimax(player, opponent, depth + 1, not maxing, max_depth))
                self.remove_token(move)
        return best_score

    @abstractmethod
    def qlearn_choose_move(self, token: str):
        pass

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
        player1, player2, games, max_depth = get_from_args(args)
        visualise = "-v" in args or player1 == "human" or player2 == "human"

        token1, token2 = cls.get_tokens()
        player1 = Player(player1, token1)
        player2 = Player(player2, token2)

        stats = {player1.token: 0, player2.token: 0, "Tie": 0}
        for i in trange(games):
            game = cls(player1, player2, max_depth, visualise)

            winner = game.play(reverse_order=bool(i % 2))
            stats[winner] += 1

        clear_screen()
        print(f"Player {player1.token} ({player1.type}) wins: {stats[player1.token]}")
        print(f"Player {player2.token} ({player2.type}) wins: {stats[player2.token]}")
        print(f"Ties: {stats['Tie']}")

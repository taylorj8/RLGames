import os
import sys
from abc import ABC, abstractmethod
from typing import Tuple

from readchar import readkey
from tqdm import trange

from util import get_from_args


def clear_screen():
    os.system('cls' if os.name=='nt' else 'clear')


class Game(ABC):
    max_moves = 0
    start_instructions = ""

    def __init__(self, player1: Tuple[str, str], player2: Tuple[str, str], visualise: bool):
        self.visualise = visualise
        self.players = (player1, player2)
        self.guide = None

    def print(self, message):
        if self.visualise:
            print(message)

    def await_key(self):
        if self.visualise:
            readkey()

    @abstractmethod
    def get_board(self, override=None):
        pass

    @abstractmethod
    def check_win(self):
        pass

    @abstractmethod
    def place_token(self, pos, token):
        pass

    def play(self, reverse_order=False):
        if self.visualise:
            clear_screen()
            print(self.start_instructions)
            print(self.get_board(self.guide))
            print("Press any key to start.")
            readkey()
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

    def game_loop(self, players):
        token = ""
        for i in range(self.max_moves):
            player, token = players[i % 2]
            col = self.choose_move(player, token)

            self.place_token(col, token)
            if self.check_win():
                break
            if self.visualise:
                clear_screen()
        return token

    def choose_move(self, player, token):
        match player:
            case "human":
                move = self.human_choose_move(token)
            case "algorithm":
                move = self.algorithm_choose_move(token)
            case "minimax":
                move = self.minimax_choose_move(token)
            case "qlearning":
                move = self.qlearning_choose_move(token)
            case _:
                print("Invalid player type.")
                exit()
        return move

    @abstractmethod
    def human_choose_move(self, token):
        pass

    @abstractmethod
    def algorithm_choose_move(self, token):
        pass

    @abstractmethod
    def minimax_choose_move(self, token):
        pass

    @abstractmethod
    def qlearning_choose_move(self, token):
        pass

    @staticmethod
    @abstractmethod
    def get_tokens():
        pass

    def get_other(self, token):
        return self.players[1][1] if token == self.players[0][1] else self.players[0][1]

    @classmethod
    def start(cls):
        player1, player2, games = get_from_args(sys.argv)
        token1, token2 = cls.get_tokens()
        player1 = (player1, token1)
        player2 = (player2, token2)

        stats = {token1: 0, token2: 0, "Tie": 0}
        for i in trange(games):
            visualise = False if games > 1 and player1 != "human" and player2 != "human" else True
            game = cls(player1, player2, visualise)

            winner = game.play(reverse_order=bool(i % 2))
            stats[winner] += 1

        clear_screen()
        print(f"Player {player1[1]} ({player1[0]}) wins: {stats[token1]}")
        print(f"Player {player2[1]} ({player2[0]}) wins: {stats[token2]}")
        print(f"Ties: {stats['Tie']}")

import json
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple

from readchar import readkey
from tqdm import trange

from player import Player
from util import get_from_args

BLANK = " "


def clear_screen():
    os.system('cls' if os.name=='nt' else 'clear')


class Game(ABC):
    max_moves = 0
    start_instructions = ""

    def __init__(self, player1: Player, player2: Player, visualise: bool):
        self.visualise = visualise
        self.players = (player1, player2)
        self.cells = []
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

            self.place_token(col, player.token)
            if self.check_win():
                break
            if self.visualise:
                clear_screen()
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

    def minimax_choose_move(self, player: Player):
        board_state = "".join(self.cells)
        if board_state in player.move_cache:
            move = player.move_cache[board_state]
            return player.move_cache[board_state]

        best_score = -float("inf")
        best_move = None
        for move in [i for i in range(9) if self.cells[i] == BLANK]:
            self.cells[move] = player.token
            score = self.minimax(player, False)
            self.cells[move] = BLANK
            if score > best_score:
                best_score = score
                best_move = move

        player.move_cache[board_state] = best_move
        player.save_cache(self.__class__.__name__, "minimax")
        return best_move



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
        player1, player2, games = get_from_args(args)
        # if "-t" in args:
        #     player1.


        token1, token2 = cls.get_tokens()
        player1 = Player(player1, token1, cls.__name__)
        player2 = Player(player2, token2, cls.__name__)

        stats = {player1.token: 0, player2.token: 0, "Tie": 0}
        for i in trange(games):
            visualise = False if games > 1 and player1 != "human" and player2 != "human" else True
            game = cls(player1, player2, visualise)

            winner = game.play(reverse_order=bool(i % 2))
            stats[winner] += 1

        clear_screen()
        print(f"Player {player1.token} ({player1.type}) wins: {stats[player1.token]}")
        print(f"Player {player2.token} ({player2.type}) wins: {stats[player2.token]}")
        print(f"Ties: {stats['Tie']}")

import json
import pickle
import os
import sys
from dataclasses import dataclass


# dataclass for the player type
# class used so players of the same type can be differentiated
@dataclass
class Player:
    number: int
    type: str


# dataclass for the qlearning parameters of the game
@dataclass()
class Parameters:
    goes_first: bool
    win_reward: float
    loss_reward: float
    draw_reward: float
    loss_threshold: float
    draw_threshold: float


# class for game stats
class Stats:
    def __init__(self, game:str, player1: str, player2: str, optional_params: str = ""):
        self.game = game
        self.id = f"{player1}_{player2}_{optional_params}"
        self.games = 0
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.win_history = []
        self.number_of_moves = []
        self.game_times = []

    def __str__(self):
        return f"""Wins: {self.wins} | Losses: {self.losses} | Draws: {self.draws}
Avg. moves: {sum(self.number_of_moves) / self.games} | Avg. time: {sum(self.game_times) / self.games}"""

    def update(self, winner: int, moves: int, time: float):
        self.add_winner(winner)
        self.number_of_moves.append(moves)
        self.game_times.append(time)

    def add_winner(self, winner: int):
        self.games += 1
        self.win_history.append(winner)
        match winner:
            case 0:
                self.draws += 1
            case 1:
                self.wins += 1
            case 2:
                self.losses += 1

    def save_to_csv(self):
        with open(f"stats/{self.game}/{self.id}_{self.games}.csv", "w") as file:
            file.write("Winner,Number of moves,Time\n")
            for i in range(self.games):
                file.write(f"{self.win_history[i]},{self.number_of_moves[i]},{self.game_times[i]}\n")



# clear the screen
def clear_screen():
    os.system('cls' if os.name=='nt' else 'clear')


# get the value of a parameter or return the default value
def param_or_default(args, flag, default):
    if flag in args:
        value = args[args.index(flag) + 1]
        if value.startswith("-"):
            return default
        if value.isdigit():
            return int(value)
        return args[args.index(flag) + 1].lower()
    return default


# get the values of the parameters from the command line arguments
def get_from_args(args):
    try:
        player1 = param_or_default(args, "-p1", "human")
        player2 = param_or_default(args, "-p2", "human")
        games = param_or_default(args, "-g", 1)
        max_depth = param_or_default(args, "-d", sys.maxsize)
    except:
        print("Usage: python connect4.py -p1 <player1> -p2 <player2> -g <number of games>")
        exit()
    return player1, player2, games, max_depth


# load the two q-tables for the game
def load_q_tables(game: str, tokens: list[str], size="", pickled=False) -> dict:
    return {tokens[0]: load_q_table(f"{game}_{size}first", pickled), tokens[1]: load_q_table(f"{game}_{size}second", pickled)}


# load a q-table from a file
# handles both json and pickle files
def load_q_table(name: str, pickled: bool) -> dict:
    file_name = f"q_tables/{name}.pkl" if pickled else f"q_tables/{name}.json"
    mode = 'rb' if pickled else 'r'
    if not os.path.exists(file_name):
        print(f"Q-learning has not been trained for {name}.")
        exit()
    with open(file_name, mode) as file:
        if pickled:
            return pickle.load(file)
        else:
            table = json.load(file)
        return {k: {int(k2): v2 for k2, v2 in v.items()} for k, v in table.items()}

import json
import pickle
import os
import sys
from dataclasses import dataclass


@dataclass
class Player:
    type: str

@dataclass()
class Parameters:
    goes_first: bool
    win_reward: float
    loss_reward: float
    draw_reward: float
    loss_threshold: float
    draw_threshold: float


def swap_order(player1: Player, player2: Player):
    player1.order, player2.order = player2.order, player1.order


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
        player1 = param_or_default(args, "-p1", "minimax")
        player2 = param_or_default(args, "-p2", "algo")
        games = param_or_default(args, "-g", 1)
        max_depth = param_or_default(args, "-d", sys.maxsize)
    except:
        print("Usage: python connect4.py -p1 <player1> -p2 <player2> -g <number of games>")
        exit()
    return player1, player2, games, max_depth


def load_q_tables(game: str, tokens: list[str], pickled=False) -> dict:
    return {tokens[0]: load_q_table(f"{game}_first", pickled), tokens[1]: load_q_table(f"{game}_second", pickled)}

def load_q_table(name: str, pickled: bool) -> dict:
    file_name = f"q_tables/{name}.pkl" if pickled else f"q_tables/{name}.json"
    if not os.path.exists(file_name):
        print(f"Q-learning has not been trained for {name}.")
        exit()
    with open(file_name, "r") as file:
        if pickled:
            return pickle.load(file)
        else:
            table = json.load(file)
        return {k: {int(k2): v2 for k2, v2 in v.items()} for k, v in table.items()}

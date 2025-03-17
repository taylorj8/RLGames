import os
import pickle
import sys
from dataclasses import dataclass


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
        max_depth = param_or_default(args, "-d", sys.maxsize)
    except:
        print("Usage: python connect4.py -p1 <player1> -p2 <player2> -g <number of games>")
        exit()
    return player1, player2, games, max_depth


def load_q_table(game: str) -> dict:
    file_name = f"q_tables/{game}.pkl"
    if not os.path.exists(file_name):
        print(f"Q-learning has not been trained for {game}.")
        exit()
    with open(file_name, "rb") as f:
        return pickle.load(f)


@dataclass
class Player:
    type: str
    token: str
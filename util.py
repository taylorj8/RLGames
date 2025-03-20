import json
import pickle
import os
import sys
from dataclasses import dataclass


# dataclass for the player type
# class used so players of the same type can be differentiated
@dataclass
class Player:
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
        player1 = param_or_default(args, "-p1", "minimax")
        player2 = param_or_default(args, "-p2", "algo")
        games = param_or_default(args, "-g", 1)
        max_depth = param_or_default(args, "-d", None)
    except:
        print("Usage: python connect4.py -p1 <player1> -p2 <player2> -g <number of games>")
        exit()
    return player1, player2, games, max_depth


# load the two q-tables for the game
def load_q_tables(game: str, tokens: tuple[str, str], size="", pickled=False) -> dict:
    return {tokens[0]: load_from_file(f"q_tables/{game}_{size}first", pickled), tokens[1]: load_from_file(f"q_tables/{game}_{size}second", pickled)}


# load a dictionary from a file
# handles both json and pickle files
def load_from_file(name: str, pickled: bool, exit_if_missing=True) -> dict:
    file_name = f"{name}.pkl" if pickled else f"{name}.json"
    mode = 'rb' if pickled else 'r'
    if not os.path.exists(file_name):
        if exit_if_missing:
            print(f"Missing file: {name}.")
            exit()
        return {}
    with open(file_name, mode) as file:
        if pickled:
            return pickle.load(file)
        else:
            table = json.load(file)
        return {k: {int(k2): v2 for k2, v2 in v.items()} for k, v in table.items()}


# save the dictionary to a file
def save_to_file(file_name: str, data=dict, pickled=False):
    file_name = f"{file_name}.pkl" if pickled else f"{file_name}.json"
    mode = 'wb' if pickled else 'w'
    with open(file_name, mode) as file:
        pickle.dump(data, file) if pickled else json.dump(data, file)

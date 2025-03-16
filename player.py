import json
import os


class Player:
    def __init__(self, type: str, token: str, game: str):
        self.type = type
        self.token = token
        self.move_cache = {}
        if type in ["minimax", "qlearning"]:
            self.load_cache(game, type)

    def load_cache(self, game: str, algorithm: str):
        file_name = f"cache/{game}_{algorithm}.json"
        if os.path.exists(file_name):
            with open(file_name, "r") as file:
                self.move_cache = json.load(file)
        else:
            self.move_cache = {}

    def save_cache(self, game: str, algorithm: str):
        with open(f"cache/{game}_{algorithm}.json", "w") as file:
            json.dump(self.move_cache, file)

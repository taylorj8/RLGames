import json
import pickle
import random

from tqdm import trange


class QLearner:
    def __init__(self, game, episodes: int, learning_rate: float, discount_factor: float):
        self.q_table = {} # state: (move: q_value)
        self.game = game
        self.episodes = episodes
        self.alpha = learning_rate
        self.gamma = discount_factor
        self.epsilon = 0.5


    def choose_move(self, state: str) -> int:
        if state not in self.q_table or random.uniform(0, 1) < self.epsilon:
            return random.choice(self.game.get_remaining_moves())
        else:
            moves = self.game.get_remaining_moves()
            max_q = max(self.q_table[state][m] for m in moves)
            best_moves = [m for m in moves if self.q_table[state][m] == max_q]
            return random.choice(best_moves)

    def update_q_table(self, state: str, next_state: str, move: int, reward: int):
        if state in self.q_table:
            q_values = self.q_table[state]
        else:
            q_values = {a: 0 for a in self.game.get_remaining_moves()}
            q_values[move] = 0

        if next_state in self.q_table:
            max_next_q = max(self.q_table[next_state].values())
        else:
            max_next_q = 0

        if move not in q_values:
            q_values[move] = 0

        # reward function
        q_values[move] += self.alpha * (reward + self.gamma * max_next_q - q_values[move])
        self.q_table[state] = q_values

    def train(self):
        for episode in trange(self.episodes):
            # alternate going first and second
            player: str = self.game.players[episode % 2].token
            while not self.game.game_over():
                state = self.game.get_state()
                move = self.choose_move(state)
                self.game.place_token(move, player)
                next_state = self.game.get_state()

                if self.game.game_over():
                    if self.game.check_win(player):
                        reward = 10
                    elif not self.game.get_remaining_moves():
                        reward = 0
                    else:
                        reward = -10
                    self.update_q_table(state, next_state, move, reward)
                else:
                    player = self.game.get_other(player)
                    self.update_q_table(state, next_state, move, 0)
            self.epsilon *= 0.99
            self.game.reset()

        self.save_q_table(f"q_tables/{self.game.__class__.__name__}.pkl")

    def save_q_table(self, file_name: str):
        with open(file_name, "wb") as f:
            pickle.dump(self.q_table, f)

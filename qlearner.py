import json
import random
from tqdm import trange


default_q = 0.0

class QLearner:
    def __init__(self, game, episodes: int):
        self.q_table = {} # state: (move: q_value)
        self.game = game
        self.episodes = episodes
        self.alpha = 0.5
        self.gamma = 1.0
        self.epsilon = 0.1


    def choose_move(self, state: str, maxing: bool) -> int:
        if state not in self.q_table or random.uniform(0, 1) < self.epsilon:
            return random.choice(self.game.get_remaining_moves())

        moves = self.game.get_remaining_moves()
        if maxing:
            max_q = max(self.q_table[state][m] for m in moves)
            best_moves = [m for m in moves if self.q_table[state][m] == max_q]
        else:
            min_q = min(self.q_table[state][m] for m in moves)
            best_moves = [m for m in moves if self.q_table[state][m] == min_q]
        return random.choice(best_moves)

    def update_q_table(self, state: str, next_state: str, move: int, reward: float):
        if state in self.q_table:
            q_values = self.q_table[state]
        else:
            q_values = {a: default_q for a in self.game.get_remaining_moves()}
            q_values[move] = default_q

        if next_state in self.q_table:
            max_next_q = max(self.q_table[next_state].values())
        else:
            max_next_q = default_q

        if move not in q_values:
            q_values[move] = default_q

        # reward function
        # q_values[move] += self.alpha * (reward + self.gamma * max_next_q - q_values[move])
        q_values[move] = (q_values[move] * (1 - self.alpha)) + (self.alpha * reward) + (self.alpha * self.gamma * max_next_q)
        self.q_table[state] = q_values

    def train(self):
        for episode in trange(self.episodes):
            original_player: str = self.game.players[0].token
            current_player = original_player
            while not self.game.game_over():
                state = self.game.get_state()
                move = self.choose_move(state, current_player == original_player)
                self.game.place_token(move, current_player)
                next_state = self.game.get_state()

                if self.game.game_over():
                    if self.game.check_win(original_player):
                        reward = 1.0
                    elif not self.game.get_remaining_moves():
                        reward = 0.0
                    else:
                        reward = -1.0
                    self.update_q_table(state, next_state, move, reward)
                else:
                    current_player = self.game.get_other(current_player)
                    # self.game.place_token(random.choice(self.game.get_remaining_moves()), other_player)
                    # reward = self.game.evaluate_early(current_player, self.game.get_other(current_player))
                    self.update_q_table(state, next_state, move, 0.0)
            # self.epsilon -= 1 / self.episodes
            self.game.reset()

        self.save_q_table(f"q_tables/{self.game.__class__.__name__}.json")

    def save_q_table(self, file_name: str):
        with open(file_name, "w") as f:
            json.dump(self.q_table, f)

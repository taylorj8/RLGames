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
        self.epsilon = 0.5

    def get_q_value(self, state, move):
        if state not in self.q_table:
            self.q_table[state] = {m: default_q for m in self.game.get_remaining_moves()}
        if move not in self.q_table[state]:
            self.q_table[state] = default_q
        return self.q_table[state][move]

    def choose_move(self, state: str) -> int:
        remaining_moves = self.game.get_remaining_moves()
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(remaining_moves)
        q_values = [self.get_q_value(state, move) for move in remaining_moves]

        max_q = max(q_values)
        if q_values.count(max_q) > 1:
            best_moves = [i for i in range(len(remaining_moves)) if q_values[i] == max_q]
            i = random.choice(best_moves)
        else:
            i = q_values.index(max_q)
        return remaining_moves[i]

    def remaining_moves_from_state(self, state: str) -> list[int]:
        return [i for i, char in enumerate(state, 1) if char == ' ']

    def update_q_table(self, state: str, next_state: str, move: int, reward: float):
        next_q_values = [self.get_q_value(next_state, next_move) for next_move in self.remaining_moves_from_state(next_state)]
        max_next_q = max(next_q_values) if next_q_values else default_q
        self.q_table[state][move] += self.alpha * (reward + self.gamma * max_next_q - self.q_table[state][move])

    def train(self):

        for e in trange(self.episodes):
            state = self.game.get_state()
            token = self.game.get_tokens()[0]
            while not self.game.game_over():
                move = self.choose_move(state)
                self.game.place_token(move, token)
                next_state = self.game.get_state()

                if self.game.check_win(token):
                    reward = 1.0
                elif self.game.get_remaining_moves() == 0:
                    reward = 0.0
                else:
                    reward = -1.0

                self.update_q_table(state, next_state, move, reward)
                state = next_state
                token = self.game.get_other(token)

        self.save_q_table(f"q_tables/{self.game.__class__.__name__}.json")

    def save_q_table(self, file_name: str):
        with open(file_name, "w") as f:
            json.dump(self.q_table, f)

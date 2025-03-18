import json
import random
import sys

from tqdm import trange


default_q = 0.0

class QLearner:
    def __init__(self, game, episodes: int):
        self.q_table = {} # state: (move: q_value)
        self.game = game
        self.episodes = episodes
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.9

    def get_moves_from_state(self, state: str) -> list[int]:
        return [i for i, char in enumerate(state, 1) if char == " "]

    def get_q_value(self, state, move):
        if state not in self.q_table:
            self.q_table[state] = {m: default_q for m in self.get_moves_from_state(state)}
        if move not in self.q_table[state]:
            self.q_table[state][move] = default_q
        return self.q_table[state][move]

    def choose_move(self, state: str, min_or_max: callable) -> int:
        remaining_moves = self.game.get_remaining_moves()
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(remaining_moves)
        q_values = [self.get_q_value(state, move) for move in remaining_moves]

        max_q = min_or_max(q_values)
        best_moves = [i for i, q in enumerate(q_values) if q == max_q]
        i = random.choice(best_moves)
        return remaining_moves[i]

    def update_q_table(self, state: str, next_state: str, move: int, reward: float) -> float:
        if state not in self.q_table:
            self.q_table[state] = {m: default_q for m in self.get_moves_from_state(state)}

        next_moves = self.get_moves_from_state(next_state)

        next_q_values = [self.get_q_value(next_state, next_move) for next_move in next_moves]
        best_next_q = max(next_q_values) if next_q_values else default_q
        diff = reward + self.gamma * best_next_q - self.q_table[state][move]
        self.q_table[state][move] += self.alpha * diff
        return abs(diff)

    def blocked_win(self, move: int, other_token: str) -> bool:
        self.game.place_token(move, other_token)
        blocked = self.game.check_win(other_token)
        self.game.remove_token(move)
        return blocked

    def train(self):
        for i in range(1, sys.maxsize):
            for _ in trange(self.episodes):
                token = self.game.get_tokens()[0]
                state = self.game.get_state()
                while not self.game.game_over():
                    if token == "X":
                        move = self.choose_move(state, max)
                    else:
                        move = self.choose_move(state, min)
                    blocked = self.blocked_win(move, self.game.get_other(token))
                    self.game.place_token(move, token)

                    # Reward is assigned from the active player's perspective.
                    if self.game.check_win("X"):
                        reward = 50.0  # win for active player
                    elif self.game.check_win("O"):
                        reward = -50.0  # loss for active player
                    elif self.game.get_remaining_moves() == 0:
                        reward = 0.0  # draw
                    else:
                        # reward the player for creating doubles
                        reward = self.game.count_doubles("X") - self.game.count_doubles("O")
                        if blocked:
                            if token == "X":
                                reward += 5.0
                            else:
                                reward -= 5.0
                        # reward = 0.0

                    token = self.game.get_other(token)
                    next_state = self.game.get_state()

                    self.update_q_table(state, next_state, move, reward)

                    state = next_state
                self.game.reset()

            stats = [0, 0, 0]
            self.game.q_table = self.q_table
            for _ in range(100):
                winner = self.game.play()
                self.game.reset()
                if winner == "X":
                    stats[0] += 1
                elif winner == "O":
                    stats[1] += 1
                else:
                    stats[2] += 1

            total_episodes = i * self.episodes
            print(f"Episodes: {total_episodes}\nWins: {stats[0]} | Losses: {stats[1]} | Draws: {stats[2]}")
            # break if no losses
            if stats[1] == 0:
                break
            # self.epsilon = max(0.1, self.epsilon * 0.99999)

        self.save_q_table(f"q_tables/{self.game.__class__.__name__}.json")

    def save_q_table(self, file_name: str):
        with open(file_name, "w") as f:
            json.dump(self.q_table, f)

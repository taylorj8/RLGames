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

    def blocked_win(self, move: int, token: str) -> bool:
        other_token = self.game.get_other(token)
        self.game.place_token(move, other_token)
        blocked = self.game.check_win(other_token)
        self.game.remove_token(move)
        return blocked

    def train(self):
        seed = random.randint(0, 1000000)
        print("Training with seed:", seed)
        random.seed(seed)
        tokens = self.game.get_tokens()
        for i in range(1, sys.maxsize):
            for e in trange(self.episodes):
                token = tokens[0]
                state_history = []
                move_history = []

                # Play a game and record states/moves
                state = self.game.get_state()
                while not self.game.game_over():
                    move = self.choose_move(state, max)
                    state_history.append(state)
                    move_history.append(move)

                    self.game.place_token(move, token)
                    state = self.game.get_state()
                    token = self.game.get_other(token)

                # Game is over - determine reward for final outcome
                if self.game.check_win(tokens[0]):
                    final_reward = 100.0  # Agent wins
                elif self.game.check_win(tokens[1]):
                    final_reward = -100.0  # Agent loses
                else:
                    final_reward = 0.0  # Draw

                # Backpropagate the final reward to all moves leading up to it
                for state, move in zip(reversed(state_history), reversed(move_history)):
                    self.update_q_table(state, state, move, final_reward)  # No next_state since game is over
                    final_reward *= 0.9  # Discount reward slightly for earlier moves
                self.game.reset()

            self.game.q_table = self.q_table

            undefeated = True
            total_episodes = i * self.episodes
            print(f"Episodes: {total_episodes}")
            for reverse in [False, True]:
                stats = [0, 0, 0]
                for _ in range(100):
                    winner = self.game.play(reverse_order=reverse)
                    self.game.reset()
                    stats[winner] += 1
                if stats[1] > 0:
                    undefeated = False
                print(f"{"Going second - " if reverse else "Going first - "}Wins: {stats[0]} | Losses: {stats[1]} | Draws: {stats[2]}")

            # break if no losses
            if undefeated:
                break
            # self.epsilon = max(0.1, self.epsilon * 0.99999)

        self.save_q_table(f"q_tables/{self.game.__class__.__name__}.json")

    def save_q_table(self, file_name: str):
        with open(file_name, "w") as f:
            json.dump(self.q_table, f)

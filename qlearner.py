import json
import random

from tqdm import trange

from util import Parameters

default_q = 0.0

class QLearner:
    def __init__(self, game, batches: int, batch_size: int):
        self.q_table = {} # state: (move: q_value)
        self.game = game
        self.batches = batches
        self.batch_size = batch_size
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 1.0

    def reset(self):
        self.q_table = {}
        self.alpha = 0.1
        self.epsilon = 1.0

    def get_moves_from_state(self, state: str) -> list[int]:
        if self.game.__class__.__name__ == "Connect4":
            state = state[35:]
        return [i for i, char in enumerate(state, 1) if char == " "]

    def get_q_value(self, state, move):
        if state not in self.q_table:
            self.q_table[state] = {m: default_q for m in self.game.get_remaining_moves()}
        if move not in self.q_table[state]:
            self.q_table[state][move] = default_q
        return self.q_table[state][move]

    def choose_move(self, state: str) -> int:
        remaining_moves = self.game.get_remaining_moves()
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(remaining_moves)
        q_values = [self.get_q_value(state, move) for move in remaining_moves]

        max_q = max(q_values)
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

    def train_once(self, params: Parameters):
        print("Training agent that goes first" if params.goes_first else "Training agent that goes second")
        tokens = self.game.get_tokens()
        agent, opponent = (tokens[0], tokens[1]) if params.goes_first else (tokens[1], tokens[0])
        for i in range(1, self.batches+1):
            for e in trange(self.batch_size):
                token = tokens[0]
                state_history = []
                move_history = []

                # Play a game and record states/moves
                state = self.game.get_state()
                move_number = 0
                while not self.game.game_over():
                    if token == agent:
                        move = self.choose_move(state)
                        state_history.append(state)
                        move_history.append(move)
                    else:
                        move = random.choice(self.game.get_remaining_moves())

                    self.game.place_token(move, token)
                    state = self.game.get_state()
                    token = self.game.get_other(token)
                    move_number += 1

                # Game is over - determine reward for final outcome
                if self.game.check_win(agent):
                    # final_reward = 20.0 - move_number  # Agent wins
                    final_reward = params.win_reward - move_number
                elif self.game.check_win(opponent):
                    # final_reward = -100.0 - move_number  # Agent loses
                    final_reward = params.loss_reward + move_number
                else:
                    # final_reward = 5.0  # Draw
                    final_reward = params.draw_reward

                # Backpropagate the final reward to all moves leading up to it
                for state, move in zip(reversed(state_history), reversed(move_history)):
                    self.update_q_table(state, state, move, final_reward)
                    # final_reward *= self.gamma # Discount reward slightly for earlier moves
                self.game.reset()

                self.alpha = max(0.01, self.alpha * 0.99999)
                self.epsilon = max(0.1, self.epsilon * 0.99999)

            self.game.q_tables[agent] = self.q_table

            total_episodes = i * self.batch_size
            print(f"Total episodes: {total_episodes}")
            stats = [0, 0, 0]
            testing_games = 1000
            for j in range(testing_games):
                winner = self.game.play(not params.goes_first)
                self.game.reset()
                stats[winner] += 1
            print(f"Wins: {stats[0]} | Losses: {stats[1]} | Draws: {stats[2]}")

            # break if no losses and under 10% ties
            if stats[1] == testing_games * params.loss_threshold and stats[2] < testing_games * params.draw_threshold:
                break

        file_name = f"q_tables/{self.game.__class__.__name__}_first.json" if params.goes_first else f"q_tables/{self.game.__class__.__name__}_second.json"
        self.save_q_table(file_name)

    def train(self, seed: int, first_params: Parameters, second_params: Parameters, order: str):
        print("Seed:", seed)
        random.seed(seed)

        if order == "first" or order == "both":
            self.train_once(first_params)
            self.reset()
        if order == "second" or order == "both":
            self.train_once(second_params)

    def save_q_table(self, file_name: str):
        with open(file_name, "w") as file:
            json.dump(self.q_table, file)

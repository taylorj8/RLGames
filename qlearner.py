import json
import pickle
import random
from tqdm import trange
from util import Parameters

# default q value for states
default_q = 0.0


# handles all the logic for training a q-learning agent
class QLearner:
    def __init__(self, game, batches: int, batch_size: int, seed: int):
        random.seed(seed)
        print("Seed:", seed)

        self.q_table = {} # state: (move: q_value)
        self.game = game
        self.batches = batches
        self.batch_size = batch_size
        self.alpha = 0.1
        self.gamma = 0.95
        self.epsilon = 0.95

    # reset the q-table, learning rate and exploration rate
    def reset(self):
        self.q_table = {}
        self.alpha = 0.1
        self.epsilon = 0.95

    # get the available moves from the string state
    def get_moves_from_state(self, state: str) -> list[int]:
        # if the game is connect4, the available moves is based on the top row
        if self.game.__class__.__name__ == "Connect4":
            top_row_index = self.game.width * (self.game.height-1)
            state = state[top_row_index:]
        return [i for i, char in enumerate(state, 1) if char == " "]

    # get the q-value for a state and move
    # if the state or move is not in the q-table, add it with the default q-value
    def get_q_value(self, state, move):
        if state not in self.q_table:
            self.q_table[state] = {m: default_q for m in self.game.get_remaining_moves()}
        if move not in self.q_table[state]:
            self.q_table[state][move] = default_q
        return self.q_table[state][move]

    # choose a move based on the epsilon-greedy policy
    def choose_move(self, state: str) -> int:
        remaining_moves = self.game.get_remaining_moves()
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(remaining_moves)
        q_values = [self.get_q_value(state, move) for move in remaining_moves]

        # get the moves with the highest q-value, if more than one, choose randomly from them
        best_moves = [i for i, q in enumerate(q_values) if q == max(q_values)]
        i = random.choice(best_moves)
        return remaining_moves[i]

    # update the q-table based on the reward and the q-values of the next state
    def update_q_table(self, state: str, next_state: str, move: int, reward: float):
        if state not in self.q_table:
            self.q_table[state] = {m: default_q for m in self.get_moves_from_state(state)}

        next_moves = self.get_moves_from_state(next_state)

        next_q_values = [self.get_q_value(next_state, next_move) for next_move in next_moves]
        best_next_q = max(next_q_values) if next_q_values else default_q
        # reward + discounted best next q-value - current q-value
        diff = reward + self.gamma * best_next_q - self.q_table[state][move]
        self.q_table[state][move] += self.alpha * diff

    # check if a move will block a win for the opponent
    # originally used as an intermediary reward for the agent
    # found it wasn't effective and removed it
    def blocked_win(self, move: int, token: str) -> bool:
        other_token = self.game.get_other(token)
        self.game.place_token(move, other_token)
        blocked = self.game.check_win(other_token)
        self.game.remove_token(move)
        return blocked

    # main training logic
    # plays games and updates the q-table based on the outcomes
    def train_once(self, params: Parameters):
        # agent that goes first is trained separately to the agent that goes second
        print("Training agent that goes first" if params.goes_first else "Training agent that goes second")
        tokens = self.game.get_tokens()
        agent, opponent = (tokens[0], tokens[1]) if params.goes_first else (tokens[1], tokens[0])

        # play games in batches
        # after each batch, test the agent against an opponent
        # if the agent loses more than the loss threshold and ties more than the draw threshold, continue training
        for i in range(1, self.batches+1):
            for e in trange(self.batch_size):
                token = tokens[0]
                state_history = []
                move_history = []

                # play a game
                state = self.game.get_state()
                move_number = 0
                while not self.game.game_over():
                    # the agent chooses a move based on the epsilon-greedy policy
                    # the moves and states leading up to the final outcome are stored
                    if token == agent:
                        move = self.choose_move(state)
                        state_history.append(state)
                        move_history.append(move)
                    else:
                        # opponent chooses a move randomly half of the time and algorithmically the other half
                        # I found this to be more effective than choosing randomly all the time
                        if random.uniform(0, 1) < 0.5:
                            move = random.choice(self.game.get_remaining_moves())
                        else:
                            move = self.game.algorithm_choose_move()

                    # place the token and update the state
                    self.game.place_token(move, token)
                    state = self.game.get_state()
                    token = self.game.get_other(token)
                    move_number += 1

                # game is over - determine reward for final outcome
                if self.game.check_win(agent):
                    final_reward = params.win_reward - move_number
                elif self.game.check_win(opponent):
                    final_reward = params.loss_reward + move_number
                else:
                    final_reward = params.draw_reward

                # the q-table is updated for each state and move leading up to the final outcome
                # the reward is discounted slightly for earlier moves
                for state, move in zip(reversed(state_history), reversed(move_history)):
                    self.update_q_table(state, state, move, final_reward)
                    final_reward *= self.gamma

                # reset the game and decrease the learning and exploration rates
                self.game.reset()
                self.alpha = max(0.01, self.alpha * 0.999999)
                self.epsilon = max(0.1, self.epsilon * 0.999999)

            # after each batch, test the agent against an opponent
            self.game.q_tables[agent] = self.q_table
            total_episodes = i * self.batch_size
            print(f"Total episodes: {total_episodes}")
            stats = [0, 0, 0]
            testing_games = 1000
            # play 1000 games and see if the agent reaches the thresholds
            for j in range(testing_games):
                winner = self.game.play(not params.goes_first)
                self.game.reset()
                stats[winner] += 1
            print(f"Wins: {stats[1]} | Losses: {stats[2]} | Draws: {stats[0]}")

            # if the agent reaches the draw/loss thresholds, stop training
            if stats[1] <= testing_games * params.loss_threshold and stats[2] <= testing_games * params.draw_threshold:
                break

        # save the q_table after training
        file_name = self.get_file_name(params.goes_first)
        self.save_q_table(file_name, True)

    # train the agent based on the parameters
    # allows to train both agents one after the other, or just one
    # allows me to run the training in parallel
    def train(self, first_params: Parameters, second_params: Parameters, order: str):
        if order == "first" or order == "both":
            self.train_once(first_params)
            self.reset()
        if order == "second" or order == "both":
            self.train_once(second_params)

    # construct the file name for the q-table
    def get_file_name(self, goes_first: bool) -> str:
        order = "first" if goes_first else "second"
        size = f"{self.game.width}x{self.game.height}_" if self.game.__class__.__name__ == "Connect4" else ""
        return f"q_tables/{self.game.__class__.__name__}_{size}{order}"

    # save the q-table to a file
    def save_q_table(self, file_name: str, pickled=False):
        file_name = f"{file_name}.pkl" if pickled else f"{file_name}.json"
        mode = 'wb' if pickled else 'w'
        with open(file_name, mode) as file:
            pickle.dump(self.q_table, file) if pickled else json.dump(self.q_table, file)
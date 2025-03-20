# Connect4 and TicTacToe

This project implements Connect4 and TicTacToe games with various player types, including human, random, algorithmic, minimax, and Q-learning agents.

## Requirements

- Python 3.12 or later
- Required Python packages: `readchar`, `tqdm`

You can install the required packages using pip:

```sh
pip install readchar tqdm
```

## Running the Games

### Connect4

To run the Connect4 game, use the following command:

```sh
python connect4.py [options]
```

### TicTacToe

To run the TicTacToe game, use the following command:

```sh
python tictactoe.py [options]
```

### Options

- `-p1 <player1>`: Set the type of player 1. Default is `minimax`.
- `-p2 <player2>`: Set the type of player 2. Default is `algo`.
- `-g <number of games>`: Set the number of games to play. Default is `1`.
- `-d <max depth>`: Set the maximum depth for the minimax algorithm. Default is the size of the board.
- `-v`: Enable visual mode.
- `-w <width>`: Set the width of the board (Connect4 only). Must be between `4` and `9`. Default is `7`.
- `-h <height>`: Set the height of the board (Connect4 only). Must be between `4` and `9`. Default is `6`.
- `-train <batches>`: Train Q-learning agents for the specified number of batches.
- `-b <batch size>`: Set the batch size for training. Default is `50000`.
- `-s <seed>`: Set the random seed for training. Default is a random integer.
- `-o <order>`: Set the training order (`first`, `second`, or `both`). Default is `both`.

### Player Types

- `human`: Human player.
- `random`: Player that chooses moves randomly.
- `algo`: Player that uses a custom algorithm to choose moves.
- `minimax`: Player that uses the minimax algorithm to choose moves.
- `minimax_ab`: Player that uses the minimax algorithm with alpha-beta pruning.
- `qlearn`: Player that uses Q-learning to choose moves.

### Examples

#### Play a Connect4 Game

To play a game between a human and a minimax player:

```sh
python connect4.py -p1 human -p2 minimax
```

#### Play a TicTacToe Game

To play a game between a human and a minimax player:

```sh
python tictactoe.py -p1 human -p2 minimax -v
```

#### Train Q-learning Agents for Connect4

To train Q-learning agents for 10 batches with a batch size of 50000:

```sh
python connect4.py -train 10 -b 50000
```

#### Train Q-learning Agents for TicTacToe

To train Q-learning agents for 10 batches with a batch size of 50000:

```sh
python tictactoe.py -train 10 -b 50000
```

## Notes

- The game will display instructions and the board if a human player is involved.
- The Q-learning agents will save their Q-tables after training.
- The Connect4 board size can be customized using the `-w` and `-h` options, but must be between `4` and `9` for both dimensions.

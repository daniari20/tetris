import json
import random

ROWS = 24
COLS = 10
NUM_TESTS = 100


def empty_board():
    return [[0 for _ in range(COLS)] for _ in range(ROWS)]


def random_board(density=0.2):
    board = []
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            row.append(1 if random.random() < density else 0)
        board.append(row)
    return board


def almost_full_line():
    board = empty_board()
    row = [1]*COLS
    row[random.randint(0, COLS-1)] = 0
    board[-1] = row
    return board


def random_stack():
    board = empty_board()

    heights = [random.randint(0, 12) for _ in range(COLS)]

    for c in range(COLS):
        for r in range(ROWS-1, ROWS-heights[c]-1, -1):
            board[r][c] = 1

    return board


def board_with_holes():
    board = random_stack()

    for c in range(COLS):
        for r in range(ROWS):
            if board[r][c] == 1 and random.random() < 0.15:
                board[r][c] = 0

    return board


generators = [
    empty_board,
    random_board,
    almost_full_line,
    random_stack,
    board_with_holes
]

tests = {}

for i in range(1, NUM_TESTS+1):
    gen = random.choice(generators)

    if gen == random_board:
        board = gen(random.uniform(0.05,0.35))
    else:
        board = gen()

    tests[f"test{i}"] = board


with open("test_cases_100.json","w") as f:
    json.dump(tests, f, indent=4)

print("Archivo generado: test_cases_100.json")
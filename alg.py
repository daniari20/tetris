# from features import aggregate_height, complete_lines, holes, bumpiness
from copy import deepcopy
import random
import json
# from evaluation import evaluate_board
# from pieces import rotate

WEIGHTS = {
    "aggregate_height": -0.510066,
    "complete_lines": 0.760666,
    "holes": -0.35663,
    "bumpiness": -0.184483
}


def evaluate_board(grid):
    score = 0

    score += WEIGHTS["aggregate_height"] * aggregate_height(grid)
    score += WEIGHTS["complete_lines"] * complete_lines(grid)
    score += WEIGHTS["holes"] * holes(grid)
    score += WEIGHTS["bumpiness"] * bumpiness(grid)

    return score

SHAPES = [
    [[1, 1, 1, 1]],  # I

    [[1, 1],
     [1, 1]],        # O

    [[0, 1, 0],
     [1, 1, 1]],     # T

    [[1, 0, 0],
     [1, 1, 1]],     # J

    [[0, 0, 1],
     [1, 1, 1]],     # L

    [[1, 1, 0],
     [0, 1, 1]],     # S

    [[0, 1, 1],
     [1, 1, 0]]      # Z
]


def rotate(shape, times):
      new_shape = shape

      for _ in range(times):
            new_shape = list(zip(*new_shape[::-1]))
            new_shape = [list(row) for row in new_shape]

      return new_shape


ROWS = 24
COLS = 10


def valid_position(grid, shape, row, col):

    for r in range(len(shape)):

        for c in range(len(shape[0])):

            if shape[r][c] == 0:
                continue

            br = row+r
            bc = col+c

            if bc < 0 or bc >= COLS:
                return False

            if br >= ROWS:
                return False

            if br >= 0 and grid[br][bc] == 1:
                return False

    return True


def drop_piece(grid, shape, col):

    row = 0

    while valid_position(grid,shape,row+1,col):
        row += 1

    new_grid = deepcopy(grid)

    for r in range(len(shape)):
        for c in range(len(shape[0])):

            if shape[r][c] == 1:
                new_grid[row+r][col+c] = 1

    return new_grid

def search_stack(grid, stack):

    if len(stack) == 0:
        return evaluate_board(grid)

    piece = stack[0]

    best_score = float("-inf")

    for rotation in range(4):

        p = rotate(piece, rotation)
        width = len(p[0])

        for col in range(COLS - width + 1):

            if not valid_position(grid, p, 0, col):
                continue

            new_grid = drop_piece(grid, p, col)

            score = search_stack(new_grid, stack[1:])

            if score > best_score:
                best_score = score

    return best_score


def search_best_move(piece_stack, grid):

    first_piece = piece_stack[0]

    best_score = float("-inf")
    best_move = None

    for rotation in range(4):

        piece = rotate(first_piece, rotation)
        width = len(piece[0])

        for col in range(COLS - width + 1):

            if not valid_position(grid, piece, 0, col):
                continue

            new_grid = drop_piece(grid, piece, col)

            score = search_stack(new_grid, piece_stack[1:])

            if score > best_score:

                best_score = score
                best_move = (rotation, col)

    return best_move

ROWS = 24
VISIBLE_ROWS = 20
COLS = 10


def occ(grid, r, c):
    return grid[r][c] != 0


def column_heights(grid):

    heights = [0]*COLS

    for c in range(COLS):

        for r in range(ROWS):

            if occ(grid,r,c):

                heights[c] = ROWS-r
                break

    return heights


def aggregate_height(grid):

    return sum(column_heights(grid))


def complete_lines(grid):

    count = 0

    for r in range(ROWS):

        if all(grid[r][c] == 1 for c in range(COLS)):
            count += 1

    return count


def holes(grid):

    h = 0

    for c in range(COLS):

        seen = False

        for r in range(ROWS):

            if occ(grid,r,c):
                seen = True

            elif seen:
                h += 1

    return h


def bumpiness(grid):

    hs = column_heights(grid)

    return sum(abs(hs[i]-hs[i+1]) for i in range(COLS-1))


def print_test(test: list) -> None:
    for _ in test:
        print(_)
    print()





def run_tests():
    with open('test_cases_100.json', 'r') as f:
        cases = json.load(f)
    tamaño_stack = 3
    for nom in cases: 
        case = cases[nom]
        stack = []
        for _ in range(tamaño_stack):
            stack.append(SHAPES[random.randint(0, 6)])
        move = search_best_move(stack, case)
        print(f"caso: {nom}, movimiento: {move}")
        print("stack")
        for ficha in stack:
            print_test(ficha)
        print_test(case)




run_tests()
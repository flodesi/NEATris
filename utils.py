from copy import copy

import numpy as np
from Tetris.global_variables import NUM_COLUMNS, NUM_ROWS
from Tetris.piece import Piece

class TetrisParams:
    def __init__(self, matrix):
        self.matrix = np.array(matrix)
        self.total_height = self.total_height()
        self.biggest_dip = self.get_biggest_dip()
        self.sum_holes = self.sum_holes()
        self.height_diff = self.height_diff()
        self.num_empty_col = self.num_empty_col()
        self.col_holes = self.get_num_col_with_holes()
        self.score = self.score() ** 2

    def col_height(self):
        peaks = np.argmax(self.matrix, axis=0)
        peaks[peaks == 0] = len(self.matrix)
        peaks = len(self.matrix) * np.ones(peaks.shape) - peaks
        return np.array(peaks, dtype=int)

    def top_height(self):
        return np.max(self.col_height())

    def total_height(self):
        return np.sum(self.col_height())

    def get_biggest_dip(self):
        tops = self.col_height()
        dips = [0 for _ in range(NUM_COLUMNS)]
        dips[0] = max((tops[1] - tops[0]), 0)
        dips[NUM_COLUMNS - 1] = max((tops[NUM_COLUMNS - 2] - tops[NUM_COLUMNS - 1]), 0)
        for i in range(1, NUM_COLUMNS - 1):
            previous = max(tops[i - 1] - tops[i], 0)
            after = max(tops[i + 1] - tops[i], 0)
            dips[i] = max(previous, after)
        return np.max(dips)

    def holes_per_col(self):
        holes_per_col = []
        peaks = self.col_height()
        for i in range(NUM_COLUMNS):
            holes_per_col.append(peaks[i] - np.sum(0 if peaks[i] == 0 else self.matrix[-peaks[i]:, i]))
        return holes_per_col

    def sum_holes(self):
        holes_per_col = np.array(self.holes_per_col())
        return np.sum(holes_per_col)

    def get_num_col_with_holes(self):
        return np.count_nonzero(np.array(self.holes_per_col()))

    def height_diff(self):
        peaks = self.col_height()
        height_diff = 0
        for i in range(1, NUM_COLUMNS):
            height_diff += abs(peaks[i] - peaks[i - 1])
        return height_diff

    def num_empty_col(self):
        return NUM_COLUMNS - np.count_nonzero(np.sum(self.matrix, axis=0))

    def score(self):
        row_sums = np.sum(self.matrix, axis=1)
        num_lines = 0
        for r in row_sums:
            if r == NUM_COLUMNS:
                num_lines += 1
        return num_lines

    def return_all_params(self):
        return (-self.total_height, -self.biggest_dip, -self.sum_holes, -self.height_diff, -self.num_empty_col,
                -self.col_holes, self.score)


def encode_shape(formatted_shape):
    x_coords, y_coords = map(list, zip(*formatted_shape))
    rows = (max(y_coords) - min(y_coords) + 1)
    cols = (max(x_coords) - min(x_coords) + 1)
    enc_shape = np.zeros(shape=(rows, cols), dtype=int)
    for x, y in formatted_shape:
        enc_shape[y - min(y_coords)][x - min(x_coords)] = 1
    return enc_shape


def get_rotations(piece_temp: Piece):
    possibilities = []
    for rotation in range(len(piece_temp.shape)):
        possibilities.append(encode_shape(piece_temp.get_formatted_shape()))
        piece_temp.rotation = (piece_temp.rotation + 1) % len(piece_temp.shape)
    return possibilities


def generate_possible_moves(init_matrix, model, piece_rotations, next_rotation=None):
    possible_moves_result = []
    best_next_fitness = np.NINF

    for rotation, piece in enumerate(piece_rotations):
        y_len, x_len = piece.shape
        for x_start in range(NUM_COLUMNS - x_len + 1):
            y_start = 0
            mat = init_matrix.copy()
            while y_start + y_len <= NUM_ROWS:
                mat = init_matrix.copy()
                mat[y_start:y_start + y_len, x_start:x_start + x_len] += piece
                if 2 in mat:
                    mat = init_matrix.copy()
                    y_start -= 1
                    if y_start == -1:
                        x_start = None
                    else:
                        mat[y_start:y_start + y_len, x_start:x_start + x_len] += piece
                    break
                y_start += 1

            if next_rotation is None:
                params = TetrisParams(mat)
                fitness = model.activate(params.return_all_params())[0]
                if fitness > best_next_fitness:
                    best_next_fitness = fitness
            else:
                next_piece_fitness = generate_possible_moves(mat, model, next_rotation, next_rotation=None)
                params = TetrisParams(mat)
                fitness = model.activate(params.return_all_params())[0]
                if x_start is not None:
                    possible_moves_result.append([rotation, x_start, round(fitness, 5), round(next_piece_fitness, 5)])

    if next_rotation is None:
        return best_next_fitness
    else:
        return possible_moves_result


def attempt(tetris, model):
    matrix = np.array(tetris.get_grid_state(), dtype=int)
    all_combs = get_rotations(copy(tetris.current_piece))
    next_piece_combs = get_rotations(copy(tetris.next_piece))
    possible_moves_result = sorted(generate_possible_moves(matrix, model, all_combs, next_piece_combs),
                                   key=lambda p: (p[2] + p[3], - abs(p[1] - tetris.current_piece.x),
                                                  - abs(p[0] - tetris.current_piece.rotation)), reverse=True)
    return possible_moves_result
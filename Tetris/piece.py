from typing import List

from Tetris.global_variables import *
from Tetris.shapes import *


class Piece:
    def __init__(self, column: int, row: int, shape: List[List]):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES_LIST.index(shape)]
        self.rotation = 0

    def get_formatted_shape(self):
        positions = list()
        formatted_shape = self.shape[self.rotation % len(self.shape)]
        for i, line in enumerate(formatted_shape):
            row = list(line)
            for j, column in enumerate(row):
                if column == '*':
                    positions.append((self.x + j, self.y + i))

        for i, pos in enumerate(positions):
            positions[i] = (pos[0] - 2, pos[1] - 4)

        return positions

    # check overlaps
    def in_valid_space(self, grid):
        accepted_pos = [[(j, i) for j in range(NUM_COLUMNS) if grid[i][j] == (0, 0, 0)] for i in range(NUM_ROWS)]
        accepted_pos = [pos for sub in accepted_pos for pos in sub]
        formatted_shape = self.get_formatted_shape()
        for pos in formatted_shape:
            if pos not in accepted_pos:
                if pos[1] > -1:
                    return False
        return True

    def __copy__(self):
        return Piece(self.x, self.y, self.shape)

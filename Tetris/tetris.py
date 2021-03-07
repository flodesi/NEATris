from random import choice
from typing import List, Tuple, Dict
import pygame
from Tetris.global_variables import *
from Tetris.piece import Piece
from Tetris.shapes import *
from Tetris.colors import *
from Tetris.rendering import *

class Tetris:
    # for turning off rendering
    OPTIMIZE = False

    def __init__(self):
        self.grid = [[(0, 0, 0) for _ in range(NUM_COLUMNS)] for _ in range(NUM_ROWS)]
        self.score = 0
        self.locked_pos = dict() # blocks that are permanently on grid (non moving blocks)
        self.game_running = True
        self.game_over = False
        self.current_piece = Piece(5, 0, choice(SHAPES_LIST))
        self.next_piece = Piece(5, 0, choice(SHAPES_LIST))
        self.change_current_piece = False
        self.game_clock = pygame.time.Clock()
        self.fall_time = 0
        self.fall_speed = 0.27 # max fall time
        self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # create grid from the locked positions
    def set_grid(self):
        for i, g in enumerate(self.grid):
            for j, _ in enumerate(g):
                if (j, i) in self.locked_pos:
                    self.grid[i][j] = self.locked_pos[(j, i)]
                else:
                    self.grid[i][j] = (0, 0, 0)
        return self.grid

    def check_game_over(self):
        for pos in self.locked_pos:
            if pos[1] < 0:
                return True
        return False

    # for when a row is filled
    def clear_rows(self):
        cleared_rows = 0
        for i in range(len(self.grid)):
            if (0, 0, 0) in self.grid[i]:
                continue
            cleared_rows += 1
            for j in range(len(self.grid[i])):
                if (j, i) in self.locked_pos.keys():
                    del self.locked_pos[(j, i)]
            temp_locked_pos = dict()
            for pos, val in self.locked_pos.items():
                x, y = pos
                if y < i:
                    temp_locked_pos[(x, y + 1)] = val
                else:
                    temp_locked_pos[(x, y)] = val

            self.locked_pos = temp_locked_pos
        # non linear score function to encourage higher clears per turn
        self.score += 100 * cleared_rows ** 2

    def draw_game_window(self):
        self.window.fill(background)
        font = pygame.font.Font('./fonts/Pixel Digivolve.otf', 36)
        label = font.render('NEATris', 1, foreground)
        self.window.blit(label, (TOP_LEFT[X] + PLAY_WIDTH / 2 - (label.get_width() / 2), 10))

        # draw blocks
        for x in range(len(self.grid)): 
            for y in range(len(self.grid[x])):
                if self.grid[x][y] in SHAPE_TO_BORDER_COLORS:
                    shape_border_color = SHAPE_TO_BORDER_COLORS[self.grid[x][y]]
                    draw_rect_border(self.window, self.grid[x][y], pygame.Rect(TOP_LEFT[X] + y * BLOCK_SIZE, TOP_LEFT[Y] + x * BLOCK_SIZE,
                                  BLOCK_SIZE, BLOCK_SIZE), 2, shape_border_color)
                else:
                    pygame.draw.rect(self.window, self.grid[x][y],
                                    (TOP_LEFT[X] + y * BLOCK_SIZE, TOP_LEFT[Y] + x * BLOCK_SIZE,
                                    BLOCK_SIZE, BLOCK_SIZE), 0)

        # draw the grid lines
        for y in range(NUM_ROWS):
            pygame.draw.line(self.window, line_color,
                             (TOP_LEFT[X], TOP_LEFT[Y] + y * BLOCK_SIZE),
                             (TOP_LEFT[X] + PLAY_WIDTH, TOP_LEFT[Y] + y * BLOCK_SIZE))
        for x in range(NUM_COLUMNS):
            pygame.draw.line(self.window, line_color,
                             (TOP_LEFT[X] + x * BLOCK_SIZE, TOP_LEFT[Y]),
                             (TOP_LEFT[X] + x * BLOCK_SIZE, TOP_LEFT[Y] + PLAY_HEIGHT))
        
        # draw border
        pygame.draw.rect(self.window, border,
                         (TOP_LEFT[X], TOP_LEFT[Y],
                          PLAY_WIDTH, PLAY_HEIGHT), 3)

        # next shape window
        start_x = TOP_LEFT[X] + PLAY_WIDTH + 20
        start_y = TOP_LEFT[Y] + PLAY_HEIGHT / 2 - 100
        font = pygame.font.Font('./fonts/Pixel Digivolve.otf', 24)
        label = font.render('Next Shape:', 1, foreground_alt)
        self.window.blit(label, (start_x + 10, start_y - 30))
        formatted_shape = self.next_piece.shape[self.next_piece.rotation % len(self.next_piece.shape)]

        # draw next shape blocks
        for i, line in enumerate(formatted_shape):
            row = list(line)
            for j, column in enumerate(row):
                if column == '*':
                    draw_rect_border(
                        self.window, 
                        self.next_piece.color, pygame.Rect(
                            start_x + j * BLOCK_SIZE, start_y + i * BLOCK_SIZE,
                            BLOCK_SIZE, BLOCK_SIZE
                            ), 
                            2, 
                            SHAPE_TO_BORDER_COLORS[self.next_piece.color]
                            )

        # draw score
        font = pygame.font.Font('./fonts/Pixel Digivolve.otf', 24)
        label = font.render('SCORE: ' + str(self.score), 1, foreground_alt)
        
        self.window.blit(label, (TOP_LEFT[X] - (PLAY_WIDTH / 2), TOP_LEFT[Y] + PLAY_HEIGHT / 2 - 130))


    
    # return simplified grid state for neat
    def get_grid_state(self):
        state = [[0 for _ in range(NUM_COLUMNS)] for _ in range(NUM_ROWS)]
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                if self.grid[i][j] != (0, 0, 0):
                    state[i][j] = 1
        return state

    # to be called every frame
    def play_game(self, action=None):
        # set the grid and increment fall time
        self.grid = self.set_grid()
        self.fall_time += self.game_clock.get_rawtime()
        self.game_clock.tick()
        # time's up, let's do this (time to fall)
        if self.fall_time >= self.fall_speed * 1000:
            self.fall_time = 0
            self.current_piece.y = self.current_piece.y + 1
            if not self.current_piece.in_valid_space(self.grid) and 0 < self.current_piece.y:
                self.current_piece.y -= 1
                self.change_current_piece = True

        if action is not None:
            if action == LEFT_KEY:
                self.current_piece.x -= 1
                if not self.current_piece.in_valid_space(self.grid):
                    self.current_piece.x += 1
            elif action == RIGHT_KEY:
                self.current_piece.x += 1
                if not self.current_piece.in_valid_space(self.grid):
                    self.current_piece.x -= 1
            elif action == ROTATE_KEY:
                self.current_piece.rotation = (self.current_piece.rotation + 1) % len(self.current_piece.shape)
                if not self.current_piece.in_valid_space(self.grid):
                    self.current_piece.rotation = (self.current_piece.rotation - 1) % len(self.current_piece.shape)
            elif action == DOWN_KEY:             
                while self.current_piece.in_valid_space(self.grid):
                    self.current_piece.y += 1
                self.current_piece.y -= 1
                self.change_current_piece = True
        formatter_shape = self.current_piece.get_formatted_shape()
        for i in range(len(formatter_shape)):
            x, y = formatter_shape[i]
            if y > -1:
                self.grid[y][x] = self.current_piece.color
        if self.change_current_piece:
            for pos in formatter_shape:
                self.locked_pos[pos] = self.current_piece.color
            self.current_piece = self.next_piece
            self.next_piece = Piece(5, 0, choice(SHAPES_LIST))
            self.change_current_piece = False
            self.clear_rows()

        if not Tetris.OPTIMIZE:
            self.draw_game_window()
            pygame.display.update()

    # animation for when game is over
    def game_over_animation(self):
        animation_over = False
        offset = 0
        speed = 0.1
        max_offset = 40
        wait_timer = 0
        wait_time = 500
        expand = 10
        while not animation_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    animation_over = True
            font = pygame.font.Font('./fonts/Pixel Digivolve.otf', 48)
            label = font.render('GAME OVER', 1, fail_color)
            label_background = pygame.Surface((label.get_width() + 2 * expand, label.get_height() + 2 * expand))
            label_background.fill(fail_background)
            # draw everything underneath
            self.draw_game_window()
            # then draw the game over text
            self.window.blit(label_background, (int(TOP_LEFT[X] + PLAY_WIDTH / 2 - (label.get_width() / 2)) - expand, 80 + int(offset) - expand))
            self.window.blit(label, (int(TOP_LEFT[X] + PLAY_WIDTH / 2 - (label.get_width() / 2)), 80 + int(offset)))
            # logic for animation control
            if offset < 80 and offset + self.game_clock.get_time() * speed >= 80:
                wait_timer = wait_time
            offset = min(80, offset + self.game_clock.get_time() * speed)
            if wait_timer > 0:
                wait_timer -= self.game_clock.get_time()
            if wait_timer < 0:
                animation_over = True
            pygame.display.update()
            self.game_clock.tick(60)

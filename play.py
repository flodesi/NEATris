import pygame
from Tetris.tetris import Tetris
from Tetris.global_variables import ROTATE_KEY, RIGHT_KEY, LEFT_KEY, DOWN_KEY



pygame.init()
pygame.display.set_caption('NEATris')
t = Tetris()
stop = False

while not stop:
    action = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            stop = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                action = LEFT_KEY
            elif event.key == pygame.K_RIGHT:
                action = RIGHT_KEY
            elif event.key == pygame.K_UP:
                action = ROTATE_KEY
            elif event.key == pygame.K_DOWN:
                action = DOWN_KEY
    t.play_game(action)
    if t.check_game_over():
        t.game_over_animation()
        stop = True
    pygame.quit()
    quit()


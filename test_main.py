import os
import pickle
from time import sleep
import neat
import pygame
from Tetris.tetris import Tetris
from Tetris.global_variables import ROTATE_KEY, RIGHT_KEY, LEFT_KEY, DOWN_KEY
from utils import attempt

pygame.init()
pygame.display.set_caption('NEATris')

with open("winner_winner_chicken_dinner.pickle", 'rb') as genome_file:
    genome = pickle.load(genome_file)
config_path = os.path.join(os.path.dirname(__file__), 'config.txt')

config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            config_path)
model = neat.nn.FeedForwardNetwork.create(genome, config)

def main():
    t = Tetris()
    while t.game_running and not t.game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                t.game_running = False
                pygame.display.quit()
                quit()
        moves = attempt(t, model)
        if moves:
            rotation, x_position, _, _ = moves[0]
            t.play_game(None)
            sleep(0.1)

            while t.current_piece.rotation != rotation:
                t.play_game(ROTATE_KEY)
                sleep(0.1)

            while x_position != min([x for x, _ in t.current_piece.get_formatted_shape()]):
                if x_position > min([x for x, _ in t.current_piece.get_formatted_shape()]):
                    t.play_game(RIGHT_KEY)
                else:
                    t.play_game(LEFT_KEY)
                sleep(0.1)
            t.play_game(DOWN_KEY)
            t.play_game(None)
        else:
            t.game_over = True
            pygame.display.quit()
            quit()

if __name__ == '__main__':
    main()

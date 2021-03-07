#!/usr/bin/python3

import os
import pickle
from time import sleep
import neat
import pygame
from Tetris.tetris import Tetris
from Tetris.global_variables import ROTATE_KEY, RIGHT_KEY, LEFT_KEY, DOWN_KEY
from utils import attempt
import argparse

pygame.init()
pygame.display.set_caption('NEATris')

with open("winner_winner_chicken_dinner.pickle", 'rb') as genome_file:
    genome = pickle.load(genome_file)
config_path = os.path.join(os.path.dirname(__file__), 'config.txt')

config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            config_path)
model = neat.nn.FeedForwardNetwork.create(genome, config)

def test_main():
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

cur_gen = 0
best_fit = 0


def main_game(genomes, config):
    global cur_gen, best_fit

    cur_gen += 1
    genome_arr = []
    game_instances = []
    models = []

    for _, genome in genomes:
        genome.fitness = 0
        genome_arr.append(genome)
        game_instances.append(Tetris())
        models.append(neat.nn.FeedForwardNetwork.create(genome, config))

    while len(models) > 0:
        for g, t, m in zip(genome_arr, game_instances, models):
            possible_moves_result = attempt(t, m)
            if possible_moves_result:
                best_rotation, x_position, _, _ = possible_moves_result[0]
                while t.current_piece.rotation != best_rotation:
                    t.play_game(ROTATE_KEY)

                while x_position != min([x for x, _ in t.current_piece.get_formatted_shape()]):
                    if x_position > min([x for x, _ in t.current_piece.get_formatted_shape()]):
                        t.play_game(RIGHT_KEY)
                    else:
                        t.play_game(LEFT_KEY)

                t.play_game(DOWN_KEY)
                t.play_game(None)
            else:
                t.game_over = True

            g.fitness = t.score

            if g.fitness > best_fit:
                best_fit = g.fitness
                for file_name in os.listdir("./best_model/"):
                    os.remove("./best_model/" + file_name)
                with open("best_model/best_model" + str(t.score) + ".pickle", 'wb') as model_file:
                    pickle.dump(g, model_file)

            if t.check_game_over() or t.game_over:
                print("Models Left in Generation: {}, Generation: {}, Fitness of Completed Model (Score): {}".format
                      (len(models) - 1, cur_gen - 1, t.score))
                game_instances.remove(t)
                models.remove(m)
                genome_arr.remove(g)

def run():
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str)
    parser.add_argument('--opt', action='store_true', help='Optimize training by turning off rendering')
    args = parser.parse_args()
    if args.mode == 'train':
        Tetris.OPTIMIZE = args.opt
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                os.path.join(os.path.dirname(__file__), 'config.txt'))

        checkpoint_dir = os.listdir("save_state/")
        if not checkpoint_dir:
            pop = neat.Population(config)
        else:
            checkpoints = []
            for checkpoint in checkpoint_dir:
                checkpoints.append(checkpoint[16:])
            best_check = sorted(checkpoints, reverse=True)[0]
            pop = neat.Checkpointer().restore_checkpoint("save_state/neat_save_state_" + str(best_check))
            print("Resuming from checkpoint ", best_check)
        pop.add_reporter(neat.StdOutReporter(True))
        pop.add_reporter(neat.StatisticsReporter())
        pop.add_reporter(neat.Checkpointer(generation_interval=1, time_interval_seconds=1200,
                                        filename_prefix='save_state/neat_save_state_'))
        winner = pop.run(main_game, 10)
        print('\n\nBest genome: {!s}'.format(winner))
        with open("winner_winner_chicken_dinner.pickle", 'wb') as model_file:
            pickle.dump(winner, model_file)
    elif args.mode == 'test':
        test_main()
    elif args.mode == 'play':
        run()

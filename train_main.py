import os
import pickle
import neat
import pygame
from Tetris.tetris import Tetris
from Tetris.global_variables import ROTATE_KEY, RIGHT_KEY, LEFT_KEY, DOWN_KEY
from utils import attempt

pygame.init()
pygame.display.set_caption('NEATris')
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


if __name__ == "__main__":
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

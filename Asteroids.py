import pygame
import neat
import time
import os
import random
pygame.font.init()

#create a game of asteroids that learns using neat. 
#The player can rotate, shoot forward, thrust forward and keep that velocity, there is no break either. The player should be able to see in an appropriate amount of directions around themselves (8 maybe?)
    #this might be done by creating a ray type object come out from the player and see if it collides with anything and then return the distance from the player to that collison
#the asteroids should spawn in 3 sizes, small medium and large, when they are shot they break into 2 of the smaller denominations, the small ones just die. They spawn offscreen and move in a random direction and velocity.
#if anything goes off screen they should loop back around
    #this may be hard so maybe just kill anything off screen

WIN_WIDTH = 800
WIN_HEIGHT = 800
STAT_FONT = pygame.font.SysFont("comicsans", 50)
#theres a better way to track gens globally
gen = 0

class SpaceShip:
    pass

class Bullet:
    pass

class Asteroid:
    pass

def draw_window(ship, bullets, asteroids, score, gen):
    pass

def main(genomes, config):
    pass

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(main,500)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
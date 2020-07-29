import pygame
import neat
import time
import os
import random
import math
pygame.font.init()

#create a game of asteroids that learns using neat. 
#The player can rotate, shoot forward, thrust forward and keep that velocity, there is no break either. The player should be able to see in an appropriate amount of directions around themselves (8 maybe?)
    #this might be done by creating a ray type object come out from the player and see if it collides with anything and then return the distance from the player to that collison
#the asteroids should spawn in 3 sizes, small medium and large, when they are shot they break into 2 of the smaller denominations, the small ones just die. They spawn offscreen and move in a random direction and velocity.
#if anything goes off screen they should loop back around
    #this may be hard so maybe just kill anything off screen

#load in images
SHIP_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "ship.png")))
THRUST_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "thrust.png")))
ASTEROID_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("images", "asteroid0.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("images", "asteroid1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("images", "asteroid2.png")))]

#set our screen size and font
WIN_WIDTH = 800
WIN_HEIGHT = 800
STAT_FONT = pygame.font.SysFont("comicsans", 50)
#theres a better way to track gens globally
gen = 0

class Ship:
    #rotation velocity, how fast the ship rotates per frame
    ROT_VEL = 20

    def __init__(self):
        self.x = WIN_WIDTH // 2
        self.y = WIN_HEIGHT // 2
        self.img = SHIP_IMG
        self.rotation = 0
        #self.tick_count = 0
        self.speed = 0
        self.horizontal_speed = 0
        self.vertical_speed = 0
        self.MAX_SPEED = 20
        self.isThrust = False

    def thrust(self):
        if self.speed < self.MAX_SPEED:
            self.horizontal_speed += math.cos(self.rotation * math.pi / 180)
            self.vertical_speed += math.sin(self.rotation * math.pi / 180)
        self.isThrust = True

    def rotate_left(self):
        self.rotation -= 1
        
    def rotate_right(self):
        self.rotation += 1

    def move(self):
        self.x += self.horizontal_speed
        self.y += self.vertical_speed
        #check if we need to wrap around the screen
        if self.x > WIN_WIDTH:
            self.x = 0
        elif self.x < 0:
            self.x = WIN_WIDTH
        if self.y > WIN_HEIGHT:
            self.y = 0
        elif self.y < 0:
            self.y = WIN_HEIGHT

    def shoot():
        return Bullet(self.x, self.y, self.rotation)

    def draw(self, win):
        rotated_img = pygame.transform.rotate(self.img, self.rotation)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        if self.isThrust:
            self.isThrust = False
            rotated_thrust_img = pygame.transform.rotate(self.img, self.rotation)
            win.blit(rotated_thrust_img, new_rect.topleft)
        else:
            win.blit(rotated_image, new_rect.topleft)
        
    #this will get all of the pixels that the ship is taking up, this will allow us to see if a ship pixel collides with an asteroid pixel 
    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Bullet:
    VEL = 30

    def __init__(self, x, y, rotation):
        pass

class Asteroid:
    pass

class Game:

    def __init__(self):
        self.ship = Ship()
        self.asteroids = []
        self.closest_asteroids = []
        self.score = 0
        for i in range(10):
            asteroids.append(Asteroid())

    def get_closest_asteroids(self):
        for asteroid in asteroids:


def draw_window(ships, bullets, asteroids, score, gen):
    for asteroid in asteroids:
        asteroid.draw(win)
    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH / 2 - text.get_width() / 2, 150))
    text = STAT_FONT.render("Generation: " + str(gen), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH / 2 - text.get_width() / 2, 100))
    ship.draw(win)
    pygame.display.update()

def main(genomes, config):
    global gen
    gen += 1
    nets = []
    ge = []
    ships = []
    
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    for _,g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        ships.append(Ship())
        g.fitness = 0
        ge.append(g)

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        for x, ship in enumerate(ships):
            ship.move()
            ge[x].fitness += 0.1
            outputs = nets[x].activate((ship.x, ship.y, ship.rotation, ship.speed)) #distance to asteroids around the ships))
            if outputs[0] > .5:
                ship.rotate_left()
            if outputs[1] > .5:
                ship.rotate_right()
            if outputs[2] > .5:
                ship.thrust()
            if outputs[3] > .5:
                ship.shoot()

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
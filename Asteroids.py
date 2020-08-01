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

#set our screen size and font
WIN_WIDTH = 800
WIN_HEIGHT = 800
STAT_FONT = pygame.font.SysFont("comicsans", 50)
#set game speed, making this number higher will let generations go faster
GAME_SPEED = 2
#constant to convert degrees to radians
D_TO_R = math.pi / 180
#theres a better way to track gens globally
gen = 0

class Ship:
    def __init__(self):
        self.x = WIN_WIDTH // 2
        self.y = WIN_HEIGHT // 2
        self.size = 20
        self.rotation = 0
        self.speed = 0
        self.horizontal_speed = 0
        self.vertical_speed = 0
        self.isThrust = False

    def thrust(self):
        self.horizontal_speed += math.cos(self.rotation * D_TO_R)
        self.vertical_speed += math.sin(self.rotation * D_TO_R)
        self.speed = math.sqrt(self.horizontal_speed**2 + self.vertical_speed**2)
        self.isThrust = True

    def rotate_left(self):
        self.rotation -= 8
        
    def rotate_right(self):
        self.rotation += 8

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

    def shoot(self):
        return Bullet(self.x, self.y, self.rotation)

    def draw(self, win):
        v0 = (self.size * math.sqrt(130) / 12)
        v1 = math.atan(7 / 9)
        v2 = math.radians(self.rotation)
        coord1 = (int(self.x - v0 * math.cos(v1 + v2)), int(self.y - v0 * math.sin(v1 +v2)))
        coord2 = (int(self.x - v0 * math.cos(v1 - v2)), int(self.y + v0 * math.sin(v1 - v2)))
        coord3 = (int(self.x + self.size * math.cos(v2)), int(self.y + self.size * math.sin(v2)))
        pygame.draw.lines(win, (255,255,255), True, (coord1,coord2, coord3))
        if self.isThrust:
            self.isThrust = False
            coord1 = (int(self.x - (self.size+10) * math.cos(v2)), int(self.y - (self.size+10) * math.sin(v2)))
            coord2 = (int(self.x - ((self.size+10) * 0.5 * math.cos(v2 + math.pi / 6))), int(self.y - ((self.size+10) * 0.5 * math.sin(v2 + math.pi / 6))))
            pygame.draw.line(win, (255,255,255), coord1, coord2)
            coord1 = (int(self.x - (self.size+10) * math.cos(-v2)), int(self.y + (self.size+10) * math.sin(-v2)))
            coord2 = (int(self.x - ((self.size+10) * 0.5 * math.cos(-v2 + math.pi / 6))), int(self.y + ((self.size+10) * 0.5 * math.sin(-v2 + math.pi / 6))))
            pygame.draw.line(win, (255,255,255), coord1, coord2)

class Bullet:

    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.VEL = 20
        self.direction = direction
        self.on_screen = True

    def move(self):
        self.x += self.VEL * math.cos(self.direction * D_TO_R)
        self.y += self.VEL * math.sin(self.direction * D_TO_R)
        if self.x > WIN_WIDTH or self.x < 0 or self.y > WIN_HEIGHT or self.y < 0:
            self.on_screen = False

    def draw(self, win):
        pygame.draw.circle(win, (255,255,255), (int(self.x), int(self.y)), 2)


class Asteroid:

    def __init__(self, x = -1, y = -1, size = -1, direction = -1):
        if size == -1:
            size = random.randrange(0,3)
            if size == 2:
                self.size = 60
            elif size == 1:
                self.size = 30
            elif size == 0:
                self.size = 15
        else:
            self.size = size
        if x == -1:
            self.x = random.randrange(-1, WIN_WIDTH +1)
        else:
            self.x = x
        if y == -1:
            self.y = random.randrange(-1, WIN_HEIGHT + 1)
        else:
            self.y = y
        if direction == -1:
            self.direction = random.randrange(0, 360) * D_TO_R
        else:
            self.direction = direction * D_TO_R
        self.speed = random.randrange(1, 5)
        self.rotation = 0

        # Make random asteroid sprites
        full_circle = random.uniform(18, 36)
        dist = random.uniform(self.size / 2, self.size)
        self.vertices = []
        while full_circle < 360:
            self.vertices.append([dist, full_circle])
            dist = random.uniform(self.size / 2, self.size)
            full_circle += random.uniform(18, 36)

    def move(self):
        self.x += self.speed / 2 * math.cos(self.direction)
        self.y += self.speed / 2 * math.sin(self.direction)
        if self.x > WIN_WIDTH:
            self.x = 0
        elif self.x < 0:
            self.x = WIN_WIDTH
        if self.y > WIN_HEIGHT:
            self.y = 0
        elif self.y < 0:
            self.y = WIN_HEIGHT

    def rotate(self):
        self.rotation += 2

    def get_distance(self, ship_x, ship_y):
        xdif = (self.x - ship_x)**2
        ydif = (self.y - ship_y)**2
        return math.sqrt(xdif + ydif)

    def get_angle(self, ship_x, ship_y):
        return math.atan2(ship_y - self.y, ship_x - self.x) * D_TO_R

    def draw(self, win):
        for v in range(len(self.vertices)):
            if v == len(self.vertices) - 1:
                next_v = self.vertices[0]
            else:
                next_v = self.vertices[v + 1]
            this_v = self.vertices[v]
            pygame.draw.line(win, (255,255,255), 
            (int(self.x + this_v[0] * math.cos(this_v[1] * D_TO_R)), int(self.y + this_v[0] * math.sin(this_v[1] * D_TO_R))),
            (int(self.x + next_v[0] * math.cos(next_v[1] * D_TO_R)), int(self.y + next_v[0] * math.sin(next_v[1] * D_TO_R))))


class Game:

    def __init__(self, win):
        self.ship = Ship()
        self.asteroids = []
        self.closest_asteroids = []
        self.bullets = []
        self.score = 0
        self.shoot_cooldown = 0
        self.win = win
        for i in range(10):
            self.asteroids.append(Asteroid())
        self.asteroids.append(Asteroid(WIN_WIDTH / 2, WIN_HEIGHT / 4, 30, 90))

    def move(self):
        self.ship.move()
        self.check_collisions(self.win)
        self.shoot_cooldown -= 1
        if len(self.asteroids) < 10:
            self.asteroids.append(Asteroid())
        for asteroid in self.asteroids:
            asteroid.move()
        for bullet in self.bullets:
            bullet.move()

    def shoot(self):
        if self.shoot_cooldown <= 0:
            self.bullets.append(self.ship.shoot())
            self.shoot_cooldown = 30

    def get_closest_asteroids(self, ship_x, ship_y):
        closest = []
        for x, asteroid in enumerate(self.asteroids):
            closer = True
            if x > 7:
                for location in closest:
                    if float(location[0]) > float(asteroid.get_distance(ship_x, ship_y)):
                        closest.pop(closest.index(location))
                        closer = True
                        break
            if closer:
                closest.append((asteroid.get_distance(ship_x, ship_y), asteroid.get_angle(ship_x, ship_y)))
        return closest

    def is_colliding(self, x, y, xTo, yTo, size):
        if x > xTo - size and x < xTo + size and y > yTo - size and y < yTo + size:
            return True
        return False

    def check_collisions(self, win):
        for b in self.bullets:
            for a in self.asteroids:
                if self.is_colliding(b.x, b.y, a.x, a.y, a.size):
                    if a.size != 15:
                        self.asteroids.append(Asteroid(a.x, a.y, a.size / 2))
                        self.asteroids.append(Asteroid(a.x, a.y, a.size / 2))
                    self.asteroids.remove(a)
                    self.bullets.remove(b)
                    self.score += 10
                    break

            
def draw_window(win, ship, bullets, asteroids, score, gen):
    win.fill((0,0,0))
    for asteroid in asteroids:
        asteroid.draw(win)
    for bullet in bullets:
        bullet.draw(win)
    ship.draw(win)
    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (int(WIN_WIDTH / 2 - text.get_width() / 2), 150))
    text = STAT_FONT.render("Generation: " + str(gen), 1, (255,255,255))
    win.blit(text, (int(WIN_WIDTH / 2 - text.get_width() / 2), 100))
    pygame.display.update()

def main(genomes, config):
    global gen
    gen += 1
    nets = []
    ge = []
    games = []
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    for _,g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        games.append(Game(win))
        g.fitness = 0
        ge.append(g)

    run = True
    while run:
        clock.tick(30 * GAME_SPEED)
        #check for user input
        '''
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_w]:
            games[0].ship.thrust()
        if pressed[pygame.K_a]:
            games[0].ship.rotate_left()
        if pressed[pygame.K_d]:
            games[0].ship.rotate_right()
        '''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            '''
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    games[0].shoot()
            '''
        
        if len(games) < 1:
            run = False
            break

        for x, game in enumerate(games):
            ship = game.ship
            score = 0
            game.move()

            if x == 0:
                s = getattr(games[0], 'ship')
                b = games[0].bullets
                a = games[0].asteroids
                sc = games[0].score
                draw_window(win, s, b, a, sc, gen)

            roids = game.get_closest_asteroids(game.ship.x, game.ship.y)
            outputs = nets[x].activate((game.ship.x, game.ship.y, game.ship.rotation, game.ship.speed, roids[0][0], roids[0][1], roids[1][0], roids[1][1], roids[2][0], roids[2][1], roids[3][0], roids[3][1], roids[4][0], roids[4][1], roids[5][0], roids[5][1], roids[6][0], roids[6][1], roids[7][0], roids[7][1]))
            if outputs[0] > 0.5:
                ship.rotate_left()
            if outputs[1] > 0.5:
                ship.rotate_right()
            if outputs[2] > 0.5:
                ship.thrust()
            if outputs[3] > 0.5:
                game.shoot()

            if game.score != score:
                score = game.score
                ge[x].fitness += 10
            ge[x].fitness += 0.1
            for a in game.asteroids:
                if game.is_colliding(ship.x, ship.y, a.x, a.y, a.size):
                    ge[x].fitness -= 10
                    games.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                    break
            
        
        
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
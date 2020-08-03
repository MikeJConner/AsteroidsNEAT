import pygame
import neat
import time
import os
import random
import math
import pickle
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
GAME_SPEED = 1
#constant to convert degrees to radians
D_TO_R = math.pi / 180
#theres a better way to track gens globally
gen = 0


def get_slope(line):
    xdif = line[1][1] - line[0][1]
    ydif = line[1][0] - line[0][0]
    if ydif == 0:
        return 9999
    return xdif / ydif

def get_y_int(line, slope):
    return line[0][1] - slope * line[0][0]

def find_intersection(line1, line2):
    m1 = get_slope(line1)
    m2 = get_slope(line2)
    b1 = get_y_int(line1, m1)
    b2 = get_y_int(line2, m2)
    if m1 == m2:
        return False
    x = (b2 - b1) / (m1-m2)
    y = m1* x + b1
    if x < line1[1][0] and x > line1[0][0] or x > line1[1][0] and x < line1[0][0]:
        if y < line1[1][1] and y > line1[0][1] or y > line1[1][1] and y < line1[0][1]:
            if x < line2[1][0] and x > line2[0][0] or x > line2[1][0] and x < line2[0][0]:
                if y < line2[1][1] and y > line2[0][1] or y > line2[1][1] and y < line2[0][1]:
                    return x, y
    return False

def get_dis(x1, x2, y1, y2):
        xdif = (x1 - x2)**2
        ydif = (y1 - y2)**2
        return int(math.sqrt(xdif + ydif))

class Ship:
    def __init__(self):
        self.x = WIN_WIDTH // 2
        self.y = WIN_HEIGHT // 2
        self.MAX_SPEED = 7
        self.size = 20
        self.rotation = 0
        self.speed = 0
        self.horizontal_speed = 0
        self.vertical_speed = 0
        self.is_thrust = False

    def thrust(self):
        self.horizontal_speed += math.cos(self.rotation * D_TO_R) / 2
        self.vertical_speed += math.sin(self.rotation * D_TO_R) / 2
        if self.horizontal_speed > self.MAX_SPEED:
            self.horizontal_speed = self.MAX_SPEED
        if self.vertical_speed > self.MAX_SPEED:
            self.vertical_speed = self.MAX_SPEED
        self.speed = math.sqrt(self.horizontal_speed**2 + self.vertical_speed**2)
        self.is_thrust = True

    def rotate_left(self):
        self.rotation -= 8
        
    def rotate_right(self):
        self.rotation += 8

    def move(self):
        if not self.is_thrust and self.horizontal_speed != 0:
            self.horizontal_speed -= self.horizontal_speed * 0.02
        if not self.is_thrust and self.vertical_speed != 0:
            self.vertical_speed -= self.vertical_speed * 0.02
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
        if self.is_thrust:
            self.is_thrust = False
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
        self.VEL = 80
        self.direction = direction
        self.life_time = 10
        self.alive = True

    def move(self):
        self.life_time -= 1
        self.x += self.VEL * math.cos(self.direction * D_TO_R)
        self.y += self.VEL * math.sin(self.direction * D_TO_R)
        if self.life_time < 0:
            self.alive = False
        return not self.alive

    def draw(self, win):
        pygame.draw.circle(win, (255,255,255), (int(self.x), int(self.y)), 2)


class Asteroid:
    def __init__(self, x = -1, y = -1, size = -1, direction = -1):
        if size != -1:
            self.size = size
        else:
            self.size = random.randint(0,2)
            if self.size == 0:
                self.size = 20
            elif self.size == 1:
                self.size = 40
            elif self.size == 2:
                self.size = 80
        if x == -1:
            self.x = 0
        else:
            self.x = x
        if y == -1:
            self.y = random.randrange(0, WIN_HEIGHT)
        else:
            self.y = y
        if direction == -1:
            self.direction = random.randrange(0, 360) * D_TO_R
        else:
            self.direction = direction * D_TO_R
        self.speed = random.randrange(3, 7)
        self.rotation = 0
        self.lines = []

        # Make random asteroid sprites
        full_circle = random.uniform(45,55)
        self.vertices = []
        while full_circle < 360:
            self.vertices.append([self.size, full_circle])
            dist = self.size * 0.9
            full_circle += random.uniform(45, 55)

        for v in range(len(self.vertices)):
            if v == len(self.vertices) - 1:
                next_v = self.vertices[0]
            else:
                next_v = self.vertices[v + 1]
            this_v = self.vertices[v]
            line = ((int(self.x + this_v[0] * math.cos(this_v[1] * D_TO_R)), int(self.y + this_v[0] * math.sin(this_v[1] * D_TO_R))),
            (int(self.x + next_v[0] * math.cos(next_v[1] * D_TO_R)), int(self.y + next_v[0] * math.sin(next_v[1] * D_TO_R))))
            self.lines.append(line)

    def move(self):
        self.x += self.speed / 1.5 * math.cos(self.direction)
        self.y += self.speed / 1.5 * math.sin(self.direction)
        self.rotate()
        if self.x > WIN_WIDTH + self.size:
            self.x = -self.size
        elif self.x < -self.size:
            self.x = WIN_WIDTH + self.size
        if self.y > WIN_HEIGHT + self.size:
            self.y = -self.size
        elif self.y < -self.size:
            self.y = WIN_HEIGHT + self.size

    def rotate(self):
        self.rotation += 2

    def draw(self, win):
        for v in range(len(self.vertices)):
            if v == len(self.vertices) - 1:
                next_v = self.vertices[0]
            else:
                next_v = self.vertices[v + 1]
            this_v = self.vertices[v]
            x1 = (self.x + this_v[0] * math.cos(this_v[1] * D_TO_R)) - self.x
            y1 = (self.y + this_v[0] * math.sin(this_v[1] * D_TO_R)) - self.y
            x2 = (self.x + next_v[0] * math.cos(next_v[1] * D_TO_R)) - self.x
            y2 = (self.y + next_v[0] * math.sin(next_v[1] * D_TO_R)) - self.y
            x11 = (x1 * math.cos(self.rotation * D_TO_R) - y1 * math.sin(self.rotation * D_TO_R)) + self.x
            y11 = (y1 * math.cos(self.rotation * D_TO_R) + x1 * math.sin(self.rotation * D_TO_R)) + self.y
            x22 = (x2 * math.cos(self.rotation * D_TO_R) - y2 * math.sin(self.rotation * D_TO_R)) + self.x
            y22 = (y2 * math.cos(self.rotation * D_TO_R) + x2 * math.sin(self.rotation * D_TO_R)) + self.y
            line = ((int(x11), int(y11)), (int(x22), int(y22)))
            self.lines[v] = line
            pygame.draw.line(win, (255,255,255), line[0], line[1])


class Game:
    def __init__(self, win):
        self.ship = Ship()
        self.asteroids = []
        self.bullets = []
        self.distances = []
        self.sight_lines = []
        self.stationary_count = 200
        self.score = 0
        self.shoot_cooldown = 0
        self.win = win
        self.hit_asteroid = False
        self.bullet_missed = False
        self.num_bullets_missed = 0
        for i in range(4):
            self.asteroids.append(Asteroid())
        self.asteroids.append(Asteroid(WIN_WIDTH / 2, WIN_HEIGHT / 4, 40, 90))

    def move(self):
        self.ship.move()
        self.sight_lines = (
            ((int(self.ship.x), int(self.ship.y)), (int(self.ship.x + math.cos(self.ship.rotation * D_TO_R) * WIN_WIDTH * 2), int(self.ship.y + math.sin(self.ship.rotation * D_TO_R) * WIN_HEIGHT * 2))),
            ((int(self.ship.x), int(self.ship.y)), (int(self.ship.x + math.cos((self.ship.rotation + 45) * D_TO_R) * WIN_WIDTH * 2), int(self.ship.y + math.sin((self.ship.rotation + 45) * D_TO_R) * WIN_HEIGHT * 2))),
            ((int(self.ship.x), int(self.ship.y)), (int(self.ship.x + math.cos((self.ship.rotation - 45) * D_TO_R) * WIN_WIDTH * 2), int(self.ship.y + math.sin((self.ship.rotation - 45) * D_TO_R) * WIN_HEIGHT * 2))),
            ((int(self.ship.x), int(self.ship.y)), (int(self.ship.x + math.cos((self.ship.rotation + 90) * D_TO_R) * WIN_WIDTH * 2), int(self.ship.y + math.sin((self.ship.rotation + 90) * D_TO_R) * WIN_HEIGHT * 2))),
            ((int(self.ship.x), int(self.ship.y)), (int(self.ship.x + math.cos((self.ship.rotation - 90) * D_TO_R) * WIN_WIDTH * 2), int(self.ship.y + math.sin((self.ship.rotation - 90) * D_TO_R) * WIN_HEIGHT * 2))),
            ((int(self.ship.x), int(self.ship.y)), (int(self.ship.x + math.cos((self.ship.rotation + 135) * D_TO_R) * WIN_WIDTH * 2), int(self.ship.y + math.sin((self.ship.rotation + 135) * D_TO_R) * WIN_HEIGHT * 2))),
            ((int(self.ship.x), int(self.ship.y)), (int(self.ship.x + math.cos((self.ship.rotation - 135) * D_TO_R) * WIN_WIDTH * 2), int(self.ship.y + math.sin((self.ship.rotation - 135) * D_TO_R) * WIN_HEIGHT * 2))),
            ((int(self.ship.x), int(self.ship.y)), (int(self.ship.x + math.cos((self.ship.rotation + 180) * D_TO_R) * WIN_WIDTH * 2), int(self.ship.y + math.sin((self.ship.rotation + 180) * D_TO_R) * WIN_HEIGHT * 2))),
            ((int(self.ship.x), int(self.ship.y)), (int(self.ship.x + math.cos((self.ship.rotation - 180) * D_TO_R) * WIN_WIDTH * 2), int(self.ship.y + math.sin((self.ship.rotation - 180) * D_TO_R) * WIN_HEIGHT * 2)))
        )
        self.distances = self.get_sight()
        self.shoot_cooldown -= 1
        self.hit_asteroid = self.check_collisions(self.win)
        self.bullet_missed = False
        if len(self.asteroids) < 5:
            flag = random.randint(0,1)
            if flag == 0:
                self.attack_player()
            else:
                self.asteroids.append(Asteroid())
        if self.ship.speed != 0:
            self.stationary_count -= 1
        else:
            self.stationary_count -= 2
        if self.stationary_count < 1:
            self.stationary_count = 200
            if len(self.asteroids) < 12:
                self.attack_player()
        for asteroid in self.asteroids:
            asteroid.move()
        for bullet in self.bullets:
            self.bullet_missed = bullet.move()
            if self.bullet_missed:
                self.bullets.remove(bullet)
                break

    def shoot(self):
        if self.shoot_cooldown <= 0:
            self.bullets.append(self.ship.shoot())
            self.shoot_cooldown = 40

    def is_colliding(self, x, y, xTo, yTo, size):
        if x > xTo - size and x < xTo + size and y > yTo - size and y < yTo + size:
            return True
        return False

    def check_collisions(self, win):
        for b in self.bullets:
            for a in self.asteroids:
                if self.is_colliding(b.x, b.y, a.x, a.y, a.size):
                    if a.size != 20:
                        self.asteroids.append(Asteroid(a.x, a.y, a.size / 2, a.direction - random.randrange(5, 20)))
                        self.asteroids.append(Asteroid(a.x, a.y, a.size / 2, a.direction + random.randrange(5, 20)))
                    self.asteroids.remove(a)
                    self.bullets.remove(b)
                    self.score += 1
                    return True
        return False

    def get_sight(self):
        s_lines = self.sight_lines
        distances = []
        for sl in self.sight_lines:
            closest = 10000
            for a in self.asteroids:
                for al in a.lines:
                    coord = find_intersection(sl, al)
                    if coord:
                        dis = get_dis(self.ship.x, coord[0], self.ship.y, coord[1])
                        if dis < closest:
                            closest = dis
            distances.append(closest)
        return distances            

    def attack_player(self):
        s = self.ship
        for i in range(random.randint(2,4)):
            temp = 0
            while abs(temp) < 200:
                x = self.ship.x + random.randint(-300, 300)
                temp = self.ship.x - x
            temp = 0
            while abs(temp) < 200:
                y = self.ship.y + random.randint(-300, 300)
                temp = self.ship.y - y
            angle = math.atan2(self.ship.x - x, y - self.ship.y) * 180 / math.pi + 270
            self.asteroids.append(Asteroid(x,y, -1, angle))
        


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

def neat_main(genomes, config):
    global gen
    gen += 1
    nets = []
    ge = []
    games = []
    best_fitness = 0
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    for _,g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        games.append(Game(win))
        g.fitness = 0
        ge.append(g)
    best_genome = ge[0]

    run = True
    while run:
        clock.tick(30 * GAME_SPEED)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        
        if len(games) < 1:
            run = False
            break

        for x, game in enumerate(games):
            ship = game.ship
            game.move()

            if x == 0:
                s = getattr(game, 'ship')
                b = game.bullets
                a = game.asteroids
                sc = game.score
                draw_window(win, s, b, a, sc, gen)

            outputs = nets[x].activate((game.distances[0], game.distances[1], game.distances[2], game.distances[3], game.distances[4], game.distances[5], game.distances[6], game.distances[7]))
            if outputs[0] > 0.8:
                ship.rotate_left()
            if outputs[1] > 0.8:
                ship.rotate_right()
            if outputs[2] > 0.8:
                ge[x].fitness -= .009
                ship.thrust()
            if outputs[3] > 0.75:
                game.shoot()

            if game.hit_asteroid:
                ge[x].fitness += 2
            if game.bullet_missed:
                ge[x].fitness -= 1
            ge[x].fitness += 0.01
            for a in game.asteroids:
                if game.is_colliding(ship.x, ship.y, a.x, a.y, a.size):
                    ge[x].fitness -= 5
                    if ge[x].fitness > best_fitness:
                        best_fitness = ge[x].fitness
                        best_genome = ge[x]
                    games.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                    break
    #create or open a pickle file to write to named f and save our linear data in it
    name = "pickles/best_genome_gen_" + str(gen) + ".p"
    pickle.dump(best_genome, open(name, "wb"))

def replay_main(genomes, config):
    global gen
    gen += 1
    nets = []
    ge = []
    games = []
    best_fitness = 0
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    for _,g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        games.append(Game(win))
        g.fitness = 0
        ge.append(g)
    best_genome = ge[0]

    run = True
    while run:
        clock.tick(30 * GAME_SPEED)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
    
        if len(games) < 1:
            run = False
            break

        for x, game in enumerate(games):
            ship = game.ship
            game.move()

            if x == 0:
                s = getattr(game, 'ship')
                b = game.bullets
                a = game.asteroids
                sc = game.score
                draw_window(win, s, b, a, sc, gen)
            outputs = nets[x].activate((game.distances[0], game.distances[1], game.distances[2], game.distances[3], game.distances[4], game.distances[5], game.distances[6], game.distances[7]))
            if outputs[0] > 0.8:
                ship.rotate_left()
            if outputs[1] > 0.8:
                ship.rotate_right()
            if outputs[2] > 0.8:
                ship.thrust()
                ge[x].fitness -= (0.005 + self.ship.speed * 0.001)
            if outputs[3] > 0.75:
                game.shoot()

            if game.hit_asteroid:
                ge[x].fitness += 2
            if game.bullet_missed:
                ge[x].fitness -= 1
            ge[x].fitness += .01
            for a in game.asteroids:
                if game.is_colliding(ship.x, ship.y, a.x, a.y, a.size):
                    if ge[x].fitness > best_fitness:
                        best_fitness = ge[x].fitness
                        best_genome = ge[x]
                    print(best_fitness)
                    games.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                    break


def player_main():
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    global gen
    gen = "Player"
    game = Game(win)

    run = True
    while run:
        clock.tick(30 * GAME_SPEED)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        #check for user input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.shoot()

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_w]:
            game.ship.thrust()
        if pressed[pygame.K_a]:
            game.ship.rotate_left()
        if pressed[pygame.K_d]:
            game.ship.rotate_right()

        game.move()
        draw_window(win, game.ship, game.bullets, game.asteroids, game.score, gen)

        for a in game.asteroids:
            if game.is_colliding(game.ship.x, game.ship.y, a.x, a.y, a.size):
                run = False
                break


def load_pickles(config_path):
    file_paths = []
    for root, directories, files in os.walk("pickles"):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
    for path in file_paths:
        replay_genome(config_path, path)

def replay_genome(config_path, pickle_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    with open(pickle_path, "rb") as f:
        genome = pickle.load(f)
    genomes = [(1,genome)]
    replay_main(genomes, config)

                 
def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(neat_main,500)

if __name__ == "__main__":
    flag = True
    while flag:
        print("Would you like to...")
        print("Run NEAT (1)")
        print("Replay the best of each last recorded generation? (2)")
        print("Play the game yourself? (3)")
        x = int(input())
        if x == 1 or x == 2 or x == 3:
            flag = False
    if x == 3:
        player_main()
    input
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    if x == 1:
        run(config_path)
    elif x == 2:
        load_pickles(config_path)
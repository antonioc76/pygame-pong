import pygame
import numpy as np
from enum import Enum
import math
from collections import namedtuple

BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)

GAME_SPEED = 60 # frames per second
DEFAULT_PADDLE_SPEED = 5 # pixels
MAX_BALL_SPEED_X = 10
MAX_BALL_SPEED_Y = 20
MAX_MAGNITUDE = np.sqrt(10**2 + 20**2)
DEFAULT_RESET_WAIT = GAME_SPEED # frames
MAX_MOMENTUM = 100 # must be divisible by 10. Can be left alone, just tweak the scaling
MOMENTUM_STEPS = MAX_MOMENTUM / np.gcd(MAX_MOMENTUM, 10)
MOMENTUM_SCALING = 0.5 # 1 means standard rate of momentum scaling

Point = namedtuple('Point', 'x, y')
Speed_Vector = namedtuple('Speed_Vector', 'x, y')

class Player():
    def __init__(self):
        self.current_score = 0

    def score_points(self, points):
        self.current_score += points

class Paddle():
    def __init__(self, global_center: Point, w, h, color:tuple, game_w, game_h):
        self.game_w = game_w
        self.game_h = game_h
        
        self.w = w
        self.h = h
        self.center = global_center
        self.speed = DEFAULT_PADDLE_SPEED
        self.color = color
        self.speed = Speed_Vector(0, 0)
        self.momentum = 0
        self.momentum_steps = MOMENTUM_STEPS
        self.on_ceiling = False
        self.on_floor = False
    
    def set_speed(self, new_speed:Speed_Vector):
        self.speed = new_speed

    def move_by_speed(self):
        new_center = Point(self.center.x + self.speed.x, self.center.y + self.speed.y)
        if new_center.y - self.h/2 < 0 or new_center.y + self.h/2 > self.game_h: # screen edges
            pass
        
        else:
            self.increment_momentum()

            self.center = new_center
        
    def increment_momentum(self):
        if self.speed.y == 0:
            self.momentum = 0
            return

        next_momentum = self.momentum + self.speed.y

        if (abs(self.momentum) == MAX_MOMENTUM) & (abs(next_momentum) < abs(self.momentum)): # direction change
            self.momentum = 0

        if abs(self.momentum) < MAX_MOMENTUM:
            self.momentum += self.speed.y * MOMENTUM_SCALING

class Ball():
    def __init__(self, global_center: Point, w, h, color:tuple, game_w, game_h):
        self.game_w = game_w
        self.game_h = game_h
        
        self.center = global_center
        self.w = w
        self.h = h
        self.color = color
        self.speed = Speed_Vector(0, 0)
        self.in_front_paddle1 = False
        self.in_front_paddle2 = False
        self.reset_wait = 0

    def clamp_speed(self):
        if self.speed.x > MAX_BALL_SPEED_X:
            new_speed = Speed_Vector(MAX_BALL_SPEED_X, self.speed.y)
            self.speed = new_speed
        elif self.speed.x < -MAX_BALL_SPEED_X:
            new_speed = Speed_Vector(-MAX_BALL_SPEED_X, self.speed.y)
            self.speed = new_speed

        if self.speed.y > MAX_BALL_SPEED_Y:
            new_speed = Speed_Vector(self.speed.x, MAX_BALL_SPEED_Y)
            self.speed = new_speed
        elif self.speed.y < -MAX_BALL_SPEED_Y:
            new_speed = Speed_Vector(self.speed.x, -MAX_BALL_SPEED_Y)
            self.speed = new_speed

        if self.speed.x == 0:
            return
        
        magnitude = np.sqrt(self.speed.x**2 + self.speed.y ** 2)
        angle = np.tan(self.speed.y / self.speed.x)
        if magnitude > MAX_MAGNITUDE:
            new_speed_x = MAX_MAGNITUDE * np.cos(angle)
            new_speed_y = MAX_MAGNITUDE * np.sin(angle)
            new_speed = Speed_Vector(new_speed_x, new_speed_y)
            self.speed = new_speed
    
    def change_speed(self, new_speed:Speed_Vector):
        self.speed = new_speed

        self.clamp_speed()

    def add_speed(self, x_add, y_add):
        new_speed_x = self.speed.x + x_add
        new_speed_y = self.speed.y + y_add
        new_speed = Speed_Vector(new_speed_x, new_speed_y)

        self.change_speed(new_speed)

    def scale_speed(self, x_mult, y_mult):
        new_speed_x = self.speed.x * x_mult
        new_speed_y = self.speed.y * y_mult
        new_speed = Speed_Vector(new_speed_x, new_speed_y)

        self.change_speed(new_speed)
    
    def move_to_position(self, new_center:Point):
        self.center = new_center

    def move_by_speed(self):
        new_center = Point(self.center.x + self.speed.x, self.center.y + self.speed.y)
        self.center = new_center

    def reset(self):
        if self.center.x - self.w/2 < 0 or self.center.x + self.w/2 > self.game_w:
            # ball has been scored
            no_speed = Speed_Vector(0, 0)
            self.change_speed(no_speed)
            screen_center = Point(self.game_w/2, self.game_h/2)
            self.move_to_position(screen_center)
            self.reset_wait = DEFAULT_RESET_WAIT

        elif self.reset_wait > 0:
            self.reset_wait -= 1
        elif self.reset_wait == 0:
            self.reset_wait -= 1
            self.serve()
    
    def serve(self):
        # serve the ball
        print("serving!")
        positive_range = list(range(2, 4))
        negative_range = list(range(-3, -1))
        speed_possibilities = positive_range + negative_range
        start_speed_x = np.random.choice(speed_possibilities)
        start_speed = Speed_Vector(start_speed_x, 0)
        self.change_speed(start_speed)
        print(self.speed)
    
    def get_hit(self, paddle:Paddle):
        # generate random x speed increase
        x_speed_scale = np.random.randint(100, 150) / 100

        # add y speed based on momentum and current ball x speed
        max_possible_y_speed = abs(self.speed.x)
        min_possible_y_speed = 0

        # generate possible y speeds
        steps = paddle.momentum_steps
        step_size = (max_possible_y_speed - min_possible_y_speed)/steps
        positive_speed_possibilities = np.arange(min_possible_y_speed, max_possible_y_speed, step_size)
        negative_speed_possibilities = -1 * positive_speed_possibilities

        # select a speed based on paddle momentum
        choice = None
        momentum_magnitude = abs(paddle.momentum)
        if paddle.momentum > 0:
            #y_speed_increment = np.random.choice(positive_speed_possibilities)
            choice = int(momentum_magnitude/len(positive_speed_possibilities)) - 1
            y_speed_increment = positive_speed_possibilities[choice]
        elif paddle.momentum < 0:
            #y_speed_increment = np.random.choice(negative_speed_possibilities)
            choice = int(momentum_magnitude/len(negative_speed_possibilities)) - 1
            y_speed_increment = negative_speed_possibilities[choice]
        elif paddle.momentum == 0:
            choice = None
            y_speed_increment = 0
        
        new_speed = Speed_Vector(-1 * (self.speed.x * x_speed_scale), self.speed.y + y_speed_increment)
        self.change_speed(new_speed)

class Pong:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h

        # initialize the display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("pong")

        # initialize key press logic
        pygame.key.set_repeat(1)

        self.clock = pygame.time.Clock()

        pygame.font.init()
        self.font = pygame.font.Font('./Lato-Black.ttf', 30)
        self.initialize_players()
        self.initialize_gameobjects()

    def initialize_players(self):
        self.player1 = Player()
        self.player2 = Player()
        self.players = [self.player1, self.player2]

    def initialize_gameobjects(self):
        # paddles
        self.paddles = []
        paddle1_starting_location = Point(20, self.h/2)
        self.paddle1 = Paddle(paddle1_starting_location, 10, 100, BLUE, self.w, self.h)
        self.paddles.append(self.paddle1)

        paddle2_starting_location = Point(self.w-20, self.h/2)
        self.paddle2 = Paddle(paddle2_starting_location, 10, 100, RED, self.w, self.h)
        self.paddles.append(self.paddle2)

        # balls
        self.balls = []
        ball_starting_position = Point(self.w/2, self.h/2)
        self.ball = Ball(ball_starting_position, 10, 10, WHITE, self.w, self.h)
        self.balls.append(self.ball)

    def step_frame(self):
        score = 0
        game_over = False

        self.user_input()

        self.check_collisions()
        for ball in self.balls:
            ball.reset()

        self.move_gameobjects()
        self.update_screen()
        self.clock.tick(GAME_SPEED)

        return game_over, score
    
    def user_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            keys_pressed = pygame.key.get_pressed()
            # left player
            if keys_pressed[pygame.K_w]:
                up_speed = Speed_Vector(0, -DEFAULT_PADDLE_SPEED)
                self.paddle1.set_speed(up_speed)
            elif keys_pressed[pygame.K_s]:
                down_speed = Speed_Vector(0, DEFAULT_PADDLE_SPEED)
                self.paddle1.set_speed(down_speed)
            else:
                no_speed = Speed_Vector(0, 0)
                self.paddle1.set_speed(no_speed)
            # right player
            if keys_pressed[pygame.K_UP]:
                up_speed = Speed_Vector(0, -DEFAULT_PADDLE_SPEED)
                self.paddle2.set_speed(up_speed)
            elif keys_pressed[pygame.K_DOWN]:
                down_speed = Speed_Vector(0, DEFAULT_PADDLE_SPEED)
                self.paddle2.set_speed(down_speed)
            else:
                no_speed = Speed_Vector(0, 0)
                self.paddle2.set_speed(no_speed)

    def check_collisions(self):
        # ball with ceiling or floor
        for ball in self.balls:
            if ball.center.y - ball.h/2 < 0 or ball.center.y + ball.h/2 > self.h:
                ball.scale_speed(1, -1)

        # ball with score zones
        for ball in self.balls:
            if ball.center.x - ball.w/2 < 0:
                self.player2.score_points(1)
            if ball.center.x + ball.w/2 > self.w:
                self.player1.score_points(1)
        
        # paddle with ceiling or floor
        for paddle in self.paddles:
            if paddle.center.y - paddle.h/2 < 0: # ceiling
                paddle.on_ceiling = True
            elif paddle.center.y + paddle.h/2 > self.h: # floor
                paddle.on_floor = True

        # ball with paddle
        # TODO: Ball behind paddle bug
        for ball in self.balls:
            # paddle 1
            # check if ball is in front of first paddle
            if (ball.center.y + ball.h/2 > (self.paddle1.center.y - self.paddle1.h/2)) and (ball.center.y - ball.h/2 < (self.paddle1.center.y + self.paddle1.h/2)):
                ball.in_front_paddle1 = True
            else:
                ball.in_front_paddle1 = False
            
            # paddle 2
            if (ball.center.y + ball.h/2 > (self.paddle2.center.y - self.paddle1.h/2)) and (ball.center.y - ball.h/2< (self.paddle2.center.y + self.paddle1.h/2)):
                ball.in_front_paddle2 = True
            else:
                ball.in_front_paddle2 = False

            # collide
            if (ball.center.x - ball.w/2 < self.paddle1.center.x + self.paddle1.w/2) & ball.in_front_paddle1:
                print("hitting paddle 1")
                ball.get_hit(self.paddle1)
                print(ball.speed)

            if (ball.center.x + ball.w/2 > self.paddle2.center.x - self.paddle2.w/2) & ball.in_front_paddle2:
                print("hitting paddle 2")
                ball.get_hit(self.paddle2)
                print(ball.speed)
        
    def get_random_speed_components(self):
        speed_x_rand = np.random.randint(100, 150) / 100
        
        # fix this, we don't like the gap
        negative_speeds = list(range(-105, -99))
        positive_speeds = list(range(100, 106))

        total_speed_possibilities = negative_speeds + positive_speeds

        speed_y_rand = np.random.choice(total_speed_possibilities) / 100

        return speed_x_rand, speed_y_rand

    def move_gameobjects(self):
        # move paddles
        for paddle in self.paddles:
            paddle.move_by_speed()
        
        # move balls
        for ball in self.balls:
            ball.move_by_speed()

    def render_paddles(self):
        for paddle in self.paddles:
            pygame.draw.rect(self.display, WHITE, pygame.Rect(paddle.center.x - paddle.w/2, paddle.center.y - paddle.h/2, paddle.w, paddle.h))
            normalization_factor = 100 / MAX_MOMENTUM
            momentum_bar_size = (2 * abs(paddle.momentum) / 5) * normalization_factor

            negative_momentum_displacement = 0
            if paddle.momentum < 0:
                negative_momentum_displacement = momentum_bar_size 

            pygame.draw.rect(self.display, paddle.color, pygame.Rect(paddle.center.x, paddle.center.y - negative_momentum_displacement, 2, momentum_bar_size))

    def render_balls(self):
        for ball in self.balls:
            pygame.draw.rect(self.display, self.ball.color, 
                            pygame.Rect(ball.center.x - ball.w/2, ball.center.y - ball.h/2, 
                                        ball.w, ball.h))
    
    def render_scores(self):
        player1_score_surface = self.font.render("p1: " + str(self.player1.current_score), False, WHITE)
        player2_score_surface = self.font.render("p2: " + str(self.player2.current_score), False, WHITE)
        self.display.blit(player1_score_surface, (self.w/2 - player1_score_surface.get_width()/2, 
                                                  self.h - player1_score_surface.get_height() -
                                                  player2_score_surface.get_height()))
        self.display.blit(player2_score_surface, (self.w/2 - player2_score_surface.get_width()/2, 
                                                  self.h - player2_score_surface.get_height()))

    def update_screen(self):
        # Clear the screen
        self.display.fill(BLACK)

        # Render the paddles
        self.render_paddles()
        self.render_balls()
        self.render_scores()
        
        # Update the display
        pygame.display.update()


if __name__ == "__main__":
    game = Pong()
    
    while True:
        game_over, score = game.step_frame()
        if game_over == True:
            break
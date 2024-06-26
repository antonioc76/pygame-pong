from enum import Enum
import numpy as np

class Direction(Enum):
    neutral = 0
    down = 1
    up = 2

class GameStateParameters():
    def __init__(self, game_w=0, game_h=0, max_paddle_speed=0, max_momentum=0, max_ball_speed_x=0, max_ball_speed_y=0):
        self.game_w = game_w
        self.game_h = game_h
        self.max_speed = max_paddle_speed
        self.max_momentum = max_momentum
        self.max_ball_speed_x = max_ball_speed_x
        self.max_ball_speed_y = max_ball_speed_y

class State():
    def __init__(self, game_state_parameters=GameStateParameters(), 
                 my_center_y=0, my_speed=0, my_momentum=0, 
                 opponent_center_y=0, opponent_speed=0, opponent_momentum=0,
                 ball_center_x=0, ball_center_y=0, ball_speed_x=0, ball_speed_y=0):
        # not normalized
        self.game_state_parameters = game_state_parameters
        self.my_center_y = my_center_y
        self.my_speed = my_speed
        self.my_momentum = my_momentum
        self.opponent_center_y = opponent_center_y
        self.opponent_speed = opponent_speed
        self.opponent_momentum = opponent_momentum
        self.ball_center_x = ball_center_x
        self.ball_center_y = ball_center_y
        self.ball_speed_x = ball_speed_x
        self.ball_speed_y = ball_speed_y
    
    def set_parameters(self, game_state_parameters:GameStateParameters):
        self.game_state_parameters = game_state_parameters

    def normalize_state(self):
        self.my_center_y = self.normalize_min_max(0, self.game_state_parameters.game_h, self.my_center_y)
        self.my_speed = self.normalize_min_max(-self.game_state_parameters.max_speed, self.game_state_parameters.max_speed, self.my_speed)
        self.my_momentum = self.normalize_min_max(-self.game_state_parameters.max_momentum, self.game_state_parameters.max_momentum, self.my_momentum) # might need to change
        self.opponent_center_y = self.normalize_min_max(0, self.game_state_parameters.game_h, self.opponent_center_y)
        self.opponent_speed = self.normalize_min_max(-self.game_state_parameters.max_speed, self.game_state_parameters.max_speed, self.opponent_speed)
        self.opponent_momentum = self.normalize_min_max(-self.game_state_parameters.max_momentum, self.game_state_parameters.max_momentum, self.opponent_momentum)
        self.ball_center_x = self.normalize_min_max(0, self.game_state_parameters.game_w, self.ball_center_x)
        self.ball_center_y = self.normalize_min_max(0, self.game_state_parameters.game_h, self.ball_center_y)
        self.ball_speed_x = self.normalize_min_max(-self.game_state_parameters.max_ball_speed_x, self.game_state_parameters.max_ball_speed_x, self.ball_speed_x)
        self.ball_speed_y = self.normalize_min_max(-self.game_state_parameters.max_ball_speed_y, self.game_state_parameters.max_ball_speed_y, self.ball_speed_y)
        
        print(self.ball_speed_x)


    def normalize_min_max(self, min, max, value):
        normalized_value = (value - min) / (max - min)
        print(f"normalizing value: {value} to {normalized_value}")
        return normalized_value

    def print_state(self):
        print("state: ")
        print(f"{self.my_center_y}, {self.my_speed}, {self.my_momentum}")
        print(f"{self.opponent_center_y}, {self.opponent_momentum}, {self.opponent_speed}")
        print(f"{self.ball_center_x}, {self.ball_center_y}, {self.ball_speed_x}, {self.ball_speed_y}")
        print()

class Agent():
    def __init__(self):
        self.brain = 0
        self.direction = Direction.neutral
        self.normalizedState = State()

    def play_random_move(self) -> None:
        random_number = np.random.randint(0, 3)

        self.direction = Direction(random_number)
    
    def set_normalized_state(self, state: State) -> None:
        print("state received: ")
        state.print_state()

        state.normalize_state()
        print("normalized state: ")
        state.print_state()
        self.normalizedState = state

if __name__ == "__main__":
    my_agent = Agent()
    print(my_agent.brain)

    print(my_agent.direction)

    my_agent.play_random_move()

    print(my_agent.direction)
from enum import Enum
import numpy as np

class Direction(Enum):
    neutral = 0
    down = 1
    up = 2

class Agent():
    def __init__(self):
        self.brain = 0
        self.direction = Direction.neutral

    def play_random_move(self):
        random_number = np.random.randint(0, 3)

        self.direction = Direction(random_number)



if __name__ == "__main__":
    my_agent = Agent()
    print(my_agent.brain)

    print(my_agent.direction)

    my_agent.play_random_move()

    print(my_agent.direction)
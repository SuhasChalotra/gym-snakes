import gym
from gym import spaces
from gym.envs.classic_control import rendering
from collections import deque
import random as rd
import numpy as np
from copy import deepcopy
import operator

def add_tup(a,b):
    return tuple(map(operator.add, a, b))

def action_to_direction(act):
    if act == 1:
        return Direction.UP
    if act == 2:
        return Direction.RIGHT
    if act == 3:
        return Direction.DOWN
    if act == 4:
        return Direction.LEFT

class Direction(object):
    UP = (0, -1)
    RIGHT = (1, 0)
    DOWN =(0, 1)
    LEFT = (-1, 0)
    LIST = [UP, RIGHT, DOWN, LEFT]

    def get_opposite(self,direction):
        if direction == self.UP:
            return self.DOWN
        if direction == self.DOWN:
            return self.UP
        if direction == self.LEFT:
            return self.RIGHT
        if direction == self.RIGHT:
            return self.LEFT
        else:
            return None

# To be used more TODO
class Rewards(object):
    food_reward = 5


class SnakesEnv(gym.Env):
    metadata = {'render.modes':['human']}

    class Snake:
        def __init__(self,loc_tuple, direction=Direction.UP, length=3):
            self.body = deque()
            self.direction = direction
            self.length = length
            self._alive_status = True
            self.to_be_rewarded = 0
            self.total_reward = 0
            self.temp_head = None
            self.create_body(loc_tuple,self.direction)

        def is_alive(self):
            return self._alive_status

        def get_head(self):
            return self.body[0]


        def snake_init_collider(self, other_snake):

            if id(self)==id(other_snake):
                for piece in other_snake.body[1:]:
                    if piece==self.get_head():
                        return True

            else:
                if other_snake.is_alive():

                    for piece in other_snake.body:

                        if piece==self.get_head():
                            return True
            return False
        
        
        def create_body(self,position, direction_in):
            # Change the direction because the snake needs to be drawn in the opposite dir
            # than it's facing
            direction = Direction().get_opposite(direction=direction_in)

            #Construct the rest of the snake
            for _ in range(self.length):
                if len(self.body) < 1:
                    self.body.append(position)
                else:
                    temp = add_tup(self.body[len(self.body) - 1],direction)
                    self.body.append(temp)


        """
        These three functions are called on every snake for movement during step phase of the Env        
        """
        def get_new_direction(self, action):
            if self.direction==Direction.LEFT or self.direction==Direction.RIGHT:
                if action in [1,3]:
                    self.direction = action_to_direction(action)
            if self.direction==Direction.UP or self.direction==Direction.DOWN:
                if action in [2,4]:
                    self.direction = action_to_direction(action)

        def get_new_head(self):
            self.temp_head = add_tup(self.get_head(), self.direction)

        def move_new_head(self):
            if not self.is_alive():
                self.temp_head = None
                return
            elif self.to_be_rewarded:
                self.total_reward += self.to_be_rewarded
                self.to_be_rewarded = 0
                self.length += 1
                self.body.appendleft(self.temp_head)
                self.temp_head = None
            else:
                self.body.pop()
                self.body.appendleft(self.temp_head)
                self.temp_head = None

        """
        This function will check for any head collisions
        """
        def head_collision_check(self,other_snake):
            test = self.temp_head
            body = other_snake.body
            for piece in body:
                if piece==test:
                    self._alive_status=False
                    return True
            return False

    def __init__(self):
        self.snakes = []
        self.food_list = []
        self.empty = set()
        self.snake_init_length = 0
        self.num_snakes = 0
        self.food_ratio = 1
        self.num_food = self.num_snakes* self.food_ratio
        self.block_num = 0
        self.block_size = 0
        self.game_windows = None
        self.game_running = False
        self.reward_range=(-50, 50)

    def create_snake_from_empty(self):
        pos_tuple = rd.choice(list(self.empty))
        dir = rd.choice(Direction.LIST)
        snake = self.Snake(pos_tuple,direction=dir)

        while not self._is_valid(snake):
            pos_tuple = rd.choice(list(self.empty))
            dir = rd.choice(Direction.LIST)
            snake = self.Snake(pos_tuple,direction=dir)

        # Remove blocks from empty
        for piece in snake.body:
            self.empty.remove(piece)

        return deepcopy(snake)

    def populate_arrays(self):
        # Populate the empty
        self.empty = set()
        for x in range(self.block_num):
            for y in range(self.block_num):
                self.empty.add((x, y))

        # Populate snakes
        self.snakes = []
        for snake in range(self.num_snakes):
            snake = self.create_snake_from_empty()
            self.snakes.append(snake)
            print(snake.body,snake.is_alive())
        print("DONE!")

        self.food_list = []
        # Populate food_list
        self.generate_food()



    """
        This function is called to test whether the current chosen body
        is under any collisions with other objects.
        Args:

        Returns:
            truth_value(bool): weather the current snake is valid or not

    """
    def _is_valid(self,snake):
        # First we check is any of co-ordinates are negative
        for piece in snake.body:
            if piece[0]<0 or piece[1]<0 :
                return False
            if piece[0]>=self.block_num or  piece[1]>=self.block_num :
                return False

        #Check for collisions with self
        clean_body = set()
        for body_part in snake.body:
            clean_body.add(body_part)
        if len(clean_body) != len(snake.body):
            return False

        # Check collision with other snakes:
        for other_snake in self.snakes :
            if snake.snake_init_collider(other_snake):
                return False

        return True

    def reset(self,num_snakes=10, snake_init_length=3, food_ratio=3, block_num=100, block_size=10):
        self.num_snakes = num_snakes
        self.snake_init_length = snake_init_length
        self.food_ratio = food_ratio
        self.num_food = int(np.ceil(self.num_snakes * self.food_ratio))
        self.block_num = block_num
        self.block_size = block_size
        self.action_space = spaces.MultiDiscrete([[0, 4]] * num_snakes)
        self.observation_space = spaces.Box(-5, 5, (self.block_num, self.block_num))
        self.populate_arrays()
        self.game_running = True


        return self.generate_obs()

    def step(self, actions):
        rewards = []

        for index, action in enumerate(actions):
            if self.snakes[index].is_alive():
                self.snakes[index].get_new_direction(action)
                self.snakes[index].get_new_head()
        self.check_snake_collisions()
        self.check_wall_collisions()
        self.check_for_food_reward(rewards)
        for snake in self.snakes:
            snake.move_new_head()
        self.generate_food()

        done = not self.game_running


        return self.generate_obs(), rewards, done, {}

    def render(self, mode='human', close=False):
        window_size = self.block_num*self.block_size

        if self.game_windows is None:
            self.game_windows = rendering.Viewer(window_size,window_size)

        self.render_snakes(self.game_windows)
        self.render_food(self.game_windows)

        return self.game_windows.render(return_rgb_array=mode=='rgb_array')


    def check_snake_collisions(self):
        for snake in self.snakes:
            if not snake.is_alive():
                pass
            for other_snake in self.snakes:
                if snake.head_collision_check(other_snake):
                    self.kill_snake(snake)

    def check_wall_collisions(self):
        for snake in self.snakes:
            if snake.is_alive():
                x, y = snake.temp_head

                if x >= self.block_num or y >= self.block_num or x < 0 or y < 0:
                    snake._alive_status = False
                    self.kill_snake(snake)

    def check_for_food_reward(self,rewards):
        for snake in self.snakes:
            if snake.is_alive():
                head = snake.get_head()
                for food in self.food_list:
                    if head==food:
                        snake.to_be_rewarded = Rewards.food_reward
                        self.food_list.remove(food)
                        self.empty.add(food)

            rewards.append(snake.to_be_rewarded)

    def generate_obs(self):
        obs = []
        gen_snake_obs = np.zeros([self.block_num, self.block_num])
        for snake in self.snakes:
            if snake.is_alive():
                for piece in snake.body:
                    gen_snake_obs[piece] = -1

        for food in self.food_list:
            gen_snake_obs[food] = 5

        for snake in self.snakes:
            snake_copy = deepcopy(gen_snake_obs)
            for piece in snake.body:
                snake_copy[piece] = 1
            obs.append(snake_copy)

        return obs

    def kill_snake(self,snake):
        if not snake.is_alive():
            for piece in snake.body:
                self.empty.add(piece)

        for snake in self.snakes:
            if snake.is_alive():
                return
            else:
                pass
        self.game_running = False

    def generate_food(self):
        num_to_make = self.num_food - len(self.food_list)
        while num_to_make:
            if num_to_make > len(self.empty):
                self.game_running = False
                return

            food = rd.choice(list(self.empty))
            self.empty.remove(food)
            self.food_list.append(food)

            num_to_make = self.num_food - len(self.food_list)

    def render_snakes(self,viewer):
        for snake in self.snakes:
            head = snake.get_head()
            if snake.is_alive():
                for x,y in snake.body:
                    if (x,y)==head:
                        self.draw(x, y, viewer, (0,0,0))
                    else:
                        self.draw(x, y, viewer, (0, 4, 0))

    def render_food(self,viewer):
        for x,y in self.food_list:
            self.draw(x, y, viewer,(4,0,0))

    def draw(self, x, y, viewer,color):
        left = x * self.block_size
        right = (x + 1) * self.block_size
        top = y * self.block_size
        bottom = (y + 1) * self.block_size

        square = rendering.FilledPolygon([(left,bottom),(left,top),(right,top),(right,bottom)])
        r,g,b = color
        square.set_color(r, g, b)
        viewer.add_onetime(square)

import gym

from gym import spaces
from gym.utils import seeding
import numpy as np
from copy import deepcopy
import pygame
import random as rd

DIR_NORTH = 0
DIR_EAST = 1
DIR_SOUTH = 2
DIR_WEST = 3

#TODO Make relevant params priv & use set/getter funcs instd

class SnakesEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    class Snake:
        snake_id_counter = 0

        """Defining a new class which is a linked list implementation with 
                    specific functions and parameters for the snake class         
                    """

        class SnakeLink:
            def __init__(self, x_pos, y_pos, next_link=None, link_dimension=20):
                self.xPos = x_pos
                self.yPos = y_pos
                self.next = next_link
                self.link_dimension = link_dimension

            def has_collided(self, other):
                if np.abs(self.xPos - other.xPos) < self.link_dimension and \
                        np.abs(self.yPos - other.yPos) < self.link_dimension:
                    return True
                else:
                    return False

        # Ending of SnakeLink

        def __init__(self, x_in, y_in, block_size, direction=DIR_NORTH, length_in=3):
            self.length = length_in
            self.direction = direction
            self.block_size = block_size
            self.color = tuple(rd.randint(0, 255) for _ in range(3))
            self.snake_id_counter += 1
            self.id = "{0}".format(self.snake_id_counter)

            self.headPos = self.SnakeLink(x_pos=x_in, y_pos=y_in, link_dimension=self.block_size)
            curr = self.headPos

            for i in range(length_in):
                if self.direction == DIR_NORTH:
                    x_in -= self.block_size
                elif self.direction == DIR_EAST:
                    y_in -= self.block_size
                elif self.direction == DIR_SOUTH:
                    x_in += self.block_size
                elif self.direction == DIR_WEST:
                    y_in += self.block_size

                curr.next = self.SnakeLink(x_pos=x_in, y_pos=y_in, link_dimension=self.block_size)
                curr = curr.next


        """Since our Snake class is stored as a linked list, we only need to pop the tail and move it 
        to where the head should have been. So we write the following two functions :One find where the 
         snake moves to and the Second one to move the tail of the snake link as the head"""

        def find_head_spot(self, action):
            if action == DIR_NORTH:
                if self.direction == DIR_EAST or self.direction == DIR_WEST:
                    self.direction = DIR_NORTH

            elif action == DIR_EAST:
                if self.direction == DIR_NORTH or self.direction == DIR_SOUTH:
                    self.direction = DIR_EAST

            elif action == DIR_SOUTH:
                if self.direction == DIR_EAST or self.direction == DIR_WEST:
                    self.direction = DIR_SOUTH

            elif action == DIR_WEST:
                if self.direction == DIR_NORTH or self.direction == DIR_SOUTH:
                    self.direction = DIR_WEST

        def move_head(self, action):
            prev = self.headPos
            curr = prev.next

            # Loop to find the last tail piece(curr) and the second last tail piece(prev)
            while curr.next:
                prev = curr
                curr = curr.next
            # Making prev the new tail and keeping curr to
            prev.next = None



            # Calling the function written above to change the direction of snake according
            # to action by user or agent
            self.find_head_spot(action)

            # Set the position of the old tail to the current head and then "move" the snake
            # according to action
            curr.x_pos = self.headPos.x_pos
            curr.y_pos = self.headPos.y_pos

            if self.direction == DIR_NORTH:
                curr.x_pos -= self.block_size
            elif self.direction == DIR_EAST:
                curr.y_pos -= self.block_size
            elif self.direction == DIR_SOUTH:
                curr.x_pos += self.block_size
            elif self.direction == DIR_WEST:
                curr.y_pos += self.block_size

            curr.next = self.headPos # Set new head
            self.headPos = curr

            def generate_snake():
                pass # TODO

            """Checks if the head of the snake collided with anything, or good or bad
            Returns -1 if dead, 0 if nothing and 1 if reward
            """
            def head_collision_check(self, other):
                pass # TODO

    """
    
    """
    def __init__(self, num_snakes=2, food_abund_factor=1.5, window_size_factor=15, delta_size=20,length=3):
        self.game_on = True
        self.num_snakes = num_snakes
        self.num_fruits = np.ceil(num_snakes*food_abund_factor)
        self.window_size = window_size_factor*delta_size
        self.delta_size = delta_size
        self.length = length
        self.snakes = []
        self.food = []
        self.screen = None
        self.food_surfaces = []
        self.snake_surfaces = []

        # Now defining some spaces for the Gym Env
        self.observation_space
        self.reward_range
        self.action_space = spaces.MultiDiscrete


    def _step(self, action):
        obs = []

        # TODO
    def _render(self, mode='human', close=False):
        self.pygame_init()
        self.generate_background()
        self.generate_snakes()
        self.generate_food()
        pygame.display.update()

    def _reset(self):




    def _seed(self, seed=None):
        pass# TODO
    def _close(self):
        pygame.quit()




    def pygame_init(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.window_size, self.window_size),
                                              pygame.HWSURFACE)
        for index, snake in enumerate(self.s)


    def generate_background(self):
        pass # TODO

    def generate_snakes(self):
        x_pos, y_pos = rd.randint(self.length+1, )
        for i in range(self.num_snakes):
            self.snakes.append(self.Snake())
            # TODO

    def generate_food(self):
        pass #TODO

    def generate_obs(self):
        pass










import pygame
import random
import numpy as np
from npnn import NeuralNetwork

class Bird():

    def __init__(self, screen, bird=None, mutation_rate=None):
        self.radius = 10
        self.gravity = 1
        self.x = 50
        self.y = 50
        self.yvelocity = 0
        self.screen = screen
        self.score = 0
        self.colour = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

        if not bird:
            self.brain = Brain()
        else:
            self.brain = bird.brain.mutate(mutation_rate)

    def __hash__(self):
        return hash(self.colour)
    
    def __eq__(self, other):
        if isinstance(other, Bird):
            return self.colour == other.colour
        
    def mutate(self, mutation_factor):
        return self.brain.mutate(mutation_factor)
        
    def draw(self):
        pygame.draw.circle(self.screen, self.colour, (self.x, self.y), self.radius)
    
    def choice(self, pipe_dst, gap_top, gap_bot):
        if np.argmax(self.brain.predict(self.y, self.yvelocity, pipe_dst, gap_top, gap_bot)) == 0:
            self.jump()

    def jump(self):
        if not self.yvelocity < 0:
            self.yvelocity -= 15

    def update(self):
        # update y position
        self.y += self.yvelocity

        # update velocity
        if self.yvelocity < 10:
            self.yvelocity += self.gravity

    def collides(self, pipe):
        # Check if bird is within pipe's area
        # Check x position is overlapping
        if self.x > pipe.toplft[0] and self.x < pipe.toplft[0] + pipe.width:
            # Check y position is above or below pipe gap
            if self.y < pipe.gapy or self.y > pipe.gapy + pipe.gapdst:
                return True
        return False
    
    def out_of_bounds(self):
        if self.y < 0 or self.y > self.screen.get_height():
            return True
        return False
    
    def set_score(self, score):
        self.score = score


class Pipe():

    def __init__(self, screen, num):
        self.screen = screen
        self.width = 60
        self.height = self.screen.get_height()
        self.toplft = (self.screen.get_width(), 0)
        self.xvelocity = -10
        self.colour = (255, 255, 255)
        self.pipe_number = num + 1

        # gapy is the the y coordinate for start of gap
        self.gapy = random.randint(self.height * 0.1, self.height * 0.6)
        # gapdst is the height of the gap
        self.gapdst = 100

    def __eq__(self, other):
        if self.gapy == other.gapy:
            return True
        return False

    def draw(self):
        pygame.draw.rect(self.screen, self.colour, 
                         (self.toplft[0], 0, 
                          self.width, self.gapy))
        pygame.draw.rect(self.screen, self.colour,
                         (self.toplft[0], self.gapdst + self.gapy,
                          self.width, self.height - self.gapy - self.gapdst))
        
        font = pygame.font.Font(None, 44)
        pipe_count_surface = font.render(f"{self.pipe_number}", True, (0,0,0))
        pipe_count_rect = pipe_count_surface.get_rect()
        pipe_count_rect.center = (self.toplft[0] + self.width / 2, self.height * 0.95)

        self.screen.blit(pipe_count_surface, pipe_count_rect)

    def update(self):
        # update toplft coordinates
        self.toplft = (self.toplft[0] + self.xvelocity, 0)
        

class Brain():

    def __init__(self, model=None):

        if not model:
            self.model = NeuralNetwork(5, 4, 2)
        else:
            self.model = model
    
    def predict(self, y_pos, y_vel, pipe_dst, gap_top, gap_bot):

        # input_data = np.array([y_pos, y_vel, pipe_dst, gap_top, gap_bot])

        input_data = [y_pos, y_vel, pipe_dst, gap_top, gap_bot]

        # input_data = input_data.reshape(-1,5)

        prediction = self.model.feedforward(input_data)
        return prediction
    
    def mutate(self, mutation_factor):

        new_model = self.model.copy()

        new_model.mutate(mutation_factor)

        return Brain(new_model)

    def __eq__(self, other):

        if self.model == other.model:
            return True
        return False
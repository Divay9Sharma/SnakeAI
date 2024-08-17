import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()

Point = namedtuple('Point','x, y')

font = pygame.font.SysFont('arial',25)

WHITE = (255,255,255)
RED = (200,0,0)
BLUE1 = (0,0,255)
BLUE2 = (0,100,255)
BLACK = (0,0,0)

BLOCK_SIZE = 20

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

class SnakeGameAI:
    
    def __init__(self,w=640,h=480):
        self.w = w
        self.h = h
        
        self.display = pygame.display.set_mode((self.w,self.h))
        pygame.display.set_caption('Snake')
        
        self.clock = pygame.time.Clock()
        self.speed = 50
        self.reset()
        
    def reset(self):
        self.direction = Direction.RIGHT
        self.head = Point(self.w/2,self.h/2)
        self.snake = [self.head,Point(self.head.x - BLOCK_SIZE,self.head.y),Point(self.head.x - 2*BLOCK_SIZE,self.head.y)]
        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def _place_food(self):
        x = random.randint(0,(self.w - BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        y = random.randint(0,(self.h - BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        self.food = Point(x,y)
        if self.food in self.snake:
            self._place_food()
    
    def play_step(self,action):
        self.frame_iteration += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()
        
        self._move(action)
        self.snake.insert(0,self.head)
        
        reward = 0.01*self.score
        game_over = False
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            reward = -10
            game_over = True
            return reward, game_over, self.score
        
        if self.head == self.food:
            self.score += 1
            reward = (10 - 0.1*self.score)
            self._place_food()
        else:
            self.snake.pop()
            
        self._update_ui()
        self.clock.tick(self.speed)
        
        return reward, game_over, self.score
    
    def is_collision(self, pt=None):
        if pt == None:
            pt = self.head
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        if pt in self.snake[1:]:
            return True
        
        return False
    
    def _move(self, action):

        clock_wise = [Direction.RIGHT,Direction.DOWN,Direction.LEFT,Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action,[1,0,0]):
            self.direction = clock_wise[idx]
        elif np.array_equal(action,[0,1,0]):
            self.direction = clock_wise[(idx+1)%4]
        else:
            self.direction = clock_wise[(idx-1)%4]
        
        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        
        self.head = Point(x,y)
    
    def _update_ui(self):
        self.display.fill(BLACK)
        
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, BLOCK_SIZE-12, BLOCK_SIZE-12))
        
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def flood_fill(self):
        if self.direction == Direction.RIGHT:
            right = Point(self.head.x, self.head.y + BLOCK_SIZE)
            left = Point(self.head.x, self.head.y - BLOCK_SIZE)
            top = Point(self.head.x + BLOCK_SIZE, self.head.y)
        elif self.direction == Direction.LEFT:
            right = Point(self.head.x, self.head.y - BLOCK_SIZE)
            left = Point(self.head.x, self.head.y + BLOCK_SIZE)
            top = Point(self.head.x - BLOCK_SIZE, self.head.y)
        elif self.direction == Direction.UP:
            right = Point(self.head.x + BLOCK_SIZE, self.head.y)
            left = Point(self.head.x - BLOCK_SIZE, self.head.y)
            top = Point(self.head.x, self.head.y - BLOCK_SIZE)
        elif self.direction == Direction.DOWN:
            right = Point(self.head.x - BLOCK_SIZE, self.head.y)
            left = Point(self.head.x + BLOCK_SIZE, self.head.y)
            top = Point(self.head.x, self.head.y + BLOCK_SIZE)

        visited = []
        length = 0
        right_safe = self._ff_helper(right, visited, length)
        #print(visited,self.food,right_safe,length)
        visited = []
        left_safe = self._ff_helper(left, visited,length)
        #print(visited,self.food,left_safe, length)
        visited = []
        top_safe = self._ff_helper(top, visited,length)
        #print(visited,self.food,top_safe, length)

        # if not(left_safe and right_safe):
        #     print(left_safe,right_safe)
        
        return left_safe,right_safe,top_safe

    
    def _ff_helper(self, point, visited, length):
        if length > 2*len(self.snake):
            return True
        if self.is_collision(point) or point in visited or point == self.head:
            return False
        
        length += 1
        visited.append(point)

        return self._ff_helper(Point(point.x + BLOCK_SIZE, point.y),visited,length) or self._ff_helper(Point(point.x - BLOCK_SIZE, point.y),visited,length) or self._ff_helper(Point(point.x, point.y + BLOCK_SIZE),visited,length) or self._ff_helper(Point(point.x, point.y - BLOCK_SIZE),visited,length)
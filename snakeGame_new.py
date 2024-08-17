import pygame
import random
from enum import Enum
from collections import namedtuple

pygame.init()

Point = namedtuple('Point','x, y')

font = pygame.font.SysFont('arial',25)

WHITE = (255,255,255)
RED = (200,0,0)
BLUE1 = (0,0,255)
BLUE2 = (0,100,255)
BLACK = (0,0,0)
POWER1 = (235, 125, 52)
POWER2 = (58, 235, 52)
POWER3 = (52, 235, 226)
SOLID = (168, 145, 50)

BLOCK_SIZE = 20

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

class Power(Enum):
    HALF_LENGTH = 1
    DOUBLE_POINT = 2
    INVISIBLE = 3

class SnakeGame:
    
    def __init__(self,w=640,h=480):
        self.w = w
        self.h = h
        
        self.display = pygame.display.set_mode((self.w,self.h))
        pygame.display.set_caption('Snake')
        
        self.clock = pygame.time.Clock()
        
        self.speed = 10
        self.direction = Direction.RIGHT
        self.head = Point(self.w/2,self.h/2)
        self.snake = [self.head,Point(self.head.x - BLOCK_SIZE,self.head.y),Point(self.head.x - 2*BLOCK_SIZE,self.head.y)]
        self.solidPart = []
        self.score = 0
        self.food = None

        self.power = None
        self.isPowerActive = False
        self.powerTimer = 0
        self.currentPower = None
        self.isDoublePoint = False
        self.isInvisible = False
        
        self.statsForNerds = False

        self._place_food()
    
    def play_step(self):
        # player controls
        direction = self.direction
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()
                if event.key == pygame.K_LEFT:
                    direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    direction = Direction.RIGHT
                elif event.key == pygame.K_UP:
                    direction = Direction.UP
                elif event.key == pygame.K_DOWN:
                    direction = Direction.DOWN
                elif event.key == pygame.K_n:
                    if self.statsForNerds:
                        self.statsForNerds = False
                    else:
                        self.statsForNerds = True
        
        if direction == Direction.RIGHT and self.direction != Direction.LEFT:
            self.direction = direction
        elif direction == Direction.LEFT and self.direction != Direction.RIGHT:
            self.direction = direction
        elif direction == Direction.UP and self.direction != Direction.DOWN:
            self.direction = direction
        elif direction == Direction.DOWN and self.direction != Direction.UP:
            self.direction = direction

        #print(self.direction)
        self._move()
        self.snake.insert(0,self.head)
        
        # collision
        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score
        
        # collecting power
        if self.head == self.power:
            self.power = None
            self.isPowerActive = False
            self._enable_power()
            self.powerTimer = pygame.time.get_ticks()

        # power timer
        seconds = (pygame.time.get_ticks() - self.powerTimer)/1000
        if seconds > 5 and self.isPowerActive:
            self.power = None
            self.isPowerActive = False
            self.currentPower = None
        elif seconds > 8 and self.isDoublePoint:
            self.isDoublePoint = False
            self.currentPower = None
        elif seconds > 10 and self.isInvisible:
            self.isInvisible = False
            self.currentPower = None

        # collecting food
        if self.head == self.food:
            if self.score%30 == 0:
                self.speed += 1
            if self.isDoublePoint:
                self.score += 2
            else:
                self.score += 1
            self._place_food()
            
            # powers
            if self.score%10 == 0:
                self._place_power()
                self.isPowerActive = True
                self.currentPower = random.choice(['INVISIBLE','HALF_LENGTH','DOUBLE_POINT'])
                self.powerTimer = pygame.time.get_ticks()
        else:
            self.snake.pop()
        
        # update ui
        self._update_ui()
        self.clock.tick(self.speed)
        
        return game_over, self.score
    
    def _enable_power(self):
        if Power.HALF_LENGTH.name == self.currentPower:
            for pt in self.snake[len(self.snake)//2:]:
                self.solidPart.append(pt)
            self.snake = self.snake[:len(self.snake)//2]
            self.currentPower = None
        elif Power.DOUBLE_POINT.name == self.currentPower:
            self.isDoublePoint = True
        elif Power.INVISIBLE.name == self.currentPower:
            self.isInvisible = True

    def _place_food(self):
        x = random.randint(0,(self.w - BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        y = random.randint(0,(self.h - BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        self.food = Point(x,y)
        if self.food in self.snake or self.food in self.solidPart:
            self._place_food()

    def _place_power(self):
        x = random.randint(0,(self.w - BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        y = random.randint(0,(self.h - BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        self.power = Point(x,y)
        if self.power in self.snake or self.power in self.food or self.power in self.solidPart:
            self._place_power()

    def _is_collision(self):
        #if self.head.x > self.w - BLOCK_SIZE or self.head.x < 0 or self.head.y > self.h - BLOCK_SIZE or self.head.y < 0:
        #    return True
        if self.isInvisible:
            return False
        if self.head in self.snake[1:] or self.head in self.solidPart:
            return True
        return False
    
    def _move(self):
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

        if x > self.w - BLOCK_SIZE:
            x = 0
        elif x < 0:
            x = self.w - BLOCK_SIZE
        if y > self.h - BLOCK_SIZE:
            y = 0
        elif y < 0:
            y = self.h - BLOCK_SIZE
        self.head = Point(x,y)
    
    def _update_ui(self):
        self.display.fill(BLACK)
        
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, BLOCK_SIZE-12, BLOCK_SIZE-12))
        
        for pt in self.solidPart:
            pygame.draw.rect(self.display, SOLID, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        
        if self.currentPower != None and self.isPowerActive == False:
            power = font.render(str(self.currentPower), True, WHITE)
            self.display.blit(power, [300, 0])
            if self.currentPower == Power.INVISIBLE.name:
                pygame.draw.rect(self.display, POWER3, pygame.Rect(self.head.x-1, self.head.y-1, BLOCK_SIZE+2, BLOCK_SIZE+2))
            elif self.currentPower == Power.DOUBLE_POINT.name:
                pygame.draw.rect(self.display, POWER2, pygame.Rect(self.head.x-1, self.head.y-1, BLOCK_SIZE+2, BLOCK_SIZE+2))
            elif self.currentPower == Power.HALF_LENGTH.name:
                pygame.draw.rect(self.display, POWER1, pygame.Rect(self.head.x-1, self.head.y-1, BLOCK_SIZE+2, BLOCK_SIZE+2))
        else:
            pygame.draw.rect(self.display, WHITE, pygame.Rect(self.head.x-1, self.head.y-1, BLOCK_SIZE+2, BLOCK_SIZE+2))

        if self.isPowerActive:
            power = font.render(str(self.currentPower), True, WHITE)
            self.display.blit(power, [300, 0])
            if self.currentPower == Power.HALF_LENGTH.name:
                pygame.draw.rect(self.display, POWER1, pygame.Rect(self.power.x, self.power.y, BLOCK_SIZE, BLOCK_SIZE))
            elif self.currentPower == Power.DOUBLE_POINT.name:
                pygame.draw.rect(self.display, POWER2, pygame.Rect(self.power.x, self.power.y, BLOCK_SIZE, BLOCK_SIZE))
            elif self.currentPower == Power.INVISIBLE.name:
                pygame.draw.rect(self.display, POWER3, pygame.Rect(self.power.x, self.power.y, BLOCK_SIZE, BLOCK_SIZE))
        
        text = font.render("Score: " + str(self.score), True, WHITE)
        stats1 = font.render("Speed: " + str(self.speed) + " Time: " + str(int(pygame.time.get_ticks()/1000)) + 
            " Power Timer: " + str((pygame.time.get_ticks() - self.powerTimer)/1000), True, WHITE)
        stats2 = font.render("isPowerActive: " + str(self.isPowerActive) +  
            " isDoublePoint: " + str(self.isDoublePoint) + " isInvisible: " + str(self.isInvisible), True, WHITE)
        self.display.blit(text, [0, 0])
        if self.statsForNerds:
            self.display.blit(stats1, [0, 30])
            self.display.blit(stats2, [0, 60])
        pygame.display.flip()
        
        
if __name__=='__main__':
    game = SnakeGame()
    
    while True:
        game_over, score = game.play_step()
        
        if game_over == True:
            break
    
    print('Final Score',score)
    
    pygame.quit()
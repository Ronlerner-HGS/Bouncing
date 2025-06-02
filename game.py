import pygame
import random

pygame.init()

# Constants
WIDTH, HEIGHT = 600, 400
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Create window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Object Bounce Simulation")
clock = pygame.time.Clock()

# Font 
font = pygame.font.SysFont(None, 40)

# Object class 
class MovingObject:
    def __init__(self, shape):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.size = random.randint(20, 50)
        self.dx = random.choice([-4, 4])
        self.dy = random.choice([-4, 4])
        self.color = self.random_color()
        self.shape = shape

    def random_color(self):
        return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

    def update(self):
        self.x += self.dx
        self.y += self.dy

        # Collision detection with walls (Source: pygame docs)
        if self.x <= 0 or self.x + self.size >= WIDTH:
            self.dx = -self.dx
            self.color = self.random_color()
        if self.y <= 0 or self.y + self.size >= HEIGHT:
            self.dy = -self.dy  
            self.color = self.random_color()

    def draw(self, screen): # (Source: pygame docs)
        if self.shape == 'square':
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))
        elif self.shape == 'circle':
            pygame.draw.circle(screen, self.color, (self.x + self.size // 2, self.y + self.size // 2), self.size // 2)
        elif self.shape == 'triangle':
            points = [(self.x, self.y + self.size), (self.x + self.size // 2, self.y), (self.x + self.size, self.y + self.size)]
            pygame.draw.polygon(screen, self.color, points)

# Menu function lets you pick the object you want to bounce.

def menu():
    screen.fill(BLACK)
    title = font.render("Select an Object to Spawn", True, WHITE)
    screen.blit(title, (WIDTH//2 - 150, 50))

    square_btn = font.render("1. Square", True, WHITE)
    circle_btn = font.render("2. Circle", True, WHITE)
    triangle_btn = font.render("3. Triangle", True, WHITE)

    screen.blit(square_btn, (WIDTH//2 - 70, 120))
    screen.blit(circle_btn, (WIDTH//2 - 70, 160))
    screen.blit(triangle_btn, (WIDTH//2 - 70, 200))

    pygame.display.flip()

# Game loop
objects = []
running = True
menu_open = True

while running:
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, HEIGHT), 5)

    if menu_open:
        menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    objects.append(MovingObject('square'))
                    menu_open = False
                if event.key == pygame.K_2:
                    objects.append(MovingObject('circle'))
                    menu_open = False
                if event.key == pygame.K_3:
                    objects.append(MovingObject('triangle'))
                    menu_open = False
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                menu_open = True

        # Updates the objects and draws to the screen.
        for obj in objects:
            obj.update()
            obj.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

pygame.quit()

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import math


#ignore everything up to line 73, before that is just documentation stuff, prerequeists, barley written by me

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


# I HAVE NO IDEA WHAT I'M DOING, BUT HERE'S SOME CODE,
# Imma be honnest, I just copied snippests from a docs and made it work
# only some parts, this is geniune code
def init_gl():
    """Initialize OpenGL settings"""
    # Set up the display
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("3D Bouncing Balls")

    # Set up perspective - copied from OpenGL tutorial
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(SCREEN_WIDTH)/float(SCREEN_HEIGHT), 0.1, 100.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Enable depth testing,
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)

    # Lighting setup - this part from OpenGL docs
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Set light properties,
    # why these values? I have no idea, they just work

    # Light position: x=2, y=2, z=2, w=1 (w=1 means positional light, w=0 would be directional)
    light_pos = [2.0, 2.0, 2.0, 1.0]
    # Ambient light: low-intensity background lighting (R, G, B, Alpha)
    light_ambient = [0.3, 0.3, 0.3, 1.0]
    # Diffuse light: main directional lighting that creates shadows (R, G, B, Alpha)
    light_diffuse = [0.8, 0.8, 0.8, 1.0]

    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)

    # Material properties
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)

def draw_sphere(radius=1.0, slices=20, stacks=20):
    """Draw a sphere using GLU quadrics"""
    quad = gluNewQuadric()
    gluQuadricDrawStyle(quad, GLU_FILL)
    gluQuadricNormals(quad, GLU_SMOOTH)
    gluSphere(quad, radius, slices, stacks)
    gluDeleteQuadric(quad)

class BouncingBall:
    def __init__(self, x=None, y=None, z=None):
        #Random intial postion of balls
        if x is None:
            x = random.uniform(-3.0, 3.0)
        if y is None:
            y = random.uniform(-2.0, 2.0)
        if z is None:
            z = random.uniform(-3.0, 3.0)

        self.x = x
        self.y = y
        self.z = z

        # Random velocity
        self.vx = random.uniform(-0.08, 0.08)
        self.vy = random.uniform(-0.08, 0.08)
        self.vz = random.uniform(-0.08, 0.08)

        self.radius = random.uniform(0.15, 0.4)

        # Random color
        self.r = random.random()
        self.g = random.random()
        self.b = random.random()

        # Boundaries
        self.boundary = 3.5

    def update_position(self):
        """Update ball position and handle collisions"""
        # Move the ball, difference from last one is that this is 3D
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz

        # Check boundaries and bounce
        # I hate myself for choosing to do this
        # IDE giving 200 warnings and 2 erorrs, asked ai to explain 33 times, complex math that i don't understand,

        if self.x + self.radius > self.boundary or self.x - self.radius < -self.boundary:
            self.vx = -self.vx
            self.x = max(-self.boundary + self.radius, min(self.boundary - self.radius, self.x))
            # Change color when bouncing - makes it more interesting
            self.r = random.random()

        if self.y + self.radius > self.boundary or self.y - self.radius < -self.boundary:
            self.vy = -self.vy
            self.y = max(-self.boundary + self.radius, min(self.boundary - self.radius, self.y))
            self.g = random.random()

        if self.z + self.radius > self.boundary or self.z - self.radius < -self.boundary:
            self.vz = -self.vz
            self.z = max(-self.boundary + self.radius, min(self.boundary - self.radius, self.z))
            self.b = random.random()

    def render(self):
        # more stuff that needs a phd to understand.
        # also why reinvent the wheel?
        # in the real world you would use a game engine for this
        """Render the ball"""
        glPushMatrix()

        glTranslatef(self.x, self.y, self.z)
        glColor3f(self.r, self.g, self.b)

        draw_sphere(self.radius, 24, 24)

        glPopMatrix()
# only code here i actually fully understand
def main():
    init_gl()

    clock = pygame.time.Clock()

    # Create some balls, more the better
    num_balls = 6
    balls = []
    for i in range(num_balls):
        ball = BouncingBall()
        balls.append(ball)

    rotation_angle = 0.0
    running = True

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Add some balls with spacebar
                elif event.key == pygame.K_SPACE:
                    balls.append(BouncingBall())

        # Clear buffers, # this is the part that makes the screen black
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Reset modelview matrix
        glLoadIdentity()

        # Move camera back and add some rotation for better view
        glTranslatef(0.0, 0.0, -8.0)
        glRotatef(rotation_angle * 0.5, 1.0, 1.0, 0.0)

        # Update and draw all balls
        for ball in balls:
            ball.update_position()
            ball.render()

        rotation_angle += 1.0
        if rotation_angle > 360:
            rotation_angle = 0

        pygame.display.flip()
        clock.tick(60)  # 60 FPS

    pygame.quit()


if __name__ == "__main__":
    main()

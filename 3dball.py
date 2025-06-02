import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

import math
import random
import numpy as np

# Ball class to represent a 3D ball with physics
class Ball:
    def __init__(self, position=(0, 0, 0), velocity=(0, 0, 0), radius=1.0, color=(1, 0.5, 0.2)):
        self.position = list(position)
        self.velocity = list(velocity)
        self.radius = radius
        self.color = color
        self.gravity = -9.8  # Gravity constant
        self.bounce_factor = 0.8  # Energy retention after bounce
        self.material_ambient = (0.2 * color[0], 0.2 * color[1], 0.2 * color[2], 1.0)
        self.material_diffuse = (0.8 * color[0], 0.8 * color[1], 0.8 * color[2], 1.0)
        self.material_specular = (1.0, 1.0, 1.0, 1.0)
        self.material_shininess = 50.0
        self.trail = []  # Store previous positions for trail effect
        self.max_trail_length = 20
        self.creation_time = pygame.time.get_ticks() / 1000.0  # Track when the ball was created

    def update(self, delta_time, bounds):
        # Store position for trail every other frame to optimize
        if random.random() > 0.5:  # Only store ~50% of positions to save memory
            if len(self.trail) >= self.max_trail_length:
                self.trail.pop(0)
            self.trail.append(list(self.position))
        
        # Apply gravity to y-velocity (vertical direction)
        self.velocity[1] += self.gravity * delta_time
        
        # Apply air resistance (drag)
        drag_factor = 0.02
        for i in range(3):
            self.velocity[i] *= (1 - drag_factor * delta_time)
        
        # Update position based on velocity
        for i in range(3):
            self.position[i] += self.velocity[i] * delta_time
        
        # Check for collisions with boundaries
        for i in range(3):
            if self.position[i] - self.radius < bounds[i][0]:
                self.position[i] = bounds[i][0] + self.radius
                self.velocity[i] *= -self.bounce_factor
            elif self.position[i] + self.radius > bounds[i][1]:
                self.position[i] = bounds[i][1] - self.radius
                self.velocity[i] *= -self.bounce_factor

    def draw(self, show_trails=True):
        # Draw trail first if enabled
        if show_trails and len(self.trail) > 2:
            glDisable(GL_LIGHTING)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
            glBegin(GL_LINE_STRIP)
            for i, pos in enumerate(self.trail):
                # Calculate alpha based on position in trail
                alpha = i / len(self.trail)
                glColor4f(self.color[0], self.color[1], self.color[2], alpha * 0.5)
                glVertex3f(pos[0], pos[1], pos[2])
            glEnd()
            
            glDisable(GL_BLEND)
            glEnable(GL_LIGHTING)
        
        # Draw the ball
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])
        
        # Set material properties
        glMaterialfv(GL_FRONT, GL_AMBIENT, self.material_ambient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, self.material_diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, self.material_specular)
        glMaterialf(GL_FRONT, GL_SHININESS, self.material_shininess)
        
        # Draw 3D sphere
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, self.radius, 32, 32)
        gluDeleteQuadric(quadric)
        
        glPopMatrix()

# Room to contain the ball
class Room:
    def __init__(self, size=(10, 10, 10)):
        self.size = size
        self.bounds = [(-size[0]/2, size[0]/2), 
                       (-size[1]/2, size[1]/2), 
                       (-size[2]/2, size[2]/2)]
    
    def draw(self):
        glDisable(GL_LIGHTING)  # Disable lighting for wireframe
        
        glBegin(GL_LINES)
        # Draw the edges of the room (a wireframe cube)
        glColor3f(0.5, 0.5, 0.5)
        
        # Bottom face
        x_min, x_max = self.bounds[0]
        y_min, y_max = self.bounds[1]
        z_min, z_max = self.bounds[2]
        
        # Bottom face lines
        glVertex3f(x_min, y_min, z_min); glVertex3f(x_max, y_min, z_min)
        glVertex3f(x_max, y_min, z_min); glVertex3f(x_max, y_min, z_max)
        glVertex3f(x_max, y_min, z_max); glVertex3f(x_min, y_min, z_max)
        glVertex3f(x_min, y_min, z_max); glVertex3f(x_min, y_min, z_min)
        
        # Top face lines
        glVertex3f(x_min, y_max, z_min); glVertex3f(x_max, y_max, z_min)
        glVertex3f(x_max, y_max, z_min); glVertex3f(x_max, y_max, z_max)
        glVertex3f(x_max, y_max, z_max); glVertex3f(x_min, y_max, z_max)
        glVertex3f(x_min, y_max, z_max); glVertex3f(x_min, y_max, z_min)
        
        # Connecting lines
        glVertex3f(x_min, y_min, z_min); glVertex3f(x_min, y_max, z_min)
        glVertex3f(x_max, y_min, z_min); glVertex3f(x_max, y_max, z_min)
        glVertex3f(x_max, y_min, z_max); glVertex3f(x_max, y_max, z_max)
        glVertex3f(x_min, y_min, z_max); glVertex3f(x_min, y_max, z_max)
        
        glEnd()
        
        # Draw semi-transparent floor
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glBegin(GL_QUADS)
        glColor4f(0.2, 0.2, 0.2, 0.3)  # Gray with alpha
        
        # Floor
        glVertex3f(x_min, y_min, z_min)
        glVertex3f(x_max, y_min, z_min)
        glVertex3f(x_max, y_min, z_max)
        glVertex3f(x_min, y_min, z_max)
        
        glEnd()
        glDisable(GL_BLEND)
        
        glEnable(GL_LIGHTING)  # Re-enable lighting after drawing wireframe

# Game class to manage the overall simulation
class Game:
    def __init__(self):
        # Initialize PyGame
        pygame.init()
        self.width, self.height = 800, 600
        self.display = pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption('3D Bouncing Ball Simulation')
        
        # Set up the camera/perspective
        gluPerspective(45, (self.width / self.height), 0.1, 50.0)
        glTranslatef(0.0, 0.0, -20)  # Move the scene away from the camera
        
        # Enable depth testing for proper 3D rendering
        glEnable(GL_DEPTH_TEST)
        
        # Set up lighting
        self.setup_lighting()
        
        # Create the room
        self.room = Room(size=(10, 10, 10))
        
        # Create balls with random positions and velocities
        self.balls = []
        for _ in range(5):
            position = [random.uniform(-4, 4) for _ in range(3)]
            velocity = [random.uniform(-5, 5), random.uniform(0, 5), random.uniform(-5, 5)]
            color = (random.uniform(0.3, 1.0), random.uniform(0.3, 1.0), random.uniform(0.3, 1.0))
            self.balls.append(Ball(position=position, velocity=velocity, radius=0.5, color=color))
        
        # Camera rotation variables
        self.camera_rot_x = 0
        self.camera_rot_y = 0
        self.last_mouse_pos = None
        self.mouse_sensitivity = 0.5
        
        # Interactive controls
        self.selected_ball = None
        self.ball_force = 10.0  # Force to apply when launching a ball
        self.show_trails = True  # Toggle for ball trails
        
        # Game timing
        self.clock = pygame.time.Clock()
        self.running = True
        
    def setup_lighting(self):
        # Enable lighting
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_NORMALIZE)  # Normalize normals for proper lighting
        
        # Set light position (positioned above and to the side)
        light_position = (5.0, 10.0, 5.0, 1.0)
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        
        # Set ambient light (dim)
        ambient_light = (0.2, 0.2, 0.2, 1.0)
        glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_light)
        
        # Set diffuse light (main illumination)
        diffuse_light = (1.0, 1.0, 1.0, 1.0)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light)
        
        # Set specular light (highlights)
        specular_light = (1.0, 1.0, 1.0, 1.0)
        glLightfv(GL_LIGHT0, GL_SPECULAR, specular_light)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.last_mouse_pos = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    self.last_mouse_pos = None
            elif event.type == pygame.MOUSEMOTION:
                if self.last_mouse_pos:
                    x, y = pygame.mouse.get_pos()
                    dx = x - self.last_mouse_pos[0]
                    dy = y - self.last_mouse_pos[1]
                    self.camera_rot_y += dx * self.mouse_sensitivity
                    self.camera_rot_x += dy * self.mouse_sensitivity
                    self.last_mouse_pos = (x, y)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Add a new ball from camera position
                    # Calculate direction vector based on camera rotation
                    angle_x_rad = math.radians(self.camera_rot_x)
                    angle_y_rad = math.radians(self.camera_rot_y)
                    dir_x = math.sin(angle_y_rad) * math.cos(angle_x_rad)
                    dir_y = -math.sin(angle_x_rad)
                    dir_z = -math.cos(angle_y_rad) * math.cos(angle_x_rad)
                    
                    # Position the ball slightly in front of the camera
                    pos_x = dir_x * 5
                    pos_y = dir_y * 5
                    pos_z = dir_z * 5
                    
                    # Launch the ball in the direction we're looking
                    vel_x = dir_x * self.ball_force
                    vel_y = dir_y * self.ball_force
                    vel_z = dir_z * self.ball_force
                    
                    color = (random.uniform(0.3, 1.0), random.uniform(0.3, 1.0), random.uniform(0.3, 1.0))
                    self.balls.append(Ball(position=(pos_x, pos_y, pos_z), 
                                          velocity=(vel_x, vel_y, vel_z), 
                                          radius=0.5, color=color))
                elif event.key == pygame.K_r:
                    # Reset camera view
                    self.camera_rot_x = 0
                    self.camera_rot_y = 0
                elif event.key == pygame.K_c:
                    # Clear all balls
                    self.balls.clear()
                elif event.key == pygame.K_UP:
                    # Increase ball launch force
                    self.ball_force += 2.0
                elif event.key == pygame.K_DOWN:
                    # Decrease ball launch force
                    self.ball_force = max(2.0, self.ball_force - 2.0)
                elif event.key == pygame.K_t:
                    # Toggle trails
                    self.show_trails = not self.show_trails
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        # Set frame rate and calculate time delta
        delta_time = self.clock.tick(60) / 1000.0  # Time in seconds since last frame
        
        # Update all balls
        for ball in self.balls:
            ball.update(delta_time, self.room.bounds)
            
        # FPS is calculated in the rendering step
        pass
    
    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Reset the modelview matrix
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -20)
        
        # Apply camera rotation
        glRotatef(self.camera_rot_x, 1, 0, 0)
        glRotatef(self.camera_rot_y, 0, 1, 0)
        
        # Update light position to keep it relative to the camera
        light_position = (5.0, 10.0, 5.0, 1.0)
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        
        # Draw the room
        self.room.draw()
        
        # Draw all balls
        for ball in self.balls:
            ball.draw(self.show_trails)
        
        # Draw help text
        self.render_hud()
        
        pygame.display.flip()
        
    def render_hud(self):
        # Disable 3D features temporarily
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # Set up ortho projection for 2D text
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Draw a semi-transparent background for the text
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0, 0, 0, 0.5)
        
        glBegin(GL_QUADS)
        glVertex2f(10, 10)
        glVertex2f(350, 10)
        glVertex2f(350, 130)
        glVertex2f(10, 130)
        glEnd()
        
        # Update window caption with controls info
        fps = self.clock.get_fps()
        pygame.display.set_caption(f'3D Ball - FPS: {fps:.1f} - Balls: {len(self.balls)} - SPACE: Launch (Force: {self.ball_force:.1f}) - UP/DOWN: Force - R: Reset View - C: Clear - ESC: Exit')
        
        # Restore the 3D state
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
        
        pygame.quit()

# Main entry point
if __name__ == "__main__":
    try:
        game = Game()
        print("3D Ball Physics Simulation")
        print("Controls:")
        print("  - Left Mouse: Rotate camera")
        print("  - SPACE: Launch a ball")
        print("  - UP/DOWN: Adjust launch force")
        print("  - R: Reset camera view")
        print("  - C: Clear all balls")
        print("  - T: Toggle ball trails")
        print("  - ESC: Exit")
        game.run()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        pygame.quit()
import pygame
import random
import math
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants and Configuration
class GameConfig:
    """Configuration class to bundle all game settings"""
    WIDTH = 800
    HEIGHT = 600
    FPS = 60
    MAX_OBJECTS = 15
    PHYSICS_DAMPING = 0.98
    GRAVITY = 0.3
    
    # Color schemes
    COLORS = {
        'background': (20, 25, 40),
        'border': (100, 150, 200),
        'menu_bg': (40, 45, 60),
        'text': (255, 255, 255),
        'accent': (100, 200, 255)
    }

class ObjectType(Enum):
    """Enumeration for different object types"""
    SQUARE = "square"
    CIRCLE = "circle"
    TRIANGLE = "triangle"
    HEXAGON = "hexagon"

@dataclass
class Vector2D:
    """Data structure to represent 2D vectors for position and velocity"""
    x: float
    y: float
    
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)
    
    def normalize(self):
        mag = self.magnitude()
        if mag > 0:
            return Vector2D(self.x / mag, self.y / mag)
        return Vector2D(0, 0)

class PhysicsBody:
    """Advanced physics component for realistic movement"""
    def __init__(self, position: Vector2D, velocity: Vector2D, mass: float = 1.0):
        self.position = position
        self.velocity = velocity
        self.acceleration = Vector2D(0, 0)
        self.mass = mass
        self.bounce_factor = random.uniform(0.7, 0.9)
        
    def apply_force(self, force: Vector2D):
        """Apply force based on F = ma"""
        self.acceleration = self.acceleration + Vector2D(force.x / self.mass, force.y / self.mass)
    
    def update(self, dt: float):
        """Update physics using Verlet integration"""
        self.velocity = self.velocity + self.acceleration * dt
        self.velocity = self.velocity * GameConfig.PHYSICS_DAMPING
        self.position = self.position + self.velocity * dt
        self.acceleration = Vector2D(0, 0)

class ParticleEffect:
    """Particle system for visual effects"""
    def __init__(self, position: Vector2D, color: Tuple[int, int, int]):
        self.particles = []
        for _ in range(random.randint(3, 8)):
            particle = {
                'pos': Vector2D(position.x, position.y),
                'vel': Vector2D(random.uniform(-3, 3), random.uniform(-3, 3)),
                'life': random.uniform(0.5, 1.5),
                'color': color,
                'size': random.randint(2, 5)
            }
            self.particles.append(particle)
    
    def update(self, dt: float):
        """Update particle positions and lifetimes"""
        self.particles = [p for p in self.particles if p['life'] > 0]
        for particle in self.particles:
            particle['pos'] = particle['pos'] + particle['vel'] * dt
            particle['vel'] = particle['vel'] * 0.95
            particle['life'] -= dt
            particle['size'] = max(1, int(particle['size'] * 0.98))
    
    def draw(self, screen):
        """Render particles with fading effect"""
        for particle in self.particles:
            alpha = max(0, min(255, int(particle['life'] * 255)))
            color = (*particle['color'], alpha)
            try:
                pygame.draw.circle(screen, particle['color'], 
                                 (int(particle['pos'].x), int(particle['pos'].y)), 
                                 particle['size'])
            except:
                pass

class GameObject:
    """Enhanced base class for all game objects using composition"""
    def __init__(self, obj_type: ObjectType, position: Vector2D):
        self.obj_type = obj_type
        self.physics = PhysicsBody(position, Vector2D(
            random.uniform(-6, 6), random.uniform(-6, 6)
        ))
        self.size = random.uniform(15, 45)
        self.color = self._generate_color()
        self.trail_positions = []
        self.collision_count = 0
        self.creation_time = pygame.time.get_ticks()
        
    def _generate_color(self) -> Tuple[int, int, int]:
        """Generate vibrant colors using HSV conversion"""
        hue = random.uniform(0, 360)
        saturation = random.uniform(0.6, 1.0)
        value = random.uniform(0.7, 1.0)
        
        # Convert HSV to RGB
        c = value * saturation
        x = c * (1 - abs((hue / 60) % 2 - 1))
        m = value - c
        
        if hue < 60:
            r, g, b = c, x, 0
        elif hue < 120:
            r, g, b = x, c, 0
        elif hue < 180:
            r, g, b = 0, c, x
        elif hue < 240:
            r, g, b = 0, x, c
        elif hue < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
            
        return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))
    
    def check_boundaries(self, width: int, height: int) -> bool:
        """Enhanced boundary collision with realistic physics"""
        collided = False
        
        # Left/Right boundaries
        if self.physics.position.x - self.size/2 <= 0:
            self.physics.position.x = self.size/2
            self.physics.velocity.x = abs(self.physics.velocity.x) * self.physics.bounce_factor
            collided = True
        elif self.physics.position.x + self.size/2 >= width:
            self.physics.position.x = width - self.size/2
            self.physics.velocity.x = -abs(self.physics.velocity.x) * self.physics.bounce_factor
            collided = True
            
        # Top/Bottom boundaries  
        if self.physics.position.y - self.size/2 <= 0:
            self.physics.position.y = self.size/2
            self.physics.velocity.y = abs(self.physics.velocity.y) * self.physics.bounce_factor
            collided = True
        elif self.physics.position.y + self.size/2 >= height:
            self.physics.position.y = height - self.size/2
            self.physics.velocity.y = -abs(self.physics.velocity.y) * self.physics.bounce_factor
            collided = True
            
        if collided:
            self.collision_count += 1
            self.color = self._generate_color()
            
        return collided
    
    def update(self, dt: float, width: int, height: int, particle_effects: List[ParticleEffect]):
        """Update object with enhanced physics and effects"""
        # Apply gravity
        self.physics.apply_force(Vector2D(0, GameConfig.GRAVITY * self.physics.mass))
        
        # Update physics
        self.physics.update(dt)
        
        # Check collisions and create effects
        if self.check_boundaries(width, height):
            effect = ParticleEffect(self.physics.position, self.color)
            particle_effects.append(effect)
        
        # Update trail
        self.trail_positions.append((self.physics.position.x, self.physics.position.y))
        if len(self.trail_positions) > 8:
            self.trail_positions.pop(0)
    
    def draw(self, screen):
        """Enhanced rendering with trails and effects"""
        # Draw trail
        if len(self.trail_positions) > 1:
            for i, pos in enumerate(self.trail_positions[:-1]):
                alpha = int(255 * (i / len(self.trail_positions)) * 0.3)
                trail_color = (*self.color, alpha)
                try:
                    pygame.draw.circle(screen, self.color, 
                                     (int(pos[0]), int(pos[1])), 
                                     int(self.size/4 * (i / len(self.trail_positions))))
                except:
                    pass
        
        # Draw main object
        pos = (int(self.physics.position.x), int(self.physics.position.y))
        
        if self.obj_type == ObjectType.SQUARE:
            rect = pygame.Rect(pos[0] - self.size/2, pos[1] - self.size/2, 
                             self.size, self.size)
            pygame.draw.rect(screen, self.color, rect)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)
            
        elif self.obj_type == ObjectType.CIRCLE:
            pygame.draw.circle(screen, self.color, pos, int(self.size/2))
            pygame.draw.circle(screen, (255, 255, 255), pos, int(self.size/2), 2)
            
        elif self.obj_type == ObjectType.TRIANGLE:
            points = [
                (pos[0], pos[1] - self.size/2),
                (pos[0] - self.size/2, pos[1] + self.size/2),
                (pos[0] + self.size/2, pos[1] + self.size/2)
            ]
            pygame.draw.polygon(screen, self.color, points)
            pygame.draw.polygon(screen, (255, 255, 255), points, 2)
            
        elif self.obj_type == ObjectType.HEXAGON:
            points = []
            for i in range(6):
                angle = i * math.pi / 3
                x = pos[0] + (self.size/2) * math.cos(angle)
                y = pos[1] + (self.size/2) * math.sin(angle)
                points.append((x, y))
            pygame.draw.polygon(screen, self.color, points)
            pygame.draw.polygon(screen, (255, 255, 255), points, 2)

class GameStats:
    """Data structure to track game statistics"""
    def __init__(self):
        self.objects_created = 0
        self.total_collisions = 0
        self.game_time = 0
        self.object_type_counts = {obj_type: 0 for obj_type in ObjectType}
    
    def update(self, objects: List[GameObject], dt: float):
        self.game_time += dt
        self.total_collisions = sum(obj.collision_count for obj in objects)
        
        # Reset counts and recalculate
        for obj_type in ObjectType:
            self.object_type_counts[obj_type] = 0
        
        for obj in objects:
            self.object_type_counts[obj.obj_type] += 1

class Menu:
    """Enhanced menu system with better organization"""
    def __init__(self, screen_width: int, screen_height: int):
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.width = screen_width
        self.height = screen_height
        
        self.menu_options = [
            ("1 - Square", ObjectType.SQUARE),
            ("2 - Circle", ObjectType.CIRCLE), 
            ("3 - Triangle", ObjectType.TRIANGLE),
            ("4 - Hexagon", ObjectType.HEXAGON),
            ("C - Clear All", None),
            ("ESC - Exit", None)
        ]
    
    def draw(self, screen, stats: GameStats, object_count: int):
        """Draw enhanced menu with statistics"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill(GameConfig.COLORS['menu_bg'])
        screen.blit(overlay, (0, 0))
        
        # Title
        title = self.font_large.render("ADVANCED BOUNCING SIMULATION", True, 
                                     GameConfig.COLORS['accent'])
        title_rect = title.get_rect(center=(self.width//2, 80))
        screen.blit(title, title_rect)
        
        # Menu options
        y_start = 150
        for i, (text, _) in enumerate(self.menu_options):
            color = GameConfig.COLORS['accent'] if i < 4 else GameConfig.COLORS['text']
            option_text = self.font_medium.render(text, True, color)
            option_rect = option_text.get_rect(center=(self.width//2, y_start + i * 40))
            screen.blit(option_text, option_rect)
        
        # Statistics panel
        stats_y = 400
        stats_texts = [
            f"Active Objects: {object_count}/{GameConfig.MAX_OBJECTS}",
            f"Total Created: {stats.objects_created}",
            f"Total Collisions: {stats.total_collisions}",
            f"Game Time: {stats.game_time:.1f}s"
        ]
        
        for i, text in enumerate(stats_texts):
            stats_surface = self.font_small.render(text, True, GameConfig.COLORS['text'])
            stats_rect = stats_surface.get_rect(center=(self.width//2, stats_y + i * 25))
            screen.blit(stats_surface, stats_rect)

class BouncingSimulation:
    """Main game class using composition and advanced techniques"""
    def __init__(self):
        self.screen = pygame.display.set_mode((GameConfig.WIDTH, GameConfig.HEIGHT))
        pygame.display.set_caption("Advanced Bouncing Ball Simulation")
        self.clock = pygame.time.Clock()
        
        # Game state using data structures
        self.objects: List[GameObject] = []
        self.particle_effects: List[ParticleEffect] = []
        self.stats = GameStats()
        self.menu = Menu(GameConfig.WIDTH, GameConfig.HEIGHT)
        
        self.running = True
        self.show_menu = True
        self.last_time = pygame.time.get_ticks()
    
    def spawn_object(self, obj_type: ObjectType):
        """Factory method to create objects with validation"""
        if len(self.objects) >= GameConfig.MAX_OBJECTS:
            return False
            
        position = Vector2D(
            random.uniform(50, GameConfig.WIDTH - 50),
            random.uniform(50, GameConfig.HEIGHT - 50)
        )
        
        new_object = GameObject(obj_type, position)
        self.objects.append(new_object)
        self.stats.objects_created += 1
        return True
    
    def clear_objects(self):
        """Clear all objects and reset statistics"""
        self.objects.clear()
        self.particle_effects.clear()
    
    def handle_events(self):
        """Enhanced event handling with better organization"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.show_menu:
                        self.running = False
                    else:
                        self.show_menu = True
                        
                elif self.show_menu:
                    # Menu navigation
                    key_mapping = {
                        pygame.K_1: ObjectType.SQUARE,
                        pygame.K_2: ObjectType.CIRCLE,
                        pygame.K_3: ObjectType.TRIANGLE,
                        pygame.K_4: ObjectType.HEXAGON
                    }
                    
                    if event.key in key_mapping:
                        if self.spawn_object(key_mapping[event.key]):
                            self.show_menu = False
                    elif event.key == pygame.K_c:
                        self.clear_objects()
                        
                else:
                    # In-game controls
                    if event.key == pygame.K_m:
                        self.show_menu = True
                    elif event.key == pygame.K_SPACE:
                        # Spawn random object
                        obj_type = random.choice(list(ObjectType))
                        self.spawn_object(obj_type)
    
    def update_simulation(self, dt: float):
        """Update all game objects and systems"""
        if not self.show_menu:
            # Update objects
            for obj in self.objects:
                obj.update(dt, GameConfig.WIDTH, GameConfig.HEIGHT, self.particle_effects)
            
            # Update particle effects
            self.particle_effects = [effect for effect in self.particle_effects if effect.particles]
            for effect in self.particle_effects:
                effect.update(dt)
            
            # Update statistics
            self.stats.update(self.objects, dt)
    
    def render(self):
        """Enhanced rendering with visual improvements"""
        # Clear screen with gradient-like effect
        self.screen.fill(GameConfig.COLORS['background'])
        
        # Draw border
        pygame.draw.rect(self.screen, GameConfig.COLORS['border'], 
                        (0, 0, GameConfig.WIDTH, GameConfig.HEIGHT), 3)
        
        if not self.show_menu:
            # Draw particle effects first (background layer)
            for effect in self.particle_effects:
                effect.draw(self.screen)
            
            # Draw all objects
            for obj in self.objects:
                obj.draw(self.screen)
            
            # Draw HUD
            self.draw_hud()
        else:
            # Draw menu
            self.menu.draw(self.screen, self.stats, len(self.objects))
        
        pygame.display.flip()
    
    def draw_hud(self):
        """Draw heads-up display with game information"""
        font = pygame.font.Font(None, 28)
        
        hud_info = [
            f"Objects: {len(self.objects)}/{GameConfig.MAX_OBJECTS}",
            f"Collisions: {self.stats.total_collisions}",
            f"Time: {self.stats.game_time:.1f}s",
            "SPACE: Random | M: Menu"
        ]
        
        for i, text in enumerate(hud_info):
            surface = font.render(text, True, GameConfig.COLORS['text'])
            self.screen.blit(surface, (10, 10 + i * 25))
    
    def run(self):
        """Main game loop with proper timing"""
        while self.running:
            current_time = pygame.time.get_ticks()
            dt = (current_time - self.last_time) / 1000.0
            self.last_time = current_time
            
            self.handle_events()
            self.update_simulation(dt)
            self.render()
            
            self.clock.tick(GameConfig.FPS)
        
        pygame.quit()

# Recursive function for generating fractal-like patterns (bonus feature)
def generate_spiral_positions(center: Vector2D, count: int, radius: float = 50, depth: int = 0) -> List[Vector2D]:
    """Recursively generate spiral positions for object placement"""
    if count <= 0 or depth > 3:
        return []
    
    positions = []
    angle_step = 2 * math.pi / count
    
    for i in range(count):
        angle = i * angle_step
        x = center.x + radius * math.cos(angle)
        y = center.y + radius * math.sin(angle)
        positions.append(Vector2D(x, y))
        
        # Recursive call for smaller spirals
        if depth < 2 and count > 2:
            sub_positions = generate_spiral_positions(
                Vector2D(x, y), 
                max(1, count // 2), 
                radius * 0.6, 
                depth + 1
            )
            positions.extend(sub_positions)
    
    return positions

if __name__ == "__main__":
    # Initialize and run the enhanced simulation
    simulation = BouncingSimulation()
    simulation.run()
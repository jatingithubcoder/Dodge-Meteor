import pygame
import random
import math

# --- PYGAME INITIALIZATION ---
pygame.init()

# --- CONSTANTS ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = "Cosmic Dodger"
CAPTION = "Dodge the Meteors!"
FONT_NAME = 'Arial'

# Colors
WHITE = (255, 255, 255)
BLACK = (10, 10, 10)
RED = (200, 50, 50)
BLUE = (50, 50, 200)
YELLOW = (255, 200, 0)
DARK_GREY = (30, 30, 30)

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()
FPS = 60

# --- HELPER FUNCTIONS ---

def draw_text(surface, text, size, x, y, color=WHITE):
    """Draws text on the screen."""
    try:
        font = pygame.font.SysFont(FONT_NAME, size, bold=True)
    except:
        font = pygame.font.Font(None, size) # Fallback if system font fails

    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

def draw_gradient_background(surface):
    """Draws a simple dark space gradient."""
    for i in range(SCREEN_HEIGHT):
        # Interpolate color from very dark blue to black
        color = (
            int(10 + (30 - 10) * (i / SCREEN_HEIGHT)),
            int(10 + (30 - 10) * (i / SCREEN_HEIGHT)),
            int(40 + (10 - 40) * (i / SCREEN_HEIGHT))
        )
        pygame.draw.line(surface, color, (0, i), (SCREEN_WIDTH, i))

# --- GAME OBJECTS ---

class Player(pygame.sprite.Sprite):
    """The player's spaceship."""
    def __init__(self):
        super().__init__()
        # Create a simple triangle ship using Pygame's Surface
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0)) # Fully transparent background

        # Draw the ship shape (triangle pointing up)
        points = [
            (25, 0),        # Top tip
            (50, 40),       # Bottom right
            (0, 40)         # Bottom left
        ]
        pygame.draw.polygon(self.image, BLUE, points)
        pygame.draw.polygon(self.image, WHITE, points, 2) # Outline

        # Draw a small engine glow
        pygame.draw.circle(self.image, RED, (25, 45), 8)
        pygame.draw.circle(self.image, YELLOW, (25, 45), 4)

        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed = 8
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()

    def update(self):
        # Handle movement based on keyboard input
        self.speed = 8 + (game_state.score // 100) * 0.5 # Speed up player as score increases
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed

        # Keep player within screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        # If hidden, make player visible after 1 second
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = SCREEN_WIDTH // 2
            self.rect.bottom = SCREEN_HEIGHT - 20

    def hide(self):
        """Hides the player temporarily after a hit."""
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (-100, -100) # Move off-screen

class Meteor(pygame.sprite.Sprite):
    """A falling hostile meteor/rock."""
    def __init__(self):
        super().__init__()
        self.size = random.randint(20, 50)
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0)) # Transparent
        
        # Draw a rocky circle shape
        color = (100, 100, 100) # Grey rock
        pygame.draw.circle(self.image, color, (self.size // 2, self.size // 2), self.size // 2)
        
        # Add rock details
        pygame.draw.circle(self.image, DARK_GREY, (self.size // 4, self.size // 4), self.size // 8)
        pygame.draw.circle(self.image, DARK_GREY, (self.size * 3 // 4, self.size * 3 // 4), self.size // 10)
        
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, SCREEN_WIDTH - self.size)
        self.rect.y = random.randrange(-100, -40) # Start above the screen
        
        # Base speed increases with game score
        base_speed = random.uniform(3, 6)
        score_multiplier = 1 + (game_state.score // 100) * 0.1
        self.speedy = base_speed * score_multiplier

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > SCREEN_HEIGHT:
            self.kill() # Remove if off screen

# --- GAME STATE MANAGER ---

class GameState:
    """Manages the overall state of the game."""
    def __init__(self):
        self.running = True
        self.is_playing = False
        self.show_menu = True
        self.score = 0
        self.high_score = 0
        self.last_meteor_spawn = pygame.time.get_ticks()

    def reset_game(self):
        """Resets variables for a new game."""
        self.score = 0
        self.is_playing = True
        self.show_menu = False
        self.last_meteor_spawn = pygame.time.get_ticks()

        # Clear existing sprites and create new ones
        all_sprites.empty()
        meteors.empty()

        self.player = Player()
        all_sprites.add(self.player)

    def update_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score

    def handle_collisions(self):
        hits = pygame.sprite.spritecollide(self.player, meteors, True, pygame.sprite.collide_mask)
        if hits and not self.player.hidden:
            self.player.lives -= 1
            if self.player.lives > 0:
                self.player.hide()
            else:
                self.is_playing = False
                self.show_menu = True
                self.update_high_score()

    def spawn_meteors(self):
        now = pygame.time.get_ticks()
        # Spawn rate gets faster as score increases
        spawn_delay = max(200, 1000 - self.score)
        
        if now - self.last_meteor_spawn > spawn_delay:
            self.last_meteor_spawn = now
            new_meteor = Meteor()
            all_sprites.add(new_meteor)
            meteors.add(new_meteor)

# --- GAME SCENES ---

def draw_score_and_lives(surface, player):
    """Draws current score and player lives on the screen."""
    draw_text(surface, f"Score: {game_state.score}", 24, SCREEN_WIDTH // 2, 10)
    
    # Draw lives visually
    x = 10
    y = 10
    ship_icon = pygame.Surface((20, 15), pygame.SRCALPHA)
    points = [(10, 0), (20, 15), (0, 15)]
    pygame.draw.polygon(ship_icon, BLUE, points)
    
    for i in range(player.lives):
        surface.blit(ship_icon, (x + i * 30, y))

def main_menu():
    """The start and game over menu screen."""
    
    # Simple starfield effect for the menu
    stars = []
    for _ in range(100):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        size = random.randint(1, 3)
        stars.append({'x': x, 'y': y, 'size': size})

    while game_state.show_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state.running = False
                game_state.show_menu = False
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                game_state.reset_game()
                return # Exit menu loop and start game

        # --- Drawing ---
        draw_gradient_background(screen)
        
        # Draw stars
        for star in stars:
            pygame.draw.circle(screen, WHITE, (star['x'], star['y']), star['size'])
            
        # Title and Instructions
        draw_text(screen, TITLE, 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, YELLOW)
        draw_text(screen, CAPTION, 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 70, WHITE)

        draw_text(screen, "Use Arrow Keys or A/D to Move", 28, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, WHITE)
        draw_text(screen, "Press SPACE to START", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, BLUE)

        # Game Over state display
        if game_state.score > 0:
            draw_text(screen, f"FINAL SCORE: {game_state.score}", 48, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120, RED)
            draw_text(screen, f"HIGH SCORE: {game_state.high_score}", 32, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100, YELLOW)

        pygame.display.flip()
        clock.tick(15) # Menu runs slower

# --- MAIN GAME LOOP ---

# Initialize Game State and Sprite Groups
game_state = GameState()
all_sprites = pygame.sprite.Group()
meteors = pygame.sprite.Group()

while game_state.running:
    # 1. Handle Menu
    if game_state.show_menu:
        main_menu()

    # 2. Handle Game Play
    if game_state.is_playing:
        
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state.running = False

        # --- Update ---
        game_state.spawn_meteors()
        all_sprites.update()
        game_state.handle_collisions()
        game_state.score += 1 # Score increases every frame

        # --- Draw ---
        draw_gradient_background(screen)
        
        # Draw all sprites
        all_sprites.draw(screen)
        
        # Draw UI
        draw_score_and_lives(screen, game_state.player)

        # Update the full display
        pygame.display.flip()
        
        # Cap the framerate
        clock.tick(FPS)

# --- CLEAN UP ---
pygame.quit()
print("Game Closed. Final High Score:", game_state.high_score)

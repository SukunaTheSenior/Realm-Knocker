import pygame
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Tabby's Parkour Adventure")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

# Game states
MENU = 0
PLAYING = 1
VICTORY = 2
game_state = MENU
fullscreen = False

# Load images (replace with your actual image files)
try:
    player_img = pygame.image.load("tabby.png")
    player_img = pygame.transform.scale(player_img, (50, 50))
    goal_img = pygame.image.load("brawlstars.png")
    goal_img = pygame.transform.scale(goal_img, (80, 80))
except:
    # Create placeholder images if files not found
    player_img = pygame.Surface((50, 50))
    player_img.fill(BLUE)
    goal_img = pygame.Surface((80, 80))
    goal_img.fill((255, 0, 0))  # Red square as placeholder

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        
        font = pygame.font.SysFont(None, 36)
        text_surf = font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = SCREEN_HEIGHT - 100
        self.velocity_y = 0
        self.jumping = False
        self.speed = 5
        
    def update(self):
        # Gravity
        self.velocity_y += 0.5
        if self.velocity_y > 10:
            self.velocity_y = 10
        self.rect.y += self.velocity_y
        
        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.jumping = False
            self.velocity_y = 0
            
    def jump(self):
        if not self.jumping:
            self.velocity_y = -12
            self.jumping = True
            
    def move_left(self):
        self.rect.x -= self.speed
        
    def move_right(self):
        self.rect.x += self.speed

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(DARK_GRAY)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Goal class
class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = goal_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def create_game_objects():
    global all_sprites, platforms, player, goal
    
    # Create sprite groups
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()

    # Create player
    player = Player()
    all_sprites.add(player)

    # Create platforms (simple parkour course)
    platform_list = [
        (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40),  # Ground
        (100, SCREEN_HEIGHT - 150, 200, 20),
        (350, SCREEN_HEIGHT - 250, 200, 20),
        (200, SCREEN_HEIGHT - 350, 150, 20),
        (500, SCREEN_HEIGHT - 450, 200, 20),
    ]

    for plat in platform_list:
        p = Platform(*plat)
        all_sprites.add(p)
        platforms.add(p)

    # Create goal (positioned at the end of the parkour)
    goal = Goal(650, SCREEN_HEIGHT - 530)
    all_sprites.add(goal)

def toggle_fullscreen():
    global fullscreen, screen, SCREEN_WIDTH, SCREEN_HEIGHT
    fullscreen = not fullscreen
    if fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    else:
        screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
        SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    create_game_objects()  # Recreate objects to fit new screen size

# Create buttons
start_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 30, 200, 50, "Start", GRAY, (150, 255, 150))
quit_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 40, 200, 50, "Quit", GRAY, (255, 150, 150))
fullscreen_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 110, 200, 50, "Fullscreen", GRAY, (150, 150, 255))

# Create game objects
create_game_objects()

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    mouse_pos = pygame.mouse.get_pos()
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if game_state == MENU:
            start_button.check_hover(mouse_pos)
            quit_button.check_hover(mouse_pos)
            fullscreen_button.check_hover(mouse_pos)
            
            if start_button.is_clicked(mouse_pos, event):
                game_state = PLAYING
            if quit_button.is_clicked(mouse_pos, event):
                running = False
            if fullscreen_button.is_clicked(mouse_pos, event):
                toggle_fullscreen()
                
        elif game_state == PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                if event.key == pygame.K_f:
                    toggle_fullscreen()
                    
        elif game_state == VICTORY:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Reset game
                    create_game_objects()
                    game_state = PLAYING
                if event.key == pygame.K_m:
                    game_state = MENU
                if event.key == pygame.K_f:
                    toggle_fullscreen()
    
    # Game logic
    if game_state == PLAYING:
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            player.move_left()
        if keys[pygame.K_d]:
            player.move_right()
        
        # Update
        player.update()
        
        # Check for platform collisions
        if player.velocity_y > 0:  # Only check when falling
            platform_hits = pygame.sprite.spritecollide(player, platforms, False)
            if platform_hits:
                player.rect.bottom = platform_hits[0].rect.top
                player.velocity_y = 0
                player.jumping = False
        
        # Check for goal collision
        if pygame.sprite.collide_rect(player, goal):
            game_state = VICTORY
    
    # Drawing
    screen.fill(WHITE)
    
    if game_state == MENU:
        # Draw menu
        title_font = pygame.font.SysFont(None, 72)
        title = title_font.render("Tabby's Adventure", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        screen.blit(title, title_rect)
        
        start_button.draw(screen)
        quit_button.draw(screen)
        fullscreen_button.draw(screen)
        
    elif game_state == PLAYING:
        # Draw game
        all_sprites.draw(screen)
        
    elif game_state == VICTORY:
        # Victory screen
        screen.fill(GREEN)
        font = pygame.font.SysFont(None, 64)
        text = font.render("You're tabby approved!", True, BLACK)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        screen.blit(text, text_rect)
        
        # Restart instructions
        small_font = pygame.font.SysFont(None, 36)
        restart_text = small_font.render("Press R to restart", True, BLACK)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        screen.blit(restart_text, restart_rect)
        
        menu_text = small_font.render("Press M for menu", True, BLACK)
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
        screen.blit(menu_text, menu_rect)
        
        full_text = small_font.render("Press F to toggle fullscreen", True, BLACK)
        full_rect = full_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 150))
        screen.blit(full_text, full_rect)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
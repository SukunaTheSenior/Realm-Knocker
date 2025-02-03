import pyglet
from pyglet.window import key, mouse
import random

# Window setup
window = pyglet.window.Window(800, 600, caption="Realm Knocker RGB", resizable=True)
batch = pyglet.graphics.Batch()
fps_display = pyglet.window.FPSDisplay(window)
fps_display.label.color = (255, 255, 255, 255)  # White FPS counter

# Game states
MENU = 0
PLAYING = 1
SETTINGS = 2
CREDITS = 3
RESOLUTION = 4
game_state = MENU

# Player setup
player = pyglet.shapes.Rectangle(300, 200, 50, 50, color=(255, 255, 0), batch=batch)
player_speed = 300
dash_cooldown = 0
dash_cooldown_max = 6  # Dash cooldown in seconds

# Rock setup
rocks = []
rock_cooldown = 0
rock_cooldown_max = 3  # Player rock cooldown in seconds

# Enemy setup
enemies = []
enemy_rock_cooldown = 3  # Enemy shoots every 3 seconds
enemy_respawn_time = 5  # Respawn time after being killed

# Wall setup
walls = [
    pyglet.shapes.Rectangle(100, 100, 50, 50, color=(139, 69, 19), batch=batch),
    pyglet.shapes.Rectangle(400, 300, 50, 50, color=(139, 69, 19), batch=batch),
]

# Key states
keys = key.KeyStateHandler()
window.push_handlers(keys)

# Mouse position
mouse_x, mouse_y = 0, 0

# System resolution
screen = window.display.get_default_screen()
SYSTEM_WIDTH = screen.width
SYSTEM_HEIGHT = screen.height

# Helper functions
def check_collision(rect1, rect2):
    return (
        rect1.x < rect2.x + rect2.width and
        rect1.x + rect1.width > rect2.x and
        rect1.y < rect2.y + rect2.height and
        rect1.y + rect1.height > rect2.y
    )

def distance(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

# Enemy class
class Enemy:
    def __init__(self, x, y):
        self.shape = pyglet.shapes.Rectangle(x, y, 50, 50, color=(255, 0, 0), batch=batch)
        self.rock_cooldown = enemy_rock_cooldown
        self.alive = True

    def update(self, dt):
        if self.alive:
            self.rock_cooldown -= dt
            if self.rock_cooldown <= 0:
                self.shoot_rock()
                self.rock_cooldown = enemy_rock_cooldown

    def shoot_rock(self):
        dx = player.x - self.shape.x
        dy = player.y - self.shape.y
        dist = distance(self.shape.x, self.shape.y, player.x, player.y)
        if dist > 0:
            rock = Rock(self.shape.x, self.shape.y, dx / dist, dy / dist, is_enemy=True)
            rocks.append(rock)

    def respawn(self):
        self.shape.x = random.randint(0, window.width)
        self.shape.y = random.randint(0, window.height)
        self.alive = True

# Rock class
class Rock:
    def __init__(self, x, y, dx, dy, is_enemy=False):
        self.shape = pyglet.shapes.Rectangle(x, y, 10, 10, color=(165, 42, 42), batch=batch)
        self.dx = dx
        self.dy = dy
        self.is_enemy = is_enemy

    def update(self, dt):
        self.shape.x += self.dx * dt * 200
        self.shape.y += self.dy * dt * 200

        # Check collision with player (if enemy rock)
        if self.is_enemy and check_collision(self.shape, player):
            self.shape.delete()
            rocks.remove(self)
            # Handle player damage (you can add health logic here)

        # Check collision with enemies (if player rock)
        if not self.is_enemy:
            for enemy in enemies:
                if enemy.alive and check_collision(self.shape, enemy.shape):
                    self.shape.delete()
                    rocks.remove(self)
                    enemy.alive = False
                    pyglet.clock.schedule_once(lambda dt: enemy.respawn(), enemy_respawn_time)

# Update function
def update(dt):
    global rock_cooldown, dash_cooldown

    if game_state == PLAYING:
        prev_x, prev_y = player.x, player.y

        if keys[key.W]:
            player.y += player_speed * dt
        if keys[key.S]:
            player.y -= player_speed * dt
        if keys[key.A]:
            player.x -= player_speed * dt
        if keys[key.D]:
            player.x += player_speed * dt

        for wall in walls:
            if check_collision(player, wall):
                player.x, player.y = prev_x, prev_y
                break

        if dash_cooldown <= 0 and keys[key.E]:
            dash_to_cursor()
            dash_cooldown = dash_cooldown_max

        if rock_cooldown <= 0 and keys[key.Q]:
            throw_rock()
            rock_cooldown = rock_cooldown_max

        if rock_cooldown > 0:
            rock_cooldown -= dt
        if dash_cooldown > 0:
            dash_cooldown -= dt

        for rock in rocks:
            rock.update(dt)

        for enemy in enemies:
            enemy.update(dt)

def dash_to_cursor():
    global player
    dx = mouse_x - player.x
    dy = mouse_y - player.y
    dist = distance(player.x, player.y, mouse_x, mouse_y)
    if dist > 0:
        player.x += dx / dist * 100  # Dash distance
        player.y += dy / dist * 100  # Dash distance

def throw_rock():
    dx = mouse_x - player.x
    dy = mouse_y - player.y
    dist = distance(player.x, player.y, mouse_x, mouse_y)
    if dist > 0:
        rock = Rock(player.x, player.y, dx / dist, dy / dist)
        rocks.append(rock)

# Draw function
@window.event
def on_draw():
    window.clear()
    if game_state == MENU:
        draw_menu()
    elif game_state == PLAYING:
        batch.draw()
        fps_display.draw()
    elif game_state == SETTINGS:
        draw_settings()
    elif game_state == CREDITS:
        draw_credits()
    elif game_state == RESOLUTION:
        draw_resolution()

# Menu and other UI functions (unchanged)
# (You can copy the existing `draw_menu`, `draw_settings`, etc., functions here)

# Initialize enemies
for _ in range(3):  # Spawn 3 enemies
    enemy = Enemy(random.randint(0, window.width), random.randint(0, window.height))
    enemies.append(enemy)

# Schedule the update function
pyglet.clock.schedule_interval(update, 1 / 120.0)

# Run the game
pyglet.app.run()
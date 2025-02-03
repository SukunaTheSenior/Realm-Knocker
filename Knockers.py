import pyglet
from pyglet.window import key, mouse
import random
import math

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
base_speed = player_speed  # Store base speed for resetting
dash_cooldown = 0
dash_cooldown_max = 6  # Dash cooldown in seconds

# Rock setup
rocks = []
rock_cooldown = 0
rock_cooldown_max = 3  # Player rock cooldown in seconds

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

# Boost setup
boost = None
boost_spawn_cooldown = 15  # Boost spawns every 15 seconds
boost_active = False
boost_duration = 5  # Boost lasts for 5 seconds

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

# Boost class
class Boost:
    def __init__(self, x, y):
        # Triangle points: (x1, y1), (x2, y2), (x3, y3)
        self.shape = pyglet.shapes.Triangle(x, y, x + 20, y - 35, x + 40, y, color=(128, 0, 128), batch=batch)
        self.active = True

    def check_collision(self, player):
        # Approximate collision detection for triangle and rectangle
        return (
            player.x < self.shape.x2 + 20 and
            player.x + player.width > self.shape.x1 and
            player.y < self.shape.y1 and
            player.y + player.height > self.shape.y2
        )

# Rock class
class Rock:
    def __init__(self, x, y, dx, dy):
        self.shape = pyglet.shapes.Rectangle(x, y, 10, 10, color=(165, 42, 42), batch=batch)
        self.dx = dx
        self.dy = dy

    def update(self, dt):
        self.shape.x += self.dx * dt * 200
        self.shape.y += self.dy * dt * 200

        # Check collision with walls
        for wall in walls:
            if check_collision(self.shape, wall):
                self.shape.delete()
                rocks.remove(self)
                break

# Update function
def update(dt):
    global rock_cooldown, dash_cooldown, boost, boost_active, player_speed

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

        # Boost logic
        if boost and boost.active:
            if boost.check_collision(player):
                boost.shape.delete()
                boost.active = False
                boost = None
                activate_speed_boost()

        # Spawn boost
        if not boost and not boost_active:
            boost_spawn_cooldown -= dt
            if boost_spawn_cooldown <= 0:
                spawn_boost()
                boost_spawn_cooldown = 15

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

def spawn_boost():
    global boost
    # Spawn boost within a radius of the player
    angle = random.uniform(0, 2 * math.pi)
    radius = random.uniform(100, 300)  # Spawn within 100-300 pixels of the player
    x = player.x + radius * math.cos(angle)
    y = player.y + radius * math.sin(angle)
    boost = Boost(x, y)

def activate_speed_boost():
    global player_speed, boost_active
    player_speed *= 2  # Double player speed
    boost_active = True
    pyglet.clock.schedule_once(reset_speed_boost, boost_duration)

def reset_speed_boost(dt):
    global player_speed, boost_active
    player_speed = base_speed  # Reset to base speed
    boost_active = False

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

# Schedule the update function
pyglet.clock.schedule_interval(update, 1 / 120.0)

# Run the game
pyglet.app.run()
import pyglet
from pyglet.window import key
import random

# Window setup
window = pyglet.window.Window(800, 600, caption="Realm Knocker RGB")
batch = pyglet.graphics.Batch()

# Player setup
player = pyglet.shapes.Rectangle(400, 300, 50, 50, color=(0, 255, 0), batch=batch)
player_speed = 300  # Pixels per second

# Rock class
class Rock:
    def __init__(self, x, y, dx, dy):
        self.shape = pyglet.shapes.Rectangle(x, y, 10, 10, color=(165, 42, 42), batch=batch)
        self.dx = dx
        self.dy = dy

    def update(self, dt):
        self.shape.x += self.dx * dt * 200  # Rock speed
        self.shape.y += self.dy * dt * 200

# Rock setup
rocks = []
rock_cooldown = 0
rock_cooldown_max = 1  # 1 second cooldown

# Teleport setup
teleport_cooldown = 0
teleport_cooldown_max = 3  # 3 seconds cooldown

# Key states
keys = key.KeyStateHandler()
window.push_handlers(keys)

def update(dt):
    global rock_cooldown, teleport_cooldown

    # Player movement (WASD)
    if keys[key.W]:
        player.y += player_speed * dt
    if keys[key.S]:
        player.y -= player_speed * dt
    if keys[key.A]:
        player.x -= player_speed * dt
    if keys[key.D]:
        player.x += player_speed * dt

    # Rock throw (Q key)
    if keys[key.Q] and rock_cooldown <= 0:
        throw_rocks()
        rock_cooldown = rock_cooldown_max

    # Teleport jump (E key)
    if keys[key.E] and teleport_cooldown <= 0:
        teleport_jump()
        teleport_cooldown = teleport_cooldown_max

    # Update cooldowns
    if rock_cooldown > 0:
        rock_cooldown -= dt
    if teleport_cooldown > 0:
        teleport_cooldown -= dt

    # Update rocks
    for rock in rocks:
        rock.update(dt)

    # Remove off-screen rocks
    rocks[:] = [rock for rock in rocks if 0 <= rock.shape.x <= 800 and 0 <= rock.shape.y <= 600]

def throw_rocks():
    # Throw 3 rocks in an upturned triangle pattern
    directions = [(-0.5, 1), (0, 1), (0.5, 1)]  # Left-up, straight-up, right-up
    for dx, dy in directions:
        rock = Rock(player.x, player.y, dx, dy)
        rocks.append(rock)

def teleport_jump():
    # Teleport the player to a random position within a radius
    radius = 100
    player.x = random.randint(int(player.x - radius), int(player.x + radius))
    player.y = random.randint(int(player.y - radius), int(player.y + radius))

@window.event
def on_draw():
    window.clear()
    batch.draw()

# Schedule updates
pyglet.clock.schedule_interval(update, 1/60.0)

# Run the game
pyglet.app.run()
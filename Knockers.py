import pyglet
from pyglet.window import key, mouse
import random

# Window setup
window = pyglet.window.Window(800, 600, caption="Realm Knocker RGB", resizable=True)
batch = pyglet.graphics.Batch()
fps_display = pyglet.window.FPSDisplay(window)
fps_display.label.color = (255, 255, 255, 255)

# Game states
MENU = 0
PLAYING = 1
SETTINGS = 2
CREDITS = 3
RESOLUTION = 4
game_state = PLAYING  # Start directly in playing state for testing

# Biome setup
current_biome = "forest"
BIOME_COLORS = {
    "forest": (34, 139, 34),  # Green
    "void": (0, 0, 0)         # Black
}
biome_border = pyglet.shapes.Rectangle(400, 0, 2, 600, color=(255, 255, 255), batch=batch)

# Player setup
player = pyglet.shapes.Rectangle(300, 200, 50, 50, color=(255, 255, 0), batch=batch)
player_speed = 300
dash_cooldown = 0
dash_cooldown_max = 6
player_health = 100
stun_duration = 0

# Projectile setup
rocks = []
rock_cooldown = 0
rock_cooldown_max = 3

# Enemy setup
enemies = []
ENEMY_TYPES = {
    "normal": {
        "color": (255, 0, 0),
        "damage": 10,
        "rock_color": (165, 42, 42)
    },
    "special": {
        "color": (0, 0, 255),
        "damage": 15,
        "rock_color": (0, 191, 255),
        "stun_duration": 3
    }
}

class Enemy:
    def __init__(self, x, y, enemy_type):
        self.shape = pyglet.shapes.Rectangle(x, y, 50, 50, color=ENEMY_TYPES[enemy_type]["color"], batch=batch)
        self.rock_cooldown = 3
        self.alive = True
        self.enemy_type = enemy_type

    def update(self, dt):
        if self.alive:
            self.rock_cooldown -= dt
            if self.rock_cooldown <= 0:
                self.shoot()
                self.rock_cooldown = 3

    def shoot(self):
        dx = player.x - self.shape.x
        dy = player.y - self.shape.y
        dist = (dx**2 + dy**2)**0.5
        if dist > 0:
            rock = Rock(
                self.shape.x + 25, self.shape.y + 25,
                dx/dist, dy/dist,
                ENEMY_TYPES[self.enemy_type]["rock_color"],
                ENEMY_TYPES[self.enemy_type]["damage"],
                is_stun=(self.enemy_type == "special")
            )
            rocks.append(rock)

    def respawn(self):
        self.shape.x = random.randint(0, window.width)
        self.shape.y = random.randint(0, window.height)
        self.alive = True

class Rock:
    def __init__(self, x, y, dx, dy, color, damage, is_stun=False):
        if is_stun:
            self.shape = pyglet.shapes.Triangle(x, y, x+10, y+17, x-10, y+17, color=color, batch=batch)
        else:
            self.shape = pyglet.shapes.Rectangle(x, y, 10, 10, color=color, batch=batch)
        self.dx = dx
        self.dy = dy
        self.damage = damage
        self.is_stun = is_stun

    def update(self, dt):
        self.shape.x += self.dx * 200 * dt
        self.shape.y += self.dy * 200 * dt

        if check_collision(self.shape, player):
            global player_health, stun_duration
            player_health -= self.damage
            if self.is_stun:
                stun_duration = max(stun_duration, 3)
            self.delete()

    def delete(self):
        if self in rocks:
            rocks.remove(self)
        self.shape.delete()

def check_collision(a, b):
    return (a.x < b.x + b.width and
            a.x + a.width > b.x and
            a.y < b.y + b.height and
            a.y + a.height > b.y)

def update(dt):
    global rock_cooldown, dash_cooldown, player_health, stun_duration, current_biome

    if game_state == PLAYING:
        current_biome = "void" if player.x > 400 else "forest"
        
        if stun_duration <= 0:
            prev_x, prev_y = player.x, player.y
            
            # Movement
            if keys[key.W]: player.y += player_speed * dt
            if keys[key.S]: player.y -= player_speed * dt
            if keys[key.A]: player.x -= player_speed * dt
            if keys[key.D]: player.x += player_speed * dt
            
            # Dash ability
            if dash_cooldown <= 0 and keys[key.E]:
                dx = mouse_x - player.x
                dy = mouse_y - player.y
                dist = (dx**2 + dy**2)**0.5
                if dist > 0:
                    player.x += dx/dist * 100
                    player.y += dy/dist * 100
                    dash_cooldown = dash_cooldown_max
            
            # Rock throwing
            if rock_cooldown <= 0 and keys[key.Q]:
                dx = mouse_x - player.x
                dy = mouse_y - player.y
                dist = (dx**2 + dy**2)**0.5
                if dist > 0:
                    rock = Rock(
                        player.x + 25, player.y + 25,
                        dx/dist, dy/dist,
                        (255, 255, 0), 10
                    )
                    rocks.append(rock)
                    rock_cooldown = rock_cooldown_max

        # Update cooldowns
        stun_duration = max(0, stun_duration - dt)
        rock_cooldown = max(0, rock_cooldown - dt)
        dash_cooldown = max(0, dash_cooldown - dt)

        # Update projectiles and enemies
        for rock in rocks[:]:
            rock.update(dt)
        for enemy in enemies:
            enemy.update(dt)

        # Health management
        if player_health <= 0:
            player_health = 100
            player.x, player.y = 300, 200

@window.event
def on_draw():
    window.clear()
    pyglet.gl.glClearColor(*BIOME_COLORS[current_biome], 255)
    batch.draw()
    fps_display.draw()
    
    # Draw UI
    health_label = pyglet.text.Label(
        f"Health: {player_health}",
        x=10, y=window.height-30,
        color=(255, 255, 255, 255)
    )
    stun_label = pyglet.text.Label(
        f"Stunned: {stun_duration:.1f}s" if stun_duration > 0 else "",
        x=10, y=window.height-60,
        color=(255, 255, 255, 255)
    )
    health_label.draw()
    stun_label.draw()

# Initialize enemies
for _ in range(4):
    enemies.append(Enemy(random.randint(100, 700), random.randint(100, 500), "normal"))
    enemies.append(Enemy(random.randint(100, 700), random.randint(100, 500), "special"))

# Handle keyboard input
window.push_handlers(keys)
pyglet.clock.schedule_interval(update, 1/120.0)
pyglet.app.run()
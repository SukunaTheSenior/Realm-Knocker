import pyglet
from pyglet.window import key, mouse
import random

# Window setup
window = pyglet.window.Window(800, 600, caption="Realm Knocker RGB", resizable=True)
batch = pyglet.graphics.Batch()
fps_display = pyglet.window.FPSDisplay(window)
fps_display.label.color = (255, 255, 255, 255)

# Game states and biome setup
current_biome = "forest"
BIOME_COLORS = {
    "forest": (34, 139, 34),
    "void": (0, 0, 0)
}

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
enemy_types = {
    "normal": {
        "color": (255, 0, 0),
        "rock_damage": 10,
        "rock_color": (165, 42, 42)
    },
    "special": {
        "color": (0, 0, 255),
        "rock_damage": 15,
        "rock_color": (0, 191, 255),
        "stun_duration": 3
    }
}

# Biome transition line
biome_border = pyglet.shapes.Line(400, 0, 400, 600, width=5, color=(255, 255, 255), batch=batch)

class Enemy:
    def __init__(self, x, y, enemy_type):
        self.shape = pyglet.shapes.Rectangle(x, y, 50, 50, color=enemy_types[enemy_type]["color"], batch=batch)
        self.rock_cooldown = random.uniform(2, 4)
        self.alive = True
        self.type = enemy_type
        self.attack_counter = 0

    def update(self, dt):
        if self.alive:
            self.rock_cooldown -= dt
            if self.rock_cooldown <= 0:
                self.shoot_rock()
                self.attack_counter += 1
                if self.type == "special" and self.attack_counter >= 2:
                    self.rock_cooldown = 5
                    self.attack_counter = 0
                else:
                    self.rock_cooldown = random.uniform(2, 4) if self.type == "normal" else 3

    def shoot_rock(self):
        dx = player.x - self.shape.x
        dy = player.y - self.shape.y
        dist = ((dx ** 2) + (dy ** 2)) ** 0.5
        if dist > 0:
            rock = Rock(
                self.shape.x + 25, self.shape.y + 25,
                dx/dist, dy/dist,
                enemy_types[self.type]["rock_color"],
                enemy_types[self.type]["rock_damage"],
                is_stun=(self.type == "special")
            )
            rocks.append(rock)

    def respawn(self):
        self.shape.x = random.randint(0, window.width)
        self.shape.y = random.randint(0, window.height)
        self.alive = True

class Rock:
    def __init__(self, x, y, dx, dy, color, damage, is_stun=False):
        if is_stun:
            self.shape = pyglet.shapes.Triangle(
                x, y, x+10, y+17, x-10, y+17,
                color=color, batch=batch
            )
        else:
            self.shape = pyglet.shapes.Rectangle(x, y, 10, 10, color=color, batch=batch)
        self.dx = dx
        self.dy = dy
        self.damage = damage
        self.is_stun = is_stun

    def update(self, dt):
        self.shape.x += self.dx * dt * 200
        self.shape.y += self.dy * dt * 200

        # Check collision with player
        if check_collision(self.shape, player):
            global player_health, stun_duration
            player_health -= self.damage
            if self.is_stun:
                stun_duration = max(stun_duration, 3)
            self.delete()
            
        # Check collision with enemies (player projectiles)
        if not self.is_stun:
            for enemy in enemies:
                if enemy.alive and check_collision(self.shape, enemy.shape):
                    enemy.alive = False
                    pyglet.clock.schedule_once(lambda dt, e=enemy: e.respawn(), 5)
                    self.delete()

    def delete(self):
        if self in rocks:
            rocks.remove(self)
        self.shape.delete()

def check_collision(shape1, shape2):
    if isinstance(shape1, pyglet.shapes.Triangle):
        x1, y1 = shape1.x, shape1.y
        size = 10
    else:
        x1, y1 = shape1.x, shape1.y
        size = shape1.width
    
    return (
        x1 < shape2.x + shape2.width and
        x1 + size > shape2.x and
        y1 < shape2.y + shape2.height and
        y1 + size > shape2.y
    )

def update(dt):
    global rock_cooldown, dash_cooldown, player_health, stun_duration

    if game_state == PLAYING:
        # Update biome based on player position
        global current_biome
        current_biome = "void" if player.x > 400 else "forest"

        # Update player state
        prev_x, prev_y = player.x, player.y
        if stun_duration <= 0:
            if keys[key.W]: player.y += player_speed * dt
            if keys[key.S]: player.y -= player_speed * dt
            if keys[key.A]: player.x -= player_speed * dt
            if keys[key.D]: player.x += player_speed * dt
            
            if dash_cooldown <= 0 and keys[key.E]:
                dash_to_cursor()
                dash_cooldown = dash_cooldown_max

            if rock_cooldown <= 0 and keys[key.Q]:
                throw_rock()
                rock_cooldown = rock_cooldown_max

        # Update cooldowns
        stun_duration = max(0, stun_duration - dt)
        rock_cooldown = max(0, rock_cooldown - dt)
        dash_cooldown = max(0, dash_cooldown - dt)

        # Collision with walls
        for wall in walls:
            if check_collision(player, wall):
                player.x, player.y = prev_x, prev_y
                break

        # Update projectiles and enemies
        for rock in rocks[:]:
            rock.update(dt)
        for enemy in enemies:
            enemy.update(dt)

        # Health management
        if player_health <= 0:
            player_health = 100
            player.x, player.y = 300, 200

def dash_to_cursor():
    dx = mouse_x - player.x
    dy = mouse_y - player.y
    dist = (dx**2 + dy**2) ** 0.5
    if dist > 0:
        player.x += dx/dist * 100
        player.y += dy/dist * 100

def throw_rock():
    dx = mouse_x - player.x
    dy = mouse_y - player.y
    dist = (dx**2 + dy**2) ** 0.5
    if dist > 0:
        rock = Rock(
            player.x + 25, player.y + 25,
            dx/dist, dy/dist,
            (255, 255, 0), 10
        )
        rocks.append(rock)

@window.event
def on_draw():
    window.clear()
    pyglet.gl.glClearColor(*BIOME_COLORS[current_biome], 255)
    
    if game_state == PLAYING:
        batch.draw()
        fps_display.draw()
        
        # Draw UI elements
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
for _ in range(3):
    enemies.append(Enemy(random.randint(0, 400), random.randint(0, 600), "normal"))
    enemies.append(Enemy(random.randint(400, 800), random.randint(0, 600), "special"))

pyglet.clock.schedule_interval(update, 1/120.0)
pyglet.app.run()
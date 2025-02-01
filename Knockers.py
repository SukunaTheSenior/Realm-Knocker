import pyglet
from pyglet.window import key, mouse
import random

# Window setup
window = pyglet.window.Window(800, 600, caption="Realm Knocker RGB")
batch = pyglet.graphics.Batch()
fps_display = pyglet.window.FPSDisplay(window)
fps_display.label.color = (255, 255, 255, 255)  # White FPS counter

# Game states
MENU = 0
PLAYING = 1
game_state = MENU

# Player setup
player = pyglet.shapes.Rectangle(400, 300, 50, 50, color=(255, 255, 0), batch=batch)  # Yellow cube
player_speed = 300  # Pixels per second
dash_cooldown = 0
dash_cooldown_max = 10  # 10 seconds cooldown

# Rock setup
rocks = []
rock_cooldown = 0
rock_cooldown_max = 7  # 7 seconds cooldown

# Enemy setup
enemies = []
enemy_spawn_timer = 0
enemy_spawn_interval = 5  # Spawn every 5 seconds

# Walls
walls = [
    pyglet.shapes.Rectangle(100, 100, 600, 20, color=(100, 100, 100), batch=batch),  # Bottom wall
    pyglet.shapes.Rectangle(100, 480, 600, 20, color=(100, 100, 100), batch=batch),  # Top wall
    pyglet.shapes.Rectangle(100, 100, 20, 400, color=(100, 100, 100), batch=batch),  # Left wall
    pyglet.shapes.Rectangle(680, 100, 20, 400, color=(100, 100, 100), batch=batch),  # Right wall
]

# Score
score = 0
score_label = pyglet.text.Label("Score: 0", x=10, y=580, color=(255, 255, 255, 255), batch=batch)

# Key states
keys = key.KeyStateHandler()
window.push_handlers(keys)

# Mouse position
mouse_x, mouse_y = 0, 0

def update(dt):
    global rock_cooldown, dash_cooldown, enemy_spawn_timer, score, enemy_spawn_interval

    if game_state == PLAYING:
        # Player movement (WASD)
        if keys[key.W]:
            player.y += player_speed * dt
        if keys[key.S]:
            player.y -= player_speed * dt
        if keys[key.A]:
            player.x -= player_speed * dt
        if keys[key.D]:
            player.x += player_speed * dt

        # Dash ability (E key)
        if dash_cooldown <= 0 and keys[key.E]:
            dash_to_cursor()
            dash_cooldown = dash_cooldown_max

        # Rock throw (Q key)
        if rock_cooldown <= 0 and keys[key.Q]:
            throw_rock()
            rock_cooldown = rock_cooldown_max

        # Update cooldowns
        if rock_cooldown > 0:
            rock_cooldown -= dt
        if dash_cooldown > 0:
            dash_cooldown -= dt

        # Spawn enemies
        enemy_spawn_timer += dt
        if enemy_spawn_timer >= enemy_spawn_interval:
            spawn_enemy()
            enemy_spawn_timer = 0

        # Update enemies
        for enemy in enemies:
            enemy.update(dt)
            if random.random() < 0.1:  # 10% chance to shoot a rock
                enemy.shoot_rock()

        # Update rocks
        for rock in rocks:
            rock.update(dt)

        # Check collisions
        check_collisions()

        # Prevent player from going through walls
        for wall in walls:
            if (player.x < wall.x + wall.width and
                player.x + player.width > wall.x and
                player.y < wall.y + wall.height and
                player.y + player.height > wall.y):
                # Push player out of the wall
                if player.x < wall.x:
                    player.x = wall.x - player.width
                elif player.x + player.width > wall.x + wall.width:
                    player.x = wall.x + wall.width
                if player.y < wall.y:
                    player.y = wall.y - player.height
                elif player.y + player.height > wall.y + wall.height:
                    player.y = wall.y + wall.height

def dash_to_cursor():
    global player
    # Move player toward cursor by a small amount (e.g., 50 pixels)
    dx = mouse_x - player.x
    dy = mouse_y - player.y
    distance = (dx ** 2 + dy ** 2) ** 0.5
    if distance > 0:
        player.x += dx / distance * 50
        player.y += dy / distance * 50

def throw_rock():
    # Throw a rock toward the cursor
    dx = mouse_x - player.x
    dy = mouse_y - player.y
    distance = (dx ** 2 + dy ** 2) ** 0.5
    if distance > 0:
        rock = Rock(player.x, player.y, dx / distance, dy / distance)
        rocks.append(rock)

def spawn_enemy():
    # Spawn an enemy at a random edge of the screen
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        x = random.randint(100, 700)
        y = 480
    elif side == "bottom":
        x = random.randint(100, 700)
        y = 100
    elif side == "left":
        x = 100
        y = random.randint(100, 480)
    elif side == "right":
        x = 680
        y = random.randint(100, 480)
    enemy = Enemy(x, y)
    enemies.append(enemy)

def check_collisions():
    global score
    # Check if rocks hit enemies
    for rock in rocks[:]:
        for enemy in enemies[:]:
            if (rock.shape.x < enemy.shape.x + enemy.shape.width and
                rock.shape.x + rock.shape.width > enemy.shape.x and
                rock.shape.y < enemy.shape.y + enemy.shape.height and
                rock.shape.y + rock.shape.height > enemy.shape.y):
                rocks.remove(rock)
                enemies.remove(enemy)
                score += 1
                score_label.text = f"Score: {score}"
                # Spawn 3 more enemies after a random delay (2-10 seconds)
                pyglet.clock.schedule_once(lambda dt: spawn_enemy_group(), random.uniform(2, 10))

def spawn_enemy_group():
    for _ in range(3):
        spawn_enemy()

@window.event
def on_draw():
    window.clear()
    if game_state == MENU:
        draw_menu()
    elif game_state == PLAYING:
        batch.draw()
        fps_display.draw()

def draw_menu():
    # Draw main menu
    title = pyglet.text.Label("Realm Knocker 0.0.1 Beta",
                              font_size=36,
                              x=window.width//2, y=window.height//2 + 50,
                              anchor_x="center", anchor_y="center",
                              color=(255, 255, 255, 255))
    play_button = pyglet.text.Label("Play",
                                    font_size=24,
                                    x=window.width//2, y=window.height//2,
                                    anchor_x="center", anchor_y="center",
                                    color=(0, 255, 0, 255))
    quit_button = pyglet.text.Label("Quit",
                                    font_size=24,
                                    x=window.width//2, y=window.height//2 - 50,
                                    anchor_x="center", anchor_y="center",
                                    color=(255, 0, 0, 255))
    title.draw()
    play_button.draw()
    quit_button.draw()

@window.event
def on_mouse_press(x, y, button, modifiers):
    global game_state
    if game_state == MENU:
        if button == mouse.LEFT:
            if 350 <= x <= 450 and 250 <= y <= 300:  # Play button
                game_state = PLAYING
            elif 350 <= x <= 450 and 200 <= y <= 250:  # Quit button
                pyglet.app.exit()

@window.event
def on_mouse_motion(x, y, dx, dy):
    global mouse_x, mouse_y
    mouse_x, mouse_y = x, y

# Rock class
class Rock:
    def __init__(self, x, y, dx, dy):
        self.shape = pyglet.shapes.Rectangle(x, y, 10, 10, color=(165, 42, 42), batch=batch)
        self.dx = dx
        self.dy = dy

    def update(self, dt):
        self.shape.x += self.dx * dt * 200  # Rock speed
        self.shape.y += self.dy * dt * 200

# Enemy class
class Enemy:
    def __init__(self, x, y):
        self.shape = pyglet.shapes.Rectangle(x, y, 30, 30, color=(255, 0, 0), batch=batch)
        self.speed = 100  # Pixels per second

    def update(self, dt):
        # Move toward the player
        dx = player.x - self.shape.x
        dy = player.y - self.shape.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 0:
            self.shape.x += dx / distance * self.speed * dt
            self.shape.y += dy / distance * self.speed * dt

    def shoot_rock(self):
        # Shoot a rock toward the player
        dx = player.x - self.shape.x
        dy = player.y - self.shape.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 0:
            rock = Rock(self.shape.x, self.shape.y, dx / distance, dy / distance)
            rocks.append(rock)

# Schedule updates
pyglet.clock.schedule_interval(update, 1/120.0)  # 120 FPS cap

# Run the game
pyglet.app.run()
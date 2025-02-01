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
wizard_hat = pyglet.shapes.Triangle(425, 350, 400, 400, 375, 350, color=(128, 0, 128), batch=batch)  # Purple hat
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
enemy_spawn_interval = random.randint(5, 15)  # Spawn every 5-15 seconds

# Score
score = 0
score_label = pyglet.text.Label("Score: 0", x=10, y=580, color=(255, 255, 255, 255), batch=batch)

# Biome setup
biomes = []

# Key states
keys = key.KeyStateHandler()
window.push_handlers(keys)

# Mouse position
mouse_x, mouse_y = 0, 0

def update(dt):
    global rock_cooldown, dash_cooldown, enemy_spawn_timer, score

    if game_state == PLAYING:
        # Player movement (WASD)
        if keys[key.W]:
            player.y += player_speed * dt
            wizard_hat.y += player_speed * dt
        if keys[key.S]:
            player.y -= player_speed * dt
            wizard_hat.y -= player_speed * dt
        if keys[key.A]:
            player.x -= player_speed * dt
            wizard_hat.x -= player_speed * dt
        if keys[key.D]:
            player.x += player_speed * dt
            wizard_hat.x += player_speed * dt

        # Dash ability (Right Click)
        if dash_cooldown <= 0 and keys[key.R]:
            dash_to_cursor()
            dash_cooldown = dash_cooldown_max

        # Rock throw (Left Click)
        if rock_cooldown <= 0 and keys[key.L]:
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
            enemy_spawn_interval = random.randint(5, 15)

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

def dash_to_cursor():
    global player, wizard_hat
    # Move player toward cursor by a small amount (e.g., 50 pixels)
    dx = mouse_x - player.x
    dy = mouse_y - player.y
    distance = (dx ** 2 + dy ** 2) ** 0.5
    if distance > 0:
        player.x += dx / distance * 50
        player.y += dy / distance * 50
        wizard_hat.x += dx / distance * 50
        wizard_hat.y += dy / distance * 50

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
        x = random.randint(0, 800)
        y = 600
    elif side == "bottom":
        x = random.randint(0, 800)
        y = 0
    elif side == "left":
        x = 0
        y = random.randint(0, 600)
    elif side == "right":
        x = 800
        y = random.randint(0, 600)
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
                              font_name="Pixel", font_size=36,
                              x=window.width//2, y=window.height//2 + 50,
                              anchor_x="center", anchor_y="center",
                              color=(255, 255, 255, 255))
    play_button = pyglet.text.Label("Play",
                                    font_name="Pixel", font_size=24,
                                    x=window.width//2, y=window.height//2,
                                    anchor_x="center", anchor_y="center",
                                    color=(0, 255, 0, 255))
    quit_button = pyglet.text.Label("Quit",
                                    font_name="Pixel", font_size=24,
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

# Schedule updates
pyglet.clock.schedule_interval(update, 1/90.0)  # 90 FPS cap

# Run the game
pyglet.app.run()
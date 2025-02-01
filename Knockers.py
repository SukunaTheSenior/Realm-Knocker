import pyglet
from pyglet.window import key, mouse
import random

# Window setup
window = pyglet.window.Window(600, 400, caption="Realm Knocker RGB")  # Smaller window
batch = pyglet.graphics.Batch()
fps_display = pyglet.window.FPSDisplay(window)
fps_display.label.color = (255, 255, 255, 255)  # White FPS counter

# Game states
MENU = 0
PLAYING = 1
CREDITS = 2
game_state = MENU

# Confirmation dialog
show_confirmation = False

# Player setup
player = pyglet.shapes.Rectangle(300, 200, 50, 50, color=(255, 255, 0), batch=batch)  # Yellow cube
player_speed = 300  # Pixels per second
dash_cooldown = 0
dash_cooldown_max = 12  # 12 seconds cooldown
dash_charges = 2  # 2 dashes before cooldown
shift_held_time = 0  # Time Left Shift is held
max_shift_hold = 5  # Max dash duration (5 seconds)

# Rock setup
rocks = []
rock_cooldown = 0
rock_cooldown_max = 7  # 7 seconds cooldown
rock_clicks = 0  # Number of rocks shot
rock_click_limit = 7  # Max rocks before cooldown

# Boomerang cube setup
boomerang = None
boomerang_cooldown = 0
boomerang_cooldown_max = 3  # 3 seconds cooldown

# Key states
keys = key.KeyStateHandler()
window.push_handlers(keys)  # Ensure key states are updated

# Mouse position
mouse_x, mouse_y = 0, 0

def update(dt):
    global rock_cooldown, dash_cooldown, dash_charges, shift_held_time, rock_clicks, boomerang_cooldown

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

        # Dash ability (Left Shift)
        if keys[key.LSHIFT]:
            shift_held_time += dt
            shift_held_time = min(shift_held_time, max_shift_hold)  # Cap at 5 seconds
        elif dash_charges > 0 and shift_held_time > 0:
            dash_to_cursor(shift_held_time)
            dash_charges -= 1
            shift_held_time = 0
            if dash_charges == 0:
                dash_cooldown = dash_cooldown_max

        # Rock throw (Left Click)
        if rock_clicks < rock_click_limit and rock_cooldown <= 0:
            if keys[key.L]:
                throw_rock()
                rock_clicks += 1
                if rock_clicks >= rock_click_limit:
                    rock_cooldown = rock_cooldown_max

        # Boomerang cube (Right Click)
        if boomerang_cooldown <= 0 and keys[key.R]:
            shoot_boomerang()
            boomerang_cooldown = boomerang_cooldown_max

        # Update cooldowns
        if rock_cooldown > 0:
            rock_cooldown -= dt
        if dash_cooldown > 0:
            dash_cooldown -= dt
            if dash_cooldown <= 0:
                dash_charges = 2  # Reset dash charges
        if boomerang_cooldown > 0:
            boomerang_cooldown -= dt

        # Update rocks
        for rock in rocks:
            rock.update(dt)

        # Update boomerang
        if boomerang:
            boomerang.update(dt)

def dash_to_cursor(duration):
    global player
    # Move player toward cursor based on how long Left Shift was held
    dx = mouse_x - player.x
    dy = mouse_y - player.y
    distance = (dx ** 2 + dy ** 2) ** 0.5
    if distance > 0:
        player.x += dx / distance * duration * 100  # Dash distance scales with duration
        player.y += dy / distance * duration * 100

def throw_rock():
    # Throw a rock toward the cursor
    dx = mouse_x - player.x
    dy = mouse_y - player.y
    distance = (dx ** 2 + dy ** 2) ** 0.5
    if distance > 0:
        rock = Rock(player.x, player.y, dx / distance, dy / distance)
        rocks.append(rock)

def shoot_boomerang():
    global boomerang
    # Shoot a boomerang cube toward the cursor
    dx = mouse_x - player.x
    dy = mouse_y - player.y
    distance = (dx ** 2 + dy ** 2) ** 0.5
    if distance > 0:
        boomerang = Boomerang(player.x, player.y, dx / distance, dy / distance)

@window.event
def on_draw():
    window.clear()
    if game_state == MENU:
        draw_menu()
    elif game_state == PLAYING:
        batch.draw()
        fps_display.draw()
        if show_confirmation:
            draw_confirmation()
    elif game_state == CREDITS:
        draw_credits()

# Schedule updates
pyglet.clock.schedule_interval(update, 1/120.0)  # 120 FPS cap

# Run the game
pyglet.app.run()
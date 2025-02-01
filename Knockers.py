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
dash_cooldown = 12
dash_cooldown_max = 12  # 12 seconds cooldown
dash_charges = 2  # 2 dashes before cooldown
shift_held_time = 0  # Time Left Shift is held
max_shift_hold = 5  # Max dash duration (5 seconds)

# Rock setup
rocks = []
rock_cooldown = 7
rock_cooldown_max = 7  # 7 seconds cooldown
rock_clicks = 0  # Number of rocks shot
rock_click_limit = 7  # Max rocks before cooldown

# Boomerang cube setup
boomerang = None
boomerang_cooldown = 3
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

def draw_menu():
    # Draw main menu
    title = pyglet.text.Label("Realm Knocker 0.0.1 Beta",
                              font_size=24,
                              x=window.width//2, y=window.height//2 + 50,
                              anchor_x="center", anchor_y="center",
                              color=(255, 255, 255, 255))
    play_button = pyglet.text.Label("Play",
                                    font_size=18,
                                    x=window.width//2, y=window.height//2,
                                    anchor_x="center", anchor_y="center",
                                    color=(0, 255, 0, 255))
    credits_button = pyglet.text.Label("Credits",
                                       font_size=18,
                                       x=window.width//2, y=window.height//2 - 50,
                                       anchor_x="center", anchor_y="center",
                                       color=(0, 0, 255, 255))
    quit_button = pyglet.text.Label("Quit",
                                    font_size=18,
                                    x=window.width//2, y=window.height//2 - 100,
                                    anchor_x="center", anchor_y="center",
                                    color=(255, 0, 0, 255))
    title.draw()
    play_button.draw()
    credits_button.draw()
    quit_button.draw()

def draw_credits():
    # Draw credits screen
    credits_text = pyglet.text.Label("Game Developer: TabbyDevelopes on YouTube\nBeta Tester: @Forgetmeh on Discord!",
                                     font_size=16,
                                     x=window.width//2, y=window.height//2,
                                     anchor_x="center", anchor_y="center",
                                     color=(255, 255, 255, 255),
                                     multiline=True,
                                     width=400,
                                     align="center")
    back_button = pyglet.text.Label("Press ESC to go back",
                                    font_size=18,
                                    x=window.width//2, y=window.height//2 - 100,
                                    anchor_x="center", anchor_y="center",
                                    color=(255, 255, 255, 255))
    credits_text.draw()
    back_button.draw()

def draw_confirmation():
    # Draw confirmation dialog
    dialog = pyglet.shapes.Rectangle(200, 150, 200, 100, color=(50, 50, 50), batch=batch)
    text = pyglet.text.Label("Do you want to go back to the Main Menu?",
                             font_size=14,
                             x=window.width//2, y=window.height//2 + 20,
                             anchor_x="center", anchor_y="center",
                             color=(255, 255, 255, 255))
    yes_button = pyglet.text.Label("Yes",
                                   font_size=14,
                                   x=window.width//2 - 50, y=window.height//2 - 20,
                                   anchor_x="center", anchor_y="center",
                                   color=(0, 255, 0, 255))
    no_button = pyglet.text.Label("No",
                                  font_size=14,
                                  x=window.width//2 + 50, y=window.height//2 - 20,
                                  anchor_x="center", anchor_y="center",
                                  color=(255, 0, 0, 255))
    dialog.draw()
    text.draw()
    yes_button.draw()
    no_button.draw()

@window.event
def on_key_press(symbol, modifiers):
    global game_state, show_confirmation
    if symbol == key.ESCAPE:
        if game_state == CREDITS:
            game_state = MENU
        elif game_state == PLAYING:
            show_confirmation = not show_confirmation

@window.event
def on_mouse_press(x, y, button, modifiers):
    global game_state, show_confirmation
    if game_state == MENU:
        if button == mouse.LEFT:
            if 250 <= x <= 350 and 180 <= y <= 220:  # Play button
                game_state = PLAYING
            elif 250 <= x <= 350 and 130 <= y <= 170:  # Credits button
                game_state = CREDITS
            elif 250 <= x <= 350 and 80 <= y <= 120:  # Quit button
                pyglet.app.exit()
    elif game_state == PLAYING and show_confirmation:
        if button == mouse.LEFT:
            if 250 <= x <= 300 and 180 <= y <= 200:  # Yes button
                game_state = MENU
                show_confirmation = False
            elif 300 <= x <= 350 and 180 <= y <= 200:  # No button
                show_confirmation = False

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
        self.shape.x += self.dx * dt * 400  # Faster rocks
        self.shape.y += self.dy * dt * 400

# Boomerang class
class Boomerang:
    def __init__(self, x, y, dx, dy):
        self.shape = pyglet.shapes.Rectangle(x, y, 20, 20, color=(0, 0, 255), batch=batch)
        self.dx = dx
        self.dy = dy
        self.distance_traveled = 0
        self.max_distance = 200  # Max distance before returning

    def update(self, dt):
        if self.distance_traveled < self.max_distance:
            self.shape.x += self.dx * dt * 300
            self.shape.y += self.dy * dt * 300
            self.distance_traveled += dt * 300
        else:
            # Return to player
            dx = player.x - self.shape.x
            dy = player.y - self.shape.y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance > 0:
                self.shape.x += dx / distance * dt * 300
                self.shape.y += dy / distance * dt * 300

# Schedule updates
pyglet.clock.schedule_interval(update, 1/120.0)  # 120 FPS cap

# Run the game
pyglet.app.run()
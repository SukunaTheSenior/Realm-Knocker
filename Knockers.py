import pyglet
from pyglet.window import key, mouse
import random

# Window setup
window = pyglet.window.Window(600, 400, caption="Realm Knocker RGB")
batch = pyglet.graphics.Batch()
fps_display = pyglet.window.FPSDisplay(window)
fps_display.label.color = (255, 255, 255, 255)

# Game states
MENU = 0
PLAYING = 1
CREDITS = 2
SETTINGS = 3
game_state = MENU

# Player setup
player = pyglet.shapes.Rectangle(300, 200, 50, 50, color=(255, 255, 0), batch=batch)
player_speed = 300
dash_cooldown = 0
dash_cooldown_max = 5  # Single dash cooldown (5 seconds)
shift_held_time = 0
max_shift_hold = 3  # Reduced max dash duration

# Rock setup
rocks = []
rock_cooldown = 0
rock_cooldown_max = 5
rock_clicks = 0
rock_click_limit = 7

# Target setup
targets = []
for _ in range(5):  # Create 5 targets
    targets.append(pyglet.shapes.Rectangle(
        x=random.randint(50, 550),
        y=random.randint(50, 350),
        width=40, height=40,
        color=(128, 0, 128),  # Purple color
        batch=batch
    ))

# Add movement properties to targets
for target in targets:
    target.dx = random.choice([-1, 1]) * 150  # Movement speed
    target.hits = 0  # Hit counter

# Key states
keys = key.KeyStateHandler()
window.push_handlers(keys)

# Mouse position
mouse_x, mouse_y = 0, 0

def update(dt):
    global rock_cooldown, dash_cooldown, shift_held_time, rock_clicks

    if game_state == PLAYING:
        # Player movement
        if keys[key.W]:
            player.y += player_speed * dt
        if keys[key.S]:
            player.y -= player_speed * dt
        if keys[key.A]:
            player.x -= player_speed * dt
        if keys[key.D]:
            player.x += player_speed * dt

        # Dash ability (single dash)
        if keys[key.LSHIFT] and dash_cooldown <= 0:
            shift_held_time += dt
            shift_held_time = min(shift_held_time, max_shift_hold)
        elif shift_held_time > 0:
            dash_to_cursor(shift_held_time)
            shift_held_time = 0
            dash_cooldown = dash_cooldown_max

        # Rock throwing
        if rock_clicks < rock_click_limit and rock_cooldown <= 0:
            if keys[key.L]:
                throw_rock()
                rock_clicks += 1
                if rock_clicks >= rock_click_limit:
                    rock_cooldown = rock_cooldown_max

        # Update cooldowns
        if rock_cooldown > 0:
            rock_cooldown -= dt
        if dash_cooldown > 0:
            dash_cooldown -= dt

        # Update rocks and check collisions
        for rock in rocks[:]:
            rock.update(dt)
            # Check collision with targets
            for target in targets[:]:
                if (abs(rock.shape.x - target.x) < 30 and
                    abs(rock.shape.y - target.y) < 30):
                    target.hits += 1
                    if target.hits >= 5:
                        targets.remove(target)
                        batch.delete(target)
                    rocks.remove(rock)
                    batch.delete(rock.shape)
                    break

        # Update targets movement
        for target in targets:
            target.x += target.dx * dt
            if target.x > 560 or target.x < 40:
                target.dx *= -1

def dash_to_cursor(duration):
    dx = mouse_x - player.x
    dy = mouse_y - player.y
    distance = (dx ** 2 + dy ** 2) ** 0.5
    if distance > 0:
        player.x += dx / distance * duration * 120
        player.y += dy / distance * duration * 120

def throw_rock():
    dx = mouse_x - player.x
    dy = mouse_y - player.y
    distance = (dx ** 2 + dy ** 2) ** 0.5
    if distance > 0:
        rock = Rock(player.x, player.y, dx / distance, dy / distance)
        rocks.append(rock)

@window.event
def on_draw():
    window.clear()
    if game_state == MENU:
        draw_menu()
    elif game_state == PLAYING:
        batch.draw()
        fps_display.draw()
    elif game_state == CREDITS:
        draw_credits()
    elif game_state == SETTINGS:
        draw_settings()

def draw_menu():
    menu_items = [
        ("Play", 0, 255, 0),
        ("Settings", 255, 255, 0),
        ("Credits", 0, 0, 255),
        ("Quit", 255, 0, 0)
    ]
    
    pyglet.text.Label("Realm Knocker 0.0.1 Beta",
        font_size=24, x=300, y=300,
        anchor_x='center', anchor_y='center',
        color=(255, 255, 255, 255)).draw()
        
    for i, (text, r, g, b) in enumerate(menu_items):
        y_position = 250 - (i * 50)
        pyglet.text.Label(text,
            font_size=18, x=300, y=y_position,
            anchor_x='center', anchor_y='center',
            color=(r, g, b, 255)).draw()

def draw_credits():
    pyglet.text.Label("Developer: TabbyDevelopes\nBeta Tester: @Forgetmeh",
        font_size=16, x=300, y=250,
        anchor_x='center', anchor_y='center',
        multiline=True, width=400,
        color=(255, 255, 255, 255)).draw()
    pyglet.text.Label("Press ESC to return",
        font_size=14, x=300, y=100,
        anchor_x='center', anchor_y='center',
        color=(255, 255, 255, 255)).draw()

def draw_settings():
    pyglet.text.Label("Settings Menu (WIP)",
        font_size=24, x=300, y=250,
        anchor_x='center', anchor_y='center',
        color=(255, 255, 255, 255)).draw()

@window.event
def on_key_press(symbol, modifiers):
    global game_state
    if symbol == key.ESCAPE:
        if game_state in [CREDITS, SETTINGS]:
            game_state = MENU

@window.event
def on_mouse_press(x, y, button, modifiers):
    global game_state
    if game_state == MENU and button == mouse.LEFT:
        if 250 <= y <= 275:  # Play button
            game_state = PLAYING
        elif 200 <= y <= 225:  # Settings
            game_state = SETTINGS
        elif 150 <= y <= 175:  # Credits
            game_state = CREDITS
        elif 100 <= y <= 125:  # Quit
            pyglet.app.exit()

class Rock:
    def __init__(self, x, y, dx, dy):
        self.shape = pyglet.shapes.Rectangle(x, y, 10, 10, color=(165, 42, 42), batch=batch)
        self.dx = dx
        self.dy = dy

    def update(self, dt):
        self.shape.x += self.dx * dt * 400
        self.shape.y += self.dy * dt * 400
        # Remove rocks that go off-screen
        if (self.shape.x < -10 or self.shape.x > 610 or
            self.shape.y < -10 or self.shape.y > 410):
            self.shape.delete()
            rocks.remove(self)

pyglet.clock.schedule_interval(update, 1/120.0)
pyglet.app.run()
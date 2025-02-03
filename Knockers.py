import pyglet
from pyglet.window import key, mouse

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
dash_cooldown_max = 6  # Changed to 6 seconds

# Rock setup
rocks = []
rock_cooldown = 0
rock_cooldown_max = 3  # Changed to 3 seconds

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

# Camera offset
camera_x, camera_y = 0, 0

def check_collision(player, obstacle):
    return (
        player.x < obstacle.x + obstacle.width and
        player.x + player.width > obstacle.x and
        player.y < obstacle.y + obstacle.height and
        player.y + player.height > obstacle.y
    )

def update(dt):
    global rock_cooldown, dash_cooldown, camera_x, camera_y

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

        # Update camera to follow player
        camera_x = window.width // 2 - player.x - player.width // 2
        camera_y = window.height // 2 - player.y - player.height // 2

def dash_to_cursor():
    global player
    dx = mouse_x - player.x
    dy = mouse_y - player.y
    distance = (dx ** 2 + dy ** 2) ** 0.5
    if distance > 0:
        player.x += dx / distance * 100  # Increased dash distance
        player.y += dy / distance * 100  # Increased dash distance

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
        # Apply camera transformation
        pyglet.gl.glPushMatrix()
        pyglet.gl.glTranslatef(-camera_x, -camera_y, 0)
        batch.draw()
        fps_display.draw()
        pyglet.gl.glPopMatrix()
    elif game_state == SETTINGS:
        draw_settings()
    elif game_state == CREDITS:
        draw_credits()
    elif game_state == RESOLUTION:
        draw_resolution()

def draw_menu():
    title = pyglet.text.Label("Realm Knocker 0.0.1 Beta",
        font_size=24, x=window.width//2, y=window.height - 100,
        anchor_x="center", anchor_y="center", color=(255, 255, 255, 255))
    
    buttons = [
        ("Play", window.height//2 + 50, PLAYING),
        ("Settings", window.height//2, SETTINGS),
        ("Quit", window.height//2 - 50, MENU)  # Quit will exit the game
    ]

    for text, y, _ in buttons:
        label = pyglet.text.Label(text,
            font_size=18, x=window.width//2, y=y,
            anchor_x="center", anchor_y="center",
            color=(0, 255, 0, 255) if text == "Play" else (255, 255, 255, 255))
        label.draw()
    
    title.draw()

def draw_settings():
    title = pyglet.text.Label("Settings",
        font_size=24, x=window.width//2, y=window.height - 100,
        anchor_x="center", anchor_y="center", color=(255, 255, 255, 255))
    
    buttons = [
        ("Resolution", window.height//2 + 50, RESOLUTION),
        ("Credits", window.height//2, CREDITS),
        ("Back", window.height//2 - 50, MENU)
    ]

    for text, y, _ in buttons:
        label = pyglet.text.Label(text,
            font_size=18, x=window.width//2, y=y,
            anchor_x="center", anchor_y="center",
            color=(255, 255, 255, 255))
        label.draw()
    
    title.draw()

def draw_resolution():
    title = pyglet.text.Label("Resolution",
        font_size=24, x=window.width//2, y=window.height - 100,
        anchor_x="center", anchor_y="center", color=(255, 255, 255, 255))
    
    buttons = [
        ("800x600", window.height//2 + 100, None),
        (f"System ({SYSTEM_WIDTH}x{SYSTEM_HEIGHT})", window.height//2 + 50, None),
        ("Fullscreen", window.height//2, None),
        ("Back", window.height//2 - 50, SETTINGS)
    ]

    for text, y, _ in buttons:
        label = pyglet.text.Label(text,
            font_size=18, x=window.width//2, y=y,
            anchor_x="center", anchor_y="center",
            color=(255, 255, 255, 255))
        label.draw()
    
    title.draw()

def draw_credits():
    credits_text = pyglet.text.Label(
        "Game Developer: TabbyDevelopes on YouTube\nBeta Tester: @Forgetmeh on Discord!",
        font_size=16, x=window.width//2, y=window.height//2 + 50,
        anchor_x="center", anchor_y="center", color=(255, 255, 255, 255),
        multiline=True, width=400, align="center")
    
    back_button = pyglet.text.Label("Back",
        font_size=18, x=window.width//2, y=window.height//2 - 100,
        anchor_x="center", anchor_y="center", color=(255, 255, 255, 255))
    
    credits_text.draw()
    back_button.draw()

@window.event
def on_mouse_press(x, y, button, modifiers):
    global game_state

    if button == mouse.LEFT:
        if game_state == MENU:
            if is_clicked(x, y, window.height//2 + 50):  # Play
                game_state = PLAYING
            elif is_clicked(x, y, window.height//2):  # Settings
                game_state = SETTINGS
            elif is_clicked(x, y, window.height//2 - 50):  # Quit
                pyglet.app.exit()

        elif game_state == SETTINGS:
            if is_clicked(x, y, window.height//2 + 50):  # Resolution
                game_state = RESOLUTION
            elif is_clicked(x, y, window.height//2):  # Credits
                game_state = CREDITS
            elif is_clicked(x, y, window.height//2 - 50):  # Back
                game_state = MENU

        elif game_state == RESOLUTION:
            if is_clicked(x, y, window.height//2 + 100):  # 800x600
                window.set_size(800, 600)
            elif is_clicked(x, y, window.height//2 + 50):  # System resolution
                window.set_size(SYSTEM_WIDTH, SYSTEM_HEIGHT)
            elif is_clicked(x, y, window.height//2):  # Fullscreen
                window.set_fullscreen(not window.fullscreen)
            elif is_clicked(x, y, window.height//2 - 50):  # Back
                game_state = SETTINGS

        elif game_state == CREDITS:
            if is_clicked(x, y, window.height//2 - 100):  # Back
                game_state = SETTINGS

def is_clicked(x, y, target_y, tolerance=20):
    return (
        window.width//2 - 75 <= x <= window.width//2 + 75 and
        target_y - tolerance <= y <= target_y + tolerance
    )

@window.event
def on_mouse_motion(x, y, dx, dy):
    global mouse_x, mouse_y
    mouse_x, mouse_y = x, y

class Rock:
    def __init__(self, x, y, dx, dy):
        self.shape = pyglet.shapes.Rectangle(x, y, 10, 10, color=(165, 42, 42), batch=batch)
        self.dx = dx
        self.dy = dy

    def update(self, dt):
        self.shape.x += self.dx * dt * 200
        self.shape.y += self.dy * dt * 200

pyglet.clock.schedule_interval(update, 1/120.0)
pyglet.app.run()
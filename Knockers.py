import pyglet
from pyglet.window import key, mouse

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

# Player setup
player = pyglet.shapes.Rectangle(300, 200, 50, 50, color=(255, 255, 0), batch=batch)  # Yellow cube
player_speed = 300  # Pixels per second
dash_cooldown = 0
dash_cooldown_max = 10  # 10 seconds cooldown

# Rock setup
rocks = []
rock_cooldown = 0
rock_cooldown_max = 7  # 7 seconds cooldown

# Wall (block) setup
walls = [
    pyglet.shapes.Rectangle(100, 100, 50, 50, color=(139, 69, 19), batch=batch),  # Brown block 1
    pyglet.shapes.Rectangle(400, 300, 50, 50, color=(139, 69, 19), batch=batch),  # Brown block 2
]

# Key states
keys = key.KeyStateHandler()
window.push_handlers(keys)

# Mouse position
mouse_x, mouse_y = 0, 0

def check_collision(player, obstacle):
    """Check if the player collides with an obstacle."""
    return (
        player.x < obstacle.x + obstacle.width and
        player.x + player.width > obstacle.x and
        player.y < obstacle.y + obstacle.height and
        player.y + player.height > obstacle.y
    )

def update(dt):
    global rock_cooldown, dash_cooldown

    if game_state == PLAYING:
        # Store the player's previous position
        prev_x, prev_y = player.x, player.y

        # Player movement (WASD)
        if keys[key.W]:
            player.y += player_speed * dt
        if keys[key.S]:
            player.y -= player_speed * dt
        if keys[key.A]:
            player.x -= player_speed * dt
        if keys[key.D]:
            player.x += player_speed * dt

        # Check for collisions with walls
        for wall in walls:
            if check_collision(player, wall):
                # Revert to the previous position if there's a collision
                player.x, player.y = prev_x, prev_y
                break  # Stop checking other walls

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

        # Update rocks
        for rock in rocks:
            rock.update(dt)

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
    back_button = pyglet.text.Label("Back",
                                    font_size=18,
                                    x=window.width//2, y=window.height//2 - 100,
                                    anchor_x="center", anchor_y="center",
                                    color=(255, 255, 255, 255))
    credits_text.draw()
    back_button.draw()

@window.event
def on_mouse_press(x, y, button, modifiers):
    global game_state
    if game_state == MENU:
        if button == mouse.LEFT:
            if 250 <= x <= 350 and 180 <= y <= 220:  # Play button
                game_state = PLAYING
            elif 250 <= x <= 350 and 130 <= y <= 170:  # Credits button
                game_state = CREDITS
            elif 250 <= x <= 350 and 80 <= y <= 120:  # Quit button
                pyglet.app.exit()
    elif game_state == CREDITS:
        if button == mouse.LEFT:
            if 250 <= x <= 350 and 80 <= y <= 120:  # Back button
                game_state = MENU

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

# Schedule updates
pyglet.clock.schedule_interval(update, 1/120.0)  # 120 FPS cap

# Run the game
pyglet.app.run()
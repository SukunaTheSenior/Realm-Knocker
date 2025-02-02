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

# Camera variables
camera_x = 0
camera_y = 0

# Player setup
player = pyglet.shapes.Rectangle(300, 200, 50, 50, color=(255, 255, 0), batch=batch)
player_speed = 300
dash_cooldown = 0
dash_cooldown_max = 6  # Updated dash cooldown to 6 seconds

# Rock setup
rocks = []
rock_cooldown = 0
rock_cooldown_max = 3  # Updated rock cooldown to 3 seconds

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

        # Update camera position to center the player
        camera_x = player.x - window.width // 2 + player.width // 2
        camera_y = player.y - window.height // 2 + player.height // 2

def dash_to_cursor():
    global player
    dx = mouse_x - player.x
    dy = mouse_y - player.y
    distance = (dx ** 2 + dy ** 2) ** 0.5
    if distance > 0:
        player.x += dx / distance * 50
        player.y += dy / distance * 50

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
        pyglet.gl.glPushMatrix()
        pyglet.gl.glTranslatef(-camera_x, -camera_y, 0)  # Apply camera translation
        batch.draw()
        pyglet.gl.glPopMatrix()
        fps_display.draw()
    elif game_state == SETTINGS:
        draw_settings()
    elif game_state == CREDITS:
        draw_credits()
    elif game_state == RESOLUTION:
        draw_resolution()

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
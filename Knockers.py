import pyglet
from pyglet.window import key, mouse
from pyglet import gl

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
game_state = MENU

# Player setup
player = pyglet.shapes.Rectangle(300, 200, 50, 50, color=(255, 255, 0), batch=batch)
player_speed = 300
dash_cooldown = 0
dash_cooldown_max = 1.5  # Reduced cooldown for better feel

# Camera setup
camera_x, camera_y = 0, 0

# Rock setup
rocks = []
rock_cooldown = 0
rock_cooldown_max = 0.8  # Reduced cooldown for click spam
rock_speed = 400  # Increased rock speed

# Wall setup
walls = [
    pyglet.shapes.Rectangle(100, 100, 50, 50, color=(139, 69, 19), batch=batch),
    pyglet.shapes.Rectangle(400, 300, 50, 50, color=(139, 69, 19), batch=batch),
]

# Key states
keys = key.KeyStateHandler()
window.push_handlers(keys)
mouse_pressed = False

# System resolution
screen = window.display.get_default_screen()
SYSTEM_WIDTH = screen.width
SYSTEM_HEIGHT = screen.height

def check_collision(obj1, obj2):
    return (
        obj1.x < obj2.x + obj2.width and
        obj1.x + obj1.width > obj2.x and
        obj1.y < obj2.y + obj2.height and
        obj1.y + obj1.height > obj2.y
    )

def update(dt):
    global rock_cooldown, dash_cooldown, camera_x, camera_y

    if game_state == PLAYING:
        # Camera follows player
        camera_x = player.x - window.width//2
        camera_y = player.y - window.height//2

        prev_x, prev_y = player.x, player.y

        # Movement with WASD
        if keys[key.W]:
            player.y += player_speed * dt
        if keys[key.S]:
            player.y -= player_speed * dt
        if keys[key.A]:
            player.x -= player_speed * dt
        if keys[key.D]:
            player.x += player_speed * dt

        # Dash with Left Shift
        if keys[key.LSHIFT] and dash_cooldown <= 0:
            dash_to_cursor()
            dash_cooldown = dash_cooldown_max

        # Collision detection
        for wall in walls:
            if check_collision(player, wall):
                player.x, player.y = prev_x, prev_y
                break

        # Update cooldowns
        dash_cooldown = max(0, dash_cooldown - dt)
        rock_cooldown = max(0, rock_cooldown - dt)

        # Update rocks
        for rock in rocks[:]:
            rock.update(dt)
            if rock.distance > 1000:  # Remove distant rocks
                rocks.remove(rock)

def dash_to_cursor():
    global player
    # Convert screen coordinates to game world coordinates
    target_x = mouse_x + camera_x
    target_y = mouse_y + camera_y
    
    dx = target_x - player.x
    dy = target_y - player.y
    distance = (dx**2 + dy**2)**0.5
    
    if distance > 0:
        player.x += dx/distance * 80  # Dash distance
        player.y += dy/distance * 80

def throw_rock():
    # Convert screen coordinates to game world coordinates
    target_x = mouse_x + camera_x
    target_y = mouse_y + camera_y
    
    dx = target_x - player.x
    dy = target_y - player.y
    distance = (dx**2 + dy**2)**0.5
    
    if distance > 0:
        rocks.append(Rock(player.x + 25, player.y + 25, dx/distance, dy/distance))

@window.event
def on_draw():
    window.clear()
    if game_state == PLAYING:
        # Camera transformation
        gl.glPushMatrix()
        gl.glTranslatef(-int(camera_x), -int(camera_y), 0)
        batch.draw()
        gl.glPopMatrix()
        fps_display.draw()
    elif game_state == MENU:
        draw_menu()
    elif game_state == SETTINGS:
        draw_settings()
    elif game_state == CREDITS:
        draw_credits()
    elif game_state == RESOLUTION:
        draw_resolution()

# [Keep all the menu/drawing functions from previous code, only showing key changes below]

@window.event
def on_mouse_press(x, y, button, modifiers):
    global game_state, rock_cooldown
    
    if game_state == PLAYING and button == mouse.LEFT:
        if rock_cooldown <= 0:
            throw_rock()
            rock_cooldown = rock_cooldown_max
            
    # [Keep existing menu click handling]

class Rock:
    def __init__(self, x, y, dx, dy):
        self.shape = pyglet.shapes.Circle(x, y, 8, color=(165, 42, 42), batch=batch)
        self.dx = dx * rock_speed
        self.dy = dy * rock_speed
        self.distance = 0

    def update(self, dt):
        self.shape.x += self.dx * dt
        self.shape.y += self.dy * dt
        self.distance += (self.dx**2 + self.dy**2)**0.5 * dt

# [Keep rest of the code]
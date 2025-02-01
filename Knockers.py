import pyglet
from pyglet.window import key, mouse
import random

# Window setup
window = pyglet.window.Window(600, 400, caption="Realm Knocker RGB")
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
player = pyglet.shapes.Rectangle(300, 200, 50, 50, color=(255, 255, 0), batch=batch)
player_speed = 300  
dash_cooldown = 0
dash_cooldown_max = 12  
dash_charges = 2  
shift_held_time = 0  
max_shift_hold = 5  

# Mouse position
mouse_x, mouse_y = 0, 0

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
    window.clear()
    title = pyglet.text.Label("Realm Knocker 0.0.1 Beta",
                              font_size=24,
                              x=window.width//2, y=window.height//2 + 80,
                              anchor_x="center", anchor_y="center",
                              color=(255, 255, 255, 255))
    
    play_button = pyglet.text.Label("[Play]",
                                    font_size=18,
                                    x=window.width//2, y=window.height//2,
                                    anchor_x="center", anchor_y="center",
                                    color=(0, 255, 0, 255))
    
    credits_button = pyglet.text.Label("[Credits]",
                                       font_size=18,
                                       x=window.width//2, y=window.height//2 - 50,
                                       anchor_x="center", anchor_y="center",
                                       color=(0, 0, 255, 255))
    
    quit_button = pyglet.text.Label("[Quit]",
                                    font_size=18,
                                    x=window.width//2, y=window.height//2 - 100,
                                    anchor_x="center", anchor_y="center",
                                    color=(255, 0, 0, 255))
    
    title.draw()
    play_button.draw()
    credits_button.draw()
    quit_button.draw()

@window.event
def on_mouse_press(x, y, button, modifiers):
    global game_state
    if game_state == MENU and button == mouse.LEFT:
        if window.height//2 - 20 <= y <= window.height//2 + 20:
            game_state = PLAYING  
        elif window.height//2 - 70 <= y <= window.height//2 - 30:
            game_state = CREDITS  
        elif window.height//2 - 120 <= y <= window.height//2 - 80:
            pyglet.app.exit()  

# Run the game
pyglet.app.run()
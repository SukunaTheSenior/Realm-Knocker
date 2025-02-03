class Enemy:
    def __init__(self, x, y):
        self.shape = pyglet.shapes.Rectangle(x, y, 50, 50, color=(255, 0, 0), batch=batch)
        self.rock_cooldown = enemy_rock_cooldown
        self.alive = True
        self.health = 3  # Enemy requires 3 hits to die
        self.speed = 100  # Movement speed

    def update(self, dt):
        if self.alive:
            self.move_towards_player(dt)
            self.rock_cooldown -= dt
            if self.rock_cooldown <= 0:
                self.shoot_rock()
                self.rock_cooldown = enemy_rock_cooldown

    def move_towards_player(self, dt):
        dx = player.x - self.shape.x
        dy = player.y - self.shape.y
        dist = distance(self.shape.x, self.shape.y, player.x, player.y)

        if dist > 0:
            move_x = (dx / dist) * self.speed * dt
            move_y = (dy / dist) * self.speed * dt

            new_x, new_y = self.shape.x + move_x, self.shape.y + move_y

            # Check collision with walls
            if not any(check_collision(pyglet.shapes.Rectangle(new_x, new_y, 50, 50), wall) for wall in walls):
                self.shape.x, self.shape.y = new_x, new_y

    def shoot_rock(self):
        dx = player.x - self.shape.x
        dy = player.y - self.shape.y
        dist = distance(self.shape.x, self.shape.y, player.x, player.y)
        if dist > 0:
            rock = Rock(self.shape.x, self.shape.y, dx / dist, dy / dist, is_enemy=True)
            rocks.append(rock)

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            self.die()

    def die(self):
        self.alive = False
        self.shape.color = (100, 100, 100)  # Change color to indicate death
        pyglet.clock.schedule_once(lambda dt: self.respawn(), enemy_respawn_time)

    def respawn(self):
        self.shape.x = random.randint(50, window.width - 50)
        self.shape.y = random.randint(50, window.height - 50)
        self.alive = True
        self.health = 3
        self.shape.color = (255, 0, 0)  # Reset to red color
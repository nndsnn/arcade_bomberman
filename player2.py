import arcade
import time

SCREEN_WIDTH = 1900
SCREEN_HEIGHT = 1050

class Player2(arcade.Sprite):
    def __init__(self, game):

        super().__init__("assets/Plear2_green/idle.png", scale=0.5)
       

        self.game = game
        self.hero_speed = 200
        self.health = 100
        self.bomb_limit = 1
        self.active_bombs = 0
        self.last_bomb_time = 0
        self.bomb_cooldown = 1.0 

        self.speed_particles = 0  
        self.bomb_particles = 0  

        self.coins = 0

        self.has_shield = False
        self.has_star = False
        self.shield_end_time = 0
        self.star_end_time = 0

        self.speed_level = 1
        self.speed_multiplier = 1.0

        self.bomb_level = 1
        self.explosion_radius = 1

        self.is_alive = True
        self.center_x = SCREEN_WIDTH - 70
        self.center_y = SCREEN_HEIGHT - 70

    
    
        self.idle_texture = arcade.load_texture("assets/Plear2_green/idle.png")
        self.texture = self.idle_texture
        self.walk_textures = []
        for i in range(1, 5):
            texture = arcade.load_texture(f"assets/Plear2_green/walk{i}.png")
            self.walk_textures.append(texture)

        self.current_texture = 0
        self.texture_change_time = 0
        self.texture_change_delay = 0.1
        self.is_walking = False

    def update_animation(self, delta_time: float = 1/60):
        if self.is_alive:
            if self.is_walking and len(self.walk_textures) > 0:
                self.texture_change_time += delta_time
                if self.texture_change_time >= self.texture_change_delay:
                    self.texture_change_time = 0
                    self.current_texture += 1
                    if self.current_texture >= len(self.walk_textures):
                        self.current_texture = 0
                    self.texture = self.walk_textures[self.current_texture]
            else:
                self.texture = self.idle_texture

    def get_effective_speed(self):
        return self.hero_speed * self.speed_multiplier

    def update(self, delta_time, keys_pressed):
        if not self.is_alive:
            return

        if self.has_shield and time.time() > self.shield_end_time:
            self.has_shield = False

        if self.has_star and time.time() > self.star_end_time:
            self.has_star = False

        dx, dy = 0, 0
        effective_speed = self.get_effective_speed()

        if arcade.key.LEFT in keys_pressed:
            dx -= effective_speed * delta_time
        if arcade.key.RIGHT in keys_pressed:
            dx += effective_speed * delta_time
        if arcade.key.UP in keys_pressed:
            dy += effective_speed * delta_time
        if arcade.key.DOWN in keys_pressed:
            dy -= effective_speed * delta_time

        if dx != 0 and dy != 0:
            factor = 0.7071
            dx *= factor
            dy *= factor

        old_x, old_y = self.center_x, self.center_y
        
        self.center_x += dx
        self.center_y += dy

        collision_happened = False
        
        if hasattr(self.game, 'collision_list'):
            if arcade.check_for_collision_with_list(self, self.game.collision_list):
                collision_happened = True
        
        if hasattr(self.game, 'destroy_list'):
            if arcade.check_for_collision_with_list(self, self.game.destroy_list):
                collision_happened = True
        
        if hasattr(self.game, 'Indestructible_list'):
            if arcade.check_for_collision_with_list(self, self.game.Indestructible_list):
                collision_happened = True
        
        if hasattr(self.game, 'destructible_list'):
            if arcade.check_for_collision_with_list(self, self.game.destructible_list):
                collision_happened = True

        if collision_happened:
            self.center_x, self.center_y = old_x, old_y

        margin_x = 30
        margin_y = 20
        self.center_x = max(margin_x, min(SCREEN_WIDTH - margin_x, self.center_x))
        self.center_y = max(margin_y, min(SCREEN_HEIGHT - margin_y, self.center_y))
        self.is_walking = dx != 0 or dy != 0

    def can_place_bomb(self):
        if not self.is_alive:
            return False

        current_time = time.time()
        time_since_last_bomb = current_time - self.last_bomb_time

        if self.active_bombs >= self.bomb_limit:
            return False

        if time_since_last_bomb < self.bomb_cooldown:
            return False

        return True

    def place_bomb(self):
        if not self.can_place_bomb():
            return None

        tile_size = self.game.tile_size
        cell_x = int(self.center_x // tile_size)
        cell_y = int(self.center_y // tile_size)
        bomb_x = cell_x * tile_size + tile_size // 2
        bomb_y = cell_y * tile_size + tile_size // 2

        for existing_bomb in self.game.bomb_list:
            existing_cell_x = int(existing_bomb.center_x // tile_size)
            existing_cell_y = int(existing_bomb.center_y // tile_size)
            if cell_x == existing_cell_x and cell_y == existing_cell_y:
                return None

        from main import Bomb
        bomb = Bomb(bomb_x, bomb_y, explosion_time=2.0, owner=self)
        self.game.bomb_list.append(bomb)
        self.active_bombs += 1
        self.last_bomb_time = time.time()
        return bomb

    def add_speed_particle(self):
        self.speed_particles += 1
        
        if self.speed_particles % 5 == 0:
            self.upgrade_speed()

    def upgrade_speed(self):
        self.speed_level += 1

        if self.speed_level == 2:
            self.speed_multiplier = 1.2
        elif self.speed_level == 3:
            self.speed_multiplier = 1.4
        elif self.speed_level == 4:
            self.speed_multiplier = 1.6
        elif self.speed_level == 5:
            self.speed_multiplier = 1.8
        else:
            self.speed_multiplier = 2.0


    def add_bomb_particle(self):
        self.bomb_particles += 1
        
        if self.bomb_particles % 8 == 0:
            self.upgrade_bombs()

    def upgrade_bombs(self):
        self.bomb_level += 1
        self.bomb_limit += 1
        self.explosion_radius += 1

    def add_coin(self, amount=1):
        self.coins += amount

    def give_shield(self):
        self.has_shield = True
        self.shield_end_time = time.time() + 10

    def give_star(self):
        self.has_star = True
        self.star_end_time = time.time() + 8

    def take_damage(self, damage):
        if not self.is_alive:
            return

        if self.has_shield:
            self.has_shield = False
            return

        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
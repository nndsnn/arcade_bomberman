import arcade
from db import DB
import math
import time
import random
from player2 import Player2
from paus import PauseButton

SCREEN_WIDTH = 1900
SCREEN_HEIGHT = 1050
SCREEN_TITLE = "Bomber"

AVAILABLE_MAPS = [
    "map1.tmx",
    "map2.tmx",
    "map3.tmx",
]


class SpeedParticle(arcade.Sprite):

    def __init__(self, x, y):
        super().__init__(center_x=x, center_y=y)

        self.texture = arcade.load_texture("Power_UP/capogipng.png")

        self.scale = 0.1
        self.alpha = 255
        self.color = arcade.color.BLUE
        self.value = 1

        self.float_timer = 0
        self.float_speed = 1.5
        self.spawn_time = time.time()
        self.lifetime = 7.0

    def update(self, delta_time: float = 1/60):
        self.float_timer += delta_time * self.float_speed
        self.center_y += math.sin(self.float_timer) * 0.2

        current_time = time.time()
        time_since_spawn = current_time - self.spawn_time

        if time_since_spawn > self.lifetime - 2.0:
            self.alpha = int(
                255 * (0.5 + 0.5 * math.sin(time_since_spawn * 10)))
        elif time_since_spawn >= self.lifetime:
            self.remove_from_sprite_lists()


class BombParticle(arcade.Sprite):

    def __init__(self, x, y):
        super().__init__(center_x=x, center_y=y)

        self.texture = arcade.load_texture("Power_UP/bomb_power.png")

        self.scale = 0.6
        self.alpha = 255
        self.color = arcade.color.RED
        self.value = 1

        self.float_timer = 0
        self.float_speed = 1.5
        self.spawn_time = time.time()
        self.lifetime = 7.0

    def update(self, delta_time: float = 1/60):
        self.float_timer += delta_time * self.float_speed
        self.center_y += math.sin(self.float_timer) * 0.2

        current_time = time.time()
        time_since_spawn = current_time - self.spawn_time

        if time_since_spawn > self.lifetime - 2.0:
            self.alpha = int(
                255 * (0.5 + 0.5 * math.sin(time_since_spawn * 10)))
        elif time_since_spawn >= self.lifetime:
            self.remove_from_sprite_lists()


class Shield(arcade.Sprite):

    def __init__(self, x, y):
        super().__init__(center_x=x, center_y=y)

        self.texture = arcade.load_texture("Power_UP/hiled.png")

        self.scale = 0.2
        self.spawn_time = time.time()
        self.lifetime = 15.0

        self.rotation_timer = 0

    def update(self, delta_time: float = 1/60):
        self.rotation_timer += delta_time
        self.angle = math.sin(self.rotation_timer * 2) * 10

        current_time = time.time()
        if current_time - self.spawn_time >= self.lifetime:
            self.remove_from_sprite_lists()


class Star(arcade.Sprite):

    def __init__(self, x, y):
        super().__init__(center_x=x, center_y=y)

        self.texture = arcade.load_texture("Power_UP/star.png")

        self.scale = 1.0
        self.spawn_time = time.time()
        self.lifetime = 10.0

        self.pulse_timer = 0

    def update(self, delta_time: float = 1/60):
        self.pulse_timer += delta_time
        pulse = 1.0 + 0.2 * math.sin(self.pulse_timer * 5)
        self.scale = pulse

        current_time = time.time()
        if current_time - self.spawn_time >= self.lifetime:
            self.remove_from_sprite_lists()


class Coin(arcade.Sprite):

    def __init__(self, x, y):
        super().__init__(center_x=x, center_y=y)

        self.texture = arcade.load_texture("Power_UP/coinGold.png")

        self.scale = 1.0
        self.spawn_time = time.time()
        self.lifetime = 10.0

        self.rotation_timer = 0

    def update(self, delta_time: float = 1/60):
        self.rotation_timer += delta_time
        self.angle = self.rotation_timer * 100

        current_time = time.time()
        if current_time - self.spawn_time >= self.lifetime:
            self.remove_from_sprite_lists()


class Bomb(arcade.Sprite):
    def __init__(self, x, y, explosion_time=2.0, owner=None):
        super().__init__()

        self.bomb_texture = arcade.load_texture("assets/Bomb/bomb.png")
        self.bomb_texture2 = arcade.load_texture("assets/Bomb/bomb1.png")
        self.has_two_textures = True
        self.texture = self.bomb_texture
        self.scale = 0.8

        self.center_x = x
        self.center_y = y
        self.explosion_time = explosion_time
        self.placed_time = time.time()
        self.has_exploded = False
        self.blink_interval = 0.3
        self.blink_timer = 0
        self.owner = owner

    def update(self, delta_time: float = 1/60):
        current_time = time.time()
        time_since_placed = current_time - self.placed_time

        if not self.has_exploded and time_since_placed >= self.explosion_time:
            self.has_exploded = True
            return

        if self.has_two_textures:
            self.blink_timer += delta_time
            if self.blink_timer >= self.blink_interval:
                self.blink_timer = 0
                if self.texture == self.bomb_texture:
                    self.texture = self.bomb_texture2
                else:
                    self.texture = self.bomb_texture


class Hero(arcade.Sprite):
    def __init__(self, game):
        super().__init__("assets/Plaer1_purple/idle.png", scale=0.5)

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
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2

        self.idle_texture = arcade.load_texture(
            "assets/Plaer1_purple/idle.png")
        self.texture = self.idle_texture
        self.walk_textures = []
        for i in range(1, 5):
            texture = arcade.load_texture(
                f"assets/Plaer1_purple/walk{i}.png")
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

        if arcade.key.A in keys_pressed:
            dx -= effective_speed * delta_time
        if arcade.key.D in keys_pressed:
            dx += effective_speed * delta_time
        if arcade.key.W in keys_pressed:
            dy += effective_speed * delta_time
        if arcade.key.S in keys_pressed:
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
        self.center_x = max(margin_x, min(
            SCREEN_WIDTH - margin_x, self.center_x))
        self.center_y = max(margin_y, min(
            SCREEN_HEIGHT - margin_y, self.center_y))
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


class MyGame(arcade.Window):
    def __init__(self, width, height, title, resizable=False):
        super().__init__(width, height, title, resizable)

        self.in_menu = True
        self.in_settings = False
        self.in_rules = False
        self.game_paused = False
        self.hover_button = 0
        self.hover_settings_button = 0
        self.sound_enabled = True
        self.db = DB()  
        self.sound_enabled = self.db.get()
        self.keys_pressed = set()
        self.explosion_time = 0
        self.show_explosion = False
        self.explosion_x = 0
        self.explosion_y = 0
        self.tile_size = 70
        self.death_time = 0
        self.restart_cooldown = 3.0
        self.background_music = None
        self.music_player = None
        self.current_map = 0
        self.particle_chance = 0.3
        self.shield_chance = 0.1
        self.star_chance = 0.1
        self.coin_chance = 0.5
        self.pause_button = PauseButton(x=40, y=SCREEN_HEIGHT - 10)

        self.background_music = arcade.load_sound(
            "music/Track-3-Boomberman.wav")

    def setup(self, map_index):
        self.current_map = map_index
        map_file = AVAILABLE_MAPS[map_index]

        self.player_list = arcade.SpriteList()
        self.bomb_list = arcade.SpriteList()
        self.speed_particles = arcade.SpriteList()
        self.bomb_particles = arcade.SpriteList()
        self.shield_list = arcade.SpriteList()
        self.star_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.loot_cells = set()
        self.pause_button.is_paused = False

        TILE_SCALING = 1
        tile_map = arcade.load_tilemap(map_file, scaling=TILE_SCALING)

        self.Indestructible_list = tile_map.sprite_lists.get(
            "Indestructible", arcade.SpriteList())
        self.destructible_list = tile_map.sprite_lists.get(
            "destructible", arcade.SpriteList())
        self.Background_list = tile_map.sprite_lists.get(
            "Background", arcade.SpriteList())
        self.collision_list = tile_map.sprite_lists.get(
            "Colision", arcade.SpriteList())
        self.destroy_list = tile_map.sprite_lists.get(
            "Destroy", arcade.SpriteList())

        self.player = Hero(self)
        self.player.center_x = 95
        self.player.center_y = 960
        self.player_list.append(self.player)

        self.player2 = Player2(self)
        self.player2.center_x = 1225
        self.player2.center_y = 110
        self.player_list.append(self.player2)

        if self.sound_enabled:
            if self.music_player is not None:
                arcade.stop_sound(self.music_player)
            self.music_player = arcade.play_sound(
                self.background_music, volume=0.3)

    def create_empty_lists(self):
        self.Indestructible_list = arcade.SpriteList()
        self.destructible_list = arcade.SpriteList()
        self.Background_list = arcade.SpriteList()
        self.collision_list = arcade.SpriteList()
        self.destroy_list = arcade.SpriteList()

    def is_player_in_explosion_radius(self, bomb_x, bomb_y, player, bomb_owner):
        if not player.is_alive:
            return False

        tile_size = self.tile_size
        bomb_cell_x = int(bomb_x // tile_size)
        bomb_cell_y = int(bomb_y // tile_size)

        player_cell_x = int(player.center_x // tile_size)
        player_cell_y = int(player.center_y // tile_size)

        current_radius = bomb_owner.explosion_radius

        if player_cell_x == bomb_cell_x and abs(player_cell_y - bomb_cell_y) <= current_radius:
            if player_cell_y > bomb_cell_y:
                for row in range(bomb_cell_y + 1, player_cell_y + 1):
                    if self.check_collision_in_cell(bomb_cell_x, row):
                        return False
            else:
                for row in range(player_cell_y, bomb_cell_y):
                    if self.check_collision_in_cell(bomb_cell_x, row):
                        return False
            return True

        elif player_cell_y == bomb_cell_y and abs(player_cell_x - bomb_cell_x) <= current_radius:
            if player_cell_x > bomb_cell_x:
                for col in range(bomb_cell_x + 1, player_cell_x + 1):
                    if self.check_collision_in_cell(col, bomb_cell_y):
                        return False
            else:
                for col in range(player_cell_x, bomb_cell_x):
                    if self.check_collision_in_cell(col, bomb_cell_y):
                        return False
            return True

        return False

    def check_collision_in_cell(self, cell_x, cell_y):
        for sprite in self.collision_list:
            sprite_cell_x = int(sprite.center_x // self.tile_size)
            sprite_cell_y = int(sprite.center_y // self.tile_size)
            if sprite_cell_x == cell_x and sprite_cell_y == cell_y:
                return True
        return False

    def get_blocks_in_cell(self, cell_x, cell_y, sprite_list):
        blocks = []
        for sprite in sprite_list:
            sprite_cell_x = int(sprite.center_x // self.tile_size)
            sprite_cell_y = int(sprite.center_y // self.tile_size)
            if sprite_cell_x == cell_x and sprite_cell_y == cell_y:
                blocks.append(sprite)
        return blocks

    def spawn_loot(self, x, y):
        tile_size = self.tile_size
        cell_x = int(x // tile_size)
        cell_y = int(y // tile_size)

        if hasattr(self, 'loot_cells'):
            if (cell_x, cell_y) in self.loot_cells:
                return
        else:
            self.loot_cells = set()

        self.loot_cells.add((cell_x, cell_y))
        loot_x = cell_x * tile_size + tile_size // 2
        loot_y = cell_y * tile_size + tile_size // 2

        rand = random.random()

        if rand < self.coin_chance:
            coin = Coin(loot_x, loot_y)
            self.coin_list.append(coin)

        elif rand < self.coin_chance + self.particle_chance:
            if random.random() < 0.5:
                particle = SpeedParticle(loot_x, loot_y)
                self.speed_particles.append(particle)
            else:
                particle = BombParticle(loot_x, loot_y)
                self.bomb_particles.append(particle)

        elif rand < self.coin_chance + self.particle_chance + self.shield_chance:
            shield = Shield(loot_x, loot_y)
            self.shield_list.append(shield)

        else:
            star = Star(loot_x, loot_y)
            self.star_list.append(star)

    def check_collisions(self):
        speed_hit_list = arcade.check_for_collision_with_list(
            self.player, self.speed_particles
        )

        for particle in speed_hit_list:
            self.player.add_speed_particle()
            particle.remove_from_sprite_lists()

        bomb_hit_list = arcade.check_for_collision_with_list(
            self.player, self.bomb_particles
        )

        for particle in bomb_hit_list:
            self.player.add_bomb_particle()
            particle.remove_from_sprite_lists()

        coin_hit_list = arcade.check_for_collision_with_list(
            self.player, self.coin_list
        )

        for coin in coin_hit_list:
            self.player.add_coin(random.randint(1, 3))
            coin.remove_from_sprite_lists()

        shield_hit_list = arcade.check_for_collision_with_list(
            self.player, self.shield_list
        )

        for shield in shield_hit_list:
            self.player.give_shield()
            shield.remove_from_sprite_lists()

        star_hit_list = arcade.check_for_collision_with_list(
            self.player, self.star_list
        )

        for star in star_hit_list:
            self.player.give_star()
            star.remove_from_sprite_lists()

        speed_hit_list2 = arcade.check_for_collision_with_list(
            self.player2, self.speed_particles
        )

        for particle in speed_hit_list2:
            self.player2.add_speed_particle()
            particle.remove_from_sprite_lists()

        bomb_hit_list2 = arcade.check_for_collision_with_list(
            self.player2, self.bomb_particles
        )

        for particle in bomb_hit_list2:
            self.player2.add_bomb_particle()
            particle.remove_from_sprite_lists()

        coin_hit_list2 = arcade.check_for_collision_with_list(
            self.player2, self.coin_list
        )

        for coin in coin_hit_list2:
            self.player2.add_coin(random.randint(1, 3))
            coin.remove_from_sprite_lists()

        shield_hit_list2 = arcade.check_for_collision_with_list(
            self.player2, self.shield_list
        )

        for shield in shield_hit_list2:
            self.player2.give_shield()
            shield.remove_from_sprite_lists()

        star_hit_list2 = arcade.check_for_collision_with_list(
            self.player2, self.star_list
        )

        for star in star_hit_list2:
            self.player2.give_star()
            star.remove_from_sprite_lists()

        self.check_star_kills()

    def check_star_kills(self):
        """Звезда убивает противника при касании"""
        if arcade.check_for_collision(self.player, self.player2):
            if self.player.has_star and self.player2.is_alive:
                if not self.player2.has_shield:
                    self.player2.take_damage(100)
                else:
                    self.player2.has_shield = False
                self.player.has_star = False

            elif self.player2.has_star and self.player.is_alive:
                if not self.player.has_shield:
                    self.player.take_damage(100)
                else:
                    self.player.has_shield = False
                self.player2.has_star = False

    def destroy_blocks(self, bomb):
        tile_size = self.tile_size
        bomb_cell_x = int(bomb.center_x // tile_size)
        bomb_cell_y = int(bomb.center_y // tile_size)

        current_radius = bomb.owner.explosion_radius

        directions = [
            (0, 0),
            (0, 1),
            (0, -1),
            (-1, 0),
            (1, 0)
        ]

        destroyed_blocks = False
        destroyed_cells = []

        for dx, dy in directions:
            check_x = bomb_cell_x + dx
            check_y = bomb_cell_y + dy

            blocked = False
            if dx != 0:
                step = 1 if dx > 0 else -1
                for i in range(1, abs(dx) + 1):
                    check_cell_x = bomb_cell_x + step * i
                    if self.check_collision_in_cell(check_cell_x, bomb_cell_y):
                        blocked = True
                        break
            elif dy != 0:
                step = 1 if dy > 0 else -1
                for i in range(1, abs(dy) + 1):
                    check_cell_y = bomb_cell_y + step * i
                    if self.check_collision_in_cell(bomb_cell_x, check_cell_y):
                        blocked = True
                        break

            if blocked:
                continue

            blocks_in_cell = self.get_blocks_in_cell(
                check_x, check_y, self.destructible_list)
            if blocks_in_cell:
                destroyed_cells.append((check_x, check_y))
                for block in blocks_in_cell:
                    block.remove_from_sprite_lists()
                    destroyed_blocks = True

            blocks_in_cell = self.get_blocks_in_cell(
                check_x, check_y, self.destroy_list)
            if blocks_in_cell:
                if (check_x, check_y) not in destroyed_cells:
                    destroyed_cells.append((check_x, check_y))
                for block in blocks_in_cell:
                    block.remove_from_sprite_lists()
                    destroyed_blocks = True

        for cell_x, cell_y in destroyed_cells:
            center_x = cell_x * tile_size + tile_size // 2
            center_y = cell_y * tile_size + tile_size // 2
            self.spawn_loot(center_x, center_y)

        return destroyed_blocks

    def draw_menu(self):
        self.clear()
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, arcade.color.DARK_SLATE_GRAY)

        arcade.draw_text("BOMBER GAME", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150,
                         arcade.color.YELLOW, 60, anchor_x="center", bold=True)

        if self.in_settings:
            self.draw_settings_menu()
        elif self.in_rules:
            self.draw_rules_menu()
        else:
            self.draw_main_menu()

    def draw_main_menu(self):
        arcade.draw_text("▼ ВЫБЕРИТЕ КАРТУ ▼", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 350,
                         arcade.color.LIGHT_CYAN, 36, anchor_x="center")

        if self.hover_button == 1:
            color1 = arcade.color.LIGHT_CORNFLOWER_BLUE
        else:
            color1 = arcade.color.LIGHT_BLUE

        left = 750
        right = 1150
        bottom = 485
        top = 565

        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, color1)
        arcade.draw_lrbt_rectangle_outline(
            left, right, bottom, top, arcade.color.WHITE, 3)
        arcade.draw_text("Карта 1", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                         arcade.color.WHITE, 28, anchor_x="center", anchor_y="center")

        if self.hover_button == 2:
            color2 = arcade.color.LIGHT_CORNFLOWER_BLUE
        else:
            color2 = arcade.color.LIGHT_BLUE

        bottom2 = 385
        top2 = 465

        arcade.draw_lrbt_rectangle_filled(left, right, bottom2, top2, color2)
        arcade.draw_lrbt_rectangle_outline(
            left, right, bottom2, top2, arcade.color.WHITE, 3)
        arcade.draw_text("Карта 2", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100,
                         arcade.color.WHITE, 28, anchor_x="center", anchor_y="center")

        if self.hover_button == 3:
            color3 = arcade.color.LIGHT_CORNFLOWER_BLUE
        else:
            color3 = arcade.color.LIGHT_BLUE

        bottom3 = 285
        top3 = 365

        arcade.draw_lrbt_rectangle_filled(left, right, bottom3, top3, color3)
        arcade.draw_lrbt_rectangle_outline(
            left, right, bottom3, top3, arcade.color.WHITE, 3)
        arcade.draw_text("Карта 3", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 200,
                         arcade.color.WHITE, 28, anchor_x="center", anchor_y="center")

        if self.hover_button == 4:
            settings_color = arcade.color.LIGHT_CORNFLOWER_BLUE
        else:
            settings_color = arcade.color.GRAY

        settings_left = SCREEN_WIDTH - 210
        settings_right = SCREEN_WIDTH - 35
        settings_bottom = 50
        settings_top = 120

        arcade.draw_lrbt_rectangle_filled(
            settings_left, settings_right, settings_bottom, settings_top, settings_color)
        arcade.draw_lrbt_rectangle_outline(
            settings_left, settings_right, settings_bottom, settings_top, arcade.color.WHITE, 3)
        arcade.draw_text("⚙️ НАСТРОЙКИ", SCREEN_WIDTH - 125, 85,
                         arcade.color.WHITE, 18, anchor_x="center", anchor_y="center")

    def draw_settings_menu(self):
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, (30, 30, 30, 200))

        window_width = 600
        window_height = 500
        left = SCREEN_WIDTH // 2 - window_width // 2
        right = SCREEN_WIDTH // 2 + window_width // 2
        bottom = SCREEN_HEIGHT // 2 - window_height // 2
        top = SCREEN_HEIGHT // 2 + window_height // 2

        arcade.draw_lrbt_rectangle_filled(
            left, right, bottom, top, arcade.color.DARK_SLATE_GRAY)
        arcade.draw_lrbt_rectangle_outline(
            left, right, bottom, top, arcade.color.WHITE, 4)

        arcade.draw_text("НАСТРОЙКИ", SCREEN_WIDTH // 2, top - 50,
                         arcade.color.YELLOW, 40, anchor_x="center", bold=True)

        sound_y = top - 130
        if self.hover_settings_button == 1:
            sound_color = arcade.color.LIGHT_CORNFLOWER_BLUE
        else:
            sound_color = arcade.color.LIGHT_BLUE

        arcade.draw_lrbt_rectangle_filled(
            left + 50, right - 50, sound_y - 30, sound_y + 30, sound_color)
        arcade.draw_lrbt_rectangle_outline(
            left + 50, right - 50, sound_y - 30, sound_y + 30, arcade.color.WHITE, 2)

        sound_text = f"🔊 Звук: {'ВКЛ' if self.sound_enabled else 'ВЫКЛ'}"
        arcade.draw_text(sound_text, SCREEN_WIDTH // 2, sound_y,
                         arcade.color.WHITE, 24, anchor_x="center", anchor_y="center")

        rules_y = top - 210
        if self.hover_settings_button == 2:
            rules_color = arcade.color.LIGHT_CORNFLOWER_BLUE
        else:
            rules_color = arcade.color.LIGHT_BLUE

        arcade.draw_lrbt_rectangle_filled(
            left + 50, right - 50, rules_y - 30, rules_y + 30, rules_color)
        arcade.draw_lrbt_rectangle_outline(
            left + 50, right - 50, rules_y - 30, rules_y + 30, arcade.color.WHITE, 2)

        arcade.draw_text("📖 ПРАВИЛА ИГРЫ", SCREEN_WIDTH // 2, rules_y,
                         arcade.color.WHITE, 24, anchor_x="center", anchor_y="center")

        back_y = bottom + 50
        if self.hover_settings_button == 3:
            back_color = arcade.color.LIGHT_CORNFLOWER_BLUE
        else:
            back_color = arcade.color.LIGHT_BLUE

        arcade.draw_lrbt_rectangle_filled(
            left + 50, right - 50, back_y - 30, back_y + 30, back_color)
        arcade.draw_lrbt_rectangle_outline(
            left + 50, right - 50, back_y - 30, back_y + 30, arcade.color.WHITE, 2)

        arcade.draw_text("НАЗАД", SCREEN_WIDTH // 2, back_y,
                         arcade.color.WHITE, 24, anchor_x="center", anchor_y="center")

    def draw_rules_menu(self):
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, (30, 30, 30, 200))

        window_width = 1000
        window_height = 750
        left = SCREEN_WIDTH // 2 - window_width // 2
        right = SCREEN_WIDTH // 2 + window_width // 2
        bottom = SCREEN_HEIGHT // 2 - window_height // 2
        top = SCREEN_HEIGHT // 2 + window_height // 2

        arcade.draw_lrbt_rectangle_filled(
            left, right, bottom, top, arcade.color.DARK_SLATE_GRAY)
        arcade.draw_lrbt_rectangle_outline(
            left, right, bottom, top, arcade.color.WHITE, 4)

        arcade.draw_text("ПРАВИЛА ИГРЫ", SCREEN_WIDTH // 2, top - 50,
                         arcade.color.YELLOW, 40, anchor_x="center", bold=True)

        rules_text = [
            "🎮 УПРАВЛЕНИЕ:",
            "Игрок 1 (фиолетовый): WASD - движение, ПРОБЕЛ - бомба",
            "Игрок 2 (зеленый): Стрелки - движение, ENTER - бомба",
            "Esc - выход в меню/шаг назад в меню",
            "",
            "💣 ИГРОВЫЕ МЕХАНИКИ:",
            "• Бомбы взрываются через 2 секунды",
            "• Взрыв уничтожает блоки и игроков",
            "• Нельзя ставить бомбу на другую бомбу",
            "",
            "⭐ УЛУЧШЕНИЯ:",
            "🔵 Синие частицы - увеличивают скорость (каждые 5 шт)",
            "🔴 Красные частицы - увеличивают кол-во бомб (каждые 8 шт)",
            "🛡️ Щит - защищает от одного попадания",
            "⭐ Звезда - убивает врага при касании",
            "💰 Монеты - просто для счета",
            "",
            "⏸️ Пауза - кнопка в левом верхнем углу",
            "",
            "Цель игры - уничтожить противника!"
        ]

        y_offset = top - 120
        for line in rules_text:
            if line.startswith("🎮") or line.startswith("💣") or line.startswith("⭐") or line.startswith("Цель"):
                color = arcade.color.YELLOW
                size = 20
            elif line == "":
                y_offset -= 20
                continue
            else:
                color = arcade.color.WHITE
                size = 18

            arcade.draw_text(line, SCREEN_WIDTH // 2, y_offset,
                             color, size, anchor_x="center")
            y_offset -= 30

        back_y = bottom + 50
        if self.hover_settings_button == 4:
            back_color = arcade.color.LIGHT_CORNFLOWER_BLUE
        else:
            back_color = arcade.color.LIGHT_BLUE

        arcade.draw_lrbt_rectangle_filled(
            left + 50, right - 50, back_y - 30, back_y + 30, back_color)
        arcade.draw_lrbt_rectangle_outline(
            left + 50, right - 50, back_y - 30, back_y + 30, arcade.color.WHITE, 2)

        arcade.draw_text("НАЗАД", SCREEN_WIDTH // 2, back_y,
                         arcade.color.WHITE, 24, anchor_x="center", anchor_y="center")

    def draw_game(self):
        self.clear()
        arcade.set_background_color(arcade.color.ASH_GREY)
        self.Background_list.draw()
        self.Indestructible_list.draw()
        self.destructible_list.draw()
        self.destroy_list.draw()

        self.coin_list.draw()
        self.speed_particles.draw()
        self.bomb_particles.draw()
        self.shield_list.draw()
        self.star_list.draw()
        self.bomb_list.draw()
        self.player_list.draw()
        self.pause_button.draw()

        if self.player.has_shield:
            arcade.draw_circle_outline(
                self.player.center_x, self.player.center_y, 40,
                arcade.color.BLUE, 3
            )

        if self.player.has_star:
            arcade.draw_circle_outline(
                self.player.center_x, self.player.center_y, 45,
                arcade.color.ORANGE, 4
            )

        if self.player2.has_shield:
            arcade.draw_circle_outline(
                self.player2.center_x, self.player2.center_y, 40,
                arcade.color.BLUE, 3
            )

        if self.player2.has_star:
            arcade.draw_circle_outline(
                self.player2.center_x, self.player2.center_y, 45,
                arcade.color.ORANGE, 4
            )

        if self.show_explosion:
            alpha = int(255 * (1 - self.explosion_time / 0.5))
            tile_size = self.tile_size
            bomb_col = int(self.explosion_x // tile_size)
            bomb_row = int(self.explosion_y // tile_size)

            directions = [(0, 0), (0, 1), (0, -1), (-1, 0), (1, 0)]
            for dx, dy in directions:
                cell_x = bomb_col + dx
                cell_y = bomb_row + dy
                cell_left = cell_x * tile_size
                cell_right = cell_left + tile_size
                cell_bottom = cell_y * tile_size
                cell_top = cell_bottom + tile_size

                arcade.draw_lrbt_rectangle_filled(
                    cell_left, cell_right, cell_bottom, cell_top,
                    (255, 0, 0, alpha // 3)
                )

        if self.game_paused:
            arcade.draw_lrbt_rectangle_filled(
                0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
                (0, 0, 0, 128)
            )

            arcade.draw_text(
                "ПАУЗА",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2,
                arcade.color.YELLOW,
                80,
                anchor_x="center",
                anchor_y="center",
                bold=True
            )

        start_x = SCREEN_WIDTH - 250
        start_y = SCREEN_HEIGHT - 50

        arcade.draw_lrbt_rectangle_filled(
            start_x - 10, SCREEN_WIDTH - 10, start_y - 210, start_y + 30,
            (50, 50, 50, 200)
        )
        arcade.draw_lrbt_rectangle_outline(
            start_x - 10, SCREEN_WIDTH - 10, start_y - 210, start_y + 30,
            arcade.color.PURPLE, 2
        )

        arcade.draw_text(
            "Игрок 1 (фиолетовый)",
            start_x, start_y,
            arcade.color.PURPLE, 20
        )

        arcade.draw_text(
            f"Бомбы: {self.player.active_bombs}/{self.player.bomb_limit}",
            start_x, start_y - 30,
            arcade.color.WHITE, 18
        )

        arcade.draw_text(
            f"Скорость: x{self.player.speed_multiplier:.1f}",
            start_x, start_y - 60,
            arcade.color.WHITE, 18
        )

        arcade.draw_text(
            f"⚡: {self.player.speed_particles}",
            start_x, start_y - 90,
            arcade.color.LIGHT_BLUE, 16
        )

        arcade.draw_text(
            f"💣: {self.player.bomb_particles}",
            start_x, start_y - 115,
            arcade.color.LIGHT_CORAL, 16
        )

        arcade.draw_text(
            f"💰: {self.player.coins}",
            start_x, start_y - 145,
            arcade.color.GOLD, 18
        )

        if self.player.has_shield:
            shield_time = max(0, self.player.shield_end_time - time.time())
            arcade.draw_text(
                f"🛡️: {shield_time:.1f}с",
                start_x, start_y - 175,
                arcade.color.LIGHT_BLUE, 16
            )

        if self.player.has_star:
            star_time = max(0, self.player.star_end_time - time.time())
            arcade.draw_text(
                f"⭐: {star_time:.1f}с",
                start_x, start_y - 200,
                arcade.color.YELLOW_ORANGE, 16
            )

        start_x2 = SCREEN_WIDTH - 250
        start_y2 = 200

        arcade.draw_lrbt_rectangle_filled(
            start_x2 - 10, SCREEN_WIDTH - 10, start_y2 - 210, start_y2 + 30,
            (50, 50, 50, 200)
        )
        arcade.draw_lrbt_rectangle_outline(
            start_x2 - 10, SCREEN_WIDTH - 10, start_y2 - 210, start_y2 + 30,
            arcade.color.GREEN, 2
        )

        arcade.draw_text(
            "Игрок 2 (зеленый)",
            start_x2, start_y2,
            arcade.color.GREEN, 20
        )

        arcade.draw_text(
            f"Бомбы: {self.player2.active_bombs}/{self.player2.bomb_limit}",
            start_x2, start_y2 - 30,
            arcade.color.WHITE, 18
        )

        arcade.draw_text(
            f"Скорость: x{self.player2.speed_multiplier:.1f}",
            start_x2, start_y2 - 60,
            arcade.color.WHITE, 18
        )

        arcade.draw_text(
            f"⚡: {self.player2.speed_particles}",
            start_x2, start_y2 - 90,
            arcade.color.LIGHT_BLUE, 16
        )

        arcade.draw_text(
            f"💣: {self.player2.bomb_particles}",
            start_x2, start_y2 - 115,
            arcade.color.LIGHT_CORAL, 16
        )

        arcade.draw_text(
            f"💰: {self.player2.coins}",
            start_x2, start_y2 - 145,
            arcade.color.GOLD, 18
        )

        if self.player2.has_shield:
            shield_time2 = max(0, self.player2.shield_end_time - time.time())
            arcade.draw_text(
                f"🛡️: {shield_time2:.1f}с",
                start_x2, start_y2 - 175,
                arcade.color.LIGHT_BLUE, 16
            )

        if self.player2.has_star:
            star_time2 = max(0, self.player2.star_end_time - time.time())
            arcade.draw_text(
                f"⭐: {star_time2:.1f}с",
                start_x2, start_y2 - 200,
                arcade.color.YELLOW_ORANGE, 16
            )

        if not self.player.is_alive or not self.player2.is_alive:
            if not self.player.is_alive and not self.player2.is_alive:
                winner_text = "НИЧЬЯ! Оба игрока погибли!"
                rect_color = (100, 100, 100, 220)
                text_color = arcade.color.LIGHT_GRAY
            elif not self.player.is_alive:
                winner_text = "ПОБЕДИТЕЛЬ: Игрок 2 (зеленый)!"
                rect_color = (0, 150, 0, 220)
                text_color = arcade.color.LIME_GREEN
            else:
                winner_text = "ПОБЕДИТЕЛЬ: Игрок 1 (фиолетовый)!"
                rect_color = (150, 0, 150, 220)
                text_color = arcade.color.VIOLET

            rect_width = 1100
            rect_height = 200
            rect_x = SCREEN_WIDTH // 2 - rect_width // 2
            rect_y = SCREEN_HEIGHT // 2 - rect_height // 2

            arcade.draw_lrbt_rectangle_filled(
                rect_x, rect_x + rect_width, rect_y, rect_y + rect_height,
                rect_color
            )

            arcade.draw_lrbt_rectangle_outline(
                rect_x, rect_x + rect_width, rect_y, rect_y + rect_height,
                arcade.color.WHITE, 4
            )

            arcade.draw_text(
                winner_text,
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30,
                text_color, 50, anchor_x="center", bold=True
            )

            arcade.draw_text(
                "Нажмите R для рестарта",
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                arcade.color.YELLOW, 35, anchor_x="center"
            )

    def on_draw(self):
        if self.in_menu:
            self.draw_menu()
        else:
            self.draw_game()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.in_menu and button == arcade.MOUSE_BUTTON_LEFT:
            if self.in_settings:
                window_width = 600
                window_height = 500
                left = SCREEN_WIDTH // 2 - window_width // 2
                right = SCREEN_WIDTH // 2 + window_width // 2
                bottom = SCREEN_HEIGHT // 2 - window_height // 2
                top = SCREEN_HEIGHT // 2 + window_height // 2

                sound_y = top - 130
                rules_y = top - 210
                back_y = bottom + 50

                if left + 50 <= x <= right - 50 and sound_y - 30 <= y <= sound_y + 30:
                    self.sound_enabled = not self.sound_enabled
                    self.db.set(self.sound_enabled)

                elif left + 50 <= x <= right - 50 and rules_y - 30 <= y <= rules_y + 30:
                    self.in_rules = True
                    self.in_settings = False

                elif left + 50 <= x <= right - 50 and back_y - 30 <= y <= back_y + 30:
                    self.in_settings = False

            elif self.in_rules:
                window_width = 1000
                window_height = 750
                left = SCREEN_WIDTH // 2 - window_width // 2
                right = SCREEN_WIDTH // 2 + window_width // 2
                bottom = SCREEN_HEIGHT // 2 - window_height // 2
                top = SCREEN_HEIGHT // 2 + window_height // 2

                back_y = bottom + 50

                if left + 50 <= x <= right - 50 and back_y - 30 <= y <= back_y + 30:
                    self.in_rules = False
                    self.in_settings = True

            else:
                if 750 <= x <= 1150:
                    if 485 <= y <= 565:
                        self.in_menu = False
                        self.setup(0)
                    elif 385 <= y <= 465:
                        self.in_menu = False
                        self.setup(1)
                    elif 285 <= y <= 365:
                        self.in_menu = False
                        self.setup(2)

                settings_left = SCREEN_WIDTH - 200
                settings_right = SCREEN_WIDTH - 50
                settings_bottom = 50
                settings_top = 120

                if settings_left <= x <= settings_right and settings_bottom <= y <= settings_top:
                    self.in_settings = True

        elif button == arcade.MOUSE_BUTTON_LEFT:
            if self.pause_button.check_click(x, y):
                self.game_paused = self.pause_button.is_paused

    def on_mouse_motion(self, x, y, dx, dy):
        if not self.in_menu:
            return

        self.hover_button = 0
        self.hover_settings_button = 0

        if self.in_settings:
            window_width = 600
            window_height = 500
            left = SCREEN_WIDTH // 2 - window_width // 2
            right = SCREEN_WIDTH // 2 + window_width // 2
            bottom = SCREEN_HEIGHT // 2 - window_height // 2
            top = SCREEN_HEIGHT // 2 + window_height // 2

            sound_y = top - 130
            rules_y = top - 210
            back_y = bottom + 50

            if left + 50 <= x <= right - 50:
                if sound_y - 30 <= y <= sound_y + 30:
                    self.hover_settings_button = 1
                elif rules_y - 30 <= y <= rules_y + 30:
                    self.hover_settings_button = 2
                elif back_y - 30 <= y <= back_y + 30:
                    self.hover_settings_button = 3

        elif self.in_rules:
            window_width = 1000
            window_height = 750
            left = SCREEN_WIDTH // 2 - window_width // 2
            right = SCREEN_WIDTH // 2 + window_width // 2
            bottom = SCREEN_HEIGHT // 2 - window_height // 2
            top = SCREEN_HEIGHT // 2 + window_height // 2

            back_y = bottom + 50

            if left + 50 <= x <= right - 50 and back_y - 30 <= y <= back_y + 30:
                self.hover_settings_button = 4

        else:
            if 750 <= x <= 1150:
                if 485 <= y <= 565:
                    self.hover_button = 1
                elif 385 <= y <= 465:
                    self.hover_button = 2
                elif 285 <= y <= 365:
                    self.hover_button = 3

            settings_left = SCREEN_WIDTH - 200
            settings_right = SCREEN_WIDTH - 50
            settings_bottom = 50
            settings_top = 120

            if settings_left <= x <= settings_right and settings_bottom <= y <= settings_top:
                self.hover_button = 4

    def on_key_press(self, key, modifiers):
        if self.in_menu:
            if key == arcade.key.KEY_1:
                self.in_menu = False
                self.setup(0)
            elif key == arcade.key.KEY_2:
                self.in_menu = False
                self.setup(1)
            elif key == arcade.key.KEY_3:
                self.in_menu = False
                self.setup(2)
            elif key == arcade.key.ESCAPE:
                if self.in_rules:
                    self.in_rules = False
                    self.in_settings = True
                elif self.in_settings:
                    self.in_settings = False
                else:
                    arcade.close_window()

        else:
            if self.game_paused:
                self.sound_enabled = False
                return

            if key == arcade.key.ESCAPE:
                if self.music_player is not None:
                    arcade.stop_sound(self.music_player)
                self.in_menu = True
                self.in_settings = False
                self.in_rules = False

            elif key == arcade.key.SPACE and self.player.is_alive:
                bomb = self.player.place_bomb()
                if bomb:
                    print("💣 [Игрок 1] Бомба поставлена!")
            elif key == arcade.key.ENTER and self.player2.is_alive:
                bomb = self.player2.place_bomb()
                if bomb:
                    print("💣 [Игрок 2] Бомба поставлена!")

            elif key == arcade.key.R:
                if self.music_player is not None:
                    arcade.stop_sound(self.music_player)
                self.setup(self.current_map)

            else:
                self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

    def on_update(self, delta_time):
        if self.in_menu:
            return

        if self.game_paused:
            return

        if not self.player.is_alive or not self.player2.is_alive:
            if self.death_time == 0:
                self.death_time = time.time()
                if not self.player.is_alive and not self.player2.is_alive:
                    print("🎮 Оба игрока погибли! Игра окончена!")
                elif not self.player.is_alive:
                    print("🎮 Игрок 1 погиб! Игра окончена!")
                else:
                    print("🎮 Игрок 2 погиб! Игра окончена!")
            return

        self.player_list.update(delta_time, self.keys_pressed)
        self.player.update_animation(delta_time)
        self.player2.update_animation(delta_time)

        self.bomb_list.update(delta_time)
        self.speed_particles.update(delta_time)
        self.bomb_particles.update(delta_time)
        self.coin_list.update(delta_time)
        self.shield_list.update(delta_time)
        self.star_list.update(delta_time)

        self.check_collisions()

        bombs_to_remove = []
        active_bombs1 = 0
        active_bombs2 = 0

        for bomb in self.bomb_list:
            if bomb.owner == self.player and not bomb.has_exploded:
                active_bombs1 += 1
            elif bomb.owner == self.player2 and not bomb.has_exploded:
                active_bombs2 += 1

            if bomb.has_exploded:
                self.show_explosion = True
                self.explosion_time = 0
                self.explosion_x = bomb.center_x
                self.explosion_y = bomb.center_y

                self.destroy_blocks(bomb)

                if bomb.owner == self.player or bomb.owner == self.player2:
                    if self.is_player_in_explosion_radius(bomb.center_x, bomb.center_y, self.player, bomb.owner):
                        self.player.take_damage(100)

                    if self.is_player_in_explosion_radius(bomb.center_x, bomb.center_y, self.player2, bomb.owner):
                        self.player2.take_damage(100)

                bombs_to_remove.append(bomb)

        self.player.active_bombs = active_bombs1
        self.player2.active_bombs = active_bombs2

        for bomb in bombs_to_remove:
            bomb.remove_from_sprite_lists()

        if self.show_explosion:
            self.explosion_time += delta_time
            if self.explosion_time >= 0.5:
                self.show_explosion = False


def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()

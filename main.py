import arcade
import math
import time

# Задаём размер окна
SCREEN_WIDTH = 1900
SCREEN_HEIGHT = 1050
RESIZABLE = True
SCREEN_TITLE = "Bomber"

class Bomb(arcade.Sprite):
    def __init__(self, x, y, explosion_time=2.0):
        super().__init__()
        
        self.scale = 0.4
        self.center_x = x
        self.center_y = y
        self.explosion_time = explosion_time
        self.placed_time = time.time()
        self.has_exploded = False
        
        self.radius = 15
        self.color = arcade.color.BLACK
        
    def draw(self):
        arcade.draw_circle_filled(self.center_x, self.center_y, self.radius, self.color)
        
    def update(self):
        if not self.has_exploded and time.time() - self.placed_time >= self.explosion_time:
            self.has_exploded = True

class Hero(arcade.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        
        self.scale = 0.5
        self.hero_speed = 300
        self.health = 100
        self.bomb_limit = 1
        self.bombs_placed = 0
        self.last_bomb_time = 0
        self.bomb_cooldown = 2.0
        self.idle_texture = arcade.load_texture("assets/Plaer1_purple/idle.png")
        self.texture = self.idle_texture

        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2
        self.walk_textures = []
        for i in range(1, 5):
            texture = arcade.load_texture(f"assets/Plaer1_purple/walk{i}.png")
            self.walk_textures.append(texture)

        self.current_texture = 0
        self.texture_change_time = 0
        self.texture_change_delay = 0.1
        self.is_walking = False

    def update_animation(self, delta_time: float = 1/60):
        if self.is_walking:
            self.texture_change_time += delta_time
            if self.texture_change_time >= self.texture_change_delay:
                self.texture_change_time = 0
                self.current_texture += 1
                if self.current_texture >= len(self.walk_textures):
                    self.current_texture = 0
                self.texture = self.walk_textures[self.current_texture]
        else:
            self.texture = self.idle_texture
            
    def update(self, delta_time, keys_pressed):
        dx, dy = 0, 0
        if arcade.key.A in keys_pressed:
            dx -= self.hero_speed * delta_time
        if arcade.key.D in keys_pressed:
            dx += self.hero_speed * delta_time
        if arcade.key.W in keys_pressed:
            dy += self.hero_speed * delta_time
        if arcade.key.S in keys_pressed:
            dy -= self.hero_speed * delta_time
            
        if dx != 0 and dy != 0:
            factor = 0.7071
            dx *= factor
            dy *= factor

        self.center_x += dx
        self.center_y += dy
        
        margin_x = 30
        margin_y = 20
        
        self.center_x = max(margin_x, min(SCREEN_WIDTH - margin_x, self.center_x))
        self.center_y = max(margin_y, min(SCREEN_HEIGHT - margin_y, self.center_y))
        self.is_walking = dx != 0 or dy != 0
        
    def can_place_bomb(self):
        current_time = time.time()
        time_since_last_bomb = current_time - self.last_bomb_time
        
        can_place = (self.bombs_placed < self.bomb_limit and 
                    time_since_last_bomb >= self.bomb_cooldown)
        
        return can_place
        
    def place_bomb(self):
        if not self.can_place_bomb():
            return None
            
        tile_size = self.game.tile_size
        
        player_cell_x = int(self.center_x // tile_size)
        player_cell_y = int(self.center_y // tile_size)
        
        bomb_x = player_cell_x * tile_size + tile_size // 2
        bomb_y = player_cell_y * tile_size + tile_size // 2
        
        for existing_bomb in self.game.bomb_list:
            existing_cell_x = int(existing_bomb.center_x // tile_size)
            existing_cell_y = int(existing_bomb.center_y // tile_size)
            if player_cell_x == existing_cell_x and player_cell_y == existing_cell_y:
                return None
        
        bomb = Bomb(bomb_x, bomb_y, explosion_time=1.0)
        self.game.bomb_list.append(bomb)
        self.bombs_placed += 1
        self.last_bomb_time = time.time()
        
        return bomb

class MyGame(arcade.Window):
    def __init__(self, width, height, title, resizable=False):
        super().__init__(width, height, title, resizable)
        arcade.set_background_color(arcade.color.ASH_GREY)
        self.keys_pressed = set()
        
        self.explosion_time = 0
        self.show_explosion = False
        self.explosion_x = 0
        self.explosion_y = 0
        self.tile_size = 70
        self.explosion_radius = 1  # Радиус 1 клетка

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.bomb_list = []
        
        map_name = "gg.tmx"
        TILE_SCALING = 1.0
        tile_map = arcade.load_tilemap(map_name, scaling=TILE_SCALING)

        self.Indestructible_list = tile_map.sprite_lists["Indestructible"]
        self.destructible_list = tile_map.sprite_lists["destructible"]
        self.Background_list = tile_map.sprite_lists["Background"]
        self.collision_list = tile_map.sprite_lists["Colision"]
        self.destroy_list = tile_map.sprite_lists["Destroy"]
        
        self.player = Hero(self)
        self.player.center_x = 70
        self.player.center_y = 980
        self.player_list.append(self.player)

        print(f"Карта загружена. Размер клетки: {self.tile_size}")
        
        self.create_physics_engines()
    
    def create_physics_engines(self):
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.collision_list,
        )
        
        self.physics_engine2 = arcade.PhysicsEngineSimple(
            self.player, self.destroy_list,
        )
    
    def check_block_in_cell(self, cell_x, cell_y, sprite_list):
        """Проверяет есть ли блок в указанной клетке"""
        for sprite in sprite_list:
            sprite_cell_x = int(sprite.center_x // self.tile_size)
            sprite_cell_y = int(sprite.center_y // self.tile_size)
            if sprite_cell_x == cell_x and sprite_cell_y == cell_y:
                return True
        return False
    
    def get_blocks_in_cell(self, cell_x, cell_y, sprite_list):
        """Возвращает все блоки в указанной клетке"""
        blocks = []
        for sprite in sprite_list:
            sprite_cell_x = int(sprite.center_x // self.tile_size)
            sprite_cell_y = int(sprite.center_y // self.tile_size)
            if sprite_cell_x == cell_x and sprite_cell_y == cell_y:
                blocks.append(sprite)
        return blocks
    
    def on_draw(self):
        self.clear()
        
        self.Background_list.draw() 
        self.Indestructible_list.draw()
        self.destructible_list.draw()
        self.destroy_list.draw()
        self.player_list.draw()
        
        for bomb in self.bomb_list:
            bomb.draw()
            
        if self.show_explosion:
            alpha = int(255 * (1 - self.explosion_time / 0.5))
            color = (255, 0, 0, alpha)
            
            tile_size = self.tile_size
            bomb_col = int(self.explosion_x // tile_size)
            bomb_row = int(self.explosion_y // tile_size)
            
            # Визуализация взрыва крестом с радиусом 1
            directions = [
                (0, 0),    # центр
                (0, 1),    # вверх
                (0, -1),   # вниз
                (-1, 0),   # влево
                (1, 0)     # вправо
            ]
            
            for dx, dy in directions:
                cell_x = bomb_col + dx
                cell_y = bomb_row + dy
                
                cell_left = cell_x * tile_size
                cell_right = cell_left + tile_size
                cell_bottom = cell_y * tile_size
                cell_top = cell_bottom + tile_size
                
                # Полупрозрачный прямоугольник для каждой пораженной клетки
                arcade.draw_lrbt_rectangle_filled(
                    cell_left, cell_right, cell_bottom, cell_top,
                    (255, 0, 0, alpha // 3)
                )
            
        current_time = time.time()
        time_since_last_bomb = current_time - self.player.last_bomb_time
        cooldown_remaining = max(0, self.player.bomb_cooldown - time_since_last_bomb)
        
        arcade.draw_text(f"Бомбы: {self.player.bomb_limit - self.player.bombs_placed}/{self.player.bomb_limit}", 
                       20, SCREEN_HEIGHT - 50,
                       arcade.color.WHITE, 24)
        
        if cooldown_remaining > 0:
            arcade.draw_text(f"Кулдаун: {cooldown_remaining:.1f}с", 
                           SCREEN_WIDTH - 200, SCREEN_HEIGHT - 50,
                           arcade.color.RED, 20)
        else:
            arcade.draw_text("Бомба готова", 
                           SCREEN_WIDTH - 200, SCREEN_HEIGHT - 50,
                           arcade.color.GREEN, 20)
            
        tile_size = self.tile_size
        player_cell_x = int(self.player.center_x // tile_size)
        player_cell_y = int(self.player.center_y // tile_size)
        arcade.draw_text(f"Клетка: ({player_cell_x}, {player_cell_y})", 
                       SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 50,
                       arcade.color.YELLOW, 20)
        
    def on_update(self, delta_time):
        self.player_list.update(delta_time, self.keys_pressed)
        self.player.update_animation()
        
        bombs_to_remove = []
        
        for bomb in self.bomb_list:
            bomb.update()
            
            if bomb.has_exploded:
                self.show_explosion = True
                self.explosion_time = 0
                self.explosion_x = bomb.center_x
                self.explosion_y = bomb.center_y
                
                # Находим блоки в радиусе взрыва
                tile_size = self.tile_size
                bomb_col = int(bomb.center_x // tile_size)
                bomb_row = int(bomb.center_y // tile_size)
                
                print(f"\n=== ВЗРЫВ БОМБЫ ===")
                print(f"Клетка бомбы: ({bomb_col}, {bomb_row})")
                print(f"Радиус взрыва: {self.explosion_radius} клетка")
                
                # Направления взрыва: центр и 4 стороны
                directions = [
                    (0, 0, "центр"),    # центр
                    (0, 1, "вверх"),    # вверх
                    (0, -1, "вниз"),    # вниз
                    (-1, 0, "влево"),   # влево
                    (1, 0, "вправо")    # вправо
                ]
                
                # Ищем блоки для удаления
                destructible_to_remove = []
                destroy_to_remove = []
                
                for dx, dy, direction in directions:
                    check_x = bomb_col + dx
                    check_y = bomb_row + dy
                    
                    # Пропускаем направления дальше радиуса 1
                    if abs(dx) + abs(dy) > self.explosion_radius:
                        continue
                    
                    # Проверяем, не блокирует ли путь непроходимый блок
                    # (только для направлений кроме центра)
                    if dx != 0 or dy != 0:
                        # Проверяем все клетки между бомбой и целевой клеткой
                        blocked = False
                        if dx != 0:  # горизонтальное направление
                            step = 1 if dx > 0 else -1
                            for i in range(1, abs(dx) + 1):
                                check_cell_x = bomb_col + step * i
                                # Проверяем непроходимые блоки в коллизиях
                                if self.check_block_in_cell(check_cell_x, bomb_row, self.collision_list):
                                    print(f"Направление {direction} заблокировано непроходимым блоком в ({check_cell_x}, {bomb_row})")
                                    blocked = True
                                    break
                        elif dy != 0:  # вертикальное направление
                            step = 1 if dy > 0 else -1
                            for i in range(1, abs(dy) + 1):
                                check_cell_y = bomb_row + step * i
                                # Проверяем непроходимые блоки в коллизиях
                                if self.check_block_in_cell(bomb_col, check_cell_y, self.collision_list):
                                    print(f"Направление {direction} заблокировано непроходимым блоком в ({bomb_col}, {check_cell_y})")
                                    blocked = True
                                    break
                        
                        if blocked:
                            continue  # Пропускаем это направление
                    
                    # Ищем destructible блоки в этой клетке
                    blocks = self.get_blocks_in_cell(check_x, check_y, self.destructible_list)
                    for block in blocks:
                        if block not in destructible_to_remove:
                            destructible_to_remove.append(block)
                            print(f"Найден destructible блок в направлении {direction} ({check_x}, {check_y})")
                    
                    # Ищем Destroy блоки в этой клетке
                    blocks = self.get_blocks_in_cell(check_x, check_y, self.destroy_list)
                    for block in blocks:
                        if block not in destroy_to_remove:
                            destroy_to_remove.append(block)
                            print(f"Найден Destroy блок в направлении {direction} ({check_x}, {check_y})")
                
                # Удаляем найденные блоки
                for sprite in destructible_to_remove:
                    if sprite in self.destructible_list:
                        self.destructible_list.remove(sprite)
                
                for sprite in destroy_to_remove:
                    if sprite in self.destroy_list:
                        self.destroy_list.remove(sprite)
                
                print(f"Уничтожено: {len(destructible_to_remove)} destructible, {len(destroy_to_remove)} Destroy")
                print(f"=== КОНЕЦ ВЗРЫВА ===\n")
                
                bombs_to_remove.append(bomb)
                self.player.bombs_placed -= 1
        
        # Удаляем взорвавшиеся бомбы
        for bomb in bombs_to_remove:
            if bomb in self.bomb_list:
                self.bomb_list.remove(bomb)
        
        # Обновляем физические движки, если были удалены блоки
        if bombs_to_remove:
            self.create_physics_engines()
        
        if self.show_explosion:
            self.explosion_time += delta_time
            if self.explosion_time >= 0.5:
                self.show_explosion = False
        
        if self.physics_engine:
            self.physics_engine.update()
        if self.physics_engine2:
            self.physics_engine2.update()
            
    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)
        
        if key == arcade.key.SPACE:
            self.player.place_bomb()

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()
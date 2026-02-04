import arcade
import math
import time
import random
import os

# Задаём размер окна
SCREEN_WIDTH = 1900
SCREEN_HEIGHT = 1050
RESIZABLE = True
SCREEN_TITLE = "Bomber"

class PowerUp(arcade.Sprite):
    """Класс усиления, которое выпадает из блоков"""

    # Типы усилений
    TYPE_BOMB_COUNT = "bomb_count"    # +1 бомба
    TYPE_EXPLOSION_RADIUS = "radius"  # +1 радиус взрыва
    TYPE_SPEED_BOOST = "speed"        # +20% скорости

    def __init__(self, x, y, power_type):
        # Определяем текстуру в зависимости от типа
        texture_path = ""
        if power_type == self.TYPE_BOMB_COUNT:
            texture_path = "assets/PowerUps/bomb_up.png"
        elif power_type == self.TYPE_EXPLOSION_RADIUS:
            texture_path = "assets/PowerUps/fire_up.png"
        elif power_type == self.TYPE_SPEED_BOOST:
            texture_path = "assets/PowerUps/speed_up.png"

        # Если текстуры нет, используем placeholder
        try:
            if os.path.exists(texture_path):
                super().__init__(texture_path, scale=0.6)
            else:
                raise FileNotFoundError(f"Файл {texture_path} не найден")
        except:
            # Создаем цветной квадрат как placeholder
            super().__init__(center_x=x, center_y=y)
            if power_type == self.TYPE_BOMB_COUNT:
                color = arcade.color.BLUE
            elif power_type == self.TYPE_EXPLOSION_RADIUS:
                color = arcade.color.RED
            else:
                color = arcade.color.GREEN
            self.texture = arcade.make_soft_square_texture(40, color, center_alpha=255)
            self.scale = 1.0

        self.center_x = x
        self.center_y = y
        self.power_type = power_type

        # Анимация парения
        self.float_timer = 0
        self.float_speed = 1.0
        self.spawn_time = time.time()

    def update(self, delta_time: float = 1/60):
        """Анимация парения усиления"""
        self.float_timer += delta_time * self.float_speed
        # Плавное движение вверх-вниз
        self.center_y += math.sin(self.float_timer) * 0.1

class Bomb(arcade.Sprite):
    def __init__(self, x, y, explosion_time=2.0):
        super().__init__()

        # Пробуем загрузить текстуры бомбы
        try:
            # Проверяем существование файлов
            if os.path.exists("assets/Bomb/bomb.png"):
                self.bomb_texture = arcade.load_texture("assets/Bomb/bomb.png")
                if os.path.exists("assets/Bomb/bomb1.png"):
                    self.bomb_texture2 = arcade.load_texture("assets/Bomb/bomb1.png")
                    self.has_two_textures = True
                else:
                    self.has_two_textures = False
                self.texture = self.bomb_texture
                self.scale = 0.8
            else:
                raise FileNotFoundError("Файлы бомбы не найдены")
        except Exception as e:
            # Создаем текстуру круга вручную
            SIZE = 50
            image = arcade.create_image(SIZE, SIZE, color=(0, 0, 0, 0))
            with image.ctx:
                arcade.draw_circle_filled(SIZE//2, SIZE//2, SIZE//2 - 2, arcade.color.BLACK)
                arcade.draw_circle_filled(SIZE//2, SIZE//2, SIZE//2 - 5, arcade.color.DARK_GRAY)
                arcade.draw_circle_filled(SIZE//2, SIZE//2, SIZE//2 - 10, arcade.color.RED)

            self.texture = image.texture
            self.has_two_textures = False
            self.scale = 1.0

        self.center_x = x
        self.center_y = y
        self.explosion_time = explosion_time
        self.placed_time = time.time()
        self.has_exploded = False

        # Параметры мигания
        self.blink_interval = 0.3
        self.blink_timer = 0

    def update(self, delta_time: float = 1/60):
        """Обновление состояния бомбы с миганием"""
        current_time = time.time()
        time_since_placed = current_time - self.placed_time

        # Проверка взрыва
        if not self.has_exploded and time_since_placed >= self.explosion_time:
            self.has_exploded = True
            return

        # Мигаем только если есть обе текстуры
        if self.has_two_textures:
            self.blink_timer += delta_time

            if self.blink_timer >= self.blink_interval:
                self.blink_timer = 0

                # Меняем текстуру на противоположную
                if self.texture == self.bomb_texture:
                    self.texture = self.bomb_texture2
                else:
                    self.texture = self.bomb_texture

class Hero(arcade.Sprite):
    def __init__(self, game):
        # Пробуем загрузить текстуру героя
        try:
            if os.path.exists("assets/Plaer1_purple/idle.png"):
                super().__init__("assets/Plaer1_purple/idle.png", scale=0.5)
            else:
                raise FileNotFoundError("Текстура героя не найдена")
        except:
            # Создаем простую текстуру
            super().__init__(center_x=SCREEN_WIDTH//2, center_y=SCREEN_HEIGHT//2)
            self.texture = arcade.make_soft_square_texture(50, arcade.color.PURPLE, center_alpha=255)

        self.game = game

        # Базовые характеристики
        self.hero_speed = 200
        self.health = 100
        self.bomb_limit = 1  # Начальный лимит бомб
        self.active_bombs = 0  # Количество активных бомб
        self.last_bomb_time = 0
        self.bomb_cooldown = 0.5  # Кулдаун между бомбами

        # Текущие усиления (НАЧАЛЬНЫЕ ЗНАЧЕНИЯ)
        self.explosion_radius = 1
        self.speed_multiplier = 1.0

        self.is_alive = True

        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2

        # Загрузка текстур для анимации
        try:
            self.idle_texture = arcade.load_texture("assets/Plaer1_purple/idle.png")
            self.texture = self.idle_texture

            self.walk_textures = []
            for i in range(1, 5):
                texture_path = f"assets/Plaer1_purple/walk{i}.png"
                if os.path.exists(texture_path):
                    texture = arcade.load_texture(texture_path)
                    self.walk_textures.append(texture)
        except:
            # Если текстуры не загрузились, используем простые цвета
            self.walk_textures = []
            self.idle_texture = arcade.make_soft_square_texture(50, arcade.color.PURPLE, center_alpha=255)
            self.texture = self.idle_texture

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
        """Возвращает скорость с учетом усилений"""
        return self.hero_speed * self.speed_multiplier

    def update(self, delta_time, keys_pressed):
        if not self.is_alive:
            return

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

        self.center_x += dx
        self.center_y += dy

        margin_x = 30
        margin_y = 20

        self.center_x = max(margin_x, min(SCREEN_WIDTH - margin_x, self.center_x))
        self.center_y = max(margin_y, min(SCREEN_HEIGHT - margin_y, self.center_y))
        self.is_walking = dx != 0 or dy != 0

    def can_place_bomb(self):
        """Проверяет, можно ли поставить бомбу"""
        if not self.is_alive:
            return False

        current_time = time.time()
        time_since_last_bomb = current_time - self.last_bomb_time

        # Проверяем лимит бомб и кулдаун
        if self.active_bombs >= self.bomb_limit:
            return False

        if time_since_last_bomb < self.bomb_cooldown:
            return False

        return True

    def place_bomb(self):
        """Ставит бомбу в центре текущей клетки"""
        if not self.can_place_bomb():
            return None

        tile_size = self.game.tile_size

        # Определяем клетку игрока
        cell_x = int(self.center_x // tile_size)
        cell_y = int(self.center_y // tile_size)

        # Вычисляем центр этой клетки
        bomb_x = cell_x * tile_size + tile_size // 2
        bomb_y = cell_y * tile_size + tile_size // 2

        # Проверяем, нет ли уже бомбы в этой клетке
        for existing_bomb in self.game.bomb_list:
            existing_cell_x = int(existing_bomb.center_x // tile_size)
            existing_cell_y = int(existing_bomb.center_y // tile_size)
            if cell_x == existing_cell_x and cell_y == existing_cell_y:
                return None

        bomb = Bomb(bomb_x, bomb_y, explosion_time=2.0)
        self.game.bomb_list.append(bomb)
        self.active_bombs += 1
        self.last_bomb_time = time.time()

        return bomb

    def apply_power_up(self, power_up):
        """Применяет усиление к игроку ТОЛЬКО ОДИН РАЗ"""
        print(f"🔧 Применяю усиление типа: {power_up.power_type}")
        print(f"🔧 Текущий радиус ДО: {self.explosion_radius}")

        if power_up.power_type == PowerUp.TYPE_BOMB_COUNT:
            self.bomb_limit += 1
            print(f"✨ Усиление: +1 бомба (теперь лимит {self.bomb_limit})")

        elif power_up.power_type == PowerUp.TYPE_EXPLOSION_RADIUS:
            # УВЕЛИЧИВАЕМ ТОЛЬКО НА 1
            self.explosion_radius += 1
            # Ограничиваем максимальный радиус
            if self.explosion_radius > 5:
                self.explosion_radius = 5
            print(f"✨ Усиление: +1 радиус взрыва (теперь {self.explosion_radius})")

        elif power_up.power_type == PowerUp.TYPE_SPEED_BOOST:
            self.speed_multiplier += 0.2
            self.speed_multiplier = min(self.speed_multiplier, 2.0)
            print(f"✨ Усиление: +20% скорости (теперь x{self.speed_multiplier:.1f})")

        print(f"🔧 Текущий радиус ПОСЛЕ: {self.explosion_radius}")

    def take_damage(self, damage):
        """Получение урона"""
        if not self.is_alive:
            return

        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            print("💀 Игрок погиб!")

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

        self.death_time = 0
        self.restart_cooldown = 3.0

        # Вероятность выпадения усиления (30%)
        self.power_up_chance = 0.3

        # Время жизни усилений (10 секунд)
        self.power_up_lifetime = 10.0

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.bomb_list = arcade.SpriteList()
        self.power_up_list = arcade.SpriteList()

        try:
            map_name = "gg.tmx"
            if os.path.exists(map_name):
                TILE_SCALING = 1.0
                tile_map = arcade.load_tilemap(map_name, scaling=TILE_SCALING)

                self.Indestructible_list = tile_map.sprite_lists.get("Indestructible", arcade.SpriteList())
                self.destructible_list = tile_map.sprite_lists.get("destructible", arcade.SpriteList())
                self.Background_list = tile_map.sprite_lists.get("Background", arcade.SpriteList())
                self.collision_list = tile_map.sprite_lists.get("Colision", arcade.SpriteList())
                self.destroy_list = tile_map.sprite_lists.get("Destroy", arcade.SpriteList())
            else:
                print("Карта не найдена, создаю пустые списки")
                self.create_empty_lists()
        except Exception as e:
            print(f"Ошибка загрузки карты: {e}")
            self.create_empty_lists()

        self.player = Hero(self)
        self.player.center_x = 70
        self.player.center_y = 980
        self.player_list.append(self.player)

        self.create_physics_engines()

    def create_empty_lists(self):
        """Создает пустые списки если карта не загрузилась"""
        self.Indestructible_list = arcade.SpriteList()
        self.destructible_list = arcade.SpriteList()
        self.Background_list = arcade.SpriteList()
        self.collision_list = arcade.SpriteList()
        self.destroy_list = arcade.SpriteList()

    def create_physics_engines(self):
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.collision_list,
        )

        self.physics_engine2 = arcade.PhysicsEngineSimple(
            self.player, self.destroy_list,
        )

    def check_collision_in_cell(self, cell_x, cell_y):
        """Проверяет, есть ли непроходимый блок в клетке"""
        for sprite in self.collision_list:
            sprite_cell_x = int(sprite.center_x // self.tile_size)
            sprite_cell_y = int(sprite.center_y // self.tile_size)
            if sprite_cell_x == cell_x and sprite_cell_y == cell_y:
                return True
        return False

    def is_player_in_explosion_radius(self, bomb_x, bomb_y):
        """Проверяет, находится ли игрок в радиусе взрыва С УЧЕТОМ ПРЕГРАД"""
        if not self.player.is_alive:
            return False

        tile_size = self.tile_size
        bomb_cell_x = int(bomb_x // tile_size)
        bomb_cell_y = int(bomb_y // tile_size)

        player_cell_x = int(self.player.center_x // tile_size)
        player_cell_y = int(self.player.center_y // tile_size)

        # Получаем текущий радиус из усилений игрока
        current_radius = self.player.explosion_radius

        # Проверяем, находится ли игрок на одной линии с бомбой в пределах радиуса
        if player_cell_x == bomb_cell_x and abs(player_cell_y - bomb_cell_y) <= current_radius:
            # Проверяем направление
            if player_cell_y > bomb_cell_y:  # Игрок выше бомбы
                for row in range(bomb_cell_y + 1, player_cell_y + 1):
                    if self.check_collision_in_cell(bomb_cell_x, row):
                        return False
            else:  # Игрок ниже бомбы
                for row in range(player_cell_y, bomb_cell_y):
                    if self.check_collision_in_cell(bomb_cell_x, row):
                        return False
            return True

        elif player_cell_y == bomb_cell_y and abs(player_cell_x - bomb_cell_x) <= current_radius:
            # Проверяем направление
            if player_cell_x > bomb_cell_x:  # Игрок справа от бомбы
                for col in range(bomb_cell_x + 1, player_cell_x + 1):
                    if self.check_collision_in_cell(col, bomb_cell_y):
                        return False
            else:  # Игрок слева от бомбы
                for col in range(player_cell_x, bomb_cell_x):
                    if self.check_collision_in_cell(col, bomb_cell_y):
                        return False
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

    def spawn_power_up(self, x, y):
        """Создает усиление в указанной позиции ТОЛЬКО ОДИН РАЗ"""
        # Случайно решаем, выпадет ли усиление
        if random.random() <= self.power_up_chance:
            # Выбираем случайный тип усиления
            power_types = [
                PowerUp.TYPE_BOMB_COUNT,
                PowerUp.TYPE_EXPLOSION_RADIUS,
                PowerUp.TYPE_SPEED_BOOST
            ]
            power_type = random.choice(power_types)

            # Создаем усиление
            power_up = PowerUp(x, y, power_type)
            power_up.spawn_time = time.time()

            # Добавляем в список
            self.power_up_list.append(power_up)

            print(f"🎁 Выпало усиление: {power_type}")
            return power_up

        return None

    def check_power_up_collision(self):
        """Проверяет столкновение игрока с усилениями ТОЛЬКО ОДИН РАЗ"""
        power_up_hit_list = arcade.check_for_collision_with_list(
            self.player, self.power_up_list
        )

        # Применяем каждое усиление только один раз
        for power_up in power_up_hit_list:
            # Проверяем, не было ли уже применено это усиление
            if hasattr(power_up, 'applied') and power_up.applied:
                continue

            # Применяем усиление
            self.player.apply_power_up(power_up)

            # Помечаем как примененное
            power_up.applied = True

            # Удаляем усиление из игры
            power_up.remove_from_sprite_lists()

            print(f"✅ Подобрано усиление: {power_up.power_type}")

    def update_power_ups(self):
        """Обновляет усиления и удаляет старые"""
        current_time = time.time()
        power_ups_to_remove = []

        for power_up in self.power_up_list:
            # Проверяем время жизни
            if hasattr(power_up, 'spawn_time'):
                if current_time - power_up.spawn_time > self.power_up_lifetime:
                    power_ups_to_remove.append(power_up)
                    continue

        # Удаляем просроченные усиления
        for power_up in power_ups_to_remove:
            power_up.remove_from_sprite_lists()

    def destroy_blocks_with_power_ups(self, bomb):
        """Уничтожает блоки и создает усиления"""
        tile_size = self.tile_size
        bomb_cell_x = int(bomb.center_x // tile_size)
        bomb_cell_y = int(bomb.center_y // tile_size)

        # Получаем текущий радиус из усилений игрока
        current_radius = self.player.explosion_radius

        # Направления взрыва
        directions = [(0, 0)]  # Центр

        # Добавляем направления для текущего радиуса
        for r in range(1, current_radius + 1):
            directions.append((0, r))    # вверх
            directions.append((0, -r))   # вниз
            directions.append((-r, 0))   # влево
            directions.append((r, 0))    # вправо

        destroyed_blocks = False

        for dx, dy in directions:
            check_x = bomb_cell_x + dx
            check_y = bomb_cell_y + dy

            # Проверяем, не блокирует ли путь непроходимый блок
            if dx != 0 or dy != 0:
                blocked = False
                if dx != 0:  # горизонтальное направление
                    step = 1 if dx > 0 else -1
                    for i in range(1, abs(dx) + 1):
                        check_cell_x = bomb_cell_x + step * i
                        if self.check_collision_in_cell(check_cell_x, bomb_cell_y):
                            blocked = True
                            break
                elif dy != 0:  # вертикальное направление
                    step = 1 if dy > 0 else -1
                    for i in range(1, abs(dy) + 1):
                        check_cell_y = bomb_cell_y + step * i
                        if self.check_collision_in_cell(bomb_cell_x, check_cell_y):
                            blocked = True
                            break

                if blocked:
                    continue  # Пропускаем это направление

            # Координаты центра клетки
            power_up_x = check_x * tile_size + tile_size // 2
            power_up_y = check_y * tile_size + tile_size // 2

            # Уничтожаем destructible блоки в этой клетке
            blocks_in_cell = self.get_blocks_in_cell(check_x, check_y, self.destructible_list)
            for block in blocks_in_cell:
                # Спавним усиление только если есть блоки для уничтожения
                self.spawn_power_up(power_up_x, power_up_y)
                block.remove_from_sprite_lists()
                destroyed_blocks = True

            # Уничтожаем Destroy блоки в этой клетке
            blocks_in_cell = self.get_blocks_in_cell(check_x, check_y, self.destroy_list)
            for block in blocks_in_cell:
                # Спавним усиление только если есть блоки для уничтожения
                self.spawn_power_up(power_up_x, power_up_y)
                block.remove_from_sprite_lists()
                destroyed_blocks = True

        return destroyed_blocks

    def on_draw(self):
        self.clear()

        self.Background_list.draw()
        self.Indestructible_list.draw()
        self.destructible_list.draw()
        self.destroy_list.draw()

        # Отрисовка усилений
        self.power_up_list.draw()

        # Отрисовка бомб
        self.bomb_list.draw()

        self.player_list.draw()

        if self.show_explosion:
            alpha = int(255 * (1 - self.explosion_time / 0.5))

            tile_size = self.tile_size
            bomb_col = int(self.explosion_x // tile_size)
            bomb_row = int(self.explosion_y // tile_size)

            # Получаем текущий радиус из усилений игрока
            current_radius = self.player.explosion_radius

            # Создаем все направления для текущего радиуса
            directions = []

            # Центр
            directions.append((0, 0))

            # Горизонтальные и вертикальные направления
            for r in range(1, current_radius + 1):
                directions.append((0, r))    # вверх
                directions.append((0, -r))   # вниз
                directions.append((-r, 0))   # влево
                directions.append((r, 0))    # вправо

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

        # Сообщение о смерти
        if not self.player.is_alive:
            arcade.draw_text("ВЫ УМЕРЛИ!",
                           SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
                           arcade.color.RED, 50, anchor_x="center")

            # Таймер до рестарта
            if self.death_time > 0:
                time_left = max(0, self.restart_cooldown - (time.time() - self.death_time))
                arcade.draw_text(f"Рестарт через: {time_left:.1f}с",
                               SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                               arcade.color.YELLOW, 30, anchor_x="center")

        # Отображение характеристик игрока
        arcade.draw_text(f"Бомбы: {self.player.active_bombs}/{self.player.bomb_limit}",
                       SCREEN_WIDTH - 200, SCREEN_HEIGHT - 50,
                       arcade.color.WHITE, 20)
        arcade.draw_text(f"Радиус: {self.player.explosion_radius}",
                       SCREEN_WIDTH - 200, SCREEN_HEIGHT - 80,
                       arcade.color.WHITE, 20)
        arcade.draw_text(f"Скорость: x{self.player.speed_multiplier:.1f}",
                       SCREEN_WIDTH - 200, SCREEN_HEIGHT - 110,
                       arcade.color.WHITE, 20)

        # Показываем клетку игрока
        player_cell_x = int(self.player.center_x // self.tile_size)
        player_cell_y = int(self.player.center_y // self.tile_size)
        arcade.draw_text(f"Клетка: ({player_cell_x}, {player_cell_y})",
                       SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 50,
                       arcade.color.YELLOW, 20)

    def on_update(self, delta_time):
        if not self.player.is_alive:
            # Проверяем таймер рестарта
            if self.death_time > 0 and time.time() - self.death_time >= self.restart_cooldown:
                self.setup()
            return

        self.player_list.update(delta_time, self.keys_pressed)
        self.player.update_animation(delta_time)

        # Обновление бомб
        self.bomb_list.update(delta_time)

        # Обновление усилений
        self.power_up_list.update(delta_time)
        self.update_power_ups()

        # Проверка сбора усилений (ТОЛЬКО ОДИН РАЗ ЗА КАДР)
        self.check_power_up_collision()

        bombs_to_remove = []

        # Считаем активные бомбы
        active_bombs = 0

        for bomb in self.bomb_list:
            if not bomb.has_exploded:
                active_bombs += 1

            if bomb.has_exploded:
                self.show_explosion = True
                self.explosion_time = 0
                self.explosion_x = bomb.center_x
                self.explosion_y = bomb.center_y

                # Проверяем попадание по игроку
                if self.is_player_in_explosion_radius(bomb.center_x, bomb.center_y):
                    self.player.take_damage(100)
                    if not self.player.is_alive:
                        self.death_time = time.time()

                # Уничтожение блоков и создание усилений
                destroyed = self.destroy_blocks_with_power_ups(bomb)

                bombs_to_remove.append(bomb)

                # Если уничтожили блоки, пересоздаем физические движки
                if destroyed:
                    self.create_physics_engines()

        # Обновляем счетчик активных бомб у игрока
        self.player.active_bombs = active_bombs

        # Удаляем взорвавшиеся бомбы
        for bomb in bombs_to_remove:
            bomb.remove_from_sprite_lists()

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

        if key == arcade.key.SPACE and self.player.is_alive:
            bomb = self.player.place_bomb()
            if bomb:
                print(f"💣 Бомба поставлена! Активных бомб: {self.player.active_bombs}/{self.player.bomb_limit}")
        elif key == arcade.key.R:  # Клавиша R для мгновенного рестарта
            self.setup()

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()
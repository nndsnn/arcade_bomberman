import arcade

# Задаём размер окна
SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 900
RESIZABLE = True
SCREEN_TITLE = "Bomber"

class Hero(arcade.Sprite):
    def __init__(self):
        super().__init__()

        # Основные характеристики
        self.scale = 0.5
        self.hero_speed = 300
        self.health = 100
        self.idle_texture = arcade.load_texture("assets/Plaer1_purple/idle.png")
        self.texture = self.idle_texture

        # Жёстко ставим персонажа в центр экрана (лучше передавать позицию в __init__)
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2
        self.walk_textures = []
        for i in range(1, 5):
            texture = arcade.load_texture(f"assets/Plaer1_purple/walk{i}.png")
            self.walk_textures.append(texture)

        self.current_texture = 0
        self.texture_change_time = 0
        self.texture_change_delay = 0.1  # секунд на кадр
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
            
         
        # Нормализация диагонального движения
        if dx != 0 and dy != 0:
            factor = 0.7071  # ≈ 1/√2
            dx *= factor
            dy *= factor

        self.center_x += dx
        self.center_y += dy
        margin_x =  30 # половина ширины спрайта
        margin_y = 20  # половина высоты спрайта
        
        self.center_x = max(margin_x, min(SCREEN_WIDTH - margin_x, self.center_x))
        self.center_y = max(margin_y, min(SCREEN_HEIGHT - margin_y, self.center_y))
        self.is_walking = dx or dy
        
        
class BoxBorder:
    """Класс для создания границы из коробочек по всему периметру"""
    def __init__(self, window_width, window_height):
        self.window_width = window_width
        self.window_height = window_height
        
        # Загружаем текстуру
        self.wall_texture = arcade.load_texture("assets/Tiles/block_blue.png")
        
        # Создаем список для хранения всех коробочек
        self.wall_list = arcade.SpriteList()
        
        self.create_full_border()
    
    def create_full_border(self):
        """Создает границу по всему периметру экрана"""
        tile_size = 128  # Размер плитки
        
        # Верхняя граница
        for x in range(0, self.window_width, tile_size):
            self.add_box(x + tile_size // 2, 
                        self.window_height - tile_size // 2)
        
        # Нижняя граница
        for x in range(0, self.window_width, tile_size):
            self.add_box(x + tile_size // 2, 
                        tile_size // 2)
        
        # Боковые границы (без углов, чтобы не дублировать)
        for y in range(tile_size, self.window_height - tile_size, tile_size):
            # Левая граница
            self.add_box(tile_size // 2, y)
            # Правая граница
            self.add_box(self.window_width - tile_size // 2, y)
    
    def add_box(self, center_x, center_y):
        """Добавляет одну коробочку"""
        wall = arcade.Sprite()
        wall.texture = self.wall_texture
        wall.center_x = center_x
        wall.center_y = center_y
        self.wall_list.append(wall)
    
    
    def get_wall_list(self):
        """Возвращает список стен для проверки столкновений"""
        return self.wall_list
         
        
class MyGame(arcade.Window):
    def __init__(self, width, height, title, resizable=False):
        super().__init__(width, height, title,resizable)
        arcade.set_background_color(arcade.color.ASH_GREY)

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.player = Hero()
        self.box = BoxBorder(self.width, self.height)
        self.player_list.append(self.player)
        self.keys_pressed = set()
    def on_draw(self):
        self.clear()
        self.player_list.draw()
        self.box.wall_list.draw()
    def on_update(self, delta_time):
        self.player_list.update(delta_time, self.keys_pressed)
        self.player.update_animation()
    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
     


def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
import arcade

# Задаём размер окна
SCREEN_WIDTH = 1900
SCREEN_HEIGHT = 1050
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
        
        
class MyGame(arcade.Window):
    def __init__(self, width, height, title, resizable=False):
        super().__init__(width, height, title,resizable)
        arcade.set_background_color(arcade.color.ASH_GREY)

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.player = Hero()
        #self.player_list.append(self.player)
        self.keys_pressed = set()
        """Настраиваем игру здесь. Вызывается при старте и при рестарте"""
        # Инициализируем списки спрайтов
        self.wallIndestructible_list = arcade.SpriteList()  # Сюда попадёт слой Collision!
        self.wallI_destroy_list = arcade.SpriteList()
        # ===== ВОЛШЕБСТВО ЗАГРУЗКИ КАРТЫ! (Почти без магии.) =====
        # Грузим тайловую карту
        map_name = "gg.tmx"
        TILE_SCALING = 1.0
        # Параметр 'scaling' ОЧЕНЬ важен! Умножает размер каждого тайла
        tile_map = arcade.load_tilemap(map_name, scaling=TILE_SCALING)

        # --- Достаём слои из карты как спрайт-листы ---
        # Слой "walls" (стены) — просто для отрисовки
        self.Indestructible_list = tile_map.sprite_lists["Indestructible"]
        # Слой "chests" (сундуки) — красота!
        self.destructible_list = tile_map.sprite_lists["destructible"]
        # Слой "exit" (выходы с уровня) — красота!
        self.Background_list = tile_map.sprite_lists["Background"]
        # САМЫЙ ГЛАВНЫЙ СЛОЙ: "Collision" — наши стены и платформы для физики!
        self.collision_list = tile_map.sprite_lists["Colision"]
        self.destroy_list = tile_map.sprite_lists["Destroy"]
        # --- Создаём игрока ---
        # Карту загрузили, теперь создаём героя, который будет по ней бегать
        # Ставим игрока куда-нибудь на землю (посмотрите в Tiled, где у вас земля!)
        self.player.center_x = 70 # Примерные координаты
        self.player.center_y = 980# Примерные координаты
        self.player_list.append(self.player)

        # --- Физический движок ---
        # Используем PhysicsEngineSimple, который знаем и любим
        
        # Он даст нам движение и коллизии со стенами (self.wall_list)!
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.collision_list,
        )
        self.physics_engine2 = arcade.PhysicsEngineSimple(
            self.player, self.destroy_list,
        )
    
    def on_draw(self):
        self.clear()
        self.Background_list.draw() 
        self.Indestructible_list.draw()
        self.destructible_list.draw()
        self.player_list.draw()
        
    def on_update(self, delta_time):
        self.player_list.update(delta_time, self.keys_pressed)
        self.player.update_animation()
        if self.physics_engine:
            self.physics_engine.update()
        if self.physics_engine2:
            self.physics_engine2.update()
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
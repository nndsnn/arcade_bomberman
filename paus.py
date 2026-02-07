import arcade

class PauseButton:
    """Кнопка паузы"""
    
    def __init__(self, x=50, y=1000, width=125, height=50):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_paused = False
        self.hovered = False
    
    def draw(self):
        """Отрисовка кнопки"""
        # Цвет кнопки в зависимости от состояния
        if self.is_paused:
            color = (255, 200, 0, 200)  # Желтый - игра на паузе
        elif self.hovered:
            color = (150, 150, 150, 200)  # Серый - наведение мыши
        else:
            color = (100, 100, 100, 200)  # Темно-серый - обычное состояние
        
        # Фон кнопки
        arcade.draw_lrbt_rectangle_filled(
            self.x, self.x + self.width,
            self.y - self.height, self.y,
            color
        )
        
        # Обводка кнопки
        arcade.draw_lrbt_rectangle_outline(
            self.x, self.x + self.width,
            self.y - self.height, self.y,
            arcade.color.WHITE, 2
        )
        
        # Текст на кнопке
        if self.is_paused:
            text = "▶ ПАУЗА"  # Значок "продолжить"
        else:
            text = "⏸ ПАУЗА"  # Значок "пауза"
        
        arcade.draw_text(
            text,
            self.x + self.width // 2,
            self.y - self.height // 2 - 5,
            arcade.color.WHITE, 20,
            anchor_x="center", anchor_y="center",
            bold=True
        )
    
    def check_click(self, x, y):
        """Проверка клика по кнопке"""
        if (self.x <= x <= self.x + self.width and
            self.y - self.height <= y <= self.y):
            self.is_paused = not self.is_paused  # Переключаем паузу
            return True
        return False
    
    def toggle_pause(self):
        """Переключение состояния паузы"""
        self.is_paused = not self.is_paused
        return self.is_paused
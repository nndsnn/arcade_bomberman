import arcade

class PauseButton:
    
    def __init__(self, x=50, y=1000, width=125, height=50):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_paused = False
        self.hovered = False
    
    def draw(self):
        if self.is_paused:
            color = (255, 200, 0, 200)
        elif self.hovered:
            color = (150, 150, 150, 200)
        else:
            color = (100, 100, 100, 200)
        
        arcade.draw_lrbt_rectangle_filled(
            self.x, self.x + self.width,
            self.y - self.height, self.y,
            color
        )
        
        arcade.draw_lrbt_rectangle_outline(
            self.x, self.x + self.width,
            self.y - self.height, self.y,
            arcade.color.WHITE, 2
        )
        
        if self.is_paused:
            text = "▶ ПАУЗА"
        else:
            text = "⏸ ПАУЗА"
        
        arcade.draw_text(
            text,
            self.x + self.width // 2,
            self.y - self.height // 2 - 5,
            arcade.color.WHITE, 20,
            anchor_x="center", anchor_y="center",
            bold=True
        )
    
    def check_click(self, x, y):
        if (self.x <= x <= self.x + self.width and
            self.y - self.height <= y <= self.y):
            self.is_paused = not self.is_paused
            return True
        return False
    
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        return self.is_paused
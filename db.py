import sqlite3

class DB:
    def __init__(self):
        self.conn = sqlite3.connect("settings.db")
        self.conn.execute("CREATE TABLE IF NOT EXISTS settings (sound INTEGER)")
        self.conn.execute("INSERT OR IGNORE INTO settings (sound) VALUES (1)")
        self.conn.commit()
    
    def get(self):
        return bool(self.conn.execute("SELECT sound FROM settings").fetchone()[0])
    
    def set(self, value):
        self.conn.execute("UPDATE settings SET sound = ?", (1 if value else 0,))
        self.conn.commit()
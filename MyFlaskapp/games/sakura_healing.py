import tkinter as tk
from base_game import NarutoGame
import random
import os

class SakuraHealing(NarutoGame):
    def __init__(self):
        super().__init__("Sakura Healing", 300, 300)
        self.root = tk.Tk()
        self.root.title(f"Score: {self.score} | High: {self.high_score}")
        self.difficulty_var = tk.StringVar(value="Medium")
        self.canvas = tk.Canvas(self.root, width=300, height=300, bg="white")
        
        # Load assets
        from PIL import Image, ImageTk
        self.assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        
        def load_resize(name, w, h):
            path = os.path.join(self.assets_dir, name)
            if os.path.exists(path):
                img = Image.open(path)
                img = img.resize((w, h), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
            return None

        self.fish_img = load_resize("fish.png", 300, 300)
        self.bandage_img = load_resize("bandage_icon.png", 40, 40)
        
        # Set background
        if self.fish_img:
            self.canvas.create_image(150, 150, image=self.fish_img)
        
        # Custom Cursor
        self.root.config(cursor="none")
        self.cursor_id = None
        if self.bandage_img:
            self.cursor_id = self.canvas.create_image(0, 0, image=self.bandage_img, tags="cursor")
            self.canvas.bind("<Motion>", self.move_cursor)
        
        self.timer = 60
        self.game_active = False
        self.speed = 1000
        self.time_label = self.canvas.create_text(50, 20, text=f"Time: {self.timer}", font=("Arial", 12), fill="black")
        self.score_label = self.canvas.create_text(250, 20, text=f"Score: {self.score}", font=("Arial", 12), fill="black")

    def move_cursor(self, event):
        if self.cursor_id is None:
            return
        self.canvas.coords(self.cursor_id, event.x, event.y)
        self.canvas.tag_raise(self.cursor_id)

    def start_game(self):
        top = tk.Frame(self.root)
        top.pack()
        tk.Label(top, text="Difficulty:").pack(side='left')
        tk.OptionMenu(top, self.difficulty_var, "Easy", "Medium", "Hard").pack(side='left')
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.heal)
        self.root.bind("p", lambda e: self.toggle_pause())
        self.set_difficulty(self.difficulty_var.get())
        f = self.difficulty_factor()
        self.timer = int(60 / (1 if f == 1.0 else (0.8 if f < 1.0 else 1.2)))
        self.game_active = True
        self.update_timer()
        self.schedule_hurt()
        self.root.mainloop()

    def update_timer(self):
        if self.paused:
            self.root.after(250, self.update_timer)
            return
        if self.game_active and self.timer > 0:
            self.timer -= 1
            self.canvas.itemconfig(self.time_label, text=f"Time: {self.timer}")
            self.root.after(1000, self.update_timer)
        elif self.timer <= 0:
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            self.game_over()

    def schedule_hurt(self):
        if not self.game_active or self.paused: return
        x = random.randint(30, 270)
        y = random.randint(40, 270)
        # Randomize "injury" type
        symbol = random.choice(["🤕", "🩹", "🩸"])
        self.canvas.create_text(x, y, text=symbol, font=("Arial", 20), tags="hurt")
        
        # Speed up as score increases
        f = self.difficulty_factor()
        base = int(1000 / f)
        current_speed = max(300, base - (self.score * int(20 * f)))
        self.root.after(current_speed, self.schedule_hurt)

    def heal(self, event):
        if not self.game_active: return
        if self.paused: return
        target = self._nearest_hurt(event.x, event.y, threshold=20)
        if target is not None:
            self.canvas.delete(target)
            # Visual effect
            self.show_heal_effect(event.x, event.y)
            self.score += 10
            self.canvas.itemconfig(self.score_label, text=f"Score: {self.score}")
            self.root.title(f"Score: {self.score} | High: {self.high_score}")
        else:
            self.score -= 5
            self.canvas.itemconfig(self.score_label, text=f"Score: {self.score}")

    def show_heal_effect(self, x, y):
        effect = self.canvas.create_text(x, y, text="+", font=("Arial", 25), fill="green")
        self.root.after(300, lambda: self.canvas.delete(effect))

    def _nearest_hurt(self, x, y, threshold=20):
        candidates = self.canvas.find_withtag("hurt")
        nearest = None
        best = None
        for item in candidates:
            bbox = self.canvas.bbox(item)
            if not bbox:
                continue
            cx = (bbox[0] + bbox[2]) / 2
            cy = (bbox[1] + bbox[3]) / 2
            dx = cx - x
            dy = cy - y
            dist2 = dx*dx + dy*dy
            if best is None or dist2 < best:
                best = dist2
                nearest = item
        if nearest is None:
            return None
        if best is not None and best <= (threshold*threshold):
            return nearest
        return None

    def update(self): pass
    def draw(self): pass

if __name__ == "__main__":
    game = SakuraHealing()
    game.start_game()

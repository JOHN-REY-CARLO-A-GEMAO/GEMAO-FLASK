import tkinter as tk
import time
import random
from base_game import NarutoGame

class KunaiReflex(NarutoGame):
    def __init__(self):
        super().__init__("Kunai Reflex", 400, 300)
        self.root = tk.Tk()
        self.root.title(f"Score: {self.score} | High: {self.high_score}")
        self.difficulty_var = tk.StringVar(value="Medium")
        self.canvas = tk.Canvas(self.root, width=400, height=300, bg="white")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.click)
        self.state = "IDLE" # IDLE, WAIT, ACTION, RESULT
        self.start_time = 0
        
        # Load Images
        from PIL import Image, ImageTk
        import os
        base_path = os.path.dirname(__file__)
        assets_path = os.path.join(base_path, 'assets')
        
        def load_resize(name, w, h):
            path = os.path.join(assets_path, name)
            if os.path.exists(path):
                img = Image.open(path)
                img = img.resize((w, h), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
            return None

        self.imgs = {}
        # Map state to image
        self.state_map = {
            "WAIT": "bush_hiding.png",
            "ACTION": "kunai_flying.png",
            "RESULT": "wood_log.png"
        }
        
        for k, v in self.state_map.items():
            res = load_resize(v, 200, 200) # Reasonable size
            if res:
                self.imgs[k] = res

        top = tk.Frame(self.root)
        top.pack()
        tk.Label(top, text="Difficulty:").pack(side='left')
        tk.OptionMenu(top, self.difficulty_var, "Easy", "Medium", "Hard").pack(side='left')
        self.draw_ui("Click to Start")

    def start_game(self):
        self.root.bind("p", lambda e: self.toggle_pause())
        self.root.mainloop()

    def click(self, event):
        if self.paused:
            return
        if self.state == "IDLE":
             self.state = "WAIT"
             self.draw_ui("Wait for Green...", bg="red")
             self.set_difficulty(self.difficulty_var.get())
             f = self.difficulty_factor()
             low = 1000 if f == 1.0 else (1500 if f < 1.0 else 700)
             high = 3000 if f == 1.0 else (3500 if f < 1.0 else 2000)
             self.root.after(random.randint(low, high), self.turn_green)
             self.audio_play("victory")
        elif self.state == "WAIT":
             # False Start
             self.state = "RESULT"
             self.draw_ui("Too Early! Click to Retry", bg="orange")
             self.score = 0
             self.state = "IDLE"
             self.audio_play("defeat")
        elif self.state == "ACTION":
             reaction = time.time() - self.start_time
             self.state = "RESULT"
             self.set_difficulty(self.difficulty_var.get())
             f = self.difficulty_factor()
             rank = "Genin"
             if reaction < (0.35 / f): rank = "Jonin"
             if reaction < (0.25 / f): rank = "Kage"
             
             self.score = int((1.0 / reaction) * (10 * f))
             self.draw_ui(f"{reaction:.3f}s\nRank: {rank}\nClick to Retry", bg="white")
             if self.score > self.high_score:
                 self.high_score = self.score
                 self.save_high_score()
             self.root.title(f"Score: {self.score} | High: {self.high_score}")
             self.state = "IDLE"
             self.audio_play("victory")

    def turn_green(self):
        if self.paused:
             return
        if self.state == "WAIT":
             self.state = "ACTION"
             self.start_time = time.time()
             self.draw_ui("DODGE! (CLICK!)", bg="green")
             self.audio_play("victory")

    def draw_ui(self, text, bg="white"):
        self.canvas.config(bg=bg)
        self.canvas.delete("all")
        
        # Draw Image if available for current state
        img = self.imgs.get(self.state)
        # Exception: For Result, always show log? Or depends on success? 
        # Prompt says: wood_log.png - Replaces the "Success" state (Substitution Jutsu).
        # But my code handles success/fail in RESULT state.
        # Logic: If RESULT and successful (score > 0), show log. Else maybe nothing or bush?
        # Let's simplify: Show image if state matches.
        
        if self.state == "RESULT" and "Rank:" in text and "Genin" not in text: 
             # Only show log if good rank? Or just show it.
             # Let's show log for result.
             img = self.imgs.get("RESULT")
        
        if img:
             self.canvas.create_image(200, 150, image=img)
             
        self.canvas.create_text(200, 150, text=text, font=("Arial", 20), justify="center", fill="black" if not img else "white")

    def update(self): pass
    def draw(self): pass

if __name__ == "__main__":
    game = KunaiReflex()
    game.start_game()

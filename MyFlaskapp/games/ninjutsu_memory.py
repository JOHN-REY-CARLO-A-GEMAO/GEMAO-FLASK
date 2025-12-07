import tkinter as tk
from tkinter import messagebox
from base_game import NarutoGame
import random
import os
from PIL import Image, ImageTk

class NinjutsuMemory(NarutoGame):
    def __init__(self):
        super().__init__("Ninjutsu Memory", 400, 400)
        self.root = tk.Tk()
        self.root.title(f"Score: {self.score} | High: {self.high_score}")
        self.difficulty_var = tk.StringVar(value="Medium")
        
        # Load assets
        self.assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        self.images = {}
        
        def load_resize(path, size):
            if os.path.exists(path):
                img = Image.open(path)
                img = img.resize(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
            return None

        elem_map = {
             'fire': 'icon_fire.png',
             'water': 'icon_water.png',
             'wind': 'icon_wind.png',
             'earth': 'icon_earth.png',
             'lightning': 'icon_lightning.png'
        }
        
        for elem, fname in elem_map.items():
             path = os.path.join(self.assets_dir, fname)
             # Resize icons to 60x60
             res = load_resize(path, (60, 60))
             if res:
                 self.images[elem] = res
             else:
                 print(f"Warning: {path} not found")
                 
        self.card_back = None
        if os.path.exists(os.path.join(self.assets_dir, "card_back_leaf.png")):
             self.card_back = load_resize(os.path.join(self.assets_dir, "card_back_leaf.png"), (60, 60))

        self.cards = list(self.images.keys()) * 2
        random.shuffle(self.cards)
        self.buttons = []
        self.first = None
        self.timer = 60
        self.label = tk.Label(self.root, text=f"Time: {self.timer}", font=("Arial", 16))
        self.label.grid(row=4, column=0, columnspan=4)
        self.game_over = False

    def start_game(self):
        self.root.bind("p", lambda e: self.toggle_pause())
        top = tk.Frame(self.root)
        top.grid(row=5, column=0, columnspan=4, pady=5)
        tk.Label(top, text="Difficulty:").pack(side='left')
        tk.OptionMenu(top, self.difficulty_var, "Easy", "Medium", "Hard").pack(side='left')
        self.set_difficulty(self.difficulty_var.get())
        f = self.difficulty_factor()
        self.timer = int(60 / (1 if f == 1.0 else (0.75 if f < 1.0 else 1.3)))
        self.label.config(text=f"Time: {self.timer}")
        for i, card in enumerate(self.cards):
            btn = tk.Button(self.root, text="?", width=10, height=3, 
                            command=lambda c=card, idx=i: self.flip(c, idx))
            if self.card_back:
                btn.config(image=self.card_back, width=60, height=60, text="")
            btn.grid(row=i//5, column=i%5) # 5 columns for 10 cards
            self.buttons.append(btn)
        self.update_timer()
        self.root.mainloop()

    def update_timer(self):
        if self.paused:
            self.root.after(250, self.update_timer)
            return
        if self.timer > 0 and not self.game_over:
            self.timer -= 1
            self.label.config(text=f"Time: {self.timer}")
            self.root.after(1000, self.update_timer)
        elif self.timer <= 0:
            messagebox.showerror("Fail", "Time Up!")
            self.audio_play("defeat")
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            self.root.quit()

    def flip(self, card, idx):
        if card in self.images:
            self.buttons[idx].config(image=self.images[card], text="", state="disabled", width=60, height=60)
        else:
            self.buttons[idx].config(text=card, state="disabled")
        if not self.first:
            self.first = (card, idx)
        else:
            if self.first[0] == card:
                self.first = None
                self.score += 1
                self.root.title(f"Score: {self.score} | High: {self.high_score}")
                self.audio_play("victory")
                if self.score == len(self.cards) // 2: 
                    self.game_over = True
                    messagebox.showinfo("Win", "All Jutsu Mastered!")
                    self.audio_play("victory")
                    if self.score > self.high_score:
                        self.high_score = self.score
                        self.save_high_score()
            else:
                first_idx = self.first[1]
                delay = int(500 / self.difficulty_factor())
                self.root.after(delay, lambda: self.reset(first_idx, idx))
                self.first = None
                self.audio_play("defeat")

    def reset(self, i1, i2):
        if self.card_back:
            self.buttons[i1].config(image=self.card_back, text="", state="normal", width=60, height=60)
            self.buttons[i2].config(image=self.card_back, text="", state="normal", width=60, height=60)
        else:
            self.buttons[i1].config(image="", text="?", state="normal", width=10, height=3)
            self.buttons[i2].config(image="", text="?", state="normal", width=10, height=3)

    def update(self): pass
    def draw(self): pass

if __name__ == "__main__":
    game = NinjutsuMemory()
    game.start_game()

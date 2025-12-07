import tkinter as tk
from tkinter import messagebox
from base_game import NarutoGame
import random

class KakashiPattern(NarutoGame):
    def __init__(self):
        super().__init__("Kakashi Copy Ninja", 400, 400) # Increased size slightly
        self.root = tk.Tk()
        self.root.title(f"Score: {self.score} | High: {self.high_score}")
        self.seq = []
        self.u_seq = []
        self.btns = []
        self.colors = ['red', 'blue', 'green', 'yellow']
        self.difficulty_var = tk.StringVar(value="Medium")
        
        # Load Images
        self.images = {}
        # Map colors to image filenames (based on prompt request)
        # Red=Tiger, Blue=Bird, Green=Boar, Yellow=Dog
        self.img_map = {
            'red': 'sign_tiger.png',
            'blue': 'sign_bird.png',
            'green': 'sign_boar.png',
            'yellow': 'sign_dog.png'
        }
        
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

        for c, fname in self.img_map.items():
            res = load_resize(fname, 100, 100)
            if res:
                self.images[c] = res
            else:
                 print(f"Missing {fname}")
        
        # Flash image
        self.flash_img = load_resize("white_flash.png", 100, 100)

        # Portrait
        self.portrait = load_resize("kakashi_portrait.png", 150, 150)
        if self.portrait:
             lbl = tk.Label(self.root, image=self.portrait)
             lbl.pack()

        self.flash_speed = 500
        self.state_label = tk.Label(self.root, text="Press Start", font=("Arial", 14))
        self.state_label.pack()

        diff_frame = tk.Frame(self.root)
        diff_frame.pack(pady=5)
        tk.Label(diff_frame, text="Difficulty:").pack(side='left')
        tk.OptionMenu(diff_frame, self.difficulty_var, "Easy", "Medium", "Hard").pack(side='left')

    def start_game(self):
        frame = tk.Frame(self.root)
        frame.pack()
        for c in self.colors:
            # Use image if available, else fallback to bg
            img = self.images.get(c)
            if img:
                b = tk.Button(frame, image=img, width=100, height=100, command=lambda c=c: self.click(c))
                # Store color in widget attribute for logic
                b.color_tag = c 
            else:
                b = tk.Button(frame, bg=c, width=10, height=5, command=lambda c=c: self.click(c))
                b.color_tag = c
            
            b.pack(side='left', padx=5)
            self.btns.append(b)
        
        tk.Button(self.root, text="START", command=self.begin_game).pack(pady=10)
        self.root.mainloop()

    def begin_game(self):
        self.seq = []
        self.score = 0
        self.set_difficulty(self.difficulty_var.get())
        base_speed = int(500 / self.difficulty_factor())
        self.flash_speed = base_speed
        self.root.title(f"Score: {self.score} | High: {self.high_score}")
        self.audio_play("victory")
        self.next_round()

    def next_round(self):
        self.u_seq = []
        self.state_label.config(text="WATCH!")
        self.seq.append(random.choice(self.colors))
        self.flash_speed = max(100, int(self.flash_speed - (len(self.seq)*20)))
        self.root.after(1000, lambda: self.flash_seq(0))

    def flash_seq(self, i):
        if i < len(self.seq):
            c = self.seq[i]
            # Find button with this color
            btn = None
            for b in self.btns:
                if b.color_tag == c:
                    btn = b
                    break
            
            if btn:
                if self.flash_img and btn['image']:
                    # Swap image
                    original_img = btn['image']
                    btn.config(image=self.flash_img)
                    self.root.after(self.flash_speed, lambda: [btn.config(image=original_img), self.root.after(200, lambda: self.flash_seq(i+1))])
                else:
                    # Fallback
                    original_bg = btn.cget('bg')
                    btn.config(bg='white')
                    self.root.after(self.flash_speed, lambda: [btn.config(bg=original_bg), self.root.after(200, lambda: self.flash_seq(i+1))])
            self.audio_play("victory")
        else:
            self.state_label.config(text="REPEAT!")

    def click(self, color):
        self.u_seq.append(color)
        if self.u_seq == self.seq[:len(self.u_seq)]:
            if len(self.u_seq) == len(self.seq):
                self.score += 1
                self.root.title(f"Score: {self.score} | High: {self.high_score}")
                self.audio_play("victory")
                self.root.after(1000, self.next_round)
        else:
            messagebox.showerror("Fail", f"Game Over! Score: {self.score}")
            self.state_label.config(text="Press Start to Retry")
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            self.seq = []
            self.audio_play("defeat")

    def update(self): pass
    def draw(self): pass

if __name__ == "__main__":
    game = KakashiPattern()
    game.start_game()

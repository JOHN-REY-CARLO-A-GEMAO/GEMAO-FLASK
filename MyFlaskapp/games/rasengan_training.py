import tkinter as tk
from tkinter import messagebox
from base_game import NarutoGame

class RasenganTraining(NarutoGame):
    def __init__(self):
        super().__init__("Rasengan Training", 400, 400)
        self.root = tk.Tk()
        self.root.title(f"Score: {self.score} | High: {self.high_score}")
        self.canvas = tk.Canvas(self.root, width=400, height=300, bg="black")
        self.power = 0
        self.stage = 1
        self.decay_rate = 2
        
        # Load Images
        import os
        from PIL import Image, ImageTk # Fixed: Use PIL for resizing and format support
        base_path = os.path.dirname(__file__)
        assets_path = os.path.join(base_path, 'assets')

        def load_and_resize(name, size):
             path = os.path.join(assets_path, name)
             if os.path.exists(path):
                 try:
                     img = Image.open(path)
                     img = img.resize(size, Image.Resampling.LANCZOS)
                     return ImageTk.PhotoImage(img)
                 except Exception as e:
                     print(f"Error loading {name}: {e}")
                     return None
             return None
        
        self.img_palm = load_and_resize("hand_palm.png", (400, 300))
        self.img_spin_s = load_and_resize("chakra_spin_small.png", (50, 50))
        self.img_spin_m = load_and_resize("chakra_spin_med.png", (100, 100))
        self.img_complete = load_and_resize("rasengan_complete.png", (200, 200))

        self.canvas.pack()
        self.draw_ui()

    def start_game(self):
        self.root.bind("p", lambda e: self.toggle_pause())
        self.root.bind("<space>", self.charge)
        self.root.bind("<Return>", self.charge)
        top = tk.Frame(self.root)
        top.pack()
        diff = tk.StringVar(value="Medium")
        tk.Label(top, text="Difficulty:").pack(side='left')
        tk.OptionMenu(top, diff, "Easy", "Medium", "Hard").pack(side='left')
        self.set_difficulty(diff.get())
        f = self.difficulty_factor()
        self.decay_rate = 2 if f < 1.0 else (2 if f == 1.0 else 3)
        self.root.focus_set()
        self.update_decay()
        self.root.mainloop()

    def update(self):
        pass

    def draw(self):
        pass

    def charge(self, event=None):
        self.power += 5
        if self.power >= 100:
            if self.stage == 1:
                messagebox.showinfo("Success", "Rasengan Formed! STAGE 2 START!")
                self.audio_play("victory")
                self.stage = 2
                self.power = 0
                f = self.difficulty_factor()
                self.decay_rate = 4 if f < 1.0 else (5 if f == 1.0 else 6)
                self.score += 1
                self.root.title(f"Score: {self.score} | High: {self.high_score}")
            else:
                messagebox.showinfo("Victory", "GIANT RASENGAN COMPLETE!")
                self.audio_play("victory")
                self.stage = 1
                self.power = 0
                f = self.difficulty_factor()
                self.decay_rate = 2 if f < 1.0 else (2 if f == 1.0 else 3)
                self.score += 5
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
                self.root.title(f"Score: {self.score} | High: {self.high_score}")
        self.draw_ui()

    def update_decay(self):
        if not self.paused:
            if self.power > 0:
                self.power -= self.decay_rate
                if self.power < 0: self.power = 0
        self.draw_ui()
        self.root.after(100, self.update_decay)

    def draw_ui(self):
        self.canvas.delete("all")
        
        cx, cy = 200, 150
        
        # Draw Background (Palm)
        if self.img_palm:
             self.canvas.create_image(cx, cy, image=self.img_palm)
        
        # Decide which image to show based on power
        spin_img = None
        if self.power >= 70:
             spin_img = self.img_complete
        elif self.power >= 30:
             spin_img = self.img_spin_m
        elif self.power > 0:
             spin_img = self.img_spin_s
             
        if spin_img:
             self.canvas.create_image(cx, cy, image=spin_img)
        elif self.power > 0:
             # Fallback
             size = self.power * 2
             color = "blue" if self.stage == 1 else "red"
             self.canvas.create_oval(cx-size/2, cy-size/2, cx+size/2, cy+size/2, fill=color, outline="white")
        
        self.canvas.create_text(200, 30, text=f"Stage: {self.stage} | Power: {self.power}%", fill="lightblue", font=("Arial", 16))
        self.canvas.create_text(200, 270, text="PRESS SPACE!", fill="white")
        self.canvas.create_text(330, 20, text=f"High: {self.high_score}", fill="white", font=("Arial", 12))
        if self.paused:
            self.canvas.create_text(200, 150, text="Paused (P)", fill="yellow", font=("Arial", 18))

if __name__ == "__main__":
    game = RasenganTraining()
    game.start_game()

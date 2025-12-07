import tkinter as tk
from tkinter import messagebox
from base_game import NarutoGame

class AkatsukiMaze(NarutoGame):
    def __init__(self):
        super().__init__("Akatsuki Maze", 400, 400)
        self.root = tk.Tk()
        self.root.title(f"Score: {self.score} | High: {self.high_score}")
        self.canvas = tk.Canvas(self.root, width=400, height=400, bg="black")
        self.player = [20, 20]
        self.score = 0
        self.difficulty_var = tk.StringVar(value="Medium")
        self.enemies = [
            {'x': 100, 'y': 100, 'dx': 5, 'dy': 0, 'limit': [50, 250]}, # Horizontal patrol
            {'x': 250, 'y': 250, 'dx': 0, 'dy': 5, 'limit': [200, 300]}  # Vertical patrol
        ]
        self.exit = [360, 360]
        self.tick_ms = 50
        
        # Load Images
        import os
        from PIL import Image, ImageTk
        base_path = os.path.dirname(__file__)
        assets_path = os.path.join(base_path, 'assets')
        
        def load_resize(name, w, h):
            path = os.path.join(assets_path, name)
            if os.path.exists(path):
                img = Image.open(path)
                img = img.resize((w, h), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
            return None

        self.img_player = load_resize("akatsuki_member.png", 20, 20)
        self.img_wall = load_resize("wall_texture.png", 40, 40)
        self.img_exit = load_resize("bijuu_exit.png", 40, 40)

    def start_game(self):
        top = tk.Frame(self.root)
        top.pack()
        tk.Label(top, text="Difficulty:").pack(side='left')
        tk.OptionMenu(top, self.difficulty_var, "Easy", "Medium", "Hard").pack(side='left')
        self.canvas.pack()
        self.draw_maze()
        self.root.bind("<Key>", self.move)
        self.root.bind("p", lambda e: self.toggle_pause())
        self.set_difficulty(self.difficulty_var.get())
        f = self.difficulty_factor()
        for e in self.enemies:
            e['dx'] = int(e['dx'] * f) if e['dx'] != 0 else 0
            e['dy'] = int(e['dy'] * f) if e['dy'] != 0 else 0
            if e['dx'] == 0 and e['dy'] == 0:
                e['dx'] = 1
        self.tick_ms = max(25, int(50 / f))
        self.run_game_loop()
        self.root.mainloop()

    def run_game_loop(self):
        if not self.paused:
            self.move_enemies()
            self.draw_entities()
            self.check_collisions()
            self.score += 1
            self.root.title(f"Score: {self.score} | High: {self.high_score}")
        self.root.after(self.tick_ms, self.run_game_loop)

    def draw_maze(self):
        self.walls = [
            (50, 50, 350, 70),
            (50, 150, 150, 350),
            (200, 100, 220, 300),
            (250, 250, 350, 270)
        ]
        if self.img_exit:
            self.canvas.create_image(380, 380, image=self.img_exit) # Centered at 380,380 (since exit is 360-400, center is 380)
        else:
            self.canvas.create_rectangle(360, 360, 400, 400, fill="green")

        for w in self.walls:
            if self.img_wall:
                # Tiling logic is complex for canvas, so we just stretch or center? 
                # Let's just place one distinct image or multiple?
                # For simplicity, fill with grey but put one texture icon to show it's a wall
                self.canvas.create_rectangle(w, fill="grey")
                # Center of wall
                cx = (w[0] + w[2]) / 2
                cy = (w[1] + w[3]) / 2
                self.canvas.create_image(cx, cy, image=self.img_wall)
            else:
                self.canvas.create_rectangle(w, fill="grey")

    def draw_entities(self):
        self.canvas.delete("p")
        self.canvas.delete("e")
        # Player
        # Player
        if self.img_player:
             self.canvas.create_image(self.player[0]+10, self.player[1]+10, image=self.img_player, tags="p")
        else:
             self.canvas.create_oval(self.player[0], self.player[1], self.player[0]+20, self.player[1]+20, fill="orange", tags="p")
        
        # Enemies (Reuse player image or default?) Prompt didn't specify enemy sprite, just player.
        # User request: "akatsuki_member.png (Replaces Orange Circle (The Player))"
        # Wait, the prompt says "Replaces the Orange Circle (The Player)". 
        # But enemies are red circles. 
        # I'll keep enemies as red circles as no sprite was requested for them explicitly, 
        # or reuse akatsuki member if it makes sense (maybe we are escaping FROM them? No, we are playing AS akatsuki member?)
        # "Akatsuki Maze" -> Maybe we are the Akatsuki member?
        # Yes, prompt says "akatsuki_member.png ... Replaces the Orange Circle (The Player)".
        # So enemies stay shapes or use default.
        for e in self.enemies:
            self.canvas.create_oval(e['x'], e['y'], e['x']+20, e['y']+20, fill="red", tags="e")

    def move(self, event):
        dx, dy = 0, 0
        if event.keysym == 'Up': dy = -20
        if event.keysym == 'Down': dy = 20
        if event.keysym == 'Left': dx = -20
        if event.keysym == 'Right': dx = 20
        
        new_x = self.player[0] + dx
        new_y = self.player[1] + dy
        
        # Check bounds
        if new_x < 0 or new_x > 380 or new_y < 0 or new_y > 380:
            return

        # Check walls
        player_rect = (new_x, new_y, new_x+20, new_y+20)
        hit_wall = False
        for w in self.walls:
            # Simple interaction check (box overlap)
            if not (player_rect[2] <= w[0] or player_rect[0] >= w[2] or player_rect[3] <= w[1] or player_rect[1] >= w[3]):
                hit_wall = True
                break
        
        if not hit_wall:
            self.player[0] = new_x
            self.player[1] = new_y
    
    def move_enemies(self):
        for e in self.enemies:
            e['x'] += e['dx']
            e['y'] += e['dy']
            
            # Simple bounce logic based on limits
            if e['dx'] != 0:
                if e['x'] < e['limit'][0] or e['x'] > e['limit'][1]: e['dx'] *= -1
            if e['dy'] != 0:
                if e['y'] < e['limit'][0] or e['y'] > e['limit'][1]: e['dy'] *= -1

    def check_collisions(self):
        # Exit
        if abs(self.player[0]-self.exit[0]) < 20 and abs(self.player[1]-self.exit[1]) < 20:
             if self.score >= 0:
                messagebox.showinfo("Win", "Escaped the Hideout!")
                self.audio_play("victory")
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
                self.reset_game()
        
        # Enemies
        p_rect = [self.player[0], self.player[1], self.player[0]+20, self.player[1]+20]
        for e in self.enemies:
            e_rect = [e['x'], e['y'], e['x']+20, e['y']+20]
            if not(p_rect[2]<=e_rect[0] or p_rect[0]>=e_rect[2] or p_rect[3]<=e_rect[1] or p_rect[1]>=e_rect[3]):
                messagebox.showerror("Caught", "Zetsu caught you!")
                self.audio_play("defeat")
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
                self.reset_game()

    def reset_game(self):
        self.player = [20, 20]
        self.score = 0
        self.root.title(f"Score: {self.score} | High: {self.high_score}")


    def update(self): pass
    def draw(self): pass

if __name__ == "__main__":
    game = AkatsukiMaze()
    game.start_game()

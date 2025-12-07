"""
Chunin Exam - Simplified Question System
Requirements:
  - Python 3.8+
  - Pillow (optional, for background): pip install Pillow
"""

import os
import json
import random
import threading
import tkinter as tk
import sys
from tkinter import messagebox
from tkinter import ttk, font
from typing import List, Tuple, Dict, Any, Optional

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None

# ---------------------------
# Base Game Class
# ---------------------------
class NarutoGame:
    def __init__(self, title: str, w: int, h: int):
        self.score = 0
        self.high_score = 0
        self.paused = False
        self._difficulty_level = "Medium"
        # Difficulty affects timer and lives
        self._difficulty_map = {"Easy": 0.75, "Medium": 1.0, "Hard": 1.3}
        self._load_high_score()

    def set_difficulty(self, level: str):
        self._difficulty_level = level

    def difficulty_factor(self) -> float:
        return self._difficulty_map.get(self._difficulty_level, 1.0)

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            messagebox.showinfo("Paused", "Game paused. Press 'p' to resume.")

    def _load_high_score(self):
        try:
            with open("high_score.json", "r", encoding="utf-8") as f:
                self.high_score = json.load(f).get("naruto_quiz", 0)
        except Exception:
            self.high_score = 0

    def save_high_score(self):
        try:
            with open("high_score.json", "w", encoding="utf-8") as f:
                json.dump({"naruto_quiz": self.high_score}, f)
        except Exception as e:
            print("Could not save high score:", e)

# ---------------------------
# QUESTION DATA (Categorized)
# ---------------------------
QUESTIONS_BY_TIER: Dict[str, List[Tuple[str, str]]] = {
    "Easy": [
        ("What is Naruto’s favorite food?", "Ramen"),
        ("Who is the sensei of Team 7?", "Kakashi Hatake"),
        ("What village does Naruto live in?", "Konoha"),
        ("Which eye technique does the Uchiha clan possess?", "Sharingan"),
        ("Who is Sasuke’s older brother?", "Itachi Uchiha"),
        ("What is the name of the Nine-Tailed Fox inside Naruto?", "Kurama"),
        ("Who became the Fifth Hokage?", "Tsunade"),
        ("What is Naruto’s signature blue energy sphere attack called?", "Rasengan"),
        ("Who is known as the 'Copy Ninja'?", "Kakashi Hatake"),
        ("Which character is famous for saying 'What a drag...'?", "Shikamaru Nara"),
    ],
    "Medium": [
        ("Who killed the Third Hokage (Hiruzen Sarutobi)?", "Orochimaru"),
        ("What is the name of the organization hunting the Tailed Beasts?", "Akatsuki"),
        ("Who is Naruto’s father?", "Minato Namikaze"),
        ("Which Akatsuki member is Itachi’s shark-like partner?", "Kisame Hoshigaki"),
        ("What is the name of Zabuza’s partner (the ice user)?", "Haku"),
        ("Who taught Naruto the Rasengan?", "Jiraiya"),
        ("What is the name of the puppet master in the Akatsuki?", "Sasori"),
        ("Which character opens the 'Eight Inner Gates'?", "Might Guy"),
        ("Who is the Jinchuriki of the One-Tail (Shukaku)?", "Gaara"),
        ("Finish the team name: Ino-Shika-____?", "Choji"),
    ],
    "Hard": [
        ("What is the name of the sword wielded by Kisame Hoshigaki?", "Samehada"),
        ("Who originally gave Nagato his Rinnegan eyes?", "Madara Uchiha"),
        ("What is the name of the secret ANBU division led by Danzo?", "Root"),
        ("How many hearts does Kakuzu have?", "5"),
        ("Who is known as the 'White Fang of the Leaf'?", "Sakumo Hatake"),
        ("Which village is Hidan from?", "Yugakure"),
        ("What is the name of the giant slug summoned by Tsunade?", "Katsuyu"),
        ("Who founded the original Akatsuki alongside Nagato and Konan?", "Yahiko"),
        ("What is the name of the Second Hokage?", "Tobirama Senju"),
        ("Who was revealed to be the man behind the orange spiral mask (Tobi)?", "Obito Uchiha"),
    ]
}

# ---------------------------
# Main Game UI: ChuninExam
# ---------------------------
class ChuninExam(NarutoGame):
    def __init__(self):
        super().__init__("Chunin Exam", 600, 420)

        self.window = tk.Tk()
        self.window.title(f"Score: {self.score} | High: {self.high_score}")
        self.window.geometry("600x420")
        self.window.resizable(True, True)

        self.difficulty_var = tk.StringVar(value="Medium")
        self.questions: List[Tuple[str, str]] = []
        self.current_q = 0
        self.lives = 3
        self.time_left = 15
        self.timer_id: Optional[str] = None
        self.entry: Optional[tk.Entry] = None
        self.timer_label: Optional[tk.Label] = None

        self.theme = {
            "bg": "#0b0f1a",
            "panel": "#141a29",
            "accent": "#ff8f00",
            "accent2": "#f44336",
            "text": "#e6e9ef",
            "muted": "#b0b8c4",
            "button": "#263043",
            "button_hover": "#32425f",
            "input_bg": "#1e2433"
        }
        self.window.configure(bg=self.theme["bg"])
        self._base_w = 600
        self._base_h = 420
        self._scale = 1.0
        self.font_title = font.Font(family="Arial", size=20, weight="bold")
        self.font_subtitle = font.Font(family="Arial", size=14, weight="bold")
        self.font_body = font.Font(family="Arial", size=12)
        self.font_timer = font.Font(family="Arial", size=14)
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass
        self.style.configure("TFrame", background=self.theme["bg"])
        self.style.configure("Panel.TFrame", background=self.theme["panel"])
        self.style.configure("Accent.TButton", background=self.theme["button"], foreground=self.theme["text"], padding=6)
        self.style.map("Accent.TButton", background=[("active", self.theme["button_hover"])])
        self.bg_img = None
        base_path = os.path.dirname(os.path.abspath(__file__))
        bg_file = os.path.join(base_path, "naruto_bg.jpg")
        
        if not os.path.exists(bg_file):
            bg_file = os.path.join(base_path, "assets", "ibiki_morino_bg.jpg")

        if Image and ImageTk and os.path.exists(bg_file):
            try:
                self._bg_original = Image.open(bg_file)
                img = self._bg_original.resize((self._base_w, self._base_h), Image.Resampling.LANCZOS)
                self.bg_img = ImageTk.PhotoImage(img)
            except Exception as e:
                print("Background image load error:", e)
        else:
            self._bg_original = None

        self.bg_label = tk.Label(self.window, image=self.bg_img) if self.bg_img else None
        if self.bg_label:
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bg_label.lower()

        self.top = tk.Frame(self.window, bg=self.theme["panel"])
        self.top.pack(anchor="nw", pady=6, padx=8, fill="x")
        tk.Label(self.top, text="Rank:", fg=self.theme["text"], bg=self.theme["panel"], font=self.font_body).pack(side="left")
        self.rank_combo = ttk.Combobox(self.top, textvariable=self.difficulty_var, values=["Easy", "Medium", "Hard"], state="readonly", width=10)
        self.rank_combo.pack(side="left", padx=6)
        self.rank_combo.bind("<<ComboboxSelected>>", lambda _: self._restart_exam())
        self.restart_btn = tk.Button(self.top, text="Restart Exam", command=self._restart_exam, bg=self.theme["button"], fg=self.theme["text"], activebackground=self.theme["button_hover"], padx=10, pady=4)
        self.restart_btn.pack(side="left", padx=6)
        self._make_hoverable(self.restart_btn)
        self.window.bind("<Configure>", self._on_resize)

    def start_game(self):
        self.window.bind("p", lambda e: self.toggle_pause())
        self.window.bind("<Return>", lambda e: self.submit_via_enter_key())
        self._restart_exam()
        self.window.mainloop()

    def _restart_exam(self):
        self.score = 0
        self.current_q = 0
        self.questions = []
        self.set_initial_lives()
        self.render_loading()
        self.fetch_questions_async()

    def set_initial_lives(self):
        level = self.difficulty_var.get()
        self.set_difficulty(level)
        # Easy = 4 lives, Medium = 3, Hard = 2
        if level == "Easy": self.lives = 4
        elif level == "Medium": self.lives = 3
        else: self.lives = 2

    # Show loading screen
    def render_loading(self):
        for w in self.window.winfo_children():
            if w is self.top or w is self.bg_label:
                continue
            w.destroy()
        if self.bg_label:
            self.bg_label.lower()
        msg = tk.Label(self.window, text="Summoning Questions...", font=self.font_title, fg=self.theme["text"], bg=self.theme["bg"])
        msg.pack(pady=40)
        self.loading_bar = ttk.Progressbar(self.window, mode="indeterminate")
        self.loading_bar.pack(pady=10, fill="x", padx=40)
        self.loading_bar.start(10)

    # Show a question
    def show_question(self):
        children = self.window.winfo_children()
        for w in children:
            if w is self.top or w is self.bg_label:
                continue
            w.destroy()
        if self.bg_label:
            self.bg_label.lower()

        # Check Game Over / Win
        if self.lives <= 0:
            self.end_game_screen(success=False)
            return

        if not self.questions or self.current_q >= len(self.questions):
            self.end_game_screen(success=True)
            return

        # Display Logic
        q_text, answer = self.questions[self.current_q]
        rank_name = {"Easy": "Genin", "Medium": "Chunin", "Hard": "Jonin"}
        rank = rank_name.get(self.difficulty_var.get(), "Ninja")
        
        self.window.title(f"Rank: {rank} | Score: {self.score} | High: {self.high_score}")
        
        header = tk.Label(self.window, text=f"Question {self.current_q + 1} (Lives: {self.lives})", font=self.font_subtitle, fg=self.theme["text"], bg=self.theme["bg"])
        header.pack(pady=10)
        wrap = max(300, int(self.window.winfo_width() * 0.9))
        q_wrap = tk.Frame(self.window, bg=self.theme["panel"], padx=10, pady=10)
        q_wrap.pack(pady=10, padx=20, fill="x")
        q_lbl = tk.Label(q_wrap, text=q_text, font=self.font_body, wraplength=wrap, fg=self.theme["text"], bg=self.theme["panel"]) 
        q_lbl.pack(fill="x")

        # Timer Logic
        base_time = 15
        if self._difficulty_level == "Easy": self.time_left = 20
        elif self._difficulty_level == "Hard": self.time_left = 10
        else: self.time_left = 15

        self.timer_label = tk.Label(self.window, text=f"Time: {self.time_left}", font=self.font_timer, fg=self.theme["accent2"], bg=self.theme["bg"])
        self.timer_label.pack(pady=2)
        self.entry = tk.Entry(self.window, width=50, font=self.font_body, bg=self.theme["input_bg"], fg=self.theme["text"], insertbackground=self.theme["text"])
        self.entry.pack(pady=15, padx=20, fill="x")
        self.entry.focus_set()

        btn_frame = tk.Frame(self.window, bg=self.theme["bg"])
        btn_frame.pack(pady=10)
        submit_btn = tk.Button(btn_frame, text="Submit Jutsu", command=lambda: self.check_answer(answer), bg=self.theme["button"], fg=self.theme["text"], activebackground=self.theme["button_hover"], padx=12, pady=6)
        submit_btn.pack(side="left", padx=8)
        self._make_hoverable(submit_btn)
        skip_btn = tk.Button(btn_frame, text="Flee (Skip)", command=self.skip_question, bg=self.theme["button"], fg=self.theme["text"], activebackground=self.theme["button_hover"], padx=12, pady=6)
        skip_btn.pack(side="left", padx=8)
        self._make_hoverable(skip_btn)

        self.start_timer()

    def end_game_screen(self, success):
        self.window.title(f"Game Over | Score: {self.score}")
        msg = "Mission Complete!" if success else "Mission Failed!"
        color = self.theme["accent"] if success else self.theme["accent2"]
        tk.Label(self.window, text=msg, font=self.font_title, fg=color, bg=self.theme["bg"]).pack(pady=40)
        tk.Label(self.window, text=f"Final Score: {self.score}", font=self.font_subtitle, fg=self.theme["text"], bg=self.theme["bg"]).pack(pady=10)
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
            tk.Label(self.window, text="New High Score!", font=self.font_body, fg=self.theme["accent"], bg=self.theme["bg"]).pack()

    def submit_via_enter_key(self):
        # Helper to submit if user presses Enter
        if self.questions and self.current_q < len(self.questions):
             _, answer = self.questions[self.current_q]
             self.check_answer(answer)

    def start_timer(self):
        if self.timer_id:
            try: self.window.after_cancel(self.timer_id)
            except: pass
        self._tick_timer()

    def _tick_timer(self):
        if self.paused:
            self.timer_id = self.window.after(250, self._tick_timer)
            return
        if self.time_left > 0:
            self.time_left -= 1
            if self.timer_label:
                col = "#4caf50" if self.time_left > 10 else ("#ffc107" if self.time_left > 5 else self.theme["accent2"]) 
                self.timer_label.config(text=f"Time: {self.time_left}", fg=col)
            self.timer_id = self.window.after(1000, self._tick_timer)
        else:
            messagebox.showwarning("Time's up", "Too slow! The enemy escaped.")
            self.lives -= 1
            self.current_q += 1
            self.show_question()

    def check_answer(self, correct_answer: str):
        if self.timer_id:
            try: self.window.after_cancel(self.timer_id)
            except: pass

        user_ans = (self.entry.get() if self.entry else "").strip().lower()
        corr_ans = correct_answer.strip().lower()

        # Logic: Exact match OR correct answer is contained in user answer (e.g. "Hidden Leaf" in "Hidden Leaf Village")
        # OR user answer is contained in correct answer (e.g. "Guy" in "Might Guy")
        is_correct = False
        if user_ans == corr_ans:
            is_correct = True
        elif len(user_ans) > 3 and (user_ans in corr_ans or corr_ans in user_ans):
            is_correct = True
        
        # Specific overrides
        if "konoha" in user_ans and "konoha" in corr_ans: is_correct = True
        if "root" in user_ans and "root" in corr_ans: is_correct = True

        if is_correct:
            self.score += 1
        else:
            messagebox.showinfo("Result", f"Wrong! \nCorrect Answer: {correct_answer}")
            self.lives -= 1

        self.current_q += 1
        self.show_question()

    def skip_question(self):
        self.lives -= 1
        self.current_q += 1
        if self.timer_id:
            try: self.window.after_cancel(self.timer_id)
            except: pass
        self.show_question()

    # -----------------------
    # Async Question Fetching
    # -----------------------
    def fetch_questions_async(self):
        t = threading.Thread(target=self._fetch_and_prepare, daemon=True)
        t.start()

    def _fetch_and_prepare(self):
        # 1. Get difficulty from dropdown
        difficulty = self.difficulty_var.get()
        
        # 2. Select the correct list from our new dictionary
        # Default to Medium if something breaks
        pool = QUESTIONS_BY_TIER.get(difficulty, QUESTIONS_BY_TIER["Medium"])[:]
        
        # 3. Shuffle and pick 10
        random.shuffle(pool)
        self.questions = pool[:10]
        
        self.current_q = 0
        self.window.after(0, self._stop_loading_and_show)

    def _stop_loading_and_show(self):
        try:
            if hasattr(self, "loading_bar") and self.loading_bar:
                self.loading_bar.stop()
                self.loading_bar.destroy()
        except Exception:
            pass
        self.show_question()

    def _make_hoverable(self, btn: tk.Button):
        normal = self.theme["button"]
        hover = self.theme["button_hover"]
        active = self.theme["accent"]
        def on_enter(e):
            btn.configure(bg=hover)
        def on_leave(e):
            btn.configure(bg=normal)
        def on_press(e):
            btn.configure(bg=active)
        def on_release(e):
            btn.configure(bg=hover)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<ButtonPress-1>", on_press)
        btn.bind("<ButtonRelease-1>", on_release)

    def _on_resize(self, event):
        try:
            w = max(300, self.window.winfo_width())
            h = max(200, self.window.winfo_height())
            sx = w / self._base_w
            sy = h / self._base_h
            self._scale = min(max(0.8, (sx + sy) / 2), 1.6)
            self.font_title.configure(size=int(20 * self._scale))
            self.font_subtitle.configure(size=int(14 * self._scale))
            self.font_body.configure(size=int(12 * self._scale))
            self.font_timer.configure(size=int(14 * self._scale))
            if self._bg_original:
                try:
                    img = self._bg_original.resize((w, h), Image.Resampling.LANCZOS)
                    self.bg_img = ImageTk.PhotoImage(img)
                    if self.bg_label:
                        self.bg_label.configure(image=self.bg_img)
                        self.bg_label.image = self.bg_img
                except Exception:
                    pass
        except Exception:
            pass

# ---------------------------
# Run
# ---------------------------
if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--test-ui":
            g = ChuninExam()
            g.render_loading()
            exists_loading = hasattr(g, "loading_bar") and g.loading_bar is not None
            print("loading_bar_created:", bool(exists_loading))
            g.questions = [("Test question?", "Answer")]
            g._stop_loading_and_show()
            print("question_header_exists:", any(isinstance(w, tk.Label) and "Question" in (w.cget("text") or "") for w in g.window.winfo_children()))
            g.window.geometry("900x630")
            g.window.update_idletasks()
            g._on_resize(None)
            print("font_title_size:", g.font_title.cget("size"))
            has_hover = bool(g.restart_btn.bind("<Enter>"))
            print("restart_btn_hover_bound:", has_hover)
            print("ui_smoke_tests_completed")
        else:
            game = ChuninExam()
            game.start_game()
    except Exception as e:
        print("Critical error:", e)

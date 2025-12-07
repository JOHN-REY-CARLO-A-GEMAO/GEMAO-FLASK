import pygame
import random
import sys
import os
from base_game import NarutoGame

class ShurikenToss(NarutoGame):
    def __init__(self):
        super().__init__("Naruto Shuriken Toss", 800, 600)
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)
        self.clock = pygame.time.Clock()
        self.targets = []
        self.shurikens = []
        self.gravity = 0.5
        self.game_state = "START"
        self.start_ticks = 0
        self.time_ms = 60000
        
        # Load assets
        self.assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        self.shuriken_img = pygame.transform.scale(pygame.image.load(os.path.join(self.assets_dir, "shuriken.png")).convert_alpha(), (30, 30))
        self.target_img = pygame.transform.scale(pygame.image.load(os.path.join(self.assets_dir, "target.png")).convert_alpha(), (40, 40))

    def start_game(self):
        self.is_running = True
        self.font = pygame.font.Font(None, 36)
        
        while self.is_running:
            self.screen.fill((30, 30, 30))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    self.toggle_pause()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1: self.set_difficulty("Easy")
                    if event.key == pygame.K_2: self.set_difficulty("Medium")
                    if event.key == pygame.K_3: self.set_difficulty("Hard")
                
                if self.game_state == "START":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.game_state = "RUNNING"
                        self.reset_game()
                
                elif self.game_state == "RUNNING":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = pygame.mouse.get_pos()
                        # Calculate velocity for arc
                        start_x = self.width // 2
                        start_y = self.height
                        dx = mx - start_x
                        dy = my - start_y
                        vx = dx * 0.05
                        vy = dy * 0.05 - 10 # Add upward boost
                        self.shurikens.append([start_x, start_y, vx, vy])
                
                elif self.game_state == "GAMEOVER":
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        self.game_state = "RUNNING"
                        self.reset_game()

            if self.game_state == "RUNNING" and not self.paused:
                self.update()
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

    def reset_game(self):
        self.targets = []
        self.shurikens = []
        self.score = 0
        self.start_ticks = pygame.time.get_ticks()
        f = self.difficulty_factor()
        self.time_ms = int(60000 / (1 if f == 1.0 else (0.8 if f < 1.0 else 1.3)))

    def update(self):
        # Spawn targets
        f = self.difficulty_factor()
        spawn_chance = 60 if f == 1.0 else (70 if f < 1.0 else 45)
        if random.randint(0, spawn_chance) == 0:
            tx = random.randint(50, self.width-50)
            ty = random.randint(50, 300)
            base_speed = 2
            dx = random.choice([-base_speed, base_speed])
            dx = int(dx * f)
            self.targets.append([tx, ty, dx]) # x, y, speed_x

        # Move Targets
        for t in self.targets:
            t[0] += t[2]
            if t[0] < 0 or t[0] > self.width - 40:
                t[2] *= -1

        # Move Shurikens (Arc Physics)
        for s in self.shurikens[:]:
            s[2] += 0 # No air resistance on X for now
            s[3] += self.gravity # Gravity on Y
            s[0] += s[2]
            s[1] += s[3]
            
            # Remove if off screen
            if s[1] > self.height or s[0] < 0 or s[0] > self.width:
                self.shurikens.remove(s)

        # Collision
        for s in self.shurikens:
            s_rect = pygame.Rect(s[0]-5, s[1]-5, 10, 10)
            for t in self.targets[:]:
                t_rect = pygame.Rect(t[0], t[1], 40, 40)
                if s_rect.colliderect(t_rect):
                    self.score += 10
                    self.targets.remove(t)
                    if s in self.shurikens: self.shurikens.remove(s)
                    break
        elapsed = pygame.time.get_ticks() - self.start_ticks
        remaining = max(0, self.time_ms - elapsed)
        if remaining == 0:
            self.game_state = "GAMEOVER"
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()

    def draw(self):
        if self.game_state == "START":
            txt = self.font.render("Click to Toss", True, (255, 255, 255))
            self.screen.blit(txt, (300, 250))
            hi = self.font.render(f"High: {self.high_score}", True, (255, 255, 255))
            self.screen.blit(hi, (10, 10))
            dtxt = self.font.render(f"Diff: {self.difficulty} (1-3)", True, (255, 255, 0))
            self.screen.blit(dtxt, (10, 40))
            
        elif self.game_state == "GAMEOVER":
            txt = self.font.render(f"Game Over! Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(txt, (250, 250))
            hi = self.font.render(f"High: {self.high_score}", True, (255, 255, 255))
            self.screen.blit(hi, (10, 10))
            
        elif self.game_state == "RUNNING":
            for t in self.targets:
                self.screen.blit(self.target_img, (t[0], t[1]))
                
            for s in self.shurikens:
                # Center the shuriken image on the coordinates
                self.screen.blit(self.shuriken_img, (s[0]-5, s[1]-5))
                
            score_text = self.font.render(f"Score: {self.score}", True, (255, 140, 0))
            self.screen.blit(score_text, (10, 10))
            hi = self.font.render(f"High: {self.high_score}", True, (255, 255, 255))
            self.screen.blit(hi, (10, 40))
            dtxt = self.font.render(f"Diff: {self.difficulty}", True, (255, 255, 0))
            self.screen.blit(dtxt, (10, 70))
            elapsed = pygame.time.get_ticks() - self.start_ticks
            remaining = max(0, (self.time_ms - elapsed) // 1000)
            timer_text = self.font.render(f"Time: {remaining}s", True, (255, 255, 255))
            self.screen.blit(timer_text, (10, 70))
            self.screen.blit(timer_text, (10, 100))
            if self.paused:
                ptxt = self.font.render("Paused (P)", True, (255, 255, 0))
                self.screen.blit(ptxt, (320, 300))

if __name__ == "__main__":
    game = ShurikenToss()
    game.start_game()

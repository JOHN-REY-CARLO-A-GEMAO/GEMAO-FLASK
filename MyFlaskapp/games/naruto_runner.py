import pygame
import sys
import os

from base_game import NarutoGame

class NarutoRunner(NarutoGame):
    def __init__(self):
        super().__init__("Naruto Runner", 800, 400)
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.player_y = 300
        self.velocity = 0
        self.jump_count = 0
        self.obstacle_x = 800
        self.game_state = "START"
        self.bg_x = 0
        
        # Load assets
        self.assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        self.player_img = pygame.transform.scale(pygame.image.load(os.path.join(self.assets_dir, "naruto_run.png")).convert_alpha(), (40, 60))
        self.rock_img = pygame.transform.scale(pygame.image.load(os.path.join(self.assets_dir, "rock.png")).convert_alpha(), (40, 40))
        self.bg_img = pygame.transform.scale(pygame.image.load(os.path.join(self.assets_dir, "forest_bg.png")).convert(), (800, 400))
        


    def start_game(self):
        self.is_running = True
        self.font = pygame.font.Font(None, 36)
        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.is_running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    self.toggle_pause()
                
                if self.game_state == "START":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_1: self.set_difficulty("Easy")
                        if event.key == pygame.K_2: self.set_difficulty("Medium")
                        if event.key == pygame.K_3: self.set_difficulty("Hard")
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.game_state = "RUNNING"
                        self.reset_game()
                        self.audio_play("victory")
                
                elif self.game_state == "RUNNING":
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        if self.jump_count < 2:
                            f = self.difficulty_factor()
                            self.velocity = -int(15 * (1 if f == 1.0 else (0.9 if f < 1.0 else 1.1)))
                            self.jump_count += 1
                            self.audio_play("victory")
                
                elif self.game_state == "GAMEOVER":
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        self.game_state = "RUNNING"
                        self.reset_game()

            if self.game_state == "RUNNING" and not self.paused:
                self.update()
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

    def reset_game(self):
        self.player_y = 300
        self.velocity = 0
        self.jump_count = 0
        self.obstacle_x = 800
        self.score = 0
        f = self.difficulty_factor()
        self.bg_speed = int(2 * f)
        self.obstacle_speed = int(10 * f)

    def update(self):
        self.player_y += self.velocity
        self.velocity += 1
        if self.player_y >= 300:
            self.player_y = 300
            self.jump_count = 0
            self.velocity = 0
        
        self.bg_x -= self.bg_speed
        if self.bg_x <= -800: self.bg_x = 0
        
        self.obstacle_x -= self.obstacle_speed
        if self.obstacle_x < -50:
            self.obstacle_x = 800
            self.score += 1
            self.audio_play("victory")

        # Hitbox
        p_rect = pygame.Rect(100, self.player_y, 40, 60)
        o_rect = pygame.Rect(self.obstacle_x, 320, 40, 40)
        if p_rect.colliderect(o_rect):
            self.game_state = "GAMEOVER"
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            self.audio_play("defeat")

    def draw(self):
        # Draw tiled background
        self.screen.blit(self.bg_img, (self.bg_x, 0))
        self.screen.blit(self.bg_img, (self.bg_x + 800, 0))
        
        if self.game_state == "START":
            txt = self.font.render("Press SPACE to Start", True, (255, 255, 255))
            self.screen.blit(txt, (300, 200))
            hi = self.font.render(f"High: {self.high_score}", True, (255, 255, 255))
            self.screen.blit(hi, (10, 10))
            dtxt = self.font.render(f"Diff: {self.difficulty} (1-3)", True, (255, 255, 0))
            self.screen.blit(dtxt, (10, 40))
        
        elif self.game_state == "RUNNING":
            self.screen.blit(self.player_img, (100, self.player_y))
            self.screen.blit(self.rock_img, (self.obstacle_x, 320))
            score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_text, (10, 10))
            hi = self.font.render(f"High: {self.high_score}", True, (255, 255, 255))
            self.screen.blit(hi, (10, 40))
            if self.paused:
                ptxt = self.font.render("Paused (P)", True, (255, 255, 0))
                self.screen.blit(ptxt, (320, 200))
            
        elif self.game_state == "GAMEOVER":
            txt = self.font.render(f"Game Over! Score: {self.score}", True, (255, 255, 255))
            retry = self.font.render("Press R to Restart", True, (255, 255, 255))
            self.screen.blit(txt, (300, 150))
            self.screen.blit(retry, (300, 200))
            hi = self.font.render(f"High: {self.high_score}", True, (255, 255, 255))
            self.screen.blit(hi, (10, 10))

if __name__ == "__main__":
    game = NarutoRunner()
    game.start_game()

import pygame
import random
import sys
from base_game import NarutoGame

class ShadowClone(NarutoGame):
    def __init__(self):
        super().__init__("Shadow Clone Snake", 600, 400)
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.clones = [(100, 100)]
        self.direction = (20, 0)
        self.scroll = [random.randint(0, 29)*20, random.randint(0, 19)*20]
        self.obstacles = []
        count = 5
        for _ in range(count):
             self.obstacles.append((random.randint(0, 29)*20, random.randint(0, 19)*20))
             
        # Load Images
        import os
        base_path = os.path.dirname(__file__)
        assets_path = os.path.join(base_path, 'assets')
        
        def load_img(name, scale=None):
            path = os.path.join(assets_path, name)
            if os.path.exists(path):
                img = pygame.image.load(path)
                if scale:
                    img = pygame.transform.scale(img, scale)
                return img
            return None

        self.img_head = load_img("naruto_head.png", (20, 20))
        self.img_body = load_img("naruto_body.png", (20, 20))
        self.img_scroll = load_img("scroll_secret.png", (20, 20))

    def start_game(self):
        self.is_running = True
        font = pygame.font.Font(None, 36)
        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.is_running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP: self.direction = (0, -20)
                    if event.key == pygame.K_DOWN: self.direction = (0, 20)
                    if event.key == pygame.K_LEFT: self.direction = (-20, 0)
                    if event.key == pygame.K_RIGHT: self.direction = (20, 0)
                    if event.key == pygame.K_p: self.toggle_pause()
                    if event.key == pygame.K_1: self.set_difficulty("Easy")
                    if event.key == pygame.K_2: self.set_difficulty("Medium")
                    if event.key == pygame.K_3: self.set_difficulty("Hard")

            if not self.paused:
                self.update()
            self.draw()
            
            score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_text, (10, 10))
            hi_text = font.render(f"High: {self.high_score}", True, (255, 255, 255))
            self.screen.blit(hi_text, (10, 40))
            diff_text = font.render(f"Diff: {self.difficulty} (1-3)", True, (200, 200, 0))
            self.screen.blit(diff_text, (10, 70))
            if self.paused:
                ptxt = font.render("Paused (P)", True, (255, 255, 0))
                self.screen.blit(ptxt, (220, 180))
            
            pygame.display.flip()
            # Speed increases with score
            f = self.difficulty_factor()
            speed = int((10 + (self.score // 2)) * f)
            self.clock.tick(max(10, speed))
        pygame.quit()
        sys.exit()

    def update(self):
        head = self.clones[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # Wrapping
        new_head = (new_head[0] % self.width, new_head[1] % self.height)
        
        if new_head == tuple(self.scroll):
            self.score += 1
            self.clones.insert(0, new_head)
            self.scroll = [random.randint(0, (self.width//20)-1)*20, random.randint(0, (self.height//20)-1)*20]
        elif new_head in self.obstacles or new_head in self.clones[1:]:
             self.game_state = "GAMEOVER"
             self.is_running = False
             if self.score > self.high_score:
                 self.high_score = self.score
                 self.save_high_score()
        else:
            self.clones.insert(0, new_head)
            self.clones.pop()

    def draw(self):
        self.screen.fill((50, 50, 50))
        # Draw Clones (Snake) with Gradient
        # Draw Clones (Snake)
        for i, c in enumerate(self.clones):
            if i == 0 and self.img_head:
                self.screen.blit(self.img_head, (c[0], c[1]))
            elif self.img_body:
                self.screen.blit(self.img_body, (c[0], c[1]))
            else:
                color_val = max(50, 255 - (i * 5))
                pygame.draw.rect(self.screen, (255, color_val, 0), (c[0], c[1], 20, 20))
            
        # Draw Scroll (Food)
        if self.img_scroll:
            self.screen.blit(self.img_scroll, (self.scroll[0], self.scroll[1]))
        else:
            pygame.draw.rect(self.screen, (0, 255, 0), (self.scroll[0], self.scroll[1], 20, 20))
        
        # Draw Obstacles (Kunai/Traps)
        for o in self.obstacles:
             pygame.draw.line(self.screen, (200, 200, 200), (o[0], o[1]), (o[0]+20, o[1]+20), 3)
             pygame.draw.line(self.screen, (200, 200, 200), (o[0]+20, o[1]), (o[0], o[1]+20), 3)

if __name__ == "__main__":
    game = ShadowClone()
    game.start_game()

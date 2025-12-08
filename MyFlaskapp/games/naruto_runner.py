import pygame
import sys
import os

from base_game import NarutoGame

class NarutoRunner(NarutoGame):
    def __init__(self):
        super().__init__("Naruto Runner", 800, 400)
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)
        self.clock = pygame.time.Clock()

        # Player state
        self.player_y = 300
        self.velocity = 0
        self.jump_count = 0

        # Obstacle / world state
        self.obstacle_x = 800
        self.bg_x = 0

        # Game state
        self.game_state = "START"  # START, RUNNING, GAMEOVER
        self.paused = False

        # Speeds (set in reset_game)
        self.bg_speed = 2
        self.obstacle_speed = 10

        # Load assets
        self.assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        self.player_img = pygame.transform.scale(
            pygame.image.load(os.path.join(self.assets_dir, "naruto_run.png")).convert_alpha(), (40, 60)
        )
        self.rock_img = pygame.transform.scale(
            pygame.image.load(os.path.join(self.assets_dir, "rock.png")).convert_alpha(), (40, 40)
        )
        self.bg_img = pygame.transform.scale(
            pygame.image.load(os.path.join(self.assets_dir, "forest_bg.png")).convert(), (800, 400)
        )

    def start_game(self):
        self.is_running = True
        self.font = pygame.font.Font(None, 36)
        self.play_background_music()  # Start background music if available

        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                    self.stop_background_music()

                # Pause toggle
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    self.toggle_pause()
                    if self.paused:
                        self.pause_background_music()
                    else:
                        self.unpause_background_music()

                # State-specific keys
                if self.game_state == "START":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_1:
                            self.set_difficulty("Easy")
                        elif event.key == pygame.K_2:
                            self.set_difficulty("Medium")
                        elif event.key == pygame.K_3:
                            self.set_difficulty("Hard")
                        elif event.key == pygame.K_m:
                            if self.is_background_music_playing():
                                self.pause_background_music()
                            else:
                                self.unpause_background_music()
                        elif event.key == pygame.K_SPACE:
                            # Start the game
                            self.game_state = "RUNNING"
                            self.reset_game()

                elif self.game_state == "RUNNING":
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        # Jump logic (allow double jump)
                        if self.jump_count < 2:
                            f = self.difficulty_factor()
                            multiplier = 1
                            if f == 1.0:
                                multiplier = 1
                            elif f < 1.0:
                                multiplier = 0.9
                            else:
                                multiplier = 1.1
                            self.velocity = -int(15 * multiplier)
                            self.jump_count += 1
                            # If you want a jump sound, use audio_play("jump") and add "jump" sound in base_game.

                elif self.game_state == "GAMEOVER":
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        self.game_state = "RUNNING"
                        self.reset_game()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                        if self.is_background_music_playing():
                            self.pause_background_music()
                        else:
                            self.unpause_background_music()

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
        # Physics
        self.player_y += self.velocity
        self.velocity += 1
        if self.player_y >= 300:
            self.player_y = 300
            self.jump_count = 0
            self.velocity = 0

        # Background scrolling (tile)
        self.bg_x -= self.bg_speed
        if self.bg_x <= -800:
            self.bg_x = 0

        # Obstacle movement and scoring
        self.obstacle_x -= self.obstacle_speed
        if self.obstacle_x < -50:
            # Reset obstacle and increment score.
            # NOTE: removed self.audio_play("victory") here to avoid playing success.mp3 on obstacle reset.
            self.obstacle_x = 800
            self.score += 1
            # If you want an occasional score sound, use something quieter and conditional:
            # if self.score % 5 == 0:
            #     self.audio_play("point")

        # Collision detection
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
            title_txt = self.font.render("Press SPACE to Start", True, (255, 255, 255))
            self.screen.blit(title_txt, (300, 200))

            hi = self.font.render(f"High: {self.high_score}", True, (255, 255, 255))
            self.screen.blit(hi, (10, 10))

            dtxt = self.font.render(f"Diff: {self.difficulty} (1-3)", True, (255, 255, 0))
            self.screen.blit(dtxt, (10, 40))

            music = self.font.render("Press M to Toggle Music", True, (255, 255, 0))
            self.screen.blit(music, (280, 240))

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
            music = self.font.render("Press M to Toggle Music", True, (255, 255, 0))

            self.screen.blit(txt, (300, 150))
            self.screen.blit(retry, (300, 200))
            self.screen.blit(music, (280, 240))

            hi = self.font.render(f"High: {self.high_score}", True, (255, 255, 255))
            self.screen.blit(hi, (10, 10))

if __name__ == "__main__":
    game = NarutoRunner()
    game.start_game()

#!/usr/bin/env python3
"""
Test script to verify background music integration in Naruto games.
This script tests the audio system without launching the full game.
"""

import pygame
import sys
import os

# Add the games directory to the path
sys.path.append(os.path.dirname(__file__))

from base_game import NarutoGame

class TestMusicGame(NarutoGame):
    """Test game to verify music functionality."""
    
    def __init__(self):
        super().__init__("Music Test", 400, 300)
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        
    def start_game(self):
        """Test the music system."""
        self.is_running = True
        
        print("=== Naruto Theme Music Test ===")
        print(f"Background music file: {self._background_music}")
        print(f"Music file exists: {os.path.exists(self._background_music) if self._background_music else False}")
        
        # Start background music
        print("Starting background music...")
        self.play_background_music()
        
        # Test music controls
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        print("Toggling music...")
                        if self.is_background_music_playing():
                            self.pause_background_music()
                            print("Music paused")
                        else:
                            self.unpause_background_music()
                            print("Music resumed")
                    elif event.key == pygame.K_s:
                        print("Stopping music...")
                        self.stop_background_music()
                    elif event.key == pygame.K_p:
                        print("Playing music...")
                        self.play_background_music()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            # Draw test interface
            self.screen.fill((20, 20, 40))
            
            # Title
            title = self.font.render("Naruto Theme Music Test", True, (255, 255, 0))
            self.screen.blit(title, (100, 20))
            
            # Status
            status = "Playing" if self.is_background_music_playing() else "Stopped"
            status_text = self.font.render(f"Music Status: {status}", True, (255, 255, 255))
            self.screen.blit(status_text, (120, 80))
            
            # Instructions
            instructions = [
                "SPACE - Toggle Music",
                "P - Play Music", 
                "S - Stop Music",
                "ESC - Exit"
            ]
            
            y = 120
            for instruction in instructions:
                text = self.font.render(instruction, True, (200, 200, 200))
                self.screen.blit(text, (100, y))
                y += 30
            
            pygame.display.flip()
            self.clock.tick(30)
        
        # Cleanup
        self.stop_background_music()
        pygame.quit()
        print("Music test completed!")
    
    def update(self):
        pass
    
    def draw(self):
        pass

if __name__ == "__main__":
    try:
        test_game = TestMusicGame()
        test_game.start_game()
    except Exception as e:
        print(f"Error during music test: {e}")
        pygame.quit()

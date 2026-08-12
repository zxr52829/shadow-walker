import pygame
import math
from .settings import ITEMS

class ItemEntity:
    def __init__(self, x, y, item_id):
        self.x = x
        self.y = y
        self.item_id = item_id
        self.data = ITEMS[item_id]
        self.size = 16
        self.bob_offset = 0
        self.bob_timer = 0
        
    def update(self):
        self.bob_timer += 0.1
        self.bob_offset = math.sin(self.bob_timer) * 3
        
    def draw(self, screen, camera_x, camera_y):
        rect = pygame.Rect(
            self.x - self.size//2 - camera_x,
            self.y - self.size//2 + self.bob_offset - camera_y,
            self.size,
            self.size
        )
        pygame.draw.rect(screen, self.data['color'], rect)
        pygame.draw.rect(screen, (255, 255, 255), rect, 1)

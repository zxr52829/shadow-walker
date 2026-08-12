import pygame
import random
from .settings import TILE_SIZE, COLORS

class Dungeon:
    def __init__(self, width, height, chapter_data):
        self.width = width
        self.height = height
        self.tiles = [[1 for _ in range(width)] for _ in range(height)]
        self.rooms = []
        self.floor_color = chapter_data['floor_color']
        self.wall_color = chapter_data['wall_color']
        self.exit_pos = None
        self.start_pos = None
        
    def generate(self):
        room_count = random.randint(8, 14)
        min_room_size = 5
        max_room_size = 14
        
        for _ in range(room_count * 4):
            if len(self.rooms) >= room_count:
                break
                
            w = random.randint(min_room_size, max_room_size)
            h = random.randint(min_room_size, max_room_size)
            x = random.randint(1, self.width - w - 1)
            y = random.randint(1, self.height - h - 1)
            
            new_room = pygame.Rect(x, y, w, h)
            overlap = False
            for room in self.rooms:
                if new_room.colliderect(room.inflate(2, 2)):
                    overlap = True
                    break
                    
            if not overlap:
                self.rooms.append(new_room)
                for rx in range(x, x + w):
                    for ry in range(y, y + h):
                        self.tiles[ry][rx] = 0
                        
        for i in range(len(self.rooms) - 1):
            r1 = self.rooms[i]
            r2 = self.rooms[i+1]
            x1, y1 = r1.center
            x2, y2 = r2.center
            
            if random.random() < 0.5:
                self.create_h_corridor(x1, x2, y1)
                self.create_v_corridor(y1, y2, x2)
            else:
                self.create_v_corridor(y1, y2, x1)
                self.create_h_corridor(x1, x2, y2)
                
        self.start_pos = (self.rooms[0].centerx * TILE_SIZE, self.rooms[0].centery * TILE_SIZE)
        self.exit_pos = (self.rooms[-1].centerx * TILE_SIZE, self.rooms[-1].centery * TILE_SIZE)
        
    def create_h_corridor(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                self.tiles[y][x] = 0
                
    def create_v_corridor(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                self.tiles[y][x] = 0
                
    def is_wall(self, x, y, size):
        corners = [
            (x - size//2, y - size//2),
            (x + size//2, y - size//2),
            (x - size//2, y + size//2),
            (x + size//2, y + size//2),
        ]
        for cx, cy in corners:
            tile_x = int(cx // TILE_SIZE)
            tile_y = int(cy // TILE_SIZE)
            if tile_x < 0 or tile_x >= self.width or tile_y < 0 or tile_y >= self.height:
                return True
            if self.tiles[tile_y][tile_x] == 1:
                return True
        return False
        
    def get_random_floor_pos(self):
        room = random.choice(self.rooms[1:-1])
        x = random.randint(room.left + 1, room.right - 2) * TILE_SIZE
        y = random.randint(room.top + 1, room.bottom - 2) * TILE_SIZE
        return (x, y)
            
    def draw(self, screen, camera_x, camera_y):
        start_tile_x = max(0, int(camera_x // TILE_SIZE))
        start_tile_y = max(0, int(camera_y // TILE_SIZE))
        end_tile_x = min(self.width, int((camera_x + screen.get_width()) // TILE_SIZE) + 1)
        end_tile_y = min(self.height, int((camera_y + screen.get_height()) // TILE_SIZE) + 1)
        
        for y in range(start_tile_y, end_tile_y):
            for x in range(start_tile_x, end_tile_x):
                tile = self.tiles[y][x]
                rect = pygame.Rect(
                    x * TILE_SIZE - camera_x,
                    y * TILE_SIZE - camera_y,
                    TILE_SIZE,
                    TILE_SIZE
                )
                if tile == 1:
                    pygame.draw.rect(screen, self.wall_color, rect)
                else:
                    pygame.draw.rect(screen, self.floor_color, rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)
                
        if self.exit_pos:
            ex, ey = self.exit_pos
            rect = pygame.Rect(
                ex - 16 - camera_x,
                ey - 16 - camera_y,
                32,
                32
            )
            pygame.draw.rect(screen, COLORS['exit'], rect)
            pygame.draw.rect(screen, COLORS['white'], rect, 2)

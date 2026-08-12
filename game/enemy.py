import pygame
import math
from .settings import ENEMY_TYPES

class Enemy:
    def __init__(self, x, y, enemy_type):
        data = ENEMY_TYPES[enemy_type]
        self.x = x
        self.y = y
        self.type = enemy_type
        self.name = data['name']
        self.max_hp = data['max_hp']
        self.hp = self.max_hp
        self.speed = data['speed']
        self.attack = data['attack']
        self.exp = data['exp']
        self.color = data['color']
        self.size = data['size']
        self.ai = data['ai']
        self.is_elite = data.get('is_elite', False)
        
        self.attack_range = data.get('attack_range', 30)
        self.attack_cooldown_max = data.get('attack_cooldown', 60)
        self.attack_cooldown = 0
        self.projectile_speed = data.get('projectile_speed', 0)
        
        self.hit_flash = 0
        self.projectiles = []
        
    def update(self, player, dungeon):
        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        target = player
        if player.shadow and player.invisible <= 0:
            dist_shadow = math.hypot(self.x - player.shadow.x, self.y - player.shadow.y)
            dist_player = math.hypot(self.x - player.x, self.y - player.y)
            if dist_shadow < dist_player * 1.5:
                target = player.shadow
        
        damage_dealt = 0
        if self.ai in ['chase', 'chase_attack']:
            damage_dealt = self.chase_ai(target, dungeon)
        elif self.ai == 'ranged':
            damage_dealt = self.ranged_ai(target, dungeon)
            
        for proj in self.projectiles[:]:
            proj['x'] += proj['dx']
            proj['y'] += proj['dy']
            proj['life'] -= 1
            if proj['life'] <= 0:
                self.projectiles.remove(proj)
                
        return damage_dealt
        
    def chase_ai(self, target, dungeon):
        dx = target.x - self.x
        dy = target.y - self.y
        dist = math.hypot(dx, dy)
        
        if dist > self.attack_range:
            if dist > 0:
                dx /= dist
                dy /= dist
                new_x = self.x + dx * self.speed
                new_y = self.y + dy * self.speed
                
                if not dungeon.is_wall(new_x, self.y, self.size):
                    self.x = new_x
                if not dungeon.is_wall(self.x, new_y, self.size):
                    self.y = new_y
            return 0
        else:
            if self.attack_cooldown <= 0 and self.ai == 'chase_attack':
                self.attack_cooldown = self.attack_cooldown_max
                return self.attack
            return 0
        
    def ranged_ai(self, target, dungeon):
        dx = target.x - self.x
        dy = target.y - self.y
        dist = math.hypot(dx, dy)
        
        if dist < 150:
            if dist > 0:
                dx /= -dist
                dy /= -dist
                new_x = self.x + dx * self.speed
                new_y = self.y + dy * self.speed
                if not dungeon.is_wall(new_x, self.y, self.size):
                    self.x = new_x
                if not dungeon.is_wall(self.x, new_y, self.size):
                    self.y = new_y
        elif dist > self.attack_range:
            dx /= dist
            dy /= dist
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            if not dungeon.is_wall(new_x, self.y, self.size):
                self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.size):
                self.y = new_y
        else:
            if self.attack_cooldown <= 0:
                self.attack_cooldown = self.attack_cooldown_max
                dx_norm = dx / dist
                dy_norm = dy / dist
                self.projectiles.append({
                    'x': self.x,
                    'y': self.y,
                    'dx': dx_norm * self.projectile_speed,
                    'dy': dy_norm * self.projectile_speed,
                    'damage': self.attack,
                    'life': 120,
                })
        return 0
                
    def take_damage(self, damage):
        self.hp -= damage
        self.hit_flash = 10
        return damage
        
    def draw(self, screen, camera_x, camera_y):
        color = (255, 255, 255) if self.hit_flash > 0 else self.color
        
        rect = pygame.Rect(
            self.x - self.size//2 - camera_x,
            self.y - self.size//2 - camera_y,
            self.size,
            self.size
        )
        pygame.draw.rect(screen, color, rect)
        
        if self.is_elite:
            pygame.draw.rect(screen, (255, 215, 0), rect, 2)
        
        hp_bar_width = self.size
        hp_bar_height = 4
        hp_percent = self.hp / self.max_hp
        bar_x = self.x - hp_bar_width//2 - camera_x
        bar_y = self.y - self.size//2 - 8 - camera_y
        
        pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, hp_bar_width, hp_bar_height))
        pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, hp_bar_width * hp_percent, hp_bar_height))
        
        for proj in self.projectiles:
            pygame.draw.circle(screen, (255, 100, 255), 
                             (int(proj['x'] - camera_x), int(proj['y'] - camera_y)), 5)

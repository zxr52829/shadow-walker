import pygame
import math
from .settings import COLORS

class Player:
    def __init__(self, x, y, character_data, permanent_buffs=None):
        self.x = x
        self.y = y
        self.size = 24
        self.base_speed = character_data['speed']
        self.speed = self.base_speed
        self.max_hp = character_data['max_hp']
        self.hp = self.max_hp
        self.base_attack = character_data['attack']
        self.attack = self.base_attack
        self.base_defense = character_data['defense']
        self.defense = self.base_defense
        self.color = character_data['color']
        self.character_id = character_data.get('id', 'traveler')
        
        if permanent_buffs:
            self.max_hp += permanent_buffs.get('max_hp', 0)
            self.hp = self.max_hp
            self.base_attack += permanent_buffs.get('attack', 0)
            self.attack = self.base_attack
        
        self.shadow = None
        self.base_shadow_duration = character_data['shadow_duration']
        self.shadow_duration = self.base_shadow_duration
        self.shadow_cooldown_max = character_data['shadow_cooldown']
        self.shadow_cooldown = 0
        self.shadow_speed = character_data['shadow_speed']
        self.shadow_damage_reduction = character_data.get('shadow_damage_reduction', 0)
        
        if permanent_buffs:
            self.shadow_duration += permanent_buffs.get('shadow_duration', 0)
        
        self.facing = (1, 0)
        self.attack_cooldown = 0
        self.invincible = 0
        self.invisible = 0
        
        self.equipment = {
            'weapon': None,
            'armor': None,
            'accessory': None,
        }
        self.inventory = []
        self.buffs = []
        
        self.level = 1
        self.exp = 0
        self.exp_to_next = 50
        
    def update(self, keys, dungeon):
        self.speed = self.base_speed
        if self.equipment['accessory']:
            self.speed += self.equipment['accessory']['effect'].get('speed', 0)
        
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_s]: dy += 1
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_d]: dx += 1
        
        if dx != 0 or dy != 0:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length
            self.facing = (dx, dy)
            
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            
            if not dungeon.is_wall(new_x, self.y, self.size):
                self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.size):
                self.y = new_y
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.shadow_cooldown > 0:
            self.shadow_cooldown -= 1
        if self.invincible > 0:
            self.invincible -= 1
        if self.invisible > 0:
            self.invisible -= 1
            
        self.update_buffs()
        
        if self.shadow:
            self.shadow.update(keys, dungeon, self)
            if self.shadow.duration <= 0:
                self.shadow = None
                
    def update_buffs(self):
        new_buffs = []
        for buff in self.buffs:
            buff['duration'] -= 1
            if buff['duration'] > 0:
                new_buffs.append(buff)
        self.buffs = new_buffs
        
    def get_total_attack(self):
        total = self.base_attack
        if self.equipment['weapon']:
            total += self.equipment['weapon']['effect'].get('attack', 0)
        for buff in self.buffs:
            if 'attack_buff' in buff:
                total += buff['attack_buff']
        return total
        
    def get_total_defense(self):
        total = self.base_defense
        if self.equipment['armor']:
            total += self.equipment['armor']['effect'].get('defense', 0)
        return total
        
    def summon_shadow(self):
        if self.shadow_cooldown <= 0 and not self.shadow:
            total_duration = self.shadow_duration
            if self.equipment['accessory']:
                total_duration += self.equipment['accessory']['effect'].get('shadow_duration', 0)
                
            self.shadow = Shadow(
                self.x + 30,
                self.y,
                total_duration,
                self.shadow_speed,
                self.shadow_damage_reduction
            )
            self.shadow_cooldown = self.shadow_cooldown_max
            
    def swap_with_shadow(self):
        if self.shadow:
            self.x, self.shadow.x = self.shadow.x, self.x
            self.y, self.shadow.y = self.shadow.y, self.y
            self.invincible = 30
            
            if self.character_id == 'assassin':
                self.invisible = 120
            
    def recall_shadow(self):
        if self.shadow:
            self.shadow = None
            self.shadow_cooldown = max(0, self.shadow_cooldown - 300)
            
    def normal_attack(self, enemies):
        if self.attack_cooldown <= 0:
            self.attack_cooldown = 20
            damage = self.get_total_attack()
            attack_range = 40
            
            hit_enemies = []
            for enemy in enemies:
                dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
                if dist < attack_range + enemy.size / 2:
                    dx = enemy.x - self.x
                    dy = enemy.y - self.y
                    dot = dx * self.facing[0] + dy * self.facing[1]
                    if dot > 0:
                        enemy.take_damage(damage)
                        hit_enemies.append(enemy)
            return hit_enemies
        return []
        
    def take_damage(self, damage):
        if self.invincible <= 0:
            actual_damage = max(1, damage - self.get_total_defense())
            self.hp -= actual_damage
            self.invincible = 60
            return actual_damage
        return 0
        
    def add_exp(self, amount):
        self.exp += amount
        while self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            self.level += 1
            self.max_hp += 10
            self.hp = min(self.hp + 10, self.max_hp)
            self.base_attack += 2
            self.exp_to_next = int(self.exp_to_next * 1.5)
            
    def draw(self, screen, camera_x, camera_y):
        if self.invisible > 0:
            return
            
        if self.invincible > 0 and self.invincible % 10 < 5:
            return
            
        rect = pygame.Rect(
            self.x - self.size//2 - camera_x,
            self.y - self.size//2 - camera_y,
            self.size,
            self.size
        )
        pygame.draw.rect(screen, self.color, rect)
        
        end_x = self.x + self.facing[0] * 15 - camera_x
        end_y = self.y + self.facing[1] * 15 - camera_y
        pygame.draw.line(screen, COLORS['white'], (self.x - camera_x, self.y - camera_y), (end_x, end_y), 2)
        
    def draw_shadow(self, screen, camera_x, camera_y):
        if self.shadow:
            self.shadow.draw(screen, camera_x, camera_y)


class Shadow:
    def __init__(self, x, y, duration, speed, damage_reduction=0):
        self.x = x
        self.y = y
        self.size = 22
        self.speed = speed
        self.duration = duration
        self.damage_reduction = damage_reduction
        self.hp = 50
        
    def update(self, keys, dungeon, player):
        self.duration -= 1
        
        dx, dy = 0, 0
        if keys[pygame.K_UP]: dy -= 1
        if keys[pygame.K_DOWN]: dy += 1
        if keys[pygame.K_LEFT]: dx -= 1
        if keys[pygame.K_RIGHT]: dx += 1
        
        if dx != 0 or dy != 0:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length
            
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            
            if not dungeon.is_wall(new_x, self.y, self.size):
                self.x = new_x
            if not dungeon.is_wall(self.x, new_y, self.size):
                self.y = new_y
                
    def take_damage(self, damage):
        actual = max(1, damage * (1 - self.damage_reduction))
        self.hp -= actual
        if self.hp <= 0:
            self.duration = 0
        return actual
        
    def draw(self, screen, camera_x, camera_y):
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        s.fill(COLORS['shadow'])
        screen.blit(s, (self.x - self.size//2 - camera_x, self.y - self.size//2 - camera_y))

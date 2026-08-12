import pygame
import sys
import random
import json
import os

from game.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, CHARACTERS, CHAPTERS, ITEMS, PERMANENT_UPGRADES
from game.player import Player
from game.dungeon import Dungeon
from game.enemy import Enemy
from game.items import ItemEntity
from game.ui import UI

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("影行者：双生回廊")
        self.clock = pygame.time.Clock()
        self.ui = UI(self.screen)
        
        self.game_state = 'menu'
        self.current_chapter = 1
        self.current_floor = 1
        self.total_crystals = 0
        self.upgrade_levels = {}
        self.load_save()
        
        self.player = None
        self.dungeon = None
        self.enemies = []
        self.items = []
        self.camera_x = 0
        self.camera_y = 0
        
        self.selected_character = 'traveler'
        self.menu_selection = 0
        self.menu_options = ['开始游戏', '永久升级', '角色选择', '退出游戏']
        
    def load_save(self):
        save_path = 'save.json'
        if os.path.exists(save_path):
            try:
                with open(save_path, 'r') as f:
                    data = json.load(f)
                    self.total_crystals = data.get('crystals', 0)
                    self.upgrade_levels = data.get('upgrades', {})
            except:
                pass
                
    def save_game(self):
        data = {
            'crystals': self.total_crystals,
            'upgrades': self.upgrade_levels,
        }
        with open('save.json', 'w') as f:
            json.dump(data, f)
            
    def get_permanent_buffs(self):
        buffs = {}
        for upgrade_id, level in self.upgrade_levels.items():
            if upgrade_id in PERMANENT_UPGRADES:
                effect = PERMANENT_UPGRADES[upgrade_id]['effect']
                for key, value in effect.items():
                    buffs[key] = buffs.get(key, 0) + value * level
        return buffs
        
    def start_new_game(self):
        chapter_data = CHAPTERS[self.current_chapter]
        self.dungeon = Dungeon(50, 50, chapter_data)
        self.dungeon.generate()
        
        char_data = CHARACTERS[self.selected_character].copy()
        char_data['id'] = self.selected_character
        self.player = Player(
            self.dungeon.start_pos[0], 
            self.dungeon.start_pos[1], 
            char_data,
            self.get_permanent_buffs()
        )
        
        self.enemies = []
        self.items = []
        self.spawn_enemies()
        self.spawn_items()
        
        self.game_state = 'playing'
        self.current_floor = 1
        
    def spawn_enemies(self):
        chapter_data = CHAPTERS[self.current_chapter]
        enemy_count = 5 + self.current_floor * 2
        
        for _ in range(enemy_count):
            pos = self.dungeon.get_random_floor_pos()
            while abs(pos[0] - self.dungeon.start_pos[0]) < 120 and abs(pos[1] - self.dungeon.start_pos[1]) < 120:
                pos = self.dungeon.get_random_floor_pos()
                
            enemy_type = random.choice(chapter_data['enemies'])
            if self.current_floor > 3 and random.random() < 0.15:
                enemy_type = 'elite_knight'
                
            enemy = Enemy(pos[0], pos[1], enemy_type)
            enemy.max_hp = int(enemy.max_hp * (1 + self.current_floor * 0.1))
            enemy.hp = enemy.max_hp
            enemy.attack = int(enemy.attack * (1 + self.current_floor * 0.08))
            self.enemies.append(enemy)
            
    def spawn_items(self):
        item_count = 4 + self.current_floor
        possible_items = list(ITEMS.keys())
        weights = [30, 20, 10, 15, 10, 5, 8, 7]
        
        for _ in range(item_count):
            pos = self.dungeon.get_random_floor_pos()
            item_id = random.choices(possible_items, weights=weights, k=1)[0]
            self.items.append(ItemEntity(pos[0], pos[1], item_id))
            
    def next_floor(self):
        self.current_floor += 1
        chapter_data = CHAPTERS[self.current_chapter]
        
        if self.current_floor > chapter_data['floors']:
            self.game_state = 'victory'
            self.save_game()
            return
            
        size = 50 + self.current_floor * 2
        self.dungeon = Dungeon(size, size, chapter_data)
        self.dungeon.generate()
        
        self.player.x, self.player.y = self.dungeon.start_pos
        self.player.hp = min(self.player.max_hp, self.player.hp + 20)
        
        self.enemies = []
        self.items = []
        self.spawn_enemies()
        self.spawn_items()
        
    def update(self):
        if self.game_state != 'playing':
            return
            
        keys = pygame.key.get_pressed()
        self.player.update(keys, self.dungeon)
        
        for enemy in self.enemies:
            damage = enemy.update(self.player, self.dungeon)
            if damage > 0:
                target = self.player
                if self.player.shadow:
                    dist_shadow = ((enemy.x - self.player.shadow.x)**2 + (enemy.y - self.player.shadow.y)**2)**0.5
                    dist_player = ((enemy.x - self.player.x)**2 + (enemy.y - self.player.y)**2)**0.5
                    if dist_shadow < dist_player:
                        target = self.player.shadow
                target.take_damage(damage)
                    
            for proj in enemy.projectiles[:]:
                if ((proj['x'] - self.player.x)**2 + (proj['y'] - self.player.y)**2)**0.5 < self.player.size//2 + 5:
                    self.player.take_damage(proj['damage'])
                    enemy.projectiles.remove(proj)
                    continue
                if self.player.shadow:
                    if ((proj['x'] - self.player.shadow.x)**2 + (proj['y'] - self.player.shadow.y)**2)**0.5 < self.player.shadow.size//2 + 5:
                        self.player.shadow.take_damage(proj['damage'])
                        enemy.projectiles.remove(proj)
                        
        for enemy in self.enemies[:]:
            if enemy.hp <= 0:
                self.player.add_exp(enemy.exp)
                if random.random() < 0.35:
                    drops = ['health_potion', 'crystal_core', 'energy_potion']
                    item_id = random.choice(drops)
                    self.items.append(ItemEntity(enemy.x, enemy.y, item_id))
                self.enemies.remove(enemy)
                
        for item in self.items:
            item.update()
            
        for item in self.items[:]:
            dist_p = ((item.x - self.player.x)**2 + (item.y - self.player.y)**2)**0.5
            dist_s = 999
            if self.player.shadow:
                dist_s = ((item.x - self.player.shadow.x)**2 + (item.y - self.player.shadow.y)**2)**0.5
                
            if dist_p < 30 or dist_s < 30:
                self.pickup_item(item)
                self.items.remove(item)
                
        exit_dist = ((self.player.x - self.dungeon.exit_pos[0])**2 + 
                    (self.player.y - self.dungeon.exit_pos[1])**2)**0.5
        if exit_dist < 30:
            self.next_floor()
            
        if self.player.hp <= 0:
            self.game_state = 'gameover'
            self.save_game()
            
        self.camera_x = self.player.x - SCREEN_WIDTH // 2
        self.camera_y = self.player.y - SCREEN_HEIGHT // 2
        
    def pickup_item(self, item):
        data = item.data
        if data['type'] == 'currency':
            self.total_crystals += data['effect']['currency']
        elif data['type'] in ['weapon', 'armor', 'accessory']:
            slot = data['type']
            old = self.player.equipment[slot]
            self.player.equipment[slot] = data
            if old and len(self.player.inventory) < 6:
                self.player.inventory.append(old)
        elif len(self.player.inventory) < 6:
            self.player.inventory.append(data)
            
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_game()
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if self.game_state == 'menu':
                    self.handle_menu_input(event.key)
                elif self.game_state == 'playing':
                    self.handle_game_input(event.key)
                elif self.game_state == 'upgrade':
                    self.handle_upgrade_input(event.key)
                elif self.game_state == 'character_select':
                    self.handle_char_select_input(event.key)
                elif self.game_state == 'paused':
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = 'playing'
                elif self.game_state in ['gameover', 'victory']:
                    if event.key == pygame.K_r:
                        self.game_state = 'menu'
                        
    def handle_menu_input(self, key):
        if key == pygame.K_w or key == pygame.K_UP:
            self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
        elif key == pygame.K_s or key == pygame.K_DOWN:
            self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
        elif key == pygame.K_RETURN:
            selected = self.menu_options[self.menu_selection]
            if selected == '开始游戏':
                self.start_new_game()
            elif selected == '永久升级':
                self.game_state = 'upgrade'
                self.upgrade_selection = 0
            elif selected == '角色选择':
                self.game_state = 'character_select'
                self.char_selection = 0
            elif selected == '退出游戏':
                self.save_game()
                pygame.quit()
                sys.exit()
                
    def handle_game_input(self, key):
        if key == pygame.K_SPACE:
            self.player.summon_shadow()
        elif key == pygame.K_e:
            self.player.swap_with_shadow()
        elif key == pygame.K_q:
            self.player.recall_shadow()
        elif key == pygame.K_j:
            self.player.normal_attack(self.enemies)
        elif key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6]:
            idx = key - pygame.K_1
            self.use_item(idx)
        elif key == pygame.K_ESCAPE:
            self.game_state = 'paused'
            
    def handle_upgrade_input(self, key):
        upgrade_list = list(PERMANENT_UPGRADES.keys())
        if key == pygame.K_w or key == pygame.K_UP:
            self.upgrade_selection = (self.upgrade_selection - 1) % len(upgrade_list)
        elif key == pygame.K_s or key == pygame.K_DOWN:
            self.upgrade_selection = (self.upgrade_selection + 1) % len(upgrade_list)
        elif key == pygame.K_RETURN:
            upgrade_id = upgrade_list[self.upgrade_selection]
            upgrade = PERMANENT_UPGRADES[upgrade_id]
            current_level = self.upgrade_levels.get(upgrade_id, 0)
            if current_level < upgrade['max_level'] and self.total_crystals >= upgrade['cost']:
                self.total_crystals -= upgrade['cost']
                self.upgrade_levels[upgrade_id] = current_level + 1
                self.save_game()
        elif key == pygame.K_ESCAPE:
            self.game_state = 'menu'
            
    def handle_char_select_input(self, key):
        char_list = list(CHARACTERS.keys())
        if key == pygame.K_w or key == pygame.K_UP:
            self.char_selection = (self.char_selection - 1) % len(char_list)
        elif key == pygame.K_s or key == pygame.K_DOWN:
            self.char_selection = (self.char_selection + 1) % len(char_list)
        elif key == pygame.K_RETURN:
            char_id = char_list[self.char_selection]
            char = CHARACTERS[char_id]
            if char.get('unlocked', True):
                self.selected_character = char_id
            else:
                cost = char.get('unlock_cost', 0)
                if self.total_crystals >= cost:
                    self.total_crystals -= cost
                    CHARACTERS[char_id]['unlocked'] = True
                    self.selected_character = char_id
                    self.save_game()
        elif key == pygame.K_ESCAPE:
            self.game_state = 'menu'
            
    def use_item(self, index):
        if index >= len(self.player.inventory):
            return
        item = self.player.inventory[index]
        if item['type'] == 'consumable':
            effect = item['effect']
            if 'heal' in effect:
                self.player.hp = min(self.player.max_hp, self.player.hp + effect['heal'])
            if 'shadow_cooldown_reset' in effect:
                self.player.shadow_cooldown = 0
            if 'attack_buff' in effect:
                self.player.buffs.append({
                    'attack_buff': effect['attack_buff'],
                    'duration': effect['duration']
                })
            self.player.inventory.pop(index)
            
    def draw(self):
        self.screen.fill((0, 0, 0))
        
        if self.game_state == 'menu':
            self.draw_menu()
        elif self.game_state == 'upgrade':
            self.draw_upgrade_menu()
        elif self.game_state == 'character_select':
            self.draw_character_select()
        elif self.game_state in ['playing', 'paused', 'gameover', 'victory']:
            self.dungeon.draw(self.screen, self.camera_x, self.camera_y)
            
            for item in self.items:
                item.draw(self.screen, self.camera_x, self.camera_y)
                
            for enemy in self.enemies:
                enemy.draw(self.screen, self.camera_x, self.camera_y)
                
            self.player.draw_shadow(self.screen, self.camera_x, self.camera_y)
            self.player.draw(self.screen, self.camera_x, self.camera_y)
            
            self.ui.draw_player_status(self.player, self.current_floor, 
                                      CHAPTERS[self.current_chapter]['name'], 
                                      self.total_crystals)
            self.ui.draw_inventory(self.player)
            self.ui.draw_equipment(self.player)
            self.ui.draw_controls_hint()
            
            if self.game_state == 'paused':
                self.ui.draw_pause_menu()
            elif self.game_state == 'gameover':
                self.ui.draw_game_over(won=False)
            elif self.game_state == 'victory':
                self.ui.draw_game_over(won=True)
                
        pygame.display.flip()
        
    def draw_menu(self):
        title = self.ui.title_font.render("影行者：双生回廊", True, (180, 120, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
        self.screen.blit(title, title_rect)
        
        subtitle = self.ui.font.render("操控影子，探索无尽地牢", True, (200, 200, 200))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4 + 60))
        self.screen.blit(subtitle, subtitle_rect)
        
        crystal_text = self.ui.font.render(f"晶核: {self.total_crystals}", True, (100, 255, 220))
        self.screen.blit(crystal_text, (SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//4 + 90))
        
        menu_y = SCREEN_HEIGHT//2
        for i, option in enumerate(self.menu_options):
            color = (255, 255, 255) if i == self.menu_selection else (150, 150, 150)
            text = self.ui.big_font.render(option, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH//2, menu_y + i * 50))
            self.screen.blit(text, rect)
            
    def draw_upgrade_menu(self):
        title = self.ui.big_font.render("永久升级", True, (255, 220, 100))
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 80))
        self.screen.blit(title, title_rect)
        
        crystal_text = self.ui.font.render(f"晶核: {self.total_crystals}", True, (100, 255, 220))
        self.screen.blit(crystal_text, (SCREEN_WIDTH//2 - 50, 130))
        
        upgrade_list = list(PERMANENT_UPGRADES.items())
        start_y = 180
        for i, (uid, upgrade) in enumerate(upgrade_list):
            y = start_y + i * 70
            current_level = self.upgrade_levels.get(uid, 0)
            color = (255, 255, 255) if i == self.upgrade_selection else (180, 180, 180)
            
            name_text = self.ui.font.render(f"{upgrade['name']} (Lv.{current_level}/{upgrade['max_level']})", True, color)
            self.screen.blit(name_text, (SCREEN_WIDTH//2 - 200, y))
            
            desc_text = self.ui.font.render(upgrade['desc'], True, (150, 150, 150))
            self.screen.blit(desc_text, (SCREEN_WIDTH//2 - 200, y + 25))
            
            cost_text = self.ui.font.render(f"消耗: {upgrade['cost']} 晶核", True, (255, 200, 100))
            self.screen.blit(cost_text, (SCREEN_WIDTH//2 + 100, y + 10))
            
        hint = self.ui.font.render("ESC 返回 | 回车 升级", True, (180, 180, 180))
        self.screen.blit(hint, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 50))
        
    def draw_character_select(self):
        title = self.ui.big_font.render("角色选择", True, (180, 120, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 80))
        self.screen.blit(title, title_rect)
        
        char_list = list(CHARACTERS.items())
        start_y = 180
        for i, (cid, char) in enumerate(char_list):
            y = start_y + i * 90
            color = (255, 255, 255) if i == self.char_selection else (180, 180, 180)
            
            unlocked = char.get('unlocked', True)
            name_text = f"{char['name']} {'(已选中)' if cid == self.selected_character else ''}"
            if not unlocked:
                name_text += f" [未解锁 - {char.get('unlock_cost', 0)}晶核]"
                
            render = self.ui.font.render(name_text, True, color)
            self.screen.blit(render, (SCREEN_WIDTH//2 - 250, y))
            
            desc_text = self.ui.font.render(char['desc'], True, (150, 150, 150))
            self.screen.blit(desc_text, (SCREEN_WIDTH//2 - 250, y + 25))
            
            stats = f"HP:{char['max_hp']} 攻击:{char['attack']} 速度:{char['speed']}"
            stats_text = self.ui.font.render(stats, True, (120, 200, 120))
            self.screen.blit(stats_text, (SCREEN_WIDTH//2 - 250, y + 50))
            
        hint = self.ui.font.render("ESC 返回 | 回车 选择/解锁", True, (180, 180, 180))
        self.screen.blit(hint, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT - 50))
        
    def run(self):
        while True:
            self.handle_events()
            if self.game_state == 'playing':
                self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()

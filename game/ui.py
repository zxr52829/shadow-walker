import pygame
from .settings import COLORS

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont('Arial', 16)
        self.big_font = pygame.font.SysFont('Arial', 32)
        self.title_font = pygame.font.SysFont('Arial', 48)
        
    def draw_player_status(self, player, floor_num, chapter_name, crystals):
        hp_bar_width = 200
        hp_bar_height = 20
        hp_x = 20
        hp_y = 20
        
        pygame.draw.rect(self.screen, (50, 0, 0), (hp_x, hp_y, hp_bar_width, hp_bar_height))
        hp_percent = player.hp / player.max_hp
        pygame.draw.rect(self.screen, COLORS['red'], (hp_x, hp_y, hp_bar_width * hp_percent, hp_bar_height))
        pygame.draw.rect(self.screen, COLORS['white'], (hp_x, hp_y, hp_bar_width, hp_bar_height), 2)
        
        hp_text = self.font.render(f"HP: {int(player.hp)}/{player.max_hp}", True, COLORS['white'])
        self.screen.blit(hp_text, (hp_x + 5, hp_y + 2))
        
        exp_text = self.font.render(f"Lv.{player.level}  EXP: {player.exp}/{player.exp_to_next}", True, COLORS['yellow'])
        self.screen.blit(exp_text, (hp_x, hp_y + 25))
        
        shadow_x = hp_x
        shadow_y = hp_y + 50
        cooldown_percent = 1 - (player.shadow_cooldown / player.shadow_cooldown_max) if player.shadow_cooldown > 0 else 1
        
        pygame.draw.rect(self.screen, (30, 30, 60), (shadow_x, shadow_y, hp_bar_width, 15))
        pygame.draw.rect(self.screen, COLORS['purple'], (shadow_x, shadow_y, hp_bar_width * cooldown_percent, 15))
        pygame.draw.rect(self.screen, COLORS['white'], (shadow_x, shadow_y, hp_bar_width, 15), 1)
        
        shadow_status = "影子就绪 [空格]" if player.shadow_cooldown <= 0 else "影子冷却中"
        if player.shadow:
            shadow_status = f"影子存在: {player.shadow.duration//60}s"
        shadow_text = self.font.render(shadow_status, True, COLORS['white'])
        self.screen.blit(shadow_text, (shadow_x + 5, shadow_y + 1))
        
        floor_text = self.font.render(f"{chapter_name} - 第 {floor_num} 层", True, COLORS['white'])
        self.screen.blit(floor_text, (self.screen.get_width() - 180, 20))
        
        crystal_text = self.font.render(f"晶核: {crystals}", True, COLORS['cyan'])
        self.screen.blit(crystal_text, (self.screen.get_width() - 180, 45))
        
    def draw_inventory(self, player):
        inv_x = 20
        inv_y = self.screen.get_height() - 100
        
        title = self.font.render("物品栏 [1-6使用]:", True, COLORS['white'])
        self.screen.blit(title, (inv_x, inv_y - 20))
        
        for i in range(6):
            slot_x = inv_x + i * 40
            slot_y = inv_y
            pygame.draw.rect(self.screen, COLORS['dark_gray'], (slot_x, slot_y, 36, 36))
            pygame.draw.rect(self.screen, COLORS['gray'], (slot_x, slot_y, 36, 36), 1)
            
            if i < len(player.inventory):
                item = player.inventory[i]
                pygame.draw.rect(self.screen, item['color'], (slot_x + 8, slot_y + 8, 20, 20))
                
            num_text = self.font.render(str(i+1), True, COLORS['white'])
            self.screen.blit(num_text, (slot_x + 2, slot_y + 2))
            
    def draw_equipment(self, player):
        eq_x = self.screen.get_width() - 150
        eq_y = 100
        
        title = self.font.render("装备:", True, COLORS['white'])
        self.screen.blit(title, (eq_x, eq_y - 20))
        
        slots = [('weapon', '武器'), ('armor', '护甲'), ('accessory', '饰品')]
        for i, (slot, name) in enumerate(slots):
            slot_y = eq_y + i * 40
            pygame.draw.rect(self.screen, COLORS['dark_gray'], (eq_x, slot_y, 130, 32))
            pygame.draw.rect(self.screen, COLORS['gray'], (eq_x, slot_y, 130, 32), 1)
            
            item = player.equipment[slot]
            text = f"{name}: {item['name']}" if item else f"{name}: 空"
            render = self.font.render(text, True, COLORS['white'])
            self.screen.blit(render, (eq_x + 5, slot_y + 8))
        
    def draw_game_over(self, won=False):
        text = "胜利！" if won else "游戏结束"
        color = COLORS['yellow'] if won else COLORS['red']
        render = self.big_font.render(text, True, color)
        rect = render.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
        self.screen.blit(render, rect)
        
        hint = self.font.render("按R返回主菜单", True, COLORS['white'])
        hint_rect = hint.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 + 50))
        self.screen.blit(hint, hint_rect)
        
    def draw_controls_hint(self):
        hints = [
            "WASD: 移动 | 方向键: 控制影子",
            "空格: 召唤影子 | E: 交换位置 | Q: 收回影子",
            "J: 攻击 | 1-6: 使用物品 | ESC: 暂停",
        ]
        y = self.screen.get_height() - 60
        for hint in hints:
            text = self.font.render(hint, True, (180, 180, 180))
            self.screen.blit(text, (self.screen.get_width() - 380, y))
            y += 20
            
    def draw_pause_menu(self):
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        text = self.big_font.render("游戏暂停", True, COLORS['white'])
        rect = text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 - 30))
        self.screen.blit(text, rect)
        
        hint = self.font.render("按 ESC 继续游戏", True, COLORS['white'])
        hint_rect = hint.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 + 20))
        self.screen.blit(hint, hint_rect)

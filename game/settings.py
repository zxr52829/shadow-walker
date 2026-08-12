import pygame

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TILE_SIZE = 32

COLORS = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'gray': (100, 100, 100),
    'dark_gray': (50, 50, 50),
    'red': (255, 60, 60),
    'green': (60, 255, 60),
    'blue': (60, 120, 255),
    'purple': (180, 60, 255),
    'yellow': (255, 220, 60),
    'cyan': (60, 255, 255),
    'orange': (255, 140, 60),
    'shadow': (80, 60, 120, 180),
    'floor': (40, 35, 50),
    'wall': (80, 70, 100),
    'player': (100, 200, 255),
    'enemy': (255, 100, 100),
    'item': (255, 215, 0),
    'exit': (100, 255, 150),
}

CHARACTERS = {
    'traveler': {
        'name': '旅者',
        'desc': '平衡型角色，影子持续时间更长',
        'max_hp': 100,
        'speed': 4,
        'attack': 10,
        'defense': 2,
        'shadow_duration': 720,
        'shadow_cooldown': 900,
        'shadow_speed': 4,
        'color': (100, 200, 255),
        'unlocked': True,
    },
    'assassin': {
        'name': '刺客',
        'desc': '敏捷型角色，影子更快，交换后隐身',
        'max_hp': 80,
        'speed': 5,
        'attack': 14,
        'defense': 1,
        'shadow_duration': 540,
        'shadow_cooldown': 840,
        'shadow_speed': 5.5,
        'color': (180, 100, 255),
        'unlocked': False,
        'unlock_cost': 50,
    },
    'guardian': {
        'name': '守卫',
        'desc': '坦克型角色，影子减伤，血量更高',
        'max_hp': 150,
        'speed': 3,
        'attack': 8,
        'defense': 5,
        'shadow_duration': 600,
        'shadow_cooldown': 1020,
        'shadow_speed': 3,
        'shadow_damage_reduction': 0.5,
        'color': (100, 150, 100),
        'unlocked': False,
        'unlock_cost': 80,
    }
}

ENEMY_TYPES = {
    'slime': {
        'name': '史莱姆',
        'max_hp': 20,
        'speed': 1.5,
        'attack': 5,
        'exp': 5,
        'color': (100, 255, 100),
        'size': 20,
        'ai': 'chase',
    },
    'skeleton': {
        'name': '骷髅兵',
        'max_hp': 40,
        'speed': 2,
        'attack': 10,
        'exp': 10,
        'color': (220, 220, 220),
        'size': 24,
        'ai': 'chase_attack',
        'attack_range': 30,
        'attack_cooldown': 60,
    },
    'mage': {
        'name': '暗影法师',
        'max_hp': 30,
        'speed': 1.2,
        'attack': 15,
        'exp': 15,
        'color': (150, 50, 200),
        'size': 22,
        'ai': 'ranged',
        'attack_range': 200,
        'attack_cooldown': 120,
        'projectile_speed': 5,
    },
    'elite_knight': {
        'name': '精英骑士',
        'max_hp': 100,
        'speed': 2.5,
        'attack': 20,
        'exp': 30,
        'color': (255, 150, 50),
        'size': 28,
        'ai': 'chase_attack',
        'attack_range': 35,
        'attack_cooldown': 45,
        'is_elite': True,
    }
}

ITEMS = {
    'health_potion': {
        'name': '生命药水',
        'type': 'consumable',
        'rarity': 'common',
        'effect': {'heal': 30},
        'desc': '恢复30点生命值',
        'color': (255, 80, 80),
    },
    'energy_potion': {
        'name': '能量药水',
        'type': 'consumable',
        'rarity': 'common',
        'effect': {'shadow_cooldown_reset': True},
        'desc': '立即重置影子冷却',
        'color': (80, 180, 255),
    },
    'attack_scroll': {
        'name': '力量卷轴',
        'type': 'consumable',
        'rarity': 'rare',
        'effect': {'attack_buff': 5, 'duration': 300},
        'desc': '5秒内攻击力+5',
        'color': (255, 180, 80),
    },
    'iron_sword': {
        'name': '铁剑',
        'type': 'weapon',
        'rarity': 'common',
        'effect': {'attack': 5},
        'desc': '攻击力+5',
        'color': (180, 180, 180),
    },
    'shadow_amulet': {
        'name': '暗影护符',
        'type': 'accessory',
        'rarity': 'rare',
        'effect': {'shadow_duration': 120},
        'desc': '影子持续时间+2秒',
        'color': (150, 80, 200),
    },
    'crystal_core': {
        'name': '晶核',
        'type': 'currency',
        'rarity': 'epic',
        'effect': {'currency': 1},
        'desc': '永久升级货币',
        'color': (100, 255, 220),
    },
    'steel_armor': {
        'name': '钢甲',
        'type': 'armor',
        'rarity': 'rare',
        'effect': {'defense': 4},
        'desc': '防御力+4',
        'color': (120, 120, 150),
    },
    'speed_boots': {
        'name': '疾风靴',
        'type': 'accessory',
        'rarity': 'rare',
        'effect': {'speed': 1},
        'desc': '移动速度+1',
        'color': (100, 255, 180),
    }
}

CHAPTERS = {
    1: {
        'name': '幽暗森林',
        'floors': 10,
        'enemies': ['slime', 'skeleton'],
        'floor_color': (30, 50, 30),
        'wall_color': (60, 100, 60),
    },
    2: {
        'name': '晶簇矿洞',
        'floors': 15,
        'enemies': ['skeleton', 'mage', 'elite_knight'],
        'floor_color': (35, 30, 55),
        'wall_color': (80, 70, 130),
    }
}

PERMANENT_UPGRADES = {
    'hp_boost': {
        'name': '生命强化',
        'desc': '最大生命值+10',
        'cost': 10,
        'max_level': 10,
        'effect': {'max_hp': 10},
    },
    'attack_boost': {
        'name': '攻击强化',
        'desc': '基础攻击力+2',
        'cost': 15,
        'max_level': 10,
        'effect': {'attack': 2},
    },
    'shadow_longer': {
        'name': '影子延长',
        'desc': '影子持续时间+1秒',
        'cost': 20,
        'max_level': 5,
        'effect': {'shadow_duration': 60},
    }
}

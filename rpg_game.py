import curses
import time
import random
from character import Character
from battle_system import BattleSystem
from game_ui import GameUI

class Game:
    def __init__(self):
        self.stdscr = None
        self.ui = None
        self.battle_system = None
        self.player = None
        self.enemy = None
        self.animation_frame = 0
        self.animation_timer = 0

    def setup_curses(self):
        self.stdscr = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)      
        curses.init_pair(2, curses.COLOR_GREEN, -1)    
        curses.init_pair(3, curses.COLOR_YELLOW, -1)   
        curses.init_pair(4, curses.COLOR_BLUE, -1)     
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)  
        curses.init_pair(6, curses.COLOR_CYAN, -1)     
        curses.curs_set(0)  
        self.stdscr.keypad(1)
        self.stdscr.timeout(100)

    def cleanup_curses(self):
        curses.endwin()

    def draw_character(self, character, x, y, is_player=True):
        if character.name == "Warrior":
            art = [
                "  ⚔️  ",
                " /|\\ ",
                " / \\ "
            ]
        elif character.name == "Mage":
            art = [
                "  🧙  ",
                " /|\\ ",
                " / \\ "
            ]
        elif character.name == "Archer":
            art = [
                "  🏹  ",
                " /|\\ ",
                " / \\ "
            ]
        else: 
            art = [
                "  👾  ",
                " /|\\ ",
                " / \\ "
            ]

        color_pair = 4 if is_player else 5
        for i, line in enumerate(art):
            self.stdscr.addstr(y + i, x, line, curses.color_pair(color_pair))

    def draw_health_bar(self, character, x, y):
        bar_width = 20
        self.stdscr.addstr(y, x, "[" + " " * bar_width + "]", curses.color_pair(1))
        
        health_width = int((character.health / character.max_health) * bar_width)
        health_bar = "█" * health_width
        self.stdscr.addstr(y, x + 1, health_bar, curses.color_pair(1))
        
        health_text = f"{character.name}: {character.health}/{character.max_health}"
        self.stdscr.addstr(y - 1, x, health_text)

    def draw_attack_animation(self, attacker, target, attack_type):
        max_y, max_x = self.stdscr.getmaxyx()
        
        if attacker == self.player:
            start_x = max_x // 4
            end_x = 3 * max_x // 4
            color = 4
        else:
            start_x = 3 * max_x // 4
            end_x = max_x // 4
            color = 5
        if attack_type == "attack":
            for i in range(5):
                self.stdscr.clear()
                self.draw_battle_screen()
                slash = "-" * (abs(end_x - start_x) // 5 * (i + 1))
                self.stdscr.addstr(max_y // 2, start_x, slash, curses.color_pair(color))
                self.stdscr.refresh()
                time.sleep(0.1)
        else:
            for i in range(5):
                self.stdscr.clear()
                self.draw_battle_screen()
                if attacker.name == "Mage":
                    spell = "*" * (abs(end_x - start_x) // 5 * (i + 1))
                    self.stdscr.addstr(max_y // 2, start_x, spell, curses.color_pair(6))
                elif attacker.name == "Warrior":
                    rage = "!" * (abs(end_x - start_x) // 5 * (i + 1))
                    self.stdscr.addstr(max_y // 2, start_x, rage, curses.color_pair(6))
                elif attacker.name == "Archer":
                    arrow = "→" * (abs(end_x - start_x) // 5 * (i + 1))
                    self.stdscr.addstr(max_y // 2, start_x, arrow, curses.color_pair(6))
                self.stdscr.refresh()
                time.sleep(0.1)

    def draw_battle_screen(self):
        max_y, max_x = self.stdscr.getmaxyx()
        
        self.stdscr.clear()
        
        self.draw_character(self.player, max_x // 4 - 3, max_y // 2 - 2, True)
        self.draw_character(self.enemy, 3 * max_x // 4 - 3, max_y // 2 - 2, False)
        
        self.draw_health_bar(self.player, max_x // 4 - 10, max_y // 2 + 2)
        self.draw_health_bar(self.enemy, 3 * max_x // 4 - 10, max_y // 2 + 2)
        
        self.stdscr.addstr(max_y // 2 + 4, max_x // 4 - 10, 
                          f"Attack: {self.player.attack} Defense: {self.player.defense}")
        self.stdscr.addstr(max_y // 2 + 4, 3 * max_x // 4 - 10, 
                          f"Attack: {self.enemy.attack} Defense: {self.enemy.defense}")
        
        log_y = max_y - 10
        self.stdscr.addstr(log_y, 2, "Combat Log:")
        for i, entry in enumerate(self.battle_system.get_combat_log()):
            self.stdscr.addstr(log_y + i + 1, 2, entry)
        
        self.stdscr.addstr(max_y - 3, 2, "Actions:")
        self.stdscr.addstr(max_y - 2, 2, "1. Attack")
        self.stdscr.addstr(max_y - 2, 15, "2. Special Ability")
        self.stdscr.addstr(max_y - 2, 35, "3. Quit")
        
        if self.player.special_cooldown > 0:
            self.stdscr.addstr(max_y - 1, 2, 
                             f"Special Cooldown: {self.player.special_cooldown} turns", 
                             curses.color_pair(3))

    def select_character_class(self):
        classes = {
            '1': ('Warrior', {'health': 120, 'attack': 15, 'defense': 10}),
            '2': ('Mage', {'health': 80, 'attack': 20, 'defense': 5}),
            '3': ('Archer', {'health': 100, 'attack': 18, 'defense': 8})
        }
        
        self.stdscr.clear()
        max_y, max_x = self.stdscr.getmaxyx()
        
        title = "Choose your character class:"
        self.stdscr.addstr(2, (max_x - len(title)) // 2, title, curses.color_pair(2))
        
        y = 4
        for i, (class_name, stats) in enumerate(classes.values(), 1):
            if class_name == "Warrior":
                icon = "⚔️"
            elif class_name == "Mage":
                icon = "🧙"
            else:
                icon = "🏹"
            
            self.stdscr.addstr(y, (max_x - 20) // 2, f"{i}. {icon} {class_name}")
            self.stdscr.addstr(y + 1, (max_x - 40) // 2, 
                             f"Health: {stats['health']} Attack: {stats['attack']} Defense: {stats['defense']}")
            y += 3
        
        while True:
            key = self.stdscr.getch()
            if key in [ord('1'), ord('2'), ord('3')]:
                class_choice = chr(key)
                class_name, stats = classes[class_choice]
                return Character(class_name, stats)

    def run(self):
        try:
            self.setup_curses()
            
            self.player = self.select_character_class()
            self.enemy = Character("Enemy", {'health': 100, 'attack': 12, 'defense': 8})
            
            self.battle_system = BattleSystem(self.player, self.enemy)
            
            while True:
                self.draw_battle_screen()
                
                key = self.stdscr.getch()
                if key == ord('3'):
                    break
                elif key == ord('1'):
                    self.draw_attack_animation(self.player, self.enemy, "attack")
                    self.battle_system.execute_turn('attack')
                elif key == ord('2'):
                    self.draw_attack_animation(self.player, self.enemy, "special")
                    self.battle_system.execute_turn('special')
                
                if self.battle_system.is_battle_over():
                    self.stdscr.addstr(self.stdscr.getmaxyx()[0] - 1, 2, 
                                     "Battle Over! Press any key to exit...", 
                                     curses.color_pair(2))
                    self.stdscr.getch()
                    break
                
                time.sleep(0.1)
                
        finally:
            self.cleanup_curses()

if __name__ == "__main__":
    game = Game()
    game.run() 
import curses

class GameUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.max_y, self.max_x = self.stdscr.getmaxyx()

    def clear_screen(self):
        self.stdscr.clear()

    def display_text(self, text, y, x):
        try:
            self.stdscr.addstr(y, x, text)
        except curses.error:
            pass

    def display_health_bar(self, character, y, x):
        health_percent = character.get_health_percentage()
        bar_width = 20
        filled_width = int((health_percent / 100) * bar_width)
        
        self.display_text(f"{character.name}:", y, x)
        self.display_text(f"HP: {character.health}/{character.max_health}", y, x + len(character.name) + 2)
        
        bar = "[" + "█" * filled_width + " " * (bar_width - filled_width) + "]"
        self.stdscr.addstr(y + 1, x, bar, curses.color_pair(1))

    def display_battle_state(self, player, enemy):
        self.display_health_bar(player, 2, 2)
        self.display_text(f"Attack: {player.attack}", 4, 2)
        self.display_text(f"Defense: {player.defense}", 5, 2)
        if player.special_cooldown > 0:
            self.display_text(f"Special Cooldown: {player.special_cooldown} turns", 6, 2)
        
        self.display_health_bar(enemy, 2, self.max_x - 30)
        self.display_text(f"Attack: {enemy.attack}", 4, self.max_x - 30)
        self.display_text(f"Defense: {enemy.defense}", 5, self.max_x - 30)
        if enemy.special_cooldown > 0:
            self.display_text(f"Special Cooldown: {enemy.special_cooldown} turns", 6, self.max_x - 30)

    def display_combat_log(self, combat_log):
        log_y = 8
        self.display_text("Combat Log:", log_y, 2)
        for i, entry in enumerate(combat_log):
            self.display_text(entry, log_y + i + 1, 2)

    def display_special_abilities(self):
        abilities = {
            "Warrior": "Berserker Rage: Double attack for one turn",
            "Mage": "Fireball: High damage with 50% chance to burn",
            "Archer": "Precision Shot: Guaranteed critical hit"
        }
        
        y = self.max_y - 8
        self.display_text("Special Abilities:", y, 2)
        for i, (class_name, ability) in enumerate(abilities.items()):
            self.display_text(f"{class_name}: {ability}", y + i + 1, 2) 
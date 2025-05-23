import random

class BattleSystem:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.combat_log = []
        self.current_turn = 0

    def execute_turn(self, action):
        self.current_turn += 1
        self.combat_log.append(f"\n--- Turn {self.current_turn} ---")
        
        if action == 'attack':
            damage = self.player.attack
            actual_damage = self.enemy.take_damage(damage)
            self.combat_log.append(f"{self.player.name} attacks for {actual_damage} damage!")
        elif action == 'special':
            success, message = self.player.use_special_ability(self.enemy)
            self.combat_log.append(message)
        
        if not self.enemy.is_alive():
            self.combat_log.append(f"{self.enemy.name} has been defeated!")
            return
        
        enemy_action = self._get_enemy_action()
        if enemy_action == 'attack':
            damage = self.enemy.attack
            actual_damage = self.player.take_damage(damage)
            self.combat_log.append(f"{self.enemy.name} attacks for {actual_damage} damage!")
        else:
            success, message = self.enemy.use_special_ability(self.player)
            self.combat_log.append(message)
        
        self.player.update_cooldowns()
        self.enemy.update_cooldowns()
        
        if not self.player.is_alive():
            self.combat_log.append(f"{self.player.name} has been defeated!")

    def _get_enemy_action(self):
        if self.enemy.special_cooldown == 0 and random.random() < 0.3:
            return 'special'
        return 'attack'

    def is_battle_over(self):
        return not self.player.is_alive() or not self.enemy.is_alive()

    def get_combat_log(self):
        return self.combat_log[-5:] if len(self.combat_log) > 5 else self.combat_log 
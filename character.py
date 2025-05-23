class Character:
    def __init__(self, name, stats):
        self.name = name
        self.max_health = stats['health']
        self.health = stats['health']
        self.attack = stats['attack']
        self.defense = stats['defense']
        self.special_cooldown = 0
        self.max_special_cooldown = 3

    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense)
        self.health = max(0, self.health - actual_damage)
        return actual_damage

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
        return amount

    def is_alive(self):
        return self.health > 0

    def get_health_percentage(self):
        return (self.health / self.max_health) * 100

    def use_special_ability(self, target):
        if self.special_cooldown > 0:
            return False, "Special ability is on cooldown!"

        self.special_cooldown = self.max_special_cooldown
        
        if self.name == "Warrior":
            damage = self.attack * 2
            actual_damage = target.take_damage(damage)
            return True, f"{self.name} uses Berserker Rage and deals {actual_damage} damage!"
            
        elif self.name == "Mage":
            damage = self.attack * 1.5
            actual_damage = target.take_damage(damage)
            if self.attack % 2 == 0: 
                target.take_damage(5) 
                return True, f"{self.name} casts Fireball dealing {actual_damage} damage and burns the target!"
            return True, f"{self.name} casts Fireball dealing {actual_damage} damage!"
            
        elif self.name == "Archer":
            damage = self.attack * 2.5
            actual_damage = target.take_damage(damage)
            return True, f"{self.name} uses Precision Shot and deals {actual_damage} damage!"

        return False, "No special ability available!"

    def update_cooldowns(self):
        if self.special_cooldown > 0:
            self.special_cooldown -= 1 
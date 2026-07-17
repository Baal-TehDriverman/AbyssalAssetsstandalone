import random
from typing import List, Dict, Optional
from datetime import datetime

class SpaceFighter:
    def __init__(self, name: str, pilot_id: str, ship_class: str):
        self.name = name
        self.pilot_id = pilot_id
        self.ship_class = ship_class # 'Interceptor', 'Fighter', 'Heavy'
        self.health = 1000
        self.shield = 500
        self.energy = 100
        self.status = "docked"
        
        # Loadout
        self.weapons = ["Laser Cannon"]
        if ship_class == "Heavy":
            self.weapons.append("Plasma Torpedo")
            self.health = 2000
            self.shield = 1000
        elif ship_class == "Interceptor":
            self.energy = 200

    def take_damage(self, amount: int):
        if self.shield > 0:
            if amount > self.shield:
                remaining = amount - self.shield
                self.shield = 0
                self.health -= remaining
            else:
                self.shield -= amount
        else:
            self.health -= amount
            
        if self.health <= 0:
            self.status = "destroyed"

    def fire_weapon(self, target: 'SpaceFighter', weapon: str) -> str:
        if self.status == "destroyed":
            return f"{self.name} is destroyed and cannot fire."
        if weapon not in self.weapons:
            return f"{weapon} not equipped."
            
        damage = 0
        if weapon == "Laser Cannon":
            damage = random.randint(50, 150)
            self.energy -= 10
        elif weapon == "Plasma Torpedo":
            damage = random.randint(300, 600)
            self.energy -= 50
            
        if self.energy < 0:
            self.energy += 10 # refund
            return f"{self.name} lacks energy to fire {weapon}."
            
        target.take_damage(damage)
        return f"{self.name} fired {weapon} at {target.name} for {damage} damage! Target Shields: {max(0, target.shield)}, Hull: {max(0, target.health)}"

class CombatInstance:
    def __init__(self, fighter_a: SpaceFighter, fighter_b: SpaceFighter):
        self.fighter_a = fighter_a
        self.fighter_b = fighter_b
        self.log = []

    def simulate_turn(self):
        if self.fighter_a.status == "destroyed" or self.fighter_b.status == "destroyed":
            return
            
        # A fires at B
        weapon_a = random.choice(self.fighter_a.weapons)
        res_a = self.fighter_a.fire_weapon(self.fighter_b, weapon_a)
        self.log.append(res_a)
        
        if self.fighter_b.status != "destroyed":
            # B fires at A
            weapon_b = random.choice(self.fighter_b.weapons)
            res_b = self.fighter_b.fire_weapon(self.fighter_a, weapon_b)
            self.log.append(res_b)
            
    def resolve_combat(self) -> str:
        while self.fighter_a.status != "destroyed" and self.fighter_b.status != "destroyed":
            self.simulate_turn()
            
        winner = self.fighter_a if self.fighter_a.status != "destroyed" else self.fighter_b
        return f"Combat Resolved. Winner: {winner.name} ({winner.health} HP remaining)."

from typing import List, Dict
import random
import time

class CargoItem:
    def __init__(self, item_id: str, name: str, quantity: int, value_per_unit: float):
        self.item_id = item_id
        self.name = name
        self.quantity = quantity
        self.value_per_unit = value_per_unit

class SpaceFreighter:
    def __init__(self, name: str, owner_id: str, max_capacity: int):
        self.name = name
        self.owner_id = owner_id
        self.max_capacity = max_capacity
        self.cargo: List[CargoItem] = []
        self.current_location = "Abyssal Hub"
        self.destination = None
        self.transit_time_remaining = 0
        self.status = "docked" # docked, in_transit, intercepted

    def get_current_load(self) -> int:
        return sum(item.quantity for item in self.cargo)

    def load_cargo(self, item: CargoItem) -> bool:
        if self.get_current_load() + item.quantity <= self.max_capacity:
            self.cargo.append(item)
            return True
        return False

    def launch(self, destination: str, transit_time: int):
        self.destination = destination
        self.transit_time_remaining = transit_time
        self.status = "in_transit"
        
    def tick(self):
        if self.status == "in_transit":
            self.transit_time_remaining -= 1
            if self.transit_time_remaining <= 0:
                self.current_location = self.destination
                self.destination = None
                self.status = "docked"

class AIBusinessLogistics:
    def __init__(self, business_id: str, name: str, funds: float):
        self.business_id = business_id
        self.name = name
        self.funds = funds
        self.freighters: List[SpaceFreighter] = []

    def purchase_freighter(self, name: str, capacity: int, cost: float) -> bool:
        if self.funds >= cost:
            self.funds -= cost
            new_freighter = SpaceFreighter(name, self.business_id, capacity)
            self.freighters.append(new_freighter)
            return True
        return False

    def evaluate_and_ship(self, market_data: Dict[str, float]):
        # Simple AI logic: find profitable route
        for freighter in self.freighters:
            if freighter.status == "docked":
                # Buy cheap cargo
                if self.funds > 1000:
                    self.funds -= 1000
                    freighter.load_cargo(CargoItem("rare_isotope", "Rare Isotope", 100, 10.0))
                    # Ship to high demand sector
                    freighter.launch("Sector 7G", transit_time=5)
                    print(f"[{self.name}] Dispatched {freighter.name} to Sector 7G with cargo.")

class LogisticsEngine:
    def __init__(self):
        self.active_freighters: List[SpaceFreighter] = []
        self.ai_businesses: List[AIBusinessLogistics] = []

    def register_business(self, business: AIBusinessLogistics):
        self.ai_businesses.append(business)

    def simulate_tick(self):
        for business in self.ai_businesses:
            business.evaluate_and_ship({"Sector 7G": 1.5}) # Dummy market data
            
            for freighter in business.freighters:
                freighter.tick()
                if freighter.status == "in_transit":
                    # 5% chance of being intercepted by pirates
                    if random.random() < 0.05:
                        freighter.status = "intercepted"
                        print(f"ALERT: Freighter {freighter.name} owned by {business.name} was intercepted by pirates!")

import re
import sys

with open("server/main.py", "r") as f:
    content = f.read()

# 1. Add Business and EconomyEvent Models
models_addition = """
class Business(Base):
    __tablename__ = "businesses"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    business_type = Column(String, nullable=False) # e.g., 'Kelp Farm', 'Trench Salvage'
    level = Column(Integer, default=1)
    funds = Column(Integer, default=0)
    is_ai_operated = Column(Boolean, default=False)
    ai_risk_tolerance = Column(Float, default=0.5)
    last_tick = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User")

class EconomyEvent(Base):
    __tablename__ = "economy_events"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    affected_zone = Column(SQLEnum(ZoneEnum), nullable=True)
    price_modifier = Column(Float, default=1.0)
    active_until = Column(DateTime, nullable=False)
"""

content = content.replace("class Hat(Base):", models_addition + "\nclass Hat(Base):")

# 2. Add Match Engine Logic
match_engine_code = """
def match_orders(db: Session, hat_id: str):
    # Fetch OPEN or PARTIAL orders for this hat
    buy_orders = db.query(Order).filter(
        Order.hat_id == hat_id,
        Order.side == OrderSide.BUY,
        Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIAL])
    ).order_by(Order.price.desc(), Order.created_at.asc()).all()
    
    sell_orders = db.query(Order).filter(
        Order.hat_id == hat_id,
        Order.side == OrderSide.SELL,
        Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIAL])
    ).order_by(Order.price.asc(), Order.created_at.asc()).all()
    
    for buy in buy_orders:
        if buy.status not in (OrderStatus.OPEN, OrderStatus.PARTIAL):
            continue
            
        for sell in sell_orders:
            if sell.status not in (OrderStatus.OPEN, OrderStatus.PARTIAL):
                continue
                
            if buy.price >= sell.price:
                # Match found! Price is based on the resting order
                match_price = sell.price if sell.created_at < buy.created_at else buy.price
                
                buy_remaining = buy.quantity - buy.filled_quantity
                sell_remaining = sell.quantity - sell.filled_quantity
                
                trade_qty = min(buy_remaining, sell_remaining)
                
                # Execute trade
                trade = Trade(
                    buy_order_id=buy.id,
                    sell_order_id=sell.id,
                    hat_id=hat_id,
                    price=match_price,
                    quantity=trade_qty,
                    buyer_id=buy.user_id,
                    seller_id=sell.user_id,
                    fee_paid=int(trade_qty * match_price * 0.03)
                )
                db.add(trade)
                
                buy.filled_quantity += trade_qty
                sell.filled_quantity += trade_qty
                
                if buy.filled_quantity >= buy.quantity:
                    buy.status = OrderStatus.FILLED
                else:
                    buy.status = OrderStatus.PARTIAL
                    
                if sell.filled_quantity >= sell.quantity:
                    sell.status = OrderStatus.FILLED
                else:
                    sell.status = OrderStatus.PARTIAL
                
                # Give hat to buyer
                buyer_inv = db.query(InventoryItem).filter(
                    InventoryItem.user_id == buy.user_id,
                    InventoryItem.hat_id == hat_id,
                    InventoryItem.equipped == False
                ).first()
                if buyer_inv:
                    buyer_inv.quantity += trade_qty
                else:
                    db.add(InventoryItem(user_id=buy.user_id, hat_id=hat_id, quantity=trade_qty))
                
                # Refund buyer if matched at a better price
                if match_price < buy.price:
                    savings = (buy.price - match_price) * trade_qty
                    refund = int(savings * 1.03)
                    buyer_user = db.query(User).filter(User.id == buy.user_id).first()
                    if buyer_user:
                        buyer_user.soul_coins += refund
                
                # Give coins to seller
                seller_user = db.query(User).filter(User.id == sell.user_id).first()
                if seller_user:
                    seller_user.soul_coins += trade_qty * match_price
                
                db.commit()
                
            if buy.status == OrderStatus.FILLED:
                break

"""

content = content.replace("@app.post(\"/api/orders\", response_model=OrderResponse)", match_engine_code + "\n@app.post(\"/api/orders\", response_model=OrderResponse)")

# Add call to match_orders inside create_order
create_order_replacement = """    db.add(order_obj)
    db.commit()
    db.refresh(order_obj)
    
    # Run matching engine
    match_orders(db, order_obj.hat_id)
    db.refresh(order_obj)
    
    return order_obj"""
content = content.replace("    db.add(order_obj)\n    db.commit()\n    db.refresh(order_obj)\n    return order_obj", create_order_replacement)

# 3. Add Procedural Economy Generation and AI Businesses Routes
ai_business_routes = """
# === PROCEDURAL ECONOMY & AI BUSINESSES ===
@app.post("/api/gm/economy/procedural-event")
async def procedural_economy_event(db: Session = Depends(get_db)):
    # Generates a random market shock
    import random
    zones = list(ZoneEnum)
    affected = random.choice(zones)
    modifier = random.uniform(0.5, 2.0)
    
    event = EconomyEvent(
        name=f"Procedural Shift: {affected.value.capitalize()}",
        description=f"A sudden shift in the currents has affected {affected.value} supply.",
        affected_zone=affected,
        price_modifier=modifier,
        active_until=datetime.utcnow() + timedelta(hours=24)
    )
    db.add(event)
    
    # Adjust base prices temporarily
    hats = db.query(Hat).filter(Hat.zone == affected).all()
    for hat in hats:
        hat.base_buy_price = int(hat.base_buy_price * modifier)
        hat.base_sell_price = int(hat.base_sell_price * modifier)
        
    db.commit()
    return {"message": "Procedural economy event generated", "event_name": event.name, "modifier": modifier}

@app.post("/api/gm/ai-business/tick")
async def ai_business_tick(db: Session = Depends(get_db)):
    import random
    # Create AI user if not exists
    bot_user = db.query(User).filter(User.username == "NessieBotCorp").first()
    if not bot_user:
        bot_user = User(
            username="NessieBotCorp",
            email="bot@loch.exchange",
            hashed_password=get_password_hash("botpassword"),
            soul_coins=1000000
        )
        db.add(bot_user)
        db.commit()
        db.refresh(bot_user)
        
    # Get or create bot businesses
    businesses = db.query(Business).filter(Business.is_ai_operated == True).all()
    if not businesses:
        b1 = Business(owner_id=bot_user.id, name="Auto Kelp Harvester", business_type="Production", is_ai_operated=True, funds=5000)
        db.add(b1)
        db.commit()
        businesses = [b1]
        
    # Simulate business activity (Bot placing random market orders)
    for b in businesses:
        # Procedurally decide to buy or sell
        hats = db.query(Hat).limit(5).all()
        target_hat = random.choice(hats)
        
        if random.random() < b.ai_risk_tolerance:
            # Create a BUY order
            price = int(target_hat.base_buy_price * random.uniform(0.9, 1.1))
            qty = random.randint(1, b.level * 2)
            if bot_user.soul_coins >= price * qty:
                order = Order(user_id=bot_user.id, hat_id=target_hat.id, side=OrderSide.BUY, price=price, quantity=qty)
                db.add(order)
                bot_user.soul_coins -= price * qty
        else:
            # Generate items and SELL
            price = int(target_hat.base_sell_price * random.uniform(0.9, 1.2))
            qty = random.randint(1, b.level)
            order = Order(user_id=bot_user.id, hat_id=target_hat.id, side=OrderSide.SELL, price=price, quantity=qty)
            db.add(order)
            
            # Grant items to bot inventory if needed
            inv = db.query(InventoryItem).filter(InventoryItem.user_id == bot_user.id, InventoryItem.hat_id == target_hat.id).first()
            if not inv:
                inv = InventoryItem(user_id=bot_user.id, hat_id=target_hat.id, quantity=qty)
                db.add(inv)
            else:
                inv.quantity += qty
                
    db.commit()
    
    # Run match engine for all hats traded
    for hat in hats:
        match_orders(db, hat.id)
        
    return {"message": "AI businesses processed tick and interacted with CLOB"}
"""

content = content.replace("# Leaderboard", ai_business_routes + "\n# Leaderboard")

with open("server/main.py", "w") as f:
    f.write(content)

print("Patch applied to server/main.py")

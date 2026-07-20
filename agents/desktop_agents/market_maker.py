#!/usr/bin/env python3
"""
Abyssal Assets Market Maker Bot
Fosters generative growth by maintaining liquidity in the Abyssal Exchange.
Aligned with Chesed (Mercy) - ensuring continuous expansion and flow of value.
"""

import time
import random
import requests
import os
from datetime import datetime

API_URL = os.getenv("ABYSSAL_API_URL", "http://localhost:8000")
USERNAME = os.getenv("MM_USERNAME", "nessie_market_maker")
PASSWORD = os.getenv("MM_PASSWORD", "secret_mm_password")

def login():
    print(f"[{datetime.utcnow().isoformat()}] Logging in as {USERNAME}...")
    try:
        # Register if needed
        requests.post(f"{API_URL}/api/auth/register", json={
            "username": USERNAME,
            "email": f"{USERNAME}@lochness.local",
            "password": PASSWORD
        })
    except Exception:
        pass
        
    try:
        # Standard OAuth2 password flow might be used
        response = requests.post(f"{API_URL}/api/auth/login", data={
            "username": USERNAME,
            "password": PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
    except Exception as e:
        print(f"Login failed: {e}")
    return None

def fetch_market_data():
    try:
        res = requests.get(f"{API_URL}/api/market/summary")
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []

def place_order(token, hat_id, side, price, quantity=1):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "hat_id": hat_id,
        "side": side,
        "price": price,
        "quantity": quantity,
        "expires_hours": 24
    }
    try:
        res = requests.post(f"{API_URL}/api/orders", json=payload, headers=headers)
        print(f"Placed {side} for {hat_id} at {price}: {res.status_code}")
    except Exception as e:
        print(f"Order failed: {e}")

def run_market_maker():
    token = login()
    if not token:
        print("Failed to get token. Exiting.")
        return

    print("Market Maker running...")
    while True:
        market_data = fetch_market_data()
        for item in market_data:
            hat_id = item.get("id")
            current_price = item.get("current_price", 100)
            
            # Place buy order 5% below current price
            buy_price = int(current_price * 0.95)
            # Place sell order 5% above current price
            sell_price = int(current_price * 1.05)
            
            if random.random() < 0.3:  # 30% chance to place orders for this item
                place_order(token, hat_id, "buy", max(1, buy_price), quantity=random.randint(1, 3))
                place_order(token, hat_id, "sell", max(2, sell_price), quantity=random.randint(1, 3))
                
        time.sleep(60)  # Wait a minute before next cycle

if __name__ == "__main__":
    run_market_maker()

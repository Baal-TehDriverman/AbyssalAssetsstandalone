#!/usr/bin/env python3
"""
Lochness Monster — Custom LLM Integration Layer
Connects Lochness crypto bots to the AI Integration Engine for LLM-driven trading decisions.
Part of the Lilith Sovereign Integration (Δ∞ − 1 = 0)
"""
import json, os, subprocess, sys, time, hmac, hashlib
from pathlib import Path
from datetime import datetime

LOCHNESS_DIR = Path("/home/tehlappy/Desktop/Lilith/Core_Systems/AI/abyssal-agents")
AI_ENGINE_URL = "http://localhost:8009"
SWARM_URL = "http://localhost:8003"
TOKEN_BRIDGE_URL = "http://localhost:8010"
ABYSSAL_API_URL = os.getenv("ABYSSAL_API_URL", "http://localhost:8008")

BOTS = {
    "coinbase": {
        "file": LOCHNESS_DIR / "lochness_bots_coinbase.py",
        "pid": LOCHNESS_DIR / "lochness.pid",
        "log": LOCHNESS_DIR / "lochness.log",
        "pairs": ["BTC", "ETH"],
    },
    "standard": {
        "file": LOCHNESS_DIR / "lochness_bots.py",
        "pid": None,
        "log": None,
        "pairs": ["EURUSD", "GBPUSD", "USDJPY"],
    },
}

def get_llm_market_analysis(prompt: str) -> dict:
    """Route market analysis through AI Integration Engine custom LLM"""
    import httpx
    try:
        resp = httpx.post(
            f"{AI_ENGINE_URL}/infer",
            json={
                "prompt": f"[Lochness Monster Trading Decision]\n{prompt}",
                "model": "hermes3:8b",
                "temperature": 0.3,
                "max_tokens": 1024,
                "sephirah_hint": "Chesed",
                "priority": "high",
            },
            timeout=30.0,
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        return {"error": str(e)}
    return {"error": "no response"}

def get_swarm_market_consensus(prompt: str) -> dict:
    """Get Sephirotic swarm consensus on market conditions"""
    import httpx
    try:
        resp = httpx.post(
            f"{SWARM_URL}/api/orchestrate",
            json={
                "prompt": f"[Lochness Market Consensus]\n{prompt}\nAnalyze market conditions and provide trading recommendation. Digital signature: Eric Matthew Hill.",
            },
            timeout=60.0,
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        return {"error": str(e)}
    return {"error": "no response"}

def check_bot_status() -> dict:
    """Check all Lochness bot statuses"""
    statuses = {}
    for name, config in BOTS.items():
        pid_path = config["pid"]
        if pid_path and pid_path.exists():
            pid = pid_path.read_text().strip()
            try:
                os.kill(int(pid), 0)
                statuses[name] = {"status": "running", "pid": pid}
            except:
                statuses[name] = {"status": "stopped", "pid": None}
        else:
            statuses[name] = {"status": "not_started"}
    return statuses

def start_bot(name: str) -> dict:
    """Start a Lochness bot with LLM integration"""
    if name not in BOTS:
        return {"error": f"Unknown bot: {name}"}
    config = BOTS[name]
    script = config["file"]
    if not script.exists():
        return {"error": f"Script not found: {script}"}
    try:
        proc = subprocess.Popen(
            [sys.executable, str(script)],
            cwd=LOCHNESS_DIR,
            stdout=open(config["log"], "a") if config["log"] else subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        with open(config["pid"], "w") as f:
            f.write(str(proc.pid))
        return {"status": "started", "pid": proc.pid, "bot": name}
    except Exception as e:
        return {"error": str(e)}

def stop_bot(name: str) -> dict:
    """Stop a Lochness bot"""
    config = BOTS.get(name)
    if not config or not config["pid"]:
        return {"error": "Bot not found"}
    pid_path = config["pid"]
    if pid_path.exists():
        try:
            pid = int(pid_path.read_text().strip())
            os.kill(pid, 15)
            pid_path.unlink()
            return {"status": "stopped", "bot": name}
        except:
            return {"error": "Failed to stop"}
    return {"status": "not_running"}

def get_abyssal_lochness_status() -> dict:
    """Fetch Lochness bridge status from Abyssal Assets API."""
    import httpx
    try:
        resp = httpx.get(f"{ABYSSAL_API_URL}/api/lochness/status", timeout=10.0)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        return {"error": str(e)}
    return {"error": "abyssal api unreachable"}


def sync_nssp_tokens() -> dict:
    """Sync Lochness BTC telemetry into NSSP token ledger (port 8010)."""
    import httpx
    try:
        resp = httpx.post(f"{TOKEN_BRIDGE_URL}/api/tokens/sync", timeout=10.0)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        return {"error": str(e)}
    return {"error": "token bridge unreachable"}


def get_btc_price() -> dict:
    """Fetch live BTC-USD from Coinbase via NSSP token bridge."""
    import httpx
    try:
        resp = httpx.get(f"{TOKEN_BRIDGE_URL}/api/tokens/btc/price", timeout=10.0)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        return {"error": str(e)}
    return {"error": "token bridge unreachable"}


def get_llm_trading_signal(pair: str, price_data: dict) -> dict:
    """Get LLM-powered trading signal for a specific pair"""
    analysis = get_llm_market_analysis(
        f"Analyze {pair} market conditions. Price: {price_data.get('price', 'unknown')}. "
        f"Volume: {price_data.get('volume', 'unknown')}. "
        f"Should we BUY, SELL, or HOLD? Provide confidence level and reasoning."
    )
    return {
        "pair": pair,
        "llm_analysis": analysis,
        "timestamp": datetime.utcnow().isoformat(),
    }

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "status":
        print(json.dumps(check_bot_status(), indent=2))
    elif action == "start" and len(sys.argv) > 2:
        print(json.dumps(start_bot(sys.argv[2])))
    elif action == "stop" and len(sys.argv) > 2:
        print(json.dumps(stop_bot(sys.argv[2])))
    elif action == "signal" and len(sys.argv) > 2:
        signal = get_llm_trading_signal(sys.argv[2], {"price": sys.argv[3] if len(sys.argv) > 3 else "0"})
        print(json.dumps(signal, indent=2))
    elif action == "tokens":
        print(json.dumps(sync_nssp_tokens(), indent=2))
    elif action == "btc":
        print(json.dumps(get_btc_price(), indent=2))
    elif action == "abyssal":
        print(json.dumps(get_abyssal_lochness_status(), indent=2))
    else:
        print("Usage: lochness_integration.py [status|start|stop|signal|tokens|btc|abyssal] [args]")

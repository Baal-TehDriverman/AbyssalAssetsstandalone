from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any


DEFAULT_DB_PATH = "/home/tehlappy/Desktop/AI/memory/golem_diary.db"
DEFAULT_CONFIG_PATH = "/home/tehlappy/Desktop/AI/Pub/config/bidirectional_memory.yaml"


class SharedMind:
    """Small SQLite adapter for the local shared cerebellum.

    The canonical memory engine lives in the Hermes concurrent-bidirectional
    memory skill. This adapter keeps MSN agents decoupled from that skill path
    while using the same WAL database and tables.
    """

    def __init__(self) -> None:
        self.db_path = Path(os.getenv("MSN_SHARED_MEMORY_DB", DEFAULT_DB_PATH))
        self.config_path = Path(os.getenv("MSN_SHARED_MEMORY_CONFIG", DEFAULT_CONFIG_PATH))
        self.busy_timeout_ms = int(os.getenv("MSN_SHARED_MEMORY_BUSY_TIMEOUT_MS", "30000"))
        self.session_id = os.getenv("HERMES_SESSION_ID", f"msn_router_{int(time.time())}")

    def available(self) -> bool:
        return self.db_path.exists()

    def _connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path, timeout=self.busy_timeout_ms / 1000)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(f"PRAGMA busy_timeout={self.busy_timeout_ms};")
        self._ensure_schema(conn)
        return conn

    def _ensure_schema(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS episodic_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                intent TEXT,
                status TEXT,
                details TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS bidirectional_memory_state (
                step_id INTEGER PRIMARY KEY AUTOINCREMENT,
                forward_state TEXT NOT NULL,
                backward_state TEXT NOT NULL,
                bridge_state TEXT NOT NULL,
                environment_signature TEXT NOT NULL,
                objective_vector TEXT NOT NULL,
                timestamp REAL NOT NULL,
                coherence_score REAL NOT NULL,
                trigger_condition TEXT,
                session_id TEXT,
                metadata TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_bidirectional_timestamp
            ON bidirectional_memory_state(timestamp)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_bidirectional_coherence
            ON bidirectional_memory_state(coherence_score)
            """
        )

    def _objective_vector(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        vector = [byte / 255.0 for byte in digest[:32]]
        norm = sum(value * value for value in vector) ** 0.5
        return [value / norm for value in vector] if norm else vector

    def _environment_signature(self, payload: dict[str, Any]) -> str:
        encoded = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:32]

    def record_event(
        self,
        *,
        agent_id: str,
        intent: str,
        status: str,
        details: dict[str, Any] | None = None,
    ) -> int | None:
        if not self.available():
            return None
        payload = {"agent_id": agent_id, **(details or {})}
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO episodic_memory(intent, status, details) VALUES (?, ?, ?)",
                (intent, status, json.dumps(payload, sort_keys=True, default=str)),
            )
            return int(cur.lastrowid)

    def record_step(
        self,
        *,
        agent_id: str,
        objective: str,
        forward_state: dict[str, Any],
        backward_state: dict[str, Any] | None = None,
        trigger_condition: str = "agent_event",
        metadata: dict[str, Any] | None = None,
    ) -> int | None:
        if not self.available():
            return None
        backward_state = backward_state or {"projected_intent": objective}
        bridge_state = {
            "agent_id": agent_id,
            "forward_keys": sorted(forward_state.keys()),
            "backward_keys": sorted(backward_state.keys()),
        }
        environment = self._environment_signature(
            {
                "agent_id": agent_id,
                "cwd": os.getcwd(),
                "pid": os.getpid(),
                "session_id": self.session_id,
            }
        )
        vector = self._objective_vector(objective)
        coherence = self._coherence(forward_state, backward_state)
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO bidirectional_memory_state
                (forward_state, backward_state, bridge_state, environment_signature,
                 objective_vector, timestamp, coherence_score, trigger_condition,
                 session_id, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    json.dumps(forward_state, sort_keys=True, default=str),
                    json.dumps(backward_state, sort_keys=True, default=str),
                    json.dumps(bridge_state, sort_keys=True, default=str),
                    environment,
                    json.dumps(vector),
                    time.time(),
                    coherence,
                    trigger_condition,
                    self.session_id,
                    json.dumps(metadata or {}, sort_keys=True, default=str),
                ),
            )
            return int(cur.lastrowid)

    def _coherence(self, forward_state: dict[str, Any], backward_state: dict[str, Any]) -> float:
        forward_tokens = set(json.dumps(forward_state, default=str).lower().split())
        backward_tokens = set(json.dumps(backward_state, default=str).lower().split())
        if not forward_tokens or not backward_tokens:
            return 0.0
        return min(1.0, len(forward_tokens & backward_tokens) / max(len(forward_tokens), len(backward_tokens)) * 1.5)

    def recall(self, *, limit: int = 5, agent_id: str | None = None) -> list[dict[str, Any]]:
        if not self.available():
            return []
        limit = max(1, min(limit, 25))
        with self._connect() as conn:
            if agent_id:
                rows = conn.execute(
                    """
                    SELECT step_id, forward_state, backward_state, bridge_state,
                           timestamp, coherence_score, trigger_condition, session_id, metadata
                    FROM bidirectional_memory_state
                    WHERE json_extract(bridge_state, '$.agent_id') = ?
                    ORDER BY step_id DESC
                    LIMIT ?
                    """,
                    (agent_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT step_id, forward_state, backward_state, bridge_state,
                           timestamp, coherence_score, trigger_condition, session_id, metadata
                    FROM bidirectional_memory_state
                    ORDER BY step_id DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
        return [
            {
                "step_id": row[0],
                "forward_state": json.loads(row[1]),
                "backward_state": json.loads(row[2]),
                "bridge_state": json.loads(row[3]),
                "timestamp": row[4],
                "coherence_score": row[5],
                "trigger_condition": row[6],
                "session_id": row[7],
                "metadata": json.loads(row[8]) if row[8] else {},
            }
            for row in rows
        ]

    def stats(self) -> dict[str, Any]:
        if not self.available():
            return {"available": False, "db_path": str(self.db_path)}
        with self._connect() as conn:
            tables = {
                "episodic_memory": conn.execute("SELECT COUNT(*) FROM episodic_memory").fetchone()[0],
                "bidirectional_memory_state": conn.execute("SELECT COUNT(*) FROM bidirectional_memory_state").fetchone()[0],
            }
            journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
            busy_timeout = conn.execute("PRAGMA busy_timeout").fetchone()[0]
        return {
            "available": True,
            "db_path": str(self.db_path),
            "config_path": str(self.config_path),
            "session_id": self.session_id,
            "journal_mode": journal_mode,
            "busy_timeout_ms": busy_timeout,
            "tables": tables,
            "ram_budget_gb": int(os.getenv("MSN_SHARED_MEMORY_RAM_BUDGET_GB", "128")),
        }


shared_mind = SharedMind()

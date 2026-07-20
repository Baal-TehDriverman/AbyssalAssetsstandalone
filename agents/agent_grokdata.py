# Wave 4 — Grokdata Memory Agent
# Indexes and queries Grok conversation history from golem_diary.db

from agents import SubAgent, AgentManifest, register_agent
from fastapi import Query
import json, os, time, sqlite3

DB_PATH = os.path.join(
    os.environ.get("PUB_ROOT", os.path.expanduser("~/Desktop/AI/Pub")),
    "00_CORE_SERVICES", "quantum_paradox_terminal", "golem_diary.db"
)

manifest = AgentManifest(
    id="grokdata",
    name="Grokdata Memory Index",
    version="1.0.1",
    description="Indexed Grok conversation history — search, browse, and retrieve past conversations",
    wave=4,
    sephira="Da'at",
)


def _get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


class GrokdataAgent(SubAgent):
    def _register_routes(self):
        super()._register_routes()

        @self.router.get("/stats")
        async def stats():
            db = _get_db()
            convs = db.execute("SELECT COUNT(*) as c FROM episodic_memories").fetchone()
            msgs = db.execute("SELECT COUNT(*) as c FROM memories WHERE log_type = 'GROK_MSG'").fetchone()
            conv_full = db.execute("SELECT COUNT(*) as c FROM memories WHERE log_type = 'GROK_CONV'").fetchone()
            total_chars = db.execute("SELECT COALESCE(SUM(LENGTH(message)), 0) as c FROM memories WHERE log_type LIKE 'GROK_%'").fetchone()
            db.close()
            return {
                "conversations": convs["c"],
                "messages": msgs["c"],
                "full_conversations": conv_full["c"],
                "total_characters": total_chars["c"],
                "source": "grok_conversations.json (2025-04 to 2026-05)",
            }

        @self.router.get("/conversations")
        async def list_conversations(limit: int = 50, offset: int = 0):
            db = _get_db()
            rows = db.execute(
                "SELECT timestamp, score, substr(message, 1, 300) as summary FROM episodic_memories ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
            db.close()
            convs = []
            for r in rows:
                lines = r["summary"].split("\n")
                title = "UNTITLED"
                msg_count = "?"
                for line in lines:
                    if line.startswith("GROK_CONVERSATION:"):
                        title = line.split(":", 1)[1].strip()
                    elif line.startswith("Messages:"):
                        msg_count = line.split(":", 1)[1].strip()
                convs.append({
                    "title": title,
                    "ts": r["timestamp"],
                    "score": r["score"],
                    "messages": msg_count,
                })
            return {"conversations": convs, "total": len(convs), "offset": offset}

        @self.router.get("/search")
        async def search(q: str = Query(..., description="Search query"), limit: int = 20):
            db = _get_db()
            pattern = f"%{q}%"
            results = db.execute(
                """SELECT timestamp, log_type, substr(message, 1, 500) as snippet
                   FROM memories
                   WHERE log_type LIKE 'GROK_%' AND message LIKE ?
                   ORDER BY timestamp DESC LIMIT ?""",
                (pattern, limit),
            ).fetchall()
            db.close()
            return {
                "query": q,
                "results": [{"ts": r["timestamp"], "type": r["log_type"], "snippet": r["snippet"]} for r in results],
            }

        @self.router.get("/conv/{conv_id:path}")
        async def get_conversation(conv_id: str, max_messages: int = 50):
            db = _get_db()
            # Search by title or display partial ID match
            pattern = f"%{conv_id}%"
            episodic = db.execute(
                "SELECT * FROM episodic_memories WHERE message LIKE ? ORDER BY timestamp DESC LIMIT 1",
                (pattern,),
            ).fetchone()
            if not episodic:
                # Try direct ID search in memory messages
                episodic = db.execute(
                    "SELECT timestamp, score, message FROM episodic_memories ORDER BY ABS(timestamp) DESC LIMIT 1"
                ).fetchone()

            if not episodic:
                db.close()
                return {"error": "No conversations found"}

            # Get messages for this conversation (by matching title)
            title_line = [l for l in episodic["message"].split("\n") if l.startswith("GROK_CONVERSATION:")]
            title = title_line[0].split(":", 1)[1].strip() if title_line else ""

            msgs = db.execute(
                """SELECT timestamp, log_type, substr(message, 1, 1000) as message
                   FROM memories
                   WHERE log_type = 'GROK_MSG' AND message LIKE ?
                   ORDER BY id DESC LIMIT ?""",
                (f"%{title[:30]}%", max_messages),
            ).fetchall()
            db.close()

            return {
                "title": title,
                "ts": episodic["timestamp"],
                "score": episodic["score"],
                "messages": [{"ts": m["timestamp"], "text": m["message"]} for m in msgs],
            }


agent = GrokdataAgent(manifest)
register_agent(agent)

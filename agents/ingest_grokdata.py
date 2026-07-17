#!/usr/bin/env python3
"""
Ingest Grok conversation export into God Engine memory database.
Reads grok_conversations.json, stores each conversation as episodic memory
and each message as a memory entry.
"""

import json
import sqlite3
import time
import sys
import os

GROK_JSON = os.path.expanduser("~/Desktop/AI/grokdata_extracted/grok_conversations.json")
DB_PATH = os.path.expanduser("~/Desktop/AI/Pub/00_CORE_SERVICES/quantum_paradox_terminal/golem_diary.db")


def ingest():
    print(f"Reading {GROK_JSON}...")
    with open(GROK_JSON) as f:
        data = json.load(f)

    convs = data.get("conversations", [])
    posts = data.get("media_posts", [])
    print(f"Loaded {len(convs)} conversations, {len(posts)} media posts")

    db = sqlite3.connect(DB_PATH)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=NORMAL")

    now_ms = int(time.time() * 1000)
    inserted_conv = 0
    inserted_msg = 0
    skipped = 0

    for c in convs:
        meta = c.get("conversation", {})
        conv_id = meta.get("id", "")
        title = meta.get("title", "UNTITLED")
        create_time = meta.get("create_time", "")
        modify_time = meta.get("modify_time", "")
        responses = c.get("responses", [])

        if not responses:
            skipped += 1
            continue

        # Parse timestamps to unix ms
        ts_epoch = 0
        if create_time:
            try:
                ts_epoch = int(
                    time.mktime(time.strptime(create_time[:19], "%Y-%m-%dT%H:%M:%S")) * 1000
                )
            except (ValueError, OSError):
                ts_epoch = now_ms

        # Score = number of responses * avg message length factor / 1000
        total_chars = sum(len(r.get("response", {}).get("message", "")) for r in responses)
        score = min(len(responses) * (total_chars / max(len(responses), 1)) / 5000, 10.0)

        # Build summary for episodic memory
        first_msg = responses[0].get("response", {}).get("message", "")[:200] if responses else ""
        summary = (
            f"GROK_CONVERSATION: {title}\n"
            f"ID: {conv_id}\n"
            f"Created: {create_time}\n"
            f"Modified: {modify_time}\n"
            f"Messages: {len(responses)}\n"
            f"Preview: {first_msg}"
        )

        # Store as episodic memory
        db.execute(
            "INSERT INTO episodic_memories (timestamp, score, message) VALUES (?, ?, ?)",
            (ts_epoch, round(score, 2), summary),
        )
        inserted_conv += 1

        # Store individual messages as memories
        for r in responses:
            resp = r.get("response", {})
            msg_text = resp.get("message", "")[:500]
            if msg_text.strip():
                db.execute(
                    "INSERT INTO memories (timestamp, log_type, message) VALUES (?, ?, ?)",
                    (ts_epoch, "GROK_MSG", msg_text),
                )
                inserted_msg += 1

        # Also store the full conversation as a single memory entry for search
        full_text = "\n\n".join(
            r.get("response", {}).get("message", "")[:2000] for r in responses
        )
        if len(full_text) > 500:
            db.execute(
                "INSERT INTO memories (timestamp, log_type, message) VALUES (?, ?, ?)",
                (ts_epoch, "GROK_CONV", f"{title}\n\n{full_text[:3000]}"),
            )

        if inserted_conv % 25 == 0:
            print(f"  Progress: {inserted_conv}/{len(convs)} conversations...")
            db.commit()

    db.commit()
    db.close()

    print(f"\nDone!")
    print(f"  Conversations: {inserted_conv} stored (+ {skipped} skipped, no messages)")
    print(f"  Messages: {inserted_msg} stored")
    print(f"  Total new rows: {inserted_conv + inserted_msg + inserted_conv}")


if __name__ == "__main__":
    ingest()

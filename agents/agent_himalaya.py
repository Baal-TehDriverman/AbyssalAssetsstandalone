# Wave 4 — Himalaya Email Swarm

from agents import SubAgent, AgentManifest, register_agent
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
import urllib.parse
import re
import httpx
import asyncio

manifest = AgentManifest(
    id="himalaya",
    name="Himalaya Email",
    version="1.1.1",
    sephira="NETZACH",
    description="AI-driven email pipeline — fetch, filter, categorize, route, draft, queue with swarm agents and human review",
    wave=4,
)

class OffloadRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = "You are a helpful assistant."
    model: Optional[str] = "Hermes"
    provider: Optional[str] = "antigravity"

class HimalayaAgent(SubAgent):
    def _register_routes(self):
        super()._register_routes()

        @self.router.get("/pipeline")
        async def email_pipeline():
            return {
                "stages": ["Fetch", "Filter", "Categorize", "Route", "Draft", "Queue"],
                "agents": ["Email Scanner", "Classifier", "Drafter", "Legal Scribe", "Ledger Clerk", "Archivist"],
            }

        @self.router.get("/categories")
        async def categories():
            return {
                "categories": ["action_required", "information", "legal", "financial", "personal", "spam"],
                "routes": {
                    "action_required": "task_system",
                    "information": "summary_and_file",
                    "legal": "palantir_rico",
                    "financial": "ledger_analytics",
                    "personal": "lyra_dialogue",
                    "spam": "silent_discard",
                },
            }

        @self.router.get("/check")
        async def himalaya_check():
            import shutil
            himalaya_path = shutil.which("himalaya")
            return {
                "installed": himalaya_path is not None,
                "path": himalaya_path,
                "hint": "Run 'sudo pacman -S himalaya' to install",
            }

        @self.router.get("/search")
        async def email_search(q: str, limit: int = 50, account: Optional[str] = None, folder: Optional[str] = None):
            db_path = "/home/tehlappy/Desktop/AI/Pub/data/himalaya_daemon_state.db"
            if not os.path.exists(db_path):
                return {"error": "Himalaya database not found. Run the daemon/pipeline first.", "emails": []}
            try:
                import sqlite3
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                conditions = ["(subject LIKE ? OR from_addr LIKE ? OR from_name LIKE ? OR to_addr LIKE ? OR raw_json LIKE ?)"]
                params = [f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%"]
                
                if account:
                    conditions.append("account = ?")
                    params.append(account)
                if folder:
                    conditions.append("folder = ?")
                    params.append(folder)
                    
                sql = f"""
                    SELECT id, account, folder, subject, from_addr, from_name, to_addr, date, urgency, case_flags
                    FROM emails
                    WHERE {" AND ".join(conditions)}
                    ORDER BY date DESC
                    LIMIT ?
                """
                params.append(limit)
                
                rows = cursor.execute(sql, params).fetchall()
                conn.close()
                return {
                    "query": q,
                    "count": len(rows),
                    "emails": [dict(r) for r in rows]
                }
            except Exception as e:
                return {"error": str(e), "emails": []}

        @self.router.post("/pipeline/run")
        async def run_pipeline():
            import subprocess
            python_path = "/home/tehlappy/Desktop/AI/Pub/.venv-pub/bin/python"
            script_path = "/home/tehlappy/Desktop/AI/Pub/scripts/himalaya_daemon.py"
            try:
                proc = await asyncio.create_subprocess_exec(
                    python_path, script_path, "once",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()
                if proc.returncode == 0:
                    return {
                        "status": "success",
                        "message": "Himalaya pipeline completed successfully.",
                        "stdout": stdout.decode(errors='replace')[-500:]
                    }
                else:
                    return {
                        "status": "failed",
                        "error": stderr.decode(errors='replace')
                    }
            except Exception as e:
                return {"status": "error", "error": str(e)}

        @self.router.post("/offload")
        async def offload_compute(req: OffloadRequest):
            if req.provider == "google":
                url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(req.prompt)}"
                headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"}
                try:
                    async with httpx.AsyncClient(timeout=15.0) as client:
                        resp = await client.get(url, headers=headers)
                        if resp.status_code == 200:
                            html = resp.text
                            if "anomaly-modal" not in html:
                                snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
                                titles = re.findall(r'<a class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
                                results = []
                                for i in range(min(len(snippets), len(titles))):
                                    clean_title = re.sub(r'<[^>]+>', '', titles[i][1]).strip()
                                    clean_snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()
                                    results.append({
                                        "title": clean_title,
                                        "link": titles[i][0],
                                        "snippet": clean_snippet
                                    })
                                if results:
                                    return {
                                        "status": "success",
                                        "provider": "duckduckgo",
                                        "results": results[:5]
                                    }
                except Exception:
                    pass
                
                # Wikipedia Fallback
                try:
                    wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(req.prompt)}&format=json"
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        wiki_resp = await client.get(wiki_url, headers={"User-Agent": "HimalayaAgent/1.1"})
                        if wiki_resp.status_code == 200:
                            data = wiki_resp.json()
                            wiki_results = []
                            for r in data.get("query", {}).get("search", []):
                                snippet = re.sub(r'<[^>]+>', '', r.get("snippet", "")).strip()
                                wiki_results.append({
                                    "title": r.get("title"),
                                    "link": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(r.get('title'))}",
                                    "snippet": snippet
                                })
                            if wiki_results:
                                return {
                                    "status": "success",
                                    "provider": "wikipedia",
                                    "results": wiki_results[:5]
                                }
                except Exception as wiki_e:
                    return {"status": "error", "error": f"DDG blocked and Wikipedia failed: {str(wiki_e)}"}
                
                return {"status": "success", "results": [], "note": "No results found (DDG blocked, Wikipedia empty)"}
            
            # Default to Antigravity Bridge
            bridge_url = "http://127.0.0.1:8002/v1/messages"
            headers = {
                "X-Token": "devtoken",
                "Content-Type": "application/json"
            }
            anthropic_payload = {
                "model": req.model,
                "max_tokens": 4096,
                "system": req.system_prompt,
                "messages": [
                    {"role": "user", "content": req.prompt}
                ],
                "stream": False
            }
            
            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    resp = await client.post(bridge_url, json=anthropic_payload, headers=headers)
                    if resp.status_code != 200:
                        return {
                            "status": "error",
                            "error": f"Bridge returned status {resp.status_code}: {resp.text}"
                        }
                    
                    data = resp.json()
                    content = data.get("content", [])
                    text_content = ""
                    for block in content:
                        if block.get("type") == "text":
                            text_content += block.get("text", "")
                            
                    return {
                        "status": "success",
                        "response": text_content,
                        "model": data.get("model")
                    }
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e)
                }

agent = HimalayaAgent(manifest)
register_agent(agent)

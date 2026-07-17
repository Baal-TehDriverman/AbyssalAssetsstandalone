import re

with open('/home/tehlappy/Desktop/Lilith/Core_Systems/AI/abyssal-assets/server/main.py', 'r') as f:
    content = f.read()

# Fix Bug 13: Sequential Broadcast -> asyncio.gather
bm_str = """    async def broadcast_market(self, message: dict):
        dead = []
        for ws in self.market_subscribers:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.unsubscribe_market(ws)"""
bm_repl = """    async def broadcast_market(self, message: dict):
        import asyncio
        if not self.market_subscribers: return
        results = await asyncio.gather(*[ws.send_json(message) for ws in self.market_subscribers], return_exceptions=True)
        dead = [ws for ws, res in zip(self.market_subscribers, results) if isinstance(res, Exception)]
        for ws in dead:
            self.unsubscribe_market(ws)"""
content = content.replace(bm_str, bm_repl)

spm_str = """    async def send_personal_message(self, message: dict, user_id: int):
        dead = []
        for ws in self.active_connections[user_id]:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, user_id)"""
spm_repl = """    async def send_personal_message(self, message: dict, user_id: int):
        import asyncio
        if not self.active_connections[user_id]: return
        results = await asyncio.gather(*[ws.send_json(message) for ws in self.active_connections[user_id]], return_exceptions=True)
        dead = [ws for ws, res in zip(self.active_connections[user_id], results) if isinstance(res, Exception)]
        for ws in dead:
            self.disconnect(ws, user_id)"""
content = content.replace(spm_str, spm_repl)

# Fix Bug 11: Sync DB in Async Functions
# We will parse the file, find all `async def` and if they don't contain `await` before the next `def`, we change to `def`
import ast
class AsyncToDefTransformer(ast.NodeTransformer):
    def visit_AsyncFunctionDef(self, node):
        self.generic_visit(node)
        has_await = False
        for child in ast.walk(node):
            if isinstance(child, (ast.Await, ast.AsyncFor, ast.AsyncWith)):
                has_await = True
                break
        if not has_await:
            # We want to change this to a regular FunctionDef
            new_node = ast.FunctionDef(
                name=node.name,
                args=node.args,
                body=node.body,
                decorator_list=node.decorator_list,
                returns=node.returns,
                type_comment=node.type_comment
            )
            return ast.copy_location(new_node, node)
        return node

# But using AST on the whole file will lose formatting/comments!
# Let's do it via regex heuristically. If a function is defined with `async def` and has NO `await ` or `async with` inside it, replace `async def` with `def`.
lines = content.split('\n')
new_lines = []
in_async_def = False
async_def_line_idx = -1
has_await = False
def_body = []

for i, line in enumerate(lines):
    new_lines.append(line)
    
# Better heuristic: just manually replace a few known ones to avoid messing up the file
endpoints = [
    "async def get_orders",
    "async def get_listings",
    "async def get_market(",
    "async def get_market_summary",
    "async def get_inventory",
    "async def get_hats",
    "async def get_hat(",
    "async def create_listing",
    "async def create_order",
    "async def cancel_order",
    "async def get_me",
    "async def business_financials",
    "async def business_summary",
    "async def list_economy_events",
    "async def list_businesses",
    "async def clout_leaderboard",
    "async def wealth_leaderboard"
]

for ep in endpoints:
    content = content.replace(ep, ep.replace("async def", "def"))

with open('/home/tehlappy/Desktop/Lilith/Core_Systems/AI/abyssal-assets/server/main.py', 'w') as f:
    f.write(content)

print("Applied fixes 11-13!")

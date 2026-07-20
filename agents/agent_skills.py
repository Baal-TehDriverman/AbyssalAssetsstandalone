# Wave 2 — Tiferet: Skill System

from agents import SubAgent, AgentManifest, register_agent

manifest = AgentManifest(
    id="skills",
    name="Abyssal Arts",
    version="1.0.1",
    sephira="TIFERET",
    description="Skill system — 24 skills across 6 categories, XP curves (1.15^level), synergies, specializations",
    wave=2,
)


class SkillsAgent(SubAgent):
    def _register_routes(self):
        super()._register_routes()

        @self.router.get("/categories")
        async def list_categories():
            return {
                "categories": [
                    "combat_survival",
                    "haberdashery_crafting",
                    "dredging_looting",
                    "market_trading",
                    "alchemical_arts",
                    "loch_lore",
                ],
                "count": 6,
            }

        @self.router.get("/xp-curve")
        async def xp_curve():
            curve = {}
            for lvl in range(1, 101):
                curve[str(lvl)] = round(100 * (1.15 ** (lvl - 1)))
            return {"formula": "100 * 1.15^(level - 1)", "curve": curve}


agent = SkillsAgent(manifest)
register_agent(agent)

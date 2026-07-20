.PHONY: all deploy resolve read sephira api validate status summary \
        reset server client dredge seed lyra-agent lyra-chat

PYTHON := python3

# ─── Sephirotic Root Interface ───────────────────────────────────

all: deploy

deploy:
	$(PYTHON) sephirotic-deploy.py

deploy-batch-1:
	$(PYTHON) sephirotic-deploy.py --batch 1

deploy-batch-2:
	$(PYTHON) sephirotic-deploy.py --batch 2

deploy-batch-3:
	$(PYTHON) sephirotic-deploy.py --batch 3

resolve:
	@[ "$(FILE)" ] && $(PYTHON) -c "from sephirotic import root; print(root.resolve('$(FILE)'))" || (echo "Usage: make resolve FILE=server/main.py"; exit 1)

read:
	@[ "$(FILE)" ] && $(PYTHON) -c "from sephirotic import root; print(root.read('$(FILE)'))" || (echo "Usage: make read FILE=GDD.md"; exit 1)

sephira:
	@[ "$(NAME)" ] && $(PYTHON) -c "from sephirotic import sephira; [print(f'  {f[\"path\"]} — {f[\"purpose\"]}') for f in sephira('$(NAME)')]" || (echo "Usage: make sephira NAME=KETER"; exit 1)

api:
	@[ "$(ENDPOINT)" ] && $(PYTHON) -c "from sephirotic import root; import json; print(json.dumps(root.api('$(INTERFACE)', '$(ENDPOINT)'), indent=2))" || $(PYTHON) -c "from sephirotic import root; import json; print(json.dumps(root.api('$(INTERFACE)'), indent=2))"
	@echo "Usage: make api INTERFACE=server-api ENDPOINT=health"

validate:
	$(PYTHON) sephirotic-deploy.py --validate

status:
	$(PYTHON) sephirotic-deploy.py --status

summary:
	$(PYTHON) sephirotic-deploy.py --summary

reset:
	$(PYTHON) sephirotic-deploy.py --reset

# ─── Game Commands ───────────────────────────────────────────────

server:
	cd server && $(PYTHON) main.py

client:
	cd client && npm run dev

dredge:
	cd client && npm run dev

seed:
	cd server && $(PYTHON) -c "from main import seed_hats; seed_hats()"

# ─── Lyra ────────────────────────────────────────────────────────

lyra-agent:
	@curl -s http://localhost:3211/lyra/state | $(PYTHON) -m json.tool

lyra-chat:
	@[ "$(MSG)" ] && curl -s -X POST http://localhost:3211/lyra/send \
		-H "Content-Type: application/json" \
		-d "{\"message\": \"$(MSG)\", \"mode\": \"analytical\"}" | $(PYTHON) -m json.tool || echo "Usage: make lyra-chat MSG='hello'"

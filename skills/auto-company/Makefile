# Auto-Company Makefile
# Commands for running the autonomous AI company

.PHONY: help start stop status ideate validate build dashboard

WORKSPACE ?= $(PWD)
CONSENSUS ?= $(WORKSPACE)/memories/consensus.md
SCRIPTS ?= $(WORKSPACE)/scripts

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

start: ## Start the auto-loop (foreground)
	@echo "Starting Auto-Company..."
	@bash $(SCRIPTS)/auto-loop.sh

stop: ## Stop the auto-loop
	@echo "Stopping Auto-Company..."
	@pkill -f auto-loop.sh || true

status: ## Show current status
	@echo "=== Auto-Company Status ==="
	@echo "Workspace: $(WORKSPACE)"
	@if [ -f $(CONSENSUS) ]; then \
		echo "Phase: $$(grep '## Current Phase' $(CONSENSUS) -A1 | tail -1)"; \
		echo "Last Updated: $$(grep '## Last Updated' $(CONSENSUS) -A1 | tail -1)"; \
		echo "Next Action: $$(grep '## Next Action' $(CONSENSUS) -A1 | tail -1)"; \
	else \
		echo "No consensus file found. Run 'make ideate' to start."; \
	fi

ideate: ## Cycle 1: Generate ideas
	@echo "=== Cycle 1: Ideation ==="
	@echo "Spawning: CEO + Research + Munger"
	@echo "Next: Edit memories/consensus.md with results"

validate: ## Cycle 2: Validate top idea (GO/NO-GO)
	@echo "=== Cycle 2: Validation ==="
	@echo "Spawning: Research + CFO + Munger + CEO"
	@echo "Next: Review financial model and market data"

build: ## Cycle 3+: Build the product
	@echo "=== Cycle 3+: Execution ==="
	@echo "Spawning: Product + UI + Full-Stack + QA + DevOps"
	@echo "Next: Review projects/ directory for output"

dashboard: ## Open the web dashboard
	@echo "Dashboard not yet implemented."
	@echo "For now, check: logs/auto-company.log"

clean: ## Clean generated files
	@echo "Cleaning..."
	@rm -rf logs/*
	@echo "Done."

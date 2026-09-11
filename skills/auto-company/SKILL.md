---
name: auto-company
description: Autonomous AI company that operates 24/7 using multi-agent teams. Orchestrates 14 expert AI agents (CEO Bezos, CTO Vogels, Munger, DHH, etc.) to ideate products, write code, deploy, and market without human intervention. Use when user wants to create a self-running AI business, launch a micro-SaaS, build a product autonomously, or run a multi-agent team for continuous execution. Triggers on "auto company", "AI business", "autonomous team", "24/7 agent", "micro-saas launcher", "multi-agent company".
---

# Auto-Company for OpenClaw

Fully autonomous AI company adapted for OpenClaw. Runs continuous cycles of ideation → validation → execution → deployment using multi-agent teams.

## Architecture

```
┌─────────────────────────────────────────┐
│ 5. Human Steering (consensus.md)       │
├─────────────────────────────────────────┤
│ 4. OpenClaw Orchestrator (you)         │
│    - reads consensus.md                 │
│    - spawns agent teams via sessions_spawn│
│    - collects results                   │
├─────────────────────────────────────────┤
│ 3. Agent Team (3-5 agents/cycle)       │
│    - spawned as subagents               │
│    - execute in parallel                │
├─────────────────────────────────────────┤
│ 2. Workflow Engine                      │
│    - Cycle 1: Ideation                  │
│    - Cycle 2: Validation (GO/NO-GO)    │
│    - Cycle 3+: Execution                │
├─────────────────────────────────────────┤
│ 1. Memory & State                       │
│    - consensus.md (cross-cycle state)   │
│    - memory/*.md (daily logs)           │
│    - projects/ (deliverables)           │
└─────────────────────────────────────────┘
```

## Workflow

### Cycle 1: Ideation
**Team:** Research → CEO → Munger
- Research analyst validates demand
- CEO picks top-3 ideas
- Munger does pre-mortem on #1

### Cycle 2: Validation (GO/NO-GO)
**Team:** Research → CFO → Munger → CEO
- Market size check
- Unit economics
- GO/NO-GO decision

### Cycle 3+: Execution
**Team:** varies by task
- Product design → UI → Code → QA → Deploy
- Or: Marketing → Sales → Ops

### Cycle Rules
1. **Ship > Plan > Discuss** — act at 70% information
2. **Discussion-only cycles forbidden** — must produce artifact
3. **Munger veto** — can kill bad ideas, not delay indefinitely
4. **Consensus update** — every cycle ends with updated consensus.md

## Agent Personas

Read from `references/agents/` when spawning:
- `ceo-bezos.md` — strategy, PR/FAQ, flywheel
- `critic-munger.md` — inversion, pre-mortem, checklist
- `cto-vogels.md` — architecture, API-first, design for failure
- `fullstack-dhh.md` — convention over configuration
- `devops-hightower.md` — automation, reliability
- `product-norman.md` — usability, mental models
- `ui-duarte.md` — design system, typography
- `interaction-cooper.md` — user flows, personas
- `qa-bach.md` — exploratory testing
- `marketing-godin.md` — purple cow, permission marketing
- `operations-pg.md` — zero-to-one growth
- `sales-ross.md` — predictable revenue
- `cfo-campbell.md` — value-based pricing
- `research-thompson.md` — aggregation theory

## Spawning Agents

Use `sessions_spawn` with `runtime="subagent"`:

```python
# Example: Spawn CEO for ideation
sessions_spawn(
    task="Read references/agents/ceo-bezos.md, then read memories/consensus.md. "
         "Propose top-3 product ideas based on current market state. "
         "Write results to docs/ideation/YYYY-MM-DD.md",
    runtime="subagent",
    label="ceo-ideation"
)
```

Spawn 3-5 agents per cycle. Wait for all to complete. Merge outputs.

## State Management

**consensus.md** — single source of truth:
```markdown
# Auto-Company Consensus

## Last Updated
2026-08-31 06:00

## Current Phase
Exploring / Building / Launching / Growing

## What We Did This Cycle
- [action]

## Next Action
[what to do next — human can edit this]

## Active Projects
- [project name]: [status]

## Metrics
- Revenue: $0
- Users: 0
- Costs: $0
```

## Safety Guardrails

| Forbidden | Details |
|-----------|---------|
| Delete repos | No `gh repo delete` |
| Delete Cloudflare | No `wrangler delete` |
| System files | No `rm -rf /` |
| Illegal activity | Fraud, theft |
| Leak credentials | Never commit secrets |
| Force push | No `git push --force` to main |

**Allowed:** create repos, deploy, create branches, commit code.

**Workspace:** all projects under `projects/`.

## Monetization Strategies

See `references/business/monetization.md` for revenue models:
- Micro-SaaS (B2B tools)
- Info-products (courses, templates)
- Agency model (AI-as-a-service)
- Content businesses (SEO, newsletters)

## Getting Started

1. Initialize consensus.md
2. Run Cycle 1: `make ideate`
3. Review docs/ideation/
4. Run Cycle 2: `make validate`
5. If GO → Run Cycle 3: `make build`

## Commands

```bash
make ideate     # Cycle 1: generate ideas
make validate   # Cycle 2: GO/NO-GO
make build      # Cycle 3+: execute
make status     # Show current state
make dashboard  # Open web dashboard
```

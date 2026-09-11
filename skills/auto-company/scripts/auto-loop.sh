#!/bin/bash
# Auto-Company Loop for OpenClaw
# Runs continuous cycles of ideation → validation → execution

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${SCRIPT_DIR}/../../.."
CONSENSUS="${WORKSPACE}/memories/consensus.md"
LOGS="${WORKSPACE}/logs"
CYCLE=0
MAX_CYCLES=${MAX_CYCLES:-10}
INTERVAL=${INTERVAL:-300}  # 5 minutes between cycles

mkdir -p "${LOGS}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOGS}/auto-company.log"
}

read_consensus() {
    if [[ -f "${CONSENSUS}" ]]; then
        cat "${CONSENSUS}"
    else
        echo "No consensus file found. Starting fresh."
    fi
}

get_phase() {
    grep -oP '## Current Phase\s*\n\s*\K.*' "${CONSENSUS}" 2>/dev/null || echo "Day 0"
}

get_next_action() {
    grep -A1 '## Next Action' "${CONSENSUS}" 2>/dev/null | tail -1 || echo "Start ideation"
}

run_cycle() {
    CYCLE=$((CYCLE + 1))
    log "=== Cycle ${CYCLE} ==="
    
    PHASE=$(get_phase)
    NEXT_ACTION=$(get_next_action)
    
    log "Phase: ${PHASE}"
    log "Next Action: ${NEXT_ACTION}"
    
    case "${PHASE}" in
        "Day 0"|"Exploring")
            log "Running: Ideation cycle"
            # Spawn CEO + Research + Munger
            ;;
        "Validating")
            log "Running: Validation cycle"
            # Spawn Research + CFO + Munger + CEO
            ;;
        "Building"|"Launching"|"Growing")
            log "Running: Execution cycle"
            # Spawn relevant team based on Next Action
            ;;
        *)
            log "Unknown phase: ${PHASE}"
            ;;
    esac
    
    # TODO: Integrate with OpenClaw sessions_spawn
    # For now, log the intent
    log "Cycle ${CYCLE} complete. Waiting ${INTERVAL}s..."
}

# Main loop
log "Auto-Company started. Max cycles: ${MAX_CYCLES}, Interval: ${INTERVAL}s"

while [[ ${CYCLE} -lt ${MAX_CYCLES} ]]; do
    run_cycle
    sleep "${INTERVAL}"
done

log "Max cycles (${MAX_CYCLES}) reached. Exiting."

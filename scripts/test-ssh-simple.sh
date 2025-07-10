#!/bin/bash

# Simple SSH Connection Test for CCLI
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

function log() { echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"; }
function success() { echo -e "${GREEN}✅ $1${NC}"; }

echo "🔗 Simple SSH Connection Tests"

# Test basic SSH functionality
for host in walnut ironwood; do
    log "Testing SSH to $host..."
    if ssh -o ConnectTimeout=5 $host "echo 'SSH working'; hostname; uptime | cut -d',' -f1"; then
        success "SSH connection to $host working"
    fi
done

# Test SSH with connection sharing
log "Testing SSH connection sharing..."
control_path="/tmp/ssh_test_$$"
ssh_opts="-o ControlMaster=auto -o ControlPath=$control_path -o ControlPersist=10"

# Establish master connection to walnut
ssh $ssh_opts walnut "echo 'Master connection established'" > /dev/null

# Test reuse (should be very fast)
start_time=$(date +%s.%N)
ssh $ssh_opts walnut "echo 'Reused connection'"
end_time=$(date +%s.%N)
duration=$(echo "$end_time - $start_time" | bc -l)

success "SSH connection reuse took ${duration:0:4}s"

# Clean up
ssh $ssh_opts -O exit walnut 2>/dev/null || true
rm -f "$control_path"

success "SSH pooling tests completed successfully"
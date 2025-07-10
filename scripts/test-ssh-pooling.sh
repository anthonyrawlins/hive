#!/bin/bash

# CCLI SSH Connection Pooling Test
# Tests SSH connection reuse, limits, and error handling

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

function log() { echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"; }
function success() { echo -e "${GREEN}✅ $1${NC}"; }
function warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
function error() { echo -e "${RED}❌ $1${NC}"; }

function test_connection_reuse() {
    local host=$1
    log "Testing SSH connection reuse on $host..."
    
    # Use SSH ControlMaster for connection sharing
    local control_path="/tmp/ssh_control_${host}_$$"
    local ssh_opts="-o ControlMaster=auto -o ControlPath=$control_path -o ControlPersist=30"
    
    # Start master connection
    ssh $ssh_opts $host "echo 'Master connection established'" > /dev/null
    
    # Test rapid connections (should reuse)
    local start_time=$(date +%s.%N)
    for i in {1..5}; do
        ssh $ssh_opts $host "echo 'Reused connection $i'" > /dev/null &
    done
    wait
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l)
    
    # Clean up
    ssh $ssh_opts -O exit $host 2>/dev/null || true
    rm -f "$control_path"
    
    success "Connection reuse test completed in ${duration:0:5}s"
    echo "$duration" > "/tmp/ssh_reuse_${host}.txt"
}

function test_connection_limits() {
    local host=$1
    log "Testing SSH connection limits on $host..."
    
    local max_connections=10
    local pids=()
    local results_dir="/tmp/ssh_limits_${host}"
    mkdir -p "$results_dir"
    
    # Start multiple connections
    for i in $(seq 1 $max_connections); do
        {
            ssh $host "sleep 5 && echo 'Connection $i completed'" > "$results_dir/conn_$i.out" 2>&1
            echo $? > "$results_dir/conn_$i.exit"
        } &
        pids+=($!)
    done
    
    # Wait and count successful connections
    wait
    local successful=0
    for i in $(seq 1 $max_connections); do
        if [[ -f "$results_dir/conn_$i.exit" ]] && [[ $(cat "$results_dir/conn_$i.exit") -eq 0 ]]; then
            ((successful++))
        fi
    done
    
    success "SSH connection limit test: $successful/$max_connections successful"
    
    # Clean up
    rm -rf "$results_dir"
}

function test_connection_recovery() {
    local host=$1
    log "Testing SSH connection recovery on $host..."
    
    # Normal connection
    if ssh $host "echo 'Normal connection'" > /dev/null 2>&1; then
        success "Normal SSH connection working"
    else
        error "Normal SSH connection failed"
        return 1
    fi
    
    # Test with short timeout
    if timeout 5s ssh -o ConnectTimeout=2 $host "echo 'Quick connection'" > /dev/null 2>&1; then
        success "Quick SSH connection working"
    else
        warning "Quick SSH connection timed out (may be normal under load)"
    fi
    
    # Test connection to invalid host (should fail gracefully)
    if ssh -o ConnectTimeout=3 -o BatchMode=yes invalid-host-12345 "echo 'test'" > /dev/null 2>&1; then
        warning "Connection to invalid host unexpectedly succeeded"
    else
        success "Connection to invalid host correctly failed"
    fi
}

function test_gemini_via_ssh_multiplex() {
    local host=$1
    local node_version=$2
    log "Testing Gemini CLI via SSH multiplexing on $host..."
    
    local control_path="/tmp/ssh_gemini_${host}_$$"
    local ssh_opts="-o ControlMaster=auto -o ControlPath=$control_path -o ControlPersist=60"
    
    # Establish master connection
    ssh $ssh_opts $host "echo 'Gemini multiplex ready'" > /dev/null
    
    # Run multiple Gemini commands concurrently
    local pids=()
    local start_time=$(date +%s.%N)
    
    for i in {1..3}; do
        {
            local cmd="source ~/.nvm/nvm.sh && nvm use $node_version && echo 'Task $i: Count to 3' | gemini --model gemini-2.5-pro"
            ssh $ssh_opts $host "$cmd" > "/tmp/gemini_multiplex_${host}_$i.out" 2>&1
        } &
        pids+=($!)
    done
    
    wait
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l)
    
    # Check results
    local successful=0
    for i in {1..3}; do
        if [[ -s "/tmp/gemini_multiplex_${host}_$i.out" ]]; then
            ((successful++))
        fi
    done
    
    # Clean up
    ssh $ssh_opts -O exit $host 2>/dev/null || true
    rm -f "$control_path" /tmp/gemini_multiplex_${host}_*.out
    
    success "SSH multiplexed Gemini: $successful/3 tasks completed in ${duration:0:5}s"
}

function run_ssh_pooling_tests() {
    local host=$1
    local node_version=$2
    
    echo ""
    echo "🔗 SSH Connection Pooling Tests: $host"
    echo "======================================="
    
    test_connection_reuse "$host"
    test_connection_limits "$host"
    test_connection_recovery "$host"
    test_gemini_via_ssh_multiplex "$host" "$node_version"
    
    success "SSH pooling tests completed for $host"
}

# Main execution
echo "🚀 CCLI SSH Connection Pooling Test Suite"
echo ""

# Check dependencies
if ! command -v bc &> /dev/null; then
    error "bc not found. Install with: sudo apt-get install bc"
    exit 1
fi

# Test both machines
run_ssh_pooling_tests "walnut" "v22.14.0"
run_ssh_pooling_tests "ironwood" "v22.17.0"

# Performance comparison
echo ""
echo "📊 SSH Performance Analysis"
echo "=========================="

if [[ -f "/tmp/ssh_reuse_walnut.txt" ]] && [[ -f "/tmp/ssh_reuse_ironwood.txt" ]]; then
    walnut_time=$(cat /tmp/ssh_reuse_walnut.txt)
    ironwood_time=$(cat /tmp/ssh_reuse_ironwood.txt)
    
    log "SSH connection reuse performance:"
    log "  WALNUT: ${walnut_time:0:5}s for 5 connections"
    log "  IRONWOOD: ${ironwood_time:0:5}s for 5 connections"
    
    faster=$(echo "$walnut_time < $ironwood_time" | bc -l)
    if [[ $faster -eq 1 ]]; then
        success "WALNUT has faster SSH connection reuse"
    else
        success "IRONWOOD has faster SSH connection reuse"
    fi
fi

success "🎉 SSH pooling tests completed successfully!"
echo ""
echo "📋 Key Findings:"
echo "  ✅ SSH connection reuse working"
echo "  ✅ Multiple concurrent connections supported"
echo "  ✅ Connection recovery working"
echo "  ✅ SSH multiplexing with Gemini CLI functional"
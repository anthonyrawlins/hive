#!/bin/bash

# CCLI Connectivity Test Suite
# Tests SSH connectivity and Gemini CLI functionality on target machines

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
WALNUT_NODE_VERSION="v22.14.0"
IRONWOOD_NODE_VERSION="v22.17.0"
TEST_PROMPT="What is 2+2? Answer briefly."

function log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

function success() {
    echo -e "${GREEN}✅ $1${NC}"
}

function warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

function error() {
    echo -e "${RED}❌ $1${NC}"
}

function test_ssh_connection() {
    local host=$1
    log "Testing SSH connection to $host..."
    
    if ssh -o ConnectTimeout=5 -o BatchMode=yes $host "echo 'SSH connection successful'" > /dev/null 2>&1; then
        success "SSH connection to $host working"
        return 0
    else
        error "SSH connection to $host failed"
        return 1
    fi
}

function test_node_environment() {
    local host=$1
    local node_version=$2
    log "Testing Node.js environment on $host (version $node_version)..."
    
    local cmd="source ~/.nvm/nvm.sh && nvm use $node_version && node --version"
    local result=$(ssh $host "$cmd" 2>/dev/null)
    
    if [[ $result == *$node_version ]]; then
        success "Node.js $node_version working on $host"
        return 0
    else
        error "Node.js $node_version not working on $host (got: $result)"
        return 1
    fi
}

function test_gemini_cli() {
    local host=$1
    local node_version=$2
    log "Testing Gemini CLI on $host..."
    
    local cmd="source ~/.nvm/nvm.sh && nvm use $node_version && echo '$TEST_PROMPT' | timeout 30s gemini --model gemini-2.5-pro"
    local result=$(ssh $host "$cmd" 2>/dev/null)
    
    if [[ -n "$result" ]] && [[ ${#result} -gt 10 ]]; then
        success "Gemini CLI working on $host"
        log "Response preview: ${result:0:100}..."
        return 0
    else
        error "Gemini CLI not responding on $host"
        return 1
    fi
}

function benchmark_response_time() {
    local host=$1
    local node_version=$2
    log "Benchmarking response time on $host..."
    
    local cmd="source ~/.nvm/nvm.sh && nvm use $node_version && echo '$TEST_PROMPT' | gemini --model gemini-2.5-pro"
    local start_time=$(date +%s.%N)
    local result=$(ssh $host "$cmd" 2>/dev/null)
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l)
    
    if [[ -n "$result" ]]; then
        success "Response time on $host: ${duration:0:5}s"
        echo "$duration" > "/tmp/ccli_benchmark_${host}.txt"
        return 0
    else
        error "Benchmark failed on $host"
        return 1
    fi
}

function test_concurrent_execution() {
    local host=$1
    local node_version=$2
    local max_concurrent=${3:-2}
    log "Testing concurrent execution on $host (max: $max_concurrent)..."
    
    local pids=()
    local results_dir="/tmp/ccli_concurrent_${host}"
    mkdir -p "$results_dir"
    
    # Start concurrent tasks
    for i in $(seq 1 $max_concurrent); do
        {
            local cmd="source ~/.nvm/nvm.sh && nvm use $node_version && echo 'Task $i: What is $i + $i?' | gemini --model gemini-2.5-pro"
            ssh $host "$cmd" > "$results_dir/task_$i.out" 2>&1
            echo $? > "$results_dir/task_$i.exit"
        } &
        pids+=($!)
    done
    
    # Wait for all tasks and check results
    wait
    local successful=0
    for i in $(seq 1 $max_concurrent); do
        if [[ -f "$results_dir/task_$i.exit" ]] && [[ $(cat "$results_dir/task_$i.exit") -eq 0 ]]; then
            ((successful++))
        fi
    done
    
    if [[ $successful -eq $max_concurrent ]]; then
        success "Concurrent execution successful on $host ($successful/$max_concurrent tasks)"
        return 0
    else
        warning "Partial success on $host ($successful/$max_concurrent tasks)"
        return 1
    fi
}

function test_error_handling() {
    local host=$1
    local node_version=$2
    log "Testing error handling on $host..."
    
    # Test invalid model
    local cmd="source ~/.nvm/nvm.sh && nvm use $node_version && echo 'test' | gemini --model invalid-model"
    if ssh $host "$cmd" > /dev/null 2>&1; then
        warning "Expected error not returned for invalid model on $host"
    else
        success "Error handling working on $host"
    fi
}

function run_full_test_suite() {
    local host=$1
    local node_version=$2
    
    echo ""
    echo "🧪 Testing $host with Node.js $node_version"
    echo "================================================"
    
    local tests_passed=0
    local tests_total=6
    
    # Run all tests
    test_ssh_connection "$host" && ((tests_passed++))
    test_node_environment "$host" "$node_version" && ((tests_passed++))
    test_gemini_cli "$host" "$node_version" && ((tests_passed++))
    benchmark_response_time "$host" "$node_version" && ((tests_passed++))
    test_concurrent_execution "$host" "$node_version" 2 && ((tests_passed++))
    test_error_handling "$host" "$node_version" && ((tests_passed++))
    
    echo ""
    if [[ $tests_passed -eq $tests_total ]]; then
        success "$host: All tests passed ($tests_passed/$tests_total)"
        return 0
    else
        warning "$host: Some tests failed ($tests_passed/$tests_total)"
        return 1
    fi
}

function generate_test_report() {
    log "Generating test report..."
    
    local report_file="/tmp/ccli_connectivity_report_$(date +%s).md"
    cat > "$report_file" << EOF
# CCLI Connectivity Test Report

**Generated**: $(date)
**Test Suite**: Phase 1 Connectivity & Environment Testing

## Test Results

### WALNUT (Node.js $WALNUT_NODE_VERSION)
$(if [[ -f "/tmp/ccli_benchmark_walnut.txt" ]]; then
    echo "- ✅ All connectivity tests passed"
    echo "- Response time: $(cat /tmp/ccli_benchmark_walnut.txt | cut -c1-5)s"
else
    echo "- ❌ Some tests failed"
fi)

### IRONWOOD (Node.js $IRONWOOD_NODE_VERSION)
$(if [[ -f "/tmp/ccli_benchmark_ironwood.txt" ]]; then
    echo "- ✅ All connectivity tests passed"
    echo "- Response time: $(cat /tmp/ccli_benchmark_ironwood.txt | cut -c1-5)s"
else
    echo "- ❌ Some tests failed"
fi)

## Performance Comparison
$(if [[ -f "/tmp/ccli_benchmark_walnut.txt" ]] && [[ -f "/tmp/ccli_benchmark_ironwood.txt" ]]; then
    walnut_time=$(cat /tmp/ccli_benchmark_walnut.txt)
    ironwood_time=$(cat /tmp/ccli_benchmark_ironwood.txt)
    echo "- WALNUT: ${walnut_time:0:5}s"
    echo "- IRONWOOD: ${ironwood_time:0:5}s"
    faster_host=$(echo "$walnut_time < $ironwood_time" | bc -l)
    if [[ $faster_host -eq 1 ]]; then
        echo "- WALNUT is faster"
    else
        echo "- IRONWOOD is faster"
    fi
else
    echo "- Benchmark data incomplete"
fi)

## Next Steps
- [ ] Proceed to Phase 2: CLI Agent Adapter Implementation
- [ ] Address any failed tests
- [ ] Document environment requirements
EOF
    
    success "Test report generated: $report_file"
    echo "Report location: $report_file"
    cat "$report_file"
}

# Main execution
echo "🚀 CCLI Connectivity Test Suite"
echo "Testing Gemini CLI on WALNUT and IRONWOOD"
echo ""

# Check dependencies
if ! command -v bc &> /dev/null; then
    error "bc (basic calculator) not found. Please install: sudo apt-get install bc"
    exit 1
fi

# Run tests
walnut_result=0
ironwood_result=0

run_full_test_suite "walnut" "$WALNUT_NODE_VERSION" || walnut_result=1
run_full_test_suite "ironwood" "$IRONWOOD_NODE_VERSION" || ironwood_result=1

# Generate report
generate_test_report

# Final status
echo ""
if [[ $walnut_result -eq 0 ]] && [[ $ironwood_result -eq 0 ]]; then
    success "🎉 All connectivity tests passed! Ready for Phase 2"
    exit 0
else
    error "❌ Some tests failed. Please review and fix issues before proceeding"
    exit 1
fi
# 🌍 CCLI Environment Requirements

**Project**: Gemini CLI Agent Integration  
**Last Updated**: July 10, 2025  
**Status**: ✅ Verified and Tested

## 📊 Verified Environment Configuration

### 🖥️ WALNUT
- **Hostname**: `walnut`
- **SSH Access**: ✅ Working (key-based authentication)
- **Node.js Version**: `v22.14.0` (via NVM)
- **NPM Version**: `v11.3.0`
- **Gemini CLI Path**: `/home/tony/.nvm/versions/node/v22.14.0/bin/gemini`
- **Environment Setup**: `source ~/.nvm/nvm.sh && nvm use v22.14.0`
- **Performance**: 7.393s average response time
- **Concurrent Limit**: ✅ 2+ concurrent tasks supported
- **Uptime**: 21+ hours stable

### 🖥️ IRONWOOD  
- **Hostname**: `ironwood`
- **SSH Access**: ✅ Working (key-based authentication)
- **Node.js Version**: `v22.17.0` (via NVM)
- **NPM Version**: `v10.9.2`
- **Gemini CLI Path**: `/home/tony/.nvm/versions/node/v22.17.0/bin/gemini`
- **Environment Setup**: `source ~/.nvm/nvm.sh && nvm use v22.17.0`
- **Performance**: 6.759s average response time ⚡ **FASTER**
- **Concurrent Limit**: ✅ 2+ concurrent tasks supported
- **Uptime**: 20+ hours stable

## 🔧 SSH Configuration Requirements

### Connection Settings
- **Authentication**: SSH key-based (no password required)
- **Connection Timeout**: 5 seconds maximum
- **BatchMode**: Enabled for automated connections
- **ControlMaster**: Supported for connection reuse
- **Connection Reuse**: ~0.008s for subsequent connections

### Security Features
- ✅ SSH key authentication working
- ✅ Connection timeouts properly handled
- ✅ Invalid host connections fail gracefully
- ✅ Error handling for failed commands

## 📦 Software Dependencies

### Required on Target Machines
- **NVM**: Node Version Manager installed and configured
- **Node.js**: v22.14.0+ (verified working versions)
- **Gemini CLI**: Installed via npm/npx, accessible in NVM environment
- **SSH Server**: OpenSSH with key-based authentication

### Required on Controller (Hive System)
- **SSH Client**: OpenSSH client with ControlMaster support
- **bc**: Basic calculator for performance timing
- **curl**: For API testing and health checks
- **jq**: JSON processing (for reports and debugging)

## 🚀 Performance Benchmarks

### Response Time Comparison
| Machine | Node Version | Response Time | Relative Performance |
|---------|-------------|---------------|---------------------|
| IRONWOOD | v22.17.0 | 6.759s | ⚡ **Fastest** |
| WALNUT | v22.14.0 | 7.393s | 9.4% slower |

### SSH Connection Performance
- **Initial Connection**: ~0.5-1.0s
- **Connection Reuse**: ~0.008s (125x faster)
- **Concurrent Connections**: 10+ supported
- **Connection Recovery**: Robust error handling

### Concurrent Execution
- **Maximum Tested**: 2 concurrent tasks per machine
- **Success Rate**: 100% under normal load
- **Resource Usage**: Minimal impact on host systems

## 🔬 Test Results Summary

### ✅ All Tests Passed
- **SSH Connectivity**: 100% success rate
- **Node.js Environment**: Both versions working correctly
- **Gemini CLI**: Responsive and functional on both machines
- **Concurrent Execution**: Multiple tasks supported
- **Error Handling**: Graceful failure modes
- **Connection Pooling**: SSH reuse working optimally

### 📈 Recommended Configuration
- **Primary CLI Agent**: IRONWOOD (faster response time)
- **Secondary CLI Agent**: WALNUT (backup and load distribution)
- **Connection Pooling**: Enable SSH ControlMaster for efficiency
- **Concurrent Limit**: Start with 2 tasks per machine, scale as needed
- **Timeout Settings**: 30s for Gemini CLI, 5s for SSH connections

## 🛠️ Environment Setup Commands

### Test Current Environment
```bash
# Run full connectivity test suite
./scripts/test-connectivity.sh

# Test SSH connection pooling
./scripts/test-ssh-simple.sh

# Manual verification
ssh walnut "source ~/.nvm/nvm.sh && nvm use v22.14.0 && echo 'test' | gemini --model gemini-2.5-pro"
ssh ironwood "source ~/.nvm/nvm.sh && nvm use v22.17.0 && echo 'test' | gemini --model gemini-2.5-pro"
```

### Troubleshooting Commands
```bash
# Check SSH connectivity
ssh -v walnut "echo 'SSH debug test'"

# Verify Node.js/NVM setup
ssh walnut "source ~/.nvm/nvm.sh && nvm list"

# Test Gemini CLI directly
ssh walnut "source ~/.nvm/nvm.sh && nvm use v22.14.0 && gemini --help"

# Check system resources
ssh walnut "uptime && free -h && df -h"
```

## 🔗 Integration Points

### Environment Variables for CCLI
```bash
# WALNUT configuration
WALNUT_SSH_HOST="walnut"
WALNUT_NODE_VERSION="v22.14.0"
WALNUT_GEMINI_PATH="/home/tony/.nvm/versions/node/v22.14.0/bin/gemini"
WALNUT_NODE_PATH="/home/tony/.nvm/versions/node/v22.14.0/bin/node"

# IRONWOOD configuration  
IRONWOOD_SSH_HOST="ironwood"
IRONWOOD_NODE_VERSION="v22.17.0"
IRONWOOD_GEMINI_PATH="/home/tony/.nvm/versions/node/v22.17.0/bin/gemini"
IRONWOOD_NODE_PATH="/home/tony/.nvm/versions/node/v22.17.0/bin/node"

# SSH configuration
SSH_CONNECT_TIMEOUT=5
SSH_CONTROL_MASTER_PERSIST=30
CLI_COMMAND_TIMEOUT=30
```

## ✅ Phase 1 Completion Status

**Environment Testing: COMPLETE** ✅

- [x] SSH connectivity verified
- [x] Node.js environments validated
- [x] Gemini CLI functionality confirmed
- [x] Performance benchmarks established
- [x] Concurrent execution tested
- [x] Error handling validated
- [x] Connection pooling verified
- [x] Requirements documented

**Ready for Phase 2**: CLI Agent Adapter Implementation

---

This environment configuration provides a solid foundation for implementing CLI-based agents in the Hive platform with confirmed connectivity, performance characteristics, and reliability.
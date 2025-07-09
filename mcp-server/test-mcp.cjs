#!/usr/bin/env node

/**
 * Simple MCP Server Test Suite
 * Tests the core functionality of the Hive MCP server
 */

const { spawn } = require('child_process');
const https = require('https');

// Test configuration
const API_BASE = 'https://hive.home.deepblack.cloud/api';
const TEST_TIMEOUT = 30000;

// Colors for output
const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m'
};

function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

// Test cases
const tests = [
  {
    name: 'API Health Check',
    test: () => testApiHealth()
  },
  {
    name: 'Agent List',
    test: () => testAgentList()
  },
  {
    name: 'MCP Server Connectivity',
    test: () => testMcpServer()
  },
  {
    name: 'Socket.IO Endpoint',
    test: () => testSocketIO()
  }
];

async function testApiHealth() {
  return new Promise((resolve, reject) => {
    https.get(`${API_BASE}/health`, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (parsed.status === 'healthy') {
            resolve(`✅ API healthy, ${Object.keys(parsed.components.agents).length} agents`);
          } else {
            reject('API not healthy');
          }
        } catch (e) {
          reject('Invalid JSON response');
        }
      });
    }).on('error', reject);
  });
}

async function testAgentList() {
  return new Promise((resolve, reject) => {
    https.get(`${API_BASE}/agents`, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (parsed.agents && Array.isArray(parsed.agents)) {
            resolve(`✅ ${parsed.total} agents registered`);
          } else {
            reject('Invalid agents response');
          }
        } catch (e) {
          reject('Invalid JSON response');
        }
      });
    }).on('error', reject);
  });
}

async function testMcpServer() {
  return new Promise((resolve, reject) => {
    const mcpProcess = spawn('node', ['dist/index.js'], {
      cwd: '/home/tony/AI/projects/hive/mcp-server',
      stdio: 'pipe'
    });

    let output = '';
    let resolved = false;

    mcpProcess.stdout.on('data', (data) => {
      output += data.toString();
      if (output.includes('Connected to Hive backend successfully') && !resolved) {
        resolved = true;
        mcpProcess.kill();
        resolve('✅ MCP server connects successfully');
      }
    });

    mcpProcess.stderr.on('data', (data) => {
      if (!resolved) {
        resolved = true;
        mcpProcess.kill();
        reject(`MCP server error: ${data.toString()}`);
      }
    });

    setTimeout(() => {
      if (!resolved) {
        resolved = true;
        mcpProcess.kill();
        reject('MCP server timeout');
      }
    }, 10000);
  });
}

async function testSocketIO() {
  return new Promise((resolve, reject) => {
    const url = 'https://hive.home.deepblack.cloud/socket.io/?EIO=4&transport=polling';
    https.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        if (data.includes('sid') && data.includes('upgrades')) {
          resolve('✅ Socket.IO endpoint responding');
        } else {
          reject('Socket.IO endpoint not responding properly');
        }
      });
    }).on('error', reject);
  });
}

// Main test runner
async function runTests() {
  log('\n🐝 Hive MCP Server Test Suite\n', colors.blue);
  
  let passed = 0;
  let failed = 0;
  
  for (const test of tests) {
    try {
      log(`Testing: ${test.name}...`, colors.yellow);
      const result = await test.test();
      log(`  ${result}`, colors.green);
      passed++;
    } catch (error) {
      log(`  ❌ ${error}`, colors.red);
      failed++;
    }
  }
  
  log(`\n📊 Test Results:`, colors.blue);
  log(`  Passed: ${passed}`, colors.green);
  log(`  Failed: ${failed}`, failed > 0 ? colors.red : colors.green);
  log(`  Total: ${passed + failed}`, colors.blue);
  
  if (failed === 0) {
    log('\n🎉 All tests passed! Hive MCP system is operational.', colors.green);
  } else {
    log('\n⚠️  Some tests failed. Check the errors above.', colors.yellow);
  }
  
  process.exit(failed > 0 ? 1 : 0);
}

// Run tests
runTests().catch(console.error);
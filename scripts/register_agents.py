#!/usr/bin/env python3
"""
Agent Registration Script for Hive
Registers cluster agents with the Hive orchestration system
"""

import json
import requests
import yaml
import sys
import time
from pathlib import Path

# Configuration
HIVE_API_URL = "http://localhost:8087"
CONFIG_FILE = "/home/tony/AI/projects/hive/config/hive.yaml"

def load_config():
    """Load the hive.yaml configuration file"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        sys.exit(1)

def test_hive_connection():
    """Test connection to Hive API"""
    try:
        response = requests.get(f"{HIVE_API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Connected to Hive API")
            return True
        else:
            print(f"❌ Hive API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to Hive API: {e}")
        return False

def test_agent_connectivity(endpoint):
    """Test if an agent endpoint is responsive"""
    try:
        response = requests.get(f"{endpoint}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def register_agent(agent_id, agent_config):
    """Register a single agent with Hive"""
    
    # Check if agent is responsive
    if not test_agent_connectivity(agent_config['endpoint']):
        print(f"⚠️  {agent_id.upper()} is not responsive at {agent_config['endpoint']}")
        return False
    
    # Prepare agent registration data
    agent_data = {
        "id": agent_id,
        "endpoint": agent_config['endpoint'],
        "model": agent_config['model'],
        "specialty": agent_config['specialization'],
        "capabilities": agent_config['capabilities'],
        "hardware": agent_config['hardware'],
        "performance_targets": agent_config['performance_targets'],
        "status": "available",
        "current_tasks": 0,
        "max_concurrent": 3  # Default concurrent task limit
    }
    
    try:
        # Register the agent
        response = requests.post(
            f"{HIVE_API_URL}/api/agents",
            json=agent_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Registered {agent_id.upper()} - Agent ID: {result.get('agent_id', 'Unknown')}")
            return True
        else:
            print(f"❌ Failed to register {agent_id.upper()}: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error registering {agent_id.upper()}: {e}")
        return False

def main():
    """Main registration process"""
    print("🐝 Hive Agent Registration Script")
    print("=" * 50)
    
    # Test Hive connection
    if not test_hive_connection():
        print("❌ Cannot connect to Hive API. Make sure Hive is running.")
        sys.exit(1)
    
    # Load configuration
    config = load_config()
    agents = config.get('hive', {}).get('agents', {})
    
    if not agents:
        print("❌ No agents found in configuration")
        sys.exit(1)
    
    print(f"📋 Found {len(agents)} agents to register:")
    for agent_id in agents.keys():
        print(f"  • {agent_id.upper()}")
    
    print("\n🔄 Starting registration process...")
    
    # Register each agent
    successful_registrations = 0
    failed_registrations = 0
    
    for agent_id, agent_config in agents.items():
        print(f"\n📡 Registering {agent_id.upper()}...")
        
        if register_agent(agent_id, agent_config):
            successful_registrations += 1
        else:
            failed_registrations += 1
        
        time.sleep(1)  # Brief pause between registrations
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Registration Summary:")
    print(f"  ✅ Successful: {successful_registrations}")
    print(f"  ❌ Failed: {failed_registrations}")
    print(f"  📈 Total: {successful_registrations + failed_registrations}")
    
    if successful_registrations > 0:
        print(f"\n🎉 Successfully registered {successful_registrations} agents!")
        print("🔗 Check agent status: curl http://localhost:8087/api/agents")
    else:
        print("\n💔 No agents were successfully registered.")
        sys.exit(1)

if __name__ == "__main__":
    main()
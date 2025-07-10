#!/usr/bin/env python3
"""
Test script for Hive backend CLI agent integration
"""

import asyncio
import sys
import os
import logging

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '../../backend')
sys.path.insert(0, backend_path)

from app.core.hive_coordinator import HiveCoordinator, Agent, AgentType
from app.cli_agents.cli_agent_manager import get_cli_agent_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_cli_agent_manager():
    """Test CLI agent manager functionality"""
    print("🧪 Testing CLI Agent Manager...")
    
    try:
        # Initialize CLI agent manager
        cli_manager = get_cli_agent_manager()
        await cli_manager.initialize()
        
        # Check predefined agents
        agent_ids = cli_manager.get_active_agent_ids()
        print(f"✅ Active CLI agents: {agent_ids}")
        
        # Test health checks
        health_results = await cli_manager.health_check_all_agents()
        for agent_id, health in health_results.items():
            status = "✅" if health.get("cli_healthy", False) else "❌"
            print(f"   {agent_id}: {status} {health.get('response_time', 'N/A')}s")
        
        # Test statistics
        stats = cli_manager.get_agent_statistics()
        print(f"✅ CLI agent statistics collected for {len(stats)} agents")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI Agent Manager test failed: {e}")
        return False


async def test_hive_coordinator_integration():
    """Test Hive coordinator with CLI agents"""
    print("\n🤖 Testing Hive Coordinator Integration...")
    
    try:
        # Initialize coordinator
        coordinator = HiveCoordinator()
        await coordinator.initialize()
        
        # Test CLI agent registration
        cli_agent = Agent(
            id="test-cli-agent",
            endpoint="cli://walnut",
            model="gemini-2.5-pro",
            specialty=AgentType.GENERAL_AI,
            max_concurrent=1,
            current_tasks=0,
            agent_type="cli",
            cli_config={
                "host": "walnut",
                "node_version": "v22.14.0",
                "model": "gemini-2.5-pro",
                "specialization": "general_ai",
                "max_concurrent": 1,
                "command_timeout": 30,
                "ssh_timeout": 5,
                "agent_type": "gemini"
            }
        )
        
        coordinator.add_agent(cli_agent)
        print("✅ CLI agent registered with coordinator")
        
        # Test task creation
        task = coordinator.create_task(
            AgentType.GENERAL_AI,
            {
                "objective": "Test CLI agent integration",
                "requirements": ["Respond with a simple acknowledgment"]
            },
            priority=4
        )
        print(f"✅ Task created: {task.id}")
        
        # Test task execution (if we have available agents)
        available_agent = coordinator.get_available_agent(AgentType.GENERAL_AI)
        if available_agent and available_agent.agent_type == "cli":
            print(f"✅ Found available CLI agent: {available_agent.id}")
            
            try:
                result = await coordinator.execute_task(task, available_agent)
                if "error" not in result:
                    print("✅ CLI task execution successful")
                    print(f"   Response: {result.get('response', 'No response')[:100]}...")
                else:
                    print(f"⚠️ CLI task execution returned error: {result['error']}")
            except Exception as e:
                print(f"⚠️ CLI task execution failed: {e}")
        else:
            print("⚠️ No available CLI agents for task execution test")
        
        # Cleanup
        await coordinator.shutdown()
        print("✅ Coordinator shutdown complete")
        
        return True
        
    except Exception as e:
        print(f"❌ Hive Coordinator integration test failed: {e}")
        return False


async def test_mixed_agent_types():
    """Test mixed agent type handling"""
    print("\n⚡ Testing Mixed Agent Types...")
    
    try:
        coordinator = HiveCoordinator()
        await coordinator.initialize()
        
        # Add both Ollama and CLI agents (simulated)
        ollama_agent = Agent(
            id="test-ollama-agent",
            endpoint="http://localhost:11434",
            model="codellama:latest",
            specialty=AgentType.DOCS_WRITER,
            max_concurrent=2,
            current_tasks=0,
            agent_type="ollama"
        )
        
        cli_agent = Agent(
            id="test-cli-agent-2",
            endpoint="cli://ironwood",
            model="gemini-2.5-pro",
            specialty=AgentType.REASONING,
            max_concurrent=1,
            current_tasks=0,
            agent_type="cli",
            cli_config={
                "host": "ironwood",
                "node_version": "v22.17.0",
                "model": "gemini-2.5-pro",
                "specialization": "reasoning"
            }
        )
        
        coordinator.add_agent(ollama_agent)
        coordinator.add_agent(cli_agent)
        print("✅ Mixed agent types registered")
        
        # Test agent selection for different task types
        docs_agent = coordinator.get_available_agent(AgentType.DOCS_WRITER)
        reasoning_agent = coordinator.get_available_agent(AgentType.REASONING)
        
        if docs_agent:
            print(f"✅ Found {docs_agent.agent_type} agent for docs: {docs_agent.id}")
        if reasoning_agent:
            print(f"✅ Found {reasoning_agent.agent_type} agent for reasoning: {reasoning_agent.id}")
        
        await coordinator.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Mixed agent types test failed: {e}")
        return False


async def main():
    """Run all backend integration tests"""
    print("🚀 CCLI Backend Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("CLI Agent Manager", test_cli_agent_manager),
        ("Hive Coordinator Integration", test_hive_coordinator_integration),
        ("Mixed Agent Types", test_mixed_agent_types)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 Backend Integration Test Results:")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n📊 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All backend integration tests passed! Ready for API testing.")
        return 0
    else:
        print("⚠️  Some tests failed. Review integration issues.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
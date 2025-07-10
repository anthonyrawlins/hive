#!/usr/bin/env python3
"""
CCLI Implementation Test Runner
Tests the CLI agent implementation with real SSH connections.
"""

import asyncio
import sys
import os
import logging
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from agents.gemini_cli_agent import GeminiCliAgent, GeminiCliConfig, TaskRequest
from agents.cli_agent_factory import CliAgentFactory, get_default_factory
from executors.ssh_executor import SSHExecutor, SSHConfig


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_ssh_executor():
    """Test SSH executor functionality"""
    print("🔗 Testing SSH Executor...")
    
    executor = SSHExecutor()
    config = SSHConfig(host="walnut", command_timeout=10)
    
    try:
        # Test basic command
        result = await executor.execute(config, "echo 'Hello from SSH'")
        assert result.returncode == 0
        assert "Hello from SSH" in result.stdout
        print(f"✅ Basic SSH command: {result.stdout.strip()}")
        
        # Test connection stats
        stats = await executor.get_connection_stats()
        print(f"✅ Connection stats: {stats['total_connections']} connections")
        
        # Cleanup
        await executor.cleanup()
        
    except Exception as e:
        print(f"❌ SSH executor test failed: {e}")
        return False
    
    return True


async def test_gemini_cli_agent():
    """Test GeminiCliAgent functionality"""
    print("\n🤖 Testing GeminiCliAgent...")
    
    config = GeminiCliConfig(
        host="walnut",
        node_version="v22.14.0",
        model="gemini-2.5-pro",
        command_timeout=30
    )
    
    agent = GeminiCliAgent(config, "test")
    
    try:
        # Test health check
        health = await agent.health_check()
        print(f"✅ Health check: SSH={health['ssh_healthy']}, CLI={health['cli_healthy']}")
        
        if not health['cli_healthy']:
            print("❌ Gemini CLI not healthy, skipping execution test")
            return False
        
        # Test simple task execution
        task = TaskRequest(
            prompt="What is 2+2? Answer with just the number.",
            task_id="test-math"
        )
        
        start_time = time.time()
        result = await agent.execute_task(task)
        execution_time = time.time() - start_time
        
        print(f"✅ Task execution:")
        print(f"   Status: {result.status.value}")
        print(f"   Response: {result.response[:100]}...")
        print(f"   Execution time: {execution_time:.2f}s")
        print(f"   Agent time: {result.execution_time:.2f}s")
        
        # Test statistics
        stats = agent.get_statistics()
        print(f"✅ Agent stats: {stats['stats']['total_tasks']} tasks total")
        
        # Cleanup
        await agent.cleanup()
        
    except Exception as e:
        print(f"❌ GeminiCliAgent test failed: {e}")
        return False
    
    return True


async def test_cli_agent_factory():
    """Test CLI agent factory"""
    print("\n🏭 Testing CliAgentFactory...")
    
    factory = CliAgentFactory()
    
    try:
        # List predefined agents
        predefined = factory.get_predefined_agent_ids()
        print(f"✅ Predefined agents: {predefined}")
        
        # Get agent info
        info = factory.get_agent_info("walnut-gemini")
        print(f"✅ Agent info: {info['description']}")
        
        # Create an agent
        agent = factory.create_agent("walnut-gemini")
        print(f"✅ Created agent: {agent.agent_id}")
        
        # Test the created agent
        health = await agent.health_check()
        print(f"✅ Factory agent health: SSH={health['ssh_healthy']}")
        
        # Cleanup
        await factory.cleanup_all()
        
    except Exception as e:
        print(f"❌ CliAgentFactory test failed: {e}")
        return False
    
    return True


async def test_concurrent_execution():
    """Test concurrent task execution"""
    print("\n⚡ Testing Concurrent Execution...")
    
    factory = get_default_factory()
    
    try:
        # Create agent
        agent = factory.create_agent("ironwood-gemini")  # Use faster machine
        
        # Create multiple tasks
        tasks = [
            TaskRequest(prompt=f"Count from 1 to {i}. Just list the numbers.", task_id=f"count-{i}")
            for i in range(1, 4)
        ]
        
        # Execute concurrently
        start_time = time.time()
        results = await asyncio.gather(*[
            agent.execute_task(task) for task in tasks
        ], return_exceptions=True)
        total_time = time.time() - start_time
        
        # Analyze results
        successful = sum(1 for r in results if hasattr(r, 'status') and r.status.value == 'completed')
        print(f"✅ Concurrent execution: {successful}/{len(tasks)} successful in {total_time:.2f}s")
        
        for i, result in enumerate(results):
            if hasattr(result, 'status'):
                print(f"   Task {i+1}: {result.status.value} ({result.execution_time:.2f}s)")
            else:
                print(f"   Task {i+1}: Exception - {result}")
        
        # Cleanup
        await factory.cleanup_all()
        
    except Exception as e:
        print(f"❌ Concurrent execution test failed: {e}")
        return False
    
    return True


async def run_performance_test():
    """Run performance comparison test"""
    print("\n📊 Performance Comparison Test...")
    
    factory = get_default_factory()
    
    try:
        # Test both machines
        results = {}
        
        for agent_id in ["walnut-gemini", "ironwood-gemini"]:
            print(f"Testing {agent_id}...")
            
            agent = factory.create_agent(agent_id)
            
            # Simple prompt for consistency
            task = TaskRequest(
                prompt="What is the capital of France? Answer in one word.",
                task_id=f"perf-{agent_id}"
            )
            
            start_time = time.time()
            result = await agent.execute_task(task)
            total_time = time.time() - start_time
            
            results[agent_id] = {
                "success": result.status.value == "completed",
                "response_time": total_time,
                "agent_time": result.execution_time,
                "response": result.response[:50] if result.response else None
            }
            
            print(f"   {agent_id}: {total_time:.2f}s ({'✅' if result.status.value == 'completed' else '❌'})")
        
        # Compare results
        if results["walnut-gemini"]["success"] and results["ironwood-gemini"]["success"]:
            walnut_time = results["walnut-gemini"]["response_time"]
            ironwood_time = results["ironwood-gemini"]["response_time"]
            
            if walnut_time < ironwood_time:
                faster = "WALNUT"
                diff = ((ironwood_time - walnut_time) / walnut_time) * 100
            else:
                faster = "IRONWOOD"
                diff = ((walnut_time - ironwood_time) / ironwood_time) * 100
            
            print(f"✅ Performance winner: {faster} (by {diff:.1f}%)")
        
        # Cleanup
        await factory.cleanup_all()
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False
    
    return True


async def main():
    """Run all implementation tests"""
    print("🚀 CCLI Implementation Test Suite")
    print("=" * 50)
    
    tests = [
        ("SSH Executor", test_ssh_executor),
        ("GeminiCliAgent", test_gemini_cli_agent),
        ("CliAgentFactory", test_cli_agent_factory),
        ("Concurrent Execution", test_concurrent_execution),
        ("Performance Comparison", run_performance_test)
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
    print("🎯 Test Results Summary:")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n📊 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Implementation ready for Phase 3.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review and fix issues.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
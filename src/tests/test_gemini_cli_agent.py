"""
Unit tests for GeminiCliAgent
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from dataclasses import dataclass

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.gemini_cli_agent import (
    GeminiCliAgent, GeminiCliConfig, TaskRequest, TaskResult, TaskStatus
)
from executors.ssh_executor import SSHResult


class TestGeminiCliAgent:
    
    @pytest.fixture
    def agent_config(self):
        return GeminiCliConfig(
            host="test-host",
            node_version="v22.14.0",
            model="gemini-2.5-pro",
            max_concurrent=2,
            command_timeout=30
        )
    
    @pytest.fixture
    def agent(self, agent_config):
        return GeminiCliAgent(agent_config, "test_specialty")
    
    @pytest.fixture
    def task_request(self):
        return TaskRequest(
            prompt="What is 2+2?",
            task_id="test-task-123"
        )
    
    def test_agent_initialization(self, agent_config):
        """Test agent initialization with proper configuration"""
        agent = GeminiCliAgent(agent_config, "general_ai")
        
        assert agent.config.host == "test-host"
        assert agent.config.node_version == "v22.14.0"
        assert agent.specialization == "general_ai"
        assert agent.agent_id == "test-host-gemini"
        assert len(agent.active_tasks) == 0
        assert agent.stats["total_tasks"] == 0
    
    def test_config_auto_paths(self):
        """Test automatic path generation in config"""
        config = GeminiCliConfig(
            host="walnut",
            node_version="v22.14.0"
        )
        
        expected_node_path = "/home/tony/.nvm/versions/node/v22.14.0/bin/node"
        expected_gemini_path = "/home/tony/.nvm/versions/node/v22.14.0/bin/gemini"
        
        assert config.node_path == expected_node_path
        assert config.gemini_path == expected_gemini_path
    
    def test_build_cli_command(self, agent):
        """Test CLI command building"""
        prompt = "What is Python?"
        model = "gemini-2.5-pro"
        
        command = agent._build_cli_command(prompt, model)
        
        assert "source ~/.nvm/nvm.sh" in command
        assert "nvm use v22.14.0" in command
        assert "gemini --model gemini-2.5-pro" in command
        assert "What is Python?" in command
    
    def test_build_cli_command_escaping(self, agent):
        """Test CLI command with special characters"""
        prompt = "What's the meaning of 'life'?"
        model = "gemini-2.5-pro"
        
        command = agent._build_cli_command(prompt, model)
        
        # Should properly escape single quotes
        assert "What\\'s the meaning of \\'life\\'?" in command
    
    def test_clean_response(self, agent):
        """Test response cleaning"""
        raw_output = """Now using node v22.14.0 (npm v11.3.0)
MCP STDERR (hive): Warning message

This is the actual response
from Gemini CLI

"""
        
        cleaned = agent._clean_response(raw_output)
        expected = "This is the actual response\nfrom Gemini CLI"
        
        assert cleaned == expected
    
    @pytest.mark.asyncio
    async def test_execute_task_success(self, agent, task_request, mocker):
        """Test successful task execution"""
        # Mock SSH executor
        mock_ssh_result = SSHResult(
            stdout="Now using node v22.14.0\n4\n",
            stderr="",
            returncode=0,
            duration=1.5,
            host="test-host",
            command="test-command"
        )
        
        mock_execute = AsyncMock(return_value=mock_ssh_result)
        mocker.patch.object(agent.ssh_executor, 'execute', mock_execute)
        
        result = await agent.execute_task(task_request)
        
        assert result.status == TaskStatus.COMPLETED
        assert result.task_id == "test-task-123"
        assert result.response == "4"
        assert result.execution_time > 0
        assert result.model == "gemini-2.5-pro"
        assert result.agent_id == "test-host-gemini"
        
        # Check statistics update
        assert agent.stats["successful_tasks"] == 1
        assert agent.stats["total_tasks"] == 1
    
    @pytest.mark.asyncio
    async def test_execute_task_failure(self, agent, task_request, mocker):
        """Test task execution failure handling"""
        mock_ssh_result = SSHResult(
            stdout="",
            stderr="Command failed: invalid model",
            returncode=1,
            duration=0.5,
            host="test-host",
            command="test-command"
        )
        
        mock_execute = AsyncMock(return_value=mock_ssh_result)
        mocker.patch.object(agent.ssh_executor, 'execute', mock_execute)
        
        result = await agent.execute_task(task_request)
        
        assert result.status == TaskStatus.FAILED
        assert "CLI execution failed" in result.error
        assert result.execution_time > 0
        
        # Check statistics update
        assert agent.stats["failed_tasks"] == 1
        assert agent.stats["total_tasks"] == 1
    
    @pytest.mark.asyncio
    async def test_execute_task_exception(self, agent, task_request, mocker):
        """Test task execution with exception"""
        mock_execute = AsyncMock(side_effect=Exception("SSH connection failed"))
        mocker.patch.object(agent.ssh_executor, 'execute', mock_execute)
        
        result = await agent.execute_task(task_request)
        
        assert result.status == TaskStatus.FAILED
        assert "SSH connection failed" in result.error
        assert result.execution_time > 0
        
        # Check statistics update
        assert agent.stats["failed_tasks"] == 1
        assert agent.stats["total_tasks"] == 1
    
    @pytest.mark.asyncio
    async def test_concurrent_task_limit(self, agent, mocker):
        """Test concurrent task execution limits"""
        # Mock a slow SSH execution
        slow_ssh_result = SSHResult(
            stdout="result",
            stderr="",
            returncode=0,
            duration=2.0,
            host="test-host",
            command="test-command"
        )
        
        async def slow_execute(*args, **kwargs):
            await asyncio.sleep(0.1)  # Simulate slow execution
            return slow_ssh_result
        
        mock_execute = AsyncMock(side_effect=slow_execute)
        mocker.patch.object(agent.ssh_executor, 'execute', mock_execute)
        
        # Start maximum concurrent tasks
        task1 = TaskRequest(prompt="Task 1", task_id="task-1")
        task2 = TaskRequest(prompt="Task 2", task_id="task-2")
        task3 = TaskRequest(prompt="Task 3", task_id="task-3")
        
        # Start first two tasks (should succeed)
        result1_coro = agent.execute_task(task1)
        result2_coro = agent.execute_task(task2)
        
        # Give tasks time to start
        await asyncio.sleep(0.01)
        
        # Third task should fail due to limit
        result3 = await agent.execute_task(task3)
        assert result3.status == TaskStatus.FAILED
        assert "maximum concurrent tasks" in result3.error
        
        # Wait for first two to complete
        result1 = await result1_coro
        result2 = await result2_coro
        
        assert result1.status == TaskStatus.COMPLETED
        assert result2.status == TaskStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, agent, mocker):
        """Test successful health check"""
        # Mock SSH connection test
        mock_test_connection = AsyncMock(return_value=True)
        mocker.patch.object(agent.ssh_executor, 'test_connection', mock_test_connection)
        
        # Mock successful CLI execution
        mock_ssh_result = SSHResult(
            stdout="health check ok\n",
            stderr="",
            returncode=0,
            duration=1.0,
            host="test-host",
            command="test-command"
        )
        mock_execute = AsyncMock(return_value=mock_ssh_result)
        mocker.patch.object(agent.ssh_executor, 'execute', mock_execute)
        
        # Mock connection stats
        mock_get_stats = AsyncMock(return_value={"total_connections": 1})
        mocker.patch.object(agent.ssh_executor, 'get_connection_stats', mock_get_stats)
        
        health = await agent.health_check()
        
        assert health["agent_id"] == "test-host-gemini"
        assert health["ssh_healthy"] is True
        assert health["cli_healthy"] is True
        assert health["response_time"] > 0
        assert health["active_tasks"] == 0
        assert health["max_concurrent"] == 2
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, agent, mocker):
        """Test health check with failures"""
        # Mock SSH connection failure
        mock_test_connection = AsyncMock(return_value=False)
        mocker.patch.object(agent.ssh_executor, 'test_connection', mock_test_connection)
        
        health = await agent.health_check()
        
        assert health["ssh_healthy"] is False
        assert health["cli_healthy"] is False
    
    @pytest.mark.asyncio
    async def test_task_status_tracking(self, agent, mocker):
        """Test task status tracking"""
        # Mock SSH execution
        mock_ssh_result = SSHResult(
            stdout="result\n",
            stderr="",
            returncode=0,
            duration=1.0,
            host="test-host",
            command="test-command"
        )
        mock_execute = AsyncMock(return_value=mock_ssh_result)
        mocker.patch.object(agent.ssh_executor, 'execute', mock_execute)
        
        task_request = TaskRequest(prompt="Test", task_id="status-test")
        
        # Execute task
        result = await agent.execute_task(task_request)
        
        # Check task in history
        status = await agent.get_task_status("status-test")
        assert status is not None
        assert status.status == TaskStatus.COMPLETED
        assert status.task_id == "status-test"
        
        # Check non-existent task
        status = await agent.get_task_status("non-existent")
        assert status is None
    
    def test_statistics(self, agent):
        """Test statistics tracking"""
        stats = agent.get_statistics()
        
        assert stats["agent_id"] == "test-host-gemini"
        assert stats["host"] == "test-host"
        assert stats["specialization"] == "test_specialty"
        assert stats["model"] == "gemini-2.5-pro"
        assert stats["stats"]["total_tasks"] == 0
        assert stats["active_tasks"] == 0
    
    @pytest.mark.asyncio
    async def test_task_cancellation(self, agent, mocker):
        """Test task cancellation"""
        # Mock a long-running SSH execution
        async def long_execute(*args, **kwargs):
            await asyncio.sleep(10)  # Long execution
            return SSHResult("", "", 0, 10.0, "test-host", "cmd")
        
        mock_execute = AsyncMock(side_effect=long_execute)
        mocker.patch.object(agent.ssh_executor, 'execute', mock_execute)
        
        task_request = TaskRequest(prompt="Long task", task_id="cancel-test")
        
        # Start task
        task_coro = agent.execute_task(task_request)
        
        # Let it start
        await asyncio.sleep(0.01)
        
        # Cancel it
        cancelled = await agent.cancel_task("cancel-test")
        assert cancelled is True
        
        # The task should be cancelled
        try:
            await task_coro
        except asyncio.CancelledError:
            pass  # Expected
    
    @pytest.mark.asyncio
    async def test_cleanup(self, agent, mocker):
        """Test agent cleanup"""
        # Mock SSH executor cleanup
        mock_cleanup = AsyncMock()
        mocker.patch.object(agent.ssh_executor, 'cleanup', mock_cleanup)
        
        await agent.cleanup()
        
        mock_cleanup.assert_called_once()


class TestTaskRequest:
    
    def test_task_request_auto_id(self):
        """Test automatic task ID generation"""
        request = TaskRequest(prompt="Test prompt")
        
        assert request.task_id is not None
        assert len(request.task_id) == 12  # MD5 hash truncated to 12 chars
    
    def test_task_request_custom_id(self):
        """Test custom task ID"""
        request = TaskRequest(prompt="Test", task_id="custom-123")
        
        assert request.task_id == "custom-123"


class TestTaskResult:
    
    def test_task_result_to_dict(self):
        """Test TaskResult serialization"""
        result = TaskResult(
            task_id="test-123",
            status=TaskStatus.COMPLETED,
            response="Test response",
            execution_time=1.5,
            model="gemini-2.5-pro",
            agent_id="test-agent"
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["task_id"] == "test-123"
        assert result_dict["status"] == "completed"
        assert result_dict["response"] == "Test response"
        assert result_dict["execution_time"] == 1.5
        assert result_dict["model"] == "gemini-2.5-pro"
        assert result_dict["agent_id"] == "test-agent"
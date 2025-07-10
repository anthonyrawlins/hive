"""
SSH Executor for CCLI
Handles SSH connections, command execution, and connection pooling for CLI agents.
"""

import asyncio
import asyncssh
import time
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager


@dataclass
class SSHResult:
    """Result of an SSH command execution"""
    stdout: str
    stderr: str
    returncode: int
    duration: float
    host: str
    command: str


@dataclass 
class SSHConfig:
    """SSH connection configuration"""
    host: str
    username: str = "tony"
    connect_timeout: int = 5
    command_timeout: int = 30
    max_retries: int = 2
    known_hosts: Optional[str] = None


class SSHConnectionPool:
    """Manages SSH connection pooling for efficiency"""
    
    def __init__(self, pool_size: int = 3, persist_timeout: int = 60):
        self.pool_size = pool_size
        self.persist_timeout = persist_timeout
        self.connections: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)
    
    async def get_connection(self, config: SSHConfig) -> asyncssh.SSHClientConnection:
        """Get a pooled SSH connection, creating if needed"""
        host_key = f"{config.username}@{config.host}"
        
        # Check if we have a valid connection
        if host_key in self.connections:
            conn_info = self.connections[host_key]
            connection = conn_info['connection']
            
            # Check if connection is still alive and not expired
            if (not connection.is_closed() and 
                time.time() - conn_info['created'] < self.persist_timeout):
                self.logger.debug(f"Reusing connection to {host_key}")
                return connection
            else:
                # Connection expired or closed, remove it
                self.logger.debug(f"Connection to {host_key} expired, creating new one")
                await self._close_connection(host_key)
        
        # Create new connection
        self.logger.debug(f"Creating new SSH connection to {host_key}")
        connection = await asyncssh.connect(
            config.host,
            username=config.username,
            connect_timeout=config.connect_timeout,
            known_hosts=config.known_hosts
        )
        
        self.connections[host_key] = {
            'connection': connection,
            'created': time.time(),
            'uses': 0
        }
        
        return connection
    
    async def _close_connection(self, host_key: str):
        """Close and remove a connection from the pool"""
        if host_key in self.connections:
            try:
                conn_info = self.connections[host_key]
                if not conn_info['connection'].is_closed():
                    conn_info['connection'].close()
                    await conn_info['connection'].wait_closed()
            except Exception as e:
                self.logger.warning(f"Error closing connection to {host_key}: {e}")
            finally:
                del self.connections[host_key]
    
    async def close_all(self):
        """Close all pooled connections"""
        for host_key in list(self.connections.keys()):
            await self._close_connection(host_key)


class SSHExecutor:
    """Main SSH command executor with connection pooling and error handling"""
    
    def __init__(self, pool_size: int = 3, persist_timeout: int = 60):
        self.pool = SSHConnectionPool(pool_size, persist_timeout)
        self.logger = logging.getLogger(__name__)
    
    async def execute(self, config: SSHConfig, command: str, **kwargs) -> SSHResult:
        """Execute a command via SSH with retries and error handling"""
        
        for attempt in range(config.max_retries + 1):
            try:
                return await self._execute_once(config, command, **kwargs)
            
            except (asyncssh.Error, asyncio.TimeoutError, OSError) as e:
                self.logger.warning(f"SSH execution attempt {attempt + 1} failed for {config.host}: {e}")
                
                if attempt < config.max_retries:
                    # Close any bad connections and retry
                    host_key = f"{config.username}@{config.host}"
                    await self.pool._close_connection(host_key)
                    await asyncio.sleep(1)  # Brief delay before retry
                else:
                    # Final attempt failed
                    raise Exception(f"SSH execution failed after {config.max_retries + 1} attempts: {e}")
    
    async def _execute_once(self, config: SSHConfig, command: str, **kwargs) -> SSHResult:
        """Execute command once via SSH"""
        start_time = time.time()
        
        try:
            connection = await self.pool.get_connection(config)
            
            # Execute command with timeout
            result = await asyncio.wait_for(
                connection.run(command, check=False, **kwargs),
                timeout=config.command_timeout
            )
            
            duration = time.time() - start_time
            
            # Update connection usage stats
            host_key = f"{config.username}@{config.host}"
            if host_key in self.pool.connections:
                self.pool.connections[host_key]['uses'] += 1
            
            return SSHResult(
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.exit_status,
                duration=duration,
                host=config.host,
                command=command
            )
            
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            raise Exception(f"SSH command timeout after {config.command_timeout}s on {config.host}")
        
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"SSH execution error on {config.host}: {e}")
            raise
    
    async def test_connection(self, config: SSHConfig) -> bool:
        """Test if SSH connection is working"""
        try:
            result = await self.execute(config, "echo 'connection_test'")
            return result.returncode == 0 and "connection_test" in result.stdout
        except Exception as e:
            self.logger.error(f"Connection test failed for {config.host}: {e}")
            return False
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about current connections"""
        stats = {
            "total_connections": len(self.pool.connections),
            "connections": {}
        }
        
        for host_key, conn_info in self.pool.connections.items():
            stats["connections"][host_key] = {
                "created": conn_info["created"],
                "age_seconds": time.time() - conn_info["created"],
                "uses": conn_info["uses"],
                "is_closed": conn_info["connection"].is_closed()
            }
        
        return stats
    
    async def cleanup(self):
        """Close all connections and cleanup resources"""
        await self.pool.close_all()
    
    @asynccontextmanager
    async def connection_context(self, config: SSHConfig):
        """Context manager for SSH connections"""
        try:
            connection = await self.pool.get_connection(config)
            yield connection
        except Exception as e:
            self.logger.error(f"SSH connection context error: {e}")
            raise
        # Connection stays in pool for reuse


# Module-level convenience functions
_default_executor = None

def get_default_executor() -> SSHExecutor:
    """Get the default SSH executor instance"""
    global _default_executor
    if _default_executor is None:
        _default_executor = SSHExecutor()
    return _default_executor

async def execute_ssh_command(host: str, command: str, **kwargs) -> SSHResult:
    """Convenience function for simple SSH command execution"""
    config = SSHConfig(host=host)
    executor = get_default_executor()
    return await executor.execute(config, command, **kwargs)
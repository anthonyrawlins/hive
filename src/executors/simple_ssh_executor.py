"""
Simple SSH Executor for CCLI
Uses subprocess for SSH execution without external dependencies.
"""

import asyncio
import subprocess
import time
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any


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
    ssh_options: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.ssh_options is None:
            self.ssh_options = {
                "BatchMode": "yes",
                "ConnectTimeout": str(self.connect_timeout),
                "StrictHostKeyChecking": "no"
            }


class SimpleSSHExecutor:
    """Simple SSH command executor using subprocess"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def execute(self, config: SSHConfig, command: str, **kwargs) -> SSHResult:
        """Execute a command via SSH with retries and error handling"""
        
        for attempt in range(config.max_retries + 1):
            try:
                return await self._execute_once(config, command, **kwargs)
            
            except Exception as e:
                self.logger.warning(f"SSH execution attempt {attempt + 1} failed for {config.host}: {e}")
                
                if attempt < config.max_retries:
                    await asyncio.sleep(1)  # Brief delay before retry
                else:
                    # Final attempt failed
                    raise Exception(f"SSH execution failed after {config.max_retries + 1} attempts: {e}")
    
    async def _execute_once(self, config: SSHConfig, command: str, **kwargs) -> SSHResult:
        """Execute command once via SSH"""
        start_time = time.time()
        
        # Build SSH command
        ssh_cmd = self._build_ssh_command(config, command)
        
        try:
            # Execute command with timeout
            process = await asyncio.create_subprocess_exec(
                *ssh_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                **kwargs
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=config.command_timeout
            )
            
            duration = time.time() - start_time
            
            return SSHResult(
                stdout=stdout.decode('utf-8'),
                stderr=stderr.decode('utf-8'),
                returncode=process.returncode,
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
    
    def _build_ssh_command(self, config: SSHConfig, command: str) -> list:
        """Build SSH command array"""
        ssh_cmd = ["ssh"]
        
        # Add SSH options
        for option, value in config.ssh_options.items():
            ssh_cmd.extend(["-o", f"{option}={value}"])
        
        # Add destination
        if config.username:
            destination = f"{config.username}@{config.host}"
        else:
            destination = config.host
        
        ssh_cmd.append(destination)
        ssh_cmd.append(command)
        
        return ssh_cmd
    
    async def test_connection(self, config: SSHConfig) -> bool:
        """Test if SSH connection is working"""
        try:
            result = await self.execute(config, "echo 'connection_test'")
            return result.returncode == 0 and "connection_test" in result.stdout
        except Exception as e:
            self.logger.error(f"Connection test failed for {config.host}: {e}")
            return False
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about current connections (simplified for subprocess)"""
        return {
            "total_connections": 0,  # subprocess doesn't maintain persistent connections
            "connection_type": "subprocess"
        }
    
    async def cleanup(self):
        """Cleanup resources (no-op for subprocess)"""
        pass


# Alias for compatibility
SSHExecutor = SimpleSSHExecutor
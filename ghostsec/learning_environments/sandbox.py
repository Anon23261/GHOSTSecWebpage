import os
import subprocess
import docker
from pathlib import Path
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class SecuritySandbox:
    """
    Isolated environment for security testing and learning
    Uses Docker containers for isolation
    """
    
    def __init__(self, workspace_name: str):
        self.workspace_name = workspace_name
        self.client = docker.from_env()
        self.container = None
        self.workspace_path = Path(f"workspaces/{workspace_name}")
        
    def create_workspace(self) -> bool:
        """Create isolated workspace directory"""
        try:
            self.workspace_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to create workspace: {e}")
            return False
            
    def start_container(self, image: str = "ubuntu:latest") -> bool:
        """Start isolated container for testing"""
        try:
            self.container = self.client.containers.run(
                image,
                detach=True,
                tty=True,
                volumes={
                    str(self.workspace_path.absolute()): {
                        'bind': '/workspace',
                        'mode': 'rw'
                    }
                },
                network_mode="none"  # Isolated network
            )
            return True
        except Exception as e:
            logger.error(f"Failed to start container: {e}")
            return False
            
    def execute_command(self, command: str) -> Optional[str]:
        """Execute command in sandbox"""
        if not self.container:
            return None
            
        try:
            result = self.container.exec_run(command)
            return result.output.decode()
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return None
            
    def upload_file(self, local_path: str, sandbox_path: str) -> bool:
        """Upload file to sandbox"""
        try:
            with open(local_path, 'rb') as f:
                data = f.read()
            self.container.put_archive('/workspace', data)
            return True
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            return False
            
    def cleanup(self):
        """Clean up sandbox environment"""
        try:
            if self.container:
                self.container.stop()
                self.container.remove()
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


class MalwareAnalysisSandbox(SecuritySandbox):
    """
    Specialized sandbox for malware analysis
    Additional security measures and monitoring
    """
    
    def __init__(self, workspace_name: str):
        super().__init__(workspace_name)
        self.monitoring_enabled = False
        
    def start_container(self, image: str = "remnux/remnux-distro:focal") -> bool:
        """Start specialized malware analysis container"""
        return super().start_container(image)
        
    def enable_monitoring(self) -> bool:
        """Enable system call monitoring"""
        try:
            self.execute_command("strace -f -p 1")
            self.monitoring_enabled = True
            return True
        except Exception as e:
            logger.error(f"Failed to enable monitoring: {e}")
            return False
            
    def analyze_file(self, file_path: str) -> Dict:
        """Analyze potentially malicious file"""
        results = {
            'strings': None,
            'file_type': None,
            'network_attempts': [],
            'suspicious_calls': []
        }
        
        try:
            # Basic static analysis
            results['strings'] = self.execute_command(f"strings {file_path}")
            results['file_type'] = self.execute_command(f"file {file_path}")
            
            # Monitor execution
            if self.monitoring_enabled:
                execution_log = self.execute_command(f"strace ./{file_path}")
                results['suspicious_calls'] = self._analyze_syscalls(execution_log)
                
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            
        return results
        
    def _analyze_syscalls(self, log: str) -> List[str]:
        """Analyze system calls for suspicious behavior"""
        suspicious = []
        suspicious_patterns = [
            'socket(', 'connect(', 'exec',
            'fork(', 'clone(', 'ptrace('
        ]
        
        for line in log.split('\n'):
            for pattern in suspicious_patterns:
                if pattern in line:
                    suspicious.append(line.strip())
                    
        return suspicious

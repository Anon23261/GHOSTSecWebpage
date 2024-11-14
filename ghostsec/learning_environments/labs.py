from typing import List, Dict
import docker
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Lab:
    """Base class for cybersecurity labs"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.completed = False
        self.progress = 0
        
    def start(self) -> bool:
        raise NotImplementedError
        
    def check_progress(self) -> int:
        return self.progress
        
    def submit_solution(self, solution: str) -> bool:
        raise NotImplementedError


class VulnerabilityLab(Lab):
    """Lab for learning about common vulnerabilities"""
    def __init__(self, name: str, vulnerability_type: str):
        super().__init__(name, f"Learn about {vulnerability_type} vulnerabilities")
        self.vulnerability_type = vulnerability_type
        self.docker_client = docker.from_env()
        self.container = None
        
    def start(self) -> bool:
        try:
            self.container = self.docker_client.containers.run(
                "webgoat/webgoat-8.0",
                detach=True,
                ports={'8080/tcp': 8080}
            )
            return True
        except Exception as e:
            logger.error(f"Failed to start vulnerability lab: {e}")
            return False
            
    def get_challenges(self) -> List[Dict]:
        return [
            {
                'name': 'SQL Injection Basics',
                'difficulty': 'Beginner',
                'points': 100
            },
            {
                'name': 'XSS Attacks',
                'difficulty': 'Intermediate',
                'points': 200
            },
            {
                'name': 'CSRF Vulnerabilities',
                'difficulty': 'Advanced',
                'points': 300
            }
        ]


class NetworkingLab(Lab):
    """Lab for network security learning"""
    def __init__(self, name: str):
        super().__init__(name, "Learn network security concepts")
        self.network = None
        self.containers = {}
        
    def start(self) -> bool:
        try:
            client = docker.from_env()
            self.network = client.networks.create(
                f"network_lab_{self.name}",
                driver="bridge",
                internal=True
            )
            
            # Create target machine
            self.containers['target'] = client.containers.run(
                "ubuntu:latest",
                detach=True,
                network=self.network.name
            )
            
            # Create attacker machine
            self.containers['attacker'] = client.containers.run(
                "kalilinux/kali-rolling",
                detach=True,
                network=self.network.name
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to start networking lab: {e}")
            return False
            
    def get_tools(self) -> List[str]:
        return [
            'nmap',
            'wireshark',
            'tcpdump',
            'netcat'
        ]


class CryptographyLab(Lab):
    """Lab for cryptography learning"""
    def __init__(self, name: str):
        super().__init__(name, "Learn cryptography and encryption")
        self.challenges = self._load_challenges()
        
    def _load_challenges(self) -> List[Dict]:
        return [
            {
                'name': 'Caesar Cipher',
                'difficulty': 'Beginner',
                'description': 'Break a simple substitution cipher'
            },
            {
                'name': 'RSA Basics',
                'difficulty': 'Intermediate',
                'description': 'Understand public-key cryptography'
            },
            {
                'name': 'Hash Cracking',
                'difficulty': 'Advanced',
                'description': 'Crack various hash formats'
            }
        ]
        
    def start(self) -> bool:
        try:
            # Set up cryptography environment
            return True
        except Exception as e:
            logger.error(f"Failed to start cryptography lab: {e}")
            return False


class ReverseEngineeringLab(Lab):
    """Lab for reverse engineering practice"""
    def __init__(self, name: str):
        super().__init__(name, "Learn reverse engineering techniques")
        self.tools = {
            'ghidra': '/opt/ghidra',
            'radare2': 'r2',
            'gdb': 'gdb'
        }
        
    def start(self) -> bool:
        try:
            client = docker.from_env()
            self.container = client.containers.run(
                "remnux/remnux-distro:focal",
                detach=True,
                volumes={
                    str(Path('samples').absolute()): {
                        'bind': '/samples',
                        'mode': 'ro'
                    }
                }
            )
            return True
        except Exception as e:
            logger.error(f"Failed to start reverse engineering lab: {e}")
            return False
            
    def get_samples(self) -> List[Dict]:
        return [
            {
                'name': 'simple_crackme',
                'difficulty': 'Beginner',
                'type': 'ELF binary'
            },
            {
                'name': 'packed_binary',
                'difficulty': 'Intermediate',
                'type': 'Packed PE'
            },
            {
                'name': 'obfuscated_code',
                'difficulty': 'Advanced',
                'type': 'JavaScript'
            }
        ]

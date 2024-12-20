from typing import List, Dict
import docker
import logging
from pathlib import Path
import time

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
        self.container = None
        self.network = None
        
    def start(self) -> bool:
        try:
            logger.info("Starting vulnerability lab container...")
            client = docker.from_env()
            
            # Create network first
            network_name = f"vuln_lab_{self.name}"
            logger.info(f"Creating network: {network_name}")
            self.network = client.networks.create(
                network_name,
                driver="bridge"
            )
            
            # For testing, use ubuntu
            # In production, we'll use webgoat/webgoat-8.0
            image = "ubuntu:latest" if "test" in self.name else "webgoat/webgoat-8.0"
            
            # Pull image first
            logger.info(f"Pulling image: {image}")
            client.images.pull(image)
            
            # Create container first
            logger.info("Creating container...")
            container = client.api.create_container(
                image=image,
                command="tail -f /dev/null",  # Keep container running
                detach=True,
                host_config=client.api.create_host_config(
                    network_mode=network_name,
                    auto_remove=True
                )
            )
            
            # Start container
            logger.info("Starting container...")
            client.api.start(container=container.get('Id'))
            
            # Get container object
            self.container = client.containers.get(container.get('Id'))
            
            # Log container info
            logger.info(f"Container ID: {self.container.id}")
            logger.info(f"Container status: {self.container.status}")
            logger.info(f"Container attrs: {self.container.attrs}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start vulnerability lab: {str(e)}")
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
        
    def cleanup(self) -> None:
        """Clean up lab resources."""
        try:
            if self.container:
                logger.info(f"Cleaning up container {self.container.id}...")
                try:
                    self.container.stop()
                    logger.info("Container stopped successfully")
                except Exception as e:
                    logger.error(f"Error during container cleanup: {e}")
                self.container = None
                
            # Clean up network
            if self.network:
                try:
                    logger.info(f"Cleaning up network {self.network.name}...")
                    self.network.remove()
                    logger.info("Network removed successfully")
                except Exception as e:
                    logger.error(f"Error removing network: {e}")
                self.network = None
                
        except Exception as e:
            logger.error(f"Failed to cleanup vulnerability lab: {e}")


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
            
    def get_tools(self) -> Dict[str, str]:
        return {
            'nmap': 'Network mapper for network discovery and security auditing',
            'wireshark': 'Network protocol analyzer for network troubleshooting and analysis',
            'tcpdump': 'Command-line packet analyzer',
            'netcat': 'Networking utility for reading/writing network connections'
        }
        
    def cleanup(self) -> None:
        """Clean up lab resources."""
        try:
            # Stop and remove containers
            for container in self.containers.values():
                try:
                    container.stop()
                    container.remove()
                except:
                    pass
            
            # Remove network
            if self.network:
                try:
                    self.network.remove()
                except:
                    pass
                    
            self.containers = {}
            self.network = None
        except Exception as e:
            logger.error(f"Failed to cleanup networking lab: {e}")


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

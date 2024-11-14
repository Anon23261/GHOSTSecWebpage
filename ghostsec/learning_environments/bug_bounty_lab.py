import docker
import logging
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import yaml

logger = logging.getLogger(__name__)

class BugBountyLab:
    """
    Bug Bounty testing and learning environment
    Includes common tools and vulnerable applications for practice
    """
    
    def __init__(self, workspace_name: str):
        self.workspace_name = workspace_name
        self.docker_client = docker.from_env()
        self.containers = {}
        self.workspace_path = Path(f"workspaces/bugbounty/{workspace_name}")
        self.tools_config = self._load_tools_config()
        
    def _load_tools_config(self) -> Dict:
        """Load bug bounty tools configuration"""
        config_path = Path(__file__).parent / "config" / "bugbounty_tools.yaml"
        with open(config_path) as f:
            return yaml.safe_load(f)
            
    def setup_environment(self) -> bool:
        """Set up bug bounty testing environment"""
        try:
            # Create workspace directories
            os.makedirs(self.workspace_path / "reports", exist_ok=True)
            os.makedirs(self.workspace_path / "tools", exist_ok=True)
            os.makedirs(self.workspace_path / "targets", exist_ok=True)
            
            # Start main container with common tools
            self.containers['main'] = self.docker_client.containers.run(
                "kalilinux/kali-rolling",
                detach=True,
                volumes={
                    str(self.workspace_path.absolute()): {
                        'bind': '/workspace',
                        'mode': 'rw'
                    }
                },
                network_mode="bridge",
                command="/bin/bash",
                tty=True
            )
            
            # Install essential tools
            self._install_tools()
            
            # Start vulnerable practice applications
            self._start_practice_targets()
            
            return True
        except Exception as e:
            logger.error(f"Failed to setup bug bounty lab: {e}")
            return False
            
    def _install_tools(self):
        """Install common bug bounty tools"""
        tools = [
            "nmap", "gobuster", "nikto", "sqlmap",
            "whatweb", "wfuzz", "ffuf", "nuclei",
            "amass", "subfinder", "httpx-toolkit",
            "burpsuite-community", "zaproxy"
        ]
        
        self.containers['main'].exec_run(
            f"apt-get update && apt-get install -y {' '.join(tools)}"
        )
        
        # Install additional tools from GitHub
        for tool in self.tools_config.get('github_tools', []):
            self.containers['main'].exec_run(
                f"git clone {tool['url']} /workspace/tools/{tool['name']}"
            )
            
    def _start_practice_targets(self):
        """Start vulnerable applications for practice"""
        practice_apps = {
            'juice-shop': 'bkimminich/juice-shop',
            'dvwa': 'vulnerables/web-dvwa',
            'mutillidae': 'citizenstig/nowasp',
            'webgoat': 'webgoat/webgoat-8.0'
        }
        
        for name, image in practice_apps.items():
            try:
                self.containers[name] = self.docker_client.containers.run(
                    image,
                    detach=True,
                    network_mode="bridge",
                    name=f"bugbounty_{name}"
                )
            except Exception as e:
                logger.error(f"Failed to start {name}: {e}")
                
    def start_scan(self, target: str, scan_type: str) -> Dict:
        """Run security scan against target"""
        results = {
            'target': target,
            'scan_type': scan_type,
            'findings': []
        }
        
        try:
            if scan_type == 'recon':
                results['findings'] = self._run_recon(target)
            elif scan_type == 'vulnerability':
                results['findings'] = self._run_vuln_scan(target)
            elif scan_type == 'fuzzing':
                results['findings'] = self._run_fuzzing(target)
        except Exception as e:
            logger.error(f"Scan failed: {e}")
            
        return results
        
    def _run_recon(self, target: str) -> List[Dict]:
        """Run reconnaissance tools"""
        findings = []
        
        # Subdomain enumeration
        cmd = f"amass enum -d {target} -o /workspace/reports/amass.txt"
        self.containers['main'].exec_run(cmd)
        
        # Port scanning
        cmd = f"nmap -sV -sC -oA /workspace/reports/nmap {target}"
        self.containers['main'].exec_run(cmd)
        
        # Web technology detection
        cmd = f"whatweb {target} -o /workspace/reports/whatweb.txt"
        self.containers['main'].exec_run(cmd)
        
        # Parse and return findings
        return self._parse_recon_results()
        
    def _run_vuln_scan(self, target: str) -> List[Dict]:
        """Run vulnerability scanners"""
        findings = []
        
        # Nuclei scan
        cmd = f"nuclei -u {target} -o /workspace/reports/nuclei.txt"
        self.containers['main'].exec_run(cmd)
        
        # Nikto scan
        cmd = f"nikto -h {target} -o /workspace/reports/nikto.txt"
        self.containers['main'].exec_run(cmd)
        
        # SQLMap scan
        cmd = f"sqlmap -u {target} --batch --random-agent -o /workspace/reports/sqlmap"
        self.containers['main'].exec_run(cmd)
        
        return self._parse_vuln_results()
        
    def _run_fuzzing(self, target: str) -> List[Dict]:
        """Run fuzzing tools"""
        findings = []
        
        # Directory fuzzing
        cmd = f"ffuf -u {target}/FUZZ -w /usr/share/wordlists/dirb/common.txt -o /workspace/reports/ffuf.json"
        self.containers['main'].exec_run(cmd)
        
        # Parameter fuzzing
        cmd = f"wfuzz -c -z file,/usr/share/wordlists/wfuzz/general/common.txt {target}?FUZZ=test"
        self.containers['main'].exec_run(cmd)
        
        return self._parse_fuzzing_results()
        
    def _parse_recon_results(self) -> List[Dict]:
        """Parse reconnaissance results"""
        findings = []
        # Parse amass results
        # Parse nmap results
        # Parse whatweb results
        return findings
        
    def _parse_vuln_results(self) -> List[Dict]:
        """Parse vulnerability scan results"""
        findings = []
        # Parse nuclei results
        # Parse nikto results
        # Parse sqlmap results
        return findings
        
    def _parse_fuzzing_results(self) -> List[Dict]:
        """Parse fuzzing results"""
        findings = []
        # Parse ffuf results
        # Parse wfuzz results
        return findings
        
    def cleanup(self):
        """Clean up bug bounty environment"""
        try:
            for container in self.containers.values():
                container.stop()
                container.remove()
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


class BugBountyChallenge:
    """
    Structured bug bounty challenges for learning
    """
    
    def __init__(self, name: str, difficulty: str):
        self.name = name
        self.difficulty = difficulty
        self.completed = False
        self.points = self._calculate_points()
        
    def _calculate_points(self) -> int:
        """Calculate points based on difficulty"""
        points_map = {
            'beginner': 100,
            'intermediate': 250,
            'advanced': 500,
            'expert': 1000
        }
        return points_map.get(self.difficulty.lower(), 100)
        
    def start(self) -> Dict:
        """Start the challenge"""
        return {
            'name': self.name,
            'difficulty': self.difficulty,
            'points': self.points,
            'objectives': self._get_objectives()
        }
        
    def _get_objectives(self) -> List[str]:
        """Get challenge objectives"""
        return [
            "Perform reconnaissance",
            "Identify vulnerabilities",
            "Develop exploit",
            "Document findings",
            "Propose fixes"
        ]
        
    def submit_solution(self, solution: Dict) -> bool:
        """Submit and verify challenge solution"""
        # Verify solution
        # Update completion status
        # Award points
        return True

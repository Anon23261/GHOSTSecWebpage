"""Test suite for GhostSec learning environments."""
import pytest
import docker
import time
import logging
from ghostsec.learning_environments.labs import (
    VulnerabilityLab,
    NetworkingLab,
    CryptographyLab,
    ReverseEngineeringLab
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_docker_available():
    """Check if Docker is available and running."""
    try:
        client = docker.from_env()
        client.ping()
        return True
    except Exception as e:
        logger.error(f"Docker not available: {e}")
        return False

def wait_for_container_status(container, target_status: str, timeout: int = 10) -> bool:
    """Wait for container to reach target status."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            container.reload()
            logger.info(f"Container status: {container.status}")
            if container.status == target_status:
                return True
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error checking container status: {e}")
            return False
    return False

@pytest.fixture
def vulnerability_lab():
    """Create a vulnerability lab instance."""
    if not is_docker_available():
        pytest.skip("Docker not available")
    lab = VulnerabilityLab("test_vuln_lab", "sql_injection")
    yield lab
    lab.cleanup()

@pytest.fixture
def networking_lab():
    """Create a networking lab instance."""
    if not is_docker_available():
        pytest.skip("Docker not available")
    lab = NetworkingLab("test_network_lab")
    yield lab
    lab.cleanup()

def test_vulnerability_lab_creation(vulnerability_lab):
    """Test vulnerability lab creation."""
    assert vulnerability_lab.name == "test_vuln_lab"
    assert vulnerability_lab.vulnerability_type == "sql_injection"
    assert vulnerability_lab.container is None

def test_vulnerability_lab_start(vulnerability_lab):
    """Test vulnerability lab startup."""
    logger.info("Starting vulnerability lab test...")
    
    # First cleanup any existing containers
    vulnerability_lab.cleanup()
    
    # Start the lab
    result = vulnerability_lab.start()
    assert result is True, "Lab start() method returned False"
    assert vulnerability_lab.container is not None, "Container is None after start"
    
    # Wait for container
    logger.info("Waiting for container to start...")
    time.sleep(2)
    
    # Check container status
    vulnerability_lab.container.reload()
    logger.info(f"Container status after reload: {vulnerability_lab.container.status}")
    logger.info(f"Container attrs after reload: {vulnerability_lab.container.attrs}")
    
    assert vulnerability_lab.container.status == "running", \
        f"Container failed to reach running state. Status: {vulnerability_lab.container.status}"

def test_vulnerability_lab_challenges(vulnerability_lab):
    """Test vulnerability lab challenges."""
    challenges = vulnerability_lab.get_challenges()
    assert isinstance(challenges, list)
    assert len(challenges) > 0
    assert all(isinstance(c, dict) for c in challenges)
    assert all('name' in c for c in challenges)
    assert all('difficulty' in c for c in challenges)
    assert all('points' in c for c in challenges)

def test_networking_lab_creation(networking_lab):
    """Test networking lab creation."""
    assert networking_lab.name == "test_network_lab"
    assert networking_lab.network is None
    assert not networking_lab.containers

def test_networking_lab_start(networking_lab):
    """Test networking lab startup."""
    result = networking_lab.start()
    assert result is True
    assert networking_lab.network is not None
    assert len(networking_lab.containers) > 0

def test_networking_lab_tools(networking_lab):
    """Test networking lab tools."""
    tools = networking_lab.get_tools()
    assert isinstance(tools, dict)
    assert len(tools) > 0
    assert all(isinstance(t, str) for t in tools.values())

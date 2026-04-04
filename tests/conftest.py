"""
Pytest configuration for RH-PPT-Skills tests.
"""

import pytest
import sys
from pathlib import Path

# Add scripts directory to Python path
scripts_dir = Path(__file__).parent.parent / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))


def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test (requires external dependencies)",
    )
    config.addinivalue_line("markers", "slow: mark test as slow running")


@pytest.fixture
def mock_env_api_key(monkeypatch):
    """Fixture to mock API key in environment."""
    monkeypatch.setenv("RH_API_KEY", "test-api-key-12345")
    return "test-api-key-12345"


@pytest.fixture
def temp_output_dir(tmp_path):
    """Provide a temporary directory for output files."""
    output_dir = tmp_path / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir

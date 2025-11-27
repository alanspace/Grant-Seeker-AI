"""Pytest configuration and fixtures."""
import pytest
import sys
from pathlib import Path

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

"""
SayToAI Shared Package
=====================

Shared utilities and components for SayToAI applications.
"""

__version__ = "0.1.0"
__author__ = "SayToAI"

# Import constants to make them available
from . import constants

# Make constants easily accessible
__all__ = ['constants']

# Minimal shared package to resolve import issues
# This is a placeholder until the actual shared package is properly implemented 
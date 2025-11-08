"""
Mai Shen Yun - Inventory Management Dashboard
Source package initialization
"""

__version__ = "1.0.0"
__author__ = "Mai Shen Yun Team"

from .data_loader import DataLoader
from .data_processor import DataProcessor
from .analytics import InventoryAnalytics
from .predictions import InventoryPredictor
from .visualizations import InventoryVisualizations

__all__ = [
    'DataLoader',
    'DataProcessor',
    'InventoryAnalytics',
    'InventoryPredictor',
    'InventoryVisualizations'
]

"""
Test script to verify all imports work correctly
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

print("Testing imports...")

try:
    from src.data_loader import DataLoader
    print("✅ DataLoader imported successfully")
except Exception as e:
    print(f"❌ DataLoader import failed: {e}")

try:
    from src.data_processor import DataProcessor
    print("✅ DataProcessor imported successfully")
except Exception as e:
    print(f"❌ DataProcessor import failed: {e}")

try:
    from src.analytics import InventoryAnalytics
    print("✅ InventoryAnalytics imported successfully")
except Exception as e:
    print(f"❌ InventoryAnalytics import failed: {e}")

try:
    from src.predictions import InventoryPredictor
    print("✅ InventoryPredictor imported successfully")
except Exception as e:
    print(f"❌ InventoryPredictor import failed: {e}")

try:
    from src.visualizations import InventoryVisualizations
    print("✅ InventoryVisualizations imported successfully")
except Exception as e:
    print(f"❌ InventoryVisualizations import failed: {e}")

print("\n" + "="*50)
print("All imports test completed!")
print("="*50)

# Test basic functionality
print("\nTesting basic functionality...")

try:
    loader = DataLoader()
    print("✅ DataLoader instantiated")

    processor = DataProcessor()
    print("✅ DataProcessor instantiated")

    analytics = InventoryAnalytics()
    print("✅ InventoryAnalytics instantiated")

    predictor = InventoryPredictor()
    print("✅ InventoryPredictor instantiated")

    viz = InventoryVisualizations()
    print("✅ InventoryVisualizations instantiated")

    print("\n✅ All basic functionality tests passed!")

except Exception as e:
    print(f"❌ Basic functionality test failed: {e}")

print("\n" + "="*50)
print("Build verification complete!")
print("="*50)

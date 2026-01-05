#!/usr/bin/env python3
"""
Quick verification that imports work after circular dependency fixes.
Enhanced version with more comprehensive checks.
"""

import sys
import os
import importlib

# Add parent directory to path for testing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_basic_imports():
    """Test that key imports work without circular dependencies"""
    print("Testing basic imports...")
    
    try:
        import agentic_reliability_framework
        print("✓ Main package imports")
        
        from agentic_reliability_framework import ARFSession, BusinessMetrics, HealingIntent
        print("✓ Core classes import")
        
        from agentic_reliability_framework.engine import ReliabilityEngine
        print("✓ Engine imports")
        
        from agentic_reliability_framework.memory import EnhancedFAISSIndex
        print("✓ Memory imports")
        
        from agentic_reliability_framework.config import get_config
        print("✓ Config imports")
        
        return True
    except Exception as e:
        print(f"✗ Basic imports failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_arf_core_imports():
    """Test ARF core imports specifically for circular dependency issues"""
    print("\nTesting ARF core imports...")
    
    try:
        # Clear any existing imports - SAFELY
        modules_to_clear = [
            m for m in sys.modules.keys() 
            if 'arf_core' in m and 'test' not in m
        ]
        for module in modules_to_clear:
            del sys.modules[module]
        
        from agentic_reliability_framework.arf_core import (
            HealingIntent,
            OSSMCPClient,
            EventSeverity,
            ReliabilityEvent,
            create_compatible_event,
        )
        print("✓ ARF core imports")
        
        # Test that ReliabilityEvent doesn't cause circular import
        event = create_compatible_event(
            component="test",
            severity=EventSeverity.MEDIUM,
            latency_p99=100.0
        )
        print("✓ ReliabilityEvent creation works")
        
        return True
    except Exception as e:
        print(f"✗ ARF core imports failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_models_imports():
    """Test that models import without circular dependencies"""
    print("\nTesting models imports...")
    
    try:
        # Test both model locations
        from agentic_reliability_framework.arf_core.models import (
            HealingIntent,
            create_rollback_intent,
        )
        print("✓ arf_core.models imports")
        
        from agentic_reliability_framework.models import (
            Incident,
            Timeline,
            SystemState,
        )
        print("✓ Main models imports")
        
        # Ensure no circular import between them
        intent = create_rollback_intent(
            component="api",
            revision="v1.0.0",
            justification="Test"
        )
        print("✓ Model creation works")
        
        return True
    except Exception as e:
        print(f"✗ Models imports failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_engine_imports():
    """Test engine module imports"""
    print("\nTesting engine imports...")
    
    try:
        from agentic_reliability_framework.engine import (
            ReliabilityEngine,
            AnomalyEngine,
            BusinessMetricsEngine,
            PredictiveEngine,
            V3ReliabilityEngine,
            MCPClient,
            MCPFactory,
            MCPServer,
            EngineFactory,
        )
        print("✓ Engine imports work")
        
        # Test factory creation
        factory = EngineFactory()
        print("✓ EngineFactory instantiation")
        
        return True
    except Exception as e:
        print(f"✗ Engine import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_oss_boundary():
    """Test OSS/Enterprise boundary"""
    print("\nTesting OSS boundary...")
    
    try:
        from agentic_reliability_framework import OSS_EDITION, OSS_LICENSE
        print(f"✓ OSS constants: edition={OSS_EDITION}, license={OSS_LICENSE}")
        
        from agentic_reliability_framework.arf_core.constants import (
            OSSBoundaryError,
            validate_oss_config,
        )
        print("✓ OSS boundary utilities")
        
        # Test OSS mode validation
        config = validate_oss_config()
        print(f"✓ OSS config validation: {config}")
        
        return True
    except Exception as e:
        print(f"✗ OSS boundary test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_complete_workflow():
    """Test a complete import workflow"""
    print("\nTesting complete import workflow...")
    
    try:
        # Clear everything and start fresh - SAFELY
        modules_to_clear = [
            m for m in sys.modules.keys() 
            if m.startswith('agentic_reliability_framework') and 'test' not in m
        ]
        for module in modules_to_clear:
            del sys.modules[module]
        
        # Import in user order
        import agentic_reliability_framework as arf
        
        # Check version
        assert hasattr(arf, '__version__'), "No __version__ found"
        print(f"✓ Package version: {arf.__version__}")
        
        # Check OSS mode
        assert arf.OSS_EDITION is True, "Should be OSS edition"
        print("✓ OSS edition confirmed")
        
        # Import key components
        from agentic_reliability_framework import (
            HealingIntent,
            create_mcp_client,
            get_oss_capabilities,
        )
        
        # Get capabilities
        caps = get_oss_capabilities()
        print(f"✓ OSS capabilities: {caps.get('mode', 'unknown')}")
        
        return True
    except Exception as e:
        print(f"✗ Complete workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main verification function"""
    print("=" * 60)
    print("ARF Import Verification Test")
    print("=" * 60)
    
    tests = [
        test_basic_imports,
        test_arf_core_imports,
        test_models_imports,
        test_engine_imports,
        test_oss_boundary,
        test_complete_workflow,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("✅ All import tests passed!")
        print("✅ Circular import fixes verified!")
        return 0
    else:
        print(f"❌ {failed} test(s) failed")
        print("❌ Import issues detected")
        return 1


if __name__ == "__main__":
    sys.exit(main())

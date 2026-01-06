#!/usr/bin/env python3
"""
Quick verification that imports work after circular dependency fixes.
Enhanced version with more comprehensive checks and OSS boundary validation.

This script now includes:
1. Comprehensive import tests for all OSS components
2. OSS boundary validation
3. Circular import detection
4. Import structure verification
"""

import sys
import os
import importlib
import traceback
from typing import List, Tuple

# Add parent directory to path for testing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def clear_module_cache():
    """Clear cached modules to test fresh imports"""
    modules_to_clear = [
        'agentic_reliability_framework',
        'agentic_reliability_framework.arf_core',
        'agentic_reliability_framework.arf_core.engine.oss_mcp_client',
        'agentic_reliability_framework.arf_core.models.healing_intent',
        'agentic_reliability_framework.config',
        'agentic_reliability_framework.engine',
        'agentic_reliability_framework.lazy',
        'agentic_reliability_framework.app',
    ]
    
    cleared = []
    for module in modules_to_clear:
        if module in sys.modules:
            del sys.modules[module]
            cleared.append(module)
    
    return cleared


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


def test_oss_import_structure():
    """Test comprehensive OSS import structure"""
    print("\nTesting OSS import structure...")
    
    try:
        # Clear cache for fresh test
        cleared = clear_module_cache()
        print(f"Cleared {len(cleared)} modules for fresh test")
        
        # Test all public API imports
        imports_to_test = [
            ("Main package", "import agentic_reliability_framework"),
            ("HealingIntent", "from agentic_reliability_framework import HealingIntent"),
            ("HealingIntentSerializer", "from agentic_reliability_framework import HealingIntentSerializer"),
            ("OSSMCPClient", "from agentic_reliability_framework import OSSMCPClient"),
            ("create_mcp_client", "from agentic_reliability_framework import create_mcp_client"),
            ("OSS Constants", "from agentic_reliability_framework import OSS_EDITION, OSS_LICENSE, EXECUTION_ALLOWED, MCP_MODES_ALLOWED"),
            ("Factory Functions", "from agentic_reliability_framework import create_rollback_intent, create_restart_intent, create_scale_out_intent"),
            ("Core Models", "from agentic_reliability_framework import ReliabilityEvent, EventSeverity, create_compatible_event"),
            ("Engine Factory", "from agentic_reliability_framework import EngineFactory, create_engine, get_engine, get_oss_engine_capabilities"),
            ("OSS Response Types", "from agentic_reliability_framework import OSSMCPResponse, OSSAnalysisResult"),
            ("OSS Validation", "from agentic_reliability_framework import OSSBoundaryError, validate_oss_config, get_oss_capabilities, check_oss_compliance"),
        ]
        
        passed_imports = 0
        failed_imports = []
        
        for name, import_stmt in imports_to_test:
            try:
                exec(import_stmt)
                print(f"✓ {name}")
                passed_imports += 1
            except RecursionError as e:
                print(f"✗ {name}: CIRCULAR IMPORT DETECTED: {e}")
                failed_imports.append(f"{name}: Circular import")
            except Exception as e:
                print(f"✗ {name}: {type(e).__name__}: {e}")
                failed_imports.append(f"{name}: {type(e).__name__}: {e}")
        
        # Verify OSS edition constraints
        import agentic_reliability_framework as arf
        assert arf.OSS_EDITION == "open-source", f"OSS_EDITION should be 'open-source', got {arf.OSS_EDITION}"
        assert arf.OSS_LICENSE == "Apache 2.0", f"OSS_LICENSE should be 'Apache 2.0', got {arf.OSS_LICENSE}"
        assert arf.EXECUTION_ALLOWED is False, f"EXECUTION_ALLOWED should be False in OSS, got {arf.EXECUTION_ALLOWED}"
        assert arf.MCP_MODES_ALLOWED == ("advisory",), f"MCP_MODES_ALLOWED should be ('advisory',), got {arf.MCP_MODES_ALLOWED}"
        
        print(f"✓ OSS boundary constraints verified")
        
        # Test that OSSMCPClient is advisory only
        from agentic_reliability_framework import OSSMCPClient
        client = OSSMCPClient()
        assert hasattr(client, 'mode'), "OSSMCPClient should have 'mode' attribute"
        assert client.mode == "advisory", f"OSSMCPClient mode should be 'advisory', got {client.mode}"
        print(f"✓ OSSMCPClient is advisory mode only")
        
        if failed_imports:
            print(f"\n❌ Failed imports: {len(failed_imports)}/{len(imports_to_test)}")
            for failed in failed_imports:
                print(f"  - {failed}")
            return False
        
        print(f"\n✅ All {passed_imports}/{len(imports_to_test)} OSS imports successful")
        return True
        
    except Exception as e:
        print(f"✗ OSS import structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_circular_import_prevention():
    """Test that circular imports are prevented"""
    print("\nTesting circular import prevention...")
    
    try:
        # Clear all ARF modules
        modules_to_clear = [
            m for m in sys.modules.keys() 
            if 'agentic_reliability_framework' in m
        ]
        for module in modules_to_clear:
            del sys.modules[module]
        
        # Import in problematic order that could cause circular imports
        import agentic_reliability_framework.arf_core.constants
        import agentic_reliability_framework.arf_core.models.healing_intent
        import agentic_reliability_framework.arf_core.engine.oss_mcp_client
        import agentic_reliability_framework.arf_core
        
        # Import main package
        import agentic_reliability_framework
        
        # Try to import everything that previously caused circular issues
        from agentic_reliability_framework.arf_core import OSSMCPClient, HealingIntent
        from agentic_reliability_framework.arf_core.constants import OSSBoundaryError
        from agentic_reliability_framework.arf_core.models.healing_intent import create_rollback_intent
        from agentic_reliability_framework.arf_core.engine.oss_mcp_client import create_oss_mcp_client
        
        # Test that imports work both ways
        from agentic_reliability_framework import create_mcp_client
        from agentic_reliability_framework.arf_core.engine.oss_mcp_client import OSSMCPClient as OrigOSSMCPClient
        
        print("✓ No circular imports detected")
        
        # Create instances to ensure no runtime circular issues
        intent = create_rollback_intent(component="test", revision="previous")
        client = create_mcp_client()
        
        print("✓ Instances created without circular dependency issues")
        
        return True
        
    except RecursionError as e:
        print(f"✗ CIRCULAR IMPORT DETECTED: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"✗ Circular import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_import_performance():
    """Test that imports are performant (no excessive module loading)"""
    print("\nTesting import performance...")
    
    try:
        import time
        
        # Clear cache
        modules_to_clear = [
            m for m in sys.modules.keys() 
            if 'agentic_reliability_framework' in m
        ]
        for module in modules_to_clear:
            del sys.modules[module]
        
        # Time the import
        start_time = time.time()
        import agentic_reliability_framework
        import_duration = time.time() - start_time
        
        print(f"✓ Main package import: {import_duration:.3f}s")
        
        # Import key components
        start_time = time.time()
        from agentic_reliability_framework import HealingIntent, OSSMCPClient
        component_duration = time.time() - start_time
        
        print(f"✓ Key component imports: {component_duration:.3f}s")
        
        # Check if import is reasonable (should be < 1 second on most systems)
        if import_duration > 2.0:
            print(f"⚠️  Warning: Slow import detected ({import_duration:.3f}s)")
            # Don't fail, just warn
        
        return True
        
    except Exception as e:
        print(f"✗ Import performance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main verification function"""
    print("=" * 60)
    print("ARF OSS Import Verification & Boundary Test")
    print("=" * 60)
    
    tests = [
        test_basic_imports,
        test_arf_core_imports,
        test_models_imports,
        test_engine_imports,
        test_oss_boundary,
        test_complete_workflow,
        test_oss_import_structure,
        test_circular_import_prevention,
        test_import_performance,
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
        print("✅ OSS boundary validation passed!")
        return 0
    else:
        print(f"❌ {failed} test(s) failed")
        print("❌ Import or boundary issues detected")
        return 1


if __name__ == "__main__":
    sys.exit(main())

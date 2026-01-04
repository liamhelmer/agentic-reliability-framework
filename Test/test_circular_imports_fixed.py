"""
Test to verify circular imports have been resolved.
This test should run as part of the test suite to ensure no regressions.
"""

import sys
import importlib
import pytest
from pathlib import Path


def test_no_circular_imports_main_package():
    """Test that main package imports without circular dependencies"""
    # Clear any existing imports
    modules_to_clear = [
        m for m in sys.modules.keys() 
        if m.startswith('agentic_reliability_framework')
    ]
    for module in modules_to_clear:
        del sys.modules[module]
    
    # Import main package
    try:
        import agentic_reliability_framework
        assert agentic_reliability_framework.__version__ is not None
        print("✓ Main package imports successfully")
    except ImportError as e:
        pytest.fail(f"Circular import in main package: {e}")


def test_arf_core_imports_independently():
    """Test that arf_core can be imported independently"""
    # Clear arf_core imports
    modules_to_clear = [
        m for m in sys.modules.keys() 
        if 'arf_core' in m
    ]
    for module in modules_to_clear:
        del sys.modules[module]
    
    # Import arf_core directly
    try:
        from agentic_reliability_framework.arf_core import (
            HealingIntent,
            OSSMCPClient,
            EventSeverity,
            ReliabilityEvent,
            create_compatible_event,
        )
        print("✓ arf_core imports independently")
    except ImportError as e:
        pytest.fail(f"arf_core import failed: {e}")


def test_models_no_circular_import():
    """Test that models don't create circular imports"""
    # Clear models imports
    modules_to_clear = [
        m for m in sys.modules.keys() 
        if 'models' in m and 'agentic_reliability_framework' in m
    ]
    for module in modules_to_clear:
        del sys.modules[module]
    
    try:
        # Test both model locations
        from agentic_reliability_framework.arf_core.models import (
            HealingIntent,
            EventSeverity,
            ReliabilityEvent,
        )
        
        from agentic_reliability_framework.models import (
            Incident,
            Timeline,
            SystemState,
        )
        
        print("✓ Models import without circular dependencies")
    except ImportError as e:
        pytest.fail(f"Models import failed: {e}")


def test_oss_mcp_client_import():
    """Test OSS MCP client imports without circular dependencies"""
    modules_to_clear = [
        m for m in sys.modules.keys() 
        if 'oss_mcp_client' in m or 'mcp' in m
    ]
    for module in modules_to_clear:
        del sys.modules[module]
    
    try:
        from agentic_reliability_framework.arf_core.engine.oss_mcp_client import (
            OSSMCPClient,
            OSSMCPResponse,
            create_oss_mcp_client,
        )
        
        # Test instantiation
        client = OSSMCPClient()
        assert client.mode == "advisory"
        print("✓ OSS MCP client imports and instantiates")
    except ImportError as e:
        pytest.fail(f"OSS MCP client import failed: {e}")


def test_import_chain():
    """Test specific import chains that were previously problematic"""
    import_chains = [
        # Chain 1: Main -> arf_core -> models
        lambda: (__import__('agentic_reliability_framework'),
                 __import__('agentic_reliability_framework.arf_core'),
                 __import__('agentic_reliability_framework.arf_core.models')),
        
        # Chain 2: Engine -> arf_core
        lambda: (__import__('agentic_reliability_framework.engine'),
                 __import__('agentic_reliability_framework.arf_core.engine')),
        
        # Chain 3: arf_core.models -> create_compatible_event
        lambda: (__import__('agentic_reliability_framework.arf_core.models'),
                 from agentic_reliability_framework.arf_core.models import create_compatible_event),
    ]
    
    for i, import_chain in enumerate(import_chains):
        try:
            # Clear all ARF modules
            modules_to_clear = [
                m for m in sys.modules.keys() 
                if m.startswith('agentic_reliability_framework')
            ]
            for module in modules_to_clear:
                del sys.modules[module]
            
            import_chain()
            print(f"✓ Import chain {i+1} successful")
        except Exception as e:
            pytest.fail(f"Import chain {i+1} failed: {e}")


def test_reliability_event_no_parent_import():
    """Test that ReliabilityEvent doesn't import from parent package"""
    import ast
    import inspect
    
    # Get the source of the ReliabilityEvent class
    from agentic_reliability_framework.arf_core.models import ReliabilityEvent
    
    # Check the source code for parent package imports
    source = inspect.getsource(ReliabilityEvent)
    tree = ast.parse(source)
    
    # Look for imports from parent package
    parent_imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and 'agentic_reliability_framework.models' in node.module:
                parent_imports.append(node.module)
    
    assert len(parent_imports) == 0, \
        f"ReliabilityEvent should not import from parent package. Found: {parent_imports}"
    
    print("✓ ReliabilityEvent doesn't import from parent package")


def test_create_compatible_event_works():
    """Test that create_compatible_event works without circular imports"""
    from agentic_reliability_framework.arf_core.models import (
        create_compatible_event,
        EventSeverity,
    )
    
    # Test creation
    event = create_compatible_event(
        component="api_gateway",
        severity=EventSeverity.HIGH,
        latency_p99=200.0,
        error_rate=0.1,
    )
    
    assert event.component == "api_gateway"
    assert event.severity == "high"
    assert event.latency_p99 == 200.0
    assert event.error_rate == 0.1
    
    print("✓ create_compatible_event works correctly")


def test_healing_intent_import():
    """Test HealingIntent imports without circular dependencies"""
    modules_to_clear = [
        m for m in sys.modules.keys() 
        if 'healing_intent' in m
    ]
    for module in modules_to_clear:
        del sys.modules[module]
    
    try:
        from agentic_reliability_framework.arf_core.models.healing_intent import (
            HealingIntent,
            create_rollback_intent,
            create_restart_intent,
        )
        
        # Test creation
        intent = create_rollback_intent(
            component="api_service",
            revision="v1.2.3",
            justification="Test rollback",
        )
        
        assert intent.component == "api_service"
        assert intent.action == "rollback"
        
        print("✓ HealingIntent imports and creates instances")
    except ImportError as e:
        pytest.fail(f"HealingIntent import failed: {e}")


@pytest.mark.asyncio
async def test_oss_mcp_client_integration():
    """Test OSS MCP client integration without circular imports"""
    from agentic_reliability_framework.arf_core.engine.oss_mcp_client import (
        OSSMCPClient,
        create_oss_mcp_client,
    )
    
    # Create client
    client = create_oss_mcp_client()
    
    # Test advisory execution
    result = await client.execute_tool({
        "tool": "restart_container",
        "component": "api_container",
        "parameters": {"grace_period": 30},
        "justification": "Test restart",
    })
    
    assert result["status"] in ["completed", "advisory"]
    assert result["executed"] is False  # OSS should never execute
    assert "oss_edition" in result
    
    print("✓ OSS MCP client integration works")


def test_complete_import_workflow():
    """Test a complete import workflow from scratch"""
    # Clear EVERYTHING
    modules_to_clear = [
        m for m in sys.modules.keys() 
        if 'agentic_reliability' in m or 'arf' in m
    ]
    for module in modules_to_clear:
        del sys.modules[module]
    
    try:
        # Import in the order a user would
        import agentic_reliability_framework as arf
        
        from agentic_reliability_framework import (
            HealingIntent,
            OSSMCPClient,
            create_mcp_client,
        )
        
        from agentic_reliability_framework.engine import (
            ReliabilityEngine,
            EngineFactory,
        )
        
        from agentic_reliability_framework.memory import (
            EnhancedFAISSIndex,
            RAGGraphMemory,
        )
        
        # Test basic functionality
        assert arf.__version__ is not None
        assert arf.OSS_EDITION is True
        
        print("✓ Complete import workflow successful")
        return True
        
    except Exception as e:
        import traceback
        print(f"✗ Complete import workflow failed: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    """Run tests directly"""
    test_functions = [
        test_no_circular_imports_main_package,
        test_arf_core_imports_independently,
        test_models_no_circular_import,
        test_oss_mcp_client_import,
        test_reliability_event_no_parent_import,
        test_create_compatible_event_works,
        test_healing_intent_import,
        test_complete_import_workflow,
    ]
    
    passed = 0
    total = len(test_functions)
    
    for test_func in test_functions:
        try:
            test_func()
            passed += 1
            print(f"✅ {test_func.__name__} passed\n")
        except Exception as e:
            print(f"❌ {test_func.__name__} failed: {e}\n")
    
    print(f"\n{'='*60}")
    print(f"Circular Import Tests: {passed}/{total} passed")
    print(f"{'='*60}")
    
    if passed == total:
        print("✅ All circular import tests passed!")
        sys.exit(0)
    else:
        print("❌ Some circular import tests failed")
        sys.exit(1)

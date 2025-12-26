# scripts/fix_mcp_server_indentation.py
import re

def fix_mcp_server_indentation():
    """Fix indentation issues in mcp_server.py"""
    
    with open('agentic_reliability_framework/engine/mcp_server.py', 'r') as f:
        content = f.read()
    
    # Find the problematic section
    lines = content.split('\n')
    
    # Find where _create_healing_intent starts
    for i, line in enumerate(lines):
        if 'async def _create_healing_intent' in line and 'class MCPServer' not in '\n'.join(lines[max(0, i-5):i]):
            print(f"Found _create_healing_intent at line {i+1}")
            print(f"Line: {line}")
            
            # Check if it's indented properly
            if not line.startswith('    '):  # Should have at least 4 spaces
                print("❌ ERROR: _create_healing_intent is not indented under MCPServer class!")
                print("This is causing syntax errors and CI failures.")
                return False
    
    print("✅ File appears to have correct indentation")
    return True

if __name__ == "__main__":
    if fix_mcp_server_indentation():
        print("\n✅ No indentation issues found")
    else:
        print("\n❌ Indentation issues detected. Need to fix:")
        print("1. Ensure _create_healing_intent is inside MCPServer class")
        print("2. Ensure _handle_advisory_mode is inside MCPServer class")
        print("3. Both methods should be indented with 4 spaces")

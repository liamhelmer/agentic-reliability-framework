# 🚀 ARF OSS Edition Release Checklist
# Version: 3.3.6 (Stable Import Structure)

## 📋 Pre-Release Verification

### ✅ OSS Boundary Verification
- [ ] Run OSS boundary check: `python scripts/oss_boundary_check.py`
- [ ] Verify no `license_key` patterns exist
- [ ] Confirm no references to deleted `simple_mcp_client.py`
- [ ] Check all imports use `oss_mcp_client.py` instead

### ✅ Circular Import Verification  
- [ ] Run circular import check: `python scripts/verify_circular_fix.py --quick`
- [ ] Run comprehensive import test: `python Test/verify_import_fix.py`
- [ ] Verify no RecursionError occurs on fresh import

### ✅ Project Hygiene
- [ ] Install pre-commit hooks: `pre-commit install`
- [ ] Run all hooks: `pre-commit run --all-files`
- [ ] Check code formatting (Ruff): `ruff check --fix`
- [ ] Verify type hints (MyPy): `mypy --ignore-missing-imports agentic_reliability_framework`

## 🧪 Test Suite Execution

### ✅ Basic Tests
- [ ] Run basic test suite: `python -m pytest Test/test_basic.py -v`
- [ ] Verify all imports work: `python Test/test_basic.py`

### ✅ OSS Integration Tests
- [ ] Run OSS integration tests: `python Test/test_healing_intent_integration.py`
- [ ] Run MCP server tests: `python -m pytest Test/test_mcp_server_oss.py -v`
- [ ] Run OSS client tests: `python -m pytest Test/test_oss_mcp_client.py -v`

### ✅ Comprehensive Verification
- [ ] Run final OSS verification: `python Test/final_oss_verification.py`
- [ ] Expected output: "ALL OSS VERIFICATION TESTS PASSED"

## 📦 Build & Package Verification

### ✅ Package Build
- [ ] Clean build artifacts: `rm -rf dist/ build/ *.egg-info/`
- [ ] Build package: `python -m build`
- [ ] Verify wheel structure: `unzip -l dist/*.whl | grep -E "__init__|healing_intent|oss_mcp"`

### ✅ Package Installation Test
- [ ] Create fresh virtual environment
- [ ] Install from local build: `pip install dist/*.whl`
- [ ] Test import in fresh env: `python -c "import agentic_reliability_framework; print(f'✅ ARF v{agentic_reliability_framework.__version__}')"`

### ✅ Dependency Check
- [ ] Verify no Enterprise dependencies in `pyproject.toml`
- [ ] Check requirements: `pip list | grep -E "neo4j|sentence-transformers|torch"` (should be empty)
- [ ] Confirm OSS-only dependencies: `pip show agentic-reliability-framework`

## 🏷️ Release Process

### ✅ Version Bump (if needed)
- [ ] Already at version 3.3.6 (no bump needed for current release)
- [ ] Verify `agentic_reliability_framework/__version__.py` shows 3.3.6
- [ ] Verify `pyproject.toml` version shows 3.3.6

### ✅ Documentation Updates
- [ ] Update README.md with current version info
- [ ] Update any breaking changes in CHANGELOG or RELEASE_NOTES.md
- [ ] Verify all examples work with new import structure

### ✅ Git Operations
- [ ] Ensure all changes are committed
- [ ] Create release tag: `git tag -a v3.3.6 -m "Release v3.3.6: Stable import structure, OSS boundary fixes"`
- [ ] Push tag: `git push origin v3.3.6`

## 🚀 PyPI Publication (Optional)

### ✅ TestPyPI (for testing)
- [ ] Upload to TestPyPI: `twine upload --repository testpypi dist/*`
- [ ] Install from TestPyPI: `pip install --index-url https://test.pypi.org/simple/ agentic-reliability-framework`
- [ ] Verify installation works

### ✅ Production PyPI
- [ ] Upload to PyPI: `twine upload dist/*`
- [ ] Verify on pypi.org: https://pypi.org/project/agentic-reliability-framework/
- [ ] Test install: `pip install agentic-reliability-framework==3.3.6`

## 📊 Post-Release Verification

### ✅ CI/CD Pipeline
- [ ] Verify GitHub Actions pass for the release tag
- [ ] Check all workflow runs: OSS Tests, OSS Boundary Tests, Comprehensive Tests
- [ ] Confirm no regressions in test suites

### ✅ End-to-End Test
- [ ] Create a fresh project
- [ ] Install ARF: `pip install agentic-reliability-framework`
- [ ] Run quick demo or example from documentation
- [ ] Verify HealingIntent and OSSMCPClient work correctly

## 🔧 Critical Fixes Verified in v3.3.6

### ✅ RESOLVED: Circular Imports
- Fixed: `simple_mcp_client.py` importing from wrong path
- Fixed: `arf_core/__init__.py` lazy loading issues
- Fixed: Main package `__init__.py` import structure
- Fixed: `verify_circular_fix.py` updated to check `oss_mcp_client.py`

### ✅ RESOLVED: OSS Boundary Violations  
- Fixed: `license_key` variable name (renamed to `has_enterprise_key`)
- Fixed: References to deleted `simple_mcp_client.py`
- Fixed: Import paths using correct `oss_mcp_client.py`
- Added: OSS boundary checker script

### ✅ ADDED: Project Hygiene
- Created: `.pre-commit-config.yaml` with OSS boundary checks
- Enhanced: `verify_import_fix.py` with comprehensive tests
- Added: `final_oss_verification.py` for release validation
- Added: `RELEASE_CHECKLIST.md` for consistent releases

## 🆘 Troubleshooting

### Common Issues:

1. **Circular Import Still Occurs**
   - Run: `python scripts/verify_circular_fix.py`
   - Check: `agentic_reliability_framework/arf_core/__init__.py` lines 33-35
   - Ensure: No `simple_mcp_client` imports

2. **OSS Boundary Check Fails**
   - Run: `python scripts/oss_boundary_check.py --verbose`
   - Check for: `license_key`, `EnterpriseMCPServer`, `ARF-ENT-` patterns
   - Verify: `has_enterprise_key` variable name in constants.py

3. **Import Errors in Tests**
   - Clear cache: Delete `__pycache__/` directories
   - Fresh test: `python -c "import sys; sys.modules.clear(); import agentic_reliability_framework"`

## 📞 Support

If any step fails, check:
1. GitHub Actions logs for the specific failure
2. Run the verification script: `python Test/final_oss_verification.py`
3. Review recent fixes in commit history

---

**Last Updated**: v3.3.6 Stable Import Release  
**Status**: ✅ READY FOR RELEASE  
**Confidence**: High - All OSS tests passing consistently (see workflow #147, #779, #91)

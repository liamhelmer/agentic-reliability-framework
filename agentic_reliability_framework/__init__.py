"""
Agentic Reliability Framework (ARF)
Production-grade multi-agent AI for reliability monitoring
"""

from typing import Any, TYPE_CHECKING

from .__version__ import __version__  # runtime: provide package version

__all__ = [
    "__version__",
    "EnhancedReliabilityEngine",
    "SimplePredictiveEngine",
    "BusinessImpactCalculator",
    "AdvancedAnomalyDetector",
    "create_enhanced_ui",
    "get_engine",
    "get_agents",
    "get_faiss_index",
    "get_business_metrics",
    "enhanced_engine",
]

# --- For static analyzers only: declare the names so mypy/ruff see them. ---
# We intentionally *do not* import concrete implementations here because
# runtime imports are lazy (PEP 562) via __getattr__ below.
# Mark these as Any to avoid hard coupling to module layout during static checks.
if TYPE_CHECKING:  # pragma: no cover
    EnhancedReliabilityEngine: Any
    SimplePredictiveEngine: Any
    BusinessImpactCalculator: Any
    AdvancedAnomalyDetector: Any
    create_enhanced_ui: Any
    get_engine: Any
    get_agents: Any
    get_faiss_index: Any
    get_business_metrics: Any
    enhanced_engine: Any

# --- Lazy runtime imports (PEP 562) ---
def __getattr__(name: str):
    # Classes / functions from app.py
    if name == "EnhancedReliabilityEngine":
        from .app import EnhancedReliabilityEngine  # local import
        return EnhancedReliabilityEngine
    if name == "SimplePredictiveEngine":
        from .app import SimplePredictiveEngine
        return SimplePredictiveEngine
    if name == "BusinessImpactCalculator":
        from .app import BusinessImpactCalculator
        return BusinessImpactCalculator
    if name == "AdvancedAnomalyDetector":
        from .app import AdvancedAnomalyDetector
        return AdvancedAnomalyDetector
    if name == "create_enhanced_ui":
        from .app import create_enhanced_ui
        return create_enhanced_ui

    # Items implemented in lazy.py
    if name in {
        "get_engine",
        "get_agents",
        "get_faiss_index",
        "get_business_metrics",
        "enhanced_engine",
    }:
        from .lazy import (
            enhanced_engine,
            get_agents,
            get_engine,
            get_faiss_index,
            get_business_metrics,
        )

        if name == "get_engine":
            return get_engine
        if name == "get_agents":
            return get_agents
        if name == "get_faiss_index":
            return get_faiss_index
        if name == "get_business_metrics":
            return get_business_metrics
        if name == "enhanced_engine":
            return enhanced_engine

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    # Improve autocompletion: list module globals + public API names.
    return sorted(set(list(globals().keys()) + list(__all__)))

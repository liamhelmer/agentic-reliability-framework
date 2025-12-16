# Standard imports
from __future__ import annotations
import asyncio
from typing import List, Dict, Any

# Project imports
from agentic_reliability_framework.memory.rag_graph import RAGGraphMemory
from agentic_reliability_framework.mcp.server import MCPServer
from agentic_reliability_framework.policy.actions import HealingAction  # <-- Fixed import

# Other imports if needed
# from agentic_reliability_framework.models import ReliabilityEvent, ToolResult, etc.

class V3ReliabilityEngine:
    """Enhanced engine with learning capability"""

    def __init__(self, rag_graph: RAGGraphMemory, mcp_server: MCPServer):
        self.rag = rag_graph
        self.mcp = mcp_server

    async def process_event_enhanced(self, event, *args, **kwargs):
        """Process a reliability event with RAG + MCP enhancements"""
        # Original v2 analysis
        result = await self._v2_process(event, *args, **kwargs)

        if result["status"] != "ANOMALY":
            return result

        # RAG retrieval
        similar_incidents = self.rag.find_similar(query_event=event, k=3)

        # Enhance policy decision
        enhanced_policy_input = {
            "current_event": event,
            "similar_past_incidents": similar_incidents,
            "outcome_statistics": self._calculate_outcome_stats(similar_incidents),
        }

        healing_actions: List[HealingAction] = self.policy_engine.evaluate_with_context(
            enhanced_policy_input
        )

        # MCP execution
        mcp_results = []
        for action in healing_actions:
            mcp_request = self._create_mcp_request(
                action=action,
                event=event,
                historical_context=similar_incidents,
            )

            mcp_response = await self.mcp.execute_tool(mcp_request)
            mcp_results.append(mcp_response)

            # Outcome recording
            if getattr(mcp_response, "executed", False):
                outcome = await self._record_outcome(
                    incident_id=result["incident_id"],
                    action=action,
                    mcp_response=mcp_response,
                )
                self.rag.store_outcome(outcome)

        # Update result
        result["rag_context"] = {
            "similar_incidents_count": len(similar_incidents),
            "most_effective_past_action": self._get_most_effective_action(similar_incidents),
        }
        result["mcp_execution"] = mcp_results

        return result

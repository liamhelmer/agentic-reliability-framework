"""
RAG Graph Memory: Bridge between FAISS vectors and structured knowledge

Phase 1: RAG Graph Foundation (2-3 weeks)
Goal: Make memory useful - retrieval before execution
"""

import numpy as np  # noqa: F401  # Keep for future use according to roadmap
import threading
import logging
import hashlib
import json
from typing import Dict, List, Optional, Any  # Removed Tuple (was unused)
from datetime import datetime
from collections import OrderedDict

from .faiss_index import ProductionFAISSIndex
from .models import (
    IncidentNode, OutcomeNode, GraphEdge, 
    SimilarityResult, EdgeType
)
from .constants import MemoryConstants
from ..models import ReliabilityEvent

logger = logging.getLogger(__name__)


class RAGGraphMemory:
    """
    Bridge between FAISS vectors and structured knowledge
    
    Technical Decisions:
    - Start with in-memory graph (simple dicts) before database
    - FAISS must expose search - already implemented in ProductionFAISSIndex
    - Incident IDs must be deterministic for idempotency
    """
    
    def __init__(self, faiss_index: ProductionFAISSIndex):
        """
        Initialize RAG Graph Memory
        
        Args:
            faiss_index: ProductionFAISSIndex instance with search capability
        """
        self.faiss = faiss_index
        self.incident_nodes: Dict[str, IncidentNode] = {}  # In-memory first
        self.outcome_nodes: Dict[str, OutcomeNode] = {}
        self.edges: List[GraphEdge] = []
        self._lock = threading.RLock()
        self._stats = {
            "total_incidents": 0,
            "total_outcomes": 0,
            "total_edges": 0,
            "similarity_searches": 0,
            "cache_hits": 0,
            "last_search_time": None
        }
        
        # LRU cache for similarity results
        self._similarity_cache: OrderedDict[str, List[SimilarityResult]] = OrderedDict()
        self._max_cache_size = MemoryConstants.GRAPH_CACHE_SIZE
        
        logger.info(
            f"Initialized RAGGraphMemory with FAISS index, "
            f"max_cache={self._max_cache_size}, "
            f"similarity_threshold={MemoryConstants.SIMILARITY_THRESHOLD}"
        )
    
    def is_enabled(self) -> bool:
        """Check if RAG graph is enabled and ready"""
        return len(self.incident_nodes) > 0 or self.faiss.get_count() > 0
    
    def _generate_incident_id(self, event: ReliabilityEvent) -> str:
        """
        Generate deterministic incident ID for idempotency
        
        Args:
            event: ReliabilityEvent to generate ID for
            
        Returns:
            Deterministic incident ID
        """
        # Create fingerprint from event data
        fingerprint_data = f"{event.component}:{event.latency_p99}:{event.error_rate}:{event.timestamp.isoformat()}"
        fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()
        
        # Return with prefix for readability
        return f"inc_{fingerprint[:16]}"
    
    def _generate_outcome_id(self, incident_id: str, action_hash: str) -> str:
        """Generate outcome ID"""
        data = f"{incident_id}:{action_hash}:{datetime.now().isoformat()}"
        return f"out_{hashlib.sha256(data.encode()).hexdigest()[:16]}"
    
    def _generate_edge_id(self, source_id: str, target_id: str, edge_type: EdgeType) -> str:
        """Generate edge ID"""
        data = f"{source_id}:{target_id}:{edge_type.value}:{datetime.now().isoformat()}"
        return f"edge_{hashlib.sha256(data.encode()).hexdigest()[:16]}"
    
    def store_incident(self, event: ReliabilityEvent, analysis: Dict[str, Any]) -> str:
        """
        Convert event+analysis to IncidentNode and store in graph
        
        Args:
            event: ReliabilityEvent to store
            analysis: Agent analysis results
            
        Returns:
            incident_id: Generated incident ID
        """
        incident_id = self._generate_incident_id(event)
        
        with self._lock:
            # Check if already exists
            if incident_id in self.incident_nodes:
                logger.debug(f"Incident {incident_id} already exists, skipping")
                return incident_id
            
            # Create IncidentNode
            node = IncidentNode(
                incident_id=incident_id,
                component=event.component,
                severity=event.severity.value,
                timestamp=event.timestamp.isoformat(),
                metrics={
                    "latency_ms": event.latency_p99,
                    "error_rate": event.error_rate,
                    "throughput": event.throughput,
                    "cpu_util": event.cpu_util if event.cpu_util else 0.0,
                    "memory_util": event.memory_util if event.memory_util else 0.0
                },
                agent_analysis=analysis,
                metadata={
                    "revenue_impact": event.revenue_impact,
                    "user_impact": event.user_impact,
                    "upstream_deps": event.upstream_deps,
                    "downstream_deps": event.downstream_deps,
                    "service_mesh": event.service_mesh
                }
            )
            
            # Store in memory
            self.incident_nodes[incident_id] = node
            self._stats["total_incidents"] += 1
            
            logger.info(
                f"Stored incident {incident_id} in RAG graph: {event.component}, "
                f"severity={event.severity.value}, metrics={node.metrics}"
            )
            
            # Evict oldest if at capacity
            if len(self.incident_nodes) > MemoryConstants.MAX_INCIDENT_NODES:
                oldest_id = next(iter(self.incident_nodes))
                del self.incident_nodes[oldest_id]
                logger.debug(f"Evicted oldest incident {oldest_id} from cache")
            
            return incident_id
    
    def store_outcome(self, outcome_node: OutcomeNode) -> str:
        """
        Store outcome node and connect to incident
        
        Args:
            outcome_node: OutcomeNode to store
            
        Returns:
            outcome_id: Generated outcome ID
        """
        with self._lock:
            # Check if incident exists
            if outcome_node.incident_id not in self.incident_nodes:
                logger.warning(
                    f"Cannot store outcome for non-existent incident: {outcome_node.incident_id}"
                )
                return outcome_node.outcome_id
            
            # Store outcome
            self.outcome_nodes[outcome_node.outcome_id] = outcome_node
            self._stats["total_outcomes"] += 1
            
            # Create edge from incident to outcome
            edge = GraphEdge(
                edge_id=self._generate_edge_id(
                    outcome_node.incident_id,
                    outcome_node.outcome_id,
                    EdgeType.RESOLVED_BY
                ),
                source_id=outcome_node.incident_id,
                target_id=outcome_node.outcome_id,
                edge_type=EdgeType.RESOLVED_BY,
                weight=1.0,
                metadata={
                    "success": outcome_node.success,
                    "resolution_time": outcome_node.resolution_time_minutes
                }
            )
            
            self.edges.append(edge)
            self._stats["total_edges"] += 1
            
            # Evict oldest if at capacity
            if len(self.outcome_nodes) > MemoryConstants.MAX_OUTCOME_NODES:
                oldest_id = next(iter(self.outcome_nodes))
                del self.outcome_nodes[oldest_id]
                logger.debug(f"Evicted oldest outcome {oldest_id} from cache")
            
            logger.info(
                f"Stored outcome {outcome_node.outcome_id} for incident {outcome_node.incident_id}: "
                f"success={outcome_node.success}, time={outcome_node.resolution_time_minutes}min"
            )
            
            return outcome_node.outcome_id
    
    def find_similar(self, query_event: ReliabilityEvent, k: int = 5) -> List[IncidentNode]:
        """
        Semantic search + graph expansion
        
        Args:
            query_event: Event to find similar incidents for
            k: Number of similar incidents to return
            
        Returns:
            List of similar IncidentNodes with expanded outcomes
        """
        cache_key = f"{query_event.component}:{query_event.latency_p99}:{query_event.error_rate}"
        
        with self._lock:
            # Check cache first
            if cache_key in self._similarity_cache:
                self._stats["cache_hits"] += 1
                self._similarity_cache.move_to_end(cache_key)  # Mark as recently used
                cached_results = self._similarity_cache[cache_key]
                
                # Convert SimilarityResult to IncidentNode
                incidents = [result.incident_node for result in cached_results[:k]]
                logger.debug(f"Cache hit for {cache_key}, returning {len(incidents)} incidents")
                return incidents
        
        try:
            # 1. FAISS similarity search
            query_text = (
                f"{query_event.component} latency {query_event.latency_p99}ms "
                f"error {query_event.error_rate:.3f}"
            )
            
            # Use existing FAISS search
            similar_incidents = []
            
            # Try async search first
            try:
                import asyncio
                loop = asyncio.get_event_loop()
                faiss_results = loop.run_until_complete

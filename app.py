"""
Enterprise Agentic Reliability Framework - Main Application
Multi-Agent AI System for Production Reliability Monitoring

This module provides the complete reliability monitoring system including:
- Multi-agent anomaly detection and root cause analysis
- Predictive analytics and forecasting
- Policy-based auto-healing
- Business impact quantification
- Vector-based incident memory
- Adaptive thresholds
- Thread-safe concurrent operations
"""

import os
import json
import numpy as np
import gradio as gr
import requests
import pandas as pd
import datetime
import threading
import logging
from typing import List, Dict, Any, Optional, Tuple
from collections import deque
from dataclasses import dataclass, asdict
import hashlib
import asyncio
from enum import Enum

# Import our modules
from models import ReliabilityEvent, EventSeverity, AnomalyResult, HealingAction
from healing_policies import PolicyEngine

# === Logging Configuration ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# === Configuration ===
class Config:
    """Centralized configuration for the reliability framework"""
    HF_TOKEN: str = os.getenv("HF_TOKEN", "").strip()
    HF_API_URL: str = "https://router.huggingface.co/hf-inference/v1/completions"
    
    # Vector storage
    VECTOR_DIM: int = 384
    INDEX_FILE: str = "incident_vectors.index"
    TEXTS_FILE: str = "incident_texts.json"
    
    # Thresholds
    LATENCY_WARNING: float = 150.0
    LATENCY_CRITICAL: float = 300.0
    LATENCY_EXTREME: float = 500.0
    ERROR_RATE_WARNING: float = 0.05
    ERROR_RATE_HIGH: float = 0.15
    ERROR_RATE_CRITICAL: float = 0.3
    CPU_WARNING: float = 0.8
    CPU_CRITICAL: float = 0.9
    MEMORY_WARNING: float = 0.8
    MEMORY_CRITICAL: float = 0.9
    
    # Performance
    HISTORY_WINDOW: int = 50
    MAX_EVENTS_STORED: int = 1000
    AGENT_TIMEOUT: int = 10
    CACHE_EXPIRY_MINUTES: int = 15
    
    # Business metrics
    BASE_REVENUE_PER_MINUTE: float = 100.0
    BASE_USERS: int = 1000

config = Config()

HEADERS = {"Authorization": f"Bearer {config.HF_TOKEN}"} if config.HF_TOKEN else {}

# === Thread-Safe Data Structures ===
class ThreadSafeEventStore:
    """Thread-safe storage for reliability events"""
    
    def __init__(self, max_size: int = config.MAX_EVENTS_STORED):
        self._events = deque(maxlen=max_size)
        self._lock = threading.RLock()
        logger.info(f"Initialized ThreadSafeEventStore with max_size={max_size}")
    
    def add(self, event: ReliabilityEvent) -> None:
        """Add event to store"""
        with self._lock:
            self._events.append(event)
            logger.debug(f"Added event for {event.component}: {event.severity.value}")
    
    def get_recent(self, n: int = 15) -> List[ReliabilityEvent]:
        """Get n most recent events"""
        with self._lock:
            return list(self._events)[-n:] if self._events else []
    
    def get_all(self) -> List[ReliabilityEvent]:
        """Get all events"""
        with self._lock:
            return list(self._events)
    
    def count(self) -> int:
        """Get total event count"""
        with self._lock:
            return len(self._events)

class ThreadSafeFAISSIndex:
    """Thread-safe wrapper for FAISS index operations with batching"""
    
    def __init__(self, index, texts: List[str]):
        self.index = index
        self.texts = texts
        self._lock = threading.RLock()
        self.last_save = datetime.datetime.now()
        self.save_interval = datetime.timedelta(seconds=30)
        self.pending_vectors = []
        self.pending_texts = []
        logger.info(f"Initialized ThreadSafeFAISSIndex with {len(texts)} existing vectors")
    
    def add(self, vector: np.ndarray, text: str) -> None:
        """Add vector and text with batching"""
        with self._lock:
            self.pending_vectors.append(vector)
            self.pending_texts.append(text)
            
            # Flush if we have enough pending
            if len(self.pending_vectors) >= 10:
                self._flush()
    
    def _flush(self) -> None:
        """Flush pending vectors to index"""
        if not self.pending_vectors:
            return
        
        try:
            vectors = np.vstack(self.pending_vectors)
            self.index.add(vectors)
            self.texts.extend(self.pending_texts)
            
            logger.info(f"Flushed {len(self.pending_vectors)} vectors to FAISS index")
            
            self.pending_vectors = []
            self.pending_texts = []
            
            # Save if enough time has passed
            if datetime.datetime.now() - self.last_save > self.save_interval:
                self._save()
        except Exception as e:
            logger.error(f"Error flushing vectors: {e}", exc_info=True)
    
    def _save(self) -> None:
        """Save index to disk"""
        try:
            import faiss
            faiss.write_index(self.index, config.INDEX_FILE)
            with open(config.TEXTS_FILE, "w") as f:
                json.dump(self.texts, f)
            self.last_save = datetime.datetime.now()
            logger.info(f"Saved FAISS index with {len(self.texts)} vectors")
        except Exception as e:
            logger.error(f"Error saving index: {e}", exc_info=True)
    
    def get_count(self) -> int:
        """Get total count of vectors"""
        with self._lock:
            return len(self.texts) + len(self.pending_texts)
    
    def force_save(self) -> None:
        """Force immediate save of pending vectors"""
        with self._lock:
            self._flush()

# === FAISS & Embeddings Setup ===
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    
    logger.info("Loading SentenceTransformer model...")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    logger.info("SentenceTransformer model loaded successfully")
    
    if os.path.exists(config.INDEX_FILE):
        logger.info(f"Loading existing FAISS index from {config.INDEX_FILE}")
        index = faiss.read_index(config.INDEX_FILE)
        
        # Validate dimension
        if index.d != config.VECTOR_DIM:
            logger.warning(f"Index dimension mismatch: {index.d} != {config.VECTOR_DIM}. Creating new index.")
            index = faiss.IndexFlatL2(config.VECTOR_DIM)
            incident_texts = []
        else:
            with open(config.TEXTS_FILE, "r") as f:
                incident_texts = json.load(f)
            logger.info(f"Loaded {len(incident_texts)} incident texts")
    else:
        logger.info("Creating new FAISS index")
        index = faiss.IndexFlatL2(config.VECTOR_DIM)
        incident_texts = []
    
    thread_safe_index = ThreadSafeFAISSIndex(index, incident_texts)
    
except ImportError as e:
    logger.warning(f"FAISS or SentenceTransformers not available: {e}")
    index = None
    incident_texts = []
    model = None
    thread_safe_index = None
except Exception as e:
    logger.error(f"Error initializing FAISS: {e}", exc_info=True)
    index = None
    incident_texts = []
    model = None
    thread_safe_index = None

# === Predictive Models ===
@dataclass
class ForecastResult:
    """Data class for forecast results"""
    metric: str
    predicted_value: float
    confidence: float
    trend: str  # "increasing", "decreasing", "stable"
    time_to_threshold: Optional[datetime.timedelta] = None
    risk_level: str = "low"  # low, medium, high, critical

class SimplePredictiveEngine:
    """
    Lightweight forecasting engine optimized for Hugging Face Spaces.
    Uses statistical methods for time-series prediction.
    """
    
    def __init__(self, history_window: int = config.HISTORY_WINDOW):
        self.history_window = history_window
        self.service_history: Dict[str, deque] = {}
        self.prediction_cache: Dict[str, Tuple[ForecastResult, datetime.datetime]] = {}
        self.max_cache_age = datetime.timedelta(minutes=config.CACHE_EXPIRY_MINUTES)
        self._lock = threading.RLock()
        logger.info(f"Initialized SimplePredictiveEngine with history_window={history_window}")
    
    def add_telemetry(self, service: str, event_data: Dict) -> None:
        """
        Add telemetry data to service history
        
        Args:
            service: Service name
            event_data: Dictionary containing metrics (latency_p99, error_rate, etc.)
        """
        with self._lock:
            if service not in self.service_history:
                self.service_history[service] = deque(maxlen=self.history_window)
            
            telemetry_point = {
                'timestamp': datetime.datetime.now(),
                'latency': event_data.get('latency_p99', 0),
                'error_rate': event_data.get('error_rate', 0),
                'throughput': event_data.get('throughput', 0),
                'cpu_util': event_data.get('cpu_util'),
                'memory_util': event_data.get('memory_util')
            }
            
            self.service_history[service].append(telemetry_point)
            
            # Clean expired cache
            self._clean_cache()
    
    def _clean_cache(self) -> None:
        """Remove expired entries from prediction cache"""
        now = datetime.datetime.now()
        expired = [k for k, (_, ts) in self.prediction_cache.items() 
                   if now - ts > self.max_cache_age]
        for k in expired:
            del self.prediction_cache[k]
        
        if expired:
            logger.debug(f"Cleaned {len(expired)} expired cache entries")
    
    def forecast_service_health(self, service: str, lookahead_minutes: int = 15) -> List[ForecastResult]:
        """
        Forecast service health metrics
        
        Args:
            service: Service name to forecast
            lookahead_minutes: Time horizon in minutes
            
        Returns:
            List of forecast results for different metrics
        """
        with self._lock:
            if service not in self.service_history or len(self.service_history[service]) < 10:
                return []
            
            history = list(self.service_history[service])
        
        forecasts = []
        
        # Forecast latency
        latency_forecast = self._forecast_latency(history, lookahead_minutes)
        if latency_forecast:
            forecasts.append(latency_forecast)
        
        # Forecast error rate
        error_forecast = self._forecast_error_rate(history, lookahead_minutes)
        if error_forecast:
            forecasts.append(error_forecast)
        
        # Forecast resource utilization
        resource_forecasts = self._forecast_resources(history, lookahead_minutes)
        forecasts.extend(resource_forecasts)
        
        # Cache results
        with self._lock:
            for forecast in forecasts:
                cache_key = f"{service}_{forecast.metric}"
                self.prediction_cache[cache_key] = (forecast, datetime.datetime.now())
        
        return forecasts
    
    def _forecast_latency(self, history: List, lookahead_minutes: int) -> Optional[ForecastResult]:
        """
        Forecast latency using linear regression and trend analysis
        
        Args:
            history: Historical telemetry data
            lookahead_minutes: Forecast horizon
            
        Returns:
            ForecastResult or None if insufficient data
        """
        try:
            latencies = [point['latency'] for point in history[-20:]]
            
            if len(latencies) < 5:
                return None
            
            # Simple linear trend
            x = np.arange(len(latencies))
            slope, intercept = np.polyfit(x, latencies, 1)
            
            # Predict next value
            next_x = len(latencies)
            predicted_latency = slope * next_x + intercept
            
            # Calculate confidence based on data quality
            residuals = latencies - (slope * x + intercept)
            confidence = max(0, 1 - (np.std(residuals) / max(1, np.mean(latencies))))
            
            # Determine trend and risk
            if slope > 5:
                trend = "increasing"
                risk = "critical" if predicted_latency > config.LATENCY_EXTREME else "high"
            elif slope < -2:
                trend = "decreasing" 
                risk = "low"
            else:
                trend = "stable"
                risk = "low" if predicted_latency < config.LATENCY_WARNING else "medium"
            
            # Calculate time to reach critical threshold (500ms)
            time_to_critical = None
            if slope > 0 and predicted_latency < config.LATENCY_EXTREME:
                denominator = predicted_latency - latencies[-1]
                if abs(denominator) > 0.1:  # Avoid division by very small numbers
                    minutes_to_critical = lookahead_minutes * (config.LATENCY_EXTREME - predicted_latency) / denominator
                    if minutes_to_critical > 0:
                        time_to_critical = datetime.timedelta(minutes=minutes_to_critical)
            
            return ForecastResult(
                metric="latency",
                predicted_value=predicted_latency,
                confidence=confidence,
                trend=trend,
                time_to_threshold=time_to_critical,
                risk_level=risk
            )
            
        except Exception as e:
            logger.error(f"Latency forecast error: {e}", exc_info=True)
            return None
    
    def _forecast_error_rate(self, history: List, lookahead_minutes: int) -> Optional[ForecastResult]:
        """
        Forecast error rate using exponential smoothing
        
        Args:
            history: Historical telemetry data
            lookahead_minutes: Forecast horizon
            
        Returns:
            ForecastResult or None if insufficient data
        """
        try:
            error_rates = [point['error_rate'] for point in history[-15:]]
            
            if len(error_rates) < 5:
                return None
            
            # Exponential smoothing
            alpha = 0.3
            forecast = error_rates[0]
            for rate in error_rates[1:]:
                forecast = alpha * rate + (1 - alpha) * forecast
            
            predicted_rate = forecast
            
            # Trend analysis
            recent_trend = np.mean(error_rates[-3:]) - np.mean(error_rates[-6:-3])
            
            if recent_trend > 0.02:
                trend = "increasing"
                risk = "critical" if predicted_rate > config.ERROR_RATE_CRITICAL else "high"
            elif recent_trend < -0.01:
                trend = "decreasing"
                risk = "low"
            else:
                trend = "stable"
                risk = "low" if predicted_rate < config.ERROR_RATE_WARNING else "medium"
            
            # Confidence based on volatility
            confidence = max(0, 1 - (np.std(error_rates) / max(0.01, np.mean(error_rates))))
            
            return ForecastResult(
                metric="error_rate",
                predicted_value=predicted_rate,
                confidence=confidence,
                trend=trend,
                risk_level=risk
            )
            
        except Exception as e:
            logger.error(f"Error rate forecast error: {e}", exc_info=True)
            return None
    
    def _forecast_resources(self, history: List, lookahead_minutes: int) -> List[ForecastResult]:
        """
        Forecast CPU and memory utilization
        
        Args:
            history: Historical telemetry data
            lookahead_minutes: Forecast horizon
            
        Returns:
            List of forecast results for CPU and memory
        """
        forecasts = []
        
        # CPU forecast
        cpu_values = [point['cpu_util'] for point in history if point.get('cpu_util') is not None]
        if len(cpu_values) >= 5:
            try:
                predicted_cpu = np.mean(cpu_values[-5:])
                trend = "increasing" if cpu_values[-1] > np.mean(cpu_values[-10:-5]) else "stable"
                
                risk = "low"
                if predicted_cpu > config.CPU_CRITICAL:
                    risk = "critical"
                elif predicted_cpu > config.CPU_WARNING:
                    risk = "high"
                elif predicted_cpu > 0.7:
                    risk = "medium"
                
                forecasts.append(ForecastResult(
                    metric="cpu_util",
                    predicted_value=predicted_cpu,
                    confidence=0.7,
                    trend=trend,
                    risk_level=risk
                ))
            except Exception as e:
                logger.error(f"CPU forecast error: {e}", exc_info=True)
        
        # Memory forecast
        memory_values = [point['memory_util'] for point in history if point.get('memory_util') is not None]
        if len(memory_values) >= 5:
            try:
                predicted_memory = np.mean(memory_values[-5:])
                trend = "increasing" if memory_values[-1] > np.mean(memory_values[-10:-5]) else "stable"
                
                risk = "low"
                if predicted_memory > config.MEMORY_CRITICAL:
                    risk = "critical"
                elif predicted_memory > config.MEMORY_WARNING:
                    risk = "high"
                elif predicted_memory > 0.7:
                    risk = "medium"
                
                forecasts.append(ForecastResult(
                    metric="memory_util",
                    predicted_value=predicted_memory,
                    confidence=0.7,
                    trend=trend,
                    risk_level=risk
                ))
            except Exception as e:
                logger.error(f"Memory forecast error: {e}", exc_info=True)
        
        return forecasts
    
    def get_predictive_insights(self, service: str) -> Dict[str, Any]:
        """
        Generate actionable insights from forecasts
        
        Args:
            service: Service name
            
        Returns:
            Dictionary containing warnings, recommendations, and forecast data
        """
        forecasts = self.forecast_service_health(service)
        
        critical_risks = [f for f in forecasts if f.risk_level in ["high", "critical"]]
        warnings = []
        recommendations = []
        
        for forecast in critical_risks:
            if forecast.metric == "latency" and forecast.risk_level in ["high", "critical"]:
                warnings.append(f"📈 Latency expected to reach {forecast.predicted_value:.0f}ms")
                if forecast.time_to_threshold:
                    minutes = int(forecast.time_to_threshold.total_seconds() / 60)
                    recommendations.append(f"⏰ Critical latency (~500ms) in ~{minutes} minutes")
                recommendations.append("🔧 Consider scaling or optimizing dependencies")
            
            elif forecast.metric == "error_rate" and forecast.risk_level in ["high", "critical"]:
                warnings.append(f"🚨 Errors expected to reach {forecast.predicted_value*100:.1f}%")
                recommendations.append("🐛 Investigate recent deployments or dependency issues")
            
            elif forecast.metric == "cpu_util" and forecast.risk_level in ["high", "critical"]:
                warnings.append(f"🔥 CPU expected at {forecast.predicted_value*100:.1f}%")
                recommendations.append("⚡ Consider scaling compute resources")
            
            elif forecast.metric == "memory_util" and forecast.risk_level in ["high", "critical"]:
                warnings.append(f"💾 Memory expected at {forecast.predicted_value*100:.1f}%")
                recommendations.append("🧹 Check for memory leaks or optimize usage")
        
        return {
            'service': service,
            'forecasts': [asdict(f) for f in forecasts],
            'warnings': warnings[:3],
            'recommendations': list(dict.fromkeys(recommendations))[:3],
            'critical_risk_count': len(critical_risks),
            'forecast_timestamp': datetime.datetime.now().isoformat()
        }

# === Core Engine Components ===
policy_engine = PolicyEngine()
events_history_store = ThreadSafeEventStore()
predictive_engine = SimplePredictiveEngine()

class BusinessImpactCalculator:
    """
    Calculate business impact of anomalies including revenue loss
    and user impact estimation
    """
    
    def __init__(self, revenue_per_request: float = 0.01):
        self.revenue_per_request = revenue_per_request
        logger.info(f"Initialized BusinessImpactCalculator with revenue_per_request={revenue_per_request}")
    
    def calculate_impact(self, event: ReliabilityEvent, duration_minutes: int = 5) -> Dict[str, Any]:
        """
        Calculate business impact for a reliability event
        
        Args:
            event: The reliability event to analyze
            duration_minutes: Assumed duration of the incident
            
        Returns:
            Dictionary containing revenue loss, user impact, and severity
        """
        base_revenue_per_minute = config.BASE_REVENUE_PER_MINUTE
        
        impact_multiplier = 1.0
        
        # Impact factors
        if event.latency_p99 > config.LATENCY_CRITICAL:
            impact_multiplier += 0.5
        if event.error_rate > 0.1:
            impact_multiplier += 0.8
        if event.cpu_util and event.cpu_util > config.CPU_CRITICAL:
            impact_multiplier += 0.3
        
        revenue_loss = base_revenue_per_minute * impact_multiplier * (duration_minutes / 60)
        
        base_users_affected = config.BASE_USERS
        user_impact_multiplier = (event.error_rate * 10) + (max(0, event.latency_p99 - 100) / 500)
        affected_users = int(base_users_affected * user_impact_multiplier)
        
        # Severity classification
        if revenue_loss > 500 or affected_users > 5000:
            severity = "CRITICAL"
        elif revenue_loss > 100 or affected_users > 1000:
            severity = "HIGH"
        elif revenue_loss > 50 or affected_users > 500:
            severity = "MEDIUM"
        else:
            severity = "LOW"
        
        logger.info(f"Business impact: ${revenue_loss:.2f} revenue loss, {affected_users} users, {severity} severity")
        
        return {
            'revenue_loss_estimate': round(revenue_loss, 2),
            'affected_users_estimate': affected_users,
            'severity_level': severity,
            'throughput_reduction_pct': round(min(100, user_impact_multiplier * 100), 1)
        }

business_calculator = BusinessImpactCalculator()

class AdvancedAnomalyDetector:
    """
    Enhanced anomaly detection with adaptive thresholds that learn
    from historical data patterns
    """
    
    def __init__(self):
        self.historical_data = deque(maxlen=100)
        self.adaptive_thresholds = {
            'latency_p99': config.LATENCY_WARNING,
            'error_rate': config.ERROR_RATE_WARNING
        }
        self._lock = threading.RLock()
        logger.info("Initialized AdvancedAnomalyDetector")
    
    def detect_anomaly(self, event: ReliabilityEvent) -> bool:
        """
        Detect if event is anomalous using adaptive thresholds
        
        Args:
            event: The reliability event to check
            
        Returns:
            True if anomaly detected, False otherwise
        """
        with self._lock:
            latency_anomaly = event.latency_p99 > self.adaptive_thresholds['latency_p99']
            error_anomaly = event.error_rate > self.adaptive_thresholds['error_rate']
            
            resource_anomaly = False
            if event.cpu_util and event.cpu_util > config.CPU_CRITICAL:
                resource_anomaly = True
            if event.memory_util and event.memory_util > config.MEMORY_CRITICAL:
                resource_anomaly = True
            
            self._update_thresholds(event)
            
            is_anomaly = latency_anomaly or error_anomaly or resource_anomaly
            
            if is_anomaly:
                logger.info(f"Anomaly detected for {event.component}: latency={latency_anomaly}, error={error_anomaly}, resource={resource_anomaly}")
            
            return is_anomaly
    
    def _update_thresholds(self, event: ReliabilityEvent) -> None:
        """Update adaptive thresholds based on historical data"""
        self.historical_data.append(event)
        
        if len(self.historical_data) > 10:
            recent_latencies = [e.latency_p99 for e in list(self.historical_data)[-20:]]
            new_threshold = np.percentile(recent_latencies, 90)
            self.adaptive_thresholds['latency_p99'] = new_threshold
            logger.debug(f"Updated adaptive latency threshold to {new_threshold:.2f}ms")

anomaly_detector = AdvancedAnomalyDetector()

# === Multi-Agent System ===
class AgentSpecialization(Enum):
    """Agent specialization types"""
    DETECTIVE = "anomaly_detection"
    DIAGNOSTICIAN = "root_cause_analysis"
    PREDICTIVE = "predictive_analytics"

class BaseAgent:
    """Base class for all specialized agents"""
    
    def __init__(self, specialization: AgentSpecialization):
        self.specialization = specialization
        self.performance_metrics = {
            'processed_events': 0,
            'successful_analyses': 0,
            'average_confidence': 0.0
        }
    
    async def analyze(self, event: ReliabilityEvent) -> Dict[str, Any]:
        """Base analysis method to be implemented by specialized agents"""
        raise NotImplementedError

class AnomalyDetectionAgent(BaseAgent):
    """
    Specialized agent for anomaly detection and pattern recognition.
    Calculates multi-dimensional anomaly scores and identifies affected metrics.
    """
    
    def __init__(self):
        super().__init__(AgentSpecialization.DETECTIVE)
        logger.info("Initialized AnomalyDetectionAgent")
    
    async def analyze(self, event: ReliabilityEvent) -> Dict[str, Any]:
        """
        Perform comprehensive anomaly analysis
        
        Args:
            event: Reliability event to analyze
            
        Returns:
            Dictionary containing anomaly score, severity, affected metrics, and recommendations
        """
        try:
            anomaly_score = self._calculate_anomaly_score(event)
            
            return {
                'specialization': self.specialization.value,
                'confidence': anomaly_score,
                'findings': {
                    'anomaly_score': anomaly_score,
                    'severity_tier': self._classify_severity(anomaly_score),
                    'primary_metrics_affected': self._identify_affected_metrics(event)
                },
                'recommendations': self._generate_detection_recommendations(event, anomaly_score)
            }
        except Exception as e:
            logger.error(f"AnomalyDetectionAgent error: {e}", exc_info=True)
            return {
                'specialization': self.specialization.value,
                'confidence': 0.0,
                'findings': {},
                'recommendations': [f"Analysis error: {str(e)}"]
            }
    
    def _calculate_anomaly_score(self, event: ReliabilityEvent) -> float:
        """
        Calculate comprehensive anomaly score (0-1) using weighted metrics
        
        Args:
            event: Reliability event
            
        Returns:
            Float between 0 and 1 representing anomaly severity
        """
        scores = []
        
        # Latency anomaly (weighted 40%)
        if event.latency_p99 > config.LATENCY_WARNING:
            latency_score = min(1.0, (event.latency_p99 - config.LATENCY_WARNING) / 500)
            scores.append(0.4 * latency_score)
        
        # Error rate anomaly (weighted 30%)
        if event.error_rate > config.ERROR_RATE_WARNING:
            error_score = min(1.0, event.error_rate / 0.3)
            scores.append(0.3 * error_score)
        
        # Resource anomaly (weighted 30%)
        resource_score = 0
        if event.cpu_util and event.cpu_util > config.CPU_WARNING:
            resource_score += 0.15 * min(1.0, (event.cpu_util - config.CPU_WARNING) / 0.2)
        if event.memory_util and event.memory_util > config.MEMORY_WARNING:
            resource_score += 0.15 * min(1.0, (event.memory_util - config.MEMORY_WARNING) / 0.2)
        scores.append(resource_score)
        
        return min(1.0, sum(scores))
    
    def _classify_severity(self, anomaly_score: float) -> str:
        """
        Classify severity tier based on anomaly score
        
        Args:
            anomaly_score: Score between 0 and 1
            
        Returns:
            Severity tier string (LOW, MEDIUM, HIGH, CRITICAL)
        """
        if anomaly_score > 0.8:
            return "CRITICAL"
        elif anomaly_score > 0.6:
            return "HIGH"
        elif anomaly_score > 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _identify_affected_metrics(self, event: ReliabilityEvent) -> List[Dict[str, Any]]:
        """
        Identify which metrics are outside normal ranges
        
        Args:
            event: Reliability event
            
        Returns:
            List of dictionaries describing affected metrics with severity
        """
        affected = []
        
        # Latency checks
        if event.latency_p99 > config.LATENCY_EXTREME:
            affected.append({
                "metric": "latency", 
                "value": event.latency_p99, 
                "severity": "CRITICAL", 
                "threshold": config.LATENCY_WARNING
            })
        elif event.latency_p99 > config.LATENCY_CRITICAL:
            affected.append({
                "metric": "latency", 
                "value": event.latency_p99, 
                "severity": "HIGH", 
                "threshold": config.LATENCY_WARNING
            })
        elif event.latency_p99 > config.LATENCY_WARNING:
            affected.append({
                "metric": "latency", 
                "value": event.latency_p99, 
                "severity": "MEDIUM", 
                "threshold": config.LATENCY_WARNING
            })
        
        # Error rate checks
        if event.error_rate > config.ERROR_RATE_CRITICAL:
            affected.append({
                "metric": "error_rate", 
                "value": event.error_rate, 
                "severity": "CRITICAL", 
                "threshold": config.ERROR_RATE_WARNING
            })
        elif event.error_rate > config.ERROR_RATE_HIGH:
            affected.append({
                "metric": "error_rate", 
                "value": event.error_rate, 
                "severity": "HIGH", 
                "threshold": config.ERROR_RATE_WARNING
            })
        elif event.error_rate > config.ERROR_RATE_WARNING:
            affected.append({
                "metric": "error_rate", 
                "value": event.error_rate, 
                "severity": "MEDIUM", 
                "threshold": config.ERROR_RATE_WARNING
            })
        
        # CPU checks
        if event.cpu_util and event.cpu_util > config.CPU_CRITICAL:
            affected.append({
                "metric": "cpu", 
                "value": event.cpu_util, 
                "severity": "CRITICAL", 
                "threshold": config.CPU_WARNING
            })
        elif event.cpu_util and event.cpu_util > config.CPU_WARNING:
            affected.append({
                "metric": "cpu", 
                "value": event.cpu_util, 
                "severity": "HIGH", 
                "threshold": config.CPU_WARNING
            })
        
        # Memory checks
        if event.memory_util and event.memory_util > config.MEMORY_CRITICAL:
            affected.append({
                "metric": "memory", 
                "value": event.memory_util, 
                "severity": "CRITICAL", 
                "threshold": config.MEMORY_WARNING
            })
        elif event.memory_util and event.memory_util > config.MEMORY_WARNING:
            affected.append({
                "metric": "memory", 
                "value": event.memory_util, 
                "severity": "HIGH", 
                "threshold": config.MEMORY_WARNING
            })
        
        return affected
    
    def _generate_detection_recommendations(self, event: ReliabilityEvent, anomaly_score: float) -> List[str]:
        """
        Generate actionable recommendations based on detected anomalies
        
        Args:
            event: Reliability event
            anomaly_score: Calculated anomaly score
            
        Returns:
            List of recommendation strings with emojis for visibility
        """
        recommendations = []
        affected_metrics = self._identify_affected_metrics(event)
        
        for metric in affected_metrics:
            metric_name = metric["metric"]
            severity = metric["severity"]
            value = metric["value"]
            threshold = metric["threshold"]
            
            if metric_name == "latency":
                if severity == "CRITICAL":
                    recommendations.append(
                        f"🚨 CRITICAL: Latency {value:.0f}ms (>{threshold}ms) - "
                        f"Check database & external dependencies"
                    )
                elif severity == "HIGH":
                    recommendations.append(
                        f"⚠️ HIGH: Latency {value:.0f}ms (>{threshold}ms) - "
                        f"Investigate service performance"
                    )
                else:
                    recommendations.append(
                        f"📈 Latency elevated: {value:.0f}ms (>{threshold}ms) - Monitor trend"
                    )
            
            elif metric_name == "error_rate":
                if severity == "CRITICAL":
                    recommendations.append(
                        f"🚨 CRITICAL: Error rate {value*100:.1f}% (>{threshold*100:.1f}%) - "
                        f"Check recent deployments"
                    )
                elif severity == "HIGH":
                    recommendations.append(
                        f"⚠️ HIGH: Error rate {value*100:.1f}% (>{threshold*100:.1f}%) - "
                        f"Review application logs"
                    )
                else:
                    recommendations.append(
                        f"📈 Errors increasing: {value*100:.1f}% (>{threshold*100:.1f}%)"
                    )
            
            elif metric_name == "cpu":
                recommendations.append(
                    f"🔥 CPU {severity}: {value*100:.1f}% utilization - Consider scaling"
                )
            
            elif metric_name == "memory":
                recommendations.append(
                    f"💾 Memory {severity}: {value*100:.1f}% utilization - Check for memory leaks"
                )
        
        # Overall severity recommendations
        if anomaly_score > 0.8:
            recommendations.append("🎯 IMMEDIATE ACTION REQUIRED: Multiple critical metrics affected")
        elif anomaly_score > 0.6:
            recommendations.append("🎯 INVESTIGATE: Significant performance degradation detected")
        elif anomaly_score > 0.4:
            recommendations.append("📊 MONITOR: Early warning signs detected")
        
        return recommendations[:4]  # Return top 4 recommendations

class RootCauseAgent(BaseAgent):
    """
    Specialized agent for root cause analysis.
    Analyzes failure patterns and provides investigation guidance.
    """
    
    def __init__(self):
        super().__init__(AgentSpecialization.DIAGNOSTICIAN)
        logger.info("Initialized RootCauseAgent")
    
    async def analyze(self, event: ReliabilityEvent) -> Dict[str, Any]:
        """
        Perform root cause analysis
        
        Args:
            event: Reliability event to analyze
            
        Returns:
            Dictionary containing likely root causes and investigation guidance
        """
        try:
            causes = self._analyze_potential_causes(event)
            
            return {
                'specialization': self.specialization.value,
                'confidence': 0.7,
                'findings': {
                    'likely_root_causes': causes,
                    'evidence_patterns': self._identify_evidence(event),
                    'investigation_priority': self._prioritize_investigation(causes)
                },
                'recommendations': [
                    f"Check {cause['cause']} for issues" for cause in causes[:2]
                ]
            }
        except Exception as e:
            logger.error(f"RootCauseAgent error: {e}", exc_info=True)
            return {
                'specialization': self.specialization.value,
                'confidence': 0.0,
                'findings': {},
                'recommendations': [f"Analysis error: {str(e)}"]
            }
    
    def _analyze_potential_causes(self, event: ReliabilityEvent) -> List[Dict[str, Any]]:
        """
        Analyze potential root causes based on event patterns
        
        Args:
            event: Reliability event
            
        Returns:
            List of potential root causes with confidence scores
        """
        causes = []
        
        # Pattern 1: Database/External Dependency Failure
        if event.latency_p99 > config.LATENCY_EXTREME and event.error_rate > 0.2:
            causes.append({
                "cause": "Database/External Dependency Failure",
                "confidence": 0.85,
                "evidence": f"Extreme latency ({event.latency_p99:.0f}ms) with high errors ({event.error_rate*100:.1f}%)",
                "investigation": "Check database connection pool, external API health"
            })
        
        # Pattern 2: Resource Exhaustion
        if (event.cpu_util and event.cpu_util > config.CPU_CRITICAL and 
            event.memory_util and event.memory_util > config.MEMORY_CRITICAL):
            causes.append({
                "cause": "Resource Exhaustion",
                "confidence": 0.90,
                "evidence": f"CPU ({event.cpu_util*100:.1f}%) and Memory ({event.memory_util*100:.1f}%) critically high",
                "investigation": "Check for memory leaks, infinite loops, insufficient resources"
            })
        
        # Pattern 3: Application Bug / Configuration Issue
        if event.error_rate > config.ERROR_RATE_CRITICAL and event.latency_p99 < 200:
            causes.append({
                "cause": "Application Bug / Configuration Issue",
                "confidence": 0.75,
                "evidence": f"High error rate ({event.error_rate*100:.1f}%) without latency impact",
                "investigation": "Review recent deployments, configuration changes, application logs"
            })
        
        # Pattern 4: Gradual Performance Degradation
        if (200 <= event.latency_p99 <= 400 and 
            config.ERROR_RATE_WARNING <= event.error_rate <= config.ERROR_RATE_HIGH):
            causes.append({
                "cause": "Gradual Performance Degradation",
                "confidence": 0.65,
                "evidence": f"Moderate latency ({event.latency_p99:.0f}ms) and errors ({event.error_rate*100:.1f}%)",
                "investigation": "Check resource trends, dependency performance, capacity planning"
            })
        
        # Default: Unknown pattern
        if not causes:
            causes.append({
                "cause": "Unknown - Requires Investigation",
                "confidence": 0.3,
                "evidence": "Pattern does not match known failure modes",
                "investigation": "Complete system review needed"
            })
        
        return causes
    
    def _identify_evidence(self, event: ReliabilityEvent) -> List[str]:
        """
        Identify evidence patterns in the event data
        
        Args:
            event: Reliability event
            
        Returns:
            List of evidence pattern identifiers
        """
        evidence = []
        
        if event.latency_p99 > event.error_rate * 1000:
            evidence.append("latency_disproportionate_to_errors")
        
        if (event.cpu_util and event.cpu_util > config.CPU_WARNING and 
            event.memory_util and event.memory_util > config.MEMORY_WARNING):
            evidence.append("correlated_resource_exhaustion")
        
        if event.error_rate > config.ERROR_RATE_HIGH and event.latency_p99 < config.LATENCY_CRITICAL:
            evidence.append("errors_without_latency_impact")
        
        return evidence
    
    def _prioritize_investigation(self, causes: List[Dict[str, Any]]) -> str:
        """
        Determine investigation priority based on identified causes
        
        Args:
            causes: List of potential root causes
            
        Returns:
            Priority level (HIGH, MEDIUM, LOW)
        """
        for cause in causes:
            if "Database" in cause["cause"] or "Resource Exhaustion" in cause["cause"]:
                return "HIGH"
        return "MEDIUM"

class PredictiveAgent(BaseAgent):
    """
    Specialized agent for predictive analytics.
    Forecasts future risks and trends using statistical models.
    """
    
    def __init__(self):
        super().__init__(AgentSpecialization.PREDICTIVE)
        self.engine = predictive_engine
        logger.info("Initialized PredictiveAgent")
    
    async def analyze(self, event: ReliabilityEvent) -> Dict[str, Any]:
        """
        Perform predictive analysis for future risks
        
        Args:
            event: Current reliability event
            
        Returns:
            Dictionary containing forecasts and predictive insights
        """
        try:
            event_data = {
                'latency_p99': event.latency_p99,
                'error_rate': event.error_rate,
                'throughput': event.throughput,
                'cpu_util': event.cpu_util,
                'memory_util': event.memory_util
            }
            self.engine.add_telemetry(event.component, event_data)
            
            insights = self.engine.get_predictive_insights(event.component)
            
            return {
                'specialization': self.specialization.value,
                'confidence': 0.8 if insights['critical_risk_count'] > 0 else 0.5,
                'findings': insights,
                'recommendations': insights['recommendations']
            }
        except Exception as e:
            logger.error(f"PredictiveAgent error: {e}", exc_info=True)
            return {
                'specialization': self.specialization.value,
                'confidence': 0.0,
                'findings': {},
                'recommendations': [f"Analysis error: {str(e)}"]
            }

class OrchestrationManager:
    """
    Orchestrates multiple specialized agents for comprehensive analysis.
    Runs agents in parallel and synthesizes their findings.
    """
    
    def __init__(self):
        self.agents = {
            AgentSpecialization.DETECTIVE: AnomalyDetectionAgent(),
            AgentSpecialization.DIAGNOSTICIAN: RootCauseAgent(),
            AgentSpecialization.PREDICTIVE: PredictiveAgent(),
        }
        logger.info(f"Initialized OrchestrationManager with {len(self.agents)} agents")
    
    async def orchestrate_analysis(self, event: ReliabilityEvent) -> Dict[str, Any]:
        """
        Coordinate multiple agents for comprehensive analysis
        
        Args:
            event: Reliability event to analyze
            
        Returns:
            Synthesized findings from all agents
        """
        agent_tasks = {
            spec: agent.analyze(event)
            for spec, agent in self.agents.items()
        }
        
        # Parallel agent execution with timeout protection
        agent_results = {}
        for specialization, task in agent_tasks.items():
            try:
                result = await asyncio.wait_for(task, timeout=5.0)
                agent_results[specialization.value] = result
                logger.debug(f"Agent {specialization.value} completed successfully")
            except asyncio.TimeoutError:
                logger.warning(f"Agent {specialization.value} timed out")
                continue
            except Exception as e:
                logger.error(f"Agent {specialization.value} error: {e}", exc_info=True)
                continue
        
        return self._synthesize_agent_findings(event, agent_results)
    
    def _synthesize_agent_findings(self, event: ReliabilityEvent, agent_results: Dict) -> Dict[str, Any]:
        """
        Combine insights from all specialized agents
        
        Args:
            event: Original reliability event
            agent_results: Results from each agent
            
        Returns:
            Synthesized analysis combining all agent findings
        """
        detective_result = agent_results.get(AgentSpecialization.DETECTIVE.value)
        diagnostician_result = agent_results.get(AgentSpecialization.DIAGNOSTICIAN.value)
        predictive_result = agent_results.get(AgentSpecialization.PREDICTIVE.value)
        
        if not detective_result:
            logger.warning("No detective agent results available")
            return {'error': 'No agent results available'}
        
        synthesis = {
            'incident_summary': {
                'severity': detective_result['findings'].get('severity_tier', 'UNKNOWN'),
                'anomaly_confidence': detective_result['confidence'],
                'primary_metrics_affected': [
                    metric["metric"] for metric in 
                    detective_result['findings'].get('primary_metrics_affected', [])
                ]
            },
            'root_cause_insights': diagnostician_result['findings'] if diagnostician_result else {},
            'predictive_insights': predictive_result['findings'] if predictive_result else {},
            'recommended_actions': self._prioritize_actions(
                detective_result.get('recommendations', []),
                diagnostician_result.get('recommendations', []) if diagnostician_result else [],
                predictive_result.get('recommendations', []) if predictive_result else []
            ),
            'agent_metadata': {
                'participating_agents': list(agent_results.keys()),
                'analysis_timestamp': datetime.datetime.now().isoformat()
            }
        }
        
        return synthesis
    
    def _prioritize_actions(self, detection_actions: List[str], 
                          diagnosis_actions: List[str], 
                          predictive_actions: List[str]) -> List[str]:
        """
        Combine and prioritize actions from multiple agents
        
        Args:
            detection_actions: Actions from detective agent
            diagnosis_actions: Actions from diagnostician agent
            predictive_actions: Actions from predictive agent
            
        Returns:
            Prioritized list of unique actions
        """
        all_actions = detection_actions + diagnosis_actions + predictive_actions
        seen = set()
        unique_actions = []
        for action in all_actions:
            if action not in seen:
                seen.add(action)
                unique_actions.append(action)
        return unique_actions[:5]  # Return top 5 actions

# Initialize orchestration manager
orchestration_manager = OrchestrationManager()

# === Enhanced Reliability Engine ===
class EnhancedReliabilityEngine:
    """
    Main engine for processing reliability events through the multi-agent system.
    Coordinates anomaly detection, agent analysis, policy evaluation, and impact calculation.
    """
    
    def __init__(self):
        self.performance_metrics = {
            'total_incidents_processed': 0,
            'multi_agent_analyses': 0,
            'anomalies_detected': 0
        }
        self._lock = threading.RLock()
        logger.info("Initialized EnhancedReliabilityEngine")
    
    async def process_event_enhanced(
        self, 
        component: str, 
        latency: float, 
        error_rate: float,
        throughput: float = 1000, 
        cpu_util: Optional[float] = None,
        memory_util: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Process a reliability event through the complete analysis pipeline
        
        Args:
            component: Service component name
            latency: P99 latency in milliseconds
            error_rate: Error rate (0-1)
            throughput: Requests per second
            cpu_util: CPU utilization (0-1)
            memory_util: Memory utilization (0-1)
            
        Returns:
            Comprehensive analysis results including agent findings, healing actions, and business impact
        """
        logger.info(f"Processing event for {component}: latency={latency}ms, error_rate={error_rate*100:.1f}%")
        
        # Create event
        event = ReliabilityEvent(
            component=component,
            latency_p99=latency,
            error_rate=error_rate,
            throughput=throughput,
            cpu_util=cpu_util,
            memory_util=memory_util,
            upstream_deps=["auth-service", "database"] if component == "api-service" else []
        )
        
        # Multi-agent analysis
        agent_analysis = await orchestration_manager.orchestrate_analysis(event)
        
        # Anomaly detection
        is_anomaly = anomaly_detector.detect_anomaly(event)

        # Determine severity based on agent confidence
        agent_confidence = 0.0
        if agent_analysis and 'incident_summary' in agent_analysis:
            agent_confidence = agent_analysis.get('incident_summary', {}).get('anomaly_confidence', 0)
        else:
            agent_confidence = 0.8 if is_anomaly else 0.1

        # Set event severity
        if agent_confidence > 0.8:
            event.severity = EventSeverity.CRITICAL
        elif agent_confidence > 0.6:
            event.severity = EventSeverity.HIGH  
        elif agent_confidence > 0.4:
            event.severity = EventSeverity.MEDIUM
        else:
            event.severity = EventSeverity.LOW
        
        # Evaluate healing policies
        healing_actions = policy_engine.evaluate_policies(event)
        
        # Calculate business impact
        business_impact = business_calculator.calculate_impact(event) if is_anomaly else None
        
        # Store in vector database for similarity detection
        if thread_safe_index is not None and model is not None and is_anomaly:
            try:
                analysis_text = agent_analysis.get('recommended_actions', ['No analysis'])[0]
                vector_text = f"{component} {latency} {error_rate} {analysis_text}"
                vec = model.encode([vector_text])
                thread_safe_index.add(np.array(vec, dtype=np.float32), vector_text)
            except Exception as e:
                logger.error(f"Error storing vector: {e}", exc_info=True)
        
        # Build comprehensive result
        result = {
            "timestamp": event.timestamp,
            "component": component,
            "latency_p99": latency,
            "error_rate": error_rate,
            "throughput": throughput,
            "status": "ANOMALY" if is_anomaly else "NORMAL",
            "multi_agent_analysis": agent_analysis,
            "healing_actions": [action.value for action in healing_actions],
            "business_impact": business_impact,
            "severity": event.severity.value,
            "similar_incidents_count": thread_safe_index.get_count() if thread_safe_index and is_anomaly else 0,
            "processing_metadata": {
                "agents_used": agent_analysis.get('agent_metadata', {}).get('participating_agents', []),
                "analysis_confidence": agent_analysis.get('incident_summary', {}).get('anomaly_confidence', 0)
            }
        }
        
        # Store event in history
        events_history_store.add(event)
        
        # Update performance metrics
        with self._lock:
            self.performance_metrics['total_incidents_processed'] += 1
            self.performance_metrics['multi_agent_analyses'] += 1
            if is_anomaly:
                self.performance_metrics['anomalies_detected'] += 1
        
        logger.info(f"Event processed: {result['status']} with {result['severity']} severity")
        
        return result

# Initialize enhanced engine
enhanced_engine = EnhancedReliabilityEngine()

# === Input Validation ===
def validate_inputs(
    latency: float, 
    error_rate: float, 
    throughput: float, 
    cpu_util: Optional[float], 
    memory_util: Optional[float]
) -> Tuple[bool, str]:
    """
    Validate user inputs for bounds and type correctness
    
    Args:
        latency: Latency value in milliseconds
        error_rate: Error rate (0-1)
        throughput: Throughput in requests/sec
        cpu_util: CPU utilization (0-1)
        memory_util: Memory utilization (0-1)
        
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if not (0 <= latency <= 10000):
        return False, "❌ Invalid latency: must be between 0-10000ms"
    if not (0 <= error_rate <= 1):
        return False, "❌ Invalid error rate: must be between 0-1"
    if throughput < 0:
        return False, "❌ Invalid throughput: must be positive"
    if cpu_util is not None and not (0 <= cpu_util <= 1):
        return False, "❌ Invalid CPU utilization: must be between 0-1"
    if memory_util is not None and not (0 <= memory_util <= 1):
        return False, "❌ Invalid memory utilization: must be between 0-1"
    
    return True, ""

# === Gradio UI ===
def create_enhanced_ui():
    """
    Create the comprehensive Gradio UI for the reliability framework.
    Includes telemetry input, multi-agent analysis display, predictive insights,
    and event history visualization.
    """
    
    with gr.Blocks(title="🧠 Enterprise Agentic Reliability Framework", theme="soft") as demo:
        gr.Markdown("""
        # 🧠 Enterprise Agentic Reliability Framework
        **Multi-Agent AI System for Production Reliability**
        
        *Specialized AI agents working together to detect, diagnose, predict, and heal system issues*
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📊 Telemetry Input")
                component = gr.Dropdown(
                    choices=["api-service", "auth-service", "payment-service", "database", "cache-service"],
                    value="api-service",
                    label="Component",
                    info="Select the service being monitored"
                )
                latency = gr.Slider(
                    minimum=10, maximum=1000, value=100, step=1,
                    label="Latency P99 (ms)",
                    info=f"Alert threshold: >{config.LATENCY_WARNING}ms (adaptive)"
                )
                error_rate = gr.Slider(
                    minimum=0, maximum=0.5, value=0.02, step=0.001,
                    label="Error Rate",
                    info=f"Alert threshold: >{config.ERROR_RATE_WARNING}"
                )
                throughput = gr.Number(
                    value=1000,
                    label="Throughput (req/sec)",
                    info="Current request rate"
                )
                cpu_util = gr.Slider(
                    minimum=0, maximum=1, value=0.4, step=0.01,
                    label="CPU Utilization",
                    info="0.0 - 1.0 scale"
                )
                memory_util = gr.Slider(
                    minimum=0, maximum=1, value=0.3, step=0.01,
                    label="Memory Utilization", 
                    info="0.0 - 1.0 scale"
                )
                submit_btn = gr.Button("🚀 Submit Telemetry Event", variant="primary", size="lg")
                
            with gr.Column(scale=2):
                gr.Markdown("### 🔍 Multi-Agent Analysis")
                output_text = gr.Textbox(
                    label="Agent Synthesis",
                    placeholder="AI agents are analyzing...",
                    lines=6
                )
                
                with gr.Accordion("🤖 Agent Specialists Analysis", open=False):
                    gr.Markdown("""
                    **Specialized AI Agents:**
                    - 🕵️ **Detective**: Anomaly detection & pattern recognition
                    - 🔍 **Diagnostician**: Root cause analysis & investigation  
                    - 🔮 **Predictive**: Future risk forecasting & trend analysis
                    """)
                    
                    agent_insights = gr.JSON(
                        label="Detailed Agent Findings",
                        value={}
                    )
                
                with gr.Accordion("🔮 Predictive Analytics & Forecasting", open=False):
                    gr.Markdown("""
                    **Future Risk Forecasting:**
                    - 📈 Latency trends and thresholds
                    - 🚨 Error rate predictions  
                    - 🔥 Resource utilization forecasts
                    - ⏰ Time-to-failure estimates
                    """)
                    
                    predictive_insights = gr.JSON(
                        label="Predictive Forecasts",
                        value={}
                    )
                
                gr.Markdown("### 📈 Recent Events (Last 15)")
                events_table = gr.Dataframe(
                    headers=["Timestamp", "Component", "Latency", "Error Rate", "Throughput", "Severity", "Analysis"],
                    label="Event History",
                    wrap=True,
                )
        
        with gr.Accordion("ℹ️ Framework Capabilities", open=False):
            gr.Markdown("""
            - **🤖 Multi-Agent AI**: Specialized agents for detection, diagnosis, prediction, and healing
            - **🔮 Predictive Analytics**: Forecast future risks and performance degradation
            - **🔧 Policy-Based Healing**: Automated recovery actions based on severity and context
            - **💰 Business Impact**: Revenue and user impact quantification
            - **🎯 Adaptive Detection**: ML-powered thresholds that learn from your environment
            - **📚 Vector Memory**: FAISS-based incident memory for similarity detection
            - **⚡ Production Ready**: Circuit breakers, cooldowns, and enterprise features
            """)
            
        with gr.Accordion("🔧 Healing Policies", open=False):
            policy_info = []
            for policy in policy_engine.policies:
                if policy.enabled:
                    actions = ", ".join([action.value for action in policy.actions])
                    policy_info.append(f"**{policy.name}**: {actions} (Priority: {policy.priority})")
            
            gr.Markdown("\n\n".join(policy_info))
        
        # ✅ FIXED: Synchronous wrapper for async function (CRITICAL FIX)
        def submit_event_enhanced_sync(component, latency, error_rate, throughput, cpu_util, memory_util):
            """
            Synchronous wrapper for async event processing.
            FIXES GRADIO ASYNC/SYNC COMPATIBILITY ISSUE.
            
            This wrapper:
            1. Validates inputs
            2. Creates new event loop for async execution
            3. Calls the async processing function
            4. Formats results for display
            5. Handles all errors gracefully
            """
            try:
                # Type conversion
                latency = float(latency)
                error_rate = float(error_rate)
                throughput = float(throughput) if throughput else 1000
                cpu_util = float(cpu_util) if cpu_util else None
                memory_util = float(memory_util) if memory_util else None
                
                # Input validation (CRITICAL FIX)
                is_valid, error_msg = validate_inputs(latency, error_rate, throughput, cpu_util, memory_util)
                if not is_valid:
                    logger.warning(f"Invalid input: {error_msg}")
                    return error_msg, {}, {}, gr.Dataframe(value=[])
                
                # Create new event loop for async execution (CRITICAL FIX)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    # Call async function
                    result = loop.run_until_complete(
                        enhanced_engine.process_event_enhanced(
                            component, latency, error_rate, throughput, cpu_util, memory_util
                        )
                    )
                finally:
                    loop.close()
                
                # Build table data (THREAD-SAFE FIX)
                table_data = []
                for event in events_history_store.get_recent(15):
                    table_data.append([
                        event.timestamp[:19],
                        event.component,
                        event.latency_p99,
                        f"{event.error_rate:.3f}",
                        event.throughput,
                        event.severity.value.upper(),
                        "Multi-agent analysis"
                    ])
                
                # Format output message
                status_emoji = "🚨" if result["status"] == "ANOMALY" else "✅"
                output_msg = f"{status_emoji} **{result['status']}**"
                
                if "multi_agent_analysis" in result:
                    analysis = result["multi_agent_analysis"]
                    confidence = analysis.get('incident_summary', {}).get('anomaly_confidence', 0)
                    output_msg += f"\n🎯 **Confidence**: {confidence*100:.1f}%"
                    
                    predictive_data = analysis.get('predictive_insights', {})
                    if predictive_data.get('critical_risk_count', 0) > 0:
                        output_msg += f"\n🔮 **PREDICTIVE**: {predictive_data['critical_risk_count']} critical risks forecast"
                    
                    if analysis.get('recommended_actions'):
                        actions_preview = ', '.join(analysis['recommended_actions'][:2])
                        output_msg += f"\n💡 **Top Insights**: {actions_preview}"
                
                if result["business_impact"]:
                    impact = result["business_impact"]
                    output_msg += (
                        f"\n💰 **Business Impact**: ${impact['revenue_loss_estimate']:.2f} | "
                        f"👥 {impact['affected_users_estimate']} users | "
                        f"🚨 {impact['severity_level']}"
                    )
                
                if result["healing_actions"] and result["healing_actions"] != ["no_action"]:
                    actions = ", ".join(result["healing_actions"])
                    output_msg += f"\n🔧 **Auto-Actions**: {actions}"
                
                agent_insights_data = result.get("multi_agent_analysis", {})
                predictive_insights_data = agent_insights_data.get('predictive_insights', {})
                
                return (
                    output_msg,
                    agent_insights_data,
                    predictive_insights_data,
                    gr.Dataframe(
                        headers=["Timestamp", "Component", "Latency", "Error Rate", "Throughput", "Severity", "Analysis"],
                        value=table_data,
                        wrap=True
                    )
                )
                
            except ValueError as e:
                error_msg = f"❌ Value error: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return error_msg, {}, {}, gr.Dataframe(value=[])
            except Exception as e:
                error_msg = f"❌ Error processing event: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return error_msg, {}, {}, gr.Dataframe(value=[])
        
        # ✅ FIXED: Use sync wrapper instead of async function (CRITICAL FIX)
        submit_btn.click(
            fn=submit_event_enhanced_sync,  # Synchronous wrapper
            inputs=[component, latency, error_rate, throughput, cpu_util, memory_util],
            outputs=[output_text, agent_insights, predictive_insights, events_table]
        )
    
    return demo

# === Main Entry Point ===
if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("Starting Enterprise Agentic Reliability Framework")
    logger.info("=" * 80)
    logger.info(f"Total events in history: {events_history_store.count()}")
    logger.info(f"Vector index size: {thread_safe_index.get_count() if thread_safe_index else 0}")
    logger.info(f"Agents initialized: {len(orchestration_manager.agents)}")
    logger.info(f"Configuration: HF_TOKEN={'SET' if config.HF_TOKEN else 'NOT SET'}")
    
    demo = create_enhanced_ui()
    
    logger.info("Launching Gradio UI on 0.0.0.0:7860...")
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
    
    # Graceful shutdown: Save any pending vectors
    if thread_safe_index:
        logger.info("Saving pending vectors before shutdown...")
        thread_safe_index.force_save()
    
    logger.info("=" * 80)
    logger.info("Application shutdown complete")
    logger.info("=" * 80)
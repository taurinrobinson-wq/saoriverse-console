"""
Phase 2.3-2.5 Deployment Monitoring Module
Tracks key metrics for success measurement and early issue detection
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import json


@dataclass
class MetricPoint:
    """Single metric measurement."""
    timestamp: datetime
    value: float
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to serializable dict."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "metadata": self.metadata
        }


@dataclass
class MetricTimeSeries:
    """Time series of metric measurements."""
    name: str
    unit: str
    points: List[MetricPoint] = field(default_factory=list)
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None

    def add_point(self, value: float, metadata: Optional[Dict] = None) -> None:
        """Add measurement point."""
        self.points.append(MetricPoint(
            timestamp=datetime.now(),
            value=value,
            metadata=metadata or {}
        ))

    def get_latest(self) -> Optional[float]:
        """Get most recent value."""
        return self.points[-1].value if self.points else None

    def get_average(self, hours: int = 1) -> float:
        """Get average over time period."""
        if not self.points:
            return 0.0

        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [p.value for p in self.points if p.timestamp >= cutoff]
        return sum(recent) / len(recent) if recent else 0.0

    def get_trend(self, hours: int = 1) -> str:
        """Determine if metric trending up, down, or stable."""
        if len(self.points) < 2:
            return "insufficient_data"

        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [p for p in self.points if p.timestamp >= cutoff]

        if len(recent) < 2:
            return "insufficient_data"

        first_half = recent[:len(recent)//2]
        second_half = recent[len(recent)//2:]

        avg_first = sum(p.value for p in first_half) / len(first_half)
        avg_second = sum(p.value for p in second_half) / len(second_half)

        if avg_second > avg_first * 1.1:
            return "increasing"
        elif avg_second < avg_first * 0.9:
            return "decreasing"
        else:
            return "stable"

    def is_alert(self) -> Optional[str]:
        """Check if metric exceeds thresholds."""
        latest = self.get_latest()
        if latest is None:
            return None

        if self.threshold_critical and latest >= self.threshold_critical:
            return "critical"
        elif self.threshold_warning and latest >= self.threshold_warning:
            return "warning"
        return None


class DeploymentMonitor:
    """Monitor system health and learning effectiveness."""

    def __init__(self):
        """Initialize monitor."""
        self.metrics: Dict[str, MetricTimeSeries] = {}
        self._initialize_metrics()

    def _initialize_metrics(self) -> None:
        """Create standard metrics."""
        # Learning effectiveness metrics
        self.metrics["user_acceptance_rate"] = MetricTimeSeries(
            name="User Acceptance Rate",
            unit="percentage",
            threshold_warning=0.4,
            threshold_critical=0.2
        )

        self.metrics["rejection_detection_accuracy"] = MetricTimeSeries(
            name="Rejection Detection Accuracy",
            unit="percentage",
            threshold_warning=0.6,
            threshold_critical=0.3
        )

        self.metrics["glyph_diversity"] = MetricTimeSeries(
            name="Unique Glyphs Used",
            unit="count"
        )

        self.metrics["repetition_rate"] = MetricTimeSeries(
            name="Glyph Repetition Rate",
            unit="percentage",
            threshold_warning=0.7,
            threshold_critical=0.9
        )

        # System performance
        self.metrics["response_time_ms"] = MetricTimeSeries(
            name="Average Response Time",
            unit="milliseconds",
            threshold_warning=500,
            threshold_critical=1000
        )

        self.metrics["error_rate"] = MetricTimeSeries(
            name="Error Rate",
            unit="percentage",
            threshold_warning=0.01,
            threshold_critical=0.05
        )

        # User engagement
        self.metrics["dashboard_engagement"] = MetricTimeSeries(
            name="Dashboard Views per Day",
            unit="count"
        )

        self.metrics["preference_override_frequency"] = MetricTimeSeries(
            name="Manual Overrides per Day",
            unit="count"
        )

        # Pattern emergence
        self.metrics["temporal_patterns_confidence"] = MetricTimeSeries(
            name="Avg Temporal Pattern Confidence",
            unit="percentage"
        )

        self.metrics["cluster_cohesion"] = MetricTimeSeries(
            name="Average Cluster Cohesion",
            unit="percentage"
        )

    def record_metric(self, metric_name: str, value: float, metadata: Optional[Dict] = None) -> None:
        """Record a metric measurement."""
        if metric_name not in self.metrics:
            raise ValueError(f"Unknown metric: {metric_name}")

        self.metrics[metric_name].add_point(value, metadata)

    def record_user_acceptance(self, user_id: str, accepted: bool) -> None:
        """Record user acceptance of a glyph."""
        acceptance_rate = 100.0 if accepted else 0.0
        self.record_metric(
            "user_acceptance_rate",
            acceptance_rate,
            {"user_id": user_id}
        )

    def record_rejection_detection(self, detected: bool, false_positive: bool = False) -> None:
        """Record rejection detection event."""
        accuracy = 100.0 if detected and not false_positive else 0.0
        self.record_metric(
            "rejection_detection_accuracy",
            accuracy,
            {"false_positive": false_positive}
        )

    def record_response_time(self, milliseconds: float) -> None:
        """Record response time."""
        self.record_metric("response_time_ms", milliseconds)

    def get_system_health(self) -> Dict:
        """Get overall system health status."""
        alerts = []
        warnings = []

        for name, metric in self.metrics.items():
            alert_level = metric.is_alert()
            if alert_level == "critical":
                alerts.append(
                    f"{metric.name}: {metric.get_latest():.1f} {metric.unit}")
            elif alert_level == "warning":
                warnings.append(
                    f"{metric.name}: {metric.get_latest():.1f} {metric.unit}")

        # Determine overall status
        if alerts:
            status = "critical"
        elif warnings:
            status = "warning"
        else:
            status = "healthy"

        return {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "alerts": alerts,
            "warnings": warnings,
            "metrics": {
                name: {
                    "latest": metric.get_latest(),
                    "trend": metric.get_trend(hours=1),
                    "average_1h": metric.get_average(hours=1),
                }
                for name, metric in self.metrics.items()
            }
        }

    def export_metrics(self) -> Dict:
        """Export all metrics as JSON."""
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                name: {
                    "unit": metric.unit,
                    "latest": metric.get_latest(),
                    "average_1h": metric.get_average(1),
                    "average_24h": metric.get_average(24),
                    "trend": metric.get_trend(1),
                    "points_count": len(metric.points),
                }
                for name, metric in self.metrics.items()
            }
        }

    def get_learning_insights(self) -> List[str]:
        """Generate insights from learning metrics."""
        insights = []

        # Acceptance rate trending
        acceptance = self.metrics["user_acceptance_rate"]
        if acceptance.get_trend(24) == "increasing":
            latest = acceptance.get_latest()
            insights.append(
                f"✅ User acceptance trending upward ({latest:.0f}% latest)")
        elif acceptance.get_trend(24) == "decreasing":
            latest = acceptance.get_latest()
            insights.append(
                f"⚠️  User acceptance declining ({latest:.0f}% latest)")

        # Rejection detection
        rejection_acc = self.metrics["rejection_detection_accuracy"]
        if rejection_acc.get_latest():
            insights.append(
                f"Rejection detection: {rejection_acc.get_average(24):.0f}% accurate")

        # Glyph diversity
        diversity = self.metrics["glyph_diversity"]
        if diversity.get_latest():
            insights.append(
                f"System using {diversity.get_latest():.0f} unique glyphs")

        # Temporal patterns
        temporal = self.metrics["temporal_patterns_confidence"]
        if temporal.get_latest():
            insights.append(
                f"Temporal patterns emerging with {temporal.get_latest():.0f}% confidence")

        # Response performance
        response = self.metrics["response_time_ms"]
        if response.get_latest():
            avg = response.get_average(1)
            insights.append(f"Average response time: {avg:.0f}ms")

        return insights if insights else ["Collecting initial metrics... Check back in 1 hour"]

    def get_critical_summary(self) -> str:
        """Get one-line critical status."""
        health = self.get_system_health()
        status = health["status"].upper()
        alert_count = len(health["alerts"])
        warning_count = len(health["warnings"])

        if status == "CRITICAL":
            return f"🔴 CRITICAL: {alert_count} alerts, {warning_count} warnings"
        elif status == "WARNING":
            return f"🟡 WARNING: {warning_count} warnings"
        else:
            return "🟢 HEALTHY: All systems nominal"


# Example usage for integration
def setup_monitoring() -> DeploymentMonitor:
    """Initialize monitoring system."""
    monitor = DeploymentMonitor()

    # Example: Record some initial metrics
    monitor.record_user_acceptance("user1", True)
    monitor.record_response_time(125.5)
    monitor.record_rejection_detection(True, False)

    return monitor


if __name__ == "__main__":
    # Test monitoring
    monitor = setup_monitoring()
    print("\n📊 System Health Report")
    print(json.dumps(monitor.get_system_health(), indent=2))
    print("\n💡 Learning Insights")
    for insight in monitor.get_learning_insights():
        print(f"  {insight}")
    print(f"\n{monitor.get_critical_summary()}")

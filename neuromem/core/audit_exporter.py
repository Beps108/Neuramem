"""
NeuraMem Audit Exporter Module (Feature 6)
Provides audit trail export and compliance reporting functionality.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json
import csv
import io


class AuditEventType(Enum):
    """Types of auditable events."""
    BELIEF_ADDED = "belief_added"
    BELIEF_UPDATED = "belief_updated"
    BELIEF_REMOVED = "belief_removed"
    BELIEF_REJECTED = "belief_rejected"
    CONTRADICTION_DETECTED = "contradiction_detected"
    CONTRADICTION_RESOLVED = "contradiction_resolved"
    CONFIDENCE_CHANGED = "confidence_changed"
    INHERITANCE_PERFORMED = "inheritance_performed"
    TRACE_CREATED = "trace_created"
    TRACE_COMPLETED = "trace_completed"
    EXPORT_REQUESTED = "export_requested"
    SYSTEM_CONFIG_CHANGED = "system_config_changed"
    USER_ACTION = "user_action"


class ExportFormat(Enum):
    """Supported export formats."""
    JSON = "json"
    CSV = "csv"
    XML = "xml"
    MARKDOWN = "markdown"


@dataclass
class AuditEvent:
    """Represents a single auditable event."""
    
    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    actor_id: Optional[str]
    description: str
    affected_entities: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "actor_id": self.actor_id,
            "description": self.description,
            "affected_entities": self.affected_entities,
            "metadata": self.metadata,
            "previous_state": self.previous_state,
            "new_state": self.new_state
        }


class AuditLogger:
    """Records and manages audit events."""
    
    def __init__(self, max_events: int = 100000):
        self._events: List[AuditEvent] = []
        self._max_events = max_events
        self._event_counter = 0
    
    def log(self, event_type: AuditEventType, description: str,
            actor_id: Optional[str] = None,
            affected_entities: Optional[List[str]] = None,
            metadata: Optional[Dict[str, Any]] = None,
            previous_state: Optional[Dict[str, Any]] = None,
            new_state: Optional[Dict[str, Any]] = None) -> str:
        """Log a new audit event."""
        self._event_counter += 1
        event_id = f"evt_{self._event_counter:08d}_{hashlib.sha256(
            f'{datetime.now().isoformat()}{description}'.encode()
        ).hexdigest()[:8]}"
        
        event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=datetime.now(),
            actor_id=actor_id,
            description=description,
            affected_entities=affected_entities or [],
            metadata=metadata or {},
            previous_state=previous_state,
            new_state=new_state
        )
        
        self._events.append(event)
        
        # Trim if exceeding max
        if len(self._events) > self._max_events:
            self._events = self._events[-self._max_events:]
        
        return event_id
    
    def get_events(self, start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None,
                  event_type: Optional[AuditEventType] = None,
                  actor_id: Optional[str] = None,
                  limit: int = 1000) -> List[AuditEvent]:
        """Query audit events with filters."""
        results = []
        
        for event in reversed(self._events):
            if len(results) >= limit:
                break
            
            if start_time and event.timestamp < start_time:
                continue
            if end_time and event.timestamp > end_time:
                continue
            if event_type and event.event_type != event_type:
                continue
            if actor_id and event.actor_id != actor_id:
                continue
            
            results.append(event)
        
        return results
    
    def count(self) -> int:
        """Get total event count."""
        return len(self._events)


class AuditExporter:
    """Exports audit logs in various formats."""
    
    def __init__(self, logger: AuditLogger):
        self.logger = logger
    
    def export(self, format: ExportFormat = ExportFormat.JSON,
              start_time: Optional[datetime] = None,
              end_time: Optional[datetime] = None,
              event_type: Optional[AuditEventType] = None,
              **kwargs) -> str:
        """Export audit events in specified format."""
        events = self.logger.get_events(
            start_time=start_time,
            end_time=end_time,
            event_type=event_type,
            limit=kwargs.get("limit", 10000)
        )
        
        if format == ExportFormat.JSON:
            return self._export_json(events, kwargs.get("indent", 2))
        elif format == ExportFormat.CSV:
            return self._export_csv(events)
        elif format == ExportFormat.XML:
            return self._export_xml(events)
        elif format == ExportFormat.MARKDOWN:
            return self._export_markdown(events)
        else:
            return self._export_json(events)
    
    def _export_json(self, events: List[AuditEvent], indent: int = 2) -> str:
        """Export as JSON."""
        data = {
            "export_timestamp": datetime.now().isoformat(),
            "event_count": len(events),
            "events": [e.to_dict() for e in events]
        }
        return json.dumps(data, indent=indent)
    
    def _export_csv(self, events: List[AuditEvent]) -> str:
        """Export as CSV."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "event_id", "event_type", "timestamp", "actor_id",
            "description", "affected_entities", "metadata"
        ])
        
        # Rows
        for event in events:
            writer.writerow([
                event.event_id,
                event.event_type.value,
                event.timestamp.isoformat(),
                event.actor_id or "",
                event.description,
                "|".join(event.affected_entities),
                json.dumps(event.metadata)
            ])
        
        return output.getvalue()
    
    def _export_xml(self, events: List[AuditEvent]) -> str:
        """Export as XML."""
        lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        lines.append('<audit_export>')
        lines.append(f'  <export_timestamp>{datetime.now().isoformat()}</export_timestamp>')
        lines.append(f'  <event_count>{len(events)}</event_count>')
        lines.append('  <events>')
        
        for event in events:
            lines.append('    <event>')
            lines.append(f'      <event_id>{self._escape_xml(event.event_id)}</event_id>')
            lines.append(f'      <event_type>{event.event_type.value}</event_type>')
            lines.append(f'      <timestamp>{event.timestamp.isoformat()}</timestamp>')
            lines.append(f'      <actor_id>{self._escape_xml(event.actor_id or "")}</actor_id>')
            lines.append(f'      <description>{self._escape_xml(event.description)}</description>')
            lines.append(f'      <affected_entities>{",".join(event.affected_entities)}</affected_entities>')
            lines.append('    </event>')
        
        lines.append('  </events>')
        lines.append('</audit_export>')
        
        return "\n".join(lines)
    
    def _export_markdown(self, events: List[AuditEvent]) -> str:
        """Export as Markdown report."""
        lines = ['# NeuraMem Audit Report']
        lines.append(f'\n**Export Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        lines.append(f'**Total Events:** {len(events)}\n')
        
        # Summary by type
        type_counts = {}
        for event in events:
            etype = event.event_type.value
            type_counts[etype] = type_counts.get(etype, 0) + 1
        
        lines.append('## Event Summary\n')
        lines.append('| Event Type | Count |')
        lines.append('|------------|-------|')
        for etype, count in sorted(type_counts.items()):
            lines.append(f'| {etype} | {count} |')
        
        lines.append('\n## Event Details\n')
        
        for event in events:
            lines.append(f'### {event.event_id}')
            lines.append(f'- **Type:** {event.event_type.value}')
            lines.append(f'- **Time:** {event.timestamp.strftime("%Y-%m-%d %H:%M:%S")}')
            lines.append(f'- **Actor:** {event.actor_id or "system"}')
            lines.append(f'- **Description:** {event.description}')
            if event.affected_entities:
                lines.append(f'- **Affected:** {", ".join(event.affected_entities)}')
            lines.append('')
        
        return "\n".join(lines)
    
    def _escape_xml(self, text: str) -> str:
        """Escape special XML characters."""
        return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;"))


class ComplianceReporter:
    """Generates compliance reports from audit data."""
    
    def __init__(self, exporter: AuditExporter):
        self.exporter = exporter
        self.logger = exporter.logger
    
    def generate_report(self, period_days: int = 30,
                       include_statistics: bool = True) -> Dict[str, Any]:
        """Generate a compliance report."""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=period_days)
        
        events = self.logger.get_events(start_time=start_time, end_time=end_time, limit=50000)
        
        report = {
            "report_type": "compliance",
            "generated_at": datetime.now().isoformat(),
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "days": period_days
            },
            "summary": {
                "total_events": len(events),
                "unique_actors": len(set(e.actor_id for e in events if e.actor_id)),
                "events_by_type": self._count_by_type(events),
                "events_by_day": self._count_by_day(events)
            }
        }
        
        if include_statistics:
            report["statistics"] = self._calculate_statistics(events)
        
        report["anomalies"] = self._detect_anomalies(events)
        
        return report
    
    def _count_by_type(self, events: List[AuditEvent]) -> Dict[str, int]:
        """Count events by type."""
        counts = {}
        for event in events:
            etype = event.event_type.value
            counts[etype] = counts.get(etype, 0) + 1
        return counts
    
    def _count_by_day(self, events: List[AuditEvent]) -> Dict[str, int]:
        """Count events by day."""
        counts = {}
        for event in events:
            day = event.timestamp.strftime("%Y-%m-%d")
            counts[day] = counts.get(day, 0) + 1
        return counts
    
    def _calculate_statistics(self, events: List[AuditEvent]) -> Dict[str, Any]:
        """Calculate statistical metrics."""
        if not events:
            return {}
        
        timestamps = [e.timestamp for e in events]
        
        return {
            "avg_events_per_day": len(events) / max(1, len(set(t.strftime("%Y-%m-%d") for t in timestamps))),
            "peak_hour": self._find_peak_hour(events),
            "most_active_actor": self._find_most_active_actor(events),
            "most_common_event_type": max(self._count_by_type(events).items(), key=lambda x: x[1])[0] if events else None
        }
    
    def _find_peak_hour(self, events: List[AuditEvent]) -> int:
        """Find the hour with most events."""
        hour_counts = {}
        for event in events:
            hour = event.timestamp.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        return max(hour_counts.items(), key=lambda x: x[1])[0] if hour_counts else 0
    
    def _find_most_active_actor(self, events: List[AuditEvent]) -> Optional[str]:
        """Find the most active actor."""
        actor_counts = {}
        for event in events:
            if event.actor_id:
                actor_counts[event.actor_id] = actor_counts.get(event.actor_id, 0) + 1
        
        return max(actor_counts.items(), key=lambda x: x[1])[0] if actor_counts else None
    
    def _detect_anomalies(self, events: List[AuditEvent]) -> List[Dict[str, Any]]:
        """Detect potential anomalies in audit data."""
        anomalies = []
        
        # Check for high-frequency events from same actor
        actor_events = {}
        for event in events:
            if event.actor_id:
                if event.actor_id not in actor_events:
                    actor_events[event.actor_id] = []
                actor_events[event.actor_id].append(event)
        
        for actor, actor_event_list in actor_events.items():
            if len(actor_event_list) > 100:  # Threshold
                anomalies.append({
                    "type": "high_frequency_actor",
                    "actor_id": actor,
                    "event_count": len(actor_event_list),
                    "severity": "medium"
                })
        
        return anomalies


# Global instances
_audit_logger: Optional[AuditLogger] = None
_audit_exporter: Optional[AuditExporter] = None


def get_audit_logger() -> AuditLogger:
    """Get the global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


def get_audit_exporter() -> AuditExporter:
    """Get the global audit exporter instance."""
    global _audit_exporter
    if _audit_exporter is None:
        _audit_exporter = AuditExporter(get_audit_logger())
    return _audit_exporter


if __name__ == "__main__":
    logger = get_audit_logger()
    exporter = get_audit_exporter()
    
    # Log some sample events
    logger.log(
        AuditEventType.BELIEF_ADDED,
        "Added new belief about climate change",
        actor_id="user_001",
        affected_entities=["bel_123"],
        metadata={"topic": "climate", "confidence": 0.95}
    )
    
    logger.log(
        AuditEventType.CONTRADICTION_DETECTED,
        "Contradiction found between beliefs",
        actor_id="system",
        affected_entities=["bel_123", "bel_456"],
        metadata={"severity": "high"}
    )
    
    logger.log(
        AuditEventType.INHERITANCE_PERFORMED,
        "Beliefs inherited from parent agent",
        actor_id="agent_002",
        affected_entities=["agent_001", "agent_002"],
        metadata={"count": 5}
    )
    
    # Export as JSON
    print("JSON Export:")
    print(exporter.export(ExportFormat.JSON, limit=10)[:500])
    
    # Generate compliance report
    reporter = ComplianceReporter(exporter)
    report = reporter.generate_report(period_days=7)
    print(f"\nCompliance Report Summary:")
    print(f"Total events: {report['summary']['total_events']}")
    print(f"Unique actors: {report['summary']['unique_actors']}")

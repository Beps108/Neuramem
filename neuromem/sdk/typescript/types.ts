export interface Belief {
  belief_id: string;
  content: string;
  confidence: number;
}

export interface Rejection {
  id: string;
  content: string;
  reason: string;
}

export interface Contradiction {
  id: string;
  belief_ids: string[];
  type: string;
  severity: string;
}

export interface Trace {
  trace_id: string;
  status: string;
  conclusion?: string;
}

export interface AuditEvent {
  event_id: string;
  event_type: string;
  timestamp: string;
  description: string;
}

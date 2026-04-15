# NeuraMem

Neural Memory Management System with belief tracking, contradiction detection, and reasoning traces.

## Features

- **Negative Memory**: Store and manage rejected beliefs and false memories
- **Confidence Decay**: Time-based confidence decay for beliefs
- **Contradiction Detection**: Automatic detection of conflicting beliefs
- **Reasoning Traces**: Track inference chains and reasoning paths
- **Agent Inheritance**: Belief propagation between agents
- **Audit Export**: Comprehensive audit logging and compliance reporting
- **Hypergraph Storage**: Kuzu-backed graph engine for complex relationships

## Installation

```bash
pip install neuromem
```

Or from source:

```bash
git clone https://github.com/Beps108/Neuramem.git
cd Neuramem
pip install -e .
```

## Quick Start

```python
from neuromem.core.confidence_decay import get_belief_store
from neuromem.core.negative_memory import get_negative_store, RejectionReason

# Create a belief
store = get_belief_store()
belief_id = store.add_belief("The sky is blue", confidence=0.95)

# Reject a belief
neg_store = get_negative_store()
neg_store.reject_belief(
    "The Earth is flat",
    reason=RejectionReason.CONTRADICTION,
    tags=["science"]
)

# Check for contradictions
from neuromem.core.contradiction import get_contradiction_store
con_store = get_contradiction_store()
con_store.check_and_record(
    "bel_001", "The light is on", 0.95,
    "bel_002", "The light is not on", 0.90
)
```

## API Server

Start the API server:

```bash
uvicorn neuromem.api.main:app --host 0.0.0.0 --port 8765
```

API endpoints:
- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/v1/beliefs/` - Create belief
- `GET /api/v1/beliefs/` - List beliefs
- `POST /api/v1/rejections/` - Reject belief
- `GET /api/v1/contradictions/` - List contradictions
- `POST /api/v1/traces/` - Create reasoning trace
- `GET /api/v1/audit/events` - Get audit events

## SDKs

### Python SDK

```python
from neuromem.sdk.python.neuromem_sdk import NeuraMemClient

client = NeuraMemClient("http://localhost:8765")
belief = client.create_belief("Test belief", 0.9)
```

### TypeScript SDK

```typescript
import NeuraMemClient from '@neuromem/sdk';

const client = new NeuraMemClient('http://localhost:8765');
const belief = await client.createBelief('Test belief', 0.9);
```

## Project Structure

```
neuromem/
├── core/           # Core modules (runtime, cache, features)
├── graph/          # Hypergraph engine and queries
├── api/            # FastAPI application and routes
├── scheduler/      # APScheduler jobs
├── sdk/            # Python and TypeScript SDKs
├── integrations/   # Third-party integrations
├── cli/            # Command-line interface
└── tests/          # Test suite
```

## License

MIT License

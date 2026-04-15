/**
 * NeuraMem TypeScript SDK
 * Client library for interacting with NeuraMem API
 */

export interface Belief {
  belief_id: string;
  content: string;
  confidence: number;
}

export interface RejectionReason {
  CONTRADICTION: 'contradiction';
  LOW_CONFIDENCE: 'low_confidence';
  EXPLICIT_REJECTION: 'explicit_rejection';
  OBSOLETE: 'obsolete';
  USER_REJECTED: 'user_rejected';
}

export class NeuraMemClient {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8765') {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  async createBelief(content: string, confidence: number = 1.0): Promise<Belief> {
    const response = await fetch(`${this.baseUrl}/api/v1/beliefs/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, confidence }),
    });
    
    if (!response.ok) throw new Error('Failed to create belief');
    return response.json();
  }

  async getBelief(beliefId: string): Promise<Belief | null> {
    const response = await fetch(`${this.baseUrl}/api/v1/beliefs/${beliefId}`);
    if (response.status === 404) return null;
    if (!response.ok) throw new Error('Failed to get belief');
    return response.json();
  }

  async listBeliefs(): Promise<Belief[]> {
    const response = await fetch(`${this.baseUrl}/api/v1/beliefs/`);
    if (!response.ok) throw new Error('Failed to list beliefs');
    return response.json();
  }

  async rejectBelief(content: string, reason: string = 'contradiction'): Promise<any> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/rejections/?content=${encodeURIComponent(content)}&reason=${reason}`,
      { method: 'POST' }
    );
    if (!response.ok) throw new Error('Failed to reject belief');
    return response.json();
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}

export default NeuraMemClient;

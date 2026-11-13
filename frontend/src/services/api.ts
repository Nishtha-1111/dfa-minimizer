import { DFADefinition, AlgorithmType, MinimizeResponse, ValidationResponse, SimulateResponse } from '../types/dfa';

const API_BASE = '/api';

export async function validateDfa(dfa: DFADefinition): Promise<ValidationResponse> {
  const res = await fetch(`${API_BASE}/validate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dfa }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Validation failed' }));
    throw new Error(err.detail || 'Validation failed');
  }
  return res.json();
}

export async function minimizeDfa(dfa: DFADefinition, algorithm: AlgorithmType): Promise<MinimizeResponse> {
  const res = await fetch(`${API_BASE}/minimize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dfa, algorithm }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Minimization request failed' }));
    throw new Error(err.detail || 'Minimization request failed');
  }
  return res.json();
}

export async function simulateDfa(
  originalDfa: DFADefinition,
  minimalDfa: DFADefinition | undefined,
  inputString: string
): Promise<SimulateResponse> {
  const res = await fetch(`${API_BASE}/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      original_dfa: originalDfa,
      minimal_dfa: minimalDfa || null,
      input_string: inputString,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Simulation request failed' }));
    throw new Error(err.detail || 'Simulation request failed');
  }
  return res.json();
}

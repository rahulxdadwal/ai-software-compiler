/** API client for the backend. */

import { PipelineResponse, ExamplePrompt, HealthResponse } from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function compilePrompt(prompt: string): Promise<PipelineResponse> {
  const res = await fetch(`${API_URL}/api/compile`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function getExamples(): Promise<ExamplePrompt[]> {
  const res = await fetch(`${API_URL}/api/examples`);
  const data = await res.json();
  return data.examples;
}

export async function getHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_URL}/health`);
  return res.json();
}

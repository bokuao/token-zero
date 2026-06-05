const BASE = import.meta.env.VITE_API_BASE_URL || "/api";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }
  return res.json();
}

export interface ProviderModel {
  id: number;
  model_id: string;
  display_name: string;
  capabilities: string[];
  input_modalities: string[];
  first_seen_at?: string;
}

export interface Provider {
  id: string;
  name: string;
  logo_url: string;
  website_url: string;
  signup_url: string;
  api_keys_url: string;
  base_url: string;
  requires_credit_card: boolean;
  requires_phone: boolean;
  trains_on_data: boolean;
  model_count: number;
  models: ProviderModel[];
}

export interface ModelDetail {
  id: number;
  model_id: string;
  display_name: string;
  description: string;
  context_length: number;
  max_output: number | null;
  capabilities: string[];
  input_modalities: string[];
  rate_limits: string;
  provider: { id: string; name: string; base_url: string };
}

export interface ConfigResult {
  filename: string;
  format: string;
  content: string;
  agent: string;
  model: string;
  paths: { windows?: string; mac?: string; linux?: string };
}

export const api = {
  getProviders: (sort?: string) => get<Provider[]>(`/providers${sort ? '?sort=' + sort : ''}`),
  getProviderHealth: (id: string) => get<{ healthy: boolean; status: number; latency_ms: number }>(`/providers/${id}/health`),
  getModel: (id: number) => get<ModelDetail>(`/models/${id}`),
  getConfig: (agent: string, modelId: number) => get<ConfigResult>(`/config/${agent}/${modelId}`),
};

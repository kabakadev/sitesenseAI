const API_URL = import.meta.env.VITE_API_URL ?? "";

export type HealthResponse = {
  status: string;
  service: string;
};

export type Analysis = {
  id: number;
  input_text: string;
  findings: string;
  recommendations: string;
  created_at: string;
};

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(body?.detail ?? `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

export function createAnalysis(input_text: string): Promise<Analysis> {
  return request<Analysis>("/analyses", {
    method: "POST",
    body: JSON.stringify({ input_text }),
  });
}

export function getAnalyses(): Promise<Analysis[]> {
  return request<Analysis[]>("/analyses");
}

const API_URL = import.meta.env.VITE_API_URL ?? "";

export type Project = {
  id: number; name: string; description: string | null; location: string | null;
  budget: number | null; status: string; completion: number; task_count: number;
  completed_task_count: number; created_at: string; updated_at: string;
};
export type Task = { id: number; project_id: number; title: string; description: string | null; status: string; priority: string; };
export type TaskSuggestion = { title: string; description: string; priority: string };

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { headers: { "Content-Type": "application/json" }, ...options });
  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(body?.detail ?? `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}
export const getProjects = () => request<Project[]>("/api/v1/projects");
export const createProject = (body: object) => request<Project>("/api/v1/projects", { method: "POST", body: JSON.stringify(body) });
export const getTasks = (id: number) => request<Task[]>(`/api/v1/projects/${id}/tasks`);
export const createTask = (id: number, body: object) => request<Task>(`/api/v1/projects/${id}/tasks`, { method: "POST", body: JSON.stringify(body) });
export const updateTask = (id: number, body: object) => request<Task>(`/api/v1/tasks/${id}`, { method: "PATCH", body: JSON.stringify(body) });
export const suggestTasks = (id: number) => request<{ suggestions: TaskSuggestion[] }>(`/api/v1/projects/${id}/suggest-tasks`, { method: "POST" });

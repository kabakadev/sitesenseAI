import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import {
  createProject,
  createTask,
  getProjects,
  getTasks,
  suggestTasks,
  updateTask,
} from "./services/api";
import type { Project, Task, TaskSuggestion } from "./services/api";

const emptyProject = { name: "", description: "", location: "", budget: "" };

export default function App() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selected, setSelected] = useState<Project | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [suggestions, setSuggestions] = useState<TaskSuggestion[]>([]);
  const [projectForm, setProjectForm] = useState(emptyProject);
  const [taskTitle, setTaskTitle] = useState("");
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  async function loadProjects() {
    setProjects(await getProjects());
    setLoading(false);
  }

  async function selectProject(project: Project) {
    setSelected(project);
    setTasks(await getTasks(project.id));
    setSuggestions([]);
  }

  useEffect(() => {
    loadProjects().catch(() => {
      setMessage("The API is unavailable. Start the backend and refresh.");
      setLoading(false);
    });
  }, []);

  async function submitProject(event: FormEvent) {
    event.preventDefault();
    const project = await createProject({
      ...projectForm,
      budget: projectForm.budget ? Number(projectForm.budget) : null,
    });
    setProjectForm(emptyProject);
    await loadProjects();
    await selectProject(project);
  }

  async function submitTask(event: FormEvent) {
    event.preventDefault();
    if (!selected || !taskTitle.trim()) return;
    const task = await createTask(selected.id, { title: taskTitle.trim() });
    setTasks((current) => [task, ...current]);
    setTaskTitle("");
    await loadProjects();
  }

  async function changeStatus(task: Task, status: string) {
    const updated = await updateTask(task.id, { status });
    setTasks((current) => current.map((item) => item.id === task.id ? updated : item));
    if (selected) {
      const refreshed = (await getProjects()).find((item) => item.id === selected.id) ?? selected;
      setSelected(refreshed);
      setProjects((current) => current.map((item) => item.id === refreshed.id ? refreshed : item));
    }
  }

  async function getSuggestions() {
    if (!selected) return;
    setMessage("Gemma is preparing practical next steps...");
    try {
      const result = await suggestTasks(selected.id);
      setSuggestions(result.suggestions);
      setMessage("");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Gemma request failed");
    }
  }

  async function addSuggestion(suggestion: TaskSuggestion) {
    if (!selected) return;
    const task = await createTask(selected.id, suggestion);
    setTasks((current) => [task, ...current]);
    setSuggestions((current) => current.filter((item) => item !== suggestion));
    await loadProjects();
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand"><span className="brand-mark">◆</span><strong>SITESENSE <em>AI</em></strong></div>
        <span className="status">PROJECT INTELLIGENCE PLATFORM</span>
      </header>
      <main>
        <section className="hero">
          <div><p className="eyebrow">CONSTRUCTION PROJECT TRACKER</p><h1>Build smarter.<br /><em>Track everything.</em></h1><p>Manage projects, tasks, progress, and practical AI-assisted planning from one workspace.</p></div>
          <div className="hero-stat"><strong>{projects.length}</strong><span>active projects</span></div>
        </section>
        {message && <p className="message" role="alert">{message}</p>}
        <section className="workspace">
          <aside className="panel">
            <div className="panel-heading"><div><p className="eyebrow">PORTFOLIO</p><h2>Projects</h2></div><span>{projects.length}</span></div>
            <form onSubmit={submitProject} className="create-form">
              <input required placeholder="Project name" value={projectForm.name} onChange={(e) => setProjectForm({ ...projectForm, name: e.target.value })} />
              <input placeholder="Location" value={projectForm.location} onChange={(e) => setProjectForm({ ...projectForm, location: e.target.value })} />
              <input placeholder="Budget (optional)" type="number" value={projectForm.budget} onChange={(e) => setProjectForm({ ...projectForm, budget: e.target.value })} />
              <textarea placeholder="Project description" rows={3} value={projectForm.description} onChange={(e) => setProjectForm({ ...projectForm, description: e.target.value })} />
              <button type="submit">+ Create project</button>
            </form>
            {loading ? <p>Loading projects...</p> : projects.map((project) => (
              <button className={`project-card ${selected?.id === project.id ? "selected" : ""}`} key={project.id} onClick={() => selectProject(project)}>
                <span><strong>{project.name}</strong><small>{project.location || "No location"}</small></span>
                <b>{project.completion}%</b>
                <i><u style={{ width: `${project.completion}%` }} /></i>
              </button>
            ))}
          </aside>
          <section className="panel project-workspace">
            {!selected ? <div className="empty"><span>◈</span><h2>Select a project</h2><p>Create or select a project to manage its tasks and progress.</p></div> : <>
              <div className="panel-heading"><div><p className="eyebrow">ACTIVE PROJECT</p><h2>{selected.name}</h2><p>{selected.description || "No description yet."}</p></div><div className="completion"><strong>{selected.completion}%</strong><small>complete</small></div></div>
              <div className="progress"><i style={{ width: `${selected.completion}%` }} /></div>
              <form className="task-form" onSubmit={submitTask}><input required placeholder="Add a task..." value={taskTitle} onChange={(e) => setTaskTitle(e.target.value)} /><button type="submit">Add task</button><button type="button" onClick={getSuggestions}>Suggest with Gemma</button></form>
              {suggestions.length > 0 && <div className="suggestions"><h3>Gemma suggestions</h3>{suggestions.map((suggestion) => <div className="suggestion" key={suggestion.title}><span><strong>{suggestion.title}</strong><small>{suggestion.description}</small></span><button onClick={() => addSuggestion(suggestion)}>Add</button></div>)}</div>}
              <div className="tasks"><h3>Tasks <span>{tasks.length}</span></h3>{tasks.length === 0 ? <p>No tasks yet. Add one or ask Gemma for suggestions.</p> : tasks.map((task) => <div className="task" key={task.id}><span className={`task-dot ${task.status}`} /><span><strong>{task.title}</strong><small>{task.priority} priority</small></span><select value={task.status} onChange={(e) => changeStatus(task, e.target.value)}><option value="todo">Todo</option><option value="in_progress">In progress</option><option value="done">Done</option></select></div>)}</div>
            </>}
          </section>
        </section>
      </main>
    </div>
  );
}

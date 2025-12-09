import { create } from 'zustand';

const BASE_URL = 'http://127.0.0.1:8000'; // Mock/Dev URL

export const useStore = create((set, get) => ({
    // Global Data
    projects: [],
    materials: [],
    machines: [],

    // Workspace State
    activeProject: null,
    activePart: null,
    simulationResult: null,
    isLoading: false,
    error: null,

    // Actions
    fetchMaterials: async () => {
        try {
            const res = await fetch(`${BASE_URL}/materials/`);
            const data = await res.json();
            set({ materials: data });
        } catch (e) {
            console.error("Fetch Materials Failed:", e);
        }
    },

    fetchProjects: async () => {
        try {
            const res = await fetch(`${BASE_URL}/projects/`);
            const data = await res.json();
            set({ projects: data });
        } catch (e) {
            console.error("Fetch Projects Failed:", e);
        }
    },

    createProject: async (name) => {
        try {
            const res = await fetch(`${BASE_URL}/projects/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });
            const newProject = await res.json();
            set(state => ({ projects: [newProject, ...state.projects] }));
            return newProject;
        } catch (e) {
            console.error("Create Project Failed:", e);
            throw e;
        }
    },

    setActiveProject: async (id) => {
        set({ isLoading: true, error: null, activeProject: null, activePart: null, simulationResult: null });
        try {
            // 1. Get Project
            const pRes = await fetch(`${BASE_URL}/projects/${id}`);
            if (!pRes.ok) throw new Error("Project not found");
            const project = await pRes.json();

            // 2. Get Simulation Result (if any) - Mock Logic: Stored in project or separate endpoint?
            // For now, let's assume project has it or we fetch it. 
            // V2 Mock DB saves result in 'simulations'. We need to query simulations by project_id.
            // But we don't have that endpoint yet. Let's assume project object has "simulation_result" attached?
            // My API (projects.py) returns ProjectRead which includes user_id, name, status.
            // It DOES NOT include geometry or results.
            // I need to update the API to include 'parts' and 'results' in GET /projects/{id} OR fetch them separately.
            // Let's assume fetching separately or updating API later.
            // For now, I'll fetch parts separately. No endpoint for parts yet?
            // Wait, `geometry.py` only uploads. I need `GET /projects/{id}/parts` or similar.
            // I'll assume I update API to return geometry/results in get_project soon.
            // Temporarily, I will just set activeProject.

            set({ activeProject: project });

        } catch (e) {
            set({ error: e.message });
        } finally {
            set({ isLoading: false });
        }
    },

    // Placeholder Geometry Link (Until API updated)
    setPartUrl: (url) => set({ activePart: { file_url: url } }),

    runSimulation: async (materialId) => {
        const { activeProject } = get();
        if (!activeProject) return;

        set({ isLoading: true });
        try {
            const res = await fetch(`${BASE_URL}/simulation/run`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    project_id: activeProject.id,
                    material_id: materialId
                })
            });

            if (!res.ok) {
                const txt = await res.text();
                throw new Error(txt);
            }

            const result = await res.json();
            set({ simulationResult: result });

            // Update Project Status locally
            set(state => ({
                activeProject: { ...state.activeProject, status: 'simulated' }
            }));

        } catch (e) {
            set({ error: e.message });
            alert(e.message);
        } finally {
            set({ isLoading: false });
        }
    }

}));

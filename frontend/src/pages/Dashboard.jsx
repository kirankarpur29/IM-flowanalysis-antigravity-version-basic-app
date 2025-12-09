import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Plus } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useStore } from '../store';

const ProjectCard = ({ project }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-slate-900/50 border border-slate-800 rounded-2xl p-5 hover:border-blue-500/50 hover:shadow-xl hover:shadow-blue-500/10 transition-all cursor-pointer group backdrop-blur-sm"
    >
        <div className="flex justify-between items-start mb-4">
            <div className="w-10 h-10 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400 group-hover:bg-indigo-500 group-hover:text-white transition-colors">
                <span className="font-bold text-lg">{project.name.charAt(0)}</span>
            </div>
            <span className={`text-xs px-2 py-1 rounded-full border ${project.status === 'completed' ? 'border-emerald-500/30 text-emerald-400 bg-emerald-500/10' :
                    'border-amber-500/30 text-amber-400 bg-amber-500/10'
                }`}>
                {project.status || 'Draft'}
            </span>
        </div>
        <h3 className="text-lg font-semibold text-white mb-1 group-hover:text-blue-400 transition-colors truncate">{project.name}</h3>
        <p className="text-sm text-slate-500">Last edited: {new Date(project.created_at || Date.now()).toLocaleDateString()}</p>
    </motion.div>
);

const Dashboard = () => {
    const { projects, fetchProjects, createProject } = useStore();
    const navigate = useNavigate();

    useEffect(() => {
        fetchProjects();
    }, []);

    const handleNewProject = async () => {
        const name = prompt("Project Name:");
        if (name) {
            const newProj = await createProject(name);
            if (newProj && newProj.id) {
                navigate(`/project/${newProj.id}`);
            }
        }
    };

    return (
        <div className="p-8 max-w-7xl mx-auto">
            <header className="flex justify-between items-center mb-10">
                <div>
                    <h2 className="text-3xl font-bold text-white mb-2">Dashboard</h2>
                    <p className="text-slate-400">Welcome back, Engineer.</p>
                </div>
                <button
                    onClick={handleNewProject}
                    className="bg-blue-600 hover:bg-blue-500 text-white px-5 py-2.5 rounded-xl font-medium flex items-center gap-2 transition-all shadow-lg shadow-blue-600/20"
                >
                    <Plus className="w-5 h-5" />
                    New Project
                </button>
            </header>

            {/* Stats Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                {/* Stats Placeholders */}
            </div>

            {/* Projects Grid */}
            <h3 className="text-xl font-semibold text-white mb-6">Recent Projects</h3>
            {projects.length === 0 ? (
                <div className="text-center py-20 bg-slate-900/30 rounded-2xl border border-dashed border-slate-800">
                    <p className="text-slate-500">No projects yet. Create one to get started.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {projects.map(p => (
                        <Link to={`/project/${p.id}`} key={p.id}>
                            <ProjectCard project={p} />
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
};


export default Dashboard;

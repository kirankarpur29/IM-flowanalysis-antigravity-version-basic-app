import React, { useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useStore } from '../store';
import ModelViewer from '../components/3d/ModelViewer';
import {
    ArrowLeft, Upload, Play, CheckCircle2, AlertTriangle,
    Thermometer, Ruler, Scale, Wind, Info
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// --- Sub-Components ---

const StatItem = ({ label, value, unit, icon: Icon }) => (
    <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700 flex items-center justify-between">
        <div className="flex items-center gap-2 text-slate-400">
            <Icon size={14} />
            <span className="text-xs font-medium uppercase">{label}</span>
        </div>
        <div className="text-sm font-bold text-white">
            {value} <span className="text-slate-500 text-xs">{unit}</span>
        </div>
    </div>
);

const ResultCard = ({ result }) => {
    const isFeasible = result.feasibility === 'Feasible';
    const isBorderline = result.feasibility === 'Borderline';

    return (
        <div className="space-y-6">
            {/* Feasibility Badge */}
            <div className={`p-4 rounded-xl border flex items-center gap-3 ${isFeasible ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' :
                    isBorderline ? 'bg-amber-500/10 border-amber-500/30 text-amber-400' :
                        'bg-red-500/10 border-red-500/30 text-red-400'
                }`}>
                {isFeasible ? <CheckCircle2 size={24} /> : <AlertTriangle size={24} />}
                <div>
                    <h4 className="font-bold text-lg">{result.feasibility}</h4>
                    <p className="text-xs opacity-80">Design Status</p>
                </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
                <StatItem label="Fill Time" value={result.fill_time_s} unit="s" icon={Wind} />
                <StatItem label="Cooling" value={result.cooling_time_s} unit="s" icon={Thermometer} />
                <StatItem label="Clamp Force" value={result.clamp_tonnage_tons} unit="T" icon={Scale} />
                <StatItem label="Pressure" value={result.injection_pressure_mpa} unit="MPa" icon={Wind} />
                <StatItem label="Shot Weight" value={result.shot_weight_g} unit="g" icon={Scale} />
                <StatItem label="Cycle Time" value={result.cycle_time_s} unit="s" icon={Thermometer} />
            </div>

            {result.warnings.length > 0 && (
                <div className="bg-amber-500/10 p-3 rounded-lg border border-amber-500/20 text-amber-200 text-xs">
                    <strong className="block mb-1 text-amber-400 uppercase tracking-wide">Warnings</strong>
                    <ul className="list-disc pl-4 space-y-1">
                        {result.warnings.map((w, i) => <li key={i}>{w}</li>)}
                    </ul>
                </div>
            )}
        </div>
    );
};

const Workspace = () => {
    const { id } = useParams();
    const {
        activeProject, isLoading, error,
        setActiveProject, fetchMaterials, materials, runSimulation,
        simulationResult, activePart // Computed via sync usually, but we rely on setActiveProject
    } = useStore();

    // Local state for material selection form
    const [selectedMatId, setSelectedMatId] = React.useState("");

    useEffect(() => {
        setActiveProject(id);
        fetchMaterials();
    }, [id]);

    useEffect(() => {
        // Sync local material selection if project has one
        if (activeProject && activeProject.material_id) {
            setSelectedMatId(activeProject.material_id);
        }
    }, [activeProject]);

    const handleUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        // Manual Fetch upload for now - could move to store
        // We need to reload project after upload
        const formData = new FormData();
        formData.append('file', file);
        formData.append('project_id', id);

        try {
            const res = await fetch('http://127.0.0.1:8000/geometry/upload', {
                method: 'POST',
                body: formData
            });
            if (!res.ok) throw new Error("Upload Failed");
            setActiveProject(id); // Reload to get new part
        } catch (err) {
            alert("Upload Failed: " + err.message);
        }
    };

    const handleRunSim = () => {
        if (!selectedMatId) return alert("Select a material first");
        runSimulation(selectedMatId);
    };

    if (!activeProject && isLoading) return <div className="text-white text-center mt-20">Loading Project...</div>;
    if (error) return <div className="text-red-400 text-center mt-20">Error: {error}</div>;
    if (!activeProject) return null;

    // Derived State
    const hasGeometry = activeProject.parts && activeProject.parts.length > 0;
    const geometryUrl = hasGeometry ? `http://127.0.0.1:8000${activeProject.parts[0].file_url}` : null;
    const result = activeProject.simulation_result || simulationResult; // Prefer fresh result from store or DB

    return (
        <div className="flex h-screen bg-slate-950 text-slate-200 overflow-hidden">
            {/* Top Bar (could be in Layout but we want specific controls) */}

            {/* LEFT PANEL: CONFIG */}
            <div className="w-80 border-r border-slate-800 bg-slate-900/50 backdrop-blur-xl flex flex-col">
                <div className="p-4 border-b border-slate-800 flex items-center gap-3">
                    <Link to="/" className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-white transition-colors">
                        <ArrowLeft size={20} />
                    </Link>
                    <div>
                        <h2 className="font-bold text-white truncate max-w-[180px]">{activeProject.name}</h2>
                        <span className="text-xs text-slate-500 uppercase font-bold tracking-wider">{activeProject.status}</span>
                    </div>
                </div>

                <div className="p-4 space-y-6 overflow-y-auto flex-1 custom-scrollbar">
                    {/* Geometry Section */}
                    <div className="space-y-3">
                        <label className="text-xs text-slate-400 font-bold uppercase tracking-wider flex items-center justify-between">
                            Geometry
                            {hasGeometry && <CheckCircle2 size={14} className="text-emerald-500" />}
                        </label>

                        {!hasGeometry ? (
                            <div className="border-2 border-dashed border-slate-700 hover:border-blue-500 hover:bg-slate-800/50 rounded-xl p-6 transition-all text-center group cursor-pointer relative">
                                <input type="file" onChange={handleUpload} className="absolute inset-0 opacity-0 cursor-pointer" accept=".stl,.step,.stp" />
                                <div className="w-10 h-10 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-3 group-hover:bg-blue-500 group-hover:text-white transition-colors">
                                    <Upload size={20} />
                                </div>
                                <p className="text-sm font-medium text-slate-300">Upload CAD File</p>
                                <p className="text-xs text-slate-500 mt-1">.STL or .STEP (Max 15MB)</p>
                            </div>
                        ) : (
                            <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700 flex items-center gap-3">
                                <div className="w-10 h-10 bg-slate-900 rounded-lg border border-slate-700 flex items-center justify-center text-blue-400">
                                    <BoxIcon />
                                </div>
                                <div className="overflow-hidden">
                                    <p className="text-sm font-medium text-white truncate">{activeProject.parts[0].file_name}</p>
                                    <p className="text-xs text-slate-500">{(activeProject.parts[0].volume / 1000).toFixed(1)} cm³</p>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Material Section */}
                    <div className="space-y-3">
                        <label className="text-xs text-slate-400 font-bold uppercase tracking-wider">Material</label>
                        <select
                            value={selectedMatId}
                            onChange={(e) => setSelectedMatId(e.target.value)}
                            className="w-full bg-slate-800 border border-slate-700 text-white text-sm rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none"
                        >
                            <option value="">Select Material...</option>
                            {materials.map(m => (
                                <option key={m.id} value={m.id}>{m.name}</option>
                            ))}
                        </select>
                        {/* Material Details (Mini) */}
                        {selectedMatId && materials.find(m => m.id === selectedMatId) && (
                            <div className="bg-slate-800/30 p-3 rounded text-xs text-slate-400 space-y-1">
                                {(() => {
                                    const mat = materials.find(m => m.id === selectedMatId);
                                    return (
                                        <>
                                            <div className="flex justify-between"><span>Density:</span> <span className="text-slate-300">{mat.density_g_cm3} g/cm³</span></div>
                                            <div className="flex justify-between"><span>Melt Temp:</span> <span className="text-slate-300">{mat.melt_temp_c}°C</span></div>
                                            <div className="flex justify-between"><span>Shrinkage:</span> <span className="text-slate-300">{(mat.shrinkage * 100).toFixed(1)}%</span></div>
                                        </>
                                    )
                                })()}
                            </div>
                        )}
                    </div>

                    {/* Action Button */}
                    <div className="pt-4">
                        <button
                            onClick={handleRunSim}
                            disabled={!hasGeometry || !selectedMatId || isLoading}
                            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold py-4 rounded-xl shadow-lg shadow-blue-600/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all hover:-translate-y-0.5"
                        >
                            {isLoading ? (
                                <span className="animate-pulse">Analyzing...</span>
                            ) : (
                                <>
                                    <Play size={18} fill="currentColor" />
                                    Run Simulation
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </div>

            {/* CENTER: 3D VIEWER */}
            <div className="flex-1 relative bg-slate-950">
                <ModelViewer url={geometryUrl} />
            </div>

            {/* RIGHT PANEL: RESULTS */}
            <div className="w-80 border-l border-slate-800 bg-slate-900/50 backdrop-blur-xl flex flex-col p-4 overflow-y-auto">
                <h3 className="text-lg font-bold text-white mb-6">Simulation Results</h3>

                {result ? (
                    <ResultCard result={result} />
                ) : (
                    <div className="flex-1 flex flex-col items-center justify-center text-slate-500 opacity-60">
                        <Info size={48} className="mb-4" />
                        <p className="text-center text-sm">Run a simulation<br />to view analysis.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

const BoxIcon = () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
);

export default Workspace;

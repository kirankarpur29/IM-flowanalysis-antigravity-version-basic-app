import React from 'react';
import { Play, Settings, Box, RotateCw, CheckCircle, AlertTriangle, XCircle, Download } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const ResultsPanel = ({ result, stats, selectedMaterial, selectedMachine, fileName, onExport }) => {
    if (!result) return null;

    const metrics = [
        { label: 'Fill Time', value: `${result.fill_time_s.toFixed(2)}s`, icon: <Play size={20} className="text-blue-500" />, color: 'blue' },
        { label: 'Inj. Pressure', value: `${result.injection_pressure_mpa.toFixed(0)} MPa`, icon: <Settings size={20} className="text-purple-500" />, color: 'purple' },
        { label: 'Clamp Force', value: `${result.clamp_tonnage_tons.toFixed(0)} Tons`, icon: <Box size={20} className="text-orange-500" />, color: 'orange' },
        { label: 'Cycle Time', value: `${result.cycle_time_s.toFixed(1)}s`, icon: <RotateCw size={20} className="text-green-500" />, color: 'green' },
    ];

    return (
        <AnimatePresence>
            <motion.div
                initial={{ y: '100%' }}
                animate={{ y: 0 }}
                exit={{ y: '100%' }}
                transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                className="absolute bottom-0 left-0 right-0 bg-white/90 backdrop-blur-xl border-t border-white/20 shadow-[0_-10px_40px_rgba(0,0,0,0.1)] z-10 max-h-[45vh] overflow-y-auto"
            >
                <div className="max-w-7xl mx-auto p-8">

                    {/* Header */}
                    <div className="flex items-center justify-between mb-8">
                        <div>
                            <h2 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
                                Analysis Results
                                <span className="text-sm font-medium text-slate-400 bg-slate-100 px-2 py-1 rounded-md">Heuristic Estimate</span>
                            </h2>
                        </div>

                        <div className="flex items-center gap-4">
                            <div className={`flex items-center gap-2 px-5 py-2.5 rounded-full font-bold text-sm border shadow-sm
                ${result.feasibility === 'Feasible' ? 'bg-green-50 text-green-700 border-green-200' :
                                    result.feasibility === 'Borderline' ? 'bg-yellow-50 text-yellow-700 border-yellow-200' : 'bg-red-50 text-red-700 border-red-200'}`}>
                                {result.feasibility === 'Feasible' && <CheckCircle size={18} />}
                                {result.feasibility === 'Borderline' && <AlertTriangle size={18} />}
                                {result.feasibility === 'Not Recommended' && <XCircle size={18} />}
                                {result.feasibility}
                            </div>

                            <button
                                onClick={onExport}
                                className="flex items-center gap-2 px-5 py-2.5 bg-slate-800 text-white rounded-xl text-sm font-bold hover:bg-slate-900 transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0"
                            >
                                <Download size={18} />
                                Export PDF
                            </button>
                        </div>
                    </div>

                    {/* Metrics Grid */}
                    <div className="grid grid-cols-4 gap-6">
                        {metrics.map((metric, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: i * 0.1 }}
                                className="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm hover:shadow-md transition-shadow"
                            >
                                <div className="flex items-center gap-3 mb-3">
                                    <div className={`p-2 rounded-lg bg-${metric.color}-50`}>
                                        {metric.icon}
                                    </div>
                                    <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">{metric.label}</span>
                                </div>
                                <p className="text-3xl font-mono font-bold text-slate-800 tracking-tight">{metric.value}</p>
                            </motion.div>
                        ))}
                    </div>

                    {/* Recommendations & Warnings */}
                    <div className="grid grid-cols-2 gap-6 mt-8">
                        {/* Warnings */}
                        {result.warnings.length > 0 && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ delay: 0.4 }}
                                className="bg-orange-50 border border-orange-100 rounded-2xl p-6"
                            >
                                <h3 className="text-sm font-bold text-orange-800 mb-4 flex items-center gap-2 uppercase tracking-wide">
                                    <AlertTriangle size={18} />
                                    Warnings Detected
                                </h3>
                                <ul className="space-y-3">
                                    {result.warnings.map((w, i) => (
                                        <li key={i} className="text-sm text-orange-800 font-medium flex items-start gap-3 bg-white/50 p-3 rounded-lg">
                                            <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-orange-500 shrink-0"></span>
                                            {w}
                                        </li>
                                    ))}
                                </ul>
                            </motion.div>
                        )}

                        {/* Recommendations */}
                        {result.recommendations.length > 0 && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ delay: 0.5 }}
                                className="bg-blue-50 border border-blue-100 rounded-2xl p-6"
                            >
                                <h3 className="text-sm font-bold text-blue-800 mb-4 flex items-center gap-2 uppercase tracking-wide">
                                    <CheckCircle size={18} />
                                    Recommendations
                                </h3>
                                <ul className="space-y-3">
                                    {result.recommendations.map((r, i) => (
                                        <li key={i} className="text-sm text-blue-800 font-medium flex items-start gap-3 bg-white/50 p-3 rounded-lg">
                                            <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-blue-500 shrink-0"></span>
                                            {r}
                                        </li>
                                    ))}
                                </ul>
                            </motion.div>
                        )}
                    </div>

                </div>
            </motion.div>
        </AnimatePresence>
    );
};

export default ResultsPanel;

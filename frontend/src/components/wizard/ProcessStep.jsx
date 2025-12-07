import React from 'react';
import { Settings, ChevronRight } from 'lucide-react';
import { motion } from 'framer-motion';

const ProcessStep = ({
    active,
    materials,
    machines,
    selectedMaterial,
    selectedMachine,
    onMaterialSelect,
    onMachineSelect
}) => {
    if (!active) return null;

    return (
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="space-y-6"
        >
            <div className="flex items-center gap-2 mb-4 pt-4 border-t border-slate-100">
                <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wide flex items-center gap-2">
                    <Settings size={16} className="text-indigo-500" />
                    Process Settings
                </h2>
            </div>

            <div className="space-y-4">
                <div>
                    <label className="block text-xs font-bold text-slate-500 mb-1.5">Material Selection</label>
                    <div className="relative">
                        <select
                            className="w-full p-3 bg-white border border-slate-200 rounded-xl text-sm text-slate-700 font-medium focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none appearance-none shadow-sm transition-shadow cursor-pointer hover:border-indigo-300"
                            value={selectedMaterial}
                            onChange={(e) => onMaterialSelect(e.target.value)}
                        >
                            <option value="">Select Material...</option>
                            {materials.map(m => (
                                <option key={m.id} value={m.id}>{m.name} ({m.family})</option>
                            ))}
                        </select>
                        <div className="absolute right-3 top-3.5 pointer-events-none text-slate-400">
                            <ChevronRight size={16} className="rotate-90" />
                        </div>
                    </div>
                </div>

                <div>
                    <label className="block text-xs font-bold text-slate-500 mb-1.5">Machine (Optional)</label>
                    <div className="relative">
                        <select
                            className="w-full p-3 bg-white border border-slate-200 rounded-xl text-sm text-slate-700 font-medium focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none appearance-none shadow-sm transition-shadow cursor-pointer hover:border-indigo-300"
                            value={selectedMachine}
                            onChange={(e) => onMachineSelect(e.target.value)}
                        >
                            <option value="">Auto-Select based on Tonnage</option>
                            {machines.map(m => (
                                <option key={m.id} value={m.id}>{m.name} ({m.clamp_tonnage}T)</option>
                            ))}
                        </select>
                        <div className="absolute right-3 top-3.5 pointer-events-none text-slate-400">
                            <ChevronRight size={16} className="rotate-90" />
                        </div>
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default ProcessStep;

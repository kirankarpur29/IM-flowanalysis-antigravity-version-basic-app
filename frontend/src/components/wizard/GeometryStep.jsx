import React from 'react';
import { Upload, RotateCw, MousePointer, CheckCircle, Box, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

const GeometryStep = ({
    active,
    uploading,
    fileName,
    stats,
    fileUrl,
    onFileUpload,
    onRotate,
    onNext
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
            <div className="flex items-center gap-2 mb-4">
                <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wide flex items-center gap-2">
                    <Box size={16} className="text-indigo-500" />
                    Geometry Upload
                </h2>
            </div>

            {/* Upload Box */}
            <div className="relative group">
                <input
                    type="file"
                    accept=".stl,.step,.stp"
                    onChange={onFileUpload}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                    disabled={uploading}
                />
                <div className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300
          ${uploading
                        ? 'border-indigo-300 bg-indigo-50/50'
                        : 'border-slate-200 bg-slate-50/50 hover:border-indigo-400 hover:bg-indigo-50/30 hover:shadow-lg hover:shadow-indigo-100/50'}`}>

                    {uploading ? (
                        <div className="flex flex-col items-center">
                            <div className="w-8 h-8 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin mb-3"></div>
                            <p className="text-sm text-indigo-700 font-semibold">Processing Geometry...</p>
                            <p className="text-xs text-indigo-400 mt-1">Converting & Meshing</p>
                        </div>
                    ) : (
                        <>
                            <div className="mx-auto w-12 h-12 bg-white text-indigo-500 rounded-xl shadow-sm flex items-center justify-center mb-4 group-hover:scale-110 group-hover:text-indigo-600 transition-transform">
                                <Upload size={24} />
                            </div>
                            <p className="text-sm font-semibold text-slate-700">Click to Upload Model</p>
                            <p className="text-xs text-slate-400 mt-1">Supports .STL and .STEP</p>
                        </>
                    )}
                </div>
            </div>

            {/* File Info & Stats */}
            {fileName && (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white rounded-xl border border-slate-100 shadow-sm overflow-hidden"
                >
                    <div className="px-4 py-3 bg-slate-50/80 border-b border-slate-100 flex items-center justify-between">
                        <span className="text-xs font-semibold text-slate-700 truncate max-w-[180px]" title={fileName}>{fileName}</span>
                        <span className="text-[10px] bg-green-100 text-green-700 px-2 py-1 rounded-full font-bold flex items-center gap-1">
                            <CheckCircle size={10} /> Ready
                        </span>
                    </div>

                    {stats && (
                        <div className="p-4 grid grid-cols-2 gap-4">
                            <div>
                                <span className="text-[10px] text-slate-400 uppercase font-bold">Volume</span>
                                <p className="font-mono text-sm font-medium text-slate-700">{(stats.volume_mm3 / 1000).toFixed(1)} <span className="text-xs text-slate-400">cm³</span></p>
                            </div>
                            <div>
                                <span className="text-[10px] text-slate-400 uppercase font-bold">Area</span>
                                <p className="font-mono text-sm font-medium text-slate-700">{(stats.projected_area_mm2 / 100).toFixed(1)} <span className="text-xs text-slate-400">cm²</span></p>
                            </div>
                            <div className="col-span-2">
                                <span className="text-[10px] text-slate-400 uppercase font-bold">Bounding Box</span>
                                <p className="font-mono text-sm font-medium text-slate-700">
                                    {stats.bbox.x.toFixed(0)} x {stats.bbox.y.toFixed(0)} x {stats.bbox.z.toFixed(0)} <span className="text-xs text-slate-400">mm</span>
                                </p>
                            </div>
                        </div>
                    )}
                </motion.div>
            )}

            {/* Tools: Orientation (Simplified) */}
            {fileName && !stats?.isManual && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.2 }}
                    className="space-y-4 pt-2"
                >
                    <div>
                        <div className="flex justify-between items-center mb-2">
                            <p className="text-[10px] font-bold text-slate-400 uppercase">Orientation</p>
                            <span className="text-[10px] text-indigo-500 font-medium">Align Z to Draw Direction</span>
                        </div>
                        <div className="flex gap-2">
                            {['X', 'Y', 'Z'].map((axis) => (
                                <button
                                    key={axis}
                                    onClick={() => onRotate(axis === 'X' ? 90 : 0, axis === 'Y' ? 90 : 0, axis === 'Z' ? 90 : 0)}
                                    className="flex-1 bg-white border border-slate-200 text-slate-600 text-xs py-2 rounded-lg hover:bg-indigo-50 hover:border-indigo-200 hover:text-indigo-600 transition-all flex items-center justify-center gap-1 font-medium shadow-sm"
                                >
                                    <RotateCw size={12} /> {axis}
                                </button>
                            ))}
                        </div>
                    </div>

                    <p className="text-xs text-slate-400 text-center italic">Gate location will be optimized automatically.</p>

                    <button
                        onClick={onNext}
                        className="w-full mt-2 flex items-center justify-center gap-1 text-xs font-bold text-indigo-600 hover:text-indigo-800 transition-colors group"
                    >
                        Next: Process Settings <ArrowRight size={12} className="group-hover:translate-x-1 transition-transform" />
                    </button>
                </motion.div>
            )}
        </motion.div>
    );
};

export default GeometryStep;

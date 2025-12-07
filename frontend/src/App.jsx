import React, { useState, useEffect } from 'react';
import { Layers, Play } from 'lucide-react';
import Viewer3D from './components/3d/Viewer3D';
import GeometryStep from './components/wizard/GeometryStep';
import ProcessStep from './components/wizard/ProcessStep';
import ResultsPanel from './components/ResultsPanel';
import { AnimatePresence } from 'framer-motion';

function App() {
  const [fileUrl, setFileUrl] = useState(null);
  const [fileName, setFileName] = useState(null);
  const [stats, setStats] = useState(null);

  const [materials, setMaterials] = useState([]);
  const [machines, setMachines] = useState([]);
  const [selectedMaterial, setSelectedMaterial] = useState("");
  const [selectedMachine, setSelectedMachine] = useState("");

  const [simulationResult, setSimulationResult] = useState(null);
  const [gateLocation, setGateLocation] = useState(null);
  const [isGateSelectionMode, setIsGateSelectionMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [activeStep, setActiveStep] = useState(1); // 1: Geometry, 2: Process, 3: Results

  useEffect(() => {
    fetch('/materials/').then(res => res.json()).then(setMaterials).catch(console.error);
    fetch('/machines/').then(res => res.json()).then(setMachines).catch(console.error);
  }, []);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    setFileName(file.name);
    setStats(null);
    setSimulationResult(null);
    setActiveStep(1);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/geometry/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        let errorMsg = 'Upload failed';
        try {
          const err = await response.json();
          if (err && err.detail) errorMsg = err.detail;
        } catch (e) {
          console.error("Failed to parse error JSON:", e);
          errorMsg = `Upload failed with status ${response.status}`;
        }
        throw new Error(errorMsg);
      }

      const data = await response.json();
      if (!data || !data.url) {
        throw new Error("Invalid response from server");
      }

      setFileUrl(data.url);
      setStats(data.stats);

    } catch (error) {
      console.error("Error uploading file:", error);
      alert(error.message);
      setFileName(null);
    } finally {
      setUploading(false);
    }
  };

  const handleRotate = async (x, y, z) => {
    if (!fileUrl) return;
    const currentFileName = fileUrl.split('/').pop();

    try {
      const response = await fetch('/geometry/transform', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filename: currentFileName,
          rotation_x: x,
          rotation_y: y,
          rotation_z: z
        })
      });

      if (!response.ok) throw new Error('Rotation failed');

      const data = await response.json();
      setFileUrl(`${data.url}?t=${Date.now()}`);
      setStats(data.stats);
      setSimulationResult(null);

    } catch (error) {
      console.error("Rotation error:", error);
      alert("Failed to rotate geometry.");
    }
  };

  const runSimulation = async () => {
    if (!stats || !selectedMaterial) {
      alert("Please upload geometry and select a material.");
      return;
    }

    setLoading(true);
    try {
      let flowLengthOverride = null;
      if (gateLocation && stats.bbox) {
        const { x, y, z } = stats.bbox;
        const corners = [
          { cx: -x / 2, cy: -y / 2, cz: -z / 2 },
          { cx: x / 2, cy: -y / 2, cz: -z / 2 },
          { cx: -x / 2, cy: y / 2, cz: -z / 2 },
          { cx: x / 2, cy: y / 2, cz: -z / 2 },
          { cx: -x / 2, cy: -y / 2, cz: z / 2 },
          { cx: x / 2, cy: -y / 2, cz: z / 2 },
          { cx: -x / 2, cy: y / 2, cz: z / 2 },
          { cx: x / 2, cy: y / 2, cz: z / 2 },
        ];

        let maxDist = 0;
        corners.forEach(c => {
          const dist = Math.sqrt(
            Math.pow(c.cx - gateLocation.x, 2) +
            Math.pow(c.cy - gateLocation.y, 2) +
            Math.pow(c.cz - gateLocation.z, 2)
          );
          if (dist > maxDist) maxDist = dist;
        });
        flowLengthOverride = maxDist;
      }

      const response = await fetch('/simulation/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          material_id: parseInt(selectedMaterial),
          machine_id: selectedMachine ? parseInt(selectedMachine) : null,
          geometry_stats: stats,
          flow_length_mm: flowLengthOverride
        })
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`Simulation failed: ${errText}`);
      }

      const result = await response.json();
      setSimulationResult(result);
      setActiveStep(3);

    } catch (error) {
      console.error(error);
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const response = await fetch('/reports/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          material_id: parseInt(selectedMaterial),
          machine_id: selectedMachine ? parseInt(selectedMachine) : null,
          geometry_stats: stats,
          simulation_result: simulationResult,
          project_name: fileName.split('.')[0],
          designer_name: "User"
        })
      });
      if (!response.ok) throw new Error('Report generation failed');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Report_${fileName.split('.')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (error) {
      console.error(error);
      alert("Failed to generate report.");
    }
  };

  return (
    <div className="flex h-screen bg-slate-50 font-sans text-slate-900 overflow-hidden selection:bg-indigo-100 selection:text-indigo-700">

      {/* Sidebar - Glassmorphism & Vibrant */}
      <div className="w-96 bg-white/80 backdrop-blur-xl shadow-2xl z-20 flex flex-col border-r border-white/20 relative">
        {/* Decorative Background Blob */}
        <div className="absolute top-0 left-0 w-full h-64 bg-gradient-to-b from-indigo-50/50 to-transparent pointer-events-none"></div>

        {/* Header */}
        <div className="p-8 relative">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-violet-600 rounded-xl shadow-lg shadow-indigo-500/30 flex items-center justify-center text-white font-bold text-lg">
              <Layers size={20} />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-800 tracking-tight">Mold Flow <span className="text-indigo-600">Lite</span></h1>
            </div>
          </div>
          <p className="text-sm text-slate-500 font-medium ml-1">Rapid Feasibility Analysis</p>
        </div>

        {/* Wizard Steps */}
        <div className="px-8 mb-6">
          <div className="flex items-center justify-between relative">
            <div className="absolute left-0 top-1/2 w-full h-0.5 bg-slate-100 -z-10"></div>
            {[1, 2, 3].map((step) => (
              <div key={step} className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300
                ${activeStep >= step ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200 scale-110' : 'bg-slate-100 text-slate-400'}`}>
                {step}
              </div>
            ))}
          </div>
          <div className="flex justify-between text-[10px] font-bold text-slate-400 uppercase mt-2 tracking-wider">
            <span>Geometry</span>
            <span>Process</span>
            <span>Results</span>
          </div>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto px-8 py-4 space-y-8 custom-scrollbar relative">
          <AnimatePresence mode="wait">
            {activeStep === 1 && (
              <GeometryStep
                key="step1"
                active={activeStep === 1}
                uploading={uploading}
                fileName={fileName}
                stats={stats}
                fileUrl={fileUrl}
                gateLocation={gateLocation}
                isGateSelectionMode={isGateSelectionMode}
                onFileUpload={handleFileUpload}
                onRotate={handleRotate}
                onToggleGateMode={() => setIsGateSelectionMode(!isGateSelectionMode)}
                onNext={() => setActiveStep(2)}
              />
            )}

            {activeStep >= 2 && (
              <ProcessStep
                key="step2"
                active={activeStep >= 2}
                materials={materials}
                machines={machines}
                selectedMaterial={selectedMaterial}
                selectedMachine={selectedMachine}
                onMaterialSelect={setSelectedMaterial}
                onMachineSelect={setSelectedMachine}
              />
            )}
          </AnimatePresence>
        </div>

        {/* Footer Action */}
        <div className="p-8 border-t border-slate-100 bg-white/50 backdrop-blur-sm">
          <button
            onClick={runSimulation}
            disabled={loading || !stats || !selectedMaterial}
            className="w-full bg-gradient-to-r from-indigo-600 to-violet-600 text-white py-4 px-6 rounded-xl font-bold text-sm shadow-xl shadow-indigo-500/30 hover:shadow-indigo-500/50 hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none disabled:translate-y-0 flex items-center justify-center gap-3"
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                Running Simulation...
              </>
            ) : (
              <>
                <Play size={20} fill="currentColor" />
                Run Analysis
              </>
            )}
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 relative flex flex-col bg-slate-100">

        {/* 3D Viewer */}
        <div className="flex-1 relative">
          {/* 3D Viewer - DISABLED AS PER USER REQUEST */}
          {/* <Viewer3D
            fileUrl={fileUrl}
            gateLocation={gateLocation}
            isGateSelectionMode={isGateSelectionMode}
            onGateSelect={(point) => {
              setGateLocation(point);
              setIsGateSelectionMode(false);
            }}
          /> */}

          <div className="w-full h-full bg-slate-100 flex items-center justify-center flex-col p-8 text-center">
            <div className="w-24 h-24 bg-indigo-50 rounded-full flex items-center justify-center mb-6">
              <Layers size={48} className="text-indigo-400" />
            </div>
            <h3 className="text-xl font-bold text-slate-700 mb-2">3D Viewer Disabled</h3>
            <p className="text-slate-500 max-w-md">
              The 3D visualization is currently disabled.
              You can still proceed with the analysis using the wizard on the left.
            </p>
            {fileUrl && (
              <div className="mt-6 bg-white px-4 py-2 rounded-lg shadow-sm border border-slate-200">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Loaded Model</p>
                <p className="text-indigo-600 font-medium truncate max-w-[200px]">{fileName}</p>
              </div>
            )}
          </div>

          {/* Legend Overlay */}
          {gateLocation && (
            <div className="absolute top-8 right-8 bg-white/90 backdrop-blur-md p-5 rounded-2xl shadow-xl border border-white/50 w-40">
              <p className="text-[10px] font-bold text-slate-400 uppercase mb-3 text-center tracking-wider">Flow Distance</p>
              <div className="flex items-center gap-4">
                <div className="h-32 w-4 bg-gradient-to-t from-blue-500 via-green-500 to-red-500 rounded-full shadow-inner"></div>
                <div className="flex flex-col justify-between h-32 text-[10px] font-bold text-slate-600">
                  <span>Far</span>
                  <span>Near</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Results Panel (Slide Up) */}
        <ResultsPanel
          result={simulationResult}
          stats={stats}
          selectedMaterial={selectedMaterial}
          selectedMachine={selectedMachine}
          fileName={fileName}
          onExport={handleExport}
        />
      </div>
    </div>
  );
}

export default App;

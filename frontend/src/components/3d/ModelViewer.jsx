import React, { Suspense, useMemo } from 'react';
import { Canvas, useLoader } from '@react-three/fiber';
import { OrbitControls, Stage, Html, Center } from '@react-three/drei';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader';
import * as THREE from 'three';

// 1. Model Component
const Model = ({ url, color = "#6366f1" }) => {
    // Use useLoader with STLLoader
    // Note: STLLoader doesn't support .step, backend MUST convert to .stl
    const geometry = useLoader(STLLoader, url);

    // Memoize geometry processing (centering/normals) if needed, 
    // but Stage handles centering, so we just focus on normals
    useMemo(() => {
        if (geometry) {
            geometry.computeVertexNormals();
        }
    }, [geometry]);

    return (
        <mesh geometry={geometry} castShadow receiveShadow>
            <meshStandardMaterial
                color={color}
                roughness={0.3}
                metalness={0.2}
                envMapIntensity={1}
            />
        </mesh>
    );
};

// 2. Error Fallback
const ErrorFallback = ({ error }) => (
    <Html center>
        <div className="bg-red-50 p-4 rounded-xl border border-red-100 shadow-xl text-center min-w-[200px]">
            <div className="text-red-500 mb-2">⚠️ Failed to Load 3D Model</div>
            <code className="text-[10px] text-red-400 block mb-2 max-w-xs truncate">{error.message}</code>
        </div>
    </Html>
);

// 3. Loading Spinner
const Loader = () => (
    <Html center>
        <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin"></div>
            <span className="text-xs font-bold text-slate-500 tracking-wider uppercase">Loading Geometry...</span>
        </div>
    </Html>
);

// 4. Main Component
const ModelViewer = ({ url }) => {
    // Key forces remount on URL change to clear caches/errors
    return (
        <div className="w-full h-full bg-slate-950 relative overflow-hidden rounded-xl shadow-inner">
            {/* Background Gradient */}
            <div className="absolute inset-0 bg-gradient-to-b from-slate-900 to-slate-950 pointer-events-none" />

            {!url ? (
                <div className="absolute inset-0 flex items-center justify-center text-slate-700">
                    <div className="text-center">
                        <p className="font-bold text-lg mb-1">No Model Selected</p>
                        <p className="text-sm">Upload geometry to view.</p>
                    </div>
                </div>
            ) : (
                <ErrorBoundary fallback={ErrorFallback}>
                    <Canvas shadows dpr={[1, 2]} camera={{ fov: 45 }}>
                        <Suspense fallback={<Loader />}>
                            <Stage environment="city" intensity={0.5} contactShadow={false}>
                                <Model url={url} />
                            </Stage>
                        </Suspense>
                        <OrbitControls makeDefault minPolarAngle={0} maxPolarAngle={Math.PI / 1.5} />
                    </Canvas>
                </ErrorBoundary>
            )}
        </div>
    );
};

// Simple Error Boundary Wrapper since React ErrorBoundary is class-based
class ErrorBoundary extends React.Component {
    state = { hasError: false, error: null };
    static getDerivedStateFromError(error) { return { hasError: true, error }; }
    render() {
        if (this.state.hasError) return <this.props.fallback error={this.state.error} />;
        return this.props.children;
    }
}

export default ModelViewer;

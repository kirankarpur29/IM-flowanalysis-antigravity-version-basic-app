import React, { useRef, useEffect, Suspense } from 'react';
import { Canvas, useLoader } from '@react-three/fiber';
import { OrbitControls, Center, Html } from '@react-three/drei';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader';
import * as THREE from 'three';

// ... (Model component remains same)

function Model({ url, gateLocation, isGateSelectionMode, onGateSelect }) {
    const originalGeometry = useLoader(STLLoader, url);
    const [geometry, setGeometry] = React.useState(null);

    useEffect(() => {
        if (originalGeometry) {
            const cloned = originalGeometry.clone();
            cloned.computeVertexNormals();
            setGeometry(cloned);
        }
    }, [originalGeometry]);

    const meshRef = useRef();

    // Reset colors when geometry changes
    useEffect(() => {
        if (meshRef.current) {
            meshRef.current.geometry.computeVertexNormals();
            // Reset to default color if no gate
            if (!gateLocation) {
                const positions = geometry.attributes.position;
                const count = positions.count;
                const colors = new Float32Array(count * 3);
                for (let i = 0; i < count * 3; i += 3) {
                    colors[i] = 0.8;     // R (Light Gray)
                    colors[i + 1] = 0.8; // G
                    colors[i + 2] = 0.8; // B
                }
                geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
            }
        }
    }, [geometry, gateLocation]);

    // Apply Heatmap when gateLocation changes
    useEffect(() => {
        if (gateLocation && meshRef.current) {
            const positions = geometry.attributes.position.array;
            const count = geometry.attributes.position.count;
            const colors = new Float32Array(count * 3);

            // 1. Find max distance for normalization
            let maxDist = 0;
            const gate = new THREE.Vector3(gateLocation.x, gateLocation.y, gateLocation.z);
            const tempVec = new THREE.Vector3();

            for (let i = 0; i < count; i++) {
                tempVec.set(positions[i * 3], positions[i * 3 + 1], positions[i * 3 + 2]);
                const dist = tempVec.distanceTo(gate);
                if (dist > maxDist) maxDist = dist;
            }

            // 2. Color vertices based on distance (Blue -> Green -> Red)
            const color = new THREE.Color();
            for (let i = 0; i < count; i++) {
                tempVec.set(positions[i * 3], positions[i * 3 + 1], positions[i * 3 + 2]);
                const dist = tempVec.distanceTo(gate);
                const t = dist / maxDist; // 0.0 to 1.0

                // Simple Heatmap: Blue (0) -> Red (1)
                color.setHSL(0.66 * (1.0 - t), 1.0, 0.5);

                colors[i * 3] = color.r;
                colors[i * 3 + 1] = color.g;
                colors[i * 3 + 2] = color.b;
            }

            geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
            // eslint-disable-next-line react-hooks/rules-of-hooks, react-hooks/exhaustive-deps
            geometry.attributes.color.needsUpdate = true;
        }
    }, [gateLocation, geometry]);

    const handleClick = (event) => {
        if (isGateSelectionMode) {
            event.stopPropagation();
            onGateSelect(event.point);
        }
    };

    return (
        <mesh
            ref={meshRef}
            geometry={geometry}
            onClick={handleClick}
            rotation={[-Math.PI / 2, 0, 0]}
        >
            <meshStandardMaterial vertexColors={true} roughness={0.5} metalness={0.1} />
        </mesh>
    );
}

// Simple Error Boundary Component
class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error("Viewer3D Error:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <Html center>
                    <div className="bg-red-50 p-4 rounded-lg border border-red-200 text-center w-64">
                        <h3 className="text-red-800 font-bold mb-2">Error Loading Model</h3>
                        <p className="text-red-600 text-xs mb-4 break-words">{this.state.error && this.state.error.message}</p>
                        <button
                            onClick={() => this.setState({ hasError: false })}
                            className="text-xs bg-red-100 text-red-700 px-3 py-1 rounded hover:bg-red-200"
                        >
                            Try Again
                        </button>
                    </div>
                </Html>
            );
        }
        return this.props.children;
    }
}

const Viewer3D = ({ fileUrl, gateLocation, isGateSelectionMode, onGateSelect }) => {
    return (
        <div className="w-full h-full bg-slate-900 relative">
            {/* Empty State Overlay */}
            {!fileUrl && (
                <div className="absolute inset-0 flex items-center justify-center bg-slate-50/90 backdrop-blur-sm z-10">
                    <div className="text-center p-8 bg-white rounded-2xl shadow-xl border border-slate-100 max-w-md">
                        <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
                        </div>
                        <h3 className="text-xl font-bold text-slate-800 mb-2">Ready to Analyze</h3>
                        <p className="text-slate-500">Upload a 3D model (.stl or .step) from the sidebar to begin your mold flow analysis.</p>
                    </div>
                </div>
            )}

            <Canvas camera={{ position: [150, 150, 150], fov: 50 }}>
                <ambientLight intensity={0.5} />
                <directionalLight position={[10, 10, 5]} intensity={1} />
                <directionalLight position={[-10, -10, -5]} intensity={0.5} />
                <Center>
                    <ErrorBoundary>
                        <Suspense fallback={<Html center><div className="text-white font-bold">Loading 3D Model...</div></Html>}>
                            {fileUrl && (
                                <Model
                                    url={fileUrl}
                                    gateLocation={gateLocation}
                                    isGateSelectionMode={isGateSelectionMode}
                                    onGateSelect={onGateSelect}
                                />
                            )}
                            {gateLocation && (
                                <mesh position={[gateLocation.x, gateLocation.y, gateLocation.z]}>
                                    <sphereGeometry args={[2, 16, 16]} />
                                    <meshBasicMaterial color="yellow" />
                                </mesh>
                            )}
                        </Suspense>
                    </ErrorBoundary>
                </Center>
                <OrbitControls makeDefault />
            </Canvas>
        </div>
    );
};

export default Viewer3D;

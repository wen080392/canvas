import React, { useCallback, useEffect, useState } from 'react';
import ReactFlow, {
    MiniMap,
    Controls,
    Background,
    useNodesState,
    useEdgesState,
    addEdge,
    MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import Shell from "@/components/layout/Shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { RefreshCw, Download, Database, Server, Globe, Shield, HardDrive } from "lucide-react";

// Custom Node Component for nicer UI
const CustomNode = ({ data, selected }) => {
    const Icon = data.icon || Server;
    return (
        <div className={`px-4 py-2 shadow-md rounded-md bg-card border-2 min-w-[150px] transition-colors ${selected ? 'border-primary' : 'border-border'}`}>
            <div className="flex items-center">
                <div className="rounded-full w-8 h-8 flex items-center justify-center bg-muted mr-3">
                    <Icon className="w-4 h-4 text-primary" />
                </div>
                <div className="ml-2">
                    <div className="text-sm font-bold text-foreground">{data.label}</div>
                    <div className="text-xs text-muted-foreground">{data.type}</div>
                </div>
            </div>
            {/* Handle connectors would be here if we were building custom handles, 
            but for simple visualization default handles are hidden or auto-placed */}
        </div>
    );
};

const nodeTypes = {
    custom: CustomNode,
};

// Initial Mock Data
const initialNodes = [
    { id: '1', type: 'input', data: { label: 'Internet', type: 'Gateway', icon: Globe }, position: { x: 250, y: 0 } },
    { id: '2', data: { label: 'VPC', type: 'Network', icon: Globe }, position: { x: 250, y: 100 } },
    { id: '3', data: { label: 'Public Subnet', type: 'Subnet', icon: HardDrive }, position: { x: 100, y: 200 } },
    { id: '4', data: { label: 'Private Subnet', type: 'Subnet', icon: Shield }, position: { x: 400, y: 200 } },
    { id: '5', data: { label: 'Web Server', type: 'EC2', icon: Server }, position: { x: 100, y: 300 } },
    { id: '6', data: { label: 'App Server', type: 'EC2', icon: Server }, position: { x: 400, y: 300 } },
    { id: '7', data: { label: 'DB Master', type: 'RDS', icon: Database }, position: { x: 400, y: 400 } },
];

const initialEdges = [
    { id: 'e1-2', source: '1', target: '2', animated: true },
    { id: 'e2-3', source: '2', target: '3' },
    { id: 'e2-4', source: '2', target: '4' },
    { id: 'e3-5', source: '3', target: '5' },
    { id: 'e4-6', source: '4', target: '6' },
    { id: 'e6-7', source: '6', target: '7', animated: true, style: { stroke: '#ef4444' } }, // Dependency
];

export default function InfrastructureGraph() {
    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
    const [loading, setLoading] = useState(false);

    const fileInputRef = React.useRef(null);
    const [uploading, setUploading] = useState(false);

    const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

    // Handle File Upload
    const handleFileUpload = async (event) => {
        const file = event.target.files?.[0];
        if (!file) return;

        setUploading(true);
        const reader = new FileReader();

        reader.onload = async (e) => {
            const content = e.target?.result;
            if (typeof content === 'string') {
                try {
                    const token = localStorage.getItem("access_token");
                    const headers = token ? {
                        "Authorization": `Bearer ${token}`,
                        "Content-Type": "application/json"
                    } : { "Content-Type": "application/json" };

                    const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/graph/generate`, {
                        method: "POST",
                        headers,
                        body: JSON.stringify({ content })
                    });

                    if (!response.ok) throw new Error("Graph generation failed");

                    const data = await response.json();

                    // Transform API nodes if necessary, or assume direct compatibility thanks to our service
                    // Our service returns { id, type, data, position } which matches ReactFlow
                    setNodes(data.nodes.map(n => ({
                        ...n,
                        // Ensure position is valid if missing (backend sends 0,0 but Dagre layout might be needed)
                        position: n.position || { x: Math.random() * 500, y: Math.random() * 500 }
                    })));
                    setEdges(data.edges);

                } catch (error) {
                    console.error("Upload failed", error);
                    alert("Failed to generate graph from file");
                } finally {
                    setUploading(false);
                }
            }
        };

        reader.readAsText(file);
    };

    const triggerUpload = () => {
        fileInputRef.current?.click();
    };

    // Function to fetch real graph data
    const fetchGraph = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem("token");
            // Try to verify if we have a real endpoint. 
            // Based on memory, there might be a POST /graph/generate.
            // For now, we simulate a delay to show the loading state.

            await new Promise(resolve => setTimeout(resolve, 1500));

            // In a real scenario, we would parse the API response to ReactFlow nodes/edges format
            // const response = await fetch('/api/graph/generate', ...);
            // setNodes(response.nodes);
            // setEdges(response.edges);

        } catch (e) {
            console.error("Failed to fetch graph", e);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Shell>
            <div className="flex items-center justify-between mb-6 animate-in fade-in slide-in-from-top-4 duration-500">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight text-foreground">Infrastructure Map</h2>
                    <p className="text-muted-foreground">Visualise dependency relationships across your AWS resources.</p>
                </div>
                <div className="flex items-center space-x-2">
                    <input
                        type="file"
                        ref={fileInputRef}
                        className="hidden"
                        accept=".tf,.tfstate,.json"
                        onChange={handleFileUpload}
                    />
                    <Button variant="outline" onClick={triggerUpload} disabled={uploading}>
                        <RefreshCw className={`mr-2 h-4 w-4 ${uploading ? 'animate-spin' : ''}`} />
                        {uploading ? 'Analyzing...' : 'Upload Terraform'}
                    </Button>
                    <Button variant="secondary">
                        <Download className="mr-2 h-4 w-4" />
                        Export
                    </Button>
                </div>
            </div>

            <Card className="h-[600px] w-full border-border glass-panel overflow-hidden relative">
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onConnect={onConnect}
                    // nodeTypes={nodeTypes} // Basic nodes for now to avoid custom node complexity issues without full setup
                    fitView
                    attributionPosition="bottom-right"
                    className="bg-background/50"
                >
                    <MiniMap style={{ background: 'transparent' }} nodeStrokeColor="#666" nodeColor="#e5e5e5" />
                    <Controls className="bg-background border-border" />
                    <Background color="#aaa" gap={16} />
                </ReactFlow>

                {loading && (
                    <div className="absolute inset-0 bg-background/50 backdrop-blur-sm flex items-center justify-center z-50">
                        <div className="flex flex-col items-center">
                            <RefreshCw className="h-10 w-10 animate-spin text-primary mb-2" />
                            <span className="text-sm font-medium text-muted-foreground">Scanning Infrastructure...</span>
                        </div>
                    </div>
                )}
            </Card>
        </Shell>
    );
}

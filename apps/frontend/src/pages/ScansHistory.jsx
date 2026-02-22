import React, { useEffect, useState } from "react";
import Shell from "@/components/layout/Shell";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
    FileSearch,
    CheckCircle2,
    XCircle,
    AlertTriangle,
    Clock,
    RefreshCw,
    Upload,
    ChevronDown,
    ChevronUp,
    FileCode
} from "lucide-react";
import { cn } from "@/lib/utils";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function ScansHistory() {
    const [scans, setScans] = useState([]);
    const [loading, setLoading] = useState(true);
    const [expandedScan, setExpandedScan] = useState(null);
    const [showNewScan, setShowNewScan] = useState(false);
    const [newScanContent, setNewScanContent] = useState("");
    const [newScanFilename, setNewScanFilename] = useState("main.tf");
    const [scanning, setScanning] = useState(false);

    const getAuthHeaders = () => {
        const token = localStorage.getItem("access_token");
        return {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        };
    };

    const fetchScans = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_URL}/scans?limit=20`, {
                headers: getAuthHeaders()
            });
            if (response.ok) {
                const data = await response.json();
                setScans(data);
            } else {
                // Mock data for demo
                setScans([
                    { id: 1, filename: "main.tf", timestamp: "2024-01-22 14:30:00", issues_count: 0, status: "PASSED" },
                    { id: 2, filename: "network.tf", timestamp: "2024-01-22 12:15:00", issues_count: 3, status: "FAILED" },
                    { id: 3, filename: "iam.tf", timestamp: "2024-01-21 16:45:00", issues_count: 1, status: "WARNING" }
                ]);
            }
        } catch (error) {
            console.error("Error fetching scans:", error);
        } finally {
            setLoading(false);
        }
    };

    const runNewScan = async () => {
        if (!newScanContent.trim()) return;

        setScanning(true);
        try {
            const response = await fetch(`${API_URL}/scans`, {
                method: "POST",
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    filename: newScanFilename,
                    content: newScanContent
                })
            });

            if (response.ok) {
                const result = await response.json();
                // Add to top of list
                setScans(prev => [result, ...prev]);
                setShowNewScan(false);
                setNewScanContent("");
                alert(`Scan complete! Found ${result.issues_count} issues.`);
            } else {
                throw new Error("Scan failed");
            }
        } catch (error) {
            console.error("Scan error:", error);
            alert("Failed to run scan. Check console.");
        } finally {
            setScanning(false);
        }
    };

    useEffect(() => {
        fetchScans();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const getStatusIcon = (status) => {
        switch (status) {
            case 'PASSED':
                return <CheckCircle2 className="h-5 w-5 text-green-500" />;
            case 'FAILED':
                return <XCircle className="h-5 w-5 text-red-500" />;
            case 'WARNING':
                return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
            default:
                return <FileSearch className="h-5 w-5 text-muted-foreground" />;
        }
    };

    const getStatusBadge = (status) => {
        const colors = {
            PASSED: "bg-green-500/20 text-green-500",
            FAILED: "bg-red-500/20 text-red-500",
            WARNING: "bg-yellow-500/20 text-yellow-500"
        };
        return colors[status] || "bg-muted text-muted-foreground";
    };

    // Stats
    const totalScans = scans.length;
    const passedScans = scans.filter(s => s.status === 'PASSED').length;
    const failedScans = scans.filter(s => s.status === 'FAILED').length;

    return (
        <Shell>
            <div className="flex items-center justify-between mb-8 animate-in fade-in slide-in-from-top-4 duration-500">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight text-foreground">Scans History</h2>
                    <p className="text-muted-foreground">View and manage your Terraform security scans.</p>
                </div>
                <div className="flex gap-2">
                    <Button onClick={fetchScans} variant="outline">
                        <RefreshCw className={cn("mr-2 h-4 w-4", loading && "animate-spin")} />
                        Refresh
                    </Button>
                    <Button onClick={() => setShowNewScan(!showNewScan)} className="bg-primary hover:bg-primary/90">
                        <Upload className="mr-2 h-4 w-4" />
                        New Scan
                    </Button>
                </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-3 gap-4 mb-8">
                <Card className="bg-card border-border">
                    <CardContent className="p-4 flex items-center justify-between">
                        <div>
                            <p className="text-2xl font-bold text-foreground">{totalScans}</p>
                            <p className="text-xs text-muted-foreground">Total Scans</p>
                        </div>
                        <FileSearch className="h-8 w-8 text-primary opacity-50" />
                    </CardContent>
                </Card>
                <Card className="bg-green-500/10 border-green-500/30">
                    <CardContent className="p-4 flex items-center justify-between">
                        <div>
                            <p className="text-2xl font-bold text-green-500">{passedScans}</p>
                            <p className="text-xs text-green-400">Passed</p>
                        </div>
                        <CheckCircle2 className="h-8 w-8 text-green-500 opacity-50" />
                    </CardContent>
                </Card>
                <Card className="bg-red-500/10 border-red-500/30">
                    <CardContent className="p-4 flex items-center justify-between">
                        <div>
                            <p className="text-2xl font-bold text-red-500">{failedScans}</p>
                            <p className="text-xs text-red-400">Failed</p>
                        </div>
                        <XCircle className="h-8 w-8 text-red-500 opacity-50" />
                    </CardContent>
                </Card>
            </div>

            {/* New Scan Form */}
            {showNewScan && (
                <Card className="mb-8 border-primary/30 animate-in fade-in slide-in-from-top-2 duration-300">
                    <CardHeader>
                        <CardTitle className="flex items-center">
                            <FileCode className="mr-2 h-5 w-5 text-primary" />
                            New Terraform Scan
                        </CardTitle>
                        <CardDescription>Paste your Terraform code below to scan for security issues.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <label className="text-sm font-medium mb-2 block">Filename</label>
                            <input
                                type="text"
                                value={newScanFilename}
                                onChange={(e) => setNewScanFilename(e.target.value)}
                                className="w-full px-3 py-2 rounded-md border border-input bg-background text-sm"
                                placeholder="main.tf"
                            />
                        </div>
                        <div>
                            <label className="text-sm font-medium mb-2 block">Terraform Content</label>
                            <textarea
                                className="flex min-h-[200px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-mono"
                                placeholder='resource "aws_s3_bucket" "example" { ... }'
                                value={newScanContent}
                                onChange={(e) => setNewScanContent(e.target.value)}
                            />
                        </div>
                        <div className="flex justify-end gap-2">
                            <Button variant="outline" onClick={() => setShowNewScan(false)}>Cancel</Button>
                            <Button onClick={runNewScan} disabled={scanning || !newScanContent.trim()}>
                                {scanning ? (
                                    <><RefreshCw className="mr-2 h-4 w-4 animate-spin" /> Scanning...</>
                                ) : (
                                    <><FileSearch className="mr-2 h-4 w-4" /> Run Scan</>
                                )}
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Scans List */}
            <Card>
                <CardHeader>
                    <CardTitle>Recent Scans</CardTitle>
                    <CardDescription>Your most recent security scans.</CardDescription>
                </CardHeader>
                <CardContent>
                    {loading ? (
                        <div className="flex justify-center py-8">
                            <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
                        </div>
                    ) : scans.length === 0 ? (
                        <div className="text-center py-12 text-muted-foreground">
                            <FileSearch className="h-12 w-12 mx-auto mb-4 opacity-50" />
                            <p>No scans found. Run your first scan above!</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {scans.map((scan) => (
                                <div
                                    key={scan.id}
                                    className={cn(
                                        "border rounded-lg overflow-hidden transition-all duration-200",
                                        expandedScan === scan.id ? "border-primary/50" : "border-border"
                                    )}
                                >
                                    <div
                                        className="flex items-center justify-between p-4 cursor-pointer hover:bg-muted/50"
                                        onClick={() => setExpandedScan(expandedScan === scan.id ? null : scan.id)}
                                    >
                                        <div className="flex items-center gap-4">
                                            {getStatusIcon(scan.status)}
                                            <div>
                                                <p className="font-medium font-mono">{scan.filename}</p>
                                                <p className="text-xs text-muted-foreground flex items-center gap-1">
                                                    <Clock className="h-3 w-3" />
                                                    {scan.timestamp}
                                                </p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-4">
                                            <span className={cn("text-xs font-bold px-2 py-1 rounded", getStatusBadge(scan.status))}>
                                                {scan.issues_count} {scan.issues_count === 1 ? 'issue' : 'issues'}
                                            </span>
                                            {expandedScan === scan.id ? (
                                                <ChevronUp className="h-4 w-4 text-muted-foreground" />
                                            ) : (
                                                <ChevronDown className="h-4 w-4 text-muted-foreground" />
                                            )}
                                        </div>
                                    </div>

                                    {expandedScan === scan.id && (
                                        <div className="border-t border-border p-4 bg-muted/30 animate-in slide-in-from-top-2 duration-200">
                                            {scan.issues && scan.issues.length > 0 ? (
                                                <div className="space-y-2">
                                                    {scan.issues.map((issue, idx) => (
                                                        <div key={idx} className="flex items-start gap-3 p-2 bg-background rounded border border-border">
                                                            <AlertTriangle className={cn(
                                                                "h-4 w-4 mt-0.5",
                                                                issue.severity === 'HIGH' ? "text-red-500" :
                                                                    issue.severity === 'MEDIUM' ? "text-yellow-500" : "text-blue-500"
                                                            )} />
                                                            <div>
                                                                <p className="text-sm font-medium">Line {issue.line}: {issue.message}</p>
                                                                <p className="text-xs text-muted-foreground">{issue.rule}</p>
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            ) : (
                                                <p className="text-sm text-muted-foreground text-center py-4">
                                                    {scan.status === 'PASSED' ? "✅ No issues found in this scan." : "Issue details not available."}
                                                </p>
                                            )}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>
        </Shell>
    );
}

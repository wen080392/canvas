import React, { useState } from 'react';
import Shell from "@/components/layout/Shell";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertCircle, CheckCircle, RefreshCw, Server, AlertTriangle, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

export default function DriftDetection() {
    const [loading, setLoading] = useState(false);
    const [alerts, setAlerts] = useState([]);
    const [scanned, setScanned] = useState(false);

    const handleFix = async (alertItem) => {
        if (!confirm(`Are you sure you want to apply the fix for ${alertItem.resource_id}? This will create a Pull Request.`)) return;

        // Map alert to issue_type (simple mapping for MVP)
        let issueType = "aws_s3_bucket_public";
        if (alertItem.resource_type === "aws_security_group") issueType = "aws_security_group_open_ssh";

        try {
            const token = localStorage.getItem("access_token");
            const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/remediation/apply`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    issue_type: issueType,
                    resource_id: alertItem.resource_id
                })
            });

            if (!response.ok) throw new Error("Remediation failed");

            const data = await response.json();
            alert(`Success: ${data.message}\nReference: ${data.pr_url}`);

            // Mark as fixed locally
            setAlerts(prev => prev.filter(a => a.id !== alertItem.id));

        } catch (error) {
            console.error("Fix error:", error);
            alert("Failed to apply fix. see console.");
        }
    };

    const runDriftScan = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem("access_token");
            const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/drift/scan`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });

            if (!response.ok) throw new Error("Scan failed");

            const data = await response.json();
            setAlerts(data);
            setScanned(true);
        } catch (error) {
            console.error("Drift scan error:", error);
            // Mock data for demo if fetch fails
            setAlerts([
                {
                    id: 1,
                    resource_id: "aws_s3_bucket.prod_data",
                    resource_type: "aws_s3_bucket",
                    severity: "HIGH",
                    drift_details: {
                        field: "acl",
                        expected: "private",
                        actual: "public-read",
                        message: "Bucket ACL changed from private to public-read"
                    }
                },
                {
                    id: 2,
                    resource_id: "aws_security_group.web_sg",
                    resource_type: "aws_security_group",
                    severity: "CRITICAL",
                    drift_details: {
                        message: "Found 1 extra rule allowing SSH (0.0.0.0/0)"
                    }
                }
            ]);
            setScanned(true);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Shell>
            <div className="flex items-center justify-between mb-8 animate-in fade-in slide-in-from-top-4 duration-500">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight text-foreground">Drift Detection</h2>
                    <p className="text-muted-foreground">Compare your Terraform state against actual cloud infrastructure.</p>
                </div>
                <Button onClick={runDriftScan} disabled={loading} size="lg" className="bg-primary hover:bg-primary/90">
                    <RefreshCw className={cn("mr-2 h-4 w-4", loading && "animate-spin")} />
                    {loading ? "Scanning..." : "Run Drift Check"}
                </Button>
            </div>

            {!scanned && !loading && (
                <div className="flex flex-col items-center justify-center h-[400px] border-2 border-dashed border-border rounded-xl bg-card/50">
                    <Server className="h-16 w-16 text-muted-foreground mb-4 opacity-50" />
                    <h3 className="text-xl font-medium text-foreground">Ready to Scan</h3>
                    <p className="text-muted-foreground mt-2 max-w-md text-center">
                        Click the button above to verify if your infrastructure matches your IaC code.
                    </p>
                </div>
            )}

            {scanned && alerts.length === 0 && (
                <Card className="border-green-500/20 bg-green-500/10">
                    <CardContent className="flex items-center p-6">
                        <CheckCircle className="h-8 w-8 text-green-500 mr-4" />
                        <div>
                            <h3 className="text-lg font-bold text-green-500">No Drift Detected</h3>
                            <p className="text-sm text-green-600/80">Your infrastructure is perfectly synced with your Terraform state.</p>
                        </div>
                    </CardContent>
                </Card>
            )}

            <div className="space-y-4">
                {alerts.map((alert) => (
                    <Card key={alert.id} className="border-l-4 border-l-red-500 overflow-hidden group hover:border-border transition-colors">
                        <CardHeader className="flex flex-row items-start justify-between pb-2 bg-muted/30">
                            <div>
                                <CardTitle className="text-lg font-mono flex items-center">
                                    <AlertTriangle className="h-4 w-4 text-red-500 mr-2" />
                                    {alert.resource_id}
                                </CardTitle>
                                <CardDescription className="font-mono text-xs mt-1">
                                    {alert.resource_type}
                                </CardDescription>
                            </div>
                            <span className={cn(
                                "text-xs font-bold px-2 py-1 rounded",
                                alert.severity === "CRITICAL" ? "bg-red-500/20 text-red-500" : "bg-orange-500/20 text-orange-500"
                            )}>
                                {alert.severity} DRIFT
                            </span>
                        </CardHeader>
                        <CardContent className="pt-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <div className="text-sm text-muted-foreground font-semibold uppercase tracking-wider">Configuration Drift</div>
                                    <p className="text-sm text-foreground">{alert.drift_details.message}</p>
                                </div>

                                {alert.drift_details.expected && (
                                    <div className="bg-black/40 p-3 rounded-md font-mono text-xs border border-white/5">
                                        <div className="flex items-center text-green-400 mb-1">
                                            <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                                            Expected: {alert.drift_details.expected}
                                        </div>
                                        <div className="flex items-center text-red-400">
                                            <span className="w-2 h-2 bg-red-400 rounded-full mr-2"></span>
                                            Actual: &nbsp;&nbsp; {alert.drift_details.actual}
                                        </div>
                                    </div>
                                )}
                            </div>

                            <div className="mt-4 flex justify-end gap-2">
                                <Button
                                    onClick={() => handleFix(alert)}
                                    size="sm"
                                    className="bg-green-600 hover:bg-green-700 text-white text-xs"
                                >
                                    <Hammer className="mr-2 h-3 w-3" /> Fix It
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </Shell>
    );
}

function Hammer({ className }) {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
            <path d="m15 12-8.5 8.5c-.83.83-2.17.83-3 0 0 0 0 0 0 0a2.12 2.12 0 0 1 0-3L12 9" />
            <path d="M17.64 15 22 10.64" />
            <path d="m20.91 11.7-1.25-1.25c-.6-.6-.93-1.4-.93-2.25V7.86c0-.55-.45-1-1-1H16.4c-.84 0-1.65-.33-2.25-.93L12.9 4.68" />
            <path d="M16 16l-4-4" />
        </svg>
    )
}

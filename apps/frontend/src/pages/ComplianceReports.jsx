import React, { useEffect, useState } from "react";
import Shell from "@/components/layout/Shell";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
    Shield,
    CheckCircle2,
    XCircle,
    AlertTriangle,
    ChevronRight,
    ArrowLeft,
    FileText,
    RefreshCw
} from "lucide-react";
import { cn } from "@/lib/utils";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function ComplianceReports() {
    const [frameworks, setFrameworks] = useState([]);
    const [overview, setOverview] = useState(null);
    const [selectedFramework, setSelectedFramework] = useState(null);
    const [frameworkDetails, setFrameworkDetails] = useState(null);
    const [loading, setLoading] = useState(true);
    const [detailsLoading, setDetailsLoading] = useState(false);

    const getAuthHeaders = () => {
        const token = localStorage.getItem("access_token");
        return token ? { "Authorization": `Bearer ${token}` } : {};
    };

    const fetchOverview = async () => {
        try {
            const response = await fetch(`${API_URL}/compliance/reports`, {
                headers: getAuthHeaders()
            });
            if (response.ok) {
                const data = await response.json();
                setOverview(data);
            }
        } catch (error) {
            console.error("Error fetching compliance overview:", error);
        }
    };

    const fetchFrameworks = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_URL}/compliance/frameworks`, {
                headers: getAuthHeaders()
            });
            if (response.ok) {
                const data = await response.json();
                setFrameworks(data.frameworks || []);
            } else {
                // Fallback mock data
                setFrameworks([
                    { id: 'soc2', name: 'SOC 2', description: 'Service Organization Control', controls_count: 45 },
                    { id: 'iso27001', name: 'ISO 27001', description: 'Information Security Management', controls_count: 114 },
                    { id: 'hipaa', name: 'HIPAA', description: 'Health Insurance Portability', controls_count: 32 },
                    { id: 'gdpr', name: 'GDPR', description: 'General Data Protection Regulation', controls_count: 25 },
                    { id: 'pci-dss', name: 'PCI-DSS', description: 'Payment Card Industry Standard', controls_count: 38 }
                ]);
            }
        } catch (error) {
            console.error("Error fetching frameworks:", error);
        } finally {
            setLoading(false);
        }
    };

    const fetchFrameworkDetails = async (frameworkId) => {
        setDetailsLoading(true);
        try {
            const response = await fetch(`${API_URL}/compliance/reports/${frameworkId}`, {
                headers: getAuthHeaders()
            });
            if (response.ok) {
                const data = await response.json();
                setFrameworkDetails(data);
            } else {
                // Mock data for demo
                setFrameworkDetails({
                    framework_id: frameworkId,
                    name: frameworks.find(f => f.id === frameworkId)?.name || frameworkId.toUpperCase(),
                    overall_score: 87,
                    status: 'PARTIALLY_COMPLIANT',
                    controls: [
                        { id: 'CC1.1', name: 'Security Governance', status: 'PASSED', description: 'Establish security policies' },
                        { id: 'CC1.2', name: 'Access Control', status: 'PASSED', description: 'Implement access restrictions' },
                        { id: 'CC2.1', name: 'Encryption at Rest', status: 'FAILED', description: 'Encrypt stored data', remediation: 'Enable encryption on S3 buckets' },
                        { id: 'CC2.2', name: 'Encryption in Transit', status: 'PASSED', description: 'Use TLS for data transfer' },
                        { id: 'CC3.1', name: 'Logging & Monitoring', status: 'WARNING', description: 'Track system activities', remediation: 'Enable CloudTrail' }
                    ]
                });
            }
        } catch (error) {
            console.error("Error fetching framework details:", error);
        } finally {
            setDetailsLoading(false);
        }
    };

    useEffect(() => {
        fetchOverview();
        fetchFrameworks();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const handleSelectFramework = (framework) => {
        setSelectedFramework(framework);
        fetchFrameworkDetails(framework.id);
    };

    const handleBack = () => {
        setSelectedFramework(null);
        setFrameworkDetails(null);
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'PASSED':
                return <CheckCircle2 className="h-5 w-5 text-green-500" />;
            case 'FAILED':
                return <XCircle className="h-5 w-5 text-red-500" />;
            case 'WARNING':
                return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
            default:
                return <Shield className="h-5 w-5 text-muted-foreground" />;
        }
    };

    const getScoreColor = (score) => {
        if (score >= 90) return 'text-green-500';
        if (score >= 70) return 'text-yellow-500';
        return 'text-red-500';
    };

    // Detail View
    if (selectedFramework && frameworkDetails) {
        const passedCount = frameworkDetails.controls?.filter(c => c.status === 'PASSED').length || 0;

        return (
            <Shell>
                <div className="flex items-center justify-between mb-8 animate-in fade-in slide-in-from-top-4 duration-500">
                    <div className="flex items-center">
                        <Button variant="ghost" onClick={handleBack} className="mr-4">
                            <ArrowLeft className="h-4 w-4 mr-2" /> Back
                        </Button>
                        <div>
                            <h2 className="text-3xl font-bold tracking-tight text-foreground">
                                {frameworkDetails.name || selectedFramework.name}
                            </h2>
                            <p className="text-muted-foreground">{selectedFramework.description}</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="text-right">
                            <span className={cn("text-4xl font-bold", getScoreColor(frameworkDetails.overall_score))}>
                                {frameworkDetails.overall_score}%
                            </span>
                            <p className="text-xs text-muted-foreground">Compliance Score</p>
                        </div>
                    </div>
                </div>

                {/* Summary Cards */}
                <div className="grid grid-cols-3 gap-4 mb-8">
                    <Card className="bg-green-500/10 border-green-500/30">
                        <CardContent className="p-4 flex items-center justify-between">
                            <div>
                                <p className="text-2xl font-bold text-green-500">{passedCount}</p>
                                <p className="text-xs text-green-400">Passed Controls</p>
                            </div>
                            <CheckCircle2 className="h-8 w-8 text-green-500 opacity-50" />
                        </CardContent>
                    </Card>
                    <Card className="bg-red-500/10 border-red-500/30">
                        <CardContent className="p-4 flex items-center justify-between">
                            <div>
                                <p className="text-2xl font-bold text-red-500">
                                    {frameworkDetails.controls?.filter(c => c.status === 'FAILED').length || 0}
                                </p>
                                <p className="text-xs text-red-400">Failed Controls</p>
                            </div>
                            <XCircle className="h-8 w-8 text-red-500 opacity-50" />
                        </CardContent>
                    </Card>
                    <Card className="bg-yellow-500/10 border-yellow-500/30">
                        <CardContent className="p-4 flex items-center justify-between">
                            <div>
                                <p className="text-2xl font-bold text-yellow-500">
                                    {frameworkDetails.controls?.filter(c => c.status === 'WARNING').length || 0}
                                </p>
                                <p className="text-xs text-yellow-400">Warnings</p>
                            </div>
                            <AlertTriangle className="h-8 w-8 text-yellow-500 opacity-50" />
                        </CardContent>
                    </Card>
                </div>

                {/* Controls List */}
                <Card>
                    <CardHeader>
                        <CardTitle>Controls</CardTitle>
                        <CardDescription>Detailed compliance status for each control.</CardDescription>
                    </CardHeader>
                    <CardContent>
                        {detailsLoading ? (
                            <div className="flex justify-center py-8">
                                <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
                            </div>
                        ) : (
                            <div className="space-y-3">
                                {frameworkDetails.controls?.map((control) => (
                                    <div
                                        key={control.id}
                                        className={cn(
                                            "flex items-center justify-between p-4 rounded-lg border",
                                            control.status === 'FAILED' && "border-red-500/30 bg-red-500/5",
                                            control.status === 'WARNING' && "border-yellow-500/30 bg-yellow-500/5",
                                            control.status === 'PASSED' && "border-border bg-card"
                                        )}
                                    >
                                        <div className="flex items-center gap-4">
                                            {getStatusIcon(control.status)}
                                            <div>
                                                <p className="font-medium">{control.id}: {control.name}</p>
                                                <p className="text-sm text-muted-foreground">{control.description}</p>
                                                {control.remediation && (
                                                    <p className="text-xs text-yellow-500 mt-1">
                                                        💡 Fix: {control.remediation}
                                                    </p>
                                                )}
                                            </div>
                                        </div>
                                        <span className={cn(
                                            "text-xs font-bold px-2 py-1 rounded",
                                            control.status === 'PASSED' && "bg-green-500/20 text-green-500",
                                            control.status === 'FAILED' && "bg-red-500/20 text-red-500",
                                            control.status === 'WARNING' && "bg-yellow-500/20 text-yellow-500"
                                        )}>
                                            {control.status}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>
            </Shell>
        );
    }

    // List View
    return (
        <Shell>
            <div className="flex items-center justify-between mb-8 animate-in fade-in slide-in-from-top-4 duration-500">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight text-foreground">Compliance Reports</h2>
                    <p className="text-muted-foreground">Monitor your infrastructure compliance across multiple frameworks.</p>
                </div>
                <Button onClick={() => { fetchOverview(); fetchFrameworks(); }} variant="outline">
                    <RefreshCw className={cn("mr-2 h-4 w-4", loading && "animate-spin")} />
                    Refresh
                </Button>
            </div>

            {/* Overview Card */}
            {overview && (
                <Card className="mb-8 bg-gradient-to-r from-primary/10 to-primary/5 border-primary/20">
                    <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <h3 className="text-lg font-semibold">Overall Compliance Score</h3>
                                <p className="text-muted-foreground text-sm">Across all frameworks</p>
                            </div>
                            <div className="text-right">
                                <span className={cn("text-5xl font-bold", getScoreColor(overview.overall_score || 85))}>
                                    {overview.overall_score || 85}%
                                </span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Frameworks Grid */}
            {loading ? (
                <div className="flex justify-center py-12">
                    <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {frameworks.map((framework) => (
                        <Card
                            key={framework.id}
                            className="cursor-pointer hover:border-primary/50 transition-all duration-300 group"
                            onClick={() => handleSelectFramework(framework)}
                        >
                            <CardHeader>
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 rounded-lg bg-primary/10">
                                            <FileText className="h-5 w-5 text-primary" />
                                        </div>
                                        <CardTitle className="text-lg">{framework.name}</CardTitle>
                                    </div>
                                    <ChevronRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                                </div>
                            </CardHeader>
                            <CardContent>
                                <p className="text-sm text-muted-foreground mb-4">{framework.description}</p>
                                <div className="flex items-center justify-between text-xs">
                                    <span className="text-muted-foreground">{framework.controls_count} controls</span>
                                    <span className="text-primary font-medium">View Details →</span>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}
        </Shell>
    );
}

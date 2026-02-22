import React, { useState } from 'react';
import Shell from "@/components/layout/Shell";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertCircle, FileCode, ShieldAlert, CheckCircle, Search } from "lucide-react";
import { cn } from "@/lib/utils";

export default function SecretScanner() {
    const [loading, setLoading] = useState(false);
    const [content, setContent] = useState("");
    const [results, setResults] = useState(null);

    const handleScan = async () => {
        if (!content.trim()) return;

        setLoading(true);
        setResults(null);

        try {
            const token = localStorage.getItem("access_token");
            const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/secrets/scan`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({
                    content: content,
                    filename: "manual_input.tf"
                })
            });

            if (!response.ok) throw new Error("Scan failed");

            const data = await response.json();
            setResults(data);
        } catch (error) {
            console.error("Scan error:", error);
            // Fallback for demo if backend not ready or connection fails
            // But since we confirmed backend is ready, this should just be error handling
            alert("Failed to scan secrets. Check console.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Shell>
            <div className="flex items-center justify-between mb-8 animate-in fade-in slide-in-from-top-4 duration-500">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight text-foreground">Secret Scanner</h2>
                    <p className="text-muted-foreground">Detect hardcoded credentials and secrets in your code.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Input Section */}
                <Card className="h-full flex flex-col">
                    <CardHeader>
                        <CardTitle className="text-lg flex items-center">
                            <FileCode className="mr-2 h-5 w-5 text-primary" />
                            Source Code
                        </CardTitle>
                        <CardDescription>Paste your Terraform or config code here to scan.</CardDescription>
                    </CardHeader>
                    <CardContent className="flex-1 flex flex-col gap-4">
                        <textarea
                            className="flex min-h-[400px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 font-mono"
                            placeholder='resource "aws_instance" "app" { ... }'
                            value={content}
                            onChange={(e) => setContent(e.target.value)}
                        />
                        <Button onClick={handleScan} disabled={loading || !content.trim()} className="w-full">
                            {loading ? (
                                <>
                                    <Search className="mr-2 h-4 w-4 animate-spin" /> Scanning...
                                </>
                            ) : (
                                <>
                                    <Search className="mr-2 h-4 w-4" /> Scan for Secrets
                                </>
                            )}
                        </Button>
                    </CardContent>
                </Card>

                {/* Results Section */}
                <div className="space-y-4">
                    {!results && !loading && (
                        <div className="h-full flex flex-col items-center justify-center p-8 border-2 border-dashed border-border rounded-xl bg-card/50 text-muted-foreground">
                            <ShieldAlert className="h-16 w-16 mb-4 opacity-20" />
                            <p>Waiting for code input...</p>
                        </div>
                    )}

                    {results && results.total_findings === 0 && (
                        <Card className="border-green-500/20 bg-green-500/10 h-full flex items-center justify-center">
                            <CardContent className="flex flex-col items-center p-6 text-center">
                                <CheckCircle className="h-12 w-12 text-green-500 mb-4" />
                                <h3 className="text-xl font-bold text-green-500">No Secrets Found</h3>
                                <p className="text-green-600/80 mt-2">Your code appears to be safe from hardcoded credentials.</p>
                            </CardContent>
                        </Card>
                    )}

                    {results && results.total_findings > 0 && (
                        <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <div className="flex gap-4 mb-4">
                                <Card className="flex-1 bg-red-500/10 border-red-500/30">
                                    <CardContent className="p-4 flex flex-col items-center">
                                        <span className="text-2xl font-bold text-red-500">{results.by_severity.CRITICAL || 0}</span>
                                        <span className="text-xs uppercase font-semibold text-red-400">Critical</span>
                                    </CardContent>
                                </Card>
                                <Card className="flex-1 bg-orange-500/10 border-orange-500/30">
                                    <CardContent className="p-4 flex flex-col items-center">
                                        <span className="text-2xl font-bold text-orange-500">{results.by_severity.HIGH || 0}</span>
                                        <span className="text-xs uppercase font-semibold text-orange-400">High</span>
                                    </CardContent>
                                </Card>
                            </div>

                            {results.findings.map((finding, index) => (
                                <Card key={index} className="border-l-4 border-l-red-500 overflow-hidden">
                                    <CardHeader className="py-3 bg-muted/30">
                                        <div className="flex items-center justify-between">
                                            <CardTitle className="text-sm font-medium flex items-center">
                                                <AlertCircle className="h-4 w-4 text-red-500 mr-2" />
                                                Line {finding.line}: {finding.type}
                                            </CardTitle>
                                            <span className="text-xs font-bold text-red-500 px-2 py-0.5 bg-red-500/10 rounded">
                                                {finding.severity}
                                            </span>
                                        </div>
                                    </CardHeader>
                                    <CardContent className="py-3">
                                        <p className="text-xs text-muted-foreground mb-2">{finding.description}</p>
                                        <div className="bg-black/80 rounded p-2 overflow-x-auto">
                                            <code className="text-xs font-mono text-red-300 block whitespace-pre">
                                                {finding.snippet}
                                            </code>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </Shell>
    );
}

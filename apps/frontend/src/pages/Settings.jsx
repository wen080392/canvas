import React, { useState, useEffect } from 'react';

export default function Settings() {
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        aws_region: 'us-east-1',
        aws_access_key: '',
        aws_secret_key: '',
        github_token: '',
        email_notifications: false
    });
    const [status, setStatus] = useState({
        has_aws_secret: false,
        has_github_token: false
    });

    useEffect(() => {
        loadSettings();
    }, []);

    const loadSettings = async () => {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`${window.API_BASE || 'http://localhost:8000'}/settings`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                setFormData(prev => ({
                    ...prev,
                    aws_region: data.aws_region || 'us-east-1',
                    aws_access_key: data.aws_access_key_masked || '',
                    email_notifications: data.email_notifications || false,
                    aws_secret_key: '', // Always empty on load
                    github_token: ''    // Always empty on load
                }));
                setStatus({
                    has_aws_secret: data.has_aws_secret,
                    has_github_token: data.has_github_token
                });
            }
        } catch (error) {
            console.error('Failed to load settings', error);
        }
    };

    const handleChange = (e) => {
        const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
        setFormData({ ...formData, [e.target.id]: value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        const token = localStorage.getItem('access_token');

        const payload = {
            aws_region: formData.aws_region,
            dark_mode: true,
            email_notifications: formData.email_notifications
        };

        // Only send keys if they are not masked/empty
        if (formData.aws_access_key && !formData.aws_access_key.includes('****')) {
            payload.aws_access_key = formData.aws_access_key;
        }
        if (formData.aws_secret_key) payload.aws_secret_key = formData.aws_secret_key;
        if (formData.github_token) payload.github_token = formData.github_token;

        try {
            const response = await fetch(`${window.API_BASE || 'http://localhost:8000'}/settings`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                const data = await response.json();
                alert('Configurações salvas!');
                setFormData(prev => ({
                    ...prev,
                    aws_access_key: data.aws_access_key_masked || prev.aws_access_key,
                    aws_secret_key: '',
                    github_token: ''
                }));
                setStatus({
                    has_aws_secret: data.has_aws_secret,
                    has_github_token: data.has_github_token
                });
            } else {
                throw new Error('Falha ao salvar');
            }
        } catch (error) {
            alert('Erro ao salvar: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8 text-slate-900">
            <header className="flex items-center justify-between border-b pb-6">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight">Platform Settings</h2>
                    <p className="text-slate-500 text-sm mt-1">System Configuration & Integrations</p>
                </div>
            </header>

            <form onSubmit={handleSubmit} className="space-y-8">

                {/* Organization Mock */}
                <div className="bg-white border rounded-xl overflow-hidden shadow-sm">
                    <div className="bg-slate-50 p-5 border-b flex items-center justify-between">
                        <div className="flex items-center">
                            <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center text-emerald-600 mr-4">
                                <i className="fas fa-building text-xl"></i>
                            </div>
                            <div>
                                <h3 className="text-lg font-bold">Organization & Billing</h3>
                                <p className="text-xs text-slate-500 uppercase font-bold">My Organization</p>
                            </div>
                        </div>
                        <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">FREE TIER</span>
                    </div>
                    <div className="p-6">
                        <p className="text-sm text-slate-600">Usage stats and billing details generally shown here.</p>
                    </div>
                </div>

                {/* AWS Section */}
                <div className="bg-white border rounded-xl overflow-hidden shadow-sm">
                    <div className="bg-slate-50 p-5 border-b flex items-center">
                        <div className="w-10 h-10 rounded-lg bg-amber-100 flex items-center justify-center text-amber-600 mr-4">
                            <i className="fab fa-aws text-2xl"></i>
                        </div>
                        <div>
                            <h3 className="text-lg font-bold">AWS Integration</h3>
                            <p className="text-xs text-slate-500 uppercase font-bold">Cloud Credentials</p>
                        </div>
                    </div>
                    <div className="p-6 space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Access Key ID</label>
                                <input
                                    type="text"
                                    id="aws_access_key"
                                    value={formData.aws_access_key}
                                    onChange={handleChange}
                                    className="w-full bg-slate-50 border rounded-lg py-2 px-3 text-sm focus:ring-2 focus:ring-amber-500 outline-none"
                                    placeholder="Masked value shown"
                                />
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Region</label>
                                <select
                                    id="aws_region"
                                    value={formData.aws_region}
                                    onChange={handleChange}
                                    className="w-full bg-slate-50 border rounded-lg py-2 px-3 text-sm focus:ring-2 focus:ring-amber-500 outline-none"
                                >
                                    <option value="us-east-1">us-east-1 (N. Virginia)</option>
                                    <option value="us-west-2">us-west-2 (Oregon)</option>
                                    <option value="eu-west-1">eu-west-1 (Ireland)</option>
                                    <option value="sa-east-1">sa-east-1 (São Paulo)</option>
                                </select>
                            </div>
                        </div>
                        <div>
                            <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Secret Access Key</label>
                            <input
                                type="password"
                                id="aws_secret_key"
                                value={formData.aws_secret_key}
                                onChange={handleChange}
                                className="w-full bg-slate-50 border rounded-lg py-2 px-3 text-sm focus:ring-2 focus:ring-amber-500 outline-none"
                                placeholder="Enter new secret key to update"
                            />
                            <p className="mt-2 text-xs flex items-center text-slate-500">
                                {status.has_aws_secret ?
                                    <span className="text-emerald-600 flex items-center"><i className="fas fa-check-circle mr-1"></i> Configured</span> :
                                    <span className="text-slate-400">Not configured</span>
                                }
                            </p>
                        </div>
                    </div>
                </div>

                {/* GitHub Section */}
                <div className="bg-white border rounded-xl overflow-hidden shadow-sm">
                    <div className="bg-slate-50 p-5 border-b flex items-center">
                        <div className="w-10 h-10 rounded-lg bg-slate-200 flex items-center justify-center text-slate-700 mr-4">
                            <i className="fab fa-github text-2xl"></i>
                        </div>
                        <div>
                            <h3 className="text-lg font-bold">GitHub Integration</h3>
                            <p className="text-xs text-slate-500 uppercase font-bold">Source Code Scanning</p>
                        </div>
                    </div>
                    <div className="p-6">
                        <div>
                            <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Personal Access Token</label>
                            <input
                                type="password"
                                id="github_token"
                                value={formData.github_token}
                                onChange={handleChange}
                                className="w-full bg-slate-50 border rounded-lg py-2 px-3 text-sm focus:ring-2 focus:ring-slate-500 outline-none"
                                placeholder="ghp_..."
                            />
                            <p className="mt-2 text-xs flex items-center text-slate-500">
                                {status.has_github_token ?
                                    <span className="text-emerald-600 flex items-center"><i className="fas fa-check-circle mr-1"></i> Configured</span> :
                                    <span className="text-slate-400">Not configured</span>
                                }
                            </p>
                        </div>
                    </div>
                </div>

                {/* Preferences */}
                <div className="bg-white border rounded-xl overflow-hidden shadow-sm">
                    <div className="bg-slate-50 p-5 border-b flex items-center">
                        <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center text-purple-600 mr-4">
                            <i className="fas fa-sliders-h text-xl"></i>
                        </div>
                        <div>
                            <h3 className="text-lg font-bold">Preferences</h3>
                            <p className="text-xs text-slate-500 uppercase font-bold">User Experience</p>
                        </div>
                    </div>
                    <div className="p-6 divide-y">
                        <div className="flex items-center justify-between py-4">
                            <div className="flex items-center">
                                <div className="mr-4 text-slate-400"><i className="fas fa-envelope text-xl"></i></div>
                                <div>
                                    <h4 className="text-sm font-bold">Email Notifications</h4>
                                    <p className="text-xs text-slate-500">Alerts for critical findings</p>
                                </div>
                            </div>
                            <input
                                type="checkbox"
                                id="email_notifications"
                                checked={formData.email_notifications}
                                onChange={handleChange}
                                className="w-5 h-5 rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                            />
                        </div>
                    </div>
                </div>

                <div className="flex justify-end pt-4 pb-12">
                    <button
                        type="submit"
                        disabled={loading}
                        className="px-8 py-3 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl shadow-lg transform transition hover:-translate-y-0.5 disabled:opacity-50"
                    >
                        {loading ? 'Saving...' : 'Save Changes'}
                    </button>
                </div>

            </form>
        </div>
    );
}

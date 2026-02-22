import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Login() {
    const navigate = useNavigate();
    const [isLogin, setIsLogin] = useState(true);
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        email: 'admin@company.com',
        password: 'password',
        regName: '',
        regEmail: '',
        regPassword: ''
    });

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.id]: e.target.value });
    };

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const params = new URLSearchParams();
            params.append('username', formData.email);
            params.append('password', formData.password);

            const response = await fetch(`${window.API_BASE || 'http://127.0.0.1:8000'}/token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: params
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                console.error('Login Error:', response.status, response.statusText, errData);
                throw new Error(errData.detail || 'Credenciais Inválidas');
            }

            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);

            // Simulate toast success
            console.log('Login success');
            navigate('/');
        } catch (error) {
            console.error("Login Fetch Error:", error);
            alert('Falha no Login: ' + error.message + (error.message.includes('Failed to fetch') ? ' (Err Connection Refused/Network)' : ''));
        } finally {
            setLoading(false);
        }
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const response = await fetch(`${window.API_BASE || 'http://127.0.0.1:8000'}/users`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: formData.regEmail,
                    password: formData.regPassword,
                    full_name: formData.regName
                })
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || 'Erro ao criar conta');

            alert('Conta Criada! Faça login agora.');
            setIsLogin(true);
            setFormData(prev => ({ ...prev, email: prev.regEmail }));
        } catch (error) {
            alert('Erro no Registro: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-black text-white h-screen flex items-center justify-center overflow-hidden relative selection:bg-neon-pink selection:text-white font-sans">
            {/* Background Orbs */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute w-[600px] h-[600px] bg-purple-500/20 top-[-20%] left-[-10%] rounded-full blur-[100px] animate-pulse"></div>
                <div className="absolute w-[500px] h-[500px] bg-blue-500/20 bottom-[-10%] right-[-10%] rounded-full blur-[100px] animate-pulse"></div>
            </div>

            <div className="w-full max-w-md p-10 rounded-3xl relative z-10 bg-black/60 backdrop-blur-xl border border-white/10 shadow-2xl">
                <div className="text-center mb-10">
                    <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-gray-900 to-black flex items-center justify-center mx-auto mb-6 border border-white/10 shadow-[0_0_30px_rgba(0,243,255,0.15)]">
                        <i className="fas fa-shield-alt text-4xl text-cyan-400"></i>
                    </div>
                    <h1 className="text-4xl font-bold text-white tracking-tight mb-2">
                        {isLogin ? 'CloudGuardian' : 'Registro'}
                    </h1>
                    <p className="text-gray-400 text-sm tracking-widest uppercase">
                        {isLogin ? 'Secure your infrastructure intelligence' : 'Junte-se à plataforma'}
                    </p>
                </div>

                {isLogin ? (
                    <form onSubmit={handleLogin} className="space-y-6">
                        <div>
                            <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2 ml-1">Identity</label>
                            <input
                                type="email"
                                id="email"
                                value={formData.email}
                                onChange={handleChange}
                                className="w-full bg-black/40 border border-white/10 text-white rounded-xl py-4 px-4 focus:outline-none focus:border-cyan-400 transition-colors placeholder-gray-700"
                                placeholder="email@company.com"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2 ml-1">Passcode</label>
                            <input
                                type="password"
                                id="password"
                                value={formData.password}
                                onChange={handleChange}
                                className="w-full bg-black/40 border border-white/10 text-white rounded-xl py-4 px-4 focus:outline-none focus:border-purple-400 transition-colors placeholder-gray-700 font-mono"
                                placeholder="••••••••"
                                required
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-4 mt-4 bg-gradient-to-r from-cyan-400 to-purple-500 text-black font-extrabold text-lg rounded-xl uppercase tracking-widest hover:brightness-110 transition-all disabled:opacity-50"
                        >
                            {loading ? 'Verifying...' : 'Authenticate'}
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleRegister} className="space-y-6">
                        <div>
                            <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2 ml-1">Name</label>
                            <input
                                type="text"
                                id="regName"
                                value={formData.regName}
                                onChange={handleChange}
                                className="w-full bg-black/40 border border-white/10 text-white rounded-xl py-4 px-4 focus:outline-none focus:border-pink-500 transition-colors"
                                placeholder="Your Name"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2 ml-1">Email</label>
                            <input
                                type="email"
                                id="regEmail"
                                value={formData.regEmail}
                                onChange={handleChange}
                                className="w-full bg-black/40 border border-white/10 text-white rounded-xl py-4 px-4 focus:outline-none focus:border-cyan-400 transition-colors"
                                placeholder="new@example.com"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2 ml-1">Password</label>
                            <input
                                type="password"
                                id="regPassword"
                                value={formData.regPassword}
                                onChange={handleChange}
                                className="w-full bg-black/40 border border-white/10 text-white rounded-xl py-4 px-4 focus:outline-none focus:border-purple-500 transition-colors"
                                placeholder="••••••••"
                                required
                                minLength={8}
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-4 mt-4 bg-gradient-to-r from-cyan-400 to-purple-500 text-black font-extrabold text-lg rounded-xl uppercase tracking-widest hover:brightness-110 transition-all disabled:opacity-50"
                        >
                            {loading ? 'Creating...' : 'Create Account'}
                        </button>
                    </form>
                )}

                <div className="mt-8 text-center text-xs text-gray-600 uppercase tracking-widest">
                    <button
                        onClick={() => setIsLogin(!isLogin)}
                        className="text-cyan-400 hover:text-white transition-colors font-bold underline"
                    >
                        {isLogin ? 'Criar Nova Conta' : 'Voltar para Login'}
                    </button>
                    <span className="mx-2">|</span>
                    System Version v2.1.0
                </div>
            </div>
        </div>
    );
}

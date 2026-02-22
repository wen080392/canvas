import React from 'react';

export default function Placeholder({ title }) {
    return (
        <div className="flex flex-col items-center justify-center h-full p-12 text-center text-slate-500">
            <div className="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mb-6 text-4xl">
                🚧
            </div>
            <h2 className="text-2xl font-bold text-slate-800 mb-2">{title}</h2>
            <p>Este módulo está sendo migrado para o novo frontend.</p>
        </div>
    );
}

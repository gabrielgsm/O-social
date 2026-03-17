"use client";

import { useEffect, useState } from 'react';
import { User, FileText, ChevronRight } from 'lucide-react';

export default function PersonasPage() {
  const [personas, setPersonas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await fetch('http://localhost:8000/personas');
        if (res.ok) setPersonas(await res.json());
      } catch (err) {
        console.error("Erro ao carregar personas:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  return (
    <div className="flex flex-col gap-10 py-6">
      <header className="flex flex-col gap-1">
        <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
          <User className="text-sky-500" /> Personas da IA
        </h1>
        <p className="text-slate-400">Vozes e diretrizes configuradas para cada plataforma</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {loading ? (
          [1, 2].map(i => <div key={i} className="h-64 bg-slate-900 rounded-xl animate-pulse border border-slate-800" />)
        ) : personas.map((persona: any) => (
          <div key={persona.name} className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
            <div className="p-5 bg-slate-800/50 border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center">
                  <FileText size={16} className="text-slate-300" />
                </div>
                <h3 className="font-bold text-white uppercase tracking-wider text-sm">{persona.name}</h3>
              </div>
              <button className="text-xs text-sky-400 font-medium flex items-center gap-1">
                Editar <ChevronRight size={14} />
              </button>
            </div>
            <div className="p-6">
              <pre className="text-xs text-slate-400 font-mono bg-black/30 p-4 rounded-lg h-60 overflow-y-auto leading-relaxed scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
                {persona.content}
              </pre>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

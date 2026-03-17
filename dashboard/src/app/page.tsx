"use client";

import { useEffect, useState } from 'react';
import PostCard from '@/components/PostCard';
import { Activity, CheckCircle2, AlertCircle, FileStack } from 'lucide-react';

interface Stats {
  pending: number;
  published: number;
  rejected: number;
  total: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [statsRes, postsRes] = await Promise.all([
          fetch('http://localhost:8000/stats'),
          fetch('http://localhost:8000/posts')
        ]);
        
        if (statsRes.ok) setStats(await statsRes.json());
        if (postsRes.ok) setPosts(await postsRes.json());
      } catch (err) {
        console.error("Erro ao carregar dados:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const statCards = [
    { label: 'Pendentes', value: stats?.pending ?? 0, icon: AlertCircle, color: 'text-amber-500' },
    { label: 'Publicados', value: stats?.published ?? 0, icon: CheckCircle2, color: 'text-emerald-500' },
    { label: 'Rejeitados', value: stats?.rejected ?? 0, icon: FileStack, color: 'text-rose-500' },
    { label: 'Atividade', value: stats?.total ?? 0, icon: Activity, color: 'text-sky-500' },
  ];

  return (
    <div className="flex flex-col gap-10 py-6">
      <header className="flex flex-col gap-1">
        <h1 className="text-3xl font-bold text-white tracking-tight">Overview do Motor</h1>
        <p className="text-slate-400">Gerenciamento proativo de presença social (X & Reddit)</p>
      </header>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat) => (
          <div key={stat.label} className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-400">{stat.label}</span>
              <stat.icon className={stat.color} size={20} />
            </div>
            <span className="text-2xl font-bold text-white tracking-tight">{stat.value}</span>
          </div>
        ))}
      </div>

      {/* Recent Activity */}
      <section className="flex flex-col gap-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-white tracking-tight">Atividade Recente</h2>
          <button className="text-sm text-blue-500 hover:text-blue-400 font-medium">Ver tudo</button>
        </div>
        
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 opacity-50 animate-pulse">
            {[1, 2, 3, 4].map(i => <div key={i} className="h-48 bg-slate-900 rounded-xl border border-slate-800" />)}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {posts.length > 0 ? (
              posts.map((post: any) => (
                <PostCard key={post.id} post={post} />
              ))
            ) : (
              <div className="col-span-full py-20 text-center border-2 border-dashed border-slate-800 rounded-2xl">
                <p className="text-slate-500">Nenhuma atividade registrada ainda.</p>
              </div>
            )}
          </div>
        )}
      </section>
    </div>
  );
}

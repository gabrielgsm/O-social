"use client";

import { useEffect, useState } from 'react';
import PostCard from '@/components/PostCard';
import { AlertCircle } from 'lucide-react';

export default function DraftsPage() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await fetch('http://localhost:8000/posts?status=PENDING');
        if (res.ok) setPosts(await res.json());
      } catch (err) {
        console.error("Erro ao carregar rascunhos:", err);
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
          <AlertCircle className="text-amber-500" /> Rascunhos Pendentes
        </h1>
        <p className="text-slate-400">Conteúdo aguardando sua revisão e aprovação final</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          [1, 2, 3].map(i => <div key={i} className="h-48 bg-slate-900 rounded-xl animate-pulse border border-slate-800" />)
        ) : posts.length > 0 ? (
          posts.map((post: any) => <PostCard key={post.id} post={post} />)
        ) : (
          <div className="col-span-full py-20 text-center border-2 border-dashed border-slate-800 rounded-2xl">
            <p className="text-slate-500">Nenhum rascunho pendente no momento.</p>
          </div>
        )}
      </div>
    </div>
  );
}

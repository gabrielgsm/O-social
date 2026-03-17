import { Twitter, MessageSquare, Clock, CheckCircle, XCircle } from 'lucide-react';

interface PostCardProps {
  post: {
    id: number;
    platform: string;
    draft: string;
    status: string;
    tone?: string;
    subreddit?: string;
    created_at: string;
  };
}

export default function PostCard({ post }: PostCardProps) {
  const isX = post.platform === 'x';
  
  const statusColors: Record<string, string> = {
    'PENDING': 'bg-amber-500/10 text-amber-500 border-amber-500/20',
    'PUBLISHED': 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
    'REJECTED': 'bg-rose-500/10 text-rose-500 border-rose-500/20',
    'APPROVED': 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-all flex flex-col gap-4 shadow-sm">
      <div className="flex justify-between items-start">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${isX ? 'bg-sky-500/10 text-sky-500' : 'bg-orange-500/10 text-orange-500'}`}>
            {isX ? <Twitter size={20} /> : <MessageSquare size={20} />}
          </div>
          <div>
            <h3 className="font-semibold text-white">ID #{post.id}</h3>
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <Clock size={12} />
              <span>{post.created_at.slice(0, 16).replace('T', ' ')}</span>
              {post.subreddit && (
                <span className="bg-slate-800 px-1.5 py-0.5 rounded uppercase tracking-wider">
                  r/{post.subreddit}
                </span>
              )}
            </div>
          </div>
        </div>
        
        <span className={`text-[10px] font-bold px-2 py-1 rounded-full border ${statusColors[post.status] || 'bg-slate-800 text-slate-400 border-slate-700'}`}>
          {post.status}
        </span>
      </div>

      <div className="bg-slate-950/50 rounded-lg p-4 text-sm text-slate-300 whitespace-pre-wrap line-clamp-4 font-mono leading-relaxed border border-slate-800/50">
        {post.draft}
      </div>

      <div className="flex items-center justify-between text-xs pt-2">
        <div className="flex gap-2">
          {post.tone && <span className="text-slate-500">Tom: <span className="text-slate-400 capitalize">{post.tone}</span></span>}
        </div>
        
        <div className="flex gap-3">
          {post.status === 'PENDING' && (
            <>
              <button className="text-rose-500 hover:text-rose-400 flex items-center gap-1 font-medium">
                <XCircle size={14} /> Rejeitar
              </button>
              <button className="text-emerald-500 hover:text-emerald-400 flex items-center gap-1 font-medium">
                <CheckCircle size={14} /> Aprovar
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

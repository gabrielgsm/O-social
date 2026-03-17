import Link from 'next/link';
import { LayoutDashboard, Send, FileText, Settings, User } from 'lucide-react';

export default function Sidebar() {
  const menuItems = [
    { icon: LayoutDashboard, label: 'Dashboard', href: '/' },
    { icon: FileText, label: 'Rascunhos', href: '/drafts' },
    { icon: Send, label: 'Publicados', href: '/published' },
    { icon: User, label: 'Personas', href: '/personas' },
  ];

  return (
    <div className="w-64 bg-slate-900 text-white h-screen p-4 flex flex-col gap-6 fixed">
      <div className="flex items-center gap-2 px-2 py-4 border-b border-slate-800">
        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center font-bold">O</div>
        <span className="text-xl font-bold tracking-tight">O-social</span>
      </div>
      
      <nav className="flex flex-col gap-1">
        {menuItems.map((item) => (
          <Link 
            key={item.href}
            href={item.href} 
            className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800 transition-colors text-slate-300 hover:text-white"
          >
            <item.icon size={20} />
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>

      <div className="mt-auto pt-6 border-t border-slate-800">
        <Link href="/settings" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800 text-slate-400">
          <Settings size={20} />
          <span>Configurações</span>
        </Link>
      </div>
    </div>
  );
}

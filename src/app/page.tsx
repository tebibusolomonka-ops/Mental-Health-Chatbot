'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  const [tgUser, setTgUser] = useState<any>(null);
  const [status, setStatus] = useState('በመግባት ላይ...');

  useEffect(() => {
    const tg = (window as any).Telegram?.WebApp;
    if (tg) {
      tg.expand();
      const user = tg.initDataUnsafe?.user;
      if (user) {
        setTgUser(user);
        handleSilentAuth(tg.initData);
      } else {
        setStatus('እባክዎን ይህንን መተግበሪያ በቴሌግራም ይክፈቱት።');
      }
    } else {
      setStatus('እባክዎን ይህንን መተግበሪያ በቴሌግራም ይክፈቱት።');
    }
  }, []);

  const handleSilentAuth = async (initData: string) => {
    try {
      const response = await fetch('/api/auth/telegram-miniapp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ initData }),
      });

      if (response.ok) {
        const data = await response.json();
        const savedUser = { ...tgUser, internal_id: data.user_id };
        localStorage.setItem('chat_user', JSON.stringify(savedUser));
        
        // Go straight to chat!
        setStatus('እንኳን በደህና መጡ! ወደ ውይይቱ በመግባት ላይ...');
        setTimeout(() => {
          router.push('/chat');
        }, 1000);
      } else {
        setStatus('ምዝገባው አልተሳካም። እባክዎን ቆይተው ይሞክሩ።');
      }
    } catch (error) {
      console.error('Auth error:', error);
      setStatus('ችግር ተፈጥሯል። እባክዎን ቆይተው ይሞክሩ።');
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-white flex flex-col items-center justify-center p-6 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-slate-950 to-slate-950">
      <div className="max-w-md w-full space-y-8 text-center animate-in fade-in duration-1000">
        <div className="space-y-4">
          <h1 className="text-5xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
            አይዞህ (Aizoh)
          </h1>
          <p className="text-xl text-slate-400 font-light">
            የአእምሮ ጤና ግንዛቤ ረዳት
          </p>
        </div>

        <div className="bg-slate-900/50 backdrop-blur-xl border border-white/10 p-8 rounded-3xl shadow-2xl flex flex-col items-center space-y-6">
           <div className="w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
           <p className="text-lg font-medium text-slate-200">{status}</p>
        </div>
      </div>
    </main>
  );
}

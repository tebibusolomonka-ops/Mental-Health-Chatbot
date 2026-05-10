'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  const [tgUser, setTgUser] = useState<any>(null);
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const tg = (window as any).Telegram?.WebApp;
    if (tg) {
      tg.expand();
      const user = tg.initDataUnsafe?.user;
      if (user) {
        setTgUser(user);
      } else {
        setError('እባክዎን ይህንን መተግበሪያ በቴሌግራም ይክፈቱት።');
      }
    }
  }, []);

  const handleStart = async () => {
    const tg = (window as any).Telegram?.WebApp;
    if (!tg || !tg.initData) return;

    setIsAuthenticating(true);
    setError(null);

    try {
      const response = await fetch('/api/auth/telegram-miniapp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ initData: tg.initData }),
      });

      if (response.ok) {
        const data = await response.json();
        const savedUser = { ...tgUser, internal_id: data.user_id };
        localStorage.setItem('chat_user', JSON.stringify(savedUser));
        router.push('/chat');
      } else {
        const detail = await response.json();
        setError(`ምዝገባው አልተሳካም: ${detail.detail || 'የማይታወቅ ስህተት'}`);
      }
    } catch (err) {
      setError('ግንኙነት ተቋርጧል። እባክዎን ኢንተርኔትዎን አረጋግጠው እንደገና ይሞክሩ።');
    } finally {
      setIsAuthenticating(false);
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

        <div className="bg-slate-900/50 backdrop-blur-xl border border-white/10 p-10 rounded-3xl shadow-2xl space-y-8">
          <div className="flex justify-center">
             <div className="w-24 h-24 rounded-full bg-gradient-to-tr from-blue-500 to-emerald-500 flex items-center justify-center text-4xl font-bold shadow-2xl ring-4 ring-white/5">
                {tgUser?.first_name?.charAt(0) || 'አ'}
             </div>
          </div>
          
          <div className="space-y-2">
            <h2 className="text-2xl font-semibold">ሰላም {tgUser?.first_name || 'ወዳጄ'}!</h2>
            <p className="text-slate-400 text-sm">ለመጀመር ከታች ያለውን ቁልፍ ይጫኑ</p>
          </div>
          
          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
              {error}
            </div>
          )}

          <button 
            onClick={handleStart}
            disabled={isAuthenticating}
            className="w-full py-5 px-6 bg-gradient-to-r from-blue-600 to-emerald-600 rounded-2xl font-bold text-xl shadow-xl hover:scale-105 active:scale-95 transition-all disabled:opacity-50 disabled:scale-100"
          >
            {isAuthenticating ? 'በመግባት ላይ...' : 'ውይይት ጀምር'}
          </button>
        </div>
      </div>
    </main>
  );
}

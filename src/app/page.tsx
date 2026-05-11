'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

declare global {
  interface Window {
    Telegram: any;
  }
}

export default function Home() {
  const [user, setUser] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const router = useRouter();

  useEffect(() => {
    if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
      const tg = window.Telegram.WebApp;
      tg.ready();
      tg.expand();
      
      if (tg.initDataUnsafe?.user) {
        setUser(tg.initDataUnsafe.user);
      }
    }
  }, []);

  const handleStart = async () => {
    if (!window.Telegram?.WebApp) {
      setError('እባክዎን ይህን መተግበሪያ በቴሌግራም ውስጥ ይክፈቱት።');
      return;
    }

    setIsAuthenticating(true);
    setError(null);

    try {
      const tg = window.Telegram.WebApp;
      const response = await fetch('/api/auth/telegram-miniapp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ initData: tg.initData }),
      });

      if (response.ok) {
        const data = await response.json();
        const chatUser = {
          ...user,
          internal_id: data.user_id,
        };
        localStorage.setItem('chat_user', JSON.stringify(chatUser));
        router.push('/chat');
      } else {
        const detail = await response.json();
        setError(`ምዝገባው አልተሳካም: ${detail.detail || 'የማይታወቅ ስህተት'}`);
      }
    } catch (err: any) {
      setError(`የግንኙነት ስህተት: ${err.message || 'ሊገናኝ አልቻለም'}`);
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

        <div className="bg-slate-900/50 backdrop-blur-xl border border-white/10 p-10 rounded-3xl shadow-2xl space-y-8 relative overflow-hidden">
          {user ? (
            <div className="space-y-6 animate-in slide-in-from-bottom-4">
              <div className="relative mx-auto w-24 h-24">
                <div className="absolute inset-0 bg-gradient-to-tr from-blue-500 to-emerald-500 rounded-full animate-pulse blur-xl opacity-50" />
                <div className="relative w-full h-full rounded-full bg-slate-800 border-2 border-white/20 flex items-center justify-center text-3xl font-bold">
                  {user.first_name?.[0]}
                </div>
              </div>
              
              <div className="space-y-2">
                <h2 className="text-3xl font-bold">ሰላም {user.first_name}!</h2>
                <p className="text-slate-400">ለመጀመር ከታች ያለውን ቁልፍ ይጫኑ</p>
              </div>

              {error && (
                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
                  {error}
                </div>
              )}

              <button 
                onClick={handleStart}
                disabled={isAuthenticating}
                className="w-full py-5 px-6 bg-gradient-to-r from-blue-600 to-emerald-600 rounded-2xl font-bold text-xl shadow-xl hover:scale-105 active:scale-95 transition-all disabled:opacity-50 disabled:hover:scale-100"
              >
                {isAuthenticating ? 'በማረጋገጥ ላይ...' : 'ውይይት ጀምር'}
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-slate-400">የቴሌግራም መረጃን በመጫን ላይ...</p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

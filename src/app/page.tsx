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
  const [loadingText, setLoadingText] = useState('የቴሌግራም መረጃን በመጫን ላይ...');
  const router = useRouter();

  useEffect(() => {
    // Check for existing session
    const savedUser = localStorage.getItem('chat_user');
    if (savedUser) {
      try {
        const parsed = JSON.parse(savedUser);
        if (parsed.first_name) {
          setUser(parsed);
        }
      } catch (e) {
        localStorage.removeItem('chat_user');
      }
    }

    const initTg = () => {
      if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
        const tg = window.Telegram.WebApp;
        tg.ready();
        
        const userData = tg.initDataUnsafe?.user;
        if (userData) {
          setUser(userData);
        } else if (tg.initData) {
          // If user object is missing but initData exists, we can still try to authenticate
          setLoadingText('ዝግጁ ነን፣ ለመጀመር እዚህ ይጫኑ...');
        } else {
          setTimeout(initTg, 1000);
        }
      }
    };

    initTg();
  }, []);

  const handleStart = async () => {
    const tg = window.Telegram?.WebApp;
    // Even if user is not in state, we can use tg.initData
    if (!tg?.initData) {
      setError('እባክዎን ይህን መተግበሪያ በቴሌግራም ውስጥ ይክፈቱት።');
      return;
    }

    setIsAuthenticating(true);
    setError(null);

    try {
      const response = await fetch('/api/auth/telegram-miniapp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ initData: tg.initData }),
      });

      const data = await response.json();

      if (response.ok) {
        const chatUser = {
          ...(user || {}),
          first_name: user?.first_name || data.user_id,
          internal_id: data.user_id,
        };
        localStorage.setItem('chat_user', JSON.stringify(chatUser));
        router.push('/chat');
      } else {
        setError(`ምዝገባው አልተሳካም: ${data.detail || 'የማይታወቅ ስህተት'}`);
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
          <div className="mx-auto w-32 h-32 mb-6 bg-white rounded-full p-2 shadow-2xl shadow-blue-500/20 flex items-center justify-center overflow-hidden border-4 border-slate-800">
            <img src="/logo.png" alt="Aizoh Robot Logo" className="w-full h-full object-contain" />
          </div>
          <h1 className="text-5xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
            አይዞህ
          </h1>
          <p className="text-xl text-slate-400 font-light">
            የአእምሮ ጤና ግንዛቤ ረዳት
          </p>
        </div>

        <div className="bg-slate-900/50 backdrop-blur-xl border border-white/10 p-10 rounded-3xl shadow-2xl space-y-8 min-h-[300px] flex flex-col justify-center">
          {user || (typeof window !== 'undefined' && window.Telegram?.WebApp?.initData) ? (
            <div className="space-y-6">
              <div className="relative mx-auto w-24 h-24 rounded-full bg-slate-800 border-2 border-white/20 flex items-center justify-center text-3xl font-bold">
                {user?.first_name?.[0] || '?'}
              </div>
              <h2 className="text-3xl font-bold">ሰላም {user?.first_name || 'ወዳጄ'}!</h2>
              
              {error && (
                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
                  {error}
                </div>
              )}

              <button 
                onClick={handleStart}
                disabled={isAuthenticating}
                className="w-full py-5 px-6 bg-gradient-to-r from-blue-600 to-emerald-600 rounded-2xl font-bold text-xl hover:scale-105 transition-all shadow-lg"
              >
                {isAuthenticating ? 'በማረጋገጥ ላይ...' : 'ውይይት ጀምር'}
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-slate-400">{loadingText}</p>
              
              <button 
                onClick={handleStart}
                className="text-sm text-blue-400 underline opacity-50 hover:opacity-100"
              >
                መረጃው ካልመጣ እዚህ ይጫኑ (Skip Loading)
              </button>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

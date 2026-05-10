'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  const [tgUser, setTgUser] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if we are inside Telegram
    const tg = (window as any).Telegram?.WebApp;
    if (tg) {
      tg.expand(); // Make it full height
      const user = tg.initDataUnsafe?.user;
      if (user) {
        setTgUser(user);
        // Silently auth with initData
        handleSilentAuth(tg.initData);
      }
    }
    setIsLoading(false);
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
        const savedUser = { ...tgUser, internal_id: data.user_id, has_phone: data.has_phone };
        localStorage.setItem('chat_user', JSON.stringify(savedUser));
        
        // If they already have a phone number in our DB, go straight to chat
        if (data.has_phone) {
          router.push('/chat');
        }
      }
    } catch (error) {
      console.error('Silent auth error:', error);
    }
  };

  const requestPhone = () => {
    const tg = (window as any).Telegram?.WebApp;
    if (tg) {
      tg.requestContact((callbackData: any) => {
        if (callbackData.status === 'sent') {
          // Send contact to backend to save phone number
          savePhoneNumber(callbackData.response_data);
        } else {
          alert('እባክዎን ስልክ ቁጥርዎን ያጋሩ። ለደህንነትዎ አስፈላጊ ነው።');
        }
      });
    }
  };

  const savePhoneNumber = async (contactData: any) => {
    try {
      const savedUser = JSON.parse(localStorage.getItem('chat_user') || '{}');
      const response = await fetch('/api/auth/save-phone', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          user_id: savedUser.internal_id,
          contact: contactData 
        }),
      });

      if (response.ok) {
        savedUser.has_phone = true;
        localStorage.setItem('chat_user', JSON.stringify(savedUser));
        router.push('/chat');
      }
    } catch (error) {
      console.error('Save phone error:', error);
    }
  };

  if (isLoading) return null;

  return (
    <main className="min-h-screen bg-slate-950 text-white flex flex-col items-center justify-center p-6 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-slate-950 to-slate-950">
      <div className="max-w-md w-full space-y-8 text-center animate-in fade-in slide-in-from-bottom-4 duration-1000">
        <div className="space-y-4">
          <h1 className="text-5xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
            አይዞህ (Aizoh)
          </h1>
          <p className="text-xl text-slate-400 font-light">
            የአእምሮ ጤና ግንዛቤ ረዳት
          </p>
        </div>

        <div className="bg-slate-900/50 backdrop-blur-xl border border-white/10 p-8 rounded-3xl shadow-2xl space-y-6">
          <div className="flex justify-center">
             <div className="w-20 h-20 rounded-full bg-gradient-to-tr from-blue-500 to-emerald-500 flex items-center justify-center text-3xl font-bold shadow-lg">
                {tgUser?.first_name?.charAt(0) || 'አ'}
             </div>
          </div>
          
          <h2 className="text-2xl font-semibold">ሰላም {tgUser?.first_name || 'ወዳጄ'}!</h2>
          
          <p className="text-slate-300 leading-relaxed">
            ውይይት ለመጀመር እባክዎን ስልክ ቁጥርዎን ያጋሩ። ይህ ለደህንነትዎ እና አስቸኳይ እርዳታ ሲያስፈልግዎት እንድንደርስልዎት ይረዳል።
          </p>
          
          <button 
            onClick={requestPhone}
            className="w-full py-4 px-6 bg-gradient-to-r from-blue-600 to-emerald-600 rounded-2xl font-bold text-lg shadow-lg hover:scale-105 transition-transform active:scale-95"
          >
            ስልክ ቁጥር አጋራ እና ጀምር
          </button>

          <p className="text-xs text-slate-500 italic">
            * ስልክዎ ለደህንነት እና ለእርዳታ ብቻ ጥቅም ላይ ይውላል።
          </p>
        </div>
      </div>
    </main>
  );
}

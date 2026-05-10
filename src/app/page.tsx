'use client';

import { useRouter } from 'next/navigation';
import TelegramLogin from '@/components/TelegramLogin';

export default function Home() {
  const router = useRouter();

  const handleAuth = async (user: any) => {
    try {
      const response = await fetch('/api/auth/telegram', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(user),
      });

      if (response.ok) {
        const data = await response.json();
        // Store user in local storage for simplicity or use a context/cookie
        localStorage.setItem('chat_user', JSON.stringify({ ...user, internal_id: data.user_id }));
        router.push('/chat');
      } else {
        alert('Authentication failed. Please try again.');
      }
    } catch (error) {
      console.error('Auth error:', error);
      alert('An error occurred during login.');
    }
  };

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
          <p className="text-slate-300 leading-relaxed">
            እንኳን በደህና መጡ። ይህ በሰው ሰራሽ አስተውሎት የሚሰራ የአእምሮ ጤና ግንዛቤ ረዳት ነው። 
            ውይይት ለመጀመር እባክዎን በቴሌግራም ይግቡ።
          </p>
          
          <div className="py-4">
            <TelegramLogin botUsername="amharic_care_bot" onAuth={handleAuth} />
          </div>

          <p className="text-xs text-slate-500 italic">
            * በመግባትዎ በአገልግሎት ውላችን ተስማምተዋል። ይህ ረዳት የህክምና ምክር አይተካም።
          </p>
        </div>

        <div className="flex justify-center space-x-4 opacity-50">
          <div className="h-1 w-12 bg-blue-500 rounded-full" />
          <div className="h-1 w-12 bg-emerald-500 rounded-full" />
          <div className="h-1 w-12 bg-blue-500 rounded-full" />
        </div>
      </div>
    </main>
  );
}

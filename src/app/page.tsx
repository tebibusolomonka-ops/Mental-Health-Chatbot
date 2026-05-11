'use client';

import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  const handleGuestLogin = () => {
    const guestUser = {
      internal_id: 'guest_user',
      first_name: 'Guest',
      username: 'guest'
    };
    localStorage.setItem('chat_user', JSON.stringify(guestUser));
    router.push('/chat');
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
          <p className="text-slate-300">የቻትቦቱን አገልግሎት ለመሞከር ከታች ያለውን ቁልፍ ይጫኑ።</p>
          
          <button 
            onClick={handleGuestLogin}
            className="w-full py-5 px-6 bg-gradient-to-r from-blue-600 to-emerald-600 rounded-2xl font-bold text-xl shadow-xl hover:scale-105 active:scale-95 transition-all"
          >
            እንደ እንግዳ ጀምር (Start as Guest)
          </button>
        </div>
      </div>
    </main>
  );
}

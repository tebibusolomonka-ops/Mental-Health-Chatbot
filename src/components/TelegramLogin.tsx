'use client';

import { useEffect, useRef } from 'react';

interface Props {
  botUsername: string;
  onAuth: (user: any) => void;
}

const TelegramLogin = ({ botUsername, onAuth }: Props) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Define the global callback
    (window as any).onTelegramAuth = (user: any) => {
      onAuth(user);
    };

    const script = document.createElement('script');
    script.src = 'https://telegram.org/js/telegram-widget.js?22';
    script.setAttribute('data-telegram-login', botUsername);
    script.setAttribute('data-size', 'large');
    script.setAttribute('data-radius', '10');
    script.setAttribute('data-onauth', 'onTelegramAuth(user)');
    script.setAttribute('data-request-access', 'write'); // Keep write for basic
    // CRITICAL: request_access="phone" is requested via the script attribute
    script.setAttribute('data-request-access', 'phone'); 
    script.async = true;

    if (containerRef.current) {
      containerRef.current.appendChild(script);
    }

    return () => {
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
    };
  }, [botUsername, onAuth]);

  return <div ref={containerRef} id="telegram-login-container" className="flex justify-center" />;
};

export default TelegramLogin;

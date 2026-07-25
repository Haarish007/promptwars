import React from 'react';
import { AlertCircle } from 'lucide-react';

export const SOSButton: React.FC = () => {
  return (
    <button
      type="button"
      aria-label="I'm Struggling — Launch immediate zero-typing crisis support"
      className="w-full bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-bold text-lg py-4 px-6 rounded-2xl shadow-xl shadow-red-600/30 flex items-center justify-center gap-3 transition-all transform active:scale-95 border border-red-400/30 min-h-[56px]"
      onClick={() => {
        alert("SOS Flow initialized. (Phase 0 Placeholder - full voice-first flow in Phase 6)");
      }}
    >
      <AlertCircle className="w-6 h-6 animate-pulse" />
      <span>I'm Struggling</span>
    </button>
  );
};

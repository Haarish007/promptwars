import React from 'react';
import { Outlet } from 'react-router-dom';
import { SOSButton } from './components/ui/SOSButton';

export const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between max-w-md mx-auto relative border-x border-slate-900 shadow-2xl">
      {/* Top Navbar */}
      <header className="p-4 border-b border-slate-900 flex items-center justify-between bg-slate-950/80 backdrop-blur sticky top-0 z-40">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-sky-500 flex items-center justify-center font-bold text-slate-950 text-lg shadow-md shadow-sky-500/20">
            A
          </div>
          <span className="font-bold text-lg text-white tracking-tight">Anchor</span>
        </div>
        <div className="text-xs text-slate-500 font-mono">v1.0.0-phase0</div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 p-4 pb-28">
        <Outlet />
      </main>

      {/* Persistent Bottom Bar with 'I'm Struggling' Slot */}
      <div className="fixed bottom-0 left-0 right-0 p-4 bg-slate-950/90 backdrop-blur border-t border-slate-900 z-50 max-w-md mx-auto">
        <SOSButton />
      </div>
    </div>
  );
};

export default App;

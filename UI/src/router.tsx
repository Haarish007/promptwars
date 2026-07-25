import React from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import App from './App';

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        index: true,
        element: (
          <div className="space-y-6">
            <header className="space-y-2">
              <h1 className="text-3xl font-bold text-white tracking-tight">Welcome to Anchor</h1>
              <p className="text-slate-400">
                Your proactive, safety-gated recovery and prevention companion.
              </p>
            </header>

            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-slate-400">Steady Score</span>
                <span className="px-3 py-1 bg-emerald-500/10 text-emerald-400 rounded-full text-xs font-semibold uppercase tracking-wider">
                  Low Risk
                </span>
              </div>
              <div className="text-4xl font-extrabold text-white">85 <span className="text-lg font-normal text-slate-500">/ 100</span></div>
              <p className="text-xs text-slate-400">
                Based on your recent sleep, check-ins, and activity.
              </p>
            </div>
          </div>
        ),
      },
    ],
  },
]);

export const AppRouter: React.FC = () => {
  return <RouterProvider router={router} />;
};

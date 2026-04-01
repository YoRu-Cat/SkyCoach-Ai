import React from 'react';

export default function Header() {
  return (
    <header className="border-b border-slate-700/50 backdrop-blur-lg bg-slate-900/80 sticky top-0 z-40">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
              ☀️ SkyCoach AI
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Weather-Based Activity Advisor
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs text-slate-500">
              Check the sky. Plan better activities.
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}

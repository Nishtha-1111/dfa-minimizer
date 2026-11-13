import React from 'react';

export const TopBar: React.FC = () => {
  return (
    <header className="h-16 bg-white border-b border-slate-200 px-8 py-3.5 flex items-center justify-between select-none">
      {/* Brand Logo & Name */}
      <div className="flex items-center gap-3.5">
        <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white font-bold text-xl shadow-sm transition-transform hover:scale-105">
          δ
        </div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">
          DFA Minimizer
        </h1>
      </div>

      <div className="text-xs font-medium text-slate-400">
        Moore & Table-Filling Methods
      </div>
    </header>
  );
};

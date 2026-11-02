import React from 'react';
import { Sparkles, Calendar } from 'lucide-react';

interface HeaderProps {
  title: string;
  subtitle: string;
}

export const Header: React.FC<HeaderProps> = ({ title, subtitle }) => {
  return (
    <header className="h-16 border-b border-cycle-border bg-cycle-dark/50 backdrop-blur px-8 flex items-center justify-between shrink-0">
      <div>
        <h2 className="text-lg font-bold text-white tracking-wide">{title}</h2>
        <p className="text-xs text-cycle-muted">{subtitle}</p>
      </div>

      <div className="flex items-center space-x-3">
        <div className="flex items-center space-x-2 bg-cycle-card border border-cycle-border px-3 py-1.5 rounded-lg text-xs text-cycle-muted">
          <Calendar className="w-3.5 h-3.5 text-cycle-accent" />
          <span>Histórico: Nov/2023 - Out/2026 (36m)</span>
        </div>

        <div className="flex items-center space-x-1.5 bg-gradient-to-r from-blue-900/40 to-indigo-900/40 border border-blue-700/50 px-3 py-1.5 rounded-lg text-xs text-blue-200">
          <Sparkles className="w-3.5 h-3.5 text-blue-400" />
          <span className="font-medium">Distribuidora de Autopeças (B2B)</span>
        </div>
      </div>
    </header>
  );
};


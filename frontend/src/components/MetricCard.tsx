import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subValue?: string;
  trend?: {
    value: number;
    isPositiveGood?: boolean;
    label?: string;
  };
  icon?: LucideIcon;
  badgeType?: 'observado' | 'preditivo' | 'avaliacao';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subValue,
  trend,
  icon: Icon,
  badgeType = 'observado',
}) => {
  const badgeConfig = {
    observado: { label: 'Observado', color: 'bg-slate-800 text-slate-300 border-slate-700' },
    preditivo: { label: 'Preditivo (IA)', color: 'bg-blue-950 text-blue-300 border-blue-800' },
    avaliacao: { label: 'Avaliação', color: 'bg-purple-950 text-purple-300 border-purple-800' },
  }[badgeType];

  return (
    <div className="bg-cycle-card border border-cycle-border rounded-xl p-5 hover:border-cycle-accent/50 transition-all shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-medium text-cycle-muted">{title}</span>
        <div className="flex items-center space-x-2">
          <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded border ${badgeConfig.color}`}>
            {badgeConfig.label}
          </span>
          {Icon && (
            <div className="w-8 h-8 rounded-lg bg-cycle-hover flex items-center justify-center text-cycle-accent">
              <Icon className="w-4 h-4" />
            </div>
          )}
        </div>
      </div>

      <div className="flex items-baseline justify-between">
        <div>
          <div className="text-2xl font-bold text-white tracking-tight">{value}</div>
          {subValue && <div className="text-xs text-cycle-muted mt-1">{subValue}</div>}
        </div>

        {trend && (
          <div
            className={`text-xs font-semibold px-2 py-1 rounded-md flex items-center space-x-1 ${
              (trend.value >= 0 && trend.isPositiveGood !== false) || (trend.value < 0 && trend.isPositiveGood === false)
                ? 'bg-emerald-500/10 text-emerald-400'
                : 'bg-rose-500/10 text-rose-400'
            }`}
          >
            <span>{trend.value >= 0 ? '+' : ''}{trend.value.toFixed(1)}%</span>
            {trend.label && <span className="text-[10px] opacity-75">{trend.label}</span>}
          </div>
        )}
      </div>
    </div>
  );
};


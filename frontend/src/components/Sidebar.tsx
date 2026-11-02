import React from 'react';
import {
  LayoutDashboard,
  Users,
  AlertTriangle,
  TrendingUp,
  UserCheck,
  Cpu,
  Database,
  Activity,
} from 'lucide-react';

export type TabType = 'dashboard' | 'segmentation' | 'churn' | 'growth' | 'customers' | 'models';

interface SidebarProps {
  activeTab: TabType;
  onSelectTab: (tab: TabType) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onSelectTab }) => {
  const menuItems = [
    { id: 'dashboard' as TabType, label: 'Visão Executiva', icon: LayoutDashboard },
    { id: 'segmentation' as TabType, label: 'Segmentação', icon: Users },
    { id: 'churn' as TabType, label: 'Risco de Churn', icon: AlertTriangle },
    { id: 'growth' as TabType, label: 'Crescimento (Growth)', icon: TrendingUp },
    { id: 'customers' as TabType, label: 'Customer 360', icon: UserCheck },
    { id: 'models' as TabType, label: 'Modelos & Métricas', icon: Cpu },
  ];

  return (
    <aside className="w-64 bg-cycle-dark border-r border-cycle-border flex flex-col justify-between shrink-0 select-none">
      <div>
        {/* Brand Header */}
        <div className="p-6 border-b border-cycle-border flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-tr from-cycle-primary to-cycle-accent flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg tracking-wider text-white">CYCLE AI</h1>
            <p className="text-xs text-cycle-muted">Inteligência Comercial</p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="p-4 space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-cycle-primary text-white shadow-md shadow-blue-600/30 font-semibold'
                    : 'text-cycle-muted hover:text-white hover:bg-cycle-hover'
                }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-cycle-muted'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-cycle-border text-xs text-cycle-muted space-y-2">
        <div className="flex items-center space-x-2 text-emerald-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="font-medium">Sistema Online</span>
        </div>
        <div className="flex items-center justify-between text-cycle-muted">
          <span className="flex items-center space-x-1">
            <Database className="w-3.5 h-3.5" />
            <span>PostgreSQL 16</span>
          </span>
          <span className="bg-cycle-card px-2 py-0.5 rounded border border-cycle-border">v1.0.0</span>
        </div>
      </div>
    </aside>
  );
};


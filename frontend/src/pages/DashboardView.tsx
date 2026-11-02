import React, { useEffect, useState } from 'react';
import { api, formatCurrency } from '../services/api';
import { ExecutiveDashboardKPIs } from '../types';
import { MetricCard } from '../components/MetricCard';
import {
  DollarSign,
  Users,
  AlertTriangle,
  TrendingUp,
  ArrowUpRight,
  ShieldAlert,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';

export const DashboardView: React.FC = () => {
  const [data, setData] = useState<ExecutiveDashboardKPIs | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const kpis = await api.getDashboardKPIs();
        setData(kpis);
      } catch (err: any) {
        setError(err.message || 'Erro ao carregar dashboard');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-cycle-accent"></div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8 text-center bg-rose-950/20 border border-rose-900 rounded-xl my-6">
        <p className="text-rose-400 font-medium">Não foi possível carregar os dados executivos.</p>
        <p className="text-xs text-rose-500/80 mt-1">{error}</p>
      </div>
    );
  }

  const CHURN_COLORS = ['#10B981', '#F59E0B', '#EF4444'];

  return (
    <div className="space-y-6">
      {/* Cards de KPIs de Primeira Linha */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <MetricCard
          title="Faturamento Histórico (12m)"
          value={formatCurrency(data.faturamento_historico_365d)}
          subValue={`${data.total_clientes_analisados.toLocaleString()} clientes analisados`}
          icon={DollarSign}
          badgeType="observado"
        />

        <MetricCard
          title="Previsão Faturamento (90d)"
          value={formatCurrency(data.faturamento_previsto_proximos_90d)}
          subValue={`vs R$ ${data.faturamento_recente_90d.toLocaleString('pt-BR')} (90d rec.)`}
          trend={{
            value: data.variacao_faturamento_pct,
            label: 'projeção IA',
          }}
          icon={ArrowUpRight}
          badgeType="preditivo"
        />

        <MetricCard
          title="Risco de Abandono (Churn)"
          value={`${data.total_clientes_em_risco_churn} clientes`}
          subValue={`${data.percentual_em_risco_churn}% da carteira total`}
          trend={{
            value: data.percentual_em_risco_churn,
            isPositiveGood: false,
            label: 'alta probabilidade',
          }}
          icon={AlertTriangle}
          badgeType="preditivo"
        />

        <MetricCard
          title="Potencial de Expansão (Growth)"
          value={`${data.total_clientes_potencial_growth} clientes`}
          subValue={`${data.percentual_potencial_growth}% com potencial real`}
          icon={TrendingUp}
          badgeType="preditivo"
        />
      </div>

      {/* Gráficos Centrais */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Gráfico 1: Evolução Histórica das Vendas */}
        <div className="lg:col-span-2 bg-cycle-card border border-cycle-border rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-white text-base">Evolução Mensal do Faturamento</h3>
              <p className="text-xs text-cycle-muted">Receita observada nos últimos 36 meses completos</p>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">
              Observado
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.evolucao_mensal}>
                <defs>
                  <linearGradient id="colorFaturamento" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3A86FF" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#3A86FF" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2E58" opacity={0.5} />
                <XAxis dataKey="mes" stroke="#94A3B8" fontSize={11} tickLine={false} />
                <YAxis
                  stroke="#94A3B8"
                  fontSize={11}
                  tickLine={false}
                  tickFormatter={(val) => `R$ ${(val / 1000000).toFixed(1)}M`}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0B132B', borderColor: '#1F2E58', borderRadius: '8px' }}
                  formatter={(val: any) => [formatCurrency(val), 'Faturamento']}
                  labelStyle={{ color: '#F8FAFC' }}
                />
                <Area
                  type="monotone"
                  dataKey="faturamento"
                  stroke="#3A86FF"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorFaturamento)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Gráfico 2: Distribuição por Faixa de Churn */}
        <div className="bg-cycle-card border border-cycle-border rounded-xl p-5 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-white text-base">Composição de Risco</h3>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">
                Preditivo
              </span>
            </div>
            <p className="text-xs text-cycle-muted mb-4">Estimativa do modelo de probabilidade em 90 dias</p>

            <div className="h-52 w-full flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={data.distribuicao_risco_churn}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={4}
                    dataKey="quantidade"
                    nameKey="faixa"
                  >
                    {data.distribuicao_risco_churn.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={CHURN_COLORS[index % CHURN_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0B132B', borderColor: '#1F2E58', borderRadius: '8px' }}
                    formatter={(val: any) => [`${val} clientes`, 'Quantidade']}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="space-y-2 pt-2 border-t border-cycle-border">
            {data.distribuicao_risco_churn.map((item, idx) => (
              <div key={item.faixa} className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2">
                  <span
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: CHURN_COLORS[idx % CHURN_COLORS.length] }}
                  ></span>
                  <span className="text-cycle-muted">{item.faixa}</span>
                </div>
                <span className="font-semibold text-white">
                  {item.quantidade} ({item.percentual}%)
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Gráfico 3: Segmentação K-Means */}
      <div className="bg-cycle-card border border-cycle-border rounded-xl p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-semibold text-white text-base">Distribuição dos Segmentos de Clientes (K-Means)</h3>
            <p className="text-xs text-cycle-muted">Volume de clientes e faturamento recente por grupo comportamental</p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded bg-blue-950 text-blue-300 border border-blue-800">
            Preditivo (K=3)
          </span>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.distribuicao_segmentos} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#1F2E58" opacity={0.5} horizontal={false} />
              <XAxis type="number" stroke="#94A3B8" fontSize={11} tickLine={false} />
              <YAxis
                type="category"
                dataKey="cluster_nome"
                stroke="#94A3B8"
                fontSize={11}
                width={220}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{ backgroundColor: '#0B132B', borderColor: '#1F2E58', borderRadius: '8px' }}
                formatter={(val: any, name: any) => [
                  name === 'faturamento_total_90d' ? formatCurrency(val) : val,
                  name === 'faturamento_total_90d' ? 'Faturamento (90d)' : 'Clientes',
                ]}
              />
              <Bar dataKey="quantidade" fill="#2563EB" radius={[0, 4, 4, 0]} name="Clientes" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};


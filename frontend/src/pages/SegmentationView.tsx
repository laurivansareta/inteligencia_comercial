import React, { useEffect, useState } from 'react';
import { api, formatCurrency } from '../services/api';
import { ClusterInfo } from '../types';
import { Users, CheckCircle2, TrendingUp, AlertCircle, ShoppingBag, Clock } from 'lucide-react';

interface SegmentationViewProps {
  onSelectCustomer: (id: number) => void;
}

export const SegmentationView: React.FC<SegmentationViewProps> = ({ onSelectCustomer }) => {
  const [data, setData] = useState<{
    model_type: string;
    total_clusters: number;
    silhouette_score: number;
    clusters: ClusterInfo[];
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const res = await api.getSegmentation();
        setData(res);
      } catch (err: any) {
        setError(err.message || 'Erro ao carregar segmentação');
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
        <p className="text-rose-400 font-medium">Não foi possível carregar os dados de segmentação.</p>
        <p className="text-xs text-rose-500/80 mt-1">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Banner Superior do Modelo */}
      <div className="bg-gradient-to-r from-cycle-card to-blue-950/40 border border-cycle-border rounded-xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-blue-900/40 text-blue-300 border border-blue-700">
              Não Supervisionado
            </span>
            <span className="text-xs text-cycle-muted">Algoritmo: {data.model_type}</span>
          </div>
          <h2 className="text-xl font-bold text-white mt-1">Segmentação Comportamental da Carteira</h2>
          <p className="text-xs text-cycle-muted mt-1 max-w-2xl">
            Grupos identificados através de aprendizado não-supervisionado com base em Recência, Frequência,
            Valor Monetário (RFM), Diversidade de Categorias e Pontualidade Financeira.
          </p>
        </div>

        <div className="flex items-center space-x-4 bg-cycle-dark/80 px-4 py-3 rounded-lg border border-cycle-border">
          <div className="text-center">
            <div className="text-2xl font-bold text-white">{data.total_clusters}</div>
            <div className="text-[10px] uppercase tracking-wider text-cycle-muted">Clusters</div>
          </div>
          <div className="h-8 w-px bg-cycle-border"></div>
          <div className="text-center">
            <div className="text-2xl font-bold text-emerald-400">{data.silhouette_score.toFixed(3)}</div>
            <div className="text-[10px] uppercase tracking-wider text-cycle-muted">Silhouette Score</div>
          </div>
        </div>
      </div>

      {/* Grid de Clusters */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {data.clusters.map((cluster) => {
          const isChampion = cluster.cluster_nome.includes('Campeões');
          const isRisk = cluster.cluster_nome.includes('Alerta') || cluster.cluster_nome.includes('Inativos');

          return (
            <div
              key={cluster.cluster_id}
              className={`bg-cycle-card border rounded-xl p-6 flex flex-col justify-between transition-all ${
                isChampion
                  ? 'border-blue-500/50 shadow-lg shadow-blue-500/5'
                  : isRisk
                  ? 'border-amber-500/30'
                  : 'border-cycle-border'
              }`}
            >
              <div>
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-cycle-muted">
                      Cluster #{cluster.cluster_id}
                    </span>
                    <h3 className="text-base font-bold text-white mt-0.5">{cluster.cluster_nome}</h3>
                  </div>
                  <div className="text-right">
                    <span className="text-lg font-bold text-white">{cluster.total_clientes}</span>
                    <span className="text-xs text-cycle-muted block">clientes</span>
                  </div>
                </div>

                {/* Métricas Médias do Cluster */}
                <div className="grid grid-cols-2 gap-3 p-3.5 bg-cycle-dark/60 rounded-lg border border-cycle-border/60 mb-5 text-xs">
                  <div>
                    <span className="text-cycle-muted block flex items-center space-x-1">
                      <Clock className="w-3 h-3 text-cycle-accent" />
                      <span>Recência Média</span>
                    </span>
                    <span className="font-semibold text-white mt-0.5 block">
                      {cluster.profile.recency_days} dias
                    </span>
                  </div>

                  <div>
                    <span className="text-cycle-muted block flex items-center space-x-1">
                      <ShoppingBag className="w-3 h-3 text-cycle-accent" />
                      <span>Frequência (90d)</span>
                    </span>
                    <span className="font-semibold text-white mt-0.5 block">
                      {cluster.profile.frequency_90d} pedidos
                    </span>
                  </div>

                  <div>
                    <span className="text-cycle-muted block flex items-center space-x-1">
                      <TrendingUp className="w-3 h-3 text-cycle-accent" />
                      <span>Receita Média (90d)</span>
                    </span>
                    <span className="font-semibold text-white mt-0.5 block">
                      {formatCurrency(cluster.profile.revenue_90d)}
                    </span>
                  </div>

                  <div>
                    <span className="text-cycle-muted block flex items-center space-x-1">
                      <Users className="w-3 h-3 text-cycle-accent" />
                      <span>Ticket Médio</span>
                    </span>
                    <span className="font-semibold text-white mt-0.5 block">
                      {formatCurrency(cluster.profile.avg_ticket_90d)}
                    </span>
                  </div>
                </div>

                {/* Clientes Típicos / Amostra */}
                <div>
                  <h4 className="text-xs font-semibold text-cycle-muted uppercase tracking-wider mb-2">
                    Clientes Típicos
                  </h4>
                  <div className="space-y-1.5">
                    {cluster.clientes_amostra.map((c) => (
                      <button
                        key={c.id_cliente}
                        onClick={() => onSelectCustomer(c.id_cliente)}
                        className="w-full flex items-center justify-between p-2 rounded bg-cycle-hover/60 hover:bg-cycle-primary/20 hover:text-white transition-all text-xs text-left group"
                      >
                        <span className="font-medium text-slate-200 group-hover:text-blue-300 truncate max-w-[170px]">
                          {c.nome_fantasia}
                        </span>
                        <span className="text-cycle-muted group-hover:text-white font-mono text-[11px]">
                          {formatCurrency(c.faturamento_90d)}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-cycle-border/60 mt-4 text-[11px] text-cycle-muted flex items-center justify-between">
                <span>Faturamento Total (90d):</span>
                <span className="font-bold text-white">{formatCurrency(cluster.faturamento_total_90d)}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};


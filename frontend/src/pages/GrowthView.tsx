import React, { useEffect, useState } from 'react';
import { api, formatCurrency } from '../services/api';
import { TrendingUp, Sparkles, Filter, User, ArrowUpRight } from 'lucide-react';

interface GrowthViewProps {
  onSelectCustomer: (id: number) => void;
}

export const GrowthView: React.FC<GrowthViewProps> = ({ onSelectCustomer }) => {
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [apenasExpansao, setApenasExpansao] = useState(true);
  const [filialFiltro, setFilialFiltro] = useState<number | undefined>(undefined);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const res = await api.getGrowthOpportunities({
          limit: 100,
          apenas_expansao: apenasExpansao,
          id_filial: filialFiltro,
        });
        setOpportunities(res.opportunities);
      } catch (err) {
        console.error('Erro ao carregar oportunidades:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [apenasExpansao, filialFiltro]);

  return (
    <div className="space-y-6">
      {/* Banner Superior com Filtros */}
      <div className="bg-cycle-card border border-cycle-border rounded-xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
              Regressão Supervisionada (90 dias)
            </span>
            <span className="text-xs text-cycle-muted">Algoritmo: XGBoost Regressor (R²: 0.8831)</span>
          </div>
          <h2 className="text-lg font-bold text-white mt-1">Oportunidades de Crescimento & Expansão de Receita</h2>
          <p className="text-xs text-cycle-muted">
            Identifique clientes com previsão de incremento substancial de faturamento e priorize ações de cross-sell e aumento de cota.
          </p>
        </div>

        {/* Filtros */}
        <div className="flex items-center space-x-3">
          <label className="flex items-center space-x-2 text-xs text-slate-300 bg-cycle-dark border border-cycle-border px-3 py-2 rounded-lg cursor-pointer select-none">
            <input
              type="checkbox"
              checked={apenasExpansao}
              onChange={(e) => setApenasExpansao(e.target.checked)}
              className="rounded bg-cycle-card text-cycle-accent focus:ring-0"
            />
            <span>Apenas Expansão (&ge; 10%)</span>
          </label>

          <select
            value={filialFiltro || ''}
            onChange={(e) => setFilialFiltro(e.target.value ? parseInt(e.target.value, 10) : undefined)}
            className="bg-cycle-dark border border-cycle-border text-xs rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cycle-accent"
          >
            <option value="">Todas as Filiais</option>
            <option value="1">Filial 1 - São Paulo (SP)</option>
            <option value="2">Filial 2 - Curitiba (PR)</option>
            <option value="3">Filial 3 - Belo Horizonte (MG)</option>
            <option value="4">Filial 4 - Goiânia (GO)</option>
            <option value="5">Filial 5 - Recife (PE)</option>
          </select>
        </div>
      </div>

      {/* Tabela de Oportunidades */}
      <div className="bg-cycle-card border border-cycle-border rounded-xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-cycle-border flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            <h3 className="font-semibold text-white text-sm">Ranking de Potencial de Receita Incremental</h3>
          </div>
          <span className="text-xs text-cycle-muted">{opportunities.length} clientes encontrados</span>
        </div>

        {loading ? (
          <div className="flex h-72 items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-cycle-accent"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-cycle-dark/80 text-cycle-muted uppercase text-[10px] tracking-wider border-b border-cycle-border">
                <tr>
                  <th className="py-3 px-4">Cliente</th>
                  <th className="py-3 px-3">Filial</th>
                  <th className="py-3 px-3">Segmento</th>
                  <th className="py-3 px-3 text-right">Faturamento Histórico (90d)</th>
                  <th className="py-3 px-3 text-right">Previsão IA (90d)</th>
                  <th className="py-3 px-3 text-right">Potencial Incremental</th>
                  <th className="py-3 px-3 text-center">Variação (%)</th>
                  <th className="py-3 px-3 text-center">Ação</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-cycle-border/60">
                {opportunities.map((row) => {
                  const isExpansion = row.fl_oportunidade_expansao;

                  return (
                    <tr key={row.id_cliente} className="hover:bg-cycle-hover transition-all">
                      <td className="py-3.5 px-4 font-medium text-white truncate max-w-[200px]">
                        <div>{row.nome_fantasia}</div>
                        <span className="text-[10px] text-cycle-muted block">ID #{row.id_cliente}</span>
                      </td>
                      <td className="py-3.5 px-3 text-cycle-muted">{row.filial_descricao}</td>
                      <td className="py-3.5 px-3">
                        <span className="text-[11px] px-2 py-0.5 rounded bg-cycle-dark border border-cycle-border text-slate-300">
                          {row.cluster_nome}
                        </span>
                      </td>
                      <td className="py-3.5 px-3 text-right font-mono text-cycle-muted">
                        {formatCurrency(row.revenue_90d_historico)}
                      </td>
                      <td className="py-3.5 px-3 text-right font-mono font-bold text-white">
                        {formatCurrency(row.faturamento_previsto_90d)}
                      </td>
                      <td className="py-3.5 px-3 text-right font-mono text-emerald-400 font-semibold">
                        +{formatCurrency(row.potencial_absoluto)}
                      </td>
                      <td className="py-3.5 px-3 text-center">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold ${
                            isExpansion
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                              : 'bg-slate-800 text-slate-300'
                          }`}
                        >
                          +{row.variacao_estimada_pct.toFixed(1)}%
                        </span>
                      </td>
                      <td className="py-3.5 px-3 text-center">
                        <button
                          onClick={() => onSelectCustomer(row.id_cliente)}
                          className="px-3 py-1 rounded bg-cycle-dark hover:bg-cycle-primary text-cycle-muted hover:text-white transition-all text-[11px] font-medium"
                        >
                          Ver 360
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

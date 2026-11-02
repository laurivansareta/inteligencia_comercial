import React, { useEffect, useState } from 'react';
import { api, formatCurrency } from '../services/api';
import { AlertTriangle, ShieldCheck, ShieldAlert, ArrowUpRight, ArrowDownRight, User } from 'lucide-react';

interface ChurnViewProps {
  onSelectCustomer: (id: number) => void;
}

export const ChurnView: React.FC<ChurnViewProps> = ({ onSelectCustomer }) => {
  const [ranking, setRanking] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [faixaFiltro, setFaixaFiltro] = useState<string>('');
  const [filialFiltro, setFilialFiltro] = useState<number | undefined>(undefined);
  const [selectedCustomerShap, setSelectedCustomerShap] = useState<any | null>(null);
  const [loadingShap, setLoadingShap] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const res = await api.getChurnRanking({
          limit: 100,
          faixa_risco: faixaFiltro || undefined,
          id_filial: filialFiltro,
        });
        setRanking(res.ranking);
        if (res.ranking.length > 0 && !selectedCustomerShap) {
          loadShap(res.ranking[0].id_cliente);
        }
      } catch (err) {
        console.error('Erro ao carregar ranking de churn:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [faixaFiltro, filialFiltro]);

  async function loadShap(customerId: number) {
    try {
      setLoadingShap(true);
      const res = await api.getCustomer360(customerId);
      setSelectedCustomerShap(res);
    } catch (err) {
      console.error('Erro ao carregar SHAP:', err);
    } finally {
      setLoadingShap(false);
    }
  }

  return (
    <div className="space-y-6">
      {/* Header com Filtros */}
      <div className="bg-cycle-card border border-cycle-border rounded-xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800">
              Supervisionado (90 dias)
            </span>
            <span className="text-xs text-cycle-muted">Sensibilidade Comercial Elevada (Recall: 92.8%)</span>
          </div>
          <h2 className="text-lg font-bold text-white mt-1">Ranking de Probabilidade de Abandono (Churn)</h2>
          <p className="text-xs text-cycle-muted">
            Priorize contatos comerciais com base no risco estimado e intervenha antes que o cliente interrompa as compras.
          </p>
        </div>

        {/* Filtros */}
        <div className="flex items-center space-x-3">
          <select
            value={faixaFiltro}
            onChange={(e) => setFaixaFiltro(e.target.value)}
            className="bg-cycle-dark border border-cycle-border text-xs rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cycle-accent"
          >
            <option value="">Todas as Faixas de Risco</option>
            <option value="Alto Risco">Apenas Alto Risco (&ge; 60%)</option>
            <option value="Médio Risco">Médio Risco (25% - 60%)</option>
            <option value="Baixo Risco">Baixo Risco (&lt; 25%)</option>
          </select>

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

      {/* Conteúdo: Tabela de Ranking à esquerda + Painel de Explicabilidade SHAP à direita */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Tabela do Ranking (2 Colunas) */}
        <div className="lg:col-span-2 bg-cycle-card border border-cycle-border rounded-xl overflow-hidden shadow-sm">
          <div className="p-4 border-b border-cycle-border flex items-center justify-between">
            <h3 className="font-semibold text-white text-sm">Clientes Priorizados para Retenção</h3>
            <span className="text-xs text-cycle-muted">{ranking.length} clientes exibidos</span>
          </div>

          {loading ? (
            <div className="flex h-72 items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-cycle-accent"></div>
            </div>
          ) : (
            <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-cycle-dark/80 text-cycle-muted uppercase text-[10px] tracking-wider sticky top-0 z-10 border-b border-cycle-border">
                  <tr>
                    <th className="py-3 px-4">Cliente</th>
                    <th className="py-3 px-3">Filial</th>
                    <th className="py-3 px-3 text-right">Recência</th>
                    <th className="py-3 px-3 text-right">Receita (90d)</th>
                    <th className="py-3 px-3 text-center">Risco Churn</th>
                    <th className="py-3 px-3 text-center">Ação</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-cycle-border/60">
                  {ranking.map((row) => {
                    const isSelected = selectedCustomerShap?.customer.id_cliente === row.id_cliente;
                    const isHigh = row.faixa_risco === 'Alto Risco';
                    const isMed = row.faixa_risco === 'Médio Risco';

                    return (
                      <tr
                        key={row.id_cliente}
                        onClick={() => loadShap(row.id_cliente)}
                        className={`hover:bg-cycle-hover cursor-pointer transition-all ${
                          isSelected ? 'bg-cycle-primary/10 border-l-2 border-cycle-accent' : ''
                        }`}
                      >
                        <td className="py-3 px-4 font-medium text-white truncate max-w-[180px]">
                          <div>{row.nome_fantasia}</div>
                          <span className="text-[10px] text-cycle-muted block">ID #{row.id_cliente}</span>
                        </td>
                        <td className="py-3 px-3 text-cycle-muted">{row.filial_descricao}</td>
                        <td className="py-3 px-3 text-right font-mono text-white">{row.recency_days}d</td>
                        <td className="py-3 px-3 text-right font-mono text-white">
                          {formatCurrency(row.revenue_90d)}
                        </td>
                        <td className="py-3 px-3 text-center">
                          <span
                            className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold ${
                              isHigh
                                ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                                : isMed
                                ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                                : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                            }`}
                          >
                            {(row.churn_probabilidade * 100).toFixed(1)}%
                          </span>
                        </td>
                        <td className="py-3 px-3 text-center">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onSelectCustomer(row.id_cliente);
                            }}
                            className="p-1 rounded bg-cycle-dark hover:bg-cycle-primary text-cycle-muted hover:text-white transition-all"
                            title="Abrir Customer 360"
                          >
                            <User className="w-3.5 h-3.5" />
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

        {/* Painel de Explicabilidade SHAP (1 Coluna) */}
        <div className="bg-cycle-card border border-cycle-border rounded-xl p-5 flex flex-col justify-between shadow-sm">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-cycle-border">
              <h3 className="font-semibold text-white text-sm">Explicação da Previsão (SHAP)</h3>
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">
                Transparência IA
              </span>
            </div>

            {loadingShap ? (
              <div className="flex h-64 items-center justify-center">
                <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-cycle-accent"></div>
              </div>
            ) : selectedCustomerShap ? (
              <div className="mt-4 space-y-4">
                {/* Perfil Rápido do Cliente Selecionado */}
                <div className="p-3 bg-cycle-dark/70 rounded-lg border border-cycle-border">
                  <div className="text-sm font-bold text-white">
                    {selectedCustomerShap.customer.nome_fantasia}
                  </div>
                  <div className="text-xs text-cycle-muted mt-0.5">
                    {selectedCustomerShap.customer.tipo_cliente} • {selectedCustomerShap.customer.porte} • {selectedCustomerShap.customer.uf}
                  </div>
                  <div className="mt-2.5 flex items-center justify-between text-xs pt-2 border-t border-cycle-border/60">
                    <span className="text-cycle-muted">Probabilidade Estimada:</span>
                    <span className="font-bold text-rose-400 text-sm">
                      {(selectedCustomerShap.ml_predictions.churn.probabilidade * 100).toFixed(1)}% ({selectedCustomerShap.ml_predictions.churn.faixa_risco})
                    </span>
                  </div>
                </div>

                {/* Fatores que Elevaram o Risco */}
                <div>
                  <h4 className="text-xs font-semibold text-rose-400 flex items-center space-x-1.5 mb-2">
                    <ArrowUpRight className="w-3.5 h-3.5" />
                    <span>Fatores que Elevaram o Risco</span>
                  </h4>
                  <div className="space-y-1.5">
                    {selectedCustomerShap.ml_predictions.churn.fatores_aumento_risco?.map((item: any, i: number) => (
                      <div
                        key={i}
                        className="p-2.5 rounded bg-rose-950/20 border border-rose-900/40 text-xs flex items-center justify-between"
                      >
                        <div>
                          <span className="font-medium text-slate-200 block">{item.label}</span>
                          <span className="text-[10px] text-cycle-muted">
                            Valor observado: {item.valor_observado}
                          </span>
                        </div>
                        <span className="text-rose-400 font-mono font-bold text-[11px]">
                          +{item.impact.toFixed(2)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Fatores que Reduziram o Risco */}
                <div>
                  <h4 className="text-xs font-semibold text-emerald-400 flex items-center space-x-1.5 mb-2">
                    <ArrowDownRight className="w-3.5 h-3.5" />
                    <span>Fatores Protetivos / Redução de Risco</span>
                  </h4>
                  <div className="space-y-1.5">
                    {selectedCustomerShap.ml_predictions.churn.fatores_reducao_risco?.map((item: any, i: number) => (
                      <div
                        key={i}
                        className="p-2.5 rounded bg-emerald-950/20 border border-emerald-900/40 text-xs flex items-center justify-between"
                      >
                        <div>
                          <span className="font-medium text-slate-200 block">{item.label}</span>
                          <span className="text-[10px] text-cycle-muted">
                            Valor observado: {item.valor_observado}
                          </span>
                        </div>
                        <span className="text-emerald-400 font-mono font-bold text-[11px]">
                          {item.impact.toFixed(2)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : null}
          </div>

          {selectedCustomerShap && (
            <button
              onClick={() => onSelectCustomer(selectedCustomerShap.customer.id_cliente)}
              className="w-full mt-4 py-2.5 px-4 bg-cycle-primary hover:bg-blue-600 text-white rounded-lg text-xs font-semibold transition-all shadow-md shadow-blue-600/20"
            >
              Abrir Customer 360 Completo
            </button>
          )}
        </div>
      </div>
    </div>
  );
};


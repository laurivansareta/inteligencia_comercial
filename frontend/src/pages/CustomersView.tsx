import React, { useEffect, useState } from 'react';
import { api, formatCurrency, formatDate } from '../services/api';
import { Customer, Customer360 } from '../types';
import {
  Search,
  Filter,
  User,
  ArrowLeft,
  Calendar,
  DollarSign,
  ShoppingBag,
  TrendingUp,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight,
  Clock,
  Briefcase,
  MapPin,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface CustomersViewProps {
  initialCustomerId?: number | null;
  onClearCustomerSelection?: () => void;
}

export const CustomersView: React.FC<CustomersViewProps> = ({
  initialCustomerId,
  onClearCustomerSelection,
}) => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [filialFiltro, setFilialFiltro] = useState<number | undefined>(undefined);
  const [clusterFiltro, setClusterFiltro] = useState<number | undefined>(undefined);
  const [faixaRiscoFiltro, setFaixaRiscoFiltro] = useState<string>('');
  const [loading, setLoading] = useState(false);

  // Customer 360 Selecionado
  const [selectedCustomerId, setSelectedCustomerId] = useState<number | null>(
    initialCustomerId || null
  );
  const [customer360, setCustomer360] = useState<Customer360 | null>(null);
  const [loading360, setLoading360] = useState(false);

  useEffect(() => {
    if (initialCustomerId) {
      setSelectedCustomerId(initialCustomerId);
    }
  }, [initialCustomerId]);

  // Carregar lista de clientes
  useEffect(() => {
    async function loadList() {
      try {
        setLoading(true);
        const res = await api.getCustomers({
          page,
          limit: 15,
          search: search || undefined,
          id_filial: filialFiltro,
          cluster_id: clusterFiltro,
          faixa_risco: faixaRiscoFiltro || undefined,
        });
        setCustomers(res.data);
        setTotal(res.total);
      } catch (err) {
        console.error('Erro ao listar clientes:', err);
      } finally {
        setLoading(false);
      }
    }
    loadList();
  }, [page, search, filialFiltro, clusterFiltro, faixaRiscoFiltro]);

  // Carregar Customer 360 quando selecionado
  useEffect(() => {
    if (!selectedCustomerId) {
      setCustomer360(null);
      return;
    }
    async function load360() {
      try {
        setLoading360(true);
        const res = await api.getCustomer360(selectedCustomerId!);
        setCustomer360(res);
      } catch (err) {
        console.error('Erro ao carregar 360:', err);
      } finally {
        setLoading360(false);
      }
    }
    load360();
  }, [selectedCustomerId]);

  function handleBackToList() {
    setSelectedCustomerId(null);
    setCustomer360(null);
    if (onClearCustomerSelection) {
      onClearCustomerSelection();
    }
  }

  // Se um cliente estiver selecionado, renderiza a visão Customer 360 completa
  if (selectedCustomerId) {
    if (loading360 || !customer360) {
      return (
        <div className="flex h-96 items-center justify-center">
          <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-cycle-accent"></div>
        </div>
      );
    }

    const { customer, latest_snapshot, monthly_history, recent_sales, ml_predictions } = customer360;
    const isHighRisk = ml_predictions.churn.faixa_risco === 'Alto Risco';

    return (
      <div className="space-y-6">
        {/* Barra Superior de Retorno */}
        <div className="flex items-center justify-between">
          <button
            onClick={handleBackToList}
            className="flex items-center space-x-2 text-xs font-semibold text-cycle-muted hover:text-white bg-cycle-card border border-cycle-border px-3.5 py-2 rounded-lg transition-all"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Voltar para Lista de Clientes</span>
          </button>

          <span className="text-xs text-cycle-muted">
            Data de Referência da Previsão: 31/10/2026
          </span>
        </div>

        {/* Ficha Cadastral e Cartão 360 */}
        <div className="bg-gradient-to-r from-cycle-card to-blue-950/30 border border-cycle-border rounded-xl p-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 rounded-xl bg-cycle-primary flex items-center justify-center text-white text-xl font-bold shrink-0 shadow-md">
                {customer.nome_fantasia.charAt(0)}
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h2 className="text-xl font-bold text-white">{customer.nome_fantasia}</h2>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-cycle-dark border border-cycle-border text-cycle-muted">
                    ID #{customer.id_cliente}
                  </span>
                </div>
                <div className="flex flex-wrap items-center gap-3 mt-1.5 text-xs text-cycle-muted">
                  <span className="flex items-center space-x-1">
                    <Briefcase className="w-3.5 h-3.5" />
                    <span>{customer.tipo_cliente} • Porte {customer.porte}</span>
                  </span>
                  <span>•</span>
                  <span className="flex items-center space-x-1">
                    <MapPin className="w-3.5 h-3.5" />
                    <span>{customer.filial_descricao} ({customer.uf})</span>
                  </span>
                  <span>•</span>
                  <span className="flex items-center space-x-1">
                    <User className="w-3.5 h-3.5" />
                    <span>{customer.vendedor_descricao}</span>
                  </span>
                </div>
              </div>
            </div>

            {/* Badges de Destaque dos Modelos */}
            <div className="flex flex-wrap items-center gap-3">
              <div className="px-3.5 py-2 rounded-lg bg-cycle-dark/80 border border-cycle-border text-right">
                <span className="text-[10px] uppercase font-bold text-cycle-muted block">Segmento</span>
                <span className="text-xs font-bold text-blue-400">
                  {ml_predictions.segmentation.cluster_nome}
                </span>
              </div>

              <div className="px-3.5 py-2 rounded-lg bg-cycle-dark/80 border border-cycle-border text-right">
                <span className="text-[10px] uppercase font-bold text-cycle-muted block">Risco de Churn</span>
                <span className={`text-xs font-bold ${isHighRisk ? 'text-rose-400' : 'text-emerald-400'}`}>
                  {(ml_predictions.churn.probabilidade * 100).toFixed(1)}% ({ml_predictions.churn.faixa_risco})
                </span>
              </div>

              <div className="px-3.5 py-2 rounded-lg bg-cycle-dark/80 border border-cycle-border text-right">
                <span className="text-[10px] uppercase font-bold text-cycle-muted block">Previsão 90d</span>
                <span className="text-xs font-bold text-white">
                  {formatCurrency(ml_predictions.growth.faturamento_previsto_90d)}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Linha de Indicadores Operacionais */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
          <div className="bg-cycle-card border border-cycle-border p-4 rounded-xl">
            <span className="text-cycle-muted block flex items-center space-x-1 mb-1">
              <Clock className="w-3.5 h-3.5 text-cycle-accent" />
              <span>Dias sem Comprar</span>
            </span>
            <span className="text-xl font-bold text-white">{latest_snapshot.recency_days} dias</span>
          </div>

          <div className="bg-cycle-card border border-cycle-border p-4 rounded-xl">
            <span className="text-cycle-muted block flex items-center space-x-1 mb-1">
              <ShoppingBag className="w-3.5 h-3.5 text-cycle-accent" />
              <span>Pedidos (90d)</span>
            </span>
            <span className="text-xl font-bold text-white">{latest_snapshot.frequency_90d} pedidos</span>
          </div>

          <div className="bg-cycle-card border border-cycle-border p-4 rounded-xl">
            <span className="text-cycle-muted block flex items-center space-x-1 mb-1">
              <DollarSign className="w-3.5 h-3.5 text-cycle-accent" />
              <span>Receita Recente (90d)</span>
            </span>
            <span className="text-xl font-bold text-white">
              {formatCurrency(latest_snapshot.revenue_90d)}
            </span>
          </div>

          <div className="bg-cycle-card border border-cycle-border p-4 rounded-xl">
            <span className="text-cycle-muted block flex items-center space-x-1 mb-1">
              <TrendingUp className="w-3.5 h-3.5 text-cycle-accent" />
              <span>Pontualidade Títulos</span>
            </span>
            <span className="text-xl font-bold text-white">
              {((1 - latest_snapshot.late_payment_rate) * 100).toFixed(0)}% em dia
            </span>
          </div>
        </div>

        {/* Gráfico Histórico + Painel SHAP */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Histórico Mensal */}
          <div className="lg:col-span-2 bg-cycle-card border border-cycle-border rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-semibold text-white text-sm">Histórico Mensal de Faturamento</h3>
                <p className="text-xs text-cycle-muted">Evolução dos pedidos e receita ao longo do tempo</p>
              </div>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                Observado
              </span>
            </div>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={monthly_history}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1F2E58" opacity={0.5} />
                  <XAxis dataKey="mes_referencia" stroke="#94A3B8" fontSize={10} tickLine={false} />
                  <YAxis
                    stroke="#94A3B8"
                    fontSize={10}
                    tickLine={false}
                    tickFormatter={(v) => `R$ ${(v / 1000).toFixed(0)}k`}
                  />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0B132B', borderColor: '#1F2E58', borderRadius: '8px' }}
                    formatter={(val: any) => [formatCurrency(val), 'Faturamento']}
                  />
                  <Area
                    type="monotone"
                    dataKey="faturamento"
                    stroke="#3A86FF"
                    fill="#3A86FF"
                    fillOpacity={0.2}
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Explicabilidade SHAP Individual */}
          <div className="bg-cycle-card border border-cycle-border rounded-xl p-5 flex flex-col justify-between shadow-sm">
            <div>
              <div className="flex items-center justify-between pb-3 border-b border-cycle-border">
                <h3 className="font-semibold text-white text-sm">Fatores de Influência (SHAP)</h3>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">
                  Explicabilidade IA
                </span>
              </div>

              <div className="mt-4 space-y-4">
                {/* Fatores que Elevaram o Risco */}
                <div>
                  <h4 className="text-xs font-semibold text-rose-400 flex items-center space-x-1.5 mb-2">
                    <ArrowUpRight className="w-3.5 h-3.5" />
                    <span>Elevaram o Risco de Abandono</span>
                  </h4>
                  <div className="space-y-1.5">
                    {ml_predictions.churn.fatores_aumento_risco?.map((item, i) => (
                      <div
                        key={i}
                        className="p-2.5 rounded bg-rose-950/20 border border-rose-900/40 text-xs flex items-center justify-between"
                      >
                        <span className="text-slate-200">{item.label}</span>
                        <span className="text-rose-400 font-mono font-bold text-[11px]">
                          +{item.impact.toFixed(2)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Fatores Protetivos */}
                <div>
                  <h4 className="text-xs font-semibold text-emerald-400 flex items-center space-x-1.5 mb-2">
                    <ArrowDownRight className="w-3.5 h-3.5" />
                    <span>Fatores de Fidelidade / Protetivos</span>
                  </h4>
                  <div className="space-y-1.5">
                    {ml_predictions.churn.fatores_reducao_risco?.map((item, i) => (
                      <div
                        key={i}
                        className="p-2.5 rounded bg-emerald-950/20 border border-emerald-900/40 text-xs flex items-center justify-between"
                      >
                        <span className="text-slate-200">{item.label}</span>
                        <span className="text-emerald-400 font-mono font-bold text-[11px]">
                          {item.impact.toFixed(2)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <p className="text-[10px] text-cycle-muted mt-4 pt-3 border-t border-cycle-border">
              * Fatores baseados nos valores SHAP da predição. Representam peso relativo das características, não causalidade comprovada.
            </p>
          </div>
        </div>

        {/* Tabela de Vendas Recentes */}
        <div className="bg-cycle-card border border-cycle-border rounded-xl p-5 shadow-sm">
          <h3 className="font-semibold text-white text-sm mb-3">Últimas Transações Registradas</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-cycle-dark/80 text-cycle-muted uppercase text-[10px] tracking-wider border-b border-cycle-border">
                <tr>
                  <th className="py-2.5 px-4">ID Venda</th>
                  <th className="py-2.5 px-3">Data</th>
                  <th className="py-2.5 px-3">Produto</th>
                  <th className="py-2.5 px-3 text-right">Qtd</th>
                  <th className="py-2.5 px-3 text-right">Valor Líquido</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-cycle-border/60">
                {recent_sales.map((v) => (
                  <tr key={v.id_venda} className="hover:bg-cycle-hover">
                    <td className="py-2.5 px-4 font-mono text-cycle-muted">#{v.id_venda}</td>
                    <td className="py-2.5 px-3 text-white">{v.data_venda}</td>
                    <td className="py-2.5 px-3 text-white font-medium">{v.produto_descricao}</td>
                    <td className="py-2.5 px-3 text-right font-mono text-cycle-muted">{v.quantidade}</td>
                    <td className="py-2.5 px-3 text-right font-mono font-semibold text-white">
                      {formatCurrency(v.valor_liquido)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  }

  // Visualização de Lista de Clientes
  return (
    <div className="space-y-6">
      {/* Barra de Filtros */}
      <div className="bg-cycle-card border border-cycle-border rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Campo de Busca */}
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-3 text-cycle-muted" />
          <input
            type="text"
            placeholder="Buscar por nome ou ID..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="w-full bg-cycle-dark border border-cycle-border rounded-lg pl-9 pr-4 py-2 text-xs text-white placeholder-cycle-muted focus:outline-none focus:border-cycle-accent"
          />
        </div>

        {/* Dropdowns de Filtro */}
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={filialFiltro || ''}
            onChange={(e) => {
              setFilialFiltro(e.target.value ? parseInt(e.target.value, 10) : undefined);
              setPage(1);
            }}
            className="bg-cycle-dark border border-cycle-border text-xs rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cycle-accent"
          >
            <option value="">Todas as Filiais</option>
            <option value="1">Filial São Paulo</option>
            <option value="2">Filial Curitiba</option>
            <option value="3">Filial Belo Horizonte</option>
            <option value="4">Filial Goiânia</option>
            <option value="5">Filial Recife</option>
          </select>

          <select
            value={clusterFiltro !== undefined ? clusterFiltro : ''}
            onChange={(e) => {
              setClusterFiltro(e.target.value !== '' ? parseInt(e.target.value, 10) : undefined);
              setPage(1);
            }}
            className="bg-cycle-dark border border-cycle-border text-xs rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cycle-accent"
          >
            <option value="">Todos os Segmentos</option>
            <option value="0">Cluster 0 (Campeões)</option>
            <option value="1">Cluster 1 (Inativos)</option>
            <option value="2">Cluster 2 (Em Alerta)</option>
          </select>

          <select
            value={faixaRiscoFiltro}
            onChange={(e) => {
              setFaixaRiscoFiltro(e.target.value);
              setPage(1);
            }}
            className="bg-cycle-dark border border-cycle-border text-xs rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cycle-accent"
          >
            <option value="">Todas as Faixas de Churn</option>
            <option value="Alto Risco">Alto Risco</option>
            <option value="Médio Risco">Médio Risco</option>
            <option value="Baixo Risco">Baixo Risco</option>
          </select>
        </div>
      </div>

      {/* Tabela de Clientes */}
      <div className="bg-cycle-card border border-cycle-border rounded-xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-cycle-border flex items-center justify-between">
          <h3 className="font-semibold text-white text-sm">Carteira de Clientes Analisada</h3>
          <span className="text-xs text-cycle-muted">{total} clientes cadastrados</span>
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
                  <th className="py-3 px-3">Tipo / Porte</th>
                  <th className="py-3 px-3">Filial</th>
                  <th className="py-3 px-3">Segmento</th>
                  <th className="py-3 px-3 text-center">Risco Churn</th>
                  <th className="py-3 px-3 text-right">Previsão 90d</th>
                  <th className="py-3 px-3 text-center">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-cycle-border/60">
                {customers.map((c) => {
                  const isHigh = c.faixa_risco === 'Alto Risco';
                  const isMed = c.faixa_risco === 'Médio Risco';

                  return (
                    <tr
                      key={c.id_cliente}
                      onClick={() => setSelectedCustomerId(c.id_cliente)}
                      className="hover:bg-cycle-hover cursor-pointer transition-all"
                    >
                      <td className="py-3.5 px-4 font-medium text-white truncate max-w-[200px]">
                        <div>{c.nome_fantasia}</div>
                        <span className="text-[10px] text-cycle-muted block">ID #{c.id_cliente}</span>
                      </td>
                      <td className="py-3.5 px-3 text-cycle-muted">
                        <div>{c.tipo_cliente}</div>
                        <span className="text-[10px] text-slate-400 block">{c.porte}</span>
                      </td>
                      <td className="py-3.5 px-3 text-cycle-muted">
                        <div>{c.filial_descricao}</div>
                        <span className="text-[10px] text-slate-400 block">{c.uf}</span>
                      </td>
                      <td className="py-3.5 px-3">
                        <span className="text-[11px] px-2 py-0.5 rounded bg-cycle-dark border border-cycle-border text-slate-300">
                          {c.cluster_nome || '-'}
                        </span>
                      </td>
                      <td className="py-3.5 px-3 text-center">
                        {c.churn_probabilidade !== undefined ? (
                          <span
                            className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold ${
                              isHigh
                                ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                                : isMed
                                ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                                : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                            }`}
                          >
                            {(c.churn_probabilidade * 100).toFixed(1)}%
                          </span>
                        ) : (
                          '-'
                        )}
                      </td>
                      <td className="py-3.5 px-3 text-right font-mono font-semibold text-white">
                        {formatCurrency(c.faturamento_previsto_90d)}
                      </td>
                      <td className="py-3.5 px-3 text-center">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedCustomerId(c.id_cliente);
                          }}
                          className="px-2.5 py-1 rounded bg-cycle-primary/20 text-blue-300 hover:bg-cycle-primary hover:text-white transition-all text-[11px] font-semibold"
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

        {/* Paginação */}
        <div className="p-4 border-t border-cycle-border flex items-center justify-between text-xs text-cycle-muted">
          <span>Página {page} de {Math.ceil(total / 15) || 1}</span>
          <div className="flex items-center space-x-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              className="px-3 py-1.5 rounded bg-cycle-dark border border-cycle-border text-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-cycle-hover"
            >
              Anterior
            </button>
            <button
              disabled={page * 15 >= total}
              onClick={() => setPage((p) => p + 1)}
              className="px-3 py-1.5 rounded bg-cycle-dark border border-cycle-border text-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-cycle-hover"
            >
              Próxima
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export interface Customer {
  id_cliente: number;
  nome_fantasia: string;
  tipo_cliente: string;
  porte: string;
  uf: string;
  id_filial: number;
  filial_descricao?: string;
  id_vendedor: number;
  vendedor_descricao?: string;
  data_cadastro: string;
  fl_ativo: boolean;
  cluster_id?: number;
  cluster_nome?: string;
  churn_probabilidade?: number;
  faixa_risco?: 'Baixo Risco' | 'Médio Risco' | 'Alto Risco';
  faturamento_previsto_90d?: number;
  potencial_absoluto?: number;
  variacao_estimada_pct?: number;
}

export interface CustomerSnapshot {
  id_cliente: number;
  data_referencia: string;
  recency_days: number;
  frequency_30d: number;
  frequency_90d: number;
  frequency_180d: number;
  revenue_30d: number;
  revenue_90d: number;
  revenue_180d: number;
  revenue_365d: number;
  avg_ticket_90d: number;
  revenue_variation_90d: number;
  frequency_variation_90d: number;
  avg_days_between_orders: number;
  category_diversity: number;
  avg_payment_delay: number;
  late_payment_rate: number;
  returns_rate: number;
  churn_label_90d?: number | null;
  future_revenue_90d?: number | null;
  feature_version: string;
}

export interface ShapFactor {
  feature: string;
  label: string;
  impact: number;
  valor_observado: number;
}

export interface Customer360 {
  customer: Customer;
  latest_snapshot: CustomerSnapshot;
  monthly_history: Array<{
    mes_referencia: string;
    faturamento: number;
    quantidade_pedidos: number;
    ticket_medio: number;
  }>;
  recent_sales: Array<{
    id_venda: number;
    data_venda: string;
    produto_descricao: string;
    quantidade: number;
    valor_liquido: number;
  }>;
  ml_predictions: {
    segmentation: {
      cluster_id: number;
      cluster_nome: string;
    };
    churn: {
      probabilidade: number;
      faixa_risco: 'Baixo Risco' | 'Médio Risco' | 'Alto Risco';
      fatores_aumento_risco: ShapFactor[];
      fatores_reducao_risco: ShapFactor[];
    };
    growth: {
      faturamento_previsto_90d: number;
      potencial_absoluto: number;
      variacao_estimada_pct: number;
      fl_oportunidade_expansao: boolean;
    };
  };
}

export interface ExecutiveDashboardKPIs {
  total_clientes_analisados: number;
  clientes_ativos: number;
  faturamento_historico_365d: number;
  faturamento_previsto_proximos_90d: number;
  faturamento_recente_90d: number;
  variacao_faturamento_pct: number;
  total_clientes_em_risco_churn: number;
  percentual_em_risco_churn: number;
  total_clientes_potencial_growth: number;
  percentual_potencial_growth: number;
  distribuicao_segmentos: Array<{
    cluster_id: number;
    cluster_nome: string;
    quantidade: number;
    faturamento_total_90d: number;
    ticket_medio: number;
  }>;
  distribuicao_risco_churn: Array<{
    faixa: string;
    quantidade: number;
    percentual: number;
  }>;
  evolucao_mensal: Array<{
    mes: string;
    faturamento: number;
    pedidos: number;
  }>;
}

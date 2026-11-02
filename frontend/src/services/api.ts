import {
  ExecutiveDashboardKPIs,
  Customer,
  Customer360,
  ClusterInfo,
  ModelsMetricsResponse,
} from '../types';

const BASE_URL = '/api';

export const api = {
  async getDashboardKPIs(): Promise<ExecutiveDashboardKPIs> {
    const res = await fetch(`${BASE_URL}/dashboard`);
    if (!res.ok) throw new Error('Falha ao carregar indicadores executivos');
    return res.json();
  },

  async getCustomers(params?: {
    page?: number;
    limit?: number;
    search?: string;
    id_filial?: number;
    cluster_id?: number;
    faixa_risco?: string;
    sortBy?: string;
    sortOrder?: 'asc' | 'desc';
  }): Promise<{
    data: Customer[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    const query = new URLSearchParams();
    if (params?.page) query.append('page', params.page.toString());
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.search) query.append('search', params.search);
    if (params?.id_filial) query.append('id_filial', params.id_filial.toString());
    if (params?.cluster_id !== undefined) query.append('cluster_id', params.cluster_id.toString());
    if (params?.faixa_risco) query.append('faixa_risco', params.faixa_risco);
    if (params?.sortBy) query.append('sortBy', params.sortBy);
    if (params?.sortOrder) query.append('sortOrder', params.sortOrder);

    const res = await fetch(`${BASE_URL}/customers?${query.toString()}`);
    if (!res.ok) throw new Error('Falha ao carregar lista de clientes');
    return res.json();
  },

  async getCustomer360(customerId: number): Promise<Customer360> {
    const res = await fetch(`${BASE_URL}/customers/${customerId}`);
    if (!res.ok) throw new Error('Falha ao carregar Customer 360');
    return res.json();
  },

  async getSegmentation(): Promise<{
    model_type: string;
    total_clusters: number;
    silhouette_score: number;
    clusters: ClusterInfo[];
  }> {
    const res = await fetch(`${BASE_URL}/segmentation`);
    if (!res.ok) throw new Error('Falha ao carregar segmentação de clientes');
    return res.json();
  },

  async getChurnRanking(params?: {
    limit?: number;
    id_filial?: number;
    faixa_risco?: string;
  }): Promise<{
    total_analisados: number;
    ranking: any[];
  }> {
    const query = new URLSearchParams();
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.id_filial) query.append('id_filial', params.id_filial.toString());
    if (params?.faixa_risco) query.append('faixa_risco', params.faixa_risco);

    const res = await fetch(`${BASE_URL}/churn/ranking?${query.toString()}`);
    if (!res.ok) throw new Error('Falha ao carregar ranking de churn');
    return res.json();
  },

  async getGrowthOpportunities(params?: {
    limit?: number;
    id_filial?: number;
    apenas_expansao?: boolean;
  }): Promise<{
    total_analisados: number;
    opportunities: any[];
  }> {
    const query = new URLSearchParams();
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.id_filial) query.append('id_filial', params.id_filial.toString());
    if (params?.apenas_expansao) query.append('apenas_expansao', 'true');

    const res = await fetch(`${BASE_URL}/growth/opportunities?${query.toString()}`);
    if (!res.ok) throw new Error('Falha ao carregar oportunidades de crescimento');
    return res.json();
  },

  async getModelsMetrics(): Promise<ModelsMetricsResponse> {
    const res = await fetch(`${BASE_URL}/models/metrics`);
    if (!res.ok) throw new Error('Falha ao carregar métricas dos modelos');
    return res.json();
  },
};

export function formatCurrency(value?: number): string {
  if (value === undefined || value === null) return 'R$ 0,00';
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
  }).format(value);
}

export function formatDate(dateStr?: string): string {
  if (!dateStr) return '-';
  try {
    const d = new Date(dateStr);
    return new Intl.DateTimeFormat('pt-BR').format(d);
  } catch {
    return dateStr;
  }
}

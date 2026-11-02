import { query } from '../db/index.js';
import { mlService } from './mlService.js';
import { Customer, Customer360, CustomerSnapshot } from '../types/index.js';

export interface ListCustomersParams {
  page?: number;
  limit?: number;
  search?: string;
  id_filial?: number;
  cluster_id?: number;
  faixa_risco?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export class CustomerService {
  public async listCustomers(params: ListCustomersParams): Promise<{
    data: Customer[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    const page = Math.max(1, params.page || 1);
    const limit = Math.min(100, Math.max(1, params.limit || 20));

    // Garantir que os scores de ML estão no cache
    const allScores = await mlService.getAllCustomerScores();
    const scoreMap = new Map(allScores.map((s) => [s.id_cliente, s]));

    // Query base no banco
    let sql = `
      SELECT 
        c.id_cliente,
        c.nome_fantasia,
        c.tipo_cliente,
        c.porte,
        c.uf,
        c.id_filial,
        f.descricao as filial_descricao,
        c.id_vendedor,
        v.descricao as vendedor_descricao,
        c.data_cadastro,
        c.fl_ativo
      FROM dim_cliente c
      JOIN dim_filial f ON c.id_filial = f.id_filial
      JOIN dim_vendedor v ON c.id_vendedor = v.id_vendedor
      WHERE 1=1
    `;

    const queryParams: any[] = [];

    if (params.search) {
      queryParams.push(`%${params.search}%`);
      sql += ` AND (c.nome_fantasia ILIKE $${queryParams.length} OR CAST(c.id_cliente AS TEXT) ILIKE $${queryParams.length})`;
    }

    if (params.id_filial) {
      queryParams.push(params.id_filial);
      sql += ` AND c.id_filial = $${queryParams.length}`;
    }

    sql += ` ORDER BY c.id_cliente ASC`;

    const res = await query(sql, queryParams);
    let rows: Customer[] = res.rows.map((r) => {
      const ml = scoreMap.get(r.id_cliente);
      return {
        ...r,
        cluster_id: ml?.cluster_id,
        cluster_nome: ml?.cluster_nome,
        churn_probabilidade: ml?.churn_probabilidade,
        faixa_risco: ml?.faixa_risco,
        faturamento_previsto_90d: ml?.faturamento_previsto_90d,
        potencial_absoluto: ml?.potencial_absoluto,
        variacao_estimada_pct: ml?.variacao_estimada_pct,
      };
    });

    // Filtros por ML (cluster_id e faixa_risco)
    if (params.cluster_id !== undefined && params.cluster_id !== null) {
      rows = rows.filter((r) => r.cluster_id === params.cluster_id);
    }

    if (params.faixa_risco) {
      rows = rows.filter((r) => r.faixa_risco === params.faixa_risco);
    }

    // Ordenação personalizada
    if (params.sortBy) {
      const field = params.sortBy as keyof Customer;
      const order = params.sortOrder === 'asc' ? 1 : -1;
      rows.sort((a, b) => {
        const valA = a[field] ?? 0;
        const valB = b[field] ?? 0;
        if (valA < valB) return -1 * order;
        if (valA > valB) return 1 * order;
        return 0;
      });
    }

    const total = rows.length;
    const totalPages = Math.ceil(total / limit);
    const offset = (page - 1) * limit;
    const paginated = rows.slice(offset, offset + limit);

    return {
      data: paginated,
      total,
      page,
      limit,
      totalPages,
    };
  }

  public async getCustomer360(customerId: number): Promise<Customer360 | null> {
    // 1. Dados cadastrais
    const custRes = await query(
      `
      SELECT 
        c.id_cliente,
        c.nome_fantasia,
        c.tipo_cliente,
        c.porte,
        c.uf,
        c.id_filial,
        f.descricao as filial_descricao,
        c.id_vendedor,
        v.descricao as vendedor_descricao,
        c.data_cadastro,
        c.fl_ativo
      FROM dim_cliente c
      JOIN dim_filial f ON c.id_filial = f.id_filial
      JOIN dim_vendedor v ON c.id_vendedor = v.id_vendedor
      WHERE c.id_cliente = $1;
      `,
      [customerId]
    );

    if (custRes.rowCount === 0) {
      return null;
    }
    const customer = custRes.rows[0];

    // 2. Snapshot mais recente
    const snapRes = await query(
      `
      SELECT *
      FROM ml_cliente_snapshot
      WHERE id_cliente = $1
      ORDER BY data_referencia DESC
      LIMIT 1;
      `,
      [customerId]
    );
    const latestSnapshot: CustomerSnapshot = snapRes.rows[0] || {};

    // 3. Histórico mensal (últimos 12 a 24 meses)
    const historyRes = await query(
      `
      SELECT 
        TO_CHAR(mes_referencia, 'YYYY-MM-DD') as mes_referencia,
        faturamento,
        quantidade_pedidos,
        ticket_medio
      FROM fato_cliente_mes
      WHERE id_cliente = $1
      ORDER BY mes_referencia ASC;
      `,
      [customerId]
    );

    // 4. Vendas recentes
    const salesRes = await query(
      `
      SELECT 
        v.id_venda,
        TO_CHAR(v.data_venda, 'YYYY-MM-DD') as data_venda,
        p.descricao as produto_descricao,
        v.quantidade,
        v.valor_liquido
      FROM fato_venda v
      JOIN dim_produto p ON v.id_produto = p.id_produto
      WHERE v.id_cliente = $1
      ORDER BY v.data_venda DESC
      LIMIT 10;
      `,
      [customerId]
    );

    // 5. Previsões e Explicabilidade SHAP
    const mlExpl = await mlService.getCustomerExplanation(customerId);

    return {
      customer,
      latest_snapshot: latestSnapshot,
      monthly_history: historyRes.rows,
      recent_sales: salesRes.rows,
      ml_predictions: {
        segmentation: mlExpl.segmentation || { cluster_id: 0, cluster_nome: 'Não classificado' },
        churn: mlExpl.churn || {
          probabilidade: 0,
          faixa_risco: 'Baixo Risco',
          fatores_aumento_risco: [],
          fatores_reducao_risco: [],
        },
        growth: mlExpl.growth || {
          faturamento_previsto_90d: 0,
          potencial_absoluto: 0,
          variacao_estimada_pct: 0,
          fl_oportunidade_expansao: false,
        },
      },
    };
  }
}

export const customerService = new CustomerService();


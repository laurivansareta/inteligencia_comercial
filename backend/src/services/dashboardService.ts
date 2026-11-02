import { query } from '../db/index.js';
import { mlService } from './mlService.js';
import { ExecutiveDashboardKPIs } from '../types/index.js';

export class DashboardService {
  public async getExecutiveKPIs(): Promise<ExecutiveDashboardKPIs> {
    // 1. Obter scores de todos os clientes
    const allScores = await mlService.getAllCustomerScores();

    // 2. Consulta de totais históricos no banco
    const totalsRes = await query(`
      SELECT 
        COUNT(DISTINCT id_cliente) as total_clientes,
        COUNT(DISTINCT CASE WHEN fl_ativo = TRUE THEN id_cliente END) as clientes_ativos
      FROM dim_cliente;
    `);
    const totalClientes = parseInt(totalsRes.rows[0]?.total_clientes || '0', 10);
    const clientesAtivos = parseInt(totalsRes.rows[0]?.clientes_ativos || '0', 10);

    // 3. Faturamento histórico dos últimos 365 dias e 90 dias
    const revRes = await query(`
      SELECT 
        COALESCE(SUM(CASE WHEN data_venda >= (SELECT MAX(data_venda) - INTERVAL '365 days' FROM fato_venda) THEN valor_liquido END), 0) as rev_365d,
        COALESCE(SUM(CASE WHEN data_venda >= (SELECT MAX(data_venda) - INTERVAL '90 days' FROM fato_venda) THEN valor_liquido END), 0) as rev_90d
      FROM fato_venda;
    `);
    const rev365d = parseFloat(revRes.rows[0]?.rev_365d || '0');
    const rev90d = parseFloat(revRes.rows[0]?.rev_90d || '0');

    // 4. Métricas consolidadas dos modelos
    let totalRiscoChurn = 0;
    let totalPotencialGrowth = 0;
    let faturamentoPrevisto90d = 0;

    const clustersMap: Record<number, { nome: string; count: number; rev90d: number }> = {};
    const churnTiersCount: Record<string, number> = {
      'Baixo Risco': 0,
      'Médio Risco': 0,
      'Alto Risco': 0,
    };

    for (const score of allScores) {
      // Churn
      if (score.faixa_risco === 'Alto Risco') {
        totalRiscoChurn++;
      }
      if (churnTiersCount[score.faixa_risco] !== undefined) {
        churnTiersCount[score.faixa_risco]++;
      }

      // Growth
      if (score.fl_oportunidade_expansao) {
        totalPotencialGrowth++;
      }
      faturamentoPrevisto90d += parseFloat(score.faturamento_previsto_90d || 0);

      // Segmentação
      const cid = score.cluster_id;
      if (!clustersMap[cid]) {
        clustersMap[cid] = {
          nome: score.cluster_nome || `Segmento ${cid}`,
          count: 0,
          rev90d: 0,
        };
      }
      clustersMap[cid].count++;
      clustersMap[cid].rev90d += parseFloat(score.revenue_90d || 0);
    }

    const pctChurn = totalClientes > 0 ? (totalRiscoChurn / totalClientes) * 100 : 0;
    const pctGrowth = totalClientes > 0 ? (totalPotencialGrowth / totalClientes) * 100 : 0;
    const variacaoFaturamentoPct =
      rev90d > 0 ? ((faturamentoPrevisto90d - rev90d) / rev90d) * 100 : 0;

    // 5. Evolução temporal mensal (agregações)
    const historyRes = await query(`
      SELECT 
        TO_CHAR(mes_referencia, 'YYYY-MM') as mes,
        ROUND(SUM(faturamento), 2) as faturamento,
        SUM(quantidade_pedidos) as pedidos
      FROM fato_cliente_mes
      GROUP BY mes_referencia
      ORDER BY mes_referencia ASC;
    `);

    const evolucaoMensal = historyRes.rows.map((r) => ({
      mes: r.mes,
      faturamento: parseFloat(r.faturamento),
      pedidos: parseInt(r.pedidos, 10),
    }));

    const distribuicaoSegmentos = Object.entries(clustersMap).map(([cid, data]) => ({
      cluster_id: parseInt(cid, 10),
      cluster_nome: data.nome,
      quantidade: data.count,
      faturamento_total_90d: Math.round(data.rev90d * 100) / 100,
      ticket_medio: data.count > 0 ? Math.round((data.rev90d / data.count) * 100) / 100 : 0,
    }));

    const distribuicaoRiscoChurn = Object.entries(churnTiersCount).map(([faixa, count]) => ({
      faixa,
      quantidade: count,
      percentual: totalClientes > 0 ? Math.round((count / totalClientes) * 1000) / 10 : 0,
    }));

    return {
      total_clientes_analisados: totalClientes,
      clientes_ativos: clientesAtivos,
      faturamento_historico_365d: Math.round(rev365d * 100) / 100,
      faturamento_previsto_proximos_90d: Math.round(faturamentoPrevisto90d * 100) / 100,
      faturamento_recente_90d: Math.round(rev90d * 100) / 100,
      variacao_faturamento_pct: Math.round(variacaoFaturamentoPct * 10) / 10,
      total_clientes_em_risco_churn: totalRiscoChurn,
      percentual_em_risco_churn: Math.round(pctChurn * 10) / 10,
      total_clientes_potencial_growth: totalPotencialGrowth,
      percentual_potencial_growth: Math.round(pctGrowth * 10) / 10,
      distribuicao_segmentos: distribuicaoSegmentos,
      distribuicao_risco_churn: distribuicaoRiscoChurn,
      evolucao_mensal: evolucaoMensal,
    };
  }
}

export const dashboardService = new DashboardService();


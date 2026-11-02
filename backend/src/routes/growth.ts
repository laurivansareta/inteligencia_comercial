import { Router, Request, Response } from 'express';
import { mlService } from '../services/mlService.js';

export const growthRouter = Router();

growthRouter.get('/opportunities', async (req: Request, res: Response) => {
  try {
    const limit = req.query.limit ? parseInt(req.query.limit as string, 10) : 50;
    const filialId = req.query.id_filial ? parseInt(req.query.id_filial as string, 10) : undefined;
    const apenasOportunidades = req.query.apenas_expansao === 'true';

    const allScores = await mlService.getAllCustomerScores();

    let filtered = allScores;
    if (filialId) {
      filtered = filtered.filter((s) => s.id_filial === filialId);
    }
    if (apenasOportunidades) {
      filtered = filtered.filter((s) => s.fl_oportunidade_expansao);
    }

    // Ordenar por potencial de crescimento absoluto decrescente
    filtered.sort((a, b) => (b.potencial_absoluto || 0) - (a.potencial_absoluto || 0));

    const opportunities = filtered.slice(0, limit).map((s) => ({
      id_cliente: s.id_cliente,
      nome_fantasia: s.nome_fantasia,
      filial_descricao: s.filial_descricao,
      cluster_nome: s.cluster_nome,
      revenue_90d_historico: s.revenue_90d,
      faturamento_previsto_90d: s.faturamento_previsto_90d,
      potencial_absoluto: s.potencial_absoluto,
      variacao_estimada_pct: s.variacao_estimada_pct,
      fl_oportunidade_expansao: s.fl_oportunidade_expansao,
    }));

    res.json({
      total_analisados: filtered.length,
      opportunities,
    });
  } catch (err: any) {
    console.error('[GrowthRouter] Erro:', err);
    res.status(500).json({ error: 'Erro ao carregar oportunidades de crescimento', details: err.message });
  }
});

growthRouter.post('/predict', async (req: Request, res: Response) => {
  try {
    const { id_cliente } = req.body;
    if (!id_cliente) {
      return res.status(400).json({ error: 'Campo id_cliente é obrigatório' });
    }

    const explanation = await mlService.getCustomerExplanation(id_cliente);
    res.json(explanation.growth || {});
  } catch (err: any) {
    console.error('[GrowthRouter] Erro ao predizer growth:', err);
    res.status(500).json({ error: 'Erro ao gerar previsão de crescimento', details: err.message });
  }
});

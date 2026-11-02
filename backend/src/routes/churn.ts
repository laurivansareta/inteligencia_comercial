import { Router, Request, Response } from 'express';
import { mlService } from '../services/mlService.js';

export const churnRouter = Router();

churnRouter.get('/ranking', async (req: Request, res: Response) => {
  try {
    const limit = req.query.limit ? parseInt(req.query.limit as string, 10) : 50;
    const filialId = req.query.id_filial ? parseInt(req.query.id_filial as string, 10) : undefined;
    const faixaRisco = req.query.faixa_risco as string;

    const allScores = await mlService.getAllCustomerScores();

    let filtered = allScores;
    if (filialId) {
      filtered = filtered.filter((s) => s.id_filial === filialId);
    }
    if (faixaRisco) {
      filtered = filtered.filter((s) => s.faixa_risco === faixaRisco);
    }

    // Ordenar por probabilidade de churn decrescente
    filtered.sort((a, b) => (b.churn_probabilidade || 0) - (a.churn_probabilidade || 0));

    const ranking = filtered.slice(0, limit).map((s) => ({
      id_cliente: s.id_cliente,
      nome_fantasia: s.nome_fantasia,
      filial_descricao: s.filial_descricao,
      cluster_nome: s.cluster_nome,
      churn_probabilidade: s.churn_probabilidade,
      faixa_risco: s.faixa_risco,
      recency_days: s.recency_days,
      frequency_90d: s.frequency_90d,
      revenue_90d: s.revenue_90d,
      late_payment_rate: s.late_payment_rate,
    }));

    res.json({
      total_analisados: filtered.length,
      ranking,
    });
  } catch (err: any) {
    console.error('[ChurnRouter] Erro ao carregar ranking:', err);
    res.status(500).json({ error: 'Erro ao carregar ranking de churn', details: err.message });
  }
});

churnRouter.post('/predict', async (req: Request, res: Response) => {
  try {
    const { id_cliente } = req.body;
    if (!id_cliente) {
      return res.status(400).json({ error: 'Campo id_cliente é obrigatório' });
    }

    const explanation = await mlService.getCustomerExplanation(id_cliente);
    res.json(explanation);
  } catch (err: any) {
    console.error('[ChurnRouter] Erro ao predizer churn:', err);
    res.status(500).json({ error: 'Erro ao gerar previsão de churn', details: err.message });
  }
});


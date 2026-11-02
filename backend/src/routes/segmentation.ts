import { Router, Request, Response } from 'express';
import { mlService } from '../services/mlService.js';

export const segmentationRouter = Router();

segmentationRouter.get('/', async (_req: Request, res: Response) => {
  try {
    const meta = mlService.getModelsMetadata().segmentation;
    const allScores = await mlService.getAllCustomerScores();

    // Calcular estatísticas agregadas por cluster
    const clusterMap: Record<number, any> = {};
    for (const [cidStr, name] of Object.entries(meta.cluster_names || {})) {
      const cid = parseInt(cidStr, 10);
      clusterMap[cid] = {
        cluster_id: cid,
        cluster_nome: name,
        profile: meta.cluster_profiles?.[cid] || {},
        total_clientes: 0,
        faturamento_total_90d: 0,
        clientes_amostra: [],
      };
    }

    for (const s of allScores) {
      const cid = s.cluster_id;
      if (clusterMap[cid]) {
        clusterMap[cid].total_clientes++;
        clusterMap[cid].faturamento_total_90d += parseFloat(s.revenue_90d || 0);
        if (clusterMap[cid].clientes_amostra.length < 5) {
          clusterMap[cid].clientes_amostra.push({
            id_cliente: s.id_cliente,
            nome_fantasia: s.nome_fantasia,
            faturamento_90d: s.revenue_90d,
            recencia: s.recency_days,
            frequencia: s.frequency_90d,
          });
        }
      }
    }

    res.json({
      model_type: meta.model_type,
      total_clusters: meta.best_k,
      silhouette_score: meta.silhouette_score,
      clusters: Object.values(clusterMap),
    });
  } catch (err: any) {
    console.error('[SegmentationRouter] Erro:', err);
    res.status(500).json({ error: 'Erro ao carregar dados de segmentação', details: err.message });
  }
});

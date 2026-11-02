import { Router, Request, Response } from 'express';
import { mlService } from '../services/mlService.js';

export const modelsRouter = Router();

modelsRouter.get('/metrics', async (_req: Request, res: Response) => {
  try {
    const meta = mlService.getModelsMetadata();
    res.json({
      timestamp: new Date().toISOString(),
      models: {
        segmentation: {
          name: 'Customer Segmentation',
          algorithm: meta.segmentation.model_type,
          k_clusters: meta.segmentation.best_k,
          silhouette_score: meta.segmentation.silhouette_score,
          features: meta.segmentation.features,
          clusters: meta.segmentation.cluster_names,
          cluster_distribution: meta.segmentation.cluster_distribution,
        },
        churn: {
          name: 'Churn Prediction (90 dias)',
          algorithm: meta.churn.model_type,
          train_dates: meta.churn.train_dates,
          validation_date: meta.churn.validation_date,
          test_date: meta.churn.test_date,
          test_metrics: meta.churn.final_test_metrics,
          feature_importances: meta.churn.feature_importances,
          comparison: meta.churn.comparison_results,
        },
        growth: {
          name: 'Growth Prediction (90 dias)',
          algorithm: meta.growth.model_type,
          train_dates: meta.growth.train_dates,
          validation_date: meta.growth.validation_date,
          test_date: meta.growth.test_date,
          test_metrics: meta.growth.final_test_metrics,
          feature_importances: meta.growth.feature_importances,
          comparison: meta.growth.comparison_results,
        },
      },
    });
  } catch (err: any) {
    console.error('[ModelsRouter] Erro:', err);
    res.status(500).json({ error: 'Erro ao carregar métricas dos modelos', details: err.message });
  }
});

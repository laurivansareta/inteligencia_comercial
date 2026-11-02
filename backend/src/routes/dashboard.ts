import { Router, Request, Response } from 'express';
import { dashboardService } from '../services/dashboardService.js';

export const dashboardRouter = Router();

dashboardRouter.get('/', async (_req: Request, res: Response) => {
  try {
    const kpis = await dashboardService.getExecutiveKPIs();
    res.json(kpis);
  } catch (err: any) {
    console.error('[DashboardRouter] Erro:', err);
    res.status(500).json({ error: 'Erro ao carregar indicadores executivos', details: err.message });
  }
});


import { Router, Request, Response } from 'express';
import { query } from '../db/index.js';

export const healthRouter = Router();

healthRouter.get('/', async (_req: Request, res: Response) => {
  try {
    const dbRes = await query('SELECT 1;');
    const isDbConnected = dbRes.rowCount === 1;

    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      database: isDbConnected ? 'connected' : 'disconnected',
      version: '1.0.0',
    });
  } catch (err: any) {
    res.status(503).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      database: 'error',
      error: err.message,
    });
  }
});


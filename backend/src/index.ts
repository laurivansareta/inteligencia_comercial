import express from 'express';
import cors from 'cors';
import { config } from './config/env.js';
import { healthRouter } from './routes/health.js';
import { dashboardRouter } from './routes/dashboard.js';
import { customersRouter } from './routes/customers.js';
import { segmentationRouter } from './routes/segmentation.js';
import { churnRouter } from './routes/churn.js';
import { growthRouter } from './routes/growth.js';
import { modelsRouter } from './routes/models.js';
import { pool } from './db/index.js';

const app = express();

app.use(cors({ origin: '*' }));
app.use(express.json());

// Registro de rotas
app.use('/api/health', healthRouter);
app.use('/api/dashboard', dashboardRouter);
app.use('/api/customers', customersRouter);
app.use('/api/segmentation', segmentationRouter);
app.use('/api/churn', churnRouter);
app.use('/api/growth', growthRouter);
app.use('/api/models', modelsRouter);

// Tratamento de rotas não encontradas
app.use((_req, res) => {
  res.status(404).json({ error: 'Endpoint não encontrado' });
});

// Middleware global de erro
app.use((err: any, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  console.error('[App] Erro não capturado:', err);
  res.status(500).json({ error: 'Erro interno no servidor', details: err.message });
});

const server = app.listen(config.port, () => {
  console.log(`[CYCLE AI Backend] Servidor ativo em http://localhost:${config.port}`);
  console.log(`[CYCLE AI Backend] Conectado ao banco: ${config.db.name} em ${config.db.host}:${config.db.port}`);
});

process.on('SIGTERM', () => {
  console.log('Fechando conexões e encerrando servidor...');
  server.close(async () => {
    await pool.end();
    process.exit(0);
  });
});

export default app;


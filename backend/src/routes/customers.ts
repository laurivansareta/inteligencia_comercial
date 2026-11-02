import { Router, Request, Response } from 'express';
import { customerService } from '../services/customerService.js';

export const customersRouter = Router();

customersRouter.get('/', async (req: Request, res: Response) => {
  try {
    const page = req.query.page ? parseInt(req.query.page as string, 10) : 1;
    const limit = req.query.limit ? parseInt(req.query.limit as string, 10) : 20;
    const search = req.query.search as string;
    const id_filial = req.query.id_filial ? parseInt(req.query.id_filial as string, 10) : undefined;
    const cluster_id = req.query.cluster_id !== undefined && req.query.cluster_id !== '' 
      ? parseInt(req.query.cluster_id as string, 10) 
      : undefined;
    const faixa_risco = req.query.faixa_risco as string;
    const sortBy = req.query.sortBy as string;
    const sortOrder = (req.query.sortOrder as 'asc' | 'desc') || 'asc';

    const result = await customerService.listCustomers({
      page,
      limit,
      search,
      id_filial,
      cluster_id,
      faixa_risco,
      sortBy,
      sortOrder,
    });

    res.json(result);
  } catch (err: any) {
    console.error('[CustomersRouter] Erro ao listar:', err);
    res.status(500).json({ error: 'Erro ao listar clientes', details: err.message });
  }
});

customersRouter.get('/:id', async (req: Request, res: Response) => {
  try {
    const id = parseInt(req.params.id, 10);
    if (isNaN(id)) {
      return res.status(400).json({ error: 'ID de cliente inválido' });
    }

    const data = await customerService.getCustomer360(id);
    if (!data) {
      return res.status(404).json({ error: 'Cliente não encontrado' });
    }

    res.json(data);
  } catch (err: any) {
    console.error(`[CustomersRouter] Erro ao obter cliente ${req.params.id}:`, err);
    res.status(500).json({ error: 'Erro ao carregar Customer 360', details: err.message });
  }
});

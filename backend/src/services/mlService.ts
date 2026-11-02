import fs from 'fs';
import path from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';
import { config } from '../config/env.js';

const execFileAsync = promisify(execFile);

export interface MLMetadata {
  segmentation: any;
  churn: any;
  growth: any;
}

class MLService {
  private cacheScores: Map<number, any> = new Map();
  private lastScoredAt: number = 0;
  private readonly CACHE_TTL_MS = 10 * 60 * 1000; // 10 minutos

  public getModelsMetadata(): MLMetadata {
    const modelsDir = path.resolve(config.projectRoot, 'models');
    
    const segMeta = JSON.parse(
      fs.readFileSync(path.join(modelsDir, 'segmentation', 'metadata.json'), 'utf-8')
    );
    const churnMeta = JSON.parse(
      fs.readFileSync(path.join(modelsDir, 'churn', 'metrics.json'), 'utf-8')
    );
    const growthMeta = JSON.parse(
      fs.readFileSync(path.join(modelsDir, 'growth', 'metrics.json'), 'utf-8')
    );

    return {
      segmentation: segMeta,
      churn: churnMeta,
      growth: growthMeta,
    };
  }

  public async getAllCustomerScores(forceRefresh = false): Promise<any[]> {
    const now = Date.now();
    if (!forceRefresh && this.cacheScores.size > 0 && now - this.lastScoredAt < this.CACHE_TTL_MS) {
      return Array.from(this.cacheScores.values());
    }

    const scriptPath = path.resolve(config.projectRoot, 'ml/service_bridge.py');
    try {
      const { stdout } = await execFileAsync(
        config.pythonPath,
        [scriptPath, '--action', 'score_all'],
        { maxBuffer: 50 * 1024 * 1024 }
      );

      const records = JSON.parse(stdout);
      this.cacheScores.clear();
      for (const rec of records) {
        this.cacheScores.set(rec.id_cliente, rec);
      }
      this.lastScoredAt = now;
      return records;
    } catch (err) {
      console.error('[MLService] Erro ao executar score_all:', err);
      return Array.from(this.cacheScores.values());
    }
  }

  public async getCustomerExplanation(customerId: number): Promise<any> {
    const scriptPath = path.resolve(config.projectRoot, 'ml/service_bridge.py');
    try {
      const { stdout } = await execFileAsync(
        config.pythonPath,
        [scriptPath, '--action', 'explain_one', '--customer-id', customerId.toString()],
        { maxBuffer: 10 * 1024 * 1024 }
      );
      return JSON.parse(stdout);
    } catch (err) {
      console.error(`[MLService] Erro ao explicar cliente ${customerId}:`, err);
      throw err;
    }
  }

  public getCachedScore(customerId: number): any | null {
    return this.cacheScores.get(customerId) || null;
  }
}

export const mlService = new MLService();


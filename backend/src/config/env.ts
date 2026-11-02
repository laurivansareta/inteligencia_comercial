import dotenv from 'dotenv';
import path from 'path';

// Carrega .env da raiz do projeto ou do diretório local
dotenv.config({ path: path.resolve(__dirname, '../../../.env') });
dotenv.config();

export const config = {
  port: parseInt(process.env.PORT || '3001', 10),
  db: {
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT || '5432', 10),
    name: process.env.DB_NAME || 'cycle_ai',
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASSWORD || 'postgres',
  },
  projectRoot: path.resolve(__dirname, '../../../'),
  pythonPath: path.resolve(__dirname, '../../../.venv/Scripts/python.exe'),
};


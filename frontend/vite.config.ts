import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Carrega as variáveis do arquivo .env na raiz do projeto
  const env = loadEnv(mode, path.resolve(__dirname, '..'), '');
  const frontendPort = parseInt(env.FRONTEND_PORT || '3002', 10);
  const backendPort = parseInt(env.PORT || '3001', 10);

  return {
    plugins: [
      react(),
      tailwindcss(),
    ],
    server: {
      port: frontendPort,
      proxy: {
        '/api': {
          target: `http://localhost:${backendPort}`,
          changeOrigin: true,
        }
      }
    }
  };
});

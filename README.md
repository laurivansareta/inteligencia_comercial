# CYCLE AI — Inteligência Comercial (Full Stack)

Plataforma B2B SaaS de Customer Intelligence para distribuidoras e atacadistas, transformando dados comerciais e financeiros em decisões orientadas por dados e preditivas.

---

## 1. Status do Projeto

- [x] **Fase 1 — Data Foundation**: 100% Concluída e Validada (PostgreSQL 16, geradores de 36 meses e conector ERP).
- [x] **Fase 2 — Machine Learning**: 100% Concluída e Validada (K-Means, Churn com SHAP e Growth XGBoost).
- [x] **Fase 3 — Backend e API REST**: 100% Concluída em **TypeScript** (Express, endpoints REST documentados).
- [x] **Fase 4 — Frontend e Interface**: 100% Concluída em **React + TypeScript** (Vite, Tailwind, Recharts, 6 módulos completos).

---

## 2. Arquitetura da Solução

```text
cycle-ai/
├── backend/                    # API REST em TypeScript (Node.js + Express)
│   ├── src/
│   │   ├── config/env.ts       # Configurações de ambiente
│   │   ├── db/index.ts         # Pool de conexões PostgreSQL (pg)
│   │   ├── routes/             # Rotas REST (/health, /dashboard, /customers, /churn, /growth, /models)
│   │   ├── services/           # Regras de negócio e integração aos modelos ML
│   │   ├── types/index.ts      # Tipagens completas TypeScript
│   │   └── index.ts            # Entrypoint do servidor HTTP (Porta 3001)
│   ├── package.json
│   └── tsconfig.json
├── frontend/                   # Interface Web em React + TypeScript + Vite
│   ├── src/
│   │   ├── components/         # Sidebar, Header, MetricCard
│   │   ├── pages/
│   │   │   ├── DashboardView.tsx    # Visão Executiva & Saúde da Carteira
│   │   │   ├── SegmentationView.tsx # Segmentação K-Means
│   │   │   ├── ChurnView.tsx        # Ranking de Risco & Explicabilidade SHAP
│   │   │   ├── GrowthView.tsx       # Oportunidades de Expansão (XGBoost)
│   │   │   ├── CustomersView.tsx    # Customer 360 & Transações
│   │   │   └── ModelsView.tsx       # Governança e Métricas dos Modelos
│   │   ├── services/api.ts     # Cliente HTTP da API REST
│   │   ├── types/index.ts      # Tipagens do frontend
│   │   ├── App.tsx             # Navegação principal e estado global
│   │   └── index.css           # Estilos globais e Tailwind v4
│   ├── package.json
│   └── vite.config.ts          # Proxy reverso /api -> http://localhost:3001
├── data/
│   ├── generators/             # Geradores de clientes, SKUs, vendas 36m e pagamentos
│   └── connectors/             # Conector de extração do ERP Flex Smart
├── database/
│   ├── schema.sql              # DDL oficial do PostgreSQL 16
│   └── connection.py           # Conexão Python (SQLAlchemy/psycopg2)
├── ml/
│   ├── segmentation/           # K-Means, seleção ótima de K e rotulação
│   ├── churn/                  # LogisticRegression + SHAP TreeExplainer
│   ├── growth/                 # XGBoost Regressor de Faturamento Futuro
│   ├── evaluation/             # Métricas (F1, PR-AUC, ROC-AUC, WAPE, MAE, Silhouette)
│   └── service_bridge.py       # Ponte de inferência em alta velocidade para o backend
├── models/                     # Modelos treinados e serializados (.joblib e .json)
├── scripts/
│   ├── generate_data.py        # Gerador sintético com seed fixa
│   ├── train_all.py            # Pipeline de treinamento dos 3 modelos
│   └── validate_data.py        # Validador de consistência e reconciliação
├── tests/                      # 15 testes automatizados (pytest)
├── EXECUTAR_SISTEMA.bat        # Inicializador 1-clique (Windows)
├── package.json                # Scripts orquestrados de build e execução
├── requirements.txt            # Dependências Python
└── context.md                  # Especificação oficial do produto
```

---

## 3. Guia Rápido de Execução

### 3.1 Inicialização Rápida com 1-Clique (Windows)
Execute o arquivo:
```cmd
EXECUTAR_SISTEMA.bat
```
Ou no PowerShell:
```powershell
.\executar_sistema.ps1
```
O sistema abrirá automaticamente o navegador em `http://localhost:3000`.

---

### 3.2 Execução Manual dos Componentes

#### Backend TypeScript (Porta 3001):
```powershell
cd backend
npm install
npm run dev
```

#### Frontend React + TypeScript (Porta 3000):
```powershell
cd frontend
npm install
npm run dev
```

---

## 4. Endpoints da API REST (Seção 10 do context.md)

| Método | Endpoint | Objetivo |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Status de saúde da API e conexão ao PostgreSQL |
| `GET` | `/api/dashboard` | KPIs consolidados da Visão Executiva e evolução mensal |
| `GET` | `/api/customers` | Listagem paginada com busca, filtros de filial, segmento e risco |
| `GET` | `/api/customers/:id` | **Customer 360** completo (cadastro, histórico e predições) |
| `GET` | `/api/segmentation` | Perfis médios e distribuição dos clusters K-Means |
| `GET` | `/api/churn/ranking` | Ranking de risco de abandono com probabilidades estimadas |
| `POST` | `/api/churn/predict` | Previsão e explicabilidade individual **SHAP** para o cliente |
| `GET` | `/api/growth/opportunities` | Ranking de potencial de crescimento incremental |
| `POST` | `/api/growth/predict` | Previsão de faturamento futuro nos 90 dias seguintes |
| `GET` | `/api/models/metrics` | Métricas de validação e teste de todos os modelos |

---

## 5. Modelos de Machine Learning e Desempenho

1. **Customer Segmentation (K-Means):**
   - **K selecionado:** 3 clusters (*Silhouette Score: 0.5533*).
   - **Perfis:** *Campeões* (R$ 32k/90d), *Em Alerta* (R$ 1.6k/90d), *Inativos* (0 vendas/90d).
2. **Churn Prediction (Logistic Regression Campeão):**
   - **ROC-AUC (Teste Out-of-Time):** `0.9261`.
   - **F1-Score:** `0.6203` | **Recall:** `92.80%` (alta sensibilidade comercial).
   - **Explicabilidade:** Explainer **SHAP** calibrado indicando fatores que elevam e reduzem o risco.
3. **Growth Prediction (XGBoost Regressor Campeão):**
   - **R² Score (Teste Out-of-Time):** `0.8831`.
   - **WAPE:** `32.71%` | **MAE:** `R$ 7.555,64`.
   - **Potencial de Expansão:** Calculado a partir da variação positiva versus histórico recente.

---

## 6. Testes Automatizados

Para rodar toda a suíte de testes do banco e modelos:
```powershell
.\.venv\Scripts\pytest -v
```
Para testar a compilação do backend e frontend:
```powershell
npm run build
```

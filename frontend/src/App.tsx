import React, { useState } from 'react';
import { Sidebar, TabType } from './components/Sidebar';
import { Header } from './components/Header';
import { DashboardView } from './pages/DashboardView';
import { SegmentationView } from './pages/SegmentationView';
import { ChurnView } from './pages/ChurnView';
import { GrowthView } from './pages/GrowthView';
import { CustomersView } from './pages/CustomersView';
import { ModelsView } from './pages/ModelsView';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');
  const [focusedCustomerId, setFocusedCustomerId] = useState<number | null>(null);

  function handleSelectCustomer(customerId: number) {
    setFocusedCustomerId(customerId);
    setActiveTab('customers');
  }

  const tabConfig: Record<TabType, { title: string; subtitle: string }> = {
    dashboard: {
      title: 'Visão Executiva & Saúde da Carteira',
      subtitle: 'Indicadores consolidados, evolução temporal e balanço de risco vs oportunidade',
    },
    segmentation: {
      title: 'Segmentação Comportamental de Clientes',
      subtitle: 'Clusterização K-Means (K=3) para compreensão dos perfis de consumo',
    },
    churn: {
      title: 'Predição & Risco de Churn (90 dias)',
      subtitle: 'Ranking de risco com explicabilidade individual de fatores via SHAP',
    },
    growth: {
      title: 'Potencial de Crescimento & Expansão',
      subtitle: 'Estimativa de faturamento futuro por XGBoost e oportunidades incrementais',
    },
    customers: {
      title: 'Customer 360 & Ficha do Cliente',
      subtitle: 'Visão unificada cadastral, transacional e preditiva por cliente',
    },
    models: {
      title: 'Governança & Métricas dos Modelos',
      subtitle: 'Métricas de avaliação no conjunto de teste, versões e transparência de dados',
    },
  };

  return (
    <div className="flex h-screen bg-cycle-darkest overflow-hidden">
      {/* Sidebar de Navegação */}
      <Sidebar
        activeTab={activeTab}
        onSelectTab={(tab) => {
          setActiveTab(tab);
          if (tab !== 'customers') {
            setFocusedCustomerId(null);
          }
        }}
      />

      {/* Conteúdo Principal */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header
          title={tabConfig[activeTab].title}
          subtitle={tabConfig[activeTab].subtitle}
        />

        <main className="flex-1 overflow-y-auto p-8">
          {activeTab === 'dashboard' && <DashboardView />}
          {activeTab === 'segmentation' && (
            <SegmentationView onSelectCustomer={handleSelectCustomer} />
          )}
          {activeTab === 'churn' && (
            <ChurnView onSelectCustomer={handleSelectCustomer} />
          )}
          {activeTab === 'growth' && (
            <GrowthView onSelectCustomer={handleSelectCustomer} />
          )}
          {activeTab === 'customers' && (
            <CustomersView
              initialCustomerId={focusedCustomerId}
              onClearCustomerSelection={() => setFocusedCustomerId(null)}
            />
          )}
          {activeTab === 'models' && <ModelsView />}
        </main>
      </div>
    </div>
  );
};

export default App;

import React from 'react';
import DashboardCard from './DashboardCard';

export default function DashboardMock() {
  return (
    <div className="dashboard-mock grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 p-8 bg-gray-50 dark:bg-gray-950 min-h-screen">
      <DashboardCard type="critical" value={5} desc="Requerem ação imediata" />
      <DashboardCard type="high" value={12} desc="Prioridade alta" />
      <DashboardCard type="medium" value={23} desc="Atenção recomendada" />
      <DashboardCard type="low" value={42} desc="Informativo" />
    </div>
  );
}

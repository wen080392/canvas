import React from 'react';
import { FaExclamationTriangle, FaBolt, FaInfoCircle } from 'react-icons/fa';

const icons = {
  critical: <FaExclamationTriangle className="text-red-600" />,
  high: <FaExclamationTriangle className="text-yellow-500" />,
  medium: <FaBolt className="text-blue-500" />,
  low: <FaInfoCircle className="text-gray-400" />,
};

export default function DashboardCard({ type, value, desc }) {
  return (
    <div
      className={`dashboard-card ${type} bg-white dark:bg-gray-900 shadow-xl rounded-xl p-6 flex items-center space-x-4 hover:scale-105 transition-transform duration-200 border-t-4 ${
        type === 'critical'
          ? 'border-red-600'
          : type === 'high'
          ? 'border-yellow-500'
          : type === 'medium'
          ? 'border-blue-500'
          : 'border-gray-400'
      }`}
    >
      <div className="card-icon text-3xl">{icons[type]}</div>
      <div className="card-content">
        <div className="card-label font-bold text-lg capitalize">{type} Issues</div>
        <div className="card-value text-2xl font-extrabold">{value}</div>
        <div className="card-desc text-sm text-gray-500 dark:text-gray-300">{desc}</div>
      </div>
    </div>
  );
}

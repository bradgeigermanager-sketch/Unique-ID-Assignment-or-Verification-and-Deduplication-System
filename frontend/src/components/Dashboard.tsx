import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

interface SystemMetrics {
  organization_nodes: number;
  reporting_relationships: number;
  active_cycles: number;
  operations_24h: number;
  timestamp: string;
}

interface PerformanceMetrics {
  avg_latency_ms: number;
  max_latency_ms: number;
  query_count_1h: number;
  timestamp: string;
}

interface Alert {
  id: string;
  type: string;
  severity: string;
  message: string;
  timestamp: string;
}

interface AuditLogEntry {
  id: string;
  action: string;
  entity_type: string;
  entity_id: string;
  user: string;
  timestamp: string;
  details: any;
}

export function Dashboard() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [perfMetrics, setPerfMetrics] = useState<PerformanceMetrics | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 30000); // 30 秒刷新
    return () => clearInterval(interval);
  }, []);

  const fetchAllData = async () => {
    try {
      const [sysRes, perfRes, alertsRes, auditRes] = await Promise.all([
        axios.get(`${API_BASE}/monitor/metrics/system`),
        axios.get(`${API_BASE}/monitor/metrics/performance`),
        axios.get(`${API_BASE}/monitor/alerts`),
        axios.get(`${API_BASE}/monitor/audit?limit=20`)
      ]);
      
      setMetrics(sysRes.data);
      setPerfMetrics(perfRes.data);
      setAlerts(alertsRes.data);
      setAuditLogs(auditRes.data.logs);
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch metrics:', err);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 系统指标卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard 
          title="组织节点数" 
          value={metrics?.organization_nodes || 0} 
          icon="👥"
          color="blue"
        />
        <MetricCard 
          title="汇报关系数" 
          value={metrics?.reporting_relationships || 0} 
          icon="🔗"
          color="green"
        />
        <MetricCard 
          title="活跃环数量" 
          value={metrics?.active_cycles || 0} 
          icon="⚠️"
          color={metrics?.active_cycles > 0 ? "red" : "green"}
        />
        <MetricCard 
          title="24 小时操作数" 
          value={metrics?.operations_24h || 0} 
          icon="📊"
          color="purple"
        />
      </div>

      {/* 性能指标 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-bold mb-4">性能指标</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 rounded p-4">
            <p className="text-sm text-blue-600">平均查询延迟</p>
            <p className="text-2xl font-bold">{perfMetrics?.avg_latency_ms.toFixed(2)} ms</p>
          </div>
          <div className="bg-yellow-50 rounded p-4">
            <p className="text-sm text-yellow-600">最大查询延迟</p>
            <p className="text-2xl font-bold">{perfMetrics?.max_latency_ms.toFixed(2)} ms</p>
          </div>
          <div className="bg-green-50 rounded p-4">
            <p className="text-sm text-green-600">1 小时查询数</p>
            <p className="text-2xl font-bold">{perfMetrics?.query_count_1h || 0}</p>
          </div>
        </div>
      </div>

      {/* 告警列表 */}
      {alerts.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-bold mb-4">告警列表</h3>
          <div className="space-y-3">
            {alerts.map((alert) => (
              <AlertCard key={alert.id} alert={alert} />
            ))}
          </div>
        </div>
      )}

      {/* 审计日志 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-bold mb-4">最近审计日志</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">时间</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">实体类型</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">实体 ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">用户</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {auditLogs.map((log) => (
                <tr key={log.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{log.action}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{log.entity_type}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-mono">{log.entity_id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{log.user}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, icon, color }: any) {
  const colorClasses = {
    blue: "bg-blue-50 border-blue-200",
    green: "bg-green-50 border-green-200",
    red: "bg-red-50 border-red-200",
    purple: "bg-purple-50 border-purple-200",
  };

  return (
    <div className={`border rounded-lg p-6 ${colorClasses[color as keyof typeof colorClasses]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>
        </div>
        <span className="text-4xl">{icon}</span>
      </div>
    </div>
  );
}

function AlertCard({ alert }: { alert: Alert }) {
  const severityColors = {
    low: "bg-blue-50 text-blue-700 border-blue-200",
    medium: "bg-yellow-50 text-yellow-700 border-yellow-200",
    high: "bg-orange-50 text-orange-700 border-orange-200",
    critical: "bg-red-50 text-red-700 border-red-200",
  };

  return (
    <div className={`border rounded-lg p-4 ${severityColors[alert.severity as keyof typeof severityColors]}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="font-bold">{alert.type}</p>
          <p className="text-sm mt-1">{alert.message}</p>
        </div>
        <span className="text-xs">{new Date(alert.timestamp).toLocaleString()}</span>
      </div>
    </div>
  );
}

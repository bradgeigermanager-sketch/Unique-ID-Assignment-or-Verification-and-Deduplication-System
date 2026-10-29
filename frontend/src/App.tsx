tsximport React, { useState } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

function App() {
  const [activeTab, setActiveTab] = useState<'org' | 'id' | 'file'>('org');
  const [cycles, setCycles] = useState<any[]>([]);
  const [hasCycle, setHasCycle] = useState(false);

  const fetchCycles = async () => {
    try {
      const res = await axios.get(`${API_BASE}/org/cycles`);
      setCycles(res.data.cycles);
      setHasCycle(res.data.has_cycle);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-blue-600 text-white p-4">
        <h1 className="text-2xl font-bold">组织治理与文件管理系统</h1>
      </header>

      <nav className="bg-white shadow p-4">
        <div className="flex space-x-4">
          <button
            onClick={() => setActiveTab('org')}
            className={`px-4 py-2 rounded ${activeTab === 'org' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          >
            组织治理
          </button>
          <button
            onClick={() => setActiveTab('id')}
            className={`px-4 py-2 rounded ${activeTab === 'id' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          >
            ID 管理
          </button>
          <button
            onClick={() => setActiveTab('file')}
            className={`px-4 py-2 rounded ${activeTab === 'file' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          >
            文件治理
          </button>
        </div>
      </nav>

      <main className="p-6">
        {activeTab === 'org' && (
          <OrgGovernancePanel onFetchCycles={fetchCycles} cycles={cycles} hasCycle={hasCycle} />
        )}
        {activeTab === 'id' && <IDManagementPanel />}
        {activeTab === 'file' && <FileGovernancePanel />}
      </main>
    </div>
  );
}

function OrgGovernancePanel({ onFetchCycles, cycles, hasCycle }: any) {
  const handleFix = async (cycle: string[]) => {
    try {
      await axios.post(`${API_BASE}/org/fix-cycle`, { cycle, strategy: 'lowest_importance' });
      alert('环已修复');
      onFetchCycles();
    } catch (err) {
      alert('修复失败');
    }
  };

  return (
    <div className="bg-white rounded shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">组织层级环检测</h2>
        <button onClick={onFetchCycles} className="bg-blue-600 text-white px-4 py-2 rounded">
          检测环
        </button>
      </div>

      {hasCycle ? (
        <div className="bg-red-100 border border-red-400 rounded p-4 mb-4">
          <p className="text-red-700 font-bold">⚠️ 发现循环汇报关系</p>
          {cycles.map((cycle, idx) => (
            <div key={idx} className="mt-2 p-2 bg-white rounded">
              <p className="font-mono text-sm">{cycle.join(' → ')}</p>
              <button
                onClick={() => handleFix(cycle)}
                className="mt-2 bg-red-600 text-white px-3 py-1 rounded text-sm"
              >
                修复此环
              </button>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-green-100 border border-green-400 rounded p-4">
          <p className="text-green-700">✅ 组织层级无循环，DAG 有效</p>
        </div>
      )}
    </div>
  );
}

function IDManagementPanel() {
  const [entityType, setEntityType] = useState('employee');
  const [generatedId, setGeneratedId] = useState('');
  const [isUnique, setIsUnique] = useState<boolean | null>(null);

  const generateUUID = async () => {
    const id = `EMP-${crypto.randomUUID()}`;
    setGeneratedId(id);
  };

  const checkUniqueness = async () => {
    if (!generatedId) return;
    try {
      const res = await axios.get(`${API_BASE}/id/check?entity_type=${entityType}&id_value=${generatedId}`);
      setIsUnique(res.data.is_unique);
    } catch (err) {
      setIsUnique(null);
    }
  };

  return (
    <div className="bg-white rounded shadow p-6">
      <h2 className="text-xl font-bold mb-4">ID 生成与检查</h2>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">实体类型</label>
          <select
            value={entityType}
            onChange={(e) => setEntityType(e.target.value)}
            className="w-full border rounded p-2"
          >
            <option value="employee">员工</option>
            <option value="department">部门</option>
            <option value="organization">组织</option>
          </select>
        </div>

        <div className="flex space-x-2">
          <button
            onClick={generateUUID}
            className="bg-blue-600 text-white px-4 py-2 rounded"
          >
            生成 UUID
          </button>
          <button
            onClick={checkUniqueness}
            disabled={!generatedId}
            className="bg-green-600 text-white px-4 py-2 rounded disabled:opacity-50"
          >
            检查唯一性
          </button>
        </div>

        {generatedId && (
          <div className="mt-4 p-4 bg-gray-100 rounded">
            <p className="text-sm text-gray-600">生成的 ID:</p>
            <p className="font-mono text-lg">{generatedId}</p>
            {isUnique !== null && (
              <p className={`mt-2 ${isUnique ? 'text-green-600' : 'text-red-600'}`}>
                {isUnique ? '✅ 唯一' : '❌ 已存在'}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function FileGovernancePanel() {
  const [entityId, setEntityId] = useState('EMP-001');
  const [duplicates, setDuplicates] = useState<any[]>([]);

  const findDuplicates = async () => {
    try {
      const res = await axios.get(`${API_BASE}/file/duplicates?entity_id=${entityId}`);
      setDuplicates(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="bg-white rounded shadow p-6">
      <h2 className="text-xl font-bold mb-4">文件重复检测</h2>
      
      <div className="flex space-x-2 mb-4">
        <input
          type="text"
          value={entityId}
          onChange={(e) => setEntityId(e.target.value)}
          className="border rounded p-2 flex-1"
          placeholder="实体 ID"
        />
        <button
          onClick={findDuplicates}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          查找重复
        </button>
      </div>

      {duplicates.length > 0 && (
        <div className="space-y-4">
          {duplicates.map((dup, idx) => (
            <div key={idx} className="border rounded p-4">
              <p className="font-mono text-sm text-gray-600">Hash: {dup.hash}</p>
              <p className="text-sm text-gray-500 mb-2">重复文件数: {dup.count}</p>
              <ul className="list-disc list-inside text-sm">
                {dup.files.map((f: any, i: number) => (
                  <li key={i}>{f.name} ({f.size} bytes)</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;

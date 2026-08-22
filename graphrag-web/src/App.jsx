import { useState } from 'react';
import axios from 'axios';
import ResultCard from './ResultCard.jsx';

const METHODS = [
  { value: 'local', label: 'Local（局部检索）' },
  { value: 'global', label: 'Global（全局综合）' },
  { value: 'drift', label: 'Drift（探索式）' },
  { value: 'basic', label: 'Basic（基础 RAG）' },
];

export default function App() {
  const [question, setQuestion] = useState('');
  const [method, setMethod] = useState('local');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      // 调用后端封装接口：POST /api/query  { question, method }
      // 后端应负责调用 graphrag query --method <method> "<question>"
      const res = await axios.post('/api/query', {
        question: question.trim(),
        method,
      });
      setResult(res.data);
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail ||
          err.message ||
          '请求失败，请确认后端服务已启动'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>GraphRAG 知识图谱问答</h1>
        <p>基于知识图谱的检索增强生成 · 支持 Local / Global / Drift / Basic 四种查询方式</p>
      </header>

      <form className="query-form" onSubmit={handleSubmit}>
        <select
          className="method-select"
          value={method}
          onChange={(e) => setMethod(e.target.value)}
        >
          {METHODS.map((m) => (
            <option key={m.value} value={m.value}>
              {m.label}
            </option>
          ))}
        </select>
        <input
          className="query-input"
          placeholder="输入你的问题，例如：GraphRAG 用了什么社区发现算法？"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button className="query-button" disabled={loading}>
          {loading ? '查询中...' : '提问'}
        </button>
      </form>

      {error && (
        <ResultCard title="错误" error>
          {error}
        </ResultCard>
      )}

      {!result && !error && !loading && (
        <div className="result-card empty">
          在上方输入问题开始查询
        </div>
      )}

      {loading && (
        <div className="result-card empty">正在向知识图谱查询，请稍候...</div>
      )}

      {result && <ResultCard title="回答" data={result} />}
    </div>
  );
}

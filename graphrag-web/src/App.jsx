import { useState } from "react";
import axios from "axios";
import ResultCard from "./ResultCard";

export default function App() {
  const [mode, setMode] = useState("direct"); // 'direct' | 'agent'
  const [method, setMethod] = useState("local");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    if (!question.trim()) {
      setError("请输入问题");
      return;
    }
    setError("");
    setLoading(true);
    setAnswer("");

    try {
      let res;
      if (mode === "direct") {
        // 直接查询模式 → 调原来的 /api/query
        res = await axios.post("/api/query", {
          method: method,
          query: question,
        });
      } else {
        // Agent 智能模式 → 调新增的 /api/agent
        res = await axios.post("/api/agent", {
          question: question,
        });
      }
      setAnswer(res.data.answer || "（无返回内容）");
    } catch (err) {
      const msg =
        err.response?.data?.answer || err.message || "请求失败";
      setError(`错误：${msg}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>GraphRAG 知识图谱问答</h1>
      <p className="subtitle">
        支持 Direct（直接查询）与 Agent（智能体自主决策）两种模式
      </p>

      {/* 模式切换 */}
      <div className="mode-switch">
        <label className="mode-label">查询模式：</label>
        <label className="radio">
          <input
            type="radio"
            name="mode"
            value="direct"
            checked={mode === "direct"}
            onChange={() => setMode("direct")}
          />
          直接查询
        </label>
        <label className="radio">
          <input
            type="radio"
            name="mode"
            value="agent"
            checked={mode === "agent"}
            onChange={() => setMode("agent")}
          />
          Agent 智能模式
        </label>
      </div>

      {/* 直接查询时显示 method 选择 */}
      {mode === "direct" && (
        <div className="field">
          <label>查询方式：</label>
          <select value={method} onChange={(e) => setMethod(e.target.value)}>
            <option value="local">Local（局部检索）</option>
            <option value="global">Global（全局综合）</option>
            <option value="drift">Drift（探索式）</option>
            <option value="basic">Basic（基础）</option>
          </select>
        </div>
      )}

      {/* Agent 模式提示 */}
      {mode === "agent" && (
        <div
          style={{
            padding: "8px 12px",
            background: "#f0f7ff",
            border: "1px solid #b3d8ff",
            borderRadius: "6px",
            marginBottom: "12px",
            fontSize: "14px",
            color: "#0066cc",
          }}
        >
          🤖 Agent 模式：由 LangChain Agent 自主判断调用 GraphRAG / 计算器等工具
        </div>
      )}

      {/* 问题输入 */}
      <div className="field">
        <label>问题：</label>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="请输入你的问题，如：GraphRAG 是谁提出的？"
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
          style={{ width: "100%", padding: "8px", marginTop: "4px" }}
        />
      </div>

      {/* 提交按钮 */}
      <button className="btn" onClick={handleSubmit} disabled={loading}>
        {loading ? "请求中..." : "提问"}
      </button>

      {/* 错误提示 */}
      {error && (
        <div
          style={{
            color: "#d93025",
            marginTop: "12px",
            padding: "8px",
            background: "#fce8e6",
            borderRadius: "6px",
          }}
        >
          {error}
        </div>
      )}

      {/* 回答展示 */}
      {answer && <ResultCard title="回答" content={answer} />}
    </div>
  );
}
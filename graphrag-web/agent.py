import os
from pydantic import SecretStr
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool
import requests


# ==================== 内部调用函数（避免重复代码） ====================
def _call_graphrag(query: str, method: str) -> str:
    """实际发请求给 GraphRAG 后端"""
    try:
        resp = requests.post(
            "http://127.0.0.1:8000/api/query",
            json={"query": query, "method": method},
            timeout=180,
        )
        resp.raise_for_status()
        return resp.json().get("answer", "GraphRAG 未返回结果")
    except requests.exceptions.Timeout:
        return "⏱️ GraphRAG 查询超时，请稍后重试或改用 local 模式。"
    except Exception as e:
        return f"❌ 调用 GraphRAG 失败: {e}"


# ==================== 工具 1：Local 检索 ====================
@tool
def graphrag_local_search(query: str) -> str:
    """
    局部检索，适合查询具体事实、实体关系、技术细节。
    例如：'GraphRAG 是谁提出的'、'LightRAG 和 GraphRAG 的区别'、'BGE-M3 是什么模型'
    """
    return _call_graphrag(query, "local")


# ==================== 工具 2：Global 检索 ====================
@tool
def graphrag_global_search(query: str) -> str:
    """
    全局综合检索，适合宏观总结、主题归纳、跨文档综合分析。
    例如：'总结文档的核心议题'、'主要技术挑战有哪些'、'整体架构是怎样的'
    """
    return _call_graphrag(query, "global")


# ==================== 工具 3：计算器 ====================
@tool
def calculator(expression: str) -> str:
    """计算数学表达式，如 '23 * 47 + 100'。"""
    allowed = set("0123456789+-*/()%. ")
    if not all(c in allowed for c in expression):
        return "❌ 表达式包含非法字符"
    try:
        return str(eval(expression, {"__builtins__": {}}))
    except Exception as e:
        return f"计算错误: {e}"


# ==================== 构建 Agent ====================
def build_agent():
    # 安全校验：确保 API Key 存在
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("❌ 未找到 OPENAI_API_KEY，请检查 .env 文件")

    model = ChatOpenAI(
        model="deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
        api_key=SecretStr(api_key),                     # ← 修复 SecretStr 报错
        base_url=os.getenv("OPENAI_BASE_URL"),
        temperature=0.1,
    )

    return create_agent(
        model=model,
        tools=[graphrag_local_search, graphrag_global_search, calculator],  # ← 3 个工具
        system_prompt="""你是智能助手，拥有以下工具：

1) graphrag_local_search：查询知识图谱获取具体事实、实体、技术细节。
   → 当用户问具体的人名、概念、区别、步骤时用。
2) graphrag_global_search：查询知识图谱进行宏观总结、主题归纳。
   → 当用户要求"总结"、"概括"、"分析整体"时用。这是总结类问题的唯一正确选择。
3) calculator：计算数学表达式。
   → 需要算数时调用。

策略：
- 总结/概括类问题 → 必须且只能用 graphrag_global_search
- 具体事实/实体/技术细节 → 用 graphrag_local_search
- 需要计算 → 用 calculator
- 闲聊/常识 → 直接回答，不调工具
- 工具返回为空或失败 → 如实告知用户，不要编造""",
    )


# ==================== 供 FastAPI 后端调用 ====================
def run_agent(question: str) -> str:
    """供 backend.py 的 /api/agent 接口调用"""
    agent = build_agent()
    result = agent.invoke({
        "messages": [{"role": "user", "content": question}]
    })
    return result["messages"][-1].content
import os
import subprocess
import asyncio
from dotenv import load_dotenv
from pydantic import SecretStr
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# ==================== 加载环境 ====================
load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 配置 ====================
GRAPHRAG_ROOT = r"C:\Users\15922\Desktop\llm\graphrag\graphrag_src"
PYTHON_EXE = r"C:\Users\15922\Desktop\llm\graphrag\graphrag_src\.venv\Scripts\python.exe"

API_KEY = str(os.getenv("OPENAI_API_KEY", ""))
BASE_URL = str(os.getenv("OPENAI_BASE_URL", ""))
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"

# ==================== GraphRAG CLI 调用 ====================
def _run_graphrag(query: str, method: str) -> str:
    cmd = [
        PYTHON_EXE, "-m", "graphrag", "query",
        "--root", GRAPHRAG_ROOT,
        "--method", method,
        str(query)
    ]
    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        result = subprocess.run(
            cmd, capture_output=True,
            cwd=GRAPHRAG_ROOT, env=env, timeout=240
        )
        output = result.stdout.decode("utf-8", errors="replace").strip()
        if result.returncode != 0:
            err = result.stderr.decode("utf-8", errors="replace")[:500]
            return f"查询失败：{err}"
        return output or "未找到相关内容。"
    except subprocess.TimeoutExpired:
        return "查询超时（240秒）。"
    except Exception as e:
        return f"调用异常：{str(e)}"

# ==================== 路由 1：Direct 直接查询 ====================
@app.post("/api/query")
async def handle_query(request: Request):
    body = await request.json()
    method = str(body.get("method", "local"))
    query = str(body.get("query") or body.get("question") or "").strip()
    if not query:
        return {"answer": "❌ 问题不能为空"}
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _run_graphrag, query, method)
    return {"answer": result}

# ==================== LangChain 初始化 ====================
def _build_llm() -> ChatOpenAI:
    if not API_KEY or not BASE_URL:
        raise ValueError("请在 .env 中配置 OPENAI_API_KEY 和 OPENAI_BASE_URL")
    return ChatOpenAI(
        model=MODEL_NAME,
        api_key=SecretStr(API_KEY),
        base_url=BASE_URL,
        temperature=0.3,
    )

# ==================== Agent 逻辑 ====================
def _decide_method(llm: ChatOpenAI, question: str) -> str:
    """第一步：判断用 local 还是 global"""
    prompt = (
        "根据用户问题选择检索模式，只输出一个单词。\n"
        "具体事实、人名、概念、技术细节 → local\n"
        "总结、概括、宏观分析、主题归纳 → global\n"
        "输出：local 或 global"
    )
    response = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=str(question))
    ])
    content = str(response.content).strip().lower()
    return "global" if "global" in content else "local"

def _summarize_local(llm: ChatOpenAI, question: str, context: str) -> str:
    """local 模式：从检索结果中提取完整答案"""
    prompt = (
        "你是一个专业的中文知识库问答助手。根据下面的检索结果，详细回答用户的问题。\n\n"
        "要求：\n"
        "1. 完整回答，不要遗漏检索结果中的关键信息\n"
        "2. 如果有多个相关事实或数据点，逐一详细列出\n"
        "3. 严格依据检索结果，保留重要数据和专业术语\n"
        "4. 用清晰的中文段落回答，可以适当分点，每个点要有完整解释\n"
        "5. 如果检索结果不足以回答，如实说明\n\n"
        f"检索结果：\n{str(context)}"
    )
    response = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=f"用户问题：{str(question)}")
    ])
    return str(response.content).strip()

def _run_agent(question: str) -> str:
    """Agent 主流程：判断 → 检索 → 返回"""
    llm = _build_llm()

    # 第一步：判断
    method = _decide_method(llm, question)

    # 第二步：检索
    context = _run_graphrag(question, method)

    # 检索失败直接返回
    if any(x in context for x in ["查询失败", "调用异常", "查询超时"]):
        return context

    # 第三步：处理
    if method == "global":
        # global 模式：GraphRAG 已生成完整总结，直接返回
        return context
    else:
        # local 模式：LLM 提取完整答案
        return _summarize_local(llm, question, context)

# ==================== 路由 2：Agent 智能模式 ====================
@app.post("/api/agent")
async def handle_agent(request: Request):
    body = await request.json()
    question = str(body.get("question") or body.get("query") or "").strip()
    if not question:
        return {"answer": "❌ 问题不能为空"}
    try:
        answer = await asyncio.to_thread(_run_agent, question)
        return {"answer": answer}
    except Exception as e:
        return {"answer": f"❌ Agent 异常：{str(e)}"}

# ==================== 路由 3：健康检查 ====================
@app.get("/api/health")
async def health():
    return {"status": "ok"}

# ==================== 启动 ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
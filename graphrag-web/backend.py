import subprocess
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ========== 跨域配置 ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 配置区 ==========
GRAPHRAG_ROOT = r"C:\Users\15922\Desktop\llm\graphrag\graphrag_src"

def build_cmd(method: str, query_text: str):
    """构造 graphrag query 命令（查询文本作为位置参数）"""
    python_exe = r"C:\Users\15922\Desktop\llm\graphrag\graphrag_src\.venv\Scripts\python.exe"
    base_cmd = [
        python_exe,
        "-m", "graphrag",
        "query",
        "--root", GRAPHRAG_ROOT,
        "--method", method,
    ]
    cmd = base_cmd + [query_text]
    return cmd

def safe_decode(raw_bytes):
    """容错解码：UTF-8 → GBK → Latin-1 兜底"""
    if not raw_bytes:
        return ""
    for enc in ["utf-8", "gbk", "cp936", "latin-1"]:
        try:
            return raw_bytes.decode(enc)
        except UnicodeDecodeError:
            continue
    # 最后兜底
    return raw_bytes.decode("utf-8", errors="replace")

# ========== API 路由 ==========
@app.post("/api/query")
async def handle_query(request: Request):
    body = await request.json()
    method = body.get("method", "local")
    query = body.get("query") or body.get("question") or ""

    if not query.strip():
        return {"answer": "❌ 问题不能为空，请输入问题后重试。"}

    cmd = build_cmd(method, query)
    print(f"[后端] 执行命令: {' '.join(cmd)}")

    try:
        # 关键：强制子进程输出 UTF-8 + 继承代理环境变量
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        # 以字节模式捕获（不指定 text=True）
        result = subprocess.run(
            cmd,
            capture_output=True,
            cwd=GRAPHRAG_ROOT,
            env=env,
            timeout=180
        )

        print(f"[后端] 返回码: {result.returncode}")

        # 容错解码 stdout 和 stderr
        stdout_text = safe_decode(result.stdout)
        stderr_text = safe_decode(result.stderr)

        if stdout_text:
            print(f"[后端] stdout 前500字:\n{stdout_text[:500]}")
        if stderr_text:
            print(f"[后端] stderr 前500字:\n{stderr_text[:500]}")

        if result.returncode != 0:
            err = stderr_text or stdout_text or "未知错误"
            return {"answer": f"❌ GraphRAG 执行失败:\n{err[:800]}"}

        output = stdout_text.strip()
        if not output:
            return {"answer": "⚠️ 模型返回为空。可能原因：\n1. 文档中无相关内容\n2. 尝试切换为 local 模式\n3. 检查代理是否通畅"}

        return {"answer": output}

    except subprocess.TimeoutExpired:
        return {"answer": "⏱️ 查询超时（180秒）。免费模型响应较慢，建议：\n1. 改用 local 模式\n2. 问题简短一些\n3. 确认 Watt Toolkit 代理已开启"}
    except Exception as e:
        return {"answer": f"❌ 后端异常: {str(e)}"}

@app.get("/api/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
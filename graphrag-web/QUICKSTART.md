# GraphRAG Web 前端 — 快速启动指南（Windows）

> 技术栈：**React 18 + Vite**（前端） + **FastAPI**（后端，调用 `graphrag query`）

## 一、前置条件

1. 已安装 **Node.js 18+**（建议 20 LTS）：https://nodejs.org
2. 已安装 **Python 3.10+** 与 **pip**
3. 你的 GraphRAG 项目已索引完成（即 `output/` 目录存在）
4. 已配置硅基流动 API Key（`.env` 文件在 graphrag 项目根目录）

## 二、后端（先启动）

```powershell
# 1. 安装 FastAPI 依赖（建议在独立环境或直接使用当前环境）
pip install fastapi uvicorn pydantic

# 2. 编辑 backend.py，确认 GRAPHRAG_ROOT 指向你的 graphrag 项目目录
#    默认值：C:\Users\15922\Desktop\llm\graphrag\graphrag_src
#    若你用 uv 管理 graphrag，把 GRAPHRAG_BIN 改为 "uv run graphrag" 并相应调整 subprocess 调用

# 3. 启动后端（默认 127.0.0.1:8000）
uvicorn backend:app --host 127.0.0.1 --port 8000 --reload
```

测试后端是否可用：
```powershell
curl http://127.0.0.1:8000/api/health
# 应返回 {"status":"ok"}
```

## 三、前端

新开一个 PowerShell 窗口：

```powershell
cd graphrag-web
npm install        # 首次安装依赖
npm run dev        # 启动开发服务器，默认 http://127.0.0.1:5173
```

浏览器打开 http://127.0.0.1:5173 即可使用。

## 四、使用

- 顶部下拉框选择查询方式：**Local / Global / Drift / Basic**
- 输入问题 → 点击「提问」→ 等待返回结果
- Vite 已配置代理：`/api/*` 自动转发到 `127.0.0.1:8000`，无需手动处理跨域

## 五、常见问题

| 问题 | 解决 |
|------|------|
| 前端报 404 / 连不上后端 | 确认后端 `uvicorn` 已启动且在 8000 端口 |
| 后端报 `未找到 graphrag 命令` | 把 `backend.py` 里 `GRAPHRAG_BIN` 改为 graphrag 的实际路径，或用 `uv run graphrag` |
| 查询超时 / 免费模型慢 | Global 查询在文档少时可能较慢，先用 Local 验证 |
| API Key 报错 | 确认 `.env` 在 graphrag 项目根目录且 Key 有效 |

## 六、生产构建

```powershell
npm run build      # 生成 dist/
npm run preview    # 预览构建结果
```

`dist/` 可部署到 GitHub Pages / Vercel / Nginx 等任意静态托管。

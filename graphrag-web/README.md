# GraphRAG Web 前端

基于 **React 18 + Vite** 的 GraphRAG 知识图谱问答前端，配合 FastAPI 后端调用 `graphrag query` 命令。

## 目录结构

```
graphrag-web/
├── index.html          # 入口 HTML
├── package.json        # 前端依赖
├── vite.config.js      # Vite 配置（含 /api 代理）
├── backend.py          # FastAPI 后端示例
└── src/
    ├── main.jsx        # React 入口
    ├── App.jsx         # 主界面（查询表单 + 结果展示）
    ├── ResultCard.jsx  # 结果卡片组件
    └── index.css       # 全局样式
```

## 快速启动

### 1. 安装前端依赖

```bash
cd graphrag-web
npm install
```

### 2. 启动前端开发服务器

```bash
npm run dev
# 访问 http://127.0.0.1:5173
```

### 3. 启动后端（另开一个终端）

```bash
# 安装后端依赖
pip install fastapi uvicorn pydantic

# 编辑 backend.py，将 GRAPHRAG_ROOT 改为你的 graphrag 项目目录
# （即包含 settings.yaml 和 output/ 的目录）

# 启动后端
uvicorn backend:app --host 127.0.0.1 --port 8000 --reload
```

> 前端 Vite 已配置代理：`/api/*` -> `http://127.0.0.1:8000`，无需额外 CORS 配置。

## 使用说明

1. 在顶部下拉框选择查询方式：**Local / Global / Drift / Basic**
   - **Local**：基于图谱实体邻居 + 原文块，适合具体事实问题
   - **Global**：基于社区报告做 map-reduce，适合跨文档宏观问题（文档多时效果更佳）
   - **Drift**：探索式搜索，适合开放性问题
   - **Basic**：基础 RAG 检索
2. 输入问题后点击「提问」，等待后端调用 graphrag 并返回结果。

## 生产构建

```bash
npm run build      # 生成 dist/
npm run preview    # 本地预览构建结果
```

构建产物 `dist/` 可部署到任意静态托管服务（如 GitHub Pages、Vercel、Nginx）。

## 注意事项

- 后端 `backend.py` 中的 `GRAPHRAG_ROOT` **必须**改为你本机的 graphrag 项目绝对路径。
- 若你使用 `uv` 管理 graphrag 环境，可将 `GRAPHRAG_BIN` 改为 `["uv", "run", "graphrag"]` 并相应调整 `subprocess.run` 调用。
- API Key（`.env`）仅由 graphrag 后端读取，**不要**提交到前端仓库。

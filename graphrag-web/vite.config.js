import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// 开发时把前端 /api 请求代理到后端服务。
// 后端 GraphRAG 服务（如用 FastAPI / Flask 封装）默认假设运行在 http://127.0.0.1:8000
// 如果你的后端端口不同，修改 proxy target 即可。
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        // 如果后端是 graphrag query 的命令行封装，可按需调整
      },
    },
  },
});

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    host: '0.0.0.0', // 监听所有网络接口，允许局域网访问
    port: 5173,
    strictPort: false,
    // 允许 CloudStudio 域名访问（支持动态分配的域名）
    // 在开发环境中，允许所有 host（Docker 容器内使用，相对安全）
    // 如果需要更严格的限制，可以指定具体的域名列表
    allowedHosts: true, // 允许所有 host（适用于 CloudStudio 等动态域名环境）
    // 如果需要更严格的限制，可以使用以下配置：
    // allowedHosts: [
    //   'localhost',
    //   '.cloudstudio.club', // 允许所有 cloudstudio.club 子域名
    //   '.coding.net', // 允许所有 coding.net 子域名
    // ],
    // 可选：配置代理以避免 CORS 问题
    // proxy: {
    //   '/api': {
    //     target: 'http://localhost:8000',
    //     changeOrigin: true,
    //   }
    // }
  },
  build: {
    rollupOptions: {
      output: {
        // 优化代码分割，避免模块导入问题
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'ui-vendor': ['axios']
        }
      }
    },
    // 增加 chunk 大小警告限制
    chunkSizeWarningLimit: 1000
  },
  optimizeDeps: {
    // 预构建依赖，避免动态导入问题
    include: ['vue', 'vue-router', 'pinia', 'axios']
  }
})

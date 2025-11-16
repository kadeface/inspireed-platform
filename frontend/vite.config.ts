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

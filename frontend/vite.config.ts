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
        // 优化代码分割，按功能模块拆分
        manualChunks: (id) => {
          // 将 node_modules 中的依赖分组
          if (id.includes('node_modules')) {
            // Vue 核心库
            if (id.includes('vue') || id.includes('@vue') || id.includes('pinia') || id.includes('vue-router')) {
              return 'vue-vendor'
            }
            // UI 组件库
            if (id.includes('@headlessui') || id.includes('@heroicons')) {
              return 'ui-vendor'
            }
            // 工具库
            if (id.includes('axios') || id.includes('lodash') || id.includes('dayjs') || id.includes('crypto-js')) {
              return 'utils-vendor'
            }
            // 编辑器相关（拆分得更细致）
            if (id.includes('monaco-editor') || id.includes('monaco')) {
              return 'monaco-vendor'
            }
            if (id.includes('codemirror') || id.includes('@codemirror')) {
              return 'codemirror-vendor'
            }
            if (id.includes('@antv') || id.includes('antv')) {
              return 'antv-vendor'
            }
            if (id.includes('@tiptap') || id.includes('tiptap') || id.includes('prosemirror')) {
              return 'tiptap-vendor'
            }
            // 图表和可视化
            if (id.includes('echarts') || id.includes('chart.js') || id.includes('three')) {
              return 'chart-vendor'
            }
            // PDF 相关
            if (id.includes('pdf') || id.includes('pdfjs-dist') || id.includes('pdf-lib')) {
              return 'pdf-vendor'
            }
            // Pyodide 相关（Python 运行时，通常很大）
            if (id.includes('pyodide') || id.includes('pyodide-')) {
              return 'pyodide-vendor'
            }
            // 3D 物理引擎
            if (id.includes('matter-js')) {
              return 'physics-vendor'
            }
            // Excel 相关
            if (id.includes('xlsx')) {
              return 'excel-vendor'
            }
            // 其他依赖
            return 'vendor'
          }
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

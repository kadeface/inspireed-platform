import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: false,
  },
  build: {
    target: 'es2020',
    cssCodeSplit: true,
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'http': ['axios'],
          'editor': ['@tiptap/vue-3', '@tiptap/starter-kit'],
          'charts': ['echarts'],
          'diagram': ['@antv/x6'],
          'codemirror': ['codemirror', '@codemirror/lang-python', '@codemirror/lang-javascript'],
        }
      }
    },
    chunkSizeWarningLimit: 1000,
  },
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', 'axios']
  }
})

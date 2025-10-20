<template>
  <div class="code-cell cell-container">
    <!-- 控制栏 - 编辑模式显示全部控件，预览模式下Python/JS显示运行按钮 -->
    <div v-if="editable || cell.content.language !== 'html'" class="flex justify-between items-center mb-2">
      <div class="flex items-center gap-2">
        <!-- 语言选择器 - 仅编辑模式显示 -->
        <select
          v-if="editable"
          v-model="cell.content.language"
          @change="handleLanguageChange"
          class="text-sm px-2 py-1 border border-gray-300 rounded bg-white hover:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
          <option value="html">HTML</option>
        </select>
        
        <span
          v-if="pyodideStatus === 'loading' && cell.content.language === 'python'"
          class="text-xs text-blue-600 flex items-center gap-1"
        >
          <svg class="animate-spin h-3 w-3" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          加载中...
        </span>
        <span
          v-else-if="pyodideStatus === 'ready' && cell.content.language === 'python'"
          class="text-xs text-green-600"
          title="Python 环境已就绪"
        >
          ✓ 已就绪
        </span>
      </div>
      <div class="flex items-center gap-2">
        <span v-if="executionTime > 0" class="text-xs text-gray-500">
          {{ formatExecutionTime(executionTime) }}
        </span>
        <button
          v-if="!isRunning"
          @click="runCode"
          class="px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600 flex items-center gap-1"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
          </svg>
          运行
        </button>
        <span v-else class="text-sm text-gray-500 flex items-center gap-1">
          <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          运行中...
        </span>
      </div>
    </div>

    <!-- 代码编辑器 - HTML类型在预览模式下隐藏，Python/JS显示 -->
    <div :class="['code-editor-wrapper', { 'hidden': !editable && cell.content.language === 'html' }]">
      <div ref="editorRef" class="code-editor"></div>
    </div>

    <!-- 输出区域 - Python/JS在预览模式下也显示 -->
    <div v-if="output && (editable || (cell.content.language !== 'html' && output.trim()))" class="output-area mt-2">
      <div class="text-xs text-gray-500 mb-1">输出:</div>
      <pre class="bg-gray-900 text-gray-100 p-3 rounded text-sm overflow-x-auto">{{ output }}</pre>
    </div>

    <!-- 错误区域 - Python/JS在预览模式下也显示 -->
    <div v-if="error && (editable || cell.content.language !== 'html')" class="error-area mt-2">
      <div class="text-xs text-red-500 mb-1">错误:</div>
      <pre class="bg-red-50 text-red-700 p-3 rounded text-sm overflow-x-auto">{{ error }}</pre>
    </div>

    <!-- HTML 预览 - 在所有模式下显示 -->
    <div v-if="cell.content.language === 'html' && cell.content.code.trim()" class="preview-area mt-2">
      <iframe 
        ref="htmlPreviewRef"
        :srcdoc="cell.content.code" 
        class="w-full border rounded bg-white overflow-hidden"
        :style="{ height: iframeHeight }"
        sandbox="allow-scripts allow-same-origin"
        @load="handleIframeLoad"
      ></iframe>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { EditorView, basicSetup } from 'codemirror'
import { python } from '@codemirror/lang-python'
import { javascript } from '@codemirror/lang-javascript'
import { html } from '@codemirror/lang-html'
import { oneDark } from '@codemirror/theme-one-dark'
import type { CodeCell as CodeCellType } from '../../types/cell'
import { pyodideService } from '../../services/pyodide'

interface Props {
  cell: CodeCellType
  editable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
})

const emit = defineEmits<{
  update: [cell: CodeCellType]
}>()

const editorRef = ref<HTMLElement>()
const htmlPreviewRef = ref<HTMLIFrameElement>()
const output = ref('')
const error = ref('')
const isRunning = ref(false)
const pyodideStatus = ref<'unloaded' | 'loading' | 'ready' | 'error'>('unloaded')
const executionTime = ref(0)
const iframeHeight = ref('400px')

let editorView: EditorView | null = null

// 语言显示名称
const languageDisplayName = computed(() => {
  switch (props.cell.content.language) {
    case 'python':
      return 'Python'
    case 'javascript':
      return 'JavaScript'
    case 'html':
      return 'HTML'
    default:
      return props.cell.content.language
  }
})

onMounted(() => {
  // 初始化编辑器（始终初始化，但通过CSS控制显示）
  if (editorRef.value) {
    const lang = 
      props.cell.content.language === 'python' ? python() :
      props.cell.content.language === 'html' ? html() :
      javascript()
    
    editorView = new EditorView({
      doc: props.cell.content.code,
      extensions: [
        basicSetup,
        lang,
        oneDark,
        EditorView.updateListener.of((update) => {
          if (update.docChanged && props.editable) {
            props.cell.content.code = update.state.doc.toString()
            emit('update', props.cell)
          }
        }),
      ],
      parent: editorRef.value,
    })
  }
  
  // 在预览模式下，如果是 HTML 类型，自动渲染；如果是 Python/JavaScript，自动运行
  if (!props.editable && props.cell.content.code.trim()) {
    if (props.cell.content.language !== 'html') {
      // 延迟执行，确保组件已完全加载
      setTimeout(() => {
        runCode()
      }, 100)
    }
  }
})

watch(
  () => props.cell.content.code,
  (newCode) => {
    if (editorView && editorView.state.doc.toString() !== newCode) {
      editorView.dispatch({
        changes: { from: 0, to: editorView.state.doc.length, insert: newCode },
      })
    }
    
    // 如果是HTML代码变化，重新计算iframe高度
    if (props.cell.content.language === 'html') {
      setTimeout(() => {
        handleIframeLoad()
      }, 200)
    }
  }
)

// 处理语言切换
function handleLanguageChange() {
  // 清空输出和错误
  output.value = ''
  error.value = ''
  executionTime.value = 0
  
  // 更新编辑器语言
  if (editorView && editorRef.value) {
    const currentCode = editorView.state.doc.toString()
    
    // 销毁旧编辑器
    editorView.destroy()
    
    // 根据新语言设置示例代码
    let newCode = currentCode
    if (!currentCode.trim() || currentCode.includes('Hello, World!')) {
      switch (props.cell.content.language) {
        case 'python':
          newCode = '# 在此编写 Python 代码\nprint("Hello, World!")'
          break
        case 'javascript':
          newCode = '// 在此编写 JavaScript 代码\nconsole.log("Hello, World!");'
          break
        case 'html':
          newCode = '<!-- 在此编写 HTML 代码 -->\n<div>\n  <h1>Hello, World!</h1>\n  <p>这是一个 HTML 示例</p>\n</div>'
          break
      }
      props.cell.content.code = newCode
    }
    
    // 选择语言扩展
    const lang = 
      props.cell.content.language === 'python' ? python() :
      props.cell.content.language === 'html' ? html() :
      javascript()
    
    // 创建新编辑器
    editorView = new EditorView({
      doc: props.cell.content.code,
      extensions: [
        basicSetup,
        lang,
        oneDark,
        EditorView.updateListener.of((update) => {
          if (update.docChanged && props.editable) {
            props.cell.content.code = update.state.doc.toString()
            emit('update', props.cell)
          }
        }),
      ],
      parent: editorRef.value,
    })
  }
  
  // 触发更新
  emit('update', props.cell)
}

// 处理iframe加载完成，自适应高度
function handleIframeLoad() {
  if (htmlPreviewRef.value) {
    try {
      const iframe = htmlPreviewRef.value
      const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document
      
      if (iframeDoc) {
        // 添加CSS确保body内容不会有滚动条
        const style = iframeDoc.createElement('style')
        style.textContent = `
          html, body {
            overflow: hidden !important;
            margin: 0;
            padding: 0;
          }
        `
        iframeDoc.head.appendChild(style)
        
        // 等待内容完全渲染（包括Chart.js等动态内容）
        setTimeout(() => {
          const body = iframeDoc.body
          const html = iframeDoc.documentElement
          
          // 获取内容的实际高度
          const height = Math.max(
            body?.scrollHeight || 0,
            body?.offsetHeight || 0,
            html?.clientHeight || 0,
            html?.scrollHeight || 0,
            html?.offsetHeight || 0
          )
          
          // 设置iframe高度，加上一些内边距
          if (height > 0) {
            iframeHeight.value = `${height + 40}px`
          } else {
            iframeHeight.value = '600px' // 默认高度
          }
          
          // 为了确保Chart.js等动态内容完全加载，再次检查
          setTimeout(() => {
            const finalHeight = Math.max(
              body?.scrollHeight || 0,
              html?.scrollHeight || 0
            )
            if (finalHeight > height) {
              iframeHeight.value = `${finalHeight + 40}px`
            }
          }, 500)
        }, 200)
      }
    } catch (e) {
      // 如果访问iframe内容失败（跨域问题），使用默认高度
      console.warn('Failed to access iframe content for height calculation', e)
      iframeHeight.value = '700px'
    }
  }
}

// 格式化执行时间
function formatExecutionTime(ms: number): string {
  if (ms < 1000) {
    return `${Math.round(ms)}ms`
  } else {
    return `${(ms / 1000).toFixed(2)}s`
  }
}

async function runCode() {
  isRunning.value = true
  output.value = ''
  error.value = ''
  executionTime.value = 0

  try {
    const language = props.cell.content.language

    // Python 代码执行
    if (language === 'python') {
      // 检查 Pyodide 状态
      if (!pyodideService.isReady()) {
        if (pyodideService.isLoading()) {
          output.value = '正在加载 Python 环境，请稍候...'
          pyodideStatus.value = 'loading'
        } else {
          output.value = '正在初始化 Python 环境...'
          pyodideStatus.value = 'loading'
          
          try {
            await pyodideService.init()
            pyodideStatus.value = 'ready'
            output.value = 'Python 环境加载完成，开始执行...'
            await new Promise((resolve) => setTimeout(resolve, 500))
          } catch (err: any) {
            pyodideStatus.value = 'error'
            error.value = '无法加载 Python 环境: ' + (err.message || '未知错误')
            return
          }
        }
      }

      // 执行 Python 代码
      try {
        const result = await pyodideService.runPython(props.cell.content.code)
        
        output.value = result.output || ''
        error.value = result.error
        executionTime.value = result.executionTime

        // 如果没有输出也没有错误，显示执行完成
        if (!output.value && !error.value) {
          output.value = '代码执行完成（无输出）'
        }
      } catch (err: any) {
        error.value = err.message || '执行失败'
      }
    } 
    // JavaScript 代码执行
    else if (language === 'javascript') {
      const startTime = performance.now()
      
      try {
        // 创建一个捕获 console.log 的函数
        const logs: string[] = []
        const originalLog = console.log
        console.log = (...args: any[]) => {
          logs.push(args.map(String).join(' '))
        }

        // 执行 JavaScript 代码
        // eslint-disable-next-line no-eval
        const result = eval(props.cell.content.code)
        
        // 恢复 console.log
        console.log = originalLog

        // 显示输出
        output.value = logs.join('\n')
        
        // 如果有返回值，也显示
        if (result !== undefined && !output.value) {
          output.value = String(result)
        }

        if (!output.value) {
          output.value = '代码执行完成（无输出）'
        }

        executionTime.value = performance.now() - startTime
      } catch (err: any) {
        console.log = console.log // 确保恢复
        error.value = err.message || '执行失败'
        executionTime.value = performance.now() - startTime
      }
    }
    // HTML 代码渲染
    else if (language === 'html') {
      const startTime = performance.now()
      
      try {
        // HTML 在 iframe 中预览，不需要执行
        output.value = 'HTML 预览已生成（请查看下方预览区域）'
        executionTime.value = performance.now() - startTime
      } catch (err: any) {
        error.value = err.message || '渲染失败'
        executionTime.value = performance.now() - startTime
      }
    }
  } catch (err: any) {
    error.value = err.message || '执行失败'
  } finally {
    isRunning.value = false
  }
}
</script>

<style scoped>
.code-cell {
  @apply p-4;
}

.code-editor-wrapper {
  @apply border rounded overflow-hidden;
}

:deep(.cm-editor) {
  @apply text-sm;
}

:deep(.cm-scroller) {
  @apply max-h-96 overflow-auto;
}
</style>


<!-- eslint-disable vue/no-mutating-props -->
<template>
  <div class="text-cell cell-container" :data-cell-id="cell.id" :class="{ 'fullscreen': isFullscreen }" ref="containerRef">
    <!-- 全屏按钮 -->
    <div class="cell-toolbar">
      <button
        class="cell-fullscreen-btn"
        :class="{ 'active': isFullscreen }"
        @click="toggleFullscreen"
        :title="isFullscreen ? '退出全屏 (Esc)' : '全屏查看'"
      >
        <svg v-if="!isFullscreen" class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
        </svg>
        <svg v-else class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
        <span class="text-sm font-medium ml-1">{{ isFullscreen ? '退出全屏' : '全屏' }}</span>
      </button>
    </div>
    
    <div 
      v-if="!isEditing && !editable" 
      class="text-cell-view"
      :class="{
        'compact-content': compactMode && !isExpanded,
        'expanded-content': compactMode && isExpanded
      }"
      v-html="sanitizedHtml"
    ></div>
    
    <!-- 预览模式下的展开/折叠按钮 -->
    <div 
      v-if="compactMode && !editable" 
      class="flex flex-col items-center gap-2 mt-2 pt-2 border-t border-gray-200"
    >
      <button
        @click="isExpanded = !isExpanded"
        class="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors flex items-center gap-2"
      >
        <svg 
          v-if="!isExpanded" 
          class="w-4 h-4" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
        <svg 
          v-else 
          class="w-4 h-4" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
        </svg>
        <span>{{ isExpanded ? '收起' : '展开查看全部' }}</span>
      </button>
      <button
        @click="scrollToTop"
        class="text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1 transition-colors"
        title="点击滚动到顶部"
      >
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>紧凑模式已启用，<span class="underline">点击前往顶部切换</span></span>
      </button>
    </div>
    
    <div v-else class="text-cell-editor">
      <div class="flex justify-between items-center mb-2">
        <input
          v-if="cell.title !== undefined"
          v-model="cell.title"
          type="text"
          placeholder="标题（可选）"
          class="text-lg font-semibold border-none outline-none bg-transparent"
          @blur="handleUpdate"
        />
        <div class="flex gap-2">
          <!-- 编辑器模式切换（仅在编辑模式下显示） -->
          <div v-if="isEditing && editable" class="flex items-center gap-1 border border-gray-300 rounded">
            <button
              @click="editorMode = 'html'"
              :class="[
                'px-3 py-1 text-sm rounded-l transition-colors',
                editorMode === 'html' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              ]"
              title="富文本编辑器"
            >
              富文本
            </button>
            <button
              @click="editorMode = 'markdown'"
              :class="[
                'px-3 py-1 text-sm rounded-r transition-colors',
                editorMode === 'markdown' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              ]"
              title="Markdown编辑器"
            >
              Markdown
            </button>
          </div>
          <button
            v-if="!isEditing && editable"
            @click="startEdit"
            class="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            编辑
          </button>
          <button
            v-if="isEditing"
            @click="saveEdit"
            class="px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600"
          >
            保存
          </button>
          <button
            v-if="isEditing"
            @click="cancelEdit"
            class="px-3 py-1 text-sm bg-gray-400 text-white rounded hover:bg-gray-500"
          >
            取消
          </button>
        </div>
      </div>
      
      <!-- 富文本编辑器 -->
      <div
        v-if="isEditing && editorMode === 'html'"
        :class="{
          'compact-editor-wrapper': compactMode && !isExpanded,
          'expanded-editor-wrapper': compactMode && isExpanded
        }"
      >
        <TipTapEditor
          :content="cell.content.html"
          @update="handleContentUpdate"
        />
      </div>
      <!-- Markdown编辑器 -->
      <div
        v-else-if="isEditing && editorMode === 'markdown'"
        :class="{
          'compact-editor-wrapper': compactMode && !isExpanded,
          'expanded-editor-wrapper': compactMode && isExpanded
        }"
      >
        <MarkdownEditor
          v-model="tempMarkdown"
          @update:modelValue="handleMarkdownUpdate"
        />
      </div>
      <!-- 预览模式 -->
      <div 
        v-else 
        class="prose max-w-none"
        :class="{
          'compact-content': compactMode && !isExpanded && !isEditing,
          'expanded-content': compactMode && isExpanded && !isEditing
        }"
        v-html="sanitizedHtml"
      ></div>
      
      <!-- 紧凑模式下的展开/折叠按钮（编辑模式） -->
      <div 
        v-if="compactMode && editable" 
        class="flex flex-col items-center gap-2 mt-2 pt-2 border-t border-gray-200"
      >
        <button
          @click="isExpanded = !isExpanded"
          class="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors flex items-center gap-2"
        >
          <svg 
            v-if="!isExpanded" 
            class="w-4 h-4" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
          <svg 
            v-else 
            class="w-4 h-4" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
          </svg>
          <span>{{ isExpanded ? '收起' : '展开查看全部' }}</span>
        </button>
        <button
          @click="scrollToTop"
          class="text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1 transition-colors"
          :title="editable ? '点击滚动到顶部工具栏' : '点击滚动到顶部'"
        >
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>紧凑模式已启用，<span class="underline">{{ editable ? '点击前往顶部关闭' : '点击前往顶部切换' }}</span></span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/* eslint-disable vue/no-mutating-props */
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import type { TextCell as TextCellType } from '../../types/cell'
import TipTapEditor from '../Editor/TipTapEditor.vue'
import MarkdownEditor from '../Editor/MarkdownEditor.vue'
import DOMPurify from 'dompurify'
import { getServerBaseUrl } from '@/utils/url'
import { useFullscreen } from '@/composables/useFullscreen'

interface Props {
  cell: TextCellType
  editable?: boolean
  compactMode?: boolean // 紧凑模式：限制长内容的高度
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
  compactMode: false,
})

const emit = defineEmits<{
  update: [cell: TextCellType]
}>()

const containerRef = ref<HTMLElement | null>(null)
const { isFullscreen, toggleFullscreen } = useFullscreen(containerRef)

const isEditing = ref(props.editable)
const tempContent = ref(props.cell.content.html)
const isExpanded = ref(false) // 是否展开（在紧凑模式下）

// 滚动到顶部
function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
// 编辑器模式：'html' 或 'markdown'
const editorMode = ref<'html' | 'markdown'>(
  props.cell.content.editorMode || (props.cell.content.markdown ? 'markdown' : 'html')
)
const tempMarkdown = ref(props.cell.content.markdown || '')

const sanitizedHtml = computed(() => {
  // 如果内容有 Markdown，优先使用 Markdown 渲染（在非编辑模式下）
  let html = ''
  if (props.cell.content.markdown && (!props.editable || !isEditing.value)) {
    // 使用 Markdown 渲染
    html = markdownToHtml(props.cell.content.markdown)
  } else {
    html = props.cell.content.html || ''
  }
  
  const isDev = import.meta.env.DEV
  const baseURL = getServerBaseUrl()
  
  // 处理图片URL：将相对路径转换为绝对路径
  if (html) {
    
    // 匹配所有img标签，处理src属性
    html = html.replace(/<img([^>]*?)>/gi, (match, attrs) => {
      // 提取src属性值（支持单引号、双引号，以及无引号的情况）
      const srcMatch = attrs.match(/\ssrc\s*=\s*(["'])([^"']+)\1/i) || 
                       attrs.match(/\ssrc\s*=\s*([^\s>]+)/i) ||
                       attrs.match(/src\s*=\s*(["'])([^"']+)\1/i) ||
                       attrs.match(/src\s*=\s*([^\s>]+)/i)
      if (srcMatch) {
        const quote = srcMatch[1] || '"'
        let src = srcMatch[2] || srcMatch[1]
        let newSrc = src
        
        // 如果是blob URL，移除该图片（blob URL已经失效）
        if (src.startsWith('blob:')) {
          return '' // 移除无效的blob URL图片
        }
        
        // 如果是data URL，不需要处理
        if (src.startsWith('data:')) {
          return match
        }
        
        // 如果URL包含localhost，需要替换为正确的服务器地址
        if (src.includes('localhost') || src.includes('127.0.0.1')) {
          // 提取路径部分（确保文件名不变）
          try {
            const url = new URL(src)
            const path = url.pathname + (url.search || '') + (url.hash || '')
            // 如果路径只是/，则不添加（避免baseURL后面出现多余的/）
            // 否则确保路径以/开头
            let normalizedPath = path
            if (path === '/') {
              normalizedPath = ''
            } else if (!path.startsWith('/')) {
              normalizedPath = '/' + path
            }
            newSrc = `${baseURL}${normalizedPath}`
            // 验证文件名是否一致
            const originalFilename = url.pathname.split('/').pop()
            const newFilename = newSrc.split('/').pop()?.split('?')[0]
            if (originalFilename && newFilename && originalFilename !== newFilename) {
              // 文件名不一致，但继续处理
            }
          } catch (e) {
            // 如果URL解析失败，尝试直接替换localhost部分
            const originalFilename = src.split('/').pop()?.split('?')[0]
            newSrc = src.replace(/https?:\/\/localhost(:\d+)?/, baseURL)
              .replace(/https?:\/\/127\.0\.0\.1(:\d+)?/, baseURL)
            const newFilename = newSrc.split('/').pop()?.split('?')[0]
            if (originalFilename && newFilename && originalFilename !== newFilename) {
              // 文件名不一致，但继续处理
            }
          }
        }
        // 如果是完整URL（http/https），检查是否需要替换为当前服务器地址
        else if (src.startsWith('http://') || src.startsWith('https://')) {
          try {
            const url = new URL(src)
            const currentHost = window.location.hostname
            const urlHost = url.hostname
            
            // 如果URL指向的是资源路径 (/uploads/resources/)，并且：
            // 1. 主机名是IP地址（192.168.x.x, 10.x.x.x, 172.x.x.x等）
            // 2. 或者是不同的主机名（排除当前主机）
            // 则替换为当前服务器地址
            if (url.pathname.startsWith('/uploads/resources/')) {
              const isIPAddress = /^(\d{1,3}\.){3}\d{1,3}$/.test(urlHost)
              const isLocalhost = urlHost === 'localhost' || urlHost === '127.0.0.1'
              const isDifferentHost = urlHost !== currentHost && !isLocalhost
              
              // 如果是IP地址或者不同的主机名，替换为当前服务器地址
              if (isIPAddress || isDifferentHost) {
                const path = url.pathname + (url.search || '') + (url.hash || '')
                newSrc = `${baseURL}${path}`
              } else {
                // 主机名相同，无需处理
                return match
              }
            } else {
              // 不是资源路径，保持原样
              return match
            }
          } catch (e) {
            // URL解析失败，保持原样
            return match
          }
        }
        // 如果是相对路径（以/开头但不是//），转换为绝对URL
        else if (src.startsWith('/') && !src.startsWith('//')) {
          newSrc = `${baseURL}${src}`
        }
        // 如果是其他相对路径，也转换为绝对URL
        else if (!src.startsWith('//')) {
          newSrc = `${baseURL}/${src.startsWith('/') ? src.slice(1) : src}`
        }
        
        // 如果URL被修改，替换原src值
        if (newSrc !== src) {
          // 提取文件名用于验证
          const originalFilename = src.split('/').pop()?.split('?')[0] // 移除查询参数
          const newFilename = newSrc.split('/').pop()?.split('?')[0] // 移除查询参数
          
          // 验证文件名是否一致（静默处理，不输出错误）
          if (originalFilename && newFilename && originalFilename !== newFilename) {
            // 文件名不一致，但继续处理
          }
          
          // 使用更可靠的替换方法：直接替换src属性值
          // 匹配src属性（支持各种引号格式）
          const srcAttrPattern = /src\s*=\s*(["']?)([^"'\s>]+)\1/i
          const newMatch = match.replace(srcAttrPattern, (fullMatch, quoteChar, urlValue) => {
            // 如果匹配到的URL值就是我们要替换的src，则替换它
            if (urlValue === src || urlValue === src.replace(/^["']|["']$/g, '')) {
              const finalQuote = quoteChar || quote
              return `src=${finalQuote}${newSrc}${finalQuote}`
            }
            return fullMatch
          })
          
          // 如果替换成功，返回新匹配；否则尝试更通用的方法
          if (newMatch !== match) {
            return newMatch
          } else {
            // 备用方法：直接替换整个src属性
            const escapedSrc = src.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
            const srcPattern = new RegExp(`(src\\s*=\\s*["']?)${escapedSrc}(["']?)`, 'gi')
            return match.replace(srcPattern, `$1${newSrc}$2`)
          }
        }
      }
      return match
    })
  }
  
  // 处理PDF和文件附件中的URL
  html = html.replace(/<div\s+class="(pdf|file)-attachment[^"]*"[^>]*>/gi, (match) => {
    // 提取data-pdf-url或data-file-url属性
    const urlMatch = match.match(/data-(pdf|file)-url\s*=\s*(["'])([^"']+)\2/i)
    if (urlMatch) {
      const quote = urlMatch[2]
      let url = urlMatch[3]
      let newUrl = url
      
      // 如果是相对路径，转换为绝对URL
      if (url.startsWith('/') && !url.startsWith('//')) {
        newUrl = `${baseURL}${url}`
      } else if (!url.startsWith('http') && !url.startsWith('//')) {
        newUrl = `${baseURL}/${url.startsWith('/') ? url.slice(1) : url}`
      }
      
      if (newUrl !== url) {
        const newUrlAttr = `data-${urlMatch[1]}-url=${quote}${url}${quote}`
        const newMatch = match.replace(urlMatch[0], newUrlAttr)
        return newMatch
      }
    }
    return match
  })
  
  // 处理文件查看按钮的onclick
  html = html.replace(/<button[^>]*class="file-view-btn"[^>]*onclick="window\.open\('([^']+)'[^)]*\)"[^>]*>/gi, (match, url) => {
    let newUrl = url
    if (url.startsWith('/') && !url.startsWith('//')) {
      newUrl = `${baseURL}${url}`
    } else if (!url.startsWith('http') && !url.startsWith('//')) {
      newUrl = `${baseURL}/${url.startsWith('/') ? url.slice(1) : url}`
    }
    if (newUrl !== url) {
      return match.replace(/window\.open\('([^']+)'/gi, `window.open('${newUrl}'`)
    }
    return match
  })
  
  // 处理文件下载链接：将相对路径转换为完整URL
  html = html.replace(/<a[^>]*class="file-download-btn"[^>]*href\s*=\s*(["'])([^"']+)\1[^>]*>/gi, (match, quote, url) => {
    let newUrl = url
    if (url.startsWith('/') && !url.startsWith('//')) {
      newUrl = `${baseURL}${url}`
    } else if (!url.startsWith('http') && !url.startsWith('//')) {
      newUrl = `${baseURL}/${url.startsWith('/') ? url.slice(1) : url}`
    }
    if (newUrl !== url) {
      return match.replace(/href\s*=\s*["'][^"']+["']/gi, `href=${quote}${newUrl}${quote}`)
    }
    return match
  })
  
  // 处理data-file-download-url属性
  html = html.replace(/data-file-download-url\s*=\s*(["'])([^"']+)\1/gi, (match, quote, url) => {
    let newUrl = url
    if (url.startsWith('/') && !url.startsWith('//')) {
      newUrl = `${baseURL}${url}`
    } else if (!url.startsWith('http') && !url.startsWith('//')) {
      newUrl = `${baseURL}/${url.startsWith('/') ? url.slice(1) : url}`
    }
    if (newUrl !== url) {
      return `data-file-download-url=${quote}${newUrl}${quote}`
    }
    return match
  })
  
  // 配置DOMPurify允许图片和文件标签
  const config = {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'u', 's', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'img', 'div', 'span', 'button'],
    ALLOWED_ATTR: ['href', 'target', 'rel', 'src', 'alt', 'title', 'width', 'height', 'class', 'style', 'id', 'data-file-url', 'data-file-filename', 'onclick', 'download'],
    ALLOW_DATA_ATTR: true,
    KEEP_CONTENT: true,
  }
  
  let sanitized = DOMPurify.sanitize(html, config)
  
  // 最终清理：替换sanitized HTML中任何剩余的localhost URL
  // 这是一个安全网，确保所有localhost URL都被替换
  // 只有当baseURL不包含localhost时才进行替换
  const baseURLHasLocalhost = baseURL.includes('localhost') || baseURL.includes('127.0.0.1')
  
  if (!baseURLHasLocalhost) {
    // 只有当baseURL不是localhost时，才需要替换localhost URL
    // 匹配完整的localhost URL（包含路径）
    sanitized = sanitized.replace(/https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?(\/[^\s"'>]*)?/gi, (match) => {
      try {
        const url = new URL(match)
        const path = url.pathname + (url.search || '') + (url.hash || '')
        // 如果路径只是/，则不添加（避免baseURL后面出现多余的/）
        // 否则确保路径以/开头
        let normalizedPath = path
        if (path === '/') {
          normalizedPath = ''
        } else if (!path.startsWith('/')) {
          normalizedPath = '/' + path
        }
        const newUrl = baseURL + normalizedPath
        return newUrl
      } catch (e) {
        // 如果URL解析失败，直接替换localhost部分
        const newUrl = match.replace(/https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?/, baseURL)
        return newUrl
      }
    })
    
    // 处理硬编码的IP地址URL（如192.168.x.x:8000/uploads/resources/...）
    // 匹配包含 /uploads/resources/ 的IP地址URL
    sanitized = sanitized.replace(/https?:\/\/(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(:\d+)?(\/uploads\/resources\/[^\s"'>]*)/gi, (match) => {
      try {
        const url = new URL(match)
        const path = url.pathname + (url.search || '') + (url.hash || '')
        // 如果是资源路径，替换为当前服务器地址
        if (path.startsWith('/uploads/resources/')) {
          let normalizedPath = path
          if (path === '/') {
            normalizedPath = ''
          } else if (!path.startsWith('/')) {
            normalizedPath = '/' + path
          }
          return baseURL + normalizedPath
        }
      } catch (e) {
        // URL解析失败，尝试直接提取路径
        const pathMatch = match.match(/\/uploads\/resources\/[^\s"'>]+/)
        if (pathMatch) {
          return baseURL + pathMatch[0]
        }
      }
      return match
    })
  }
  
  // 修复双斜杠问题（如果baseURL以/结尾，路径也以/开头）
  // 转义baseURL中的特殊字符用于正则表达式
  const escapedBaseURL = baseURL.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  sanitized = sanitized.replace(new RegExp(escapedBaseURL + '//+', 'g'), baseURL + '/')
  
  // 检查处理后的HTML（仅在开发环境或发现问题时输出日志）
  const originalHasImg = html.includes('<img')
  const sanitizedHasImg = sanitized.includes('<img')
  if (originalHasImg) {
    // 只有当baseURL不包含localhost时，才检查是否有localhost URL
    // 如果baseURL本身就是localhost，那么包含localhost是正常的
    if (!baseURLHasLocalhost) {
      const hasLocalhost = /localhost|127\.0\.0\.1/.test(sanitized)
      if (hasLocalhost) {
        // 静默处理，不输出错误
      }
    }
    
    if (!sanitizedHasImg) {
      // 图片标签被过滤，静默处理
    }
  }
  
  return sanitized
})

// Markdown 转 HTML 的简单实现（用于预览）
function markdownToHtml(markdown: string): string {
  if (!markdown) return ''
  
  // 使用 MarkdownPreview 组件的逻辑
  const lines = markdown.split(/\r?\n/)
  const html: string[] = []
  let inList = false
  let inBlockquote = false
  let inCodeBlock = false
  let codeBuffer: string[] = []

  const escapeHtml = (input: string): string => {
    return input
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;')
  }

  const renderInline = (text: string): string => {
    let result = escapeHtml(text)
    result = result.replace(
      /\[([^\]]+)]\((https?:\/\/[^\s)]+)\)/g,
      (_match, label, url) =>
        `<a href="${url}" target="_blank" rel="noopener noreferrer">${label}</a>`
    )
    result = result.replace(/`([^`]+)`/g, '<code>$1</code>')
    result = result.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    result = result.replace(/\*([^*]+)\*/g, '<em>$1</em>')
    return result
  }

  const closeList = () => {
    if (inList) {
      html.push('</ul>')
      inList = false
    }
  }

  const closeBlockquote = () => {
    if (inBlockquote) {
      html.push('</blockquote>')
      inBlockquote = false
    }
  }

  const closeCodeBlock = () => {
    if (inCodeBlock) {
      const codeContent = escapeHtml(codeBuffer.join('\n'))
      html.push(`<pre><code>${codeContent}</code></pre>`)
      inCodeBlock = false
      codeBuffer = []
    }
  }

  lines.forEach((line) => {
    if (/^```/.test(line.trim())) {
      if (inCodeBlock) {
        closeCodeBlock()
      } else {
        closeList()
        closeBlockquote()
        inCodeBlock = true
        codeBuffer = []
      }
      return
    }

    if (inCodeBlock) {
      codeBuffer.push(line)
      return
    }

    if (line.trim() === '') {
      closeList()
      closeBlockquote()
      html.push('<p></p>')
      return
    }

    const headingMatch = line.match(/^(#{1,3})\s+(.*)$/)
    if (headingMatch) {
      closeList()
      closeBlockquote()
      const level = headingMatch[1].length
      const content = renderInline(headingMatch[2])
      html.push(`<h${level}>${content}</h${level}>`)
      return
    }

    if (/^>\s+/.test(line)) {
      closeList()
      if (!inBlockquote) {
        html.push('<blockquote>')
        inBlockquote = true
      }
      html.push(`<p>${renderInline(line.replace(/^>\s+/, ''))}</p>`)
      return
    }

    if (/^-\s+/.test(line)) {
      closeBlockquote()
      if (!inList) {
        html.push('<ul>')
        inList = true
      }
      html.push(`<li>${renderInline(line.replace(/^-\s+/, ''))}</li>`)
      return
    }

    closeList()
    closeBlockquote()
    html.push(`<p>${renderInline(line)}</p>`)
  })

  closeCodeBlock()
  closeList()
  closeBlockquote()

  return html.join('\n')
}

function startEdit() {
  isEditing.value = true
  // 根据当前内容决定编辑器模式
  if (props.cell.content.markdown) {
    editorMode.value = 'markdown'
    tempMarkdown.value = props.cell.content.markdown
  } else {
    editorMode.value = props.cell.content.editorMode || 'html'
    tempContent.value = props.cell.content.html
    if (editorMode.value === 'markdown' && !tempMarkdown.value) {
      // 如果切换到 Markdown 模式但没有 Markdown 内容，尝试从 HTML 转换
      tempMarkdown.value = htmlToMarkdown(props.cell.content.html)
    }
  }
}

function saveEdit() {
  isEditing.value = false
  handleUpdate()
}

function cancelEdit() {
  isEditing.value = false
  tempContent.value = props.cell.content.html
  tempMarkdown.value = props.cell.content.markdown || ''
  editorMode.value = props.cell.content.editorMode || (props.cell.content.markdown ? 'markdown' : 'html')
}

function handleContentUpdate(html: string) {
  tempContent.value = html
  props.cell.content.html = html
  props.cell.content.editorMode = 'html'
  // 如果使用 HTML 编辑器，清除 Markdown 内容
  if (editorMode.value === 'html') {
    props.cell.content.markdown = undefined
  }
}

function handleMarkdownUpdate(markdown: string) {
  tempMarkdown.value = markdown
  props.cell.content.markdown = markdown
  props.cell.content.editorMode = 'markdown'
  // 将 Markdown 转换为 HTML 用于预览和兼容性
  props.cell.content.html = markdownToHtml(markdown)
}

// HTML 转 Markdown 的简单实现（用于从 HTML 模式切换到 Markdown 模式）
function htmlToMarkdown(html: string): string {
  if (!html) return ''
  
  // 创建一个临时 DOM 元素来解析 HTML
  const tempDiv = document.createElement('div')
  tempDiv.innerHTML = html
  
  let markdown = ''
  
  const processNode = (node: Node): string => {
    if (node.nodeType === Node.TEXT_NODE) {
      return node.textContent || ''
    }
    
    if (node.nodeType !== Node.ELEMENT_NODE) {
      return ''
    }
    
    const element = node as HTMLElement
    const tagName = element.tagName.toLowerCase()
    const children = Array.from(element.childNodes)
    const content = children.map(processNode).join('')
    
    switch (tagName) {
      case 'h1':
        return `# ${content}\n\n`
      case 'h2':
        return `## ${content}\n\n`
      case 'h3':
        return `### ${content}\n\n`
      case 'strong':
      case 'b':
        return `**${content}**`
      case 'em':
      case 'i':
        return `*${content}*`
      case 'code':
        return `\`${content}\``
      case 'pre':
        return `\`\`\`\n${content}\n\`\`\`\n\n`
      case 'ul':
        return `${content}\n`
      case 'ol':
        return `${content}\n`
      case 'li':
        return `- ${content}\n`
      case 'blockquote':
        return `> ${content}\n\n`
      case 'p':
        return `${content}\n\n`
      case 'br':
        return '\n'
      case 'a':
        const href = element.getAttribute('href') || ''
        return `[${content}](${href})`
      case 'img':
        const src = element.getAttribute('src') || ''
        const alt = element.getAttribute('alt') || ''
        return `![${alt}](${src})`
      default:
        return content
    }
  }
  
  markdown = processNode(tempDiv).trim()
  return markdown
}

// 监听编辑器模式变化
watch(editorMode, (newMode) => {
  if (isEditing.value) {
    if (newMode === 'markdown' && !tempMarkdown.value && props.cell.content.html) {
      // 从 HTML 模式切换到 Markdown 模式，尝试转换
      tempMarkdown.value = htmlToMarkdown(props.cell.content.html)
    }
  }
})

function handleUpdate() {
  emit('update', props.cell)
}

// 监听图片加载错误
function handleImageError(event: Event) {
  // 静默处理图片加载错误
}

onMounted(async () => {
  // 等待DOM渲染完成后再添加事件监听
  await nextTick()
  
  const isDev = import.meta.env.DEV
  
  // 在组件挂载后，为所有图片添加错误监听
  const cellElement = document.querySelector(`[data-cell-id="${props.cell.id}"]`)
  if (cellElement) {
    const images = cellElement.querySelectorAll('img')
    images.forEach(img => {
      img.addEventListener('error', handleImageError)
    })
  }
})

onUnmounted(() => {
  // 清理事件监听
  const cellElement = document.querySelector(`[data-cell-id="${props.cell.id}"]`)
  if (cellElement) {
    const images = cellElement.querySelectorAll('img')
    images.forEach(img => {
      img.removeEventListener('error', handleImageError)
    })
  }
})
</script>

<style scoped>
.text-cell-view {
  @apply prose max-w-none;
}

.text-cell-editor {
  @apply w-full;
}

/* 确保图片在全屏预览中正常显示 */
:deep(.text-cell-view img),
:deep(.prose img) {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 1rem 0;
}

/* 确保图片容器不会隐藏内容 */
.text-cell-view :deep(img),
.text-cell-editor :deep(img) {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 1rem 0;
}

/* 文件附件样式 */
.text-cell-view :deep(.file-attachment),
.text-cell-editor :deep(.file-attachment) {
  @apply my-6 border border-gray-300 rounded-lg overflow-hidden bg-white shadow-sm;
}

.text-cell-view :deep(.file-preview-card),
.text-cell-editor :deep(.file-preview-card) {
  @apply flex items-center gap-3 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 transition-all duration-200;
}

.text-cell-view :deep(.file-actions),
.text-cell-editor :deep(.file-actions) {
  @apply flex items-center gap-2;
}

.text-cell-view :deep(.pdf-icon),
.text-cell-view :deep(.file-icon),
.text-cell-editor :deep(.pdf-icon),
.text-cell-editor :deep(.file-icon) {
  @apply text-3xl flex-shrink-0;
}

.text-cell-view :deep(.pdf-info),
.text-cell-view :deep(.file-info),
.text-cell-editor :deep(.pdf-info),
.text-cell-editor :deep(.file-info) {
  @apply flex-1 min-w-0;
}

.text-cell-view :deep(.pdf-filename),
.text-cell-view :deep(.file-filename),
.text-cell-editor :deep(.pdf-filename),
.text-cell-editor :deep(.file-filename) {
  @apply font-medium text-gray-900 truncate;
}

.text-cell-view :deep(.pdf-size),
.text-cell-view :deep(.file-size),
.text-cell-editor :deep(.pdf-size),
.text-cell-editor :deep(.file-size) {
  @apply text-sm text-gray-500 mt-1;
}

/* 全屏按钮样式 */
.cell-toolbar {
  @apply flex justify-end mb-2;
}

.cell-fullscreen-btn {
  @apply flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-50 hover:bg-gray-100 rounded-md transition-colors;
}

.cell-fullscreen-btn.active {
  @apply bg-red-50 hover:bg-red-100 text-red-700;
}

.cell-fullscreen-btn .icon {
  @apply w-4 h-4;
}

/* 全屏模式样式 */
.text-cell.fullscreen {
  @apply fixed inset-0 z-50 bg-white overflow-auto;
}

.text-cell.fullscreen .text-cell-view {
  @apply p-8 max-w-5xl mx-auto;
}

.text-cell-view :deep(.file-view-btn),
.text-cell-view :deep(.file-download-btn),
.text-cell-editor :deep(.file-view-btn),
.text-cell-editor :deep(.file-download-btn) {
  @apply px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors text-sm font-medium flex-shrink-0 shadow-sm hover:shadow;
  text-decoration: none;
  cursor: pointer;
  border: none;
}

.text-cell-view :deep(.file-view-btn),
.text-cell-editor :deep(.file-view-btn) {
  @apply bg-green-500 hover:bg-green-600;
}

/* 紧凑模式样式 */
.text-cell-view.compact-content,
.compact-content {
  max-height: 400px !important;
  overflow: hidden !important;
  position: relative;
}

.text-cell-view.compact-content::after,
.compact-content::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0), rgba(255, 255, 255, 0.95));
  pointer-events: none;
  z-index: 1;
}

.text-cell-view.expanded-content,
.expanded-content {
  max-height: none !important;
}

/* 编辑器紧凑模式样式 */
.compact-editor-wrapper {
  position: relative;
}

.compact-editor-wrapper::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0), rgba(255, 255, 255, 0.95));
  pointer-events: none;
  z-index: 10;
}

.expanded-editor-wrapper {
  max-height: none;
}

/* 确保编辑器内容在紧凑模式下可以滚动 */
.compact-editor-wrapper :deep(.tiptap-editor) {
  max-height: 400px;
  overflow: hidden;
  position: relative;
}

.compact-editor-wrapper :deep(.tiptap-editor .editor-content) {
  max-height: calc(400px - 60px); /* 减去工具栏高度 */
  overflow-y: auto;
}

.compact-editor-wrapper :deep(.markdown-editor) {
  max-height: 400px;
  overflow: hidden;
}

.compact-editor-wrapper :deep(.markdown-editor .editor-content) {
  max-height: calc(400px - 50px); /* 减去工具栏高度 */
  overflow-y: auto;
}
</style>


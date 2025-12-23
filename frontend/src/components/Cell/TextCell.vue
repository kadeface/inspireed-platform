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
    
    <!-- 非编辑模式且不可编辑：纯预览模式 -->
    <template v-if="!editable">
      <div 
        v-if="sanitizedHtml" 
        class="text-cell-view"
        :class="{
          'compact-content': compactMode && !isExpanded,
          'expanded-content': compactMode && isExpanded
        }"
        v-html="sanitizedHtml"
      ></div>
      
      <!-- 预览模式下的展开/折叠按钮 -->
      <div 
        v-if="compactMode && sanitizedHtml" 
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
    </template>
    
    <!-- 可编辑模式：编辑器容器 -->
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
  
  // 过滤占位符文本：在非编辑模式下，移除占位符文本
  if (!props.editable && html) {
    // 定义占位符文本
    const placeholderTexts = [
      '在此输入文本内容...',
      'Enter text content here...'
    ]
    
    // 先检查是否有图片或其他实际内容
    const hasImage = /<img[^>]*>/i.test(html)
    const hasFile = /<a[^>]*class="file-[^"]*"[^>]*>/i.test(html)
    const hasOtherContent = /<(?:h[1-6]|ul|ol|li|blockquote|code|pre|table|div|span)[^>]*>/i.test(html)
    
    // 如果有实际内容（图片、文件等），移除占位符文本但保留实际内容
    if (hasImage || hasFile || hasOtherContent) {
      // 从HTML中移除占位符文本
      placeholderTexts.forEach(placeholder => {
        // 转义占位符文本中的特殊字符
        const escapedPlaceholder = placeholder.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
        
        // 匹配并移除占位符文本（无论它在什么位置）
        // 例如：<p>在此输入文本内容...</p> 或 <p>图片 <img> 在此输入文本内容...</p>
        const placeholderPattern = new RegExp(escapedPlaceholder, 'gi')
        html = html.replace(placeholderPattern, '')
      })
      
      // 清理可能产生的只包含空白字符的p标签
      html = html.replace(/<p[^>]*>\s*<\/p>/gi, '')
      
      // 清理p标签开头或结尾的多余空白
      html = html.replace(/(<p[^>]*>)\s+/g, '$1')
      html = html.replace(/\s+(<\/p>)/g, '$1')
    } else {
      // 如果只有占位符文本，检查是否完全是占位符
      const textContent = html.replace(/<[^>]*>/g, '').trim()
      
      // 如果内容只是占位符，返回空字符串
      if (placeholderTexts.some(placeholder => {
        return textContent === placeholder || html.trim() === `<p>${placeholder}</p>` || html.trim() === placeholder
      })) {
        return ''
      }
    }
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
        
        // 如果是纯文件名（没有路径，只有文件名），假设是资源文件
        // 例如：9ffa58aa-610a-4a2d-b640-65e0d5be2d41.png
        if (!src.startsWith('/') && !src.startsWith('http://') && !src.startsWith('https://') && !src.startsWith('blob:')) {
          // 检查是否看起来像一个文件名（包含扩展名）
          if (/\.(png|jpe?g|gif|webp|svg|mp4|pdf|docx?|xlsx?|pptx?)$/i.test(src)) {
            newSrc = `${baseURL}/uploads/resources/${src}`
            const newSrcAttr = ` src=${quote}${newSrc}${quote}`
            return match.replace(srcMatch[0], newSrcAttr)
          }
        }
        
        // 如果是完整URL（http/https），检查是否需要替换为当前服务器地址
        if (src.startsWith('http://') || src.startsWith('https://')) {
          try {
            const url = new URL(src)
            
            // 如果URL指向的是资源路径 (/uploads/)，统一替换为当前服务器地址
            // 这样可以确保无论数据来自哪个环境（localhost、不同IP等），都能在当前环境正确显示
            if (url.pathname.startsWith('/uploads/')) {
              const path = url.pathname + (url.search || '') + (url.hash || '')
              newSrc = `${baseURL}${path}`
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
    
    // URL处理完成后，再次去重：移除重复的图片（相同的src或相同的文件名）
    // 使用 matchAll 方法更可靠地收集所有图片
    const imageMatches: Array<{ match: string; normalizedSrc: string; filename: string; startIndex: number; endIndex: number; originalSrc: string; resourcePath: string; resourceId: string }> = []
    
    // 收集所有图片及其标准化src和位置信息
    const imgRegex = /<img([^>]*?)>/gi
    const allMatches = Array.from(html.matchAll(imgRegex))
    
    allMatches.forEach((match) => {
      const fullMatch = match[0]
      const attrs = match[1]
      const startIndex = match.index!
      const endIndex = startIndex + fullMatch.length
      
      const srcMatch = attrs.match(/\ssrc\s*=\s*(["'])([^"']+)\1/i) || 
                       attrs.match(/\ssrc\s*=\s*([^\s>]+)/i) ||
                       attrs.match(/src\s*=\s*(["'])([^"']+)\1/i) ||
                       attrs.match(/src\s*=\s*([^\s>]+)/i)
      if (srcMatch) {
        let src = srcMatch[2] || srcMatch[1]
        const originalSrc = src
        
        // 标准化src用于比较（移除查询参数和hash）
        let normalizedSrc = src.split('?')[0].split('#')[0].toLowerCase()
        // 提取资源路径用于比较（移除协议、域名和端口，只保留路径）
        let resourcePath = normalizedSrc
        let resourceId = '' // 用于提取资源ID（如UUID）
        
        try {
          if (normalizedSrc.startsWith('http://') || normalizedSrc.startsWith('https://')) {
            const url = new URL(normalizedSrc)
            resourcePath = url.pathname.toLowerCase()
            normalizedSrc = url.pathname.toLowerCase()
          } else if (normalizedSrc.startsWith('/')) {
            // 已经是路径，直接使用
            resourcePath = normalizedSrc.toLowerCase()
            normalizedSrc = normalizedSrc.toLowerCase()
          } else {
            // 尝试提取路径部分
            resourcePath = normalizedSrc.replace(/^https?:\/\/[^\/]+/i, '').toLowerCase()
            if (!resourcePath.startsWith('/')) {
              resourcePath = '/' + resourcePath
            }
          }
          
          // 尝试从路径中提取资源ID（通常是UUID格式）
          // 匹配 /uploads/resources/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.扩展名
          const resourceIdMatch = resourcePath.match(/\/uploads\/resources\/([a-f0-9\-]{36})/i)
          if (resourceIdMatch) {
            resourceId = resourceIdMatch[1].toLowerCase()
          }
        } catch {
          // URL解析失败，使用原始路径
          resourcePath = normalizedSrc.replace(/^https?:\/\/[^\/]+/i, '').toLowerCase()
          if (!resourcePath.startsWith('/')) {
            resourcePath = '/' + resourcePath
          }
          normalizedSrc = resourcePath
          
          // 尝试提取资源ID
          const resourceIdMatch = resourcePath.match(/\/uploads\/resources\/([a-f0-9\-]{36})/i)
          if (resourceIdMatch) {
            resourceId = resourceIdMatch[1].toLowerCase()
          }
        }
        
        // 提取文件名用于比较
        const filename = normalizedSrc.split('/').pop() || ''
        
        imageMatches.push({ 
          match: fullMatch, 
          normalizedSrc: resourcePath, // 使用resourcePath作为标准化src
          filename, 
          startIndex, 
          endIndex,
          originalSrc,
          resourcePath,
          resourceId
        })
      }
    })
    
    // 按位置从前往后排序，标记哪些是重复的（保留第一个出现的）
    const seenPaths = new Set<string>()
    const seenFilenames = new Set<string>()
    const seenResourceIds = new Set<string>()
    const duplicatesToRemove: Array<{ startIndex: number; endIndex: number }> = []
    
    imageMatches.forEach(({ normalizedSrc, filename, startIndex, endIndex, resourcePath, resourceId }) => {
      // 检查是否已经见过相同的路径、文件名或资源ID
      // 优先使用资源ID进行比较（最准确），其次是资源路径，最后是文件名
      const isDuplicate = 
        (resourceId && resourceId.length > 0 && seenResourceIds.has(resourceId)) ||
        seenPaths.has(resourcePath) || 
        seenPaths.has(normalizedSrc) ||
        (filename && filename.length > 0 && seenFilenames.has(filename))
      
      if (isDuplicate) {
        // 标记为需要移除
        duplicatesToRemove.push({ startIndex, endIndex })
      } else {
        // 记录这个图片（保留第一个出现的）
        if (resourceId && resourceId.length > 0) {
          seenResourceIds.add(resourceId)
        }
        seenPaths.add(resourcePath)
        seenPaths.add(normalizedSrc)
        if (filename && filename.length > 0 && filename !== resourcePath) {
          seenFilenames.add(filename)
        }
      }
    })
    
    // 按位置从后往前排序，然后移除重复的图片（这样不会影响前面的索引）
    duplicatesToRemove.sort((a, b) => b.startIndex - a.startIndex)
    duplicatesToRemove.forEach(({ startIndex, endIndex }) => {
      html = html.substring(0, startIndex) + html.substring(endIndex)
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
  
  // 安全网：在DOMPurify之后，使用更精确的正则匹配HTML标签中的src属性
  // 匹配所有指向 /uploads/ 路径的完整URL，无论主机名是什么，都替换为当前服务器地址
  sanitized = sanitized.replace(/src\s*=\s*(["'])(https?:\/\/[^"']+\/uploads\/[^"']+)\1/gi, (match, quote, url) => {
    try {
      const urlObj = new URL(url)
      if (urlObj.pathname.startsWith('/uploads/')) {
        const path = urlObj.pathname + (urlObj.search || '') + (urlObj.hash || '')
        return `src=${quote}${baseURL}${path}${quote}`
      }
    } catch (e) {
      // URL解析失败，尝试直接提取路径
      const pathMatch = url.match(/\/uploads\/[^"']+/)
      if (pathMatch) {
        return `src=${quote}${baseURL}${pathMatch[0]}${quote}`
      }
    }
    return match
  })
  
  // 额外安全网：直接替换HTML字符串中所有指向 /uploads/ 的完整URL
  // 这样可以确保无论原始URL的主机名是什么（localhost、不同IP等），都替换为当前服务器地址
  sanitized = sanitized.replace(/https?:\/\/[^\s"'>]+\/uploads\/[^\s"'>]+/gi, (match) => {
    try {
      const urlObj = new URL(match)
      if (urlObj.pathname.startsWith('/uploads/')) {
        const path = urlObj.pathname + (urlObj.search || '') + (urlObj.hash || '')
        return baseURL + path
      }
    } catch (e) {
      // URL解析失败，尝试直接提取路径
      const pathMatch = match.match(/\/uploads\/[^\s"'>]+/)
      if (pathMatch) {
        return baseURL + pathMatch[0]
      }
    }
    return match
  })
  
  // 修复双斜杠问题（如果baseURL以/结尾，路径也以/开头）
  // 转义baseURL中的特殊字符用于正则表达式
  const escapedBaseURL = baseURL.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  sanitized = sanitized.replace(new RegExp(escapedBaseURL + '//+', 'g'), baseURL + '/')
  
  // 检查处理后的HTML（仅在开发环境或发现问题时输出日志）
  const originalHasImg = html.includes('<img')
  const sanitizedHasImg = sanitized.includes('<img')
  if (originalHasImg && !sanitizedHasImg) {
    // 图片标签被过滤，静默处理
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
    // 处理图片语法 ![alt](url) - 必须在链接之前处理，因为图片和链接语法相似
    result = result.replace(
      /!\[([^\]]*)\]\((https?:\/\/[^\s)]+|\/[^\s)]+|[^\s)]+)\)/g,
      (_match, alt, url) => {
        // 规范化图片URL（在转换为HTML之前）
        const baseURL = getServerBaseUrl()
        let normalizedUrl = url
        // 如果是完整URL且指向资源路径，统一替换为当前服务器地址
        if (url.startsWith('http://') || url.startsWith('https://')) {
          try {
            const urlObj = new URL(url)
            // 如果URL指向的是资源路径 (/uploads/)，统一替换为当前服务器地址
            // 这样可以确保无论数据来自哪个环境，都能在当前环境正确显示
            if (urlObj.pathname.startsWith('/uploads/')) {
              const path = urlObj.pathname + (urlObj.search || '') + (urlObj.hash || '')
              normalizedUrl = `${baseURL}${path}`
            }
          } catch {
            // URL解析失败，使用原URL
          }
        } else if (url.startsWith('/')) {
          // 相对路径，转换为完整URL
          normalizedUrl = `${baseURL}${url}`
        } else if (!url.startsWith('/') && !url.startsWith('http://') && !url.startsWith('https://')) {
          // 纯文件名，假设是资源文件
          if (/\.(png|jpe?g|gif|webp|svg|mp4|pdf|docx?|xlsx?|pptx?)$/i.test(url)) {
            normalizedUrl = `${baseURL}/uploads/resources/${url}`
          }
        }
        return `<img src="${normalizedUrl}" alt="${alt}" />`
      }
    )
    // 处理链接语法 [text](url)
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
        let src = element.getAttribute('src') || ''
        const alt = element.getAttribute('alt') || ''
        // 规范化图片URL，确保localhost和不同IP地址的URL都被替换为当前服务器地址
        if (src && !src.startsWith('blob:') && !src.startsWith('data:')) {
          const baseURL = getServerBaseUrl()
          // 如果是完整URL且指向资源路径，统一替换为当前服务器地址
          if (src.startsWith('http://') || src.startsWith('https://')) {
            try {
              const urlObj = new URL(src)
              if (urlObj.pathname.startsWith('/uploads/')) {
                const path = urlObj.pathname + (urlObj.search || '') + (urlObj.hash || '')
                src = `${baseURL}${path}`
              }
            } catch {
              // URL解析失败，使用原URL
            }
          } else if (src.startsWith('/')) {
            // 相对路径，转换为完整URL
            src = `${baseURL}${src}`
          } else if (!src.startsWith('/') && !src.startsWith('http://') && !src.startsWith('https://')) {
            // 纯文件名，假设是资源文件
            if (/\.(png|jpe?g|gif|webp|svg|mp4|pdf|docx?|xlsx?|pptx?)$/i.test(src)) {
              src = `${baseURL}/uploads/resources/${src}`
            }
          }
        }
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


<!-- eslint-disable vue/no-mutating-props -->
<template>
  <div class="text-cell cell-container" :data-cell-id="cell.id">
    <div v-if="!isEditing && !editable" class="text-cell-view" v-html="sanitizedHtml"></div>
    
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
      
      <TipTapEditor
        v-if="isEditing"
        :content="cell.content.html"
        @update="handleContentUpdate"
      />
      <div v-else class="prose max-w-none" v-html="sanitizedHtml"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
/* eslint-disable vue/no-mutating-props */
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import type { TextCell as TextCellType } from '../../types/cell'
import TipTapEditor from '../Editor/TipTapEditor.vue'
import DOMPurify from 'dompurify'
import { getServerBaseUrl } from '@/utils/url'

interface Props {
  cell: TextCellType
  editable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
})

const emit = defineEmits<{
  update: [cell: TextCellType]
}>()

const isEditing = ref(props.editable)
const tempContent = ref(props.cell.content.html)

const sanitizedHtml = computed(() => {
  let html = props.cell.content.html || ''
  
  // 处理图片URL：将相对路径转换为绝对路径
  if (html) {
    const baseURL = getServerBaseUrl()
    
    // 先检查是否有图片标签
    const hasImgTags = /<img\s+[^>]*>/gi.test(html)
    if (hasImgTags) {
      console.log('🖼️ TextCell检测到图片标签，开始处理:', {
        cellId: props.cell.id,
        baseURL,
        htmlLength: html.length,
        htmlPreview: html.substring(0, 500)
      })
    }
    
    // 匹配所有img标签，处理src属性
    // 使用更宽松的正则表达式，确保能匹配到所有img标签
    html = html.replace(/<img([^>]*?)>/gi, (match, attrs) => {
      console.log('🖼️ 处理img标签:', { match, attrs, 完整标签: match })
      // 提取src属性值（支持单引号、双引号，以及无引号的情况）
      const srcMatch = attrs.match(/\ssrc\s*=\s*(["'])([^"']+)\1/i) || 
                       attrs.match(/\ssrc\s*=\s*([^\s>]+)/i) ||
                       attrs.match(/src\s*=\s*(["'])([^"']+)\1/i) ||
                       attrs.match(/src\s*=\s*([^\s>]+)/i)
      if (srcMatch) {
        console.log('🖼️ 找到src属性:', srcMatch)
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
            newSrc = `${baseURL}${path}`
            // 验证文件名是否一致
            const originalFilename = url.pathname.split('/').pop()
            const newFilename = newSrc.split('/').pop()?.split('?')[0]
            if (originalFilename && newFilename && originalFilename !== newFilename) {
              console.error('❌ localhost URL转换时文件名不一致！', {
                原始URL: src,
                转换后URL: newSrc,
                原始文件名: originalFilename,
                新文件名: newFilename
              })
            } else {
              console.log('✅ localhost URL转换成功:', {
                原始URL: src,
                转换后URL: newSrc,
                文件名: newFilename || originalFilename
              })
            }
          } catch (e) {
            // 如果URL解析失败，尝试直接替换localhost部分
            console.warn('⚠️ URL解析失败，使用字符串替换:', e)
            const originalFilename = src.split('/').pop()?.split('?')[0]
            newSrc = src.replace(/https?:\/\/localhost(:\d+)?/, baseURL)
              .replace(/https?:\/\/127\.0\.0\.1(:\d+)?/, baseURL)
            const newFilename = newSrc.split('/').pop()?.split('?')[0]
            if (originalFilename && newFilename && originalFilename !== newFilename) {
              console.error('❌ localhost URL替换时文件名不一致！', {
                原始URL: src,
                转换后URL: newSrc,
                原始文件名: originalFilename,
                新文件名: newFilename
              })
            } else {
              console.log('✅ localhost URL替换成功:', {
                原始URL: src,
                转换后URL: newSrc,
                文件名: newFilename || originalFilename
              })
            }
          }
        }
        // 如果已经是完整URL（http/https），且不包含localhost，不需要处理
        else if (src.startsWith('http://') || src.startsWith('https://')) {
          console.log('🖼️ 完整URL（非localhost），不处理:', src)
          return match
        }
        // 如果是相对路径（以/开头但不是//），转换为绝对URL
        else if (src.startsWith('/') && !src.startsWith('//')) {
          newSrc = `${baseURL}${src}`
          console.log('🖼️ 相对路径转换:', { 原始: src, 转换后: newSrc })
        }
        // 如果是其他相对路径，也转换为绝对URL
        else if (!src.startsWith('//')) {
          newSrc = `${baseURL}/${src.startsWith('/') ? src.slice(1) : src}`
          console.log('🖼️ 其他相对路径转换:', { 原始: src, 转换后: newSrc })
        }
        
        // 重要：如果已经处理了localhost，确保后续逻辑不会覆盖newSrc
        // 但这里newSrc已经在上面设置好了，所以不需要额外处理
        
        // 如果URL被修改，替换原src值
        if (newSrc !== src) {
          // 提取文件名用于验证
          const originalFilename = src.split('/').pop()?.split('?')[0] // 移除查询参数
          const newFilename = newSrc.split('/').pop()?.split('?')[0] // 移除查询参数
          
          // 验证文件名是否一致
          if (originalFilename && newFilename && originalFilename !== newFilename) {
            console.error('❌ 文件名不一致！', {
              原始URL: src,
              转换后URL: newSrc,
              原始文件名: originalFilename,
              新文件名: newFilename,
              baseURL
            })
          } else {
            // 调试日志
            console.log('🖼️ 图片URL转换:', { 
              原始: src, 
              转换后: newSrc, 
              baseURL,
              文件名: newFilename || originalFilename,
              文件名一致: originalFilename === newFilename
            })
          }
          
          const originalSrcAttr = srcMatch[0]
          const newSrcAttr = ` src=${quote}${newSrc}${quote}`
          return match.replace(originalSrcAttr, newSrcAttr)
        } else {
          // 即使没有修改，也输出日志以便排查
          const filename = src.split('/').pop()?.split('?')[0]
          console.log('🖼️ 图片URL未修改:', { 
            src,
            文件名: filename,
            baseURL
          })
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
  
  const sanitized = DOMPurify.sanitize(html, config)
  
  // 调试：检查处理后的HTML
  const originalHasImg = html.includes('<img')
  const sanitizedHasImg = sanitized.includes('<img')
  if (originalHasImg) {
    // 检查是否有localhost URL
    const hasLocalhost = /localhost|127\.0\.0\.1/.test(sanitized)
    if (hasLocalhost) {
      console.error('❌ 处理后的HTML仍然包含localhost URL！', {
        cellId: props.cell.id,
        htmlPreview: html.substring(0, 300),
        sanitizedPreview: sanitized.substring(0, 300),
        baseURL: getServerBaseUrl()
      })
    } else {
      console.log('✅ HTML处理成功，已移除localhost URL')
    }
    
    if (!sanitizedHasImg) {
      console.warn('⚠️ 图片标签被DOMPurify过滤掉了', {
        original: html.substring(0, 200),
        sanitized: sanitized.substring(0, 200),
      })
    }
  }
  
  return sanitized
})

function startEdit() {
  isEditing.value = true
  tempContent.value = props.cell.content.html
}

function saveEdit() {
  isEditing.value = false
  handleUpdate()
}

function cancelEdit() {
  isEditing.value = false
  tempContent.value = props.cell.content.html
}

function handleContentUpdate(html: string) {
  tempContent.value = html
  props.cell.content.html = html
}

function handleUpdate() {
  emit('update', props.cell)
}

// 监听图片加载错误
function handleImageError(event: Event) {
  const img = event.target as HTMLImageElement
  console.error('❌ 图片加载失败:', {
    src: img.src,
    cellId: props.cell.id,
    baseURL: getServerBaseUrl(),
    文件名: img.src.split('/').pop(),
    完整URL: img.src
  })
}

onMounted(async () => {
  // 等待DOM渲染完成后再添加事件监听
  await nextTick()
  
  // 在组件挂载后，为所有图片添加错误监听
  const cellElement = document.querySelector(`[data-cell-id="${props.cell.id}"]`)
  if (cellElement) {
    const images = cellElement.querySelectorAll('img')
    console.log('🖼️ TextCell挂载，找到图片数量:', images.length, 'cellId:', props.cell.id)
    images.forEach(img => {
      console.log('🖼️ 为图片添加错误监听:', img.src)
      img.addEventListener('error', handleImageError)
      // 也监听load事件，确认图片加载成功
      img.addEventListener('load', () => {
        console.log('✅ 图片加载成功:', img.src)
      })
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
</style>


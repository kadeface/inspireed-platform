<template>
  <div class="tiptap-editor">
    <div v-if="editor" class="menu-bar">
      <button
        @click="editor.chain().focus().toggleBold().run()"
        :class="{ 'is-active': editor.isActive('bold') }"
        class="menu-btn"
      >
        <strong>B</strong>
      </button>
      <button
        @click="editor.chain().focus().toggleItalic().run()"
        :class="{ 'is-active': editor.isActive('italic') }"
        class="menu-btn"
      >
        <em>I</em>
      </button>
      <button
        @click="editor.chain().focus().toggleStrike().run()"
        :class="{ 'is-active': editor.isActive('strike') }"
        class="menu-btn"
      >
        <s>S</s>
      </button>
      <button
        @click="editor.chain().focus().toggleHeading({ level: 1 }).run()"
        :class="{ 'is-active': editor.isActive('heading', { level: 1 }) }"
        class="menu-btn"
      >
        H1
      </button>
      <button
        @click="editor.chain().focus().toggleHeading({ level: 2 }).run()"
        :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }"
        class="menu-btn"
      >
        H2
      </button>
      <button
        @click="editor.chain().focus().toggleBulletList().run()"
        :class="{ 'is-active': editor.isActive('bulletList') }"
        class="menu-btn"
      >
        • List
      </button>
      <button
        @click="editor.chain().focus().toggleOrderedList().run()"
        :class="{ 'is-active': editor.isActive('orderedList') }"
        class="menu-btn"
      >
        1. List
      </button>
      <button
        @click="editor.chain().focus().toggleCodeBlock().run()"
        :class="{ 'is-active': editor.isActive('codeBlock') }"
        class="menu-btn"
      >
        &lt;/&gt;
      </button>
      <button @click="triggerImageUpload" class="menu-btn">🖼️ Image</button>
      <div class="relative inline-block">
        <button 
          @click.stop="toggleFileMenu" 
          class="menu-btn"
          type="button"
        >
          📎 File
        </button>
        <!-- 文件菜单下拉 -->
        <Transition name="dropdown">
          <div
            v-if="showFileMenu"
            v-click-outside="closeFileMenu"
            class="absolute top-full left-0 mt-1 bg-white border border-gray-300 rounded-lg shadow-lg z-[100] min-w-[200px]"
            @click.stop
          >
            <button
              @click.stop="triggerFileUpload"
              type="button"
              class="w-full text-left px-4 py-2 hover:bg-gray-100 flex items-center gap-2 text-sm"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              上传本地文件
            </button>
            <button
              @click.stop="openLibraryPicker"
              type="button"
              class="w-full text-left px-4 py-2 hover:bg-gray-100 flex items-center gap-2 text-sm"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              从资源库选择
            </button>
          </div>
        </Transition>
      </div>
      <input
        ref="imageInput"
        type="file"
        accept="image/*"
        @change="handleImageUpload"
        style="display: none"
      />
      <input
        ref="fileInput"
        type="file"
        @change="handleFileUpload"
        style="display: none"
      />
    </div>
    <editor-content :editor="editor" class="editor-content" />
    <div v-if="isUploadingImage || isUploadingFile" class="upload-status">
      <p class="text-sm text-gray-600">上传中... {{ uploadProgress }}%</p>
    </div>

    <!-- 资源库选择器模态框 -->
    <Teleport to="body">
      <div
        v-if="showLibraryPicker"
        class="fixed inset-0 z-50 overflow-y-auto"
        @click.self="showLibraryPicker = false"
      >
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75" @click="showLibraryPicker = false"></div>
        <div class="flex min-h-full items-center justify-center p-4">
          <div class="relative bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div class="px-6 pt-6 pb-4 border-b flex items-center justify-between">
              <h3 class="text-xl font-semibold text-gray-900">从资源库选择资源</h3>
              <button @click="showLibraryPicker = false" class="text-gray-400 hover:text-gray-500">
                <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="flex-1 overflow-y-auto p-6">
              <AssetPicker
                ref="assetPicker"
                @select="handleLibraryAssetSelect"
              />
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'
import Link from '@tiptap/extension-link'
import { watch, onBeforeUnmount, ref } from 'vue'
import api from '../../services/api'
import { getServerBaseUrl } from '@/utils/url'
import AssetPicker from '@/components/Library/AssetPicker.vue'
import type { LibraryAssetSummary } from '@/types/library'

interface Props {
  content: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  update: [html: string]
}>()

// 标准化HTML内容中的图片URL（将IP地址替换为当前服务器地址）
function normalizeImageUrls(html: string): string {
  if (!html) return html
  
  const baseURL = getServerBaseUrl()
  
  // 处理图片URL：将IP地址或不同主机的URL替换为当前服务器地址
  html = html.replace(/<img\s+([^>]*?)>/gi, (match, attrs) => {
    const srcMatch = attrs.match(/\ssrc\s*=\s*(["'])([^"']+)\1/i) || attrs.match(/\ssrc\s*=\s*([^\s>]+)/i)
    if (srcMatch) {
      const quote = srcMatch[1] || '"'
      let src = srcMatch[2] || srcMatch[1]
      
      // 如果是blob URL或data URL，不需要处理
      if (src.startsWith('blob:') || src.startsWith('data:')) {
        return match
      }
      
      // 如果是相对路径，转换为完整URL以便在编辑器中显示
      if (src.startsWith('/') && !src.startsWith('//')) {
        const fullUrl = `${baseURL}${src}`
        const newSrcAttr = ` src=${quote}${fullUrl}${quote}`
        return match.replace(srcMatch[0], newSrcAttr)
      }
      
      // 如果是完整URL，检查是否需要替换
      if (src.startsWith('http://') || src.startsWith('https://')) {
        try {
          const url = new URL(src)
          // 如果是资源路径（/uploads/resources/），检查主机名
          if (url.pathname.startsWith('/uploads/resources/')) {
            const isIPAddress = /^(\d{1,3}\.){3}\d{1,3}$/.test(url.hostname)
            const isLocalhost = url.hostname === 'localhost' || url.hostname === '127.0.0.1'
            const currentHost = window.location.hostname
            const isDifferentHost = url.hostname !== currentHost && !isLocalhost
            
            // 如果是IP地址或不同的主机名，替换为当前服务器地址
            if (isIPAddress || isDifferentHost) {
              const path = url.pathname + (url.search || '') + (url.hash || '')
              const newUrl = `${baseURL}${path}`
              const newSrcAttr = ` src=${quote}${newUrl}${quote}`
              return match.replace(srcMatch[0], newSrcAttr)
            }
          }
        } catch {
          // URL解析失败，保持原样
        }
      }
    }
    return match
  })
  
  return html
}

const editor = useEditor({
  content: normalizeImageUrls(props.content),
  extensions: [
    StarterKit,
    Image.configure({
      inline: true,
      allowBase64: true,
    }),
    Link.configure({
      openOnClick: false,
    }),
  ],
  onUpdate: ({ editor }) => {
    // 在保存到数据库之前，将完整URL（包含localhost和IP地址）转换为相对路径
    let html = editor.getHTML()
    const baseURL = getServerBaseUrl()
    
    // 替换所有包含localhost、127.0.0.1或IP地址的图片URL为相对路径
    html = html.replace(/<img\s+([^>]*?)>/gi, (match, attrs) => {
      const srcMatch = attrs.match(/\ssrc\s*=\s*(["'])([^"']+)\1/i) || attrs.match(/\ssrc\s*=\s*([^\s>]+)/i)
      if (srcMatch) {
        const quote = srcMatch[1] || '"'
        let src = srcMatch[2] || srcMatch[1]
        
        // 如果是blob URL或data URL，不需要处理
        if (src.startsWith('blob:') || src.startsWith('data:')) {
          return match
        }
        
        // 如果URL包含localhost、127.0.0.1或IP地址，提取相对路径
        if (src.includes('localhost') || src.includes('127.0.0.1') || /https?:\/\/(\d{1,3}\.){3}\d{1,3}/.test(src)) {
          try {
            const url = new URL(src)
            // 如果是资源路径（/uploads/resources/），提取相对路径
            if (url.pathname.startsWith('/uploads/resources/')) {
              const relativePath = url.pathname + (url.search || '') + (url.hash || '')
              const newSrcAttr = ` src=${quote}${relativePath}${quote}`
              return match.replace(srcMatch[0], newSrcAttr)
            }
            // 如果是其他路径，也提取相对路径
            const relativePath = url.pathname + (url.search || '') + (url.hash || '')
            const newSrcAttr = ` src=${quote}${relativePath}${quote}`
            return match.replace(srcMatch[0], newSrcAttr)
          } catch {
            // URL解析失败，尝试直接提取路径
            const pathMatch = src.match(/\/uploads\/[^"'\s]+/)
            if (pathMatch) {
              const newSrcAttr = ` src=${quote}${pathMatch[0]}${quote}`
              return match.replace(srcMatch[0], newSrcAttr)
            }
          }
        }
        // 如果URL是完整URL但指向当前服务器，也转换为相对路径
        else if (src.startsWith('http://') || src.startsWith('https://')) {
          try {
            const url = new URL(src)
            // 检查是否是资源路径
            if (url.pathname.startsWith('/uploads/resources/')) {
              // 检查是否是当前服务器地址（通过比较路径部分）
              // 如果是，转换为相对路径
              const relativePath = url.pathname + (url.search || '') + (url.hash || '')
              const newSrcAttr = ` src=${quote}${relativePath}${quote}`
              return match.replace(srcMatch[0], newSrcAttr)
            }
          } catch {
            // URL解析失败，保持原样
          }
        }
      }
      return match
    })
    
    // 替换PDF和文件组件中的完整URL为相对路径
    html = html.replace(/<div\s+class="(pdf|file)-attachment[^"]*"[^>]*>/gi, (match) => {
      // 提取data-pdf-url或data-file-url属性
      const urlMatch = match.match(/data-(pdf|file)-url\s*=\s*(["'])([^"']+)\2/i)
      if (urlMatch) {
        const quote = urlMatch[2]
        let url = urlMatch[3]
        
        // 如果URL包含完整地址（localhost、127.0.0.1或IP地址），提取相对路径
        if (url.includes('localhost') || url.includes('127.0.0.1') || /https?:\/\/(\d{1,3}\.){3}\d{1,3}/.test(url) || url.startsWith('http')) {
          try {
            const urlObj = new URL(url)
            const relativePath = urlObj.pathname
            const newUrlAttr = `data-${urlMatch[1]}-url=${quote}${relativePath}${quote}`
            return match.replace(urlMatch[0], newUrlAttr)
          } catch {
            // URL解析失败，尝试直接提取路径
            const pathMatch = url.match(/\/uploads\/[^"'\s]+/)
            if (pathMatch) {
              const newUrlAttr = `data-${urlMatch[1]}-url=${quote}${pathMatch[0]}${quote}`
              return match.replace(urlMatch[0], newUrlAttr)
            }
          }
        }
      }
      return match
    })
    
    // 替换PDF查看按钮中的data-pdf-view-url属性为相对路径
    html = html.replace(/data-pdf-view-url\s*=\s*(["'])([^"']+)\1/gi, (match, quote, url) => {
      if (url.includes('localhost') || url.includes('127.0.0.1') || /https?:\/\/(\d{1,3}\.){3}\d{1,3}/.test(url) || url.startsWith('http')) {
        try {
          const urlObj = new URL(url)
          const relativePath = urlObj.pathname
          return `data-pdf-view-url=${quote}${relativePath}${quote}`
        } catch {
          const pathMatch = url.match(/\/uploads\/[^"'\s]+/)
          if (pathMatch) {
            return `data-pdf-view-url=${quote}${pathMatch[0]}${quote}`
          }
        }
      }
      return match
    })
    
    // 替换文件下载链接中的href为相对路径
    html = html.replace(/href\s*=\s*(["'])([^"']+)\1[^>]*download/gi, (match, quote, url) => {
      if (url.includes('localhost') || url.includes('127.0.0.1') || /https?:\/\/(\d{1,3}\.){3}\d{1,3}/.test(url) || url.startsWith('http')) {
        try {
          const urlObj = new URL(url)
          const relativePath = urlObj.pathname
          return `href=${quote}${relativePath}${quote} download`
        } catch {
          const pathMatch = url.match(/\/uploads\/[^"'\s]+/)
          if (pathMatch) {
            return `href=${quote}${pathMatch[0]}${quote} download`
          }
        }
      }
      return match
    })
    
    // 替换data-file-download-url属性为相对路径
    html = html.replace(/data-file-download-url\s*=\s*(["'])([^"']+)\1/gi, (match, quote, url) => {
      if (url.includes('localhost') || url.includes('127.0.0.1') || /https?:\/\/(\d{1,3}\.){3}\d{1,3}/.test(url) || url.startsWith('http')) {
        try {
          const urlObj = new URL(url)
          const relativePath = urlObj.pathname
          return `data-file-download-url=${quote}${relativePath}${quote}`
        } catch {
          const pathMatch = url.match(/\/uploads\/[^"'\s]+/)
          if (pathMatch) {
            return `data-file-download-url=${quote}${pathMatch[0]}${quote}`
          }
        }
      }
      return match
    })
    
    emit('update', html)
  },
  editorProps: {
    attributes: {
      class: 'prose max-w-none focus:outline-none',
    },
  },
})

watch(
  () => props.content,
  (newContent) => {
    if (editor.value && editor.value.getHTML() !== newContent) {
      // 在设置内容之前，标准化图片URL
      const normalizedContent = normalizeImageUrls(newContent)
      editor.value.commands.setContent(normalizedContent, false)
    }
  }
)

const imageInput = ref<HTMLInputElement | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const isUploadingImage = ref(false)
const isUploadingFile = ref(false)
const uploadProgress = ref(0)

// 文件菜单和资源库选择器
const showFileMenu = ref(false)
const showLibraryPicker = ref(false)
const assetPicker = ref<InstanceType<typeof AssetPicker>>()

function triggerImageUpload() {
  // 直接触发文件选择，优先使用本地图片上传
  imageInput.value?.click()
}

function toggleFileMenu() {
  showFileMenu.value = !showFileMenu.value
}

function closeFileMenu() {
  showFileMenu.value = false
}

function triggerFileUpload() {
  closeFileMenu()
  fileInput.value?.click()
}

function openLibraryPicker() {
  closeFileMenu()
  showLibraryPicker.value = true
}

// 添加通过URL插入图片的功能（可以通过右键菜单或其他方式调用）
function addImageByUrl() {
  const url = window.prompt('请输入图片URL:')
  if (url && editor.value) {
    editor.value.chain().focus().setImage({ src: url }).run()
  }
}

async function handleImageUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file || !editor.value) {
    return
  }

  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    alert('请选择图片文件')
    return
  }

  // 验证文件大小（限制为10MB）
  const maxSize = 10 * 1024 * 1024 // 10MB
  if (file.size > maxSize) {
    alert('图片文件大小不能超过10MB')
    return
  }

  isUploadingImage.value = true
  uploadProgress.value = 0

  // 创建临时预览URL
  const tempUrl = URL.createObjectURL(file)
  let tempUrlInserted = false

  try {
    // 先插入临时图片用于预览
    editor.value.chain().focus().setImage({ src: tempUrl }).run()
    tempUrlInserted = true

    // 准备上传到服务器
    const formData = new FormData()
    formData.append('file', file)

    // 上传文件
    const response = await api.post<{
      file_url: string
      file_size: number
      filename: string
    }>('/upload/', formData, {
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        }
      },
      timeout: 300000, // 5分钟超时
    })

    // 使用相对路径保存到数据库（这样学生端可以根据自己的服务器地址动态构建URL）
    // 只保存相对路径，不保存完整的服务器URL
    const imageUrl = response.file_url  // 已经是 /uploads/resources/xxx.png 格式
    
    // 为了在编辑器中显示，需要构建完整的预览URL
    const previewUrl = imageUrl.startsWith('/uploads/') 
      ? `${getServerBaseUrl()}${imageUrl}`
      : imageUrl

    // 更新图片src为相对路径（保存到数据库时使用相对路径）
    // 但在编辑器中显示时使用完整URL以便预览
    if (editor.value) {
      const { state } = editor.value
      const { tr } = state
      let updated = false
      
      // 遍历所有节点，找到使用tempUrl的图片节点并更新
      state.doc.descendants((node, pos) => {
        if (node.type.name === 'image' && node.attrs.src === tempUrl) {
          // 保存相对路径到数据库，但使用完整URL在编辑器中预览
          tr.setNodeMarkup(pos, undefined, {
            ...node.attrs,
            src: previewUrl,  // 编辑器中使用完整URL以便预览
          })
          updated = true
        }
      })
      
      if (updated) {
        editor.value.view.dispatch(tr)
        // 在保存到数据库之前，将完整URL替换为相对路径
        // 通过监听onUpdate事件来处理
      } else {
        // 如果通过节点更新失败，尝试通过HTML替换
        const html = editor.value.getHTML()
        // 使用更全面的正则表达式替换所有可能的blob URL格式
        const blobUrlPattern = new RegExp(tempUrl.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi')
        const updatedHtml = html.replace(blobUrlPattern, previewUrl)
        if (updatedHtml !== html) {
          editor.value.commands.setContent(updatedHtml)
        }
      }
    }

    uploadProgress.value = 100
    
    // 确保替换完成后再清理blob URL
    await new Promise(resolve => setTimeout(resolve, 100))
  } catch (error: any) {
    console.error('图片上传失败:', error)
    alert(error.response?.data?.detail || error.message || '图片上传失败，请稍后重试')
    
    // 移除临时插入的图片
    if (editor.value && tempUrlInserted) {
      const html = editor.value.getHTML()
      // 替换临时URL为空，移除图片
      const updatedHtml = html.replace(new RegExp(`<img[^>]*src=["']${tempUrl.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}["'][^>]*>`, 'gi'), '')
      if (updatedHtml !== html) {
        editor.value.commands.setContent(updatedHtml)
      }
    }
  } finally {
    // 延迟清理临时URL，确保所有替换都已完成
    setTimeout(() => {
      try {
        URL.revokeObjectURL(tempUrl)
      } catch (e) {
        // 忽略清理错误
      }
    }, 500)
    
    isUploadingImage.value = false
    uploadProgress.value = 0
    // 清空文件输入，允许重复选择同一个文件
    if (target) {
      target.value = ''
    }
  }
}

// 文件上传处理（支持所有文件类型，包括PDF）
async function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file || !editor.value) {
    return
  }

  // 验证文件大小（限制为500MB）
  const maxSize = 500 * 1024 * 1024 // 500MB
  if (file.size > maxSize) {
    alert('文件大小不能超过500MB')
    return
  }

  isUploadingFile.value = true
  uploadProgress.value = 0

  try {
    // 准备上传到服务器
    const formData = new FormData()
    formData.append('file', file)

    // 上传文件
    const response = await api.post<{
      file_url: string
      file_size: number
      filename: string
    }>('/upload/', formData, {
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        }
      },
      timeout: 300000, // 5分钟超时
    })

    // 获取相对路径（与图片上传保持一致，api服务已经返回数据对象）
    const fileUrl = response.file_url
    const filename = response.filename || file.name
    
    // 构建下载URL
    const downloadUrl = fileUrl.startsWith('/uploads/') 
      ? `${getServerBaseUrl()}${fileUrl}`
      : fileUrl

    // 获取文件图标和类型
    const fileIcon = getFileIcon(filename)
    const isPDF = filename.toLowerCase().endsWith('.pdf')
    
    // 在编辑器中插入文件下载/查看组件
    // 使用相对路径保存，在查看时动态构建完整URL
    const fileHtml = `
      <div class="file-attachment" data-file-url="${fileUrl}" data-file-filename="${filename}">
        <div class="file-preview-card">
          <div class="file-icon">${fileIcon}</div>
          <div class="file-info">
            <div class="file-filename">${filename}</div>
            <div class="file-size">${formatFileSize(response.file_size)}</div>
          </div>
          <div class="file-actions">
            ${isPDF ? `<button class="file-view-btn" onclick="window.open('${downloadUrl}', '_blank')">查看</button>` : ''}
            <a href="${downloadUrl}" download="${filename}" class="file-download-btn">下载</a>
          </div>
        </div>
      </div>
    `

    // 插入HTML
    editor.value.chain().focus().insertContent(fileHtml).run()

    uploadProgress.value = 100
  } catch (error: any) {
    console.error('文件上传失败:', error)
    alert(error.response?.data?.detail || error.message || '文件上传失败，请稍后重试')
  } finally {
    isUploadingFile.value = false
    uploadProgress.value = 0
    // 清空文件输入
    if (target) {
      target.value = ''
    }
  }
}

// 格式化文件大小
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 根据文件扩展名获取图标
function getFileIcon(filename: string): string {
  const ext = filename.split('.').pop()?.toLowerCase() || ''
  const iconMap: Record<string, string> = {
    'pdf': '📄',
    'doc': '📝',
    'docx': '📝',
    'xls': '📊',
    'xlsx': '📊',
    'ppt': '📊',
    'pptx': '📊',
    'zip': '📦',
    'rar': '📦',
    'txt': '📄',
    'md': '📄',
    'mp4': '🎬',
    'avi': '🎬',
    'mov': '🎬',
  }
  return iconMap[ext] || '📎'
}

// 处理从资源库选择的资源
async function handleLibraryAssetSelect(asset: LibraryAssetSummary | null) {
  if (!asset || !editor.value) {
    showLibraryPicker.value = false
    return
  }

  try {
    const fileUrl = asset.public_url || ''
    const filename = asset.title || '资源文件'
    
    // 根据资源类型处理
    if (asset.asset_type === 'image') {
      // 图片资源：直接插入图片
      const imageUrl = fileUrl.startsWith('/uploads/') 
        ? `${getServerBaseUrl()}${fileUrl}`
        : fileUrl
      editor.value.chain().focus().setImage({ src: imageUrl }).run()
    } else if (asset.asset_type === 'video') {
      // 视频资源：插入视频链接或嵌入代码
      const videoUrl = fileUrl.startsWith('/uploads/') 
        ? `${getServerBaseUrl()}${fileUrl}`
        : fileUrl
      const videoHtml = `
        <div class="video-embed">
          <video controls style="max-width: 100%; height: auto;">
            <source src="${videoUrl}" type="video/mp4">
            您的浏览器不支持视频播放
          </video>
        </div>
      `
      editor.value.chain().focus().insertContent(videoHtml).run()
    } else if (asset.asset_type === 'pdf') {
      // PDF资源：插入PDF查看/下载组件
      const pdfUrl = fileUrl.startsWith('/uploads/') 
        ? `${getServerBaseUrl()}${fileUrl}`
        : fileUrl
      const pdfHtml = `
        <div class="file-attachment pdf-attachment" data-pdf-url="${fileUrl}" data-file-filename="${filename}">
          <div class="file-preview-card">
            <div class="file-icon">📄</div>
            <div class="file-info">
              <div class="file-filename">${filename}</div>
              <div class="file-size">PDF文档</div>
            </div>
            <div class="file-actions">
              <button class="file-view-btn" onclick="window.open('${pdfUrl}', '_blank')">查看</button>
              <a href="${pdfUrl}" download="${filename}" class="file-download-btn">下载</a>
            </div>
          </div>
        </div>
      `
      editor.value.chain().focus().insertContent(pdfHtml).run()
    } else {
      // 其他文件类型：插入文件下载组件
      const downloadUrl = fileUrl.startsWith('/uploads/') 
        ? `${getServerBaseUrl()}${fileUrl}`
        : fileUrl
      const fileIcon = getFileIcon(filename)
      const fileHtml = `
        <div class="file-attachment" data-file-url="${fileUrl}" data-file-filename="${filename}">
          <div class="file-preview-card">
            <div class="file-icon">${fileIcon}</div>
            <div class="file-info">
              <div class="file-filename">${filename}</div>
              <div class="file-size">${asset.size_bytes ? formatFileSize(asset.size_bytes) : ''}</div>
            </div>
            <div class="file-actions">
              <a href="${downloadUrl}" download="${filename}" class="file-download-btn">下载</a>
            </div>
          </div>
        </div>
      `
      editor.value.chain().focus().insertContent(fileHtml).run()
    }
    
    showLibraryPicker.value = false
  } catch (error) {
    console.error('插入资源库资源失败:', error)
    alert('插入资源失败，请重试')
  }
}

// 自定义指令：点击外部关闭菜单
const vClickOutside = {
  mounted(el: HTMLElement & { clickOutsideEvent?: (event: MouseEvent) => void }, binding: any) {
    el.clickOutsideEvent = (event: MouseEvent) => {
      const target = event.target as Node
      if (!(el === target || el.contains(target))) {
        binding.value(event)
      }
    }
    // 使用 nextTick 确保在下一个事件循环中添加监听器，避免立即触发
    setTimeout(() => {
      document.addEventListener('click', el.clickOutsideEvent!, true)
    }, 0)
  },
  unmounted(el: HTMLElement & { clickOutsideEvent?: (event: MouseEvent) => void }) {
    if (el.clickOutsideEvent) {
      document.removeEventListener('click', el.clickOutsideEvent, true)
    }
  },
}

onBeforeUnmount(() => {
  editor.value?.destroy()
})
</script>

<style scoped>
.tiptap-editor {
  @apply border rounded-lg overflow-hidden;
}

.menu-bar {
  @apply flex gap-1 p-2 border-b bg-gray-50 flex-wrap;
}

.menu-btn {
  @apply px-3 py-1 text-sm border rounded hover:bg-gray-200 transition-colors;
}

.menu-btn.is-active {
  @apply bg-blue-500 text-white border-blue-600;
}

.editor-content {
  @apply p-4 min-h-[200px] bg-white;
}

:deep(.ProseMirror) {
  @apply focus:outline-none;
}

:deep(.ProseMirror h1) {
  @apply text-3xl font-bold mt-4 mb-2;
}

:deep(.ProseMirror h2) {
  @apply text-2xl font-bold mt-3 mb-2;
}

:deep(.ProseMirror ul) {
  @apply list-disc pl-6 my-2;
}

:deep(.ProseMirror ol) {
  @apply list-decimal pl-6 my-2;
}

:deep(.ProseMirror code) {
  @apply bg-gray-100 px-1 py-0.5 rounded text-sm font-mono;
}

:deep(.ProseMirror pre) {
  @apply bg-gray-900 text-gray-100 p-4 rounded my-2 overflow-x-auto;
}

:deep(.ProseMirror img) {
  @apply max-w-full h-auto rounded;
}

:deep(.ProseMirror .file-attachment) {
  @apply my-6 border border-gray-300 rounded-lg overflow-hidden bg-white shadow-sm;
}

:deep(.ProseMirror .file-preview-card) {
  @apply flex items-center gap-3 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 transition-all duration-200;
}

:deep(.ProseMirror .file-actions) {
  @apply flex items-center gap-2;
}

:deep(.ProseMirror .pdf-icon),
:deep(.ProseMirror .file-icon) {
  @apply text-3xl flex-shrink-0;
}

:deep(.ProseMirror .pdf-info),
:deep(.ProseMirror .file-info) {
  @apply flex-1 min-w-0;
}

:deep(.ProseMirror .pdf-filename),
:deep(.ProseMirror .file-filename) {
  @apply font-medium text-gray-900 truncate;
}

:deep(.ProseMirror .pdf-size),
:deep(.ProseMirror .file-size) {
  @apply text-sm text-gray-500 mt-1;
}

:deep(.ProseMirror .file-view-btn),
:deep(.ProseMirror .file-download-btn) {
  @apply px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors text-sm font-medium flex-shrink-0 shadow-sm hover:shadow;
  text-decoration: none;
  border: none;
  cursor: pointer;
}

:deep(.ProseMirror .file-view-btn) {
  @apply bg-green-500 hover:bg-green-600;
}

.upload-status {
  @apply px-4 py-2 bg-blue-50 border-t border-blue-200;
}

/* 文件菜单下拉样式 */
.menu-btn {
  position: relative;
}

/* 视频嵌入样式 */
:deep(.ProseMirror .video-embed) {
  @apply my-4;
}

:deep(.ProseMirror .video-embed video) {
  @apply w-full rounded-lg;
}

/* 下拉菜单动画 */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>


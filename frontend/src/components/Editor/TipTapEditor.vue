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
      <input
        ref="imageInput"
        type="file"
        accept="image/*"
        @change="handleImageUpload"
        style="display: none"
      />
    </div>
    <editor-content :editor="editor" class="editor-content" />
    <div v-if="isUploadingImage" class="upload-status">
      <p class="text-sm text-gray-600">上传中... {{ uploadProgress }}%</p>
    </div>
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

interface Props {
  content: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  update: [html: string]
}>()

const editor = useEditor({
  content: props.content,
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
    // 在保存到数据库之前，将完整URL（包含localhost）转换为相对路径
    let html = editor.getHTML()
    
    // 替换所有包含localhost或127.0.0.1的图片URL为相对路径
    html = html.replace(/<img\s+([^>]*?)>/gi, (match, attrs) => {
      const srcMatch = attrs.match(/\ssrc\s*=\s*(["'])([^"']+)\1/i) || attrs.match(/\ssrc\s*=\s*([^\s>]+)/i)
      if (srcMatch) {
        const quote = srcMatch[1] || '"'
        let src = srcMatch[2] || srcMatch[1]
        
        // 如果URL包含localhost或127.0.0.1，提取相对路径
        if (src.includes('localhost') || src.includes('127.0.0.1')) {
          try {
            const url = new URL(src)
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
      editor.value.commands.setContent(newContent, false)
    }
  }
)

const imageInput = ref<HTMLInputElement | null>(null)
const isUploadingImage = ref(false)
const uploadProgress = ref(0)

function triggerImageUpload() {
  // 直接触发文件选择，优先使用本地图片上传
  imageInput.value?.click()
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

.upload-status {
  @apply px-4 py-2 bg-blue-50 border-t border-blue-200;
}
</style>


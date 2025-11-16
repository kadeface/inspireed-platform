<template>
  <div class="markdown-editor">
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <button
          type="button"
          @click="toggleView"
          class="toolbar-btn"
          :title="viewMode === 'split' ? '切换到预览模式' : viewMode === 'preview' ? '切换到编辑模式' : '切换到分屏模式'"
        >
          <svg v-if="viewMode === 'edit'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
          <svg v-else-if="viewMode === 'preview'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
          <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
          </svg>
          <span class="ml-1">{{ viewMode === 'edit' ? '预览' : viewMode === 'preview' ? '编辑' : '分屏' }}</span>
        </button>
      </div>
      <div class="toolbar-right">
        <button
          type="button"
          @click="insertMarkdown('**', '**')"
          class="toolbar-btn"
          title="粗体"
        >
          <strong>B</strong>
        </button>
        <button
          type="button"
          @click="insertMarkdown('*', '*')"
          class="toolbar-btn"
          title="斜体"
        >
          <em>I</em>
        </button>
        <button
          type="button"
          @click="insertMarkdown('`', '`')"
          class="toolbar-btn"
          title="行内代码"
        >
          &lt;/&gt;
        </button>
        <button
          type="button"
          @click="insertMarkdown('- ', '')"
          class="toolbar-btn"
          title="无序列表"
        >
          •
        </button>
        <button
          type="button"
          @click="insertMarkdown('# ', '')"
          class="toolbar-btn"
          title="标题"
        >
          H
        </button>
        <button
          type="button"
          @click="insertMarkdown('```\n', '\n```')"
          class="toolbar-btn"
          title="代码块"
        >
          { }
        </button>
      </div>
    </div>
    <div class="editor-content" :class="viewMode">
      <div v-if="viewMode === 'edit' || viewMode === 'split'" class="editor-pane">
        <textarea
          ref="textareaRef"
          v-model="localValue"
          @input="handleInput"
          @keydown="handleKeydown"
          placeholder="支持 Markdown 格式，使用工具栏快速插入格式..."
          class="markdown-textarea"
        ></textarea>
      </div>
      <div v-if="viewMode === 'preview' || viewMode === 'split'" class="preview-pane">
        <MarkdownPreview :content="localValue" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import MarkdownPreview from '@/components/Common/MarkdownPreview.vue'

interface Props {
  modelValue: string
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '支持 Markdown 格式...',
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const localValue = ref(props.modelValue)
const viewMode = ref<'edit' | 'preview' | 'split'>('edit')
const textareaRef = ref<HTMLTextAreaElement | null>(null)

watch(() => props.modelValue, (newValue) => {
  if (localValue.value !== newValue) {
    localValue.value = newValue
  }
})

const handleInput = () => {
  emit('update:modelValue', localValue.value)
}

const toggleView = () => {
  if (viewMode.value === 'edit') {
    viewMode.value = 'split'
  } else if (viewMode.value === 'split') {
    viewMode.value = 'preview'
  } else {
    viewMode.value = 'edit'
  }
}

const insertMarkdown = (before: string, after: string) => {
  const textarea = textareaRef.value
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selectedText = localValue.value.substring(start, end)
  const newText = before + selectedText + after

  localValue.value =
    localValue.value.substring(0, start) +
    newText +
    localValue.value.substring(end)

  emit('update:modelValue', localValue.value)

  // 恢复焦点并设置光标位置
  nextTick(() => {
    textarea.focus()
    const newCursorPos = start + before.length + selectedText.length + after.length
    textarea.setSelectionRange(newCursorPos, newCursorPos)
  })
}

const handleKeydown = (e: KeyboardEvent) => {
  // Tab 键插入两个空格（Markdown 常用缩进）
  if (e.key === 'Tab' && !e.shiftKey) {
    e.preventDefault()
    const textarea = textareaRef.value
    if (!textarea) return

    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const spaces = '  ' // 两个空格

    localValue.value =
      localValue.value.substring(0, start) +
      spaces +
      localValue.value.substring(end)

    emit('update:modelValue', localValue.value)

    nextTick(() => {
      textarea.focus()
      const newCursorPos = start + spaces.length
      textarea.setSelectionRange(newCursorPos, newCursorPos)
    })
  }
}
</script>

<style scoped>
.markdown-editor {
  @apply flex flex-col h-full border border-gray-300 rounded-lg overflow-hidden bg-white;
  min-height: 0; /* 确保 flex 子元素可以收缩 */
}

.editor-toolbar {
  @apply flex items-center justify-between px-3 py-2 border-b border-gray-200 bg-gray-50;
  flex-shrink: 0;
}

.toolbar-left,
.toolbar-right {
  @apply flex items-center gap-1;
}

.toolbar-btn {
  @apply px-2 py-1 text-sm text-gray-600 hover:bg-gray-200 rounded transition-colors flex items-center;
  white-space: nowrap;
}

.toolbar-btn:active {
  @apply bg-gray-300;
}

.editor-content {
  @apply flex-1 overflow-hidden flex;
  min-height: 0; /* 确保 flex 子元素可以收缩 */
}

.editor-content.edit {
  @apply flex-col;
}

.editor-content.preview {
  @apply flex-col;
}

.editor-content.split {
  @apply flex-row;
}

.editor-pane {
  @apply flex-1 overflow-hidden;
  min-height: 0;
}

.editor-content.split .editor-pane {
  @apply border-r border-gray-200;
  min-width: 0; /* 允许 flex 子元素收缩 */
}

.preview-pane {
  @apply flex-1 overflow-y-auto p-4 bg-gray-50;
  min-width: 0; /* 允许 flex 子元素收缩 */
}

.markdown-textarea {
  @apply w-full h-full resize-none border-none outline-none p-4 font-mono text-sm;
  @apply focus:ring-0;
  line-height: 1.6;
  min-height: 0;
}

.markdown-textarea::placeholder {
  @apply text-gray-400;
}
</style>


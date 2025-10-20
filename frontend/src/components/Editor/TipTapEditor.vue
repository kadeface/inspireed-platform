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
      <button @click="addImage" class="menu-btn">🖼️ Image</button>
    </div>
    <editor-content :editor="editor" class="editor-content" />
  </div>
</template>

<script setup lang="ts">
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'
import Link from '@tiptap/extension-link'
import { watch, onBeforeUnmount } from 'vue'

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
    emit('update', editor.getHTML())
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

function addImage() {
  const url = window.prompt('请输入图片URL:')
  if (url && editor.value) {
    editor.value.chain().focus().setImage({ src: url }).run()
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
</style>


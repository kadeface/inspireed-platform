<template>
  <div class="text-cell cell-container">
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
import { ref, computed } from 'vue'
import type { TextCell as TextCellType } from '../../types/cell'
import TipTapEditor from '../Editor/TipTapEditor.vue'
import DOMPurify from 'dompurify'

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
  return DOMPurify.sanitize(props.cell.content.html)
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
</script>

<style scoped>
.text-cell-view {
  @apply prose max-w-none;
}

.text-cell-editor {
  @apply w-full;
}
</style>


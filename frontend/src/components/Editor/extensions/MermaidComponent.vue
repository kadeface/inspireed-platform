<template>
  <node-view-wrapper class="mermaid-node">
    <div class="mermaid-container">
      <div class="mermaid-header">
        <span class="mermaid-label">{{ node.attrs.type || 'flowchart' }}</span>
        <div class="mermaid-actions">
          <button @click="editDiagram" class="mermaid-btn" title="Edit diagram">
            ✏️ Edit
          </button>
          <button @click="deleteNode" class="mermaid-btn mermaid-btn-danger" title="Delete">
            🗑️
          </button>
        </div>
      </div>
      <div class="mermaid-content" ref="mermaidRef">
        <pre v-if="!rendered">{{ node.attrs.code }}</pre>
      </div>
      <div v-if="error" class="mermaid-error">{{ error }}</div>
    </div>

    <!-- Edit Dialog -->
    <Teleport to="body">
      <div v-if="isEditing" class="fixed inset-0 z-50 overflow-y-auto" @click.self="closeEdit">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75" @click="closeEdit"></div>
        <div class="flex min-h-full items-center justify-center p-4">
          <div class="relative bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div class="px-6 pt-6 pb-4 border-b flex items-center justify-between">
              <h3 class="text-xl font-semibold text-gray-900">Edit Mermaid Diagram</h3>
              <button @click="closeEdit" class="text-gray-400 hover:text-gray-500">
                <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div class="flex-1 overflow-y-auto p-6">
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Diagram Type</label>
                  <select v-model="editType" class="w-full border border-gray-300 rounded-md px-3 py-2">
                    <option value="flowchart">Flowchart</option>
                    <option value="sequence">Sequence Diagram</option>
                    <option value="class">Class Diagram</option>
                    <option value="state">State Diagram</option>
                    <option value="er">ER Diagram</option>
                    <option value="gantt">Gantt Chart</option>
                    <option value="pie">Pie Chart</option>
                    <option value="mindmap">Mindmap</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Mermaid Code</label>
                  <textarea
                    v-model="editCode"
                    class="w-full border border-gray-300 rounded-md px-3 py-2 font-mono text-sm"
                    rows="15"
                    placeholder="Enter mermaid diagram code..."
                  ></textarea>
                </div>

                <div v-if="editError" class="text-red-600 text-sm">{{ editError }}</div>

                <div class="border rounded-md p-4 bg-gray-50">
                  <h4 class="text-sm font-medium text-gray-700 mb-2">Preview</h4>
                  <div class="mermaid-preview" ref="previewRef">
                    <pre v-if="!previewRendered">{{ editCode }}</pre>
                  </div>
                </div>
              </div>
            </div>

            <div class="px-6 py-4 border-t bg-gray-50 flex justify-end gap-2">
              <button @click="closeEdit" class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-100">
                Cancel
              </button>
              <button @click="saveDiagram" class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600">
                Save
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </node-view-wrapper>
</template>

<script setup lang="ts">
import { NodeViewWrapper, nodeViewProps } from '@tiptap/vue-3'
import { ref, onMounted, watch, nextTick } from 'vue'
import mermaid from 'mermaid'

const props = defineProps(nodeViewProps)

const mermaidRef = ref<HTMLElement>()
const previewRef = ref<HTMLElement>()
const isEditing = ref(false)
const editCode = ref('')
const editType = ref('flowchart')
const editError = ref('')
const rendered = ref(false)
const error = ref('')
const previewRendered = ref(false)

// Initialize mermaid
onMounted(() => {
  mermaid.initialize({
    startOnLoad: false,
    theme: 'default',
    securityLevel: 'loose',
  })
  renderDiagram()
})

// Render the diagram
async function renderDiagram() {
  if (!mermaidRef.value || !props.node.attrs.code) return

  try {
    const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`
    const { svg } = await mermaid.render(id, props.node.attrs.code)

    if (mermaidRef.value) {
      mermaidRef.value.innerHTML = svg
      rendered.value = true
      error.value = ''
    }
  } catch (err: any) {
    error.value = err.message || 'Failed to render diagram'
    rendered.value = false
  }
}

// Edit diagram
function editDiagram() {
  editCode.value = props.node.attrs.code || ''
  editType.value = props.node.attrs.type || 'flowchart'
  isEditing.value = true
  nextTick(() => {
    renderPreview()
  })
}

// Close edit dialog
function closeEdit() {
  isEditing.value = false
  editCode.value = ''
  editType.value = 'flowchart'
  editError.value = ''
  previewRendered.value = false
}

// Save diagram
function saveDiagram() {
  if (!editCode.value.trim()) {
    editError.value = 'Please enter diagram code'
    return
  }

  props.updateAttributes({
    code: editCode.value,
    type: editType.value,
  })

  closeEdit()
  nextTick(() => {
    renderDiagram()
  })
}

// Delete node
function deleteNode() {
  props.deleteNode()
}

// Render preview in edit dialog
async function renderPreview() {
  if (!previewRef.value || !editCode.value) return

  try {
    const id = `mermaid-preview-${Math.random().toString(36).substr(2, 9)}`
    const { svg } = await mermaid.render(id, editCode.value)

    if (previewRef.value) {
      previewRef.value.innerHTML = svg
      previewRendered.value = true
      editError.value = ''
    }
  } catch (err: any) {
    editError.value = err.message || 'Invalid mermaid code'
    previewRendered.value = false
  }
}

// Watch for code changes
watch(
  () => editCode.value,
  () => {
    if (isEditing.value) {
      renderPreview()
    }
  }
)
</script>

<style scoped>
.mermaid-node {
  margin: 1em 0;
}

.mermaid-container {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
  background: white;
}

.mermaid-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 1rem;
  background: linear-gradient(to right, #f3f4f6, #e5e7eb);
  border-bottom: 1px solid #e5e7eb;
}

.mermaid-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  text-transform: uppercase;
}

.mermaid-actions {
  display: flex;
  gap: 0.5rem;
}

.mermaid-btn {
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}

.mermaid-btn:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.mermaid-btn-danger:hover {
  background: #fef2f2;
  border-color: #f87171;
  color: #dc2626;
}

.mermaid-content {
  padding: 1rem;
  min-height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow-x: auto;
}

.mermaid-content :deep(svg) {
  max-width: 100%;
  height: auto;
}

.mermaid-content pre {
  margin: 0;
  padding: 0.5rem;
  background: #f9fafb;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  overflow-x: auto;
}

.mermaid-error {
  padding: 0.75rem 1rem;
  background: #fef2f2;
  color: #dc2626;
  font-size: 0.875rem;
  border-top: 1px solid #fecaca;
}

.mermaid-preview {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow-x: auto;
}

.mermaid-preview :deep(svg) {
  max-width: 100%;
  height: auto;
}

.mermaid-preview pre {
  margin: 0;
  padding: 0.5rem;
  background: #f9fafb;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  overflow-x: auto;
}
</style>

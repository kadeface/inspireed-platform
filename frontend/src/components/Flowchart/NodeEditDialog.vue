<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900">编辑节点</h3>
      </div>

      <div class="px-6 py-4 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            节点类型
          </label>
          <div class="text-sm text-gray-600">
            {{ nodeTypeLabels[node.type] }}
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            节点标签
          </label>
          <input
            v-model="editedLabel"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="输入节点标签"
          />
        </div>

        <div v-if="node.type === 'decision'">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            分支说明
          </label>
          <textarea
            v-model="editedDescription"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="描述判断条件和各分支的含义"
          />
        </div>
      </div>

      <div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
        <button
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          @click="$emit('close')"
        >
          取消
        </button>
        <button
          class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700"
          @click="handleSave"
        >
          保存
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { FlowchartNode } from '@/types/cell'

interface Props {
  node: FlowchartNode
}

const props = defineProps<Props>()

const emit = defineEmits<{
  save: [node: FlowchartNode]
  close: []
}>()

const editedLabel = ref(props.node.label)
const editedDescription = ref(props.node.data?.description || '')

const nodeTypeLabels = {
  start: '开始节点',
  process: '处理过程',
  decision: '判断条件',
  loop: '循环节点',
  end: '结束节点',
  custom: '自定义',
}

function handleSave() {
  emit('save', {
    ...props.node,
    label: editedLabel.value,
    data: {
      ...props.node.data,
      description: editedDescription.value,
    },
  })
}

watch(
  () => props.node,
  (newNode) => {
    editedLabel.value = newNode.label
    editedDescription.value = newNode.data?.description || ''
  },
  { deep: true }
)
</script>


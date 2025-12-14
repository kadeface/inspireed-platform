<template>
  <div class="resource-directory-tree bg-white border-r border-gray-200 h-full overflow-y-auto">
    <div class="p-4">
      <h3 class="text-sm font-semibold text-gray-700 mb-3">资源目录</h3>
      
      <div class="tree-container">
        <div
          v-for="node in treeNodes"
          :key="node.id"
          class="tree-node"
        >
          <!-- 根节点 -->
          <div
            :class="[
              'tree-item flex items-center gap-2 px-2 py-1.5 rounded cursor-pointer hover:bg-gray-100',
              isSelected(node) ? 'bg-purple-50 text-purple-700' : 'text-gray-700'
            ]"
            @click="handleNodeClick(node)"
          >
            <span v-if="node.children && node.children.length > 0" class="flex-shrink-0">
              <svg
                :class="[
                  'w-4 h-4 transition-transform',
                  expandedNodes.has(node.id) ? 'rotate-90' : ''
                ]"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                @click.stop="toggleExpand(node.id)"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </span>
            <span v-else class="w-4 h-4"></span>
            
            <span v-if="node.icon" class="text-base">{{ node.icon }}</span>
            <span class="flex-1 text-sm truncate">{{ node.label }}</span>
            <span v-if="node.count !== undefined" class="text-xs text-gray-500">
              ({{ node.count }})
            </span>
          </div>

          <!-- 子节点 -->
          <div
            v-if="node.children && expandedNodes.has(node.id)"
            class="ml-4 mt-1"
          >
            <div
              v-for="child in node.children"
              :key="child.id"
              class="tree-node"
            >
              <div
                :class="[
                  'tree-item flex items-center gap-2 px-2 py-1.5 rounded cursor-pointer hover:bg-gray-100',
                  isSelected(child) ? 'bg-purple-50 text-purple-700' : 'text-gray-700'
                ]"
                @click="handleNodeClick(child)"
              >
                <span v-if="child.children && child.children.length > 0" class="flex-shrink-0">
                  <svg
                    :class="[
                      'w-4 h-4 transition-transform',
                      expandedNodes.has(child.id) ? 'rotate-90' : ''
                    ]"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    @click.stop="toggleExpand(child.id)"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </span>
                <span v-else class="w-4 h-4"></span>
                
                <span v-if="child.icon" class="text-base">{{ child.icon }}</span>
                <span class="flex-1 text-sm truncate">{{ child.label }}</span>
                <span v-if="child.count !== undefined" class="text-xs text-gray-500">
                  ({{ child.count }})
                </span>
              </div>

              <!-- 三级节点 -->
              <div
                v-if="child.children && expandedNodes.has(child.id)"
                class="ml-4 mt-1"
              >
                <div
                  v-for="grandchild in child.children"
                  :key="grandchild.id"
                  class="tree-node"
                >
                  <div
                    :class="[
                      'tree-item flex items-center gap-2 px-2 py-1.5 rounded cursor-pointer hover:bg-gray-100',
                      isSelected(grandchild) ? 'bg-purple-50 text-purple-700' : 'text-gray-700'
                    ]"
                    @click="handleNodeClick(grandchild)"
                  >
                    <span class="w-4 h-4"></span>
                    <span v-if="grandchild.icon" class="text-base">{{ grandchild.icon }}</span>
                    <span class="flex-1 text-sm truncate">{{ grandchild.label }}</span>
                    <span v-if="grandchild.count !== undefined" class="text-xs text-gray-500">
                      ({{ grandchild.count }})
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { ResourceTreeNode, ResourceFilter } from '@/types/library'
import type { Subject, Grade } from '@/types/curriculum'
import { LibraryAssetType, getAssetTypeIcon, getAssetTypeName } from '@/types/library'

interface Props {
  subjects: Subject[]
  grades: Grade[]
  selectedFilter?: ResourceFilter
}

const props = defineProps<Props>()
const emit = defineEmits<{
  select: [filter: ResourceFilter]
}>()

const expandedNodes = ref<Set<string>>(new Set(['all', 'by-subject']))
const selectedNodeId = ref<string>('all')

// 构建树形结构
const treeNodes = computed<ResourceTreeNode[]>(() => {
  const nodes: ResourceTreeNode[] = []

  // 全部资源
  nodes.push({
    id: 'all',
    label: '全部资源',
    kind: 'root',
    icon: '📚',
  })

  // 按学科分类
  const bySubjectNode: ResourceTreeNode = {
    id: 'by-subject',
    label: '按学科分类',
    kind: 'category',
    icon: '📖',
    children: props.subjects.map(subject => {
      // 每个学科下有：通用 + 各年级
      const gradeNodes: ResourceTreeNode[] = [
        {
          id: `subject:${subject.id}:grade:null`,
          label: '跨年级通用',
          kind: 'grade',
          subject_id: subject.id,
          grade_id: null,
          icon: '🌐',
        },
        ...props.grades.map(grade => ({
          id: `subject:${subject.id}:grade:${grade.id}`,
          label: grade.name,
          kind: 'grade',
          subject_id: subject.id,
          grade_id: grade.id,
          icon: '📘',
          children: Object.values(LibraryAssetType).map(type => ({
            id: `subject:${subject.id}:grade:${grade.id}:type:${type}`,
            label: getAssetTypeName(type),
            kind: 'asset_type',
            subject_id: subject.id,
            grade_id: grade.id,
            asset_type: type,
            icon: getAssetTypeIcon(type),
          })) as ResourceTreeNode[],
        })),
      ]

      return {
        id: `subject:${subject.id}`,
        label: subject.name,
        kind: 'subject',
        subject_id: subject.id,
        icon: '📕',
        children: gradeNodes,
      }
    }),
  }

  nodes.push(bySubjectNode)

  // 按类型分类
  const byTypeNode: ResourceTreeNode = {
    id: 'by-type',
    label: '按类型分类',
    kind: 'category',
    icon: '🗂️',
    children: Object.values(LibraryAssetType).map(type => ({
      id: `type:${type}`,
      label: getAssetTypeName(type),
      kind: 'asset_type',
      asset_type: type,
      icon: getAssetTypeIcon(type),
    })),
  }

  nodes.push(byTypeNode)

  // 我的资源
  nodes.push({
    id: 'my-resources',
    label: '我的资源',
    kind: 'visibility',
    icon: '👤',
  })

  return nodes
})

// 检查节点是否被选中
const isSelected = (node: ResourceTreeNode): boolean => {
  return node.id === selectedNodeId.value
}

// 切换展开/折叠
const toggleExpand = (nodeId: string) => {
  if (expandedNodes.value.has(nodeId)) {
    expandedNodes.value.delete(nodeId)
  } else {
    expandedNodes.value.add(nodeId)
  }
}

// 处理节点点击
const handleNodeClick = (node: ResourceTreeNode) => {
  selectedNodeId.value = node.id

  // 构建筛选条件
  const filter: ResourceFilter = {}

  if (node.id === 'all') {
    // 全部资源，不设置任何筛选
    emit('select', {})
    return
  }

  if (node.id === 'my-resources') {
    // 我的资源
    filter.visibility = 'teacher_only'
    emit('select', filter)
    return
  }

  // 根据节点类型设置筛选条件
  if (node.subject_id !== undefined) {
    filter.subject_id = node.subject_id
  }

  if (node.grade_id !== undefined) {
    filter.grade_id = node.grade_id
  }

  if (node.asset_type) {
    filter.asset_type = node.asset_type
  }

  emit('select', filter)
}

// 监听外部筛选条件变化，同步选中状态
watch(() => props.selectedFilter, (newFilter) => {
  if (!newFilter || Object.keys(newFilter).length === 0) {
    selectedNodeId.value = 'all'
    return
  }

  // 根据筛选条件找到对应的节点ID
  if (newFilter.visibility === 'teacher_only' && !newFilter.subject_id && !newFilter.grade_id && !newFilter.asset_type) {
    selectedNodeId.value = 'my-resources'
    return
  }

  // 构建节点ID
  let nodeId = ''
  if (newFilter.subject_id) {
    nodeId = `subject:${newFilter.subject_id}`
    if (newFilter.grade_id !== undefined) {
      nodeId += `:grade:${newFilter.grade_id}`
      if (newFilter.asset_type) {
        nodeId += `:type:${newFilter.asset_type}`
      }
    }
  } else if (newFilter.asset_type) {
    nodeId = `type:${newFilter.asset_type}`
  }

  if (nodeId) {
    selectedNodeId.value = nodeId
    // 自动展开相关节点
    const parts = nodeId.split(':')
    if (parts[0] === 'subject') {
      expandedNodes.value.add('by-subject')
      expandedNodes.value.add(`subject:${parts[1]}`)
      if (parts[2] === 'grade') {
        expandedNodes.value.add(nodeId.split(':type:')[0])
      }
    } else if (parts[0] === 'type') {
      expandedNodes.value.add('by-type')
    }
  }
}, { immediate: true })
</script>

<style scoped>
.resource-directory-tree {
  min-width: 280px;
  max-width: 320px;
}

.tree-container {
  user-select: none;
}

.tree-item {
  transition: background-color 0.15s ease;
}

.tree-item:hover {
  background-color: rgb(243, 244, 246);
}
</style>

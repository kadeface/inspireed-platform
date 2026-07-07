<template>
  <div v-if="code" class="rounded-xl border border-sky-200 bg-white overflow-hidden">
    <div class="px-3 py-2 bg-sky-100/60 text-xs font-medium text-sky-800">图示</div>
    <!-- mermaid 渲染目标：独立元素，内部不放任何 Vue 管理的子节点，避免 innerHTML 与虚拟 DOM 冲突 -->
    <div class="p-3 overflow-x-auto flex justify-center min-h-[80px]">
      <div ref="containerRef"></div>
    </div>
    <div v-if="error" class="px-3 py-2 text-xs text-amber-700 bg-amber-50 border-t border-amber-100">
      图示暂时无法显示，请先看下方文字说明。
    </div>
  </div>
</template>

<script setup lang="ts">
import mermaid from 'mermaid'
import { nextTick, onMounted, ref, watch } from 'vue'

const props = defineProps<{
  code: string
}>()

const containerRef = ref<HTMLElement>()
const error = ref('')

let mermaidReady = false

function ensureMermaid() {
  if (mermaidReady) return
  mermaid.initialize({
    startOnLoad: false,
    theme: 'neutral',
    securityLevel: 'loose',
    flowchart: { useMaxWidth: true, htmlLabels: true },
  })
  mermaidReady = true
}

async function renderDiagram() {
  error.value = ''
  const target = containerRef.value
  if (!props.code?.trim() || !target) return

  ensureMermaid()
  try {
    const id = `self-study-mmd-${Math.random().toString(36).slice(2, 10)}`
    const { svg } = await mermaid.render(id, props.code.trim())
    // target 是叶子元素（无 Vue 子节点），直接写 innerHTML 安全
    if (containerRef.value) {
      containerRef.value.innerHTML = svg
    }
  } catch {
    if (containerRef.value) {
      containerRef.value.innerHTML = ''
    }
    error.value = 'render_failed'
  }
}

onMounted(() => {
  nextTick(renderDiagram)
})

watch(
  () => props.code,
  () => {
    nextTick(renderDiagram)
  }
)
</script>

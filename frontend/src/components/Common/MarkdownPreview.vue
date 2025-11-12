<template>
  <div
    class="prose prose-sm max-w-none text-slate-800"
    v-html="renderedHtml"
  ></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import DOMPurify from 'dompurify'

const props = defineProps({
  content: {
    type: String,
    default: '',
  },
})

function escapeHtml(input: string): string {
  return input
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function renderInline(text: string): string {
  let result = escapeHtml(text)

  result = result.replace(
    /\[([^\]]+)]\((https?:\/\/[^\s)]+)\)/g,
    (_match, label, url) =>
      `<a href="${url}" target="_blank" rel="noopener noreferrer">${label}</a>`
  )

  result = result.replace(/`([^`]+)`/g, '<code>$1</code>')
  result = result.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  result = result.replace(/\*([^*]+)\*/g, '<em>$1</em>')

  return result
}

function renderMarkdown(markdown: string): string {
  const lines = markdown.split(/\r?\n/)
  const html: string[] = []
  let inList = false
  let inBlockquote = false
  let inCodeBlock = false
  let codeBuffer: string[] = []

  const closeList = () => {
    if (inList) {
      html.push('</ul>')
      inList = false
    }
  }

  const closeBlockquote = () => {
    if (inBlockquote) {
      html.push('</blockquote>')
      inBlockquote = false
    }
  }

  const closeCodeBlock = () => {
    if (inCodeBlock) {
      const codeContent = escapeHtml(codeBuffer.join('\n'))
      html.push(`<pre><code>${codeContent}</code></pre>`)
      inCodeBlock = false
      codeBuffer = []
    }
  }

  lines.forEach((line) => {
    if (/^```/.test(line.trim())) {
      if (inCodeBlock) {
        closeCodeBlock()
      } else {
        closeList()
        closeBlockquote()
        inCodeBlock = true
        codeBuffer = []
      }
      return
    }

    if (inCodeBlock) {
      codeBuffer.push(line)
      return
    }

    if (line.trim() === '') {
      closeList()
      closeBlockquote()
      html.push('<p></p>')
      return
    }

    const headingMatch = line.match(/^(#{1,3})\s+(.*)$/)
    if (headingMatch) {
      closeList()
      closeBlockquote()
      const level = headingMatch[1].length
      const content = renderInline(headingMatch[2])
      html.push(`<h${level}>${content}</h${level}>`)
      return
    }

    if (/^>\s+/.test(line)) {
      closeList()
      if (!inBlockquote) {
        html.push('<blockquote>')
        inBlockquote = true
      }
      html.push(`<p>${renderInline(line.replace(/^>\s+/, ''))}</p>`)
      return
    }

    if (/^-\s+/.test(line)) {
      closeBlockquote()
      if (!inList) {
        html.push('<ul>')
        inList = true
      }
      html.push(`<li>${renderInline(line.replace(/^-\s+/, ''))}</li>`)
      return
    }

    closeList()
    closeBlockquote()
    html.push(`<p>${renderInline(line)}</p>`)
  })

  closeCodeBlock()
  closeList()
  closeBlockquote()

  return html.join('\n')
}

const renderedHtml = computed(() => {
  const markdown = props.content || ''
  const rawHtml = renderMarkdown(markdown.trim())
  return DOMPurify.sanitize(rawHtml || '<p>（暂无内容）</p>')
})
</script>

<style scoped>
.prose :where(pre code):not(:where([class~="not-prose"] *)) {
  background-color: inherit;
  color: inherit;
}
</style>


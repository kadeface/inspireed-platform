<template>
  <div
    class="prose prose-sm max-w-none text-slate-800"
    v-html="renderedHtml"
  ></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import DOMPurify from 'dompurify'
import { getServerBaseUrl } from '@/utils/url'

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

  // 处理图片语法 ![alt](url) - 必须在链接之前处理，因为图片和链接语法相似
  result = result.replace(
    /!\[([^\]]*)\]\((https?:\/\/[^\s)]+|\/[^\s)]+|[^\s)]+)\)/g,
    (_match, alt, url) => {
      // 规范化图片URL（在转换为HTML之前）
      const baseURL = getServerBaseUrl()
      let normalizedUrl = url
      // 如果是完整URL且指向资源路径，统一替换为当前服务器地址
      if (url.startsWith('http://') || url.startsWith('https://')) {
        try {
          const urlObj = new URL(url)
          // 如果URL指向的是资源路径 (/uploads/)，统一替换为当前服务器地址
          // 这样可以确保无论数据来自哪个环境，都能在当前环境正确显示
          if (urlObj.pathname.startsWith('/uploads/')) {
            const path = urlObj.pathname + (urlObj.search || '') + (urlObj.hash || '')
            normalizedUrl = `${baseURL}${path}`
          }
        } catch {
          // URL解析失败，使用原URL
        }
      } else if (url.startsWith('/')) {
        // 相对路径，转换为完整URL
        normalizedUrl = `${baseURL}${url}`
      } else if (!url.startsWith('/') && !url.startsWith('http://') && !url.startsWith('https://')) {
        // 纯文件名，假设是资源文件
        if (/\.(png|jpe?g|gif|webp|svg|mp4|pdf|docx?|xlsx?|pptx?)$/i.test(url)) {
          normalizedUrl = `${baseURL}/uploads/resources/${url}`
        }
      }
      return `<img src="${normalizedUrl}" alt="${alt}" />`
    }
  )

  // 处理链接语法 [text](url)
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
  let rawHtml = renderMarkdown(markdown.trim())
  
  // 对渲染后的HTML进行URL规范化处理（安全网）
  // 确保所有图片URL都被规范化
  const baseURL = getServerBaseUrl()
  
  // 处理HTML中的图片URL，确保所有指向 /uploads/ 的完整URL都被替换为当前服务器地址
  rawHtml = rawHtml.replace(/src\s*=\s*(["'])(https?:\/\/[^"']+\/uploads\/[^"']+)\1/gi, (match, quote, url) => {
    try {
      const urlObj = new URL(url)
      if (urlObj.pathname.startsWith('/uploads/')) {
        const path = urlObj.pathname + (urlObj.search || '') + (urlObj.hash || '')
        return `src=${quote}${baseURL}${path}${quote}`
      }
    } catch {
      // URL解析失败，尝试直接提取路径
      const pathMatch = url.match(/\/uploads\/[^"']+/)
      if (pathMatch) {
        return `src=${quote}${baseURL}${pathMatch[0]}${quote}`
      }
    }
    return match
  })
  
  // 额外安全网：直接替换HTML字符串中所有指向 /uploads/ 的完整URL
  rawHtml = rawHtml.replace(/https?:\/\/[^\s"'>]+\/uploads\/[^\s"'>]+/gi, (match) => {
    try {
      const urlObj = new URL(match)
      if (urlObj.pathname.startsWith('/uploads/')) {
        const path = urlObj.pathname + (urlObj.search || '') + (urlObj.hash || '')
        return baseURL + path
      }
    } catch {
      const pathMatch = match.match(/\/uploads\/[^\s"'>]+/)
      if (pathMatch) {
        return baseURL + pathMatch[0]
      }
    }
    return match
  })
  
  return DOMPurify.sanitize(rawHtml || '<p>（暂无内容）</p>', {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'u', 's', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'img', 'div', 'span'],
    ALLOWED_ATTR: ['href', 'target', 'rel', 'src', 'alt', 'title', 'class'],
  })
})
</script>

<style scoped>
.prose :where(pre code):not(:where([class~="not-prose"] *)) {
  background-color: inherit;
  color: inherit;
}
</style>


/** 授课播放时铺满画面的图片：图片单元，或正文里只有图片的文本单元。 */

export function isPresentationImageCell(
  cell: { type?: string; content?: unknown } | null | undefined,
): boolean {
  if (!cell?.type) return false
  const type = String(cell.type).toUpperCase()
  if (type === 'IMAGE') return true
  if (type !== 'TEXT') return false

  const content = cell.content as { html?: string; markdown?: string } | undefined
  const html = content?.html?.trim() || ''
  if (html) return isImageOnlyMarkup(html)

  const markdown = content?.markdown?.trim() || ''
  return /^!\[[^\]]*\]\([^)]+\)\s*$/.test(markdown)
}

function isImageOnlyMarkup(html: string): boolean {
  if (!/<img\b/i.test(html)) return false
  const text = html
    .replace(/<img\b[^>]*>/gi, '')
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/gi, ' ')
    .replace(/\s+/g, '')
  return text.length === 0
}

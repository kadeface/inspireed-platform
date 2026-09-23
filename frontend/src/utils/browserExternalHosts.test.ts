import { describe, expect, it } from 'vitest'
import { embedIframeSrc } from './browserExternalHosts'

const bilibiliUrl =
  'https://player.bilibili.com/player.html?isOutside=true&aid=117313592367632&bvid=BV1wDhj6wEa8&cid=42106031130&p=1'

describe('embedIframeSrc', () => {
  it('turns off Bilibili autoplay when the embed URL omits it', () => {
    const src = new URL(embedIframeSrc(bilibiliUrl))
    expect(src.searchParams.get('autoplay')).toBe('0')
    expect(src.searchParams.get('bvid')).toBe('BV1wDhj6wEa8')
  })

  it('keeps an explicit Bilibili autoplay flag', () => {
    const src = embedIframeSrc(`${bilibiliUrl}&autoplay=1`)
    expect(new URL(src).searchParams.get('autoplay')).toBe('1')
  })

  it('leaves other sites unchanged', () => {
    const url = 'https://example.com/watch'
    expect(embedIframeSrc(url)).toBe(url)
  })
})

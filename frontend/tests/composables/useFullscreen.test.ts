/**
 * useFullscreen Composable 单元测试
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { ref } from 'vue'
import { useFullscreen } from '@/components/Classroom/composables/useFullscreen'

describe('useFullscreen', () => {
  // Mock document 对象
  let mockDocument: any
  let mockElement: any

  beforeEach(() => {
    // 保存原始 document
    mockDocument = global.document

    // 创建 mock 元素
    mockElement = {
      requestFullscreen: vi.fn(() => Promise.resolve()),
      webkitRequestFullscreen: vi.fn(() => Promise.resolve()),
      mozRequestFullScreen: vi.fn(() => Promise.resolve()),
      msRequestFullscreen: vi.fn(() => Promise.resolve()),
    }

    // 设置全局 document
    global.document = {
      ...mockDocument,
      documentElement: mockElement,
      fullscreenElement: null,
      webkitFullscreenElement: null,
      mozFullScreenElement: null,
      msFullscreenElement: null,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      exitFullscreen: vi.fn(() => Promise.resolve()),
      webkitExitFullscreen: vi.fn(() => Promise.resolve()),
      mozCancelFullScreen: vi.fn(() => Promise.resolve()),
      msExitFullscreen: vi.fn(() => Promise.resolve()),
    } as any
  })

  it('应该正确初始化状态', () => {
    const { modulePanelFullscreen, isPanelFullscreen } = useFullscreen()

    expect(modulePanelFullscreen.value).toBe(false)
    expect(isPanelFullscreen.value).toBe(false)
  })

  it('应该切换模块面板全屏状态', () => {
    const { modulePanelFullscreen, toggleModulePanelFullscreen } = useFullscreen()

    expect(modulePanelFullscreen.value).toBe(false)

    toggleModulePanelFullscreen()

    expect(modulePanelFullscreen.value).toBe(true)

    toggleModulePanelFullscreen()

    expect(modulePanelFullscreen.value).toBe(false)
  })

  it('应该支持浏览器全屏切换', async () => {
    const { isPanelFullscreen, togglePanelFullscreen } = useFullscreen()

    expect(isPanelFullscreen.value).toBe(false)

    // 模拟成功进入全屏
    global.document.fullscreenElement = mockElement

    await togglePanelFullscreen()

    expect(mockElement.requestFullscreen).toHaveBeenCalled()
    expect(isPanelFullscreen.value).toBe(true)
  })

  it('应该处理全屏切换失败的情况', async () => {
    const { isPanelFullscreen, togglePanelFullscreen } = useFullscreen()

    // 模拟全屏 API 失败
    mockElement.requestFullscreen = vi.fn(() => Promise.reject(new Error('Fullscreen failed')))

    try {
      await togglePanelFullscreen()
    } catch (error) {
      // 预期会捕获错误
    }

    // 即使失败，也应该设置状态为 true（降级到 CSS 全屏）
    expect(isPanelFullscreen.value).toBe(true)
  })

  it('应该支持退出全屏', async () => {
    const { isPanelFullscreen, togglePanelFullscreen } = useFullscreen()

    // 先进入全屏
    global.document.fullscreenElement = mockElement
    isPanelFullscreen.value = true

    // 模拟 exitFullscreen
    global.document.exitFullscreen = vi.fn(() => Promise.resolve())

    await togglePanelFullscreen()

    expect(global.document.exitFullscreen).toHaveBeenCalled()
    expect(isPanelFullscreen.value).toBe(false)
  })

  it('应该设置全屏监听器', () => {
    const addEventListenerSpy = vi.spyOn(global.document, 'addEventListener')

    const { setupFullscreenListeners } = useFullscreen()

    setupFullscreenListeners()

    expect(addEventListenerSpy).toHaveBeenCalledWith('fullscreenchange', expect.any(Function))
    expect(addEventListenerSpy).toHaveBeenCalledWith('webkitfullscreenchange', expect.any(Function))
    expect(addEventListenerSpy).toHaveBeenCalledWith('mozfullscreenchange', expect.any(Function))
    expect(addEventListenerSpy).toHaveBeenCalledWith('MSFullscreenChange', expect.any(Function))

    addEventListenerSpy.mockRestore()
  })

  it('应该清理全屏监听器', () => {
    const removeEventListenerSpy = vi.spyOn(global.document, 'removeEventListener')

    const { cleanupFullscreenListeners } = useFullscreen()

    cleanupFullscreenListeners()

    expect(removeEventListenerSpy).toHaveBeenCalledWith('fullscreenchange', expect.any(Function))
    expect(removeEventListenerSpy).toHaveBeenCalledWith('webkitfullscreenchange', expect.any(Function))
    expect(removeEventListenerSpy).toHaveBeenCalledWith('mozfullscreenchange', expect.any(Function))
    expect(removeEventListenerSpy).toHaveBeenCalledWith('MSFullscreenChange', expect.any(Function))

    removeEventListenerSpy.mockRestore()
  })

  it('应该监听全屏状态变化', () => {
    const { isPanelFullscreen, setupFullscreenListeners, handleFullscreenChange } = useFullscreen()

    // 初始状态：不在全屏
    global.document.fullscreenElement = null
    isPanelFullscreen.value = true

    // 触发全屏变化事件（退出全屏）
    handleFullscreenChange()

    expect(isPanelFullscreen.value).toBe(false)
  })

  it('应该在组件卸载时自动清理监听器', () => {
    const removeEventListenerSpy = vi.spyOn(global.document, 'removeEventListener')

    // 导入并使用 composable 会触发 onBeforeUnmount
    // 这里我们手动测试清理功能
    const { cleanupFullscreenListeners } = useFullscreen()

    cleanupFullscreenListeners()

    expect(removeEventListenerSpy).toHaveBeenCalledTimes(4)

    removeEventListenerSpy.mockRestore()
  })
})

/**
 * 全屏控制 Composable
 *
 * 管理浏览器全屏和模块面板全屏功能
 */

import { ref, onMounted, onBeforeUnmount, type Ref } from 'vue'

export function useFullscreen() {
  // 模块面板全屏状态
  const modulePanelFullscreen = ref(false)

  // 整个导播台全屏状态
  const isPanelFullscreen = ref(false)

  /**
   * 切换模块面板全屏
   */
  function toggleModulePanelFullscreen() {
    modulePanelFullscreen.value = !modulePanelFullscreen.value
  }

  /**
   * 切换整个导播台全屏
   */
  async function togglePanelFullscreen() {
    if (!isPanelFullscreen.value) {
      // 进入全屏
      try {
        const element = document.documentElement
        if (element.requestFullscreen) {
          await element.requestFullscreen()
        } else if ((element as any).webkitRequestFullscreen) {
          await (element as any).webkitRequestFullscreen()
        } else if ((element as any).mozRequestFullScreen) {
          await (element as any).mozRequestFullScreen()
        } else if ((element as any).msRequestFullscreen) {
          await (element as any).msRequestFullscreen()
        }
        isPanelFullscreen.value = true
      } catch (error: any) {
        console.error('进入全屏失败:', error)
        // 如果浏览器全屏失败，使用CSS全屏模式
        isPanelFullscreen.value = true
      }
    } else {
      // 退出全屏
      try {
        if (document.exitFullscreen) {
          await document.exitFullscreen()
        } else if ((document as any).webkitExitFullscreen) {
          await (document as any).webkitExitFullscreen()
        } else if ((document as any).mozCancelFullScreen) {
          await (document as any).mozCancelFullScreen()
        } else if ((document as any).msExitFullscreen) {
          await (document as any).msExitFullscreen()
        }
        isPanelFullscreen.value = false
      } catch (error: any) {
        console.error('退出全屏失败:', error)
        isPanelFullscreen.value = false
      }
    }
  }

  /**
   * 监听浏览器全屏状态变化
   */
  function handleFullscreenChange() {
    const isCurrentlyFullscreen = !!(
      document.fullscreenElement ||
      (document as any).webkitFullscreenElement ||
      (document as any).mozFullScreenElement ||
      (document as any).msFullscreenElement
    )

    if (!isCurrentlyFullscreen && isPanelFullscreen.value) {
      isPanelFullscreen.value = false
    }
  }

  /**
   * 设置全屏监听器
   */
  function setupFullscreenListeners() {
    document.addEventListener('fullscreenchange', handleFullscreenChange)
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
    document.addEventListener('mozfullscreenchange', handleFullscreenChange)
    document.addEventListener('MSFullscreenChange', handleFullscreenChange)
  }

  /**
   * 清理全屏监听器
   */
  function cleanupFullscreenListeners() {
    document.removeEventListener('fullscreenchange', handleFullscreenChange)
    document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
    document.removeEventListener('mozfullscreenchange', handleFullscreenChange)
    document.removeEventListener('MSFullscreenChange', handleFullscreenChange)
  }

  return {
    // 状态
    modulePanelFullscreen,
    isPanelFullscreen,

    // 方法
    toggleModulePanelFullscreen,
    togglePanelFullscreen,
    handleFullscreenChange,
    setupFullscreenListeners,
    cleanupFullscreenListeners,
  }
}

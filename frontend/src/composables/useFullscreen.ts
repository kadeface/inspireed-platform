/**
 * 全屏功能 Composable
 */
import { ref, onMounted, onUnmounted } from 'vue'

export function useFullscreen(elementRef?: { value: HTMLElement | null }) {
  const isFullscreen = ref(false)

  // 进入全屏
  async function enterFullscreen() {
    try {
      const element = elementRef?.value || document.documentElement
      
      if (element.requestFullscreen) {
        await element.requestFullscreen()
      } else if ((element as any).webkitRequestFullscreen) {
        await (element as any).webkitRequestFullscreen()
      } else if ((element as any).mozRequestFullScreen) {
        await (element as any).mozRequestFullScreen()
      } else if ((element as any).msRequestFullscreen) {
        await (element as any).msRequestFullscreen()
      }
      
      isFullscreen.value = true
      console.log('✅ 已进入全屏模式')
    } catch (error: any) {
      console.error('❌ 进入全屏失败:', error)
      if (error.name !== 'NotAllowedError') {
        console.warn('⚠️ 全屏请求被拒绝或浏览器不支持')
      }
      throw error
    }
  }

  // 退出全屏
  async function exitFullscreen() {
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
      
      isFullscreen.value = false
      console.log('✅ 已退出全屏模式')
    } catch (error: any) {
      console.error('❌ 退出全屏失败:', error)
      throw error
    }
  }

  // 切换全屏
  async function toggleFullscreen() {
    if (isFullscreen.value) {
      await exitFullscreen()
    } else {
      await enterFullscreen()
    }
  }

  // 检查当前全屏状态
  function checkFullscreenStatus() {
    const isCurrentlyFullscreen = !!(
      document.fullscreenElement ||
      (document as any).webkitFullscreenElement ||
      (document as any).mozFullScreenElement ||
      (document as any).msFullscreenElement
    )
    
    isFullscreen.value = isCurrentlyFullscreen
    return isCurrentlyFullscreen
  }

  // 处理全屏状态变化
  function handleFullscreenChange() {
    checkFullscreenStatus()
  }

  onMounted(() => {
    // 监听全屏状态变化
    document.addEventListener('fullscreenchange', handleFullscreenChange)
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
    document.addEventListener('mozfullscreenchange', handleFullscreenChange)
    document.addEventListener('MSFullscreenChange', handleFullscreenChange)
    
    // 初始化状态
    checkFullscreenStatus()
  })

  onUnmounted(() => {
    // 移除监听器
    document.removeEventListener('fullscreenchange', handleFullscreenChange)
    document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
    document.removeEventListener('mozfullscreenchange', handleFullscreenChange)
    document.removeEventListener('MSFullscreenChange', handleFullscreenChange)
  })

  return {
    isFullscreen,
    enterFullscreen,
    exitFullscreen,
    toggleFullscreen,
    checkFullscreenStatus,
  }
}


/**
 * 教案编辑器 - 幻灯片模式：索引、goTo、全屏、控制条显隐、键盘
 */

import { ref, computed, watch, type Ref } from 'vue'
import { useFullscreen } from './useFullscreen'
import type { Cell } from '../types/cell'

export function useLessonEditorSlides(
  slideContainerRef: Ref<HTMLElement | undefined>,
  displayCells: Ref<unknown[]>,
  isFullscreenPreview: Ref<boolean>
) {
  const { isFullscreen: isSlideNativeFullscreen, toggleFullscreen: toggleSlideFullscreen } =
    useFullscreen(slideContainerRef as any)

  const slideMode = ref(false)
  const currentSlideIndex = ref(0)
  const slideFullscreen = ref(false)
  const showSlideControls = ref(true)
  let slideControlsTimer: ReturnType<typeof setTimeout> | null = null

  const currentCell = computed<Cell | null>(() => {
    const list = displayCells.value ?? []
    if (!slideMode.value || list.length === 0) return null
    const i = Math.max(0, Math.min(currentSlideIndex.value, list.length - 1))
    return (list[i] ?? null) as Cell | null
  })

  function clearControlsTimer() {
    if (slideControlsTimer) {
      clearTimeout(slideControlsTimer)
      slideControlsTimer = null
    }
  }

  function resetControlsTimer() {
    clearControlsTimer()
    if (slideFullscreen.value) {
      slideControlsTimer = setTimeout(() => {
        if (slideFullscreen.value) showSlideControls.value = false
      }, 3000)
    }
  }

  function goToPreviousSlide() {
    if (currentSlideIndex.value > 0) currentSlideIndex.value--
  }

  function goToNextSlide() {
    const len = (displayCells.value ?? []).length
    if (currentSlideIndex.value < len - 1) currentSlideIndex.value++
  }

  function goToSlide(index: number) {
    const len = (displayCells.value ?? []).length
    currentSlideIndex.value = Math.max(0, Math.min(index, len - 1))
  }

  function scrollToTop() {
    const el = document.querySelector('.fixed.inset-0 .overflow-y-auto') as HTMLElement | null
    if (el?.scrollTo) el.scrollTo({ top: 0, behavior: 'smooth' })
  }

  function handleSlideMouseMove() {
    if (slideFullscreen.value) {
      showSlideControls.value = true
      resetControlsTimer()
    }
  }

  function handleSlideMouseLeave() {
    if (slideFullscreen.value) resetControlsTimer()
  }

  function handleControlsMouseEnter() {
    if (slideFullscreen.value) {
      clearControlsTimer()
      showSlideControls.value = true
    }
  }

  function handleControlsMouseLeave() {
    if (slideFullscreen.value) resetControlsTimer()
  }

  /** 处理幻灯片相关键盘事件；若已处理返回 true */
  function handleSlideKeydown(e: KeyboardEvent): boolean {
    if (e.key === 'Escape') {
      if (slideFullscreen.value && isSlideNativeFullscreen.value) {
        toggleSlideFullscreen()
        return true
      }
      return false
    }
    if (!slideMode.value) return false
    if (['ArrowLeft', 'ArrowRight', 'Space', 'Enter', 'Home', 'End'].includes(e.key)) {
      e.preventDefault()
    }
    const list = displayCells.value ?? []
    switch (e.key) {
      case 'ArrowLeft':
        goToPreviousSlide()
        return true
      case 'ArrowRight':
      case 'Space':
      case 'Enter':
        goToNextSlide()
        return true
      case 'Home':
        goToSlide(0)
        return true
      case 'End':
        goToSlide(list.length - 1)
        return true
      default:
        return false
    }
  }

  watch(isSlideNativeFullscreen, (v) => {
    slideFullscreen.value = v
    if (v) {
      showSlideControls.value = true
      resetControlsTimer()
    } else clearControlsTimer()
  })

  watch(slideFullscreen, (v) => {
    if (v) {
      showSlideControls.value = true
      resetControlsTimer()
    } else clearControlsTimer()
  })

  watch(slideMode, (v) => {
    if (v && isFullscreenPreview.value) {
      currentSlideIndex.value = 0
      slideFullscreen.value = false
    }
  })

  watch(
    () => (displayCells.value ?? []).length,
    (len) => {
      if (slideMode.value && currentSlideIndex.value >= len) {
        currentSlideIndex.value = Math.max(0, len - 1)
      }
    }
  )

  return {
    slideMode,
    currentSlideIndex,
    slideFullscreen,
    showSlideControls,
    currentCell,
    isSlideNativeFullscreen,
    toggleSlideFullscreen,
    goToPreviousSlide,
    goToNextSlide,
    goToSlide,
    scrollToTop,
    handleSlideMouseMove,
    handleSlideMouseLeave,
    handleControlsMouseEnter,
    handleControlsMouseLeave,
    resetControlsTimer,
    clearControlsTimer,
    handleSlideKeydown,
  }
}

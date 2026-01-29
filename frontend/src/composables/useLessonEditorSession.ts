/**
 * 教案编辑器 - 课堂 Session：sessionId、provide、与 TeacherControlPanel 的各类 watch 与轮询
 */

import { ref, computed, watch, onMounted, onUnmounted, type Ref, type WatchStopHandle } from 'vue'

export function useLessonEditorSession(
  teacherControlPanelRef: Ref<any>,
  isPreviewMode: Ref<boolean>,
  showClassroomPanel: Ref<boolean>
) {
  const currentSessionId = ref<number | undefined>(undefined)
  const providedSessionRef = ref<any>(null)
  let isUnmounted = false

  const providedSessionId = computed(() => {
    if (isUnmounted) return currentSessionId.value
    if (providedSessionRef.value?.id != null) return providedSessionRef.value.id
    const panel = teacherControlPanelRef.value
    if (!panel) return currentSessionId.value
    try {
      if (panel?.sessionId?.value != null) return panel.sessionId.value
      if (panel?.session?.value?.id != null) return panel.session.value.id
    } catch (e) {
      // 组件可能已销毁，忽略错误
      return currentSessionId.value
    }
    return currentSessionId.value
  })

  function handleSessionChanged(session: any | null) {
    if (isUnmounted) return
    if (session?.id) {
      currentSessionId.value = session.id
      providedSessionRef.value = session
    } else {
      currentSessionId.value = undefined
      providedSessionRef.value = null
    }
  }

  function checkSessionId() {
    if (isUnmounted) return
    if (!isPreviewMode.value || !showClassroomPanel.value || !teacherControlPanelRef.value) return
    const panel = teacherControlPanelRef.value as any
    if (!panel) return
    try {
      const id = panel?.sessionId?.value ?? panel?.session?.value?.id
      if (id != null && id !== currentSessionId.value) currentSessionId.value = id
    } catch (e) {
      // 组件可能已销毁，忽略错误
    }
  }

  const panelSession = computed(() => {
    if (isUnmounted || !teacherControlPanelRef.value) return null
    const panel = teacherControlPanelRef.value as any
    if (!panel) return null
    try {
      return panel?.session?.value ?? null
    } catch (e) {
      // 组件可能已销毁，忽略错误
      return null
    }
  })

  const stopWatch1 = watch(panelSession, (v) => {
    if (isUnmounted) return
    if (v?.id) providedSessionRef.value = v
  }, { immediate: true, deep: true })

  const stopWatch2 = watch(
    () => {
      if (isUnmounted) return undefined
      if (!isPreviewMode.value || !showClassroomPanel.value) return undefined
      const panel = teacherControlPanelRef.value as any
      if (!panel) return undefined
      try {
        if (panel?.sessionId?.value != null) return panel.sessionId.value
        if (panel?.session?.value?.id != null) return panel.session.value.id
      } catch (e) {
        // 组件可能已销毁，忽略错误
        return undefined
      }
      return undefined
    },
    (id) => {
      if (isUnmounted) return
      if (id != null && id !== currentSessionId.value) currentSessionId.value = id
      else if (id == null && currentSessionId.value != null) currentSessionId.value = undefined
    },
    { immediate: true, deep: true }
  )

  const stopWatch3 = watch(teacherControlPanelRef, (panel) => {
    if (isUnmounted) return
    if (panel && isPreviewMode.value && showClassroomPanel.value) {
      try {
        const p = panel as any
        const id = p?.sessionId?.value ?? p?.session?.value?.id
        if (id != null && id !== currentSessionId.value) currentSessionId.value = id
      } catch (e) {
        // 组件可能已销毁，忽略错误
      }
    }
  }, { immediate: true, deep: true })

  let sessionIdCheckInterval: ReturnType<typeof setInterval> | null = null
  let mountedCheckInterval: ReturnType<typeof setInterval> | null = null

  const stopWatch4 = watch(
    [isPreviewMode, showClassroomPanel, teacherControlPanelRef],
    ([preview, show, panel]) => {
      if (isUnmounted) {
        if (sessionIdCheckInterval) {
          clearInterval(sessionIdCheckInterval)
          sessionIdCheckInterval = null
        }
        return
      }
      if (preview && show && panel && !sessionIdCheckInterval) {
        let n = 0
        sessionIdCheckInterval = setInterval(() => {
          if (isUnmounted || currentSessionId.value != null || n >= 10) {
            if (sessionIdCheckInterval) {
              clearInterval(sessionIdCheckInterval)
              sessionIdCheckInterval = null
            }
            return
          }
          // 检查组件是否已销毁
          if (!panel) {
            if (sessionIdCheckInterval) {
              clearInterval(sessionIdCheckInterval)
              sessionIdCheckInterval = null
            }
            return
          }
          try {
            const p = panel as any
            const id = p?.sessionId?.value ?? p?.session?.value?.id
            if (id != null) {
              currentSessionId.value = id
              if (sessionIdCheckInterval) {
                clearInterval(sessionIdCheckInterval)
                sessionIdCheckInterval = null
              }
            }
          } catch (e) {
            // 组件可能已销毁，忽略错误
            if (sessionIdCheckInterval) {
              clearInterval(sessionIdCheckInterval)
              sessionIdCheckInterval = null
            }
          }
          n++
        }, 500)
      } else if ((!preview || !show || !panel) && sessionIdCheckInterval) {
        clearInterval(sessionIdCheckInterval)
        sessionIdCheckInterval = null
      }
    },
    { immediate: true }
  )

  onMounted(() => {
    setTimeout(() => {
      if (isUnmounted) return
      checkSessionId()
      let n = 0
      mountedCheckInterval = setInterval(() => {
        if (isUnmounted) {
          if (mountedCheckInterval) {
            clearInterval(mountedCheckInterval)
            mountedCheckInterval = null
          }
          return
        }
        checkSessionId()
        n++
        if (currentSessionId.value != null || n >= 10) {
          if (mountedCheckInterval) {
            clearInterval(mountedCheckInterval)
            mountedCheckInterval = null
          }
        }
      }, 500)
    }, 100)
  })

  onUnmounted(() => {
    isUnmounted = true
    // 停止所有 watch
    stopWatch1()
    stopWatch2()
    stopWatch3()
    stopWatch4()
    // 清理所有定时器
    if (sessionIdCheckInterval) {
      clearInterval(sessionIdCheckInterval)
      sessionIdCheckInterval = null
    }
    if (mountedCheckInterval) {
      clearInterval(mountedCheckInterval)
      mountedCheckInterval = null
    }
  })

  return {
    currentSessionId,
    providedSessionRef,
    providedSessionId,
    handleSessionChanged,
    checkSessionId,
  }
}

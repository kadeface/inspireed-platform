/**
 * 教案编辑器 - 课堂 Session：sessionId、provide、与 TeacherControlPanel 的各类 watch 与轮询
 */

import { ref, computed, watch, onMounted, type Ref } from 'vue'

export function useLessonEditorSession(
  teacherControlPanelRef: Ref<any>,
  isPreviewMode: Ref<boolean>,
  showClassroomPanel: Ref<boolean>
) {
  const currentSessionId = ref<number | undefined>(undefined)
  const providedSessionRef = ref<any>(null)

  const providedSessionId = computed(() => {
    if (providedSessionRef.value?.id != null) return providedSessionRef.value.id
    const panel = teacherControlPanelRef.value
    if (panel?.sessionId?.value != null) return panel.sessionId.value
    if (panel?.session?.value?.id != null) return panel.session.value.id
    return currentSessionId.value
  })

  function handleSessionChanged(session: any | null) {
    if (session?.id) {
      currentSessionId.value = session.id
      providedSessionRef.value = session
    } else {
      currentSessionId.value = undefined
      providedSessionRef.value = null
    }
  }

  function checkSessionId() {
    if (!isPreviewMode.value || !showClassroomPanel.value || !teacherControlPanelRef.value) return
    const panel = teacherControlPanelRef.value as any
    const id = panel?.sessionId?.value ?? panel?.session?.value?.id
    if (id != null && id !== currentSessionId.value) currentSessionId.value = id
  }

  const panelSession = computed(() => {
    if (!teacherControlPanelRef.value) return null
    const panel = teacherControlPanelRef.value as any
    return panel?.session?.value ?? null
  })

  watch(panelSession, (v) => {
    if (v?.id) providedSessionRef.value = v
  }, { immediate: true, deep: true })

  watch(
    () => {
      if (!isPreviewMode.value || !showClassroomPanel.value) return undefined
      const panel = teacherControlPanelRef.value as any
      if (panel?.sessionId?.value != null) return panel.sessionId.value
      if (panel?.session?.value?.id != null) return panel.session.value.id
      return undefined
    },
    (id) => {
      if (id != null && id !== currentSessionId.value) currentSessionId.value = id
      else if (id == null && currentSessionId.value != null) currentSessionId.value = undefined
    },
    { immediate: true, deep: true }
  )

  watch(teacherControlPanelRef, (panel) => {
    if (panel && isPreviewMode.value && showClassroomPanel.value) {
      const p = panel as any
      const id = p?.sessionId?.value ?? p?.session?.value?.id
      if (id != null && id !== currentSessionId.value) currentSessionId.value = id
    }
  }, { immediate: true, deep: true })

  let sessionIdCheckInterval: ReturnType<typeof setInterval> | null = null
  watch(
    [isPreviewMode, showClassroomPanel, teacherControlPanelRef],
    ([preview, show, panel]) => {
      if (preview && show && panel && !sessionIdCheckInterval) {
        let n = 0
        sessionIdCheckInterval = setInterval(() => {
          if (currentSessionId.value != null || n >= 10) {
            if (sessionIdCheckInterval) {
              clearInterval(sessionIdCheckInterval)
              sessionIdCheckInterval = null
            }
            return
          }
          const p = panel as any
          const id = p?.sessionId?.value ?? p?.session?.value?.id
          if (id != null) {
            currentSessionId.value = id
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
      checkSessionId()
      let n = 0
      const id = setInterval(() => {
        checkSessionId()
        n++
        if (currentSessionId.value != null || n >= 10) clearInterval(id)
      }, 500)
    }, 100)
  })

  return {
    currentSessionId,
    providedSessionRef,
    providedSessionId,
    handleSessionChanged,
    checkSessionId,
  }
}

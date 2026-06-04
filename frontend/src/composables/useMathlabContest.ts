/**
 * MathLab 课堂竞赛 — 教师/学生共享状态
 */

import { ref, computed, onUnmounted, type Ref } from 'vue'
import { mathlabContestService } from '@/services/mathlabContest'
import type {
  MathlabContest,
  MathlabContestLeaderboard,
  MathlabContestSubmission,
} from '@/types/mathlabContest'
import type { WebSocketMessage } from '@/services/websocket'

const activeContest = ref<MathlabContest | null>(null)
const leaderboard = ref<MathlabContestLeaderboard | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

export function useMathlabContestState() {
  return { activeContest, leaderboard, loading, error }
}

/** 刷新指定竞赛排行榜（供 SimCell 提交后拉取排名） */
export async function refreshMathlabContestLeaderboard(contestId: number) {
  leaderboard.value = await mathlabContestService.getLeaderboard(contestId)
  return leaderboard.value
}

export function useMathlabContest(sessionId: Ref<number | undefined>) {
  async function refreshActive() {
    const sid = sessionId.value
    if (!sid) {
      activeContest.value = null
      return null
    }
    loading.value = true
    error.value = null
    try {
      activeContest.value = await mathlabContestService.getActive(sid)
      if (activeContest.value) {
        await refreshLeaderboard(activeContest.value.id)
      } else {
        leaderboard.value = null
      }
      return activeContest.value
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : '加载竞赛失败'
      return null
    } finally {
      loading.value = false
    }
  }

  async function refreshLeaderboard(contestId: number) {
    leaderboard.value = await mathlabContestService.getLeaderboard(contestId)
  }

  function handleWsMessage(message: WebSocketMessage) {
    const type = message.type as string
    const data = message.data || {}
    if (type === 'mathlab_contest_started') {
      activeContest.value = {
        id: Number(data.contest_id),
        sessionId: Number(data.session_id),
        cellId: data.cell_id != null ? Number(data.cell_id) : undefined,
        teacherId: 0,
        taskId: String(data.task_id),
        status: 'running',
        timeLimitSec: data.time_limit_sec != null ? Number(data.time_limit_sec) : undefined,
        allowResubmit: Boolean(data.allow_resubmit),
        passThreshold: Number(data.pass_threshold ?? 85),
        settings: (data.settings as Record<string, unknown>) || {},
        startedAt: new Date().toISOString(),
        endsAt: data.ends_at ? String(data.ends_at) : undefined,
      }
      if (activeContest.value.id) {
        refreshLeaderboard(activeContest.value.id).catch(() => {})
      }
    } else if (type === 'mathlab_contest_task_changed' && activeContest.value) {
      activeContest.value = { ...activeContest.value, taskId: String(data.task_id) }
    } else if (type === 'mathlab_contest_ended') {
      if (activeContest.value?.id === Number(data.contest_id)) {
        activeContest.value = { ...activeContest.value, status: 'ended' }
      }
    } else if (type === 'mathlab_contest_submission' && activeContest.value?.id === Number(data.contest_id)) {
      refreshLeaderboard(activeContest.value.id).catch(() => {})
    }
  }

  return {
    activeContest,
    leaderboard,
    loading,
    error,
    refreshActive,
    refreshLeaderboard,
    handleWsMessage,
  }
}

/** 向 mathlab iframe 发送竞赛事件 */
export function postContestToIframe(
  iframe: HTMLIFrameElement | null | undefined,
  type: string,
  data: Record<string, unknown> = {}
) {
  if (!iframe?.contentWindow) return
  iframe.contentWindow.postMessage({ source: 'inspireed', type, data }, '*')
}

/** SimCell 监听 iframe 提交 */
export function useMathlabContestBridge(options: {
  iframeRef: Ref<HTMLIFrameElement | null | undefined>
  contestId: Ref<number | undefined>
  passThreshold: Ref<number>
  onSubmitted?: (submission: MathlabContestSubmission) => void
}) {
  function onMessage(event: MessageEvent) {
    const msg = event.data
    if (!msg || msg.source !== 'mathlab' || msg.type !== 'contest:submit') return
    const cid = options.contestId.value
    if (!cid) return
    const msgData = (msg.data || {}) as Record<string, unknown>
    const analysis = (msgData.analysis || {}) as Record<string, unknown>
    const autoScore = Number(
      msgData.autoScore ?? analysis.matchPercent ?? analysis.autoScore ?? 0
    )
    const threshold = options.passThreshold.value
    const autoPassed =
      autoScore >= threshold ||
      Boolean(msgData.autoPassed ?? analysis.autoPassed)
    const payload: Record<string, unknown> = {
      ...analysis,
      taskId: msgData.taskId ?? analysis.taskId,
      travelSubtype: msgData.travelSubtype ?? analysis.subtype ?? null,
      meetTimeSec: msgData.meetTimeSec ?? analysis.meetTimeSec ?? null,
      finalDistanceCm: msgData.finalDistanceCm ?? analysis.finalDistanceCm ?? null,
      parametricSummary:
        analysis.parametricSummary ?? analysis.parametric ?? null,
    }
    if (Array.isArray(analysis.trailSample)) {
      payload.trailSample = analysis.trailSample
    }
    mathlabContestService
      .submit(cid, {
        autoScore,
        autoPassed,
        elapsedSec:
          msgData.elapsedSec != null ? Number(msgData.elapsedSec) : undefined,
        payload,
      })
      .then((submission) => options.onSubmitted?.(submission))
      .catch((err) => console.error('MathLab contest submit failed', err))
  }

  if (typeof window !== 'undefined') {
    window.addEventListener('message', onMessage)
    onUnmounted(() => window.removeEventListener('message', onMessage))
  }

  return { postContestToIframe: (type: string, data?: Record<string, unknown>) =>
    postContestToIframe(options.iframeRef.value ?? null, type, data) }
}

/**
 * useDurationTimer Composable 单元测试
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { ref, nextTick } from 'vue'
import { useDurationTimer } from '@/components/Classroom/composables/useDurationTimer'

describe('useDurationTimer', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  // Mock 数据
  const mockGetSessionStatus = vi.fn(() => 'preparing')

  it('应该正确初始化状态', () => {
    const { sessionDuration, durationInterval } = useDurationTimer({
      getSessionStatus: mockGetSessionStatus,
    })

    expect(sessionDuration.value).toBe(0)
    expect(durationInterval.value).toBeNull()
  })

  it('应该启动计时器', () => {
    const onTimerStateChange = vi.fn()
    const { sessionDuration, durationInterval, startDurationTimer } = useDurationTimer({
      getSessionStatus: mockGetSessionStatus,
      onTimerStateChange,
    })

    startDurationTimer()

    expect(durationInterval.value).not.toBeNull()
    expect(onTimerStateChange).toHaveBeenCalledWith(true)

    // 快进1秒
    vi.advanceTimersByTime(1000)

    expect(sessionDuration.value).toBe(1)

    // 快进到10秒
    vi.advanceTimersByTime(9000)

    expect(sessionDuration.value).toBe(10)
  })

  it('应该停止计时器', () => {
    const onTimerStateChange = vi.fn()
    const { sessionDuration, durationInterval, startDurationTimer, stopDurationTimer } = useDurationTimer({
      getSessionStatus: mockGetSessionStatus,
      onTimerStateChange,
    })

    startDurationTimer()
    vi.advanceTimersByTime(5000)

    expect(sessionDuration.value).toBe(5)
    expect(durationInterval.value).not.toBeNull()

    stopDurationTimer()

    expect(durationInterval.value).toBeNull()
    expect(onTimerStateChange).toHaveBeenCalledWith(false)

    // 再快进5秒（计时器已停止，不应增加）
    vi.advanceTimersByTime(5000)

    expect(sessionDuration.value).toBe(5) // 保持不变
  })

  it('应该重置计时器', () => {
    const { sessionDuration, startDurationTimer, resetDurationTimer } = useDurationTimer({
      getSessionStatus: mockGetSessionStatus,
    })

    startDurationTimer()
    vi.advanceTimersByTime(10000)

    expect(sessionDuration.value).toBe(10)

    resetDurationTimer()

    expect(sessionDuration.value).toBe(0)
  })

  it('应该支持自定义课程时长', () => {
    const customDuration = 60 * 30 // 30分钟
    const { sessionDuration, startDurationTimer } = useDurationTimer({
      getSessionStatus: mockGetSessionStatus,
      lessonDuration: customDuration,
    })

    startDurationTimer()

    // 快进到课程时长
    vi.advanceTimersByTime(customDuration * 1000)

    expect(sessionDuration.value).toBe(customDuration)

    // 再快进，应该不超过课程时长
    vi.advanceTimersByTime(10000)

    expect(sessionDuration.value).toBe(customDuration) // 保持最大值
  })

  it('应该正确计算剩余时间', () => {
    const { sessionDuration, startDurationTimer, getRemainingTime } = useDurationTimer({
      getSessionStatus: mockGetSessionStatus,
      lessonDuration: 100, // 100秒
    })

    expect(getRemainingTime()).toBe(100)

    startDurationTimer()
    vi.advanceTimersByTime(30000)

    expect(sessionDuration.value).toBe(30)
    expect(getRemainingTime()).toBe(70)

    vi.advanceTimersByTime(70000)

    expect(sessionDuration.value).toBe(100)
    expect(getRemainingTime()).toBe(0) // 不应该为负数
  })

  it('应该只在 active/teaching 状态显示时长', () => {
    const mockGetSessionStatusDynamic = vi.fn(() => 'preparing')
    const { sessionDuration, getDisplayDuration } = useDurationTimer({
      getSessionStatus: mockGetSessionStatusDynamic,
    })

    // preparing 状态：不显示时长
    expect(getDisplayDuration()).toBe(0)

    sessionDuration.value = 50
    expect(getDisplayDuration()).toBe(0)

    // active 状态：显示时长
    mockGetSessionStatusDynamic.mockReturnValue('active')
    expect(getDisplayDuration()).toBe(50)

    // teaching 状态：显示时长
    mockGetSessionStatusDynamic.mockReturnValue('teaching')
    expect(getDisplayDuration()).toBe(50)

    // ended 状态：不显示时长
    mockGetSessionStatusDynamic.mockReturnValue('ended')
    expect(getDisplayDuration()).toBe(0)
  })

  it('应该监听会话状态并自动启动计时器', async () => {
    const sessionStatus = ref<string | null>('preparing')
    const onTimerStateChange = vi.fn()

    const { sessionDuration, watchSessionStatus } = useDurationTimer({
      getSessionStatus: () => sessionStatus.value,
      onTimerStateChange,
    })

    watchSessionStatus(sessionStatus)

    expect(sessionDuration.value).toBe(0)

    // 切换到 active 状态
    sessionStatus.value = 'active'
    await nextTick()

    // 计时器应该已启动
    vi.advanceTimersByTime(1000)

    expect(sessionDuration.value).toBe(1)
    expect(onTimerStateChange).toHaveBeenCalledWith(true)
  })

  it('应该在状态从 preparing 切换到 active 时重置时长', async () => {
    const sessionStatus = ref('preparing')

    const { sessionDuration, watchSessionStatus } = useDurationTimer({
      getSessionStatus: () => sessionStatus.value,
    })

    watchSessionStatus(sessionStatus)

    // 先设置一些时长
    sessionDuration.value = 50

    // 切换到 active（从 preparing 来，应该重置为0）
    sessionStatus.value = 'active'
    await nextTick()

    expect(sessionDuration.value).toBe(0)

    // 快进1秒，应该从0开始计时
    vi.advanceTimersByTime(1000)

    expect(sessionDuration.value).toBe(1)
  })

  it('应该在状态切换时停止计时器', async () => {
    const sessionStatus = ref('active')
    const onTimerStateChange = vi.fn()

    const { sessionDuration, durationInterval, watchSessionStatus } = useDurationTimer({
      getSessionStatus: () => sessionStatus.value,
      onTimerStateChange,
    })

    watchSessionStatus(sessionStatus)
    await nextTick()

    // 计时器应该已启动
    vi.advanceTimersByTime(5000)

    expect(sessionDuration.value).toBe(5)
    expect(durationInterval.value).not.toBeNull()

    // 切换到 ended 状态
    sessionStatus.value = 'ended'
    await nextTick()

    expect(durationInterval.value).toBeNull()
    expect(onTimerStateChange).toHaveBeenCalledWith(false)

    // 再快进，时长不应增加
    vi.advanceTimersByTime(5000)

    expect(sessionDuration.value).toBe(5)
  })

  it('应该支持多次启动而不重复创建定时器', () => {
    const { durationInterval, startDurationTimer } = useDurationTimer({
      getSessionStatus: mockGetSessionStatus,
    })

    startDurationTimer()
    const firstInterval = durationInterval.value

    startDurationTimer()
    const secondInterval = durationInterval.value

    expect(firstInterval).toBe(secondInterval) // 应该是同一个定时器
  })

  it('应该正确处理 paused 状态', async () => {
    const sessionStatus = ref('active')
    const onTimerStateChange = vi.fn()

    const { sessionDuration, durationInterval, watchSessionStatus } = useDurationTimer({
      getSessionStatus: () => sessionStatus.value,
      onTimerStateChange,
    })

    watchSessionStatus(sessionStatus)
    await nextTick()

    // active 状态：计时器运行
    vi.advanceTimersByTime(10000)

    expect(sessionDuration.value).toBe(10)
    expect(durationInterval.value).not.toBeNull()

    // 切换到 paused 状态：停止计时但保持时长
    sessionStatus.value = 'paused'
    await nextTick()

    expect(durationInterval.value).toBeNull()
    expect(sessionDuration.value).toBe(10) // 保持当前时长
    expect(onTimerStateChange).toHaveBeenCalledWith(false)

    // 再快进，时长不应增加
    vi.advanceTimersByTime(5000)

    expect(sessionDuration.value).toBe(10)
  })

  it('应该支持暂停后恢复（从 paused 切回 active）', async () => {
    const sessionStatus = ref('active')

    const { sessionDuration, watchSessionStatus } = useDurationTimer({
      getSessionStatus: () => sessionStatus.value,
    })

    watchSessionStatus(sessionStatus)
    await nextTick()

    // active 状态：计时到10秒
    vi.advanceTimersByTime(10000)

    expect(sessionDuration.value).toBe(10)

    // 切换到 paused
    sessionStatus.value = 'paused'
    await nextTick()

    expect(sessionDuration.value).toBe(10)

    // 切换回 active（不是从 preparing 来，应该从10继续）
    sessionStatus.value = 'active'
    await nextTick()

    expect(sessionDuration.value).toBe(10) // 保持10

    // 再计时5秒
    vi.advanceTimersByTime(5000)

    expect(sessionDuration.value).toBe(15) // 从10继续到15
  })

  it('应该使用默认课程时长（40分钟）', () => {
    const { startDurationTimer, getRemainingTime } = useDurationTimer({
      getSessionStatus: mockGetSessionStatus,
    })

    const expectedDefaultDuration = 40 * 60 // 2400秒

    expect(getRemainingTime()).toBe(expectedDefaultDuration)

    startDurationTimer()

    // 快进到默认时长
    vi.advanceTimersByTime(expectedDefaultDuration * 1000)

    expect(getRemainingTime()).toBe(0)
  })
})

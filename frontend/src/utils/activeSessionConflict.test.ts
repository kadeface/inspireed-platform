import { describe, expect, it } from 'vitest'
import {
  isActiveSessionConflict,
  isHiddenFromStudents,
  isUnfinishedClassSession,
  readExistingSessionId,
} from './activeSessionConflict'

const MINUTE = 60 * 1000
const HOUR = 60 * MINUTE

describe('isHiddenFromStudents', () => {
  const now = Date.parse('2026-10-21T07:00:00Z')

  it('hides a teaching session that started more than 40 minutes ago', () => {
    expect(
      isHiddenFromStudents(
        { status: 'TEACHING', actual_start: new Date(now - 41 * MINUTE).toISOString() },
        now,
      ),
    ).toBe(true)
  })

  it('keeps a teaching session that started within 40 minutes', () => {
    expect(
      isHiddenFromStudents(
        { status: 'teaching', actualStart: new Date(now - 39 * MINUTE).toISOString() },
        now,
      ),
    ).toBe(false)
  })

  it('uses created_at when a teaching session has no actual start', () => {
    expect(
      isHiddenFromStudents(
        { status: 'TEACHING', created_at: new Date(now - 41 * MINUTE).toISOString() },
        now,
      ),
    ).toBe(true)
  })

  it('hides a preparing session created more than 48 hours ago', () => {
    expect(
      isHiddenFromStudents(
        { status: 'PREPARING', createdAt: new Date(now - 49 * HOUR).toISOString() },
        now,
      ),
    ).toBe(true)
  })

  it('keeps a preparing session created within 48 hours', () => {
    expect(
      isHiddenFromStudents(
        { status: 'preparing', created_at: new Date(now - 47 * HOUR).toISOString() },
        now,
      ),
    ).toBe(false)
  })
})

describe('isUnfinishedClassSession', () => {
  it('treats preparing and teaching as unfinished', () => {
    expect(isUnfinishedClassSession({ status: 'PREPARING' })).toBe(true)
    expect(isUnfinishedClassSession({ status: 'teaching' })).toBe(true)
    expect(isUnfinishedClassSession({ status: 'ENDED' })).toBe(false)
  })
})

describe('readExistingSessionId', () => {
  it('reads the id from a structured conflict payload', () => {
    const error = {
      response: {
        status: 409,
        data: {
          detail: { code: 'active_session_exists', existing_session_id: 42 },
        },
      },
    }
    expect(isActiveSessionConflict(error)).toBe(true)
    expect(readExistingSessionId(error)).toBe(42)
  })

  it('reads the id from the legacy Chinese message', () => {
    const error = {
      response: {
        status: 400,
        data: { detail: '该班级已有活跃的课堂会话（ID: 17），请先结束或使用现有会话' },
      },
    }
    expect(isActiveSessionConflict(error)).toBe(true)
    expect(readExistingSessionId(error)).toBe(17)
  })

  it('treats the integrity-error wording as the same conflict', () => {
    const error = {
      message: '创建会话失败：无法创建课堂：该教案与班级下已有未结束的会话，或数据冲突。',
    }
    expect(isActiveSessionConflict(error)).toBe(true)
    expect(readExistingSessionId(error)).toBeNull()
  })
})

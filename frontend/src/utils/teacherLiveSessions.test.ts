import { describe, expect, it } from 'vitest'
import { groupLiveClassroomsByLesson } from './teacherLiveSessions'

describe('groupLiveClassroomsByLesson', () => {
  it('groups classroom names by lesson and drops duplicates', () => {
    expect(
      groupLiveClassroomsByLesson([
        { lesson_id: 64, classroom_id: 3, classroom_name: '七年级一班' },
        { lesson_id: 64, classroom_id: 3, classroom_name: '七年级一班' },
        { lesson_id: 64, classroom_id: 8, classroom_name: '七年级二班' },
        { lesson_id: 12, classroom_id: 1, classroom_name: '  ' },
      ]),
    ).toEqual({
      64: ['七年级一班', '七年级二班'],
      12: ['班级 1'],
    })
  })
})

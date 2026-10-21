export interface TeacherLiveSession {
  lesson_id: number
  classroom_id: number
  classroom_name?: string | null
}

/** 同一课例可能同时在多个班上课，班级名按出现顺序去重。 */
export function groupLiveClassroomsByLesson(
  sessions: TeacherLiveSession[],
): Record<number, string[]> {
  const grouped: Record<number, string[]> = {}
  for (const session of sessions) {
    const lessonId = session.lesson_id
    if (!Number.isFinite(lessonId)) continue
    const name =
      (session.classroom_name && session.classroom_name.trim()) ||
      (session.classroom_id ? `班级 ${session.classroom_id}` : '')
    if (!name) continue
    const names = grouped[lessonId] ?? []
    if (!names.includes(name)) names.push(name)
    grouped[lessonId] = names
  }
  return grouped
}

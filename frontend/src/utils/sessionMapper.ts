import type { ClassSession, StudentParticipation } from '@/types/classroomSession'

/**
 * Map a raw API response (snake_case) to ClassSession (camelCase).
 * Handles both snake_case and camelCase inputs gracefully.
 */
export function mapClassSession(raw: Record<string, any>): ClassSession {
  return {
    ...raw,
    id: raw.id,
    lessonId: raw.lesson_id ?? raw.lessonId,
    classroomId: raw.classroom_id ?? raw.classroomId,
    teacherId: raw.teacher_id ?? raw.teacherId,
    status: raw.status,
    scheduledStart: raw.scheduled_start ?? raw.scheduledStart,
    actualStart: raw.actual_start ?? raw.actualStart,
    endedAt: raw.ended_at ?? raw.endedAt,
    durationMinutes: raw.duration_minutes ?? raw.durationMinutes,
    currentCellId: raw.current_cell_id ?? raw.currentCellId ?? null,
    currentActivityId: raw.current_activity_id ?? raw.currentActivityId ?? null,
    settings: raw.settings ?? {},
    totalStudents: raw.total_students ?? raw.totalStudents ?? 0,
    activeStudents: raw.active_students ?? raw.activeStudents ?? 0,
    guestAccessEnabled: raw.guest_access_enabled ?? raw.guestAccessEnabled ?? false,
    guestAccessCode: raw.guest_access_code ?? raw.guestAccessCode ?? null,
    guestCount: raw.guest_count ?? raw.guestCount ?? 0,
    createdAt: raw.created_at ?? raw.createdAt,
    updatedAt: raw.updated_at ?? raw.updatedAt,
    lessonTitle: raw.lesson_title ?? raw.lessonTitle,
    classroomName: raw.classroom_name ?? raw.classroomName,
    teacherName: raw.teacher_name ?? raw.teacherName,
  } as ClassSession
}

/**
 * Map a raw API response to StudentParticipation.
 */
export function mapParticipation(raw: Record<string, any>): StudentParticipation {
  return {
    ...raw,
    id: raw.id,
    sessionId: raw.session_id ?? raw.sessionId,
    studentId: raw.student_id ?? raw.studentId,
    joinedAt: raw.joined_at ?? raw.joinedAt,
    lastActiveAt: raw.last_active_at ?? raw.lastActiveAt,
    leftAt: raw.left_at ?? raw.leftAt,
    isActive: raw.is_active ?? raw.isActive ?? true,
    currentCellId: raw.current_cell_id ?? raw.currentCellId ?? null,
    completedCells: raw.completed_cells ?? raw.completedCells ?? [],
    progressPercentage: raw.progress_percentage ?? raw.progressPercentage ?? 0,
    studentName: raw.student_name ?? raw.studentName,
    studentEmail: raw.student_email ?? raw.studentEmail,
  } as StudentParticipation
}

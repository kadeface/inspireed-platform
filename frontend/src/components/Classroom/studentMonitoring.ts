/**
 * 学生监控工具函数
 *
 * 用于计算学生状态、参与度、得分等监控指标
 */

import type { ActivityCell } from '@/types/cell'

/**
 * 获取学生状态类（用于指示器颜色）
 * @param student - 学生对象
 * @param currentCell - 当前活动模块
 * @param studentSubmissionStatus - 学生提交状态映射
 * @returns CSS类名
 */
export function getStudentStatusClass(
  student: any,
  currentCell: any,
  studentSubmissionStatus: Map<string, string>
): string {
  // 如果当前是活动模块，根据提交状态显示颜色
  if (currentCell && currentCell.type === 'activity' && studentSubmissionStatus.size > 0) {
    // 尝试多种可能的ID字段
    const studentId = student.id || student.userId || student.user_id || student.studentId || student.student_id
    const submissionStatus = studentId ? studentSubmissionStatus.get(String(studentId)) : null

    // 已提交：绿色
    if (submissionStatus === 'submitted' || submissionStatus === 'graded') {
      return 'indicator-green'
    }
    // 未提交（包括 not_started, draft）：红色
    if (submissionStatus === 'not_started' || submissionStatus === 'draft' || !submissionStatus) {
      return 'indicator-red'
    }
    // 其他状态：黄色
    return 'indicator-yellow'
  }

  // 非活动模块，根据进度显示颜色
  const progress = student.progressPercentage || student.progress_percentage || 0
  if (progress >= 80) return 'indicator-green'
  if (progress >= 50) return 'indicator-yellow'
  return 'indicator-red'
}

/**
 * 获取学生提示信息
 * @param student - 学生对象
 * @param currentCell - 当前活动模块
 * @param studentSubmissionStatus - 学生提交状态映射
 * @returns 提示文本
 */
export function getStudentTooltip(
  student: any,
  currentCell: any,
  studentSubmissionStatus: Map<string, string>
): string {
  const name = student.studentName || student.student_name || '学生'
  const account = getStudentAccount(student)
  const progress = Math.round(student.progressPercentage || student.progress_percentage || 0)

  // 如果当前是活动模块，添加提交状态信息
  if (currentCell && currentCell.type === 'activity' && studentSubmissionStatus.size > 0) {
    // 尝试多种可能的ID字段
    const studentId = student.id || student.userId || student.user_id || student.studentId || student.student_id
    const submissionStatus = studentId ? studentSubmissionStatus.get(String(studentId)) : null
    const statusLabels: Record<string, string> = {
      'not_started': '未开始',
      'draft': '草稿',
      'submitted': '已提交',
      'graded': '已评分',
      'returned': '已退回',
    }
    const statusLabel = submissionStatus ? statusLabels[submissionStatus] || submissionStatus : '未开始'
    return `${name} (${account}) - 进度: ${progress}% - 提交状态: ${statusLabel}`
  }

  return `${name} (${account}) - 进度: ${progress}%`
}

/**
 * 获取学生登录账号
 * @param student - 学生对象
 * @returns 学生账号
 */
export function getStudentAccount(student: any): string {
  // 尝试多种可能的字段名，但不包括姓名字段
  return student.username ||
         student.account ||
         student.loginAccount ||
         student.login_account ||
         student.userAccount ||
         student.user_account ||
         student.email ||
         student.user_id?.toString() ||
         student.id?.toString() ||
         '未知账号'
}

/**
 * 计算参与度（基于在线学生和总学生的比例，以及平均进度）
 * @param activeStudents - 在线学生列表
 * @param totalStudents - 总学生数
 * @param averageProgress - 平均进度
 * @returns 参与度（0-100）
 */
export function calculateParticipationRate(
  activeStudents: any[],
  totalStudents: number,
  averageProgress: number
): number {
  if (totalStudents === 0) return 0
  const onlineRatio = (activeStudents.length / totalStudents) * 100
  // 综合在线率和平均进度
  return Math.round((onlineRatio * 0.6 + averageProgress * 0.4))
}

/**
 * 计算平均得分
 * @param averageScore - 实际平均得分（如果有）
 * @param averageProgress - 平均进度
 * @returns 平均得分
 */
export function calculateAverageScore(
  averageScore: number | undefined,
  averageProgress: number
): number {
  if (averageScore !== undefined) {
    return Math.round(averageScore)
  }
  // 如果没有得分数据，基于进度估算
  return Math.round(averageProgress * 0.8) // 假设进度和得分有一定相关性
}

/**
 * 计算进度落后学生数量（进度 < 50%）
 * @param activeStudents - 在线学生列表
 * @returns 落后学生数量
 */
export function calculateStudentsBehindCount(activeStudents: any[]): number {
  return activeStudents.filter(s => {
    const progress = s.progressPercentage || s.progress_percentage || 0
    return progress < 50
  }).length
}

/**
 * 检查是否有预警（用于高亮预警栏）
 * @param studentsBehindCount - 落后学生数量
 * @param hasLowSubmissionRate - 是否有低提交率
 * @returns 是否有预警
 */
export function hasAlerts(studentsBehindCount: number, hasLowSubmissionRate: boolean): boolean {
  return studentsBehindCount > 0 || hasLowSubmissionRate
}

/**
 * 检查是否有低提交率（活动模块）
 * 注意：这个函数需要根据实际的提交统计数据来实现
 * @param currentCell - 当前模块
 * @param sessionStatistics - 会话统计
 * @returns 是否有低提交率
 */
export function checkLowSubmissionRate(currentCell: any, sessionStatistics: any): boolean {
  if (!currentCell || currentCell.type !== 'activity') return false
  if (!sessionStatistics) return false
  // 假设如果提交率低于 50% 且总学生数 > 5，则显示预警
  // 这里需要根据实际的提交统计数据来判断
  return false // TODO: 根据实际数据实现
}

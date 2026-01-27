/**
 * 学科教研组服务
 */

import { api } from './api'
import type {
  SubjectGroup,
  SubjectGroupCreate,
  SubjectGroupUpdate,
  SubjectGroupListResponse,
  SubjectGroupQueryParams,
  GroupMembership,
  GroupMembershipCreate,
  GroupMembershipUpdate,
  GroupMembershipListResponse,
  GroupMemberQueryParams,
  SharedLesson,
  SharedLessonCreate,
  SharedLessonUpdate,
  SharedLessonListResponse,
  SharedLessonQueryParams,
  SubjectGroupStatistics,
} from '@/types/subjectGroup'

// ==================== 教研组管理 ====================

/**
 * 创建教研组
 */
export async function createSubjectGroup(
  data: SubjectGroupCreate
): Promise<SubjectGroup> {
  return await api.post<SubjectGroup>('/subject-groups/', data)
}

/**
 * 获取教研组列表
 */
export async function getSubjectGroups(
  params?: SubjectGroupQueryParams
): Promise<SubjectGroupListResponse> {
  return await api.get<SubjectGroupListResponse>('/subject-groups/', { params })
}

/**
 * 获取教研组详情
 */
export async function getSubjectGroup(groupId: number): Promise<SubjectGroup> {
  return await api.get<SubjectGroup>(`/subject-groups/${groupId}`)
}

/**
 * 更新教研组
 */
export async function updateSubjectGroup(
  groupId: number,
  data: SubjectGroupUpdate
): Promise<SubjectGroup> {
  return await api.put<SubjectGroup>(`/subject-groups/${groupId}`, data)
}

/**
 * 删除教研组
 */
export async function deleteSubjectGroup(groupId: number): Promise<void> {
  await api.delete<void>(`/subject-groups/${groupId}`)
}

// ==================== 成员管理 ====================

/**
 * 获取教研组成员列表
 */
export async function getGroupMembers(
  groupId: number,
  params?: GroupMemberQueryParams
): Promise<GroupMembershipListResponse> {
  return await api.get<GroupMembershipListResponse>(
    `/subject-groups/${groupId}/members`,
    { params }
  )
}

/**
 * 添加教研组成员
 */
export async function addGroupMember(
  groupId: number,
  data: GroupMembershipCreate
): Promise<GroupMembership> {
  return await api.post<GroupMembership>(
    `/subject-groups/${groupId}/members`,
    data
  )
}

/**
 * 更新教研组成员
 */
export async function updateGroupMember(
  groupId: number,
  userId: number,
  data: GroupMembershipUpdate
): Promise<GroupMembership> {
  return await api.put<GroupMembership>(
    `/subject-groups/${groupId}/members/${userId}`,
    data
  )
}

/**
 * 移除教研组成员
 */
export async function removeGroupMember(
  groupId: number,
  userId: number
): Promise<void> {
  await api.delete<void>(
    `/subject-groups/${groupId}/members/${userId}`
  )
}

// ==================== 教学设计共享 ====================

/**
 * 获取教研组共享教学设计列表
 */
export async function getSharedLessons(
  groupId: number,
  params?: SharedLessonQueryParams
): Promise<SharedLessonListResponse> {
  return await api.get<SharedLessonListResponse>(
    `/subject-groups/${groupId}/lessons`,
    { params }
  )
}

/**
 * 分享教学设计到教研组
 */
export async function shareLessonToGroup(
  groupId: number,
  data: SharedLessonCreate
): Promise<SharedLesson> {
  return await api.post<SharedLesson>(
    `/subject-groups/${groupId}/lessons`,
    data
  )
}

/**
 * 更新共享教学设计
 */
export async function updateSharedLesson(
  groupId: number,
  lessonId: number,
  data: SharedLessonUpdate
): Promise<SharedLesson> {
  return await api.put<SharedLesson>(
    `/subject-groups/${groupId}/lessons/${lessonId}`,
    data
  )
}

/**
 * 取消分享教学设计
 */
export async function unshareLesson(
  groupId: number,
  lessonId: number
): Promise<void> {
  await api.delete<void>(
    `/subject-groups/${groupId}/lessons/${lessonId}`
  )
}

/**
 * 增加教学设计查看次数
 */
export async function incrementLessonView(
  groupId: number,
  lessonId: number
): Promise<{ view_count: number }> {
  return await api.post<{ view_count: number }>(
    `/subject-groups/${groupId}/lessons/${lessonId}/view`
  )
}

/**
 * 增加教学设计下载次数
 */
export async function incrementLessonDownload(
  groupId: number,
  lessonId: number
): Promise<{ download_count: number }> {
  return await api.post<{ download_count: number }>(
    `/subject-groups/${groupId}/lessons/${lessonId}/download`
  )
}

// ==================== 统计信息 ====================

/**
 * 获取教研组统计信息
 */
export async function getSubjectGroupStatistics(): Promise<SubjectGroupStatistics> {
  return await api.get<SubjectGroupStatistics>(
    '/subject-groups/statistics/overview'
  )
}


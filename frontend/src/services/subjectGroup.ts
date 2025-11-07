/**
 * 学科教研组服务
 */

import axios from 'axios'
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

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// ==================== 教研组管理 ====================

/**
 * 创建教研组
 */
export async function createSubjectGroup(
  data: SubjectGroupCreate
): Promise<SubjectGroup> {
  const response = await axios.post(`${API_BASE_URL}/api/v1/subject-groups/`, data)
  return response.data
}

/**
 * 获取教研组列表
 */
export async function getSubjectGroups(
  params?: SubjectGroupQueryParams
): Promise<SubjectGroupListResponse> {
  const response = await axios.get(`${API_BASE_URL}/api/v1/subject-groups/`, {
    params,
  })
  return response.data
}

/**
 * 获取教研组详情
 */
export async function getSubjectGroup(groupId: number): Promise<SubjectGroup> {
  const response = await axios.get(`${API_BASE_URL}/api/v1/subject-groups/${groupId}`)
  return response.data
}

/**
 * 更新教研组
 */
export async function updateSubjectGroup(
  groupId: number,
  data: SubjectGroupUpdate
): Promise<SubjectGroup> {
  const response = await axios.put(
    `${API_BASE_URL}/api/v1/subject-groups/${groupId}`,
    data
  )
  return response.data
}

/**
 * 删除教研组
 */
export async function deleteSubjectGroup(groupId: number): Promise<void> {
  await axios.delete(`${API_BASE_URL}/api/v1/subject-groups/${groupId}`)
}

// ==================== 成员管理 ====================

/**
 * 获取教研组成员列表
 */
export async function getGroupMembers(
  groupId: number,
  params?: GroupMemberQueryParams
): Promise<GroupMembershipListResponse> {
  const response = await axios.get(
    `${API_BASE_URL}/api/v1/subject-groups/${groupId}/members`,
    { params }
  )
  return response.data
}

/**
 * 添加教研组成员
 */
export async function addGroupMember(
  groupId: number,
  data: GroupMembershipCreate
): Promise<GroupMembership> {
  const response = await axios.post(
    `${API_BASE_URL}/api/v1/subject-groups/${groupId}/members`,
    data
  )
  return response.data
}

/**
 * 更新教研组成员
 */
export async function updateGroupMember(
  groupId: number,
  userId: number,
  data: GroupMembershipUpdate
): Promise<GroupMembership> {
  const response = await axios.put(
    `${API_BASE_URL}/api/v1/subject-groups/${groupId}/members/${userId}`,
    data
  )
  return response.data
}

/**
 * 移除教研组成员
 */
export async function removeGroupMember(
  groupId: number,
  userId: number
): Promise<void> {
  await axios.delete(
    `${API_BASE_URL}/api/v1/subject-groups/${groupId}/members/${userId}`
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
  const response = await axios.get(
    `${API_BASE_URL}/api/v1/subject-groups/${groupId}/lessons`,
    { params }
  )
  return response.data
}

/**
 * 分享教学设计到教研组
 */
export async function shareLessonToGroup(
  groupId: number,
  data: SharedLessonCreate
): Promise<SharedLesson> {
  const response = await axios.post(
    `${API_BASE_URL}/api/v1/subject-groups/${groupId}/lessons`,
    data
  )
  return response.data
}

/**
 * 更新共享教学设计
 */
export async function updateSharedLesson(
  groupId: number,
  lessonId: number,
  data: SharedLessonUpdate
): Promise<SharedLesson> {
  const response = await axios.put(
    `${API_BASE_URL}/api/v1/subject-groups/${groupId}/lessons/${lessonId}`,
    data
  )
  return response.data
}

/**
 * 取消分享教学设计
 */
export async function unshareLesson(
  groupId: number,
  lessonId: number
): Promise<void> {
  await axios.delete(
    `${API_BASE_URL}/api/v1/subject-groups/${groupId}/lessons/${lessonId}`
  )
}

/**
 * 增加教学设计查看次数
 */
export async function incrementLessonView(
  groupId: number,
  lessonId: number
): Promise<{ view_count: number }> {
  const response = await axios.post(
    `${API_BASE_URL}/api/v1/subject-groups/${groupId}/lessons/${lessonId}/view`
  )
  return response.data
}

/**
 * 增加教学设计下载次数
 */
export async function incrementLessonDownload(
  groupId: number,
  lessonId: number
): Promise<{ download_count: number }> {
  const response = await axios.post(
    `${API_BASE_URL}/api/v1/subject-groups/${groupId}/lessons/${lessonId}/download`
  )
  return response.data
}

// ==================== 统计信息 ====================

/**
 * 获取教研组统计信息
 */
export async function getSubjectGroupStatistics(): Promise<SubjectGroupStatistics> {
  const response = await axios.get(
    `${API_BASE_URL}/api/v1/subject-groups/statistics/overview`
  )
  return response.data
}


/**
 * 活动状态管理 Composable
 * 管理答案、提交状态、进度等
 */

import { ref, computed } from 'vue'
import type { ActivityCell } from '../types/cell'

interface UseActivityStateOptions {
  cell: ActivityCell
}

export function useActivityState(options: UseActivityStateOptions) {
  const { cell } = options
  
  // 提交状态
  const isSubmitted = ref(false)
  const submissionData = ref<any>(null)  // 存储提交后的完整数据（包含正确答案）
  
  // 答案状态
  const answers = ref<Record<string, any>>({})
  const submitting = ref(false)
  const startTime = ref(new Date())
  const submissionId = ref<number | null>(null)
  
  /**
   * 获取题目的答案数据（包含正确性判断）
   * 确保返回的答案格式符合组件期望（对象或 null）
   */
  function getItemAnswer(itemId: string): any {
    if (!submissionData.value || !submissionData.value.responses) {
      return null
    }
    
    const answer = submissionData.value.responses[itemId]
    
    // 如果答案是 null 或 undefined，直接返回 null
    if (answer === null || answer === undefined) {
      return null
    }
    
    // 如果答案已经是对象格式，直接返回
    if (typeof answer === 'object' && !Array.isArray(answer)) {
      return answer
    }
    
    // 如果答案是字符串或数组，需要转换为对象格式
    // 找到对应的题目类型，以便正确转换
    const item = cell.content.items.find(item => item.id === itemId)
    if (!item) {
      // 如果找不到题目，返回 null
      return null
    }
    
    // 根据题型转换答案格式
    if (item.type === 'single-choice' || item.type === 'true-false') {
      // 单选题或判断题：字符串 -> {answer: string}
      return {
        answer: answer
      }
    } else if (item.type === 'multiple-choice') {
      // 多选题：数组 -> {answer: string[]}
      return {
        answer: Array.isArray(answer) ? answer : [answer]
      }
    } else if (item.type === 'short-answer' || item.type === 'long-answer') {
      // 简答题或论述题：字符串 -> {text: string}
      return {
        text: String(answer)
      }
    } else if (item.type === 'scale') {
      // 量表题：数字 -> {value: number}
      return {
        value: typeof answer === 'number' ? answer : Number(answer)
      }
    }
    
    // 其他情况，返回原答案（可能是对象格式）
    return answer
  }
  
  /**
   * 计算已答题数量
   */
  const answeredCount = computed(() => {
    return Object.keys(answers.value).filter(key => {
      const answer = answers.value[key]
      return answer !== undefined && answer !== null && answer !== ''
    }).length
  })
  
  /**
   * 计算进度百分比
   */
  const progress = computed(() => {
    const total = cell.content.items.length
    return total > 0 ? Math.round((answeredCount.value / total) * 100) : 0
  })
  
  /**
   * 检查是否可以提交（所有必答题是否已完成）
   */
  const canSubmit = computed(() => {
    const requiredItems = cell.content.items.filter(item => item.required)
    return requiredItems.every(item => {
      const answer = answers.value[item.id]
      return answer !== undefined && answer !== null && answer !== ''
    })
  })
  
  /**
   * 设置答案
   */
  function setAnswer(itemId: string, value: any) {
    answers.value[itemId] = value
  }
  
  /**
   * 获取答案
   */
  function getAnswer(itemId: string): any {
    return answers.value[itemId]
  }
  
  /**
   * 设置所有答案
   */
  function setAnswers(newAnswers: Record<string, any>) {
    answers.value = { ...newAnswers }
  }
  
  /**
   * 设置提交状态
   */
  function setSubmitted(submitted: boolean, data?: any) {
    isSubmitted.value = submitted
    if (data) {
      submissionData.value = data
      // 更新 answers 为包含正确答案的完整数据
      if (data.responses) {
        answers.value = data.responses
      }
    }
  }
  
  /**
   * 设置提交ID
   */
  function setSubmissionId(id: number | null) {
    submissionId.value = id
  }
  
  /**
   * 设置提交中状态
   */
  function setSubmitting(value: boolean) {
    submitting.value = value
  }
  
  /**
   * 重置状态
   */
  function reset() {
    answers.value = {}
    isSubmitted.value = false
    submissionData.value = null
    submissionId.value = null
    submitting.value = false
    startTime.value = new Date()
  }
  
  return {
    // 状态
    answers,
    isSubmitted,
    submissionData,
    submitting,
    startTime,
    submissionId,
    
    // 计算属性
    answeredCount,
    progress,
    canSubmit,
    
    // 方法
    getItemAnswer,
    setAnswer,
    getAnswer,
    setAnswers,
    setSubmitted,
    setSubmissionId,
    setSubmitting,
    reset,
  }
}


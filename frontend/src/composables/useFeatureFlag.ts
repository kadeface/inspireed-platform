/**
 * 特性开关管理
 * 用于控制新功能的逐步发布
 */

import { ref, computed } from 'vue'

interface FeatureFlags {
  'use-x6-editor': boolean
  'use-mindmap': boolean
  'use-auto-save': boolean
  'use-surveyjs': boolean  // 是否使用 SurveyJS 渲染活动模块
  [key: string]: boolean
}

// 从环境变量或本地存储读取特性开关配置
// 默认启用 X6 编辑器（新功能已就绪）
const defaultFlags: FeatureFlags = {
  'use-x6-editor': import.meta.env.VITE_USE_X6_EDITOR !== 'false', // 默认 true，除非环境变量明确设为 false
  'use-mindmap': import.meta.env.VITE_USE_MINDMAP === 'true' || true, // 默认启用思维导图
  'use-auto-save': import.meta.env.VITE_USE_AUTO_SAVE === 'true' || true,
  'use-surveyjs': import.meta.env.VITE_USE_SURVEYJS === 'true' || false, // 默认 false，可通过环境变量启用
}

// 从 localStorage 读取用户自定义的特性开关
function loadFlags(): FeatureFlags {
  // 默认值：X6 编辑器默认启用
  let flags = { ...defaultFlags }
  let parsed: any = null
  
  try {
    const stored = localStorage.getItem('feature-flags')
    if (stored) {
      parsed = JSON.parse(stored)
      // 如果用户之前明确禁用了 X6，但现在默认启用，自动升级（清除旧设置）
      if (parsed['use-x6-editor'] === false && defaultFlags['use-x6-editor'] === true) {
        // 清除旧的禁用设置，使用新的默认值
        delete parsed['use-x6-editor']
        const updated = { ...defaultFlags, ...parsed }
        saveFlags(updated)
        return updated
      }
      // 合并用户设置
      flags = { ...flags, ...parsed }
    }
  } catch (error) {
    console.warn('Failed to load feature flags from localStorage:', error)
  }
  
  // 环境变量优先级最高（可以强制禁用）
  if (import.meta.env.VITE_USE_X6_EDITOR === 'false') {
    flags['use-x6-editor'] = false
  }
  
  return flags
}

// 保存特性开关到 localStorage
function saveFlags(flags: FeatureFlags) {
  try {
    localStorage.setItem('feature-flags', JSON.stringify(flags))
  } catch (error) {
    console.warn('Failed to save feature flags to localStorage:', error)
  }
}

const featureFlags = ref<FeatureFlags>(loadFlags())

export function useFeatureFlag() {
  /**
   * 检查特性是否启用
   */
  function isEnabled(flagName: keyof FeatureFlags): boolean {
    return featureFlags.value[flagName] === true
  }

  /**
   * 启用特性
   */
  function enable(flagName: keyof FeatureFlags) {
    featureFlags.value[flagName] = true
    saveFlags(featureFlags.value)
  }

  /**
   * 禁用特性
   */
  function disable(flagName: keyof FeatureFlags) {
    featureFlags.value[flagName] = false
    saveFlags(featureFlags.value)
  }

  /**
   * 切换特性状态
   */
  function toggle(flagName: keyof FeatureFlags) {
    featureFlags.value[flagName] = !featureFlags.value[flagName]
    saveFlags(featureFlags.value)
  }

  /**
   * 获取所有特性开关状态
   */
  const allFlags = computed(() => featureFlags.value)

  return {
    isEnabled,
    enable,
    disable,
    toggle,
    allFlags,
  }
}


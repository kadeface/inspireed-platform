/**
 * 调试活动提交面板显示问题的工具函数
 * 在浏览器控制台中调用这些函数来检查状态
 */

export function debugActivityPanel() {
  console.log('🔍 开始检查活动提交面板显示条件...\n')
  
  // 尝试从 Vue DevTools 或全局获取数据
  const vueApp = (window as any).__VUE_DEVTOOLS_GLOBAL_HOOK__
  
  console.log('📋 活动提交面板显示条件检查：')
  console.log('需要满足以下三个条件：')
  console.log('1. session 存在')
  console.log('2. session.current_activity_id 存在（活动已启动）')
  console.log('3. currentActivityCell 存在（能找到对应的活动Cell）\n')
  
  console.log('💡 请在浏览器控制台执行以下代码来检查当前状态：')
  console.log(`
// 检查方法（粘贴到浏览器控制台）：
const checkActivityPanel = () => {
  // 从 localStorage 或 sessionStorage 获取可能的会话信息
  console.log('=== 会话信息检查 ===')
  console.log('localStorage:', localStorage)
  console.log('sessionStorage:', sessionStorage)
  
  // 检查网络请求
  console.log('\\n=== 建议检查的内容 ===')
  console.log('1. 打开浏览器开发者工具的 Network 标签')
  console.log('2. 查找以下请求：')
  console.log('   - POST /api/v1/classroom-sessions/{id}/start')
  console.log('   - POST /api/v1/classroom-sessions/{id}/start-activity')
  console.log('3. 检查响应中的 current_activity_id 字段')
  console.log('\\n=== Vue DevTools 检查 ===')
  console.log('1. 安装 Vue DevTools 扩展')
  console.log('2. 找到 TeacherControlPanel 组件')
  console.log('3. 检查以下数据：')
  console.log('   - session.current_activity_id')
  console.log('   - currentActivityCell')
  console.log('   - activitySubmissions')
}

checkActivityPanel()
  `)
  
  return {
    message: '请查看上方控制台输出的调试指令',
    nextSteps: [
      '1. 确认已点击"开始上课"按钮',
      '2. 在导播台中点击活动模块',
      '3. 点击"开始活动"按钮',
      '4. 检查是否有错误提示',
      '5. 使用浏览器开发者工具查看 Network 请求'
    ]
  }
}

// 在控制台中可以调用
if (typeof window !== 'undefined') {
  (window as any).debugActivityPanel = debugActivityPanel
}


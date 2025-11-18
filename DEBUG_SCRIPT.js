// 在学生端浏览器控制台执行此脚本
// 复制粘贴到 Console 并按回车

console.log('====== 学生端状态调试 ======')

// 尝试从 localStorage 获取状态
const token = localStorage.getItem('access_token')
const user = localStorage.getItem('user')

console.log('1. 认证状态:')
console.log('  - Token:', token ? '存在' : '不存在')
console.log('  - User:', user ? JSON.parse(user) : '不存在')

// 尝试从 Vue DevTools 获取组件状态
// 注意：这需要安装 Vue DevTools 扩展

console.log('\n2. 请手动检查以下内容:')
console.log('  a) 打开 Vue DevTools')
console.log('  b) 找到 LessonView 组件')
console.log('  c) 查看以下属性:')
console.log('     - lesson.content.length (教案有多少个Cell)')
console.log('     - lesson.content[0].order (第一个Cell的order)')
console.log('     - classroomSession.value (会话对象)')
console.log('     - classroomSession.value?.settings?.display_cell_orders (显示的orders)')
console.log('     - isInClassroomMode (是否在课堂模式)')
console.log('     - shouldSyncDisplay (是否严格同步)')
console.log('     - filteredCells.length (过滤后的Cell数量)')

console.log('\n3. 或者在控制台过滤日志:')
console.log('  - 输入: 🔍')
console.log('  - 输入: 🔄')
console.log('  - 输入: ✅')
console.log('  查看相关日志')

console.log('\n====== 调试脚本结束 ======')


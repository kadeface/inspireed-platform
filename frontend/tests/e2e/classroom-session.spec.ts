/**
 * 课堂会话管理 E2E 测试
 *
 * 测试场景：
 * 1. 教师创建课堂会话
 * 2. 学生加入课堂
 * 3. 教师开始授课
 * 4. 教师结束会话
 */

import { test, expect } from '@playwright/test'

// 测试配置
const TEST_CONFIG = {
  baseURL: process.env.BASE_URL || 'http://localhost:5173',
  teacherUsername: process.env.TEACHER_USERNAME || 'teacher@test.com',
  teacherPassword: process.env.TEACHER_PASSWORD || 'password123',
  studentUsername: process.env.STUDENT_USERNAME || 'student@test.com',
  studentPassword: process.env.STUDENT_PASSWORD || 'password123',
  lessonId: process.env.TEST_LESSON_ID || '1',
}

test.describe('课堂会话管理', () => {
  test.beforeEach(async ({ page }) => {
    // 每个测试前登录
    await page.goto(TEST_CONFIG.baseURL)
    await page.waitForLoadState('networkidle')
  })

  /**
   * 测试1：教师创建课堂会话
   */
  test('教师应该能够创建课堂会话', async ({ page }) => {
    // 登录
    await loginAsTeacher(page)

    // 导航到教案编辑页面
    await page.goto(`${TEST_CONFIG.baseURL}/teacher/lesson/${TEST_CONFIG.lessonId}`)
    await page.waitForLoadState('networkidle')

    // 检查课堂控制面板是否存在
    const controlPanel = page.locator('[data-testid="teacher-control-panel"]')
    await expect(controlPanel).toBeVisible()

    // 检查会话创建按钮
    const createSessionButton = page.locator(
      '[data-testid="create-session-button"]'
    )
    await expect(createSessionButton).toBeVisible()

    // 点击创建会话按钮
    await createSessionButton.click()

    // 等待会话创建成功
    const sessionStatus = page.locator('[data-testid="session-status"]')
    await expect(sessionStatus).toBeVisible({ timeout: 10000 })
    await expect(sessionStatus).toContainText('preparing', { timeout: 5000 })

    console.log('✅ 课堂会话创建成功')
  })

  /**
   * 测试2：教师开始授课
   */
  test('教师应该能够开始授课', async ({ page }) => {
    // 登录并导航到教案页面
    await loginAsTeacher(page)
    await page.goto(`${TEST_CONFIG.baseURL}/teacher/lesson/${TEST_CONFIG.lessonId}`)
    await page.waitForLoadState('networkidle')

    // 创建会话（如果还没有）
    const createSessionButton = page.locator(
      '[data-testid="create-session-button"]'
    )
    if (await createSessionButton.isVisible()) {
      await createSessionButton.click()
      await page.waitForTimeout(2000)
    }

    // 检查开始授课按钮
    const startTeachingButton = page.locator(
      '[data-testid="start-teaching-button"]'
    )
    await expect(startTeachingButton).toBeVisible()

    // 点击开始授课
    await startTeachingButton.click()

    // 等待状态更新为 teaching
    const sessionStatus = page.locator('[data-testid="session-status"]')
    await expect(sessionStatus).toContainText('teaching', { timeout: 10000 })

    // 检查会话时长显示
    const durationDisplay = page.locator('[data-testid="session-duration"]')
    await expect(durationDisplay).toBeVisible()

    console.log('✅ 开始授课成功')
  })

  /**
   * 测试3：教师结束会话
   */
  test('教师应该能够结束会话', async ({ page }) => {
    // 登录并导航到教案页面
    await loginAsTeacher(page)
    await page.goto(`${TEST_CONFIG.baseURL}/teacher/lesson/${TEST_CONFIG.lessonId}`)
    await page.waitForLoadState('networkidle')

    // 确保会话正在授课中
    const sessionStatus = page.locator('[data-testid="session-status"]')
    const currentStatus = await sessionStatus.textContent()

    if (!currentStatus?.includes('teaching')) {
      // 开始授课
      const startButton = page.locator('[data-testid="start-teaching-button"]')
      if (await startButton.isVisible()) {
        await startButton.click()
        await page.waitForTimeout(2000)
      }
    }

    // 点击结束会话按钮
    const endSessionButton = page.locator('[data-testid="end-session-button"]')
    await expect(endSessionButton).toBeVisible()

    // 确认结束会话
    await endSessionButton.click()

    // 等待确认对话框
    const confirmDialog = page.locator('[data-testid="confirm-end-dialog"]')
    await expect(confirmDialog).toBeVisible()

    // 点击确认
    const confirmButton = page.locator(
      '[data-testid="confirm-end-button"]'
    )
    await confirmButton.click()

    // 等待会话状态更新为 ended
    await expect(sessionStatus).toContainText('ended', { timeout: 10000 })

    console.log('✅ 会话结束成功')
  })

  /**
   * 测试4：检查会话统计信息
   */
  test('应该正确显示会话统计信息', async ({ page }) => {
    await loginAsTeacher(page)
    await page.goto(`${TEST_CONFIG.baseURL}/teacher/lesson/${TEST_CONFIG.lessonId}`)
    await page.waitForLoadState('networkidle')

    // 检查学生数量显示
    const studentCount = page.locator('[data-testid="student-count"]')
    await expect(studentCount).toBeVisible()

    // 检查模块数量显示
    const moduleCount = page.locator('[data-testid="module-count"]')
    await expect(moduleCount).toBeVisible()

    // 检查活动统计面板
    const activityStats = page.locator('[data-testid="activity-statistics"]')
    await expect(activityStats).toBeVisible()

    console.log('✅ 统计信息显示正常')
  })

  /**
   * 测试5：检查模块列表显示
   */
  test('应该正确显示模块列表', async ({ page }) => {
    await loginAsTeacher(page)
    await page.goto(`${TEST_CONFIG.baseURL}/teacher/lesson/${TEST_CONFIG.lessonId}`)
    await page.waitForLoadState('networkidle')

    // 检查模块列表
    const moduleList = page.locator('[data-testid="module-list"]')
    await expect(moduleList).toBeVisible()

    // 检查模块项是否存在
    const moduleItems = page.locator('[data-testid^="module-item-"]')
    const count = await moduleItems.count()

    expect(count).toBeGreaterThan(0)

    console.log(`✅ 模块列表显示正常，共 ${count} 个模块`)
  })
})

/**
 * 辅助函数：以教师身份登录
 */
async function loginAsTeacher(page: any) {
  // 导航到登录页面
  await page.goto(`${TEST_CONFIG.baseURL}/login`)

  // 填写登录表单
  await page.fill('[data-testid="username-input"]', TEST_CONFIG.teacherUsername)
  await page.fill('[data-testid="password-input"]', TEST_CONFIG.teacherPassword)

  // 点击登录按钮
  await page.click('[data-testid="login-button"]')

  // 等待导航到教师工作台
  await page.waitForURL(`${TEST_CONFIG.baseURL}/teacher`)

  console.log('✅ 教师登录成功')
}

/**
 * 辅助函数：以学生身份登录
 */
async function loginAsStudent(page: any) {
  await page.goto(`${TEST_CONFIG.baseURL}/login`)

  await page.fill('[data-testid="username-input"]', TEST_CONFIG.studentUsername)
  await page.fill('[data-testid="password-input"]', TEST_CONFIG.studentPassword)

  await page.click('[data-testid="login-button"]')

  // 等待导航成功
  await page.waitForLoadState('networkidle')

  console.log('✅ 学生登录成功')
}

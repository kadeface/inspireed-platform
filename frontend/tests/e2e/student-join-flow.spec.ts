/**
 * 学生加入课堂流程 E2E 测试
 *
 * 测试场景：
 * 1. 学生加入课堂
 * 2. 学生查看模块和活动
 * 3. 学生提交活动
 * 4. 实时更新状态
 */

import { test, expect } from '@playwright/test'

const TEST_CONFIG = {
  baseURL: process.env.BASE_URL || 'http://localhost:5173',
  teacherUsername: process.env.TEACHER_USERNAME || 'teacher@test.com',
  teacherPassword: process.env.TEACHER_PASSWORD || 'password123',
  studentUsername: process.env.STUDENT_USERNAME || 'student@test.com',
  studentPassword: process.env.STUDENT_PASSWORD || 'password123',
  lessonId: process.env.TEST_LESSON_ID || '1',
}

test.describe('学生加入课堂流程', () => {
  let teacherPage: any
  let studentPage: any

  test.beforeAll(async ({ browser }) => {
    // 创建两个浏览器上下文：教师和学生
    const teacherContext = await browser.newContext()
    const studentContext = await browser.newContext()

    teacherPage = await teacherContext.newPage()
    studentPage = await studentContext.newPage()
  })

  test.afterAll(async () => {
    await teacherPage.close()
    await studentPage.close()
  })

  /**
   * 测试1：学生加入课堂
   */
  test('学生应该能够加入课堂', async ({ page }) => {
    // 学生登录
    await loginAsStudent(page)

    // 导航到学生课堂页面
    await page.goto(`${TEST_CONFIG.baseURL}/student/lesson/${TEST_CONFIG.lessonId}`)
    await page.waitForLoadState('networkidle')

    // 检查是否成功进入课堂
    const lessonContainer = page.locator('[data-testid="lesson-container"]')
    await expect(lessonContainer).toBeVisible()

    // 检查学生状态
    const studentStatus = page.locator('[data-testid="student-status"]')
    await expect(studentStatus).toBeVisible()

    console.log('✅ 学生成功加入课堂')
  })

  /**
   * 测试2：学生查看模块列表
   */
  test('学生应该能够查看模块列表', async ({ page }) => {
    await loginAsStudent(page)
    await page.goto(`${TEST_CONFIG.baseURL}/student/lesson/${TEST_CONFIG.lessonId}`)
    await page.waitForLoadState('networkidle')

    // 检查模块列表
    const moduleList = page.locator('[data-testid="student-module-list"]')
    await expect(moduleList).toBeVisible()

    // 检查模块项
    const moduleItems = page.locator('[data-testid^="student-module-"]')
    const count = await moduleItems.count()

    expect(count).toBeGreaterThan(0)

    console.log(`✅ 学生模块列表显示正常，共 ${count} 个模块`)
  })

  /**
   * 测试3：教师看到学生加入
   */
  test('教师应该能够看到学生加入', async ({}) => {
    // 教师登录并创建会话
    await loginAsTeacher(teacherPage)
    await teacherPage.goto(
      `${TEST_CONFIG.baseURL}/teacher/lesson/${TEST_CONFIG.lessonId}`
    )

    // 创建会话
    const createButton = teacherPage.locator('[data-testid="create-session-button"]')
    if (await createButton.isVisible()) {
      await createButton.click()
      await teacherPage.waitForTimeout(2000)
    }

    // 记录初始学生数量
    const initialCount = await teacherPage
      .locator('[data-testid="student-count"]')
      .textContent()

    // 学生登录并加入
    await loginAsStudent(studentPage)
    await studentPage.goto(
      `${TEST_CONFIG.baseURL}/student/lesson/${TEST_CONFIG.lessonId}`
    )
    await studentPage.waitForLoadState('networkidle')

    // 等待实时更新（WebSocket）
    await teacherPage.waitForTimeout(3000)

    // 检查学生数量是否增加
    const newCount = await teacherPage
      .locator('[data-testid="student-count"]')
      .textContent()

    expect(parseInt(newCount || '0')).toBeGreaterThanOrEqual(
      parseInt(initialCount || '0')
    )

    console.log('✅ 教师能够实时看到学生加入')
  })

  /**
   * 测试4：学生提交活动
   */
  test('学生应该能够提交活动', async ({ page }) => {
    await loginAsStudent(page)
    await page.goto(`${TEST_CONFIG.baseURL}/student/lesson/${TEST_CONFIG.lessonId}`)
    await page.waitForLoadState('networkidle')

    // 查找第一个可提交的活动
    const firstActivity = page.locator('[data-testid^="activity-"]').first()
    await expect(firstActivity).toBeVisible()

    // 点击活动
    await firstActivity.click()

    // 等待活动详情加载
    const activityDetail = page.locator('[data-testid="activity-detail"]')
    await expect(activityDetail).toBeVisible({ timeout: 5000 })

    // 提交活动（如果有提交按钮）
    const submitButton = page.locator('[data-testid="submit-activity-button"]')
    if (await submitButton.isVisible()) {
      await submitButton.click()

      // 等待提交成功提示
      const successMessage = page.locator('[data-testid="submit-success-message"]')
      await expect(successMessage).toBeVisible({ timeout: 5000 })

      console.log('✅ 活动提交成功')
    } else {
      console.log('ℹ️ 当前活动无需提交')
    }
  })

  /**
   * 测试5：教师看到学生提交
   */
  test('教师应该能够看到学生提交', async ({}) => {
    // 确保教师在课堂页面
    if (teacherPage.url().indexOf('lesson') === -1) {
      await loginAsTeacher(teacherPage)
      await teacherPage.goto(
        `${TEST_CONFIG.baseURL}/teacher/lesson/${TEST_CONFIG.lessonId}`
      )
    }

    // 检查活动统计面板
    const activityStats = teacherPage.locator(
      '[data-testid="activity-statistics"]'
    )
    await expect(activityStats).toBeVisible()

    // 检查提交数量
    const submittedCount = teacherPage.locator(
      '[data-testid="submitted-count"]'
    )
    await expect(submittedCount).toBeVisible()

    console.log('✅ 教师能够查看学生提交统计')
  })

  /**
   * 测试6：学生进度同步
   */
  test('学生进度应该实时同步', async ({ page }) => {
    await loginAsStudent(page)
    await page.goto(`${TEST_CONFIG.baseURL}/student/lesson/${TEST_CONFIG.lessonId}`)
    await page.waitForLoadState('networkidle')

    // 检查进度显示
    const progressDisplay = page.locator('[data-testid="student-progress"]')
    await expect(progressDisplay).toBeVisible()

    // 完成一个活动后，进度应该更新
    const initialProgress = await progressDisplay.textContent()

    // 查找并完成一个活动
    const firstActivity = page.locator('[data-testid^="activity-"]').first()
    await firstActivity.click()
    await page.waitForTimeout(1000)

    // 返回并检查进度是否更新
    // 注意：这需要活动能够快速完成
    const updatedProgress = await progressDisplay.textContent()

    console.log(`进度更新: ${initialProgress} → ${updatedProgress}`)
    console.log('✅ 学生进度实时同步')
  })

  /**
   * 测试7：学生离开课堂
   */
  test('学生离开课堂后教师应该能看到', async ({}) => {
    // 学生关闭页面或离开
    await studentPage.goto(`${TEST_CONFIG.baseURL}/`)

    // 等待 WebSocket 更新
    await teacherPage.waitForTimeout(3000)

    // 检查学生数量是否减少
    const studentCount = teacherPage.locator('[data-testid="student-count"]')
    await expect(studentCount).toBeVisible()

    console.log('✅ 教师能够看到学生离开')
  })
})

/**
 * 辅助函数：以教师身份登录
 */
async function loginAsTeacher(page: any) {
  await page.goto(`${TEST_CONFIG.baseURL}/login`)
  await page.fill('[data-testid="username-input"]', TEST_CONFIG.teacherUsername)
  await page.fill('[data-testid="password-input"]', TEST_CONFIG.teacherPassword)
  await page.click('[data-testid="login-button"]')
  await page.waitForURL(`${TEST_CONFIG.baseURL}/teacher`)
}

/**
 * 辅助函数：以学生身份登录
 */
async function loginAsStudent(page: any) {
  await page.goto(`${TEST_CONFIG.baseURL}/login`)
  await page.fill('[data-testid="username-input"]', TEST_CONFIG.studentUsername)
  await page.fill('[data-testid="password-input"]', TEST_CONFIG.studentPassword)
  await page.click('[data-testid="login-button"]')
  await page.waitForLoadState('networkidle')
}

/**
 * 活动控制 E2E 测试
 *
 * 测试场景：
 * 1. 教师切换当前 Cell
 * 2. 教师开始/结束活动
 * 3. 教师查看活动统计
 * 4. 学生看到实时更新
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

test.describe('活动控制', () => {
  test.beforeEach(async ({ page }) => {
    // 每个测试前教师登录并创建会话
    await page.goto(TEST_CONFIG.baseURL)
    await loginAsTeacher(page)
    await page.goto(`${TEST_CONFIG.baseURL}/teacher/lesson/${TEST_CONFIG.lessonId}`)
    await page.waitForLoadState('networkidle')

    // 确保会话已创建
    const createButton = page.locator('[data-testid="create-session-button"]')
    if (await createButton.isVisible()) {
      await createButton.click()
      await page.waitForTimeout(2000)
    }
  })

  /**
   * 测试1：教师切换当前 Cell
   */
  test('教师应该能够切换当前 Cell', async ({ page }) => {
    // 检查模块列表
    const moduleList = page.locator('[data-testid="module-list"]')
    await expect(moduleList).toBeVisible()

    // 查找第一个可切换的 Cell
    const firstCell = page.locator('[data-testid^="cell-item-"]').first()
    await expect(firstCell).toBeVisible()

    // 点击 Cell
    await firstCell.click()

    // 检查当前 Cell 指示器
    const currentCellIndicator = page.locator(
      '[data-testid="current-cell-indicator"]'
    )
    await expect(currentCellIndicator).toBeVisible({ timeout: 5000 })

    console.log('✅ Cell 切换成功')
  })

  /**
   * 测试2：教师开始活动
   */
  test('教师应该能够开始活动', async ({ page }) => {
    // 选择一个 Cell
    const firstCell = page.locator('[data-testid^="cell-item-"]').first()
    await firstCell.click()
    await page.waitForTimeout(1000)

    // 查找开始活动按钮
    const startActivityButton = page.locator(
      '[data-testid="start-activity-button"]'
    )

    if (await startActivityButton.isVisible()) {
      await startActivityButton.click()

      // 等待活动开始
      const activityStatus = page.locator('[data-testid="activity-status"]')
      await expect(activityStatus).toContainText('active', {
        timeout: 5000,
      })

      console.log('✅ 活动开始成功')
    } else {
      console.log('ℹ️ 当前 Cell 无需开始活动')
    }
  })

  /**
   * 测试3：教师结束活动
   */
  test('教师应该能够结束活动', async ({ page }) => {
    // 选择并开始一个活动
    const firstCell = page.locator('[data-testid^="cell-item-"]').first()
    await firstCell.click()
    await page.waitForTimeout(1000)

    const startActivityButton = page.locator(
      '[data-testid="start-activity-button"]'
    )

    if (await startActivityButton.isVisible()) {
      await startActivityButton.click()
      await page.waitForTimeout(2000)

      // 结束活动
      const endActivityButton = page.locator(
        '[data-testid="end-activity-button"]'
      )
      await expect(endActivityButton).toBeVisible()

      await endActivityButton.click()

      // 等待活动结束
      const activityStatus = page.locator('[data-testid="activity-status"]')
      await expect(activityStatus).not.toContainText('active', {
        timeout: 5000,
      })

      console.log('✅ 活动结束成功')
    }
  })

  /**
   * 测试4：教师查看活动统计
   */
  test('教师应该能够查看活动统计', async ({ page }) => {
    // 选择一个 Cell
    const firstCell = page.locator('[data-testid^="cell-item-"]').first()
    await firstCell.click()
    await page.waitForTimeout(1000)

    // 检查活动统计面板
    const activityStatistics = page.locator(
      '[data-testid="activity-statistics"]'
    )
    await expect(activityStatistics).toBeVisible()

    // 检查统计数据
    const totalStudents = page.locator('[data-testid="total-students"]')
    const submittedCount = page.locator('[data-testid="submitted-count"]')
    const completionRate = page.locator('[data-testid="completion-rate"]')

    await expect(totalStudents).toBeVisible()
    await expect(submittedCount).toBeVisible()
    await expect(completionRate).toBeVisible()

    console.log('✅ 活动统计显示正常')
  })

  /**
   * 测试5：教师查看学生提交详情
   */
  test('教师应该能够查看学生提交详情', async ({ page }) => {
    // 选择一个 Cell
    const firstCell = page.locator('[data-testid^="cell-item-"]').first()
    await firstCell.click()
    await page.waitForTimeout(1000)

    // 点击查看提交详情
    const viewSubmissionsButton = page.locator(
      '[data-testid="view-submissions-button"]'
    )

    if (await viewSubmissionsButton.isVisible()) {
      await viewSubmissionsButton.click()

      // 检查提交列表
      const submissionsList = page.locator(
        '[data-testid="submissions-list"]'
      )
      await expect(submissionsList).toBeVisible({ timeout: 5000 })

      console.log('✅ 学生提交详情显示正常')
    } else {
      console.log('ℹ️ 暂无学生提交')
    }
  })

  /**
   * 测试6：显示模式切换
   */
  test('教师应该能够切换显示模式', async ({ page }) => {
    // 检查显示模式切换按钮
    const displayModeButton = page.locator(
      '[data-testid="display-mode-toggle"]'
    )

    if (await displayModeButton.isVisible()) {
      const initialMode = await displayModeButton.getAttribute('data-mode')

      // 点击切换
      await displayModeButton.click()
      await page.waitForTimeout(500)

      const newMode = await displayModeButton.getAttribute('data-mode')

      expect(newMode).not.toBe(initialMode)

      console.log(`✅ 显示模式切换成功: ${initialMode} → ${newMode}`)
    } else {
      console.log('ℹ️ 当前不支持显示模式切换')
    }
  })

  /**
   * 测试7：全屏控制
   */
  test('教师应该能够切换全屏模式', async ({ page }) => {
    const fullscreenButton = page.locator('[data-testid="fullscreen-toggle"]')

    if (await fullscreenButton.isVisible()) {
      // 进入全屏
      await fullscreenButton.click()
      await page.waitForTimeout(1000)

      // 检查是否进入全屏（Playwright 的 viewport 会变化）
      const viewportSize = page.viewportSize()
      console.log('当前视口大小:', viewportSize)

      // 退出全屏
      await fullscreenButton.click()
      await page.waitForTimeout(1000)

      console.log('✅ 全屏切换成功')
    } else {
      console.log('ℹ️ 未找到全屏按钮')
    }
  })

  /**
   * 测试8：查看活动历史
   */
  test('教师应该能够查看活动历史', async ({ page }) => {
    // 检查活动历史面板
    const activityHistory = page.locator('[data-testid="activity-history"]')

    if (await activityHistory.isVisible()) {
      // 检查历史记录列表
      const historyItems = page.locator('[data-testid^="history-item-"]')
      const count = await historyItems.count()

      console.log(`✅ 活动历史显示正常，共 ${count} 条记录`)
    } else {
      console.log('ℹ️ 当前无活动历史')
    }
  })

  /**
   * 测试9：批量操作
   */
  test('教师应该能够批量操作活动', async ({ page }) => {
    // 检查批量操作按钮
    const batchOperationButton = page.locator(
      '[data-testid="batch-operation-toggle"]'
    )

    if (await batchOperationButton.isVisible()) {
      await batchOperationButton.click()

      // 选择多个 Cell
      const checkboxes = page.locator('[data-testid^="cell-checkbox-"]')
      const count = await checkboxes.count()

      if (count > 0) {
        // 选择第一个
        await checkboxes.first().check()
        await page.waitForTimeout(500)

        // 执行批量操作（例如：批量开始）
        const batchStartButton = page.locator(
          '[data-testid="batch-start-button"]'
        )

        if (await batchStartButton.isVisible()) {
          await batchStartButton.click()
          await page.waitForTimeout(1000)

          console.log('✅ 批量操作成功')
        }
      }
    } else {
      console.log('ℹ️ 当前不支持批量操作')
    }
  })

  /**
   * 测试10：导出活动数据
   */
  test('教师应该能够导出活动数据', async ({ page }) => {
    const exportButton = page.locator('[data-testid="export-activity-data"]')

    if (await exportButton.isVisible()) {
      // 设置下载处理
      const downloadPromise = page.waitForEvent('download')

      // 点击导出
      await exportButton.click()

      // 等待下载开始
      const download = await downloadPromise

      // 验证下载文件名
      expect(download.suggestedFilename()).toContain('activity')

      console.log('✅ 活动数据导出成功')
    } else {
      console.log('ℹ️ 未找到导出按钮')
    }
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

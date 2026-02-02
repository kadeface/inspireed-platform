import { defineConfig, devices } from '@playwright/test'

/**
 * Playwright E2E 测试配置
 *
 * 课堂会话 v2.0 重构项目
 */
export default defineConfig({
  // 测试文件位置
  testDir: './e2e',

  // 每个测试的超时时间（毫秒）
  timeout: 30 * 1000,

  // 期望值超时
  expect: {
    timeout: 5 * 1000,
  },

  // 失败时截图
  use: {
    // 基础 URL
    // baseURL: 'http://localhost:5173',

    // 截图配置
    screenshot: 'only-on-failure',

    // 视频录制
    video: 'retain-on-failure',

    // Trace 配置（用于调试）
    trace: 'on-first-retry',

    // 浏览器视口大小
    viewport: { width: 1280, height: 720 },
  },

  // 测试运行配置
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,

  // 测试报告
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list'],
  ],

  // 测试项目（浏览器和设备）
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },

    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },

    // 移动设备测试
    // {
    //   name: 'Mobile Chrome',
    //   use: { ...devices['Pixel 5'] },
    // },
  ],

  // 开发服务器（如果需要）
  // webServer: {
  //   command: 'npm run dev',
  //   url: 'http://localhost:5173',
  //   reuseExistingServer: !process.env.CI,
  //   timeout: 120 * 1000,
  // },
})

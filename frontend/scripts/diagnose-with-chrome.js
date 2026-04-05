/**
 * 使用系统 Chrome 的诊断脚本
 */

import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 配置
const CONFIG = {
  baseURL: 'http://111.230.61.28',
  loginURL: 'http://111.230.61.28/login',
  username: 'lzd',
  password: '123',
  screenshotDir: path.join(__dirname, '../../screenshots'),
};

// 确保截图目录存在
if (!fs.existsSync(CONFIG.screenshotDir)) {
  fs.mkdirSync(CONFIG.screenshotDir, { recursive: true });
}

async function diagnose() {
  console.log('🚀 开始诊断"开始上课"按钮问题\n');

  // 使用系统安装的 Chrome
  const browser = await puppeteer.launch({
    headless: false, // 显示浏览器
    devtools: true,  // 打开开发者工具
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    defaultViewport: { width: 1280, height: 720 },
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
    ],
  });

  const page = await browser.newPage();

  // 收集控制台日志
  const consoleLogs = [];
  const consoleErrors = [];

  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();

    if (type === 'error') {
      consoleErrors.push(text);
      console.log(`🔴 控制台错误: ${text}`);
    } else if (type === 'warning') {
      console.log(`⚠️  控制台警告: ${text}`);
    } else {
      consoleLogs.push(text);
    }
  });

  // 收集页面错误
  const pageErrors = [];
  page.on('pageerror', error => {
    pageErrors.push(error.message);
    console.log(`🔴 页面错误: ${error.message}`);
  });

  // 收集 API 请求
  const apiRequests = [];
  page.on('request', request => {
    const url = request.url();
    if (url.includes('/api/')) {
      console.log(`📤 API请求: ${request.method()} ${url}`);
      apiRequests.push({
        method: request.method(),
        url: url,
        timestamp: new Date().toISOString(),
      });
    }
  });

  page.on('response', response => {
    const url = response.url();
    if (url.includes('/api/')) {
      const status = response.status();
      console.log(`📥 API响应: ${status} ${url}`);

      // 更新请求状态
      const req = apiRequests.find(r => r.url === url);
      if (req) {
        req.status = status;
      }

      if (status >= 400) {
        response.text().then(body => {
          console.log(`❌ 错误响应: ${body}`);
        }).catch(e => {
          console.log(`❌ 无法读取响应体`);
        });
      }
    }
  });

  try {
    // 步骤 1: 访问登录页面
    console.log('\n🌐 步骤1: 访问登录页面');
    await page.goto(CONFIG.loginURL, { waitUntil: 'networkidle2', timeout: 30000 });
    console.log('✅ 登录页面加载完成');

    await page.screenshot({ path: path.join(CONFIG.screenshotDir, '01-login-page.png') });
    await new Promise(resolve => setTimeout(resolve, 1000));

    // 步骤 2: 查找并填写表单
    console.log('\n📝 步骤2: 填写登录表单');

    // 查找输入框
    const usernameInput = await page.evaluateHandle(() => {
      const selectors = [
        'input[name="username"]',
        'input[type="text"]',
        'input[placeholder*="用户名"]',
        'input[placeholder*="账号"]',
        '#username',
      ];
      for (const selector of selectors) {
        const input = document.querySelector(selector);
        if (input && input.offsetParent !== null) {
          return input;
        }
      }
      return null;
    });

    const passwordInput = await page.evaluateHandle(() => {
      const selectors = [
        'input[name="password"]',
        'input[type="password"]',
        'input[placeholder*="密码"]',
        '#password',
      ];
      for (const selector of selectors) {
        const input = document.querySelector(selector);
        if (input && input.offsetParent !== null) {
          return input;
        }
      }
      return null;
    });

    if (!usernameInput || !passwordInput) {
      console.error('❌ 无法找到登录表单');
      await page.screenshot({ path: path.join(CONFIG.screenshotDir, 'error-no-form.png') });
      console.log('\n等待10秒，请查看浏览器...');
      await new Promise(resolve => setTimeout(resolve, 10000));
      await browser.close();
      return;
    }

    console.log('✅ 找到登录表单');

    // 填写表单
    const usernameElement = usernameInput.asElement();
    const passwordElement = passwordInput.asElement();

    await usernameElement.click();
    await usernameElement.type(CONFIG.username);

    await passwordElement.click();
    await passwordElement.type(CONFIG.password);

    await page.screenshot({ path: path.join(CONFIG.screenshotDir, '02-form-filled.png') });
    console.log('✅ 表单填写完成');

    // 步骤 3: 点击登录
    console.log('\n🖱️  步骤3: 点击登录按钮');

    const loginButton = await page.evaluateHandle(() => {
      const selectors = [
        'button[type="submit"]',
        'button:has-text("登录")',
        'input[type="submit"]',
      ];
      for (const selector of selectors) {
        const button = document.querySelector(selector);
        if (button && button.offsetParent !== null) {
          return button;
        }
      }
      return null;
    });

    if (!loginButton) {
      console.error('❌ 无法找到登录按钮');
      await browser.close();
      return;
    }

    const loginButtonElement = loginButton.asElement();
    await loginButtonElement.click();

    // 等待导航
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 }).catch(() => {
      console.log('⚠️  导航超时，可能已登录');
    });

    console.log('✅ 登录操作完成');
    await page.screenshot({ path: path.join(CONFIG.screenshotDir, '03-after-login.png') });
    await new Promise(resolve => setTimeout(resolve, 3000));

    // 步骤 4: 查找"开始上课"按钮
    console.log('\n🔍 步骤4: 查找"开始上课"按钮');

    // 列出所有按钮
    const allButtons = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button, a'));
      return buttons
        .filter(btn => btn.offsetParent !== null)
        .map(btn => ({
          tag: btn.tagName,
          text: btn.textContent?.trim().substring(0, 50),
          class: btn.className,
          id: btn.id,
        }))
        .slice(0, 30);
    });

    console.log('📋 页面上的按钮和链接:');
    allButtons.forEach(btn => {
      console.log(`   [${btn.tag}] ${btn.text}`);
    });

    // 查找"开始上课"按钮
    const startButtons = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button, a'));
      return buttons
        .filter(btn => {
          const text = btn.textContent || '';
          return (
            text.includes('开始上课') ||
            text.includes('开始授课') ||
            text.includes('授课模式') ||
            text.includes('进入课堂')
          );
        })
        .map(btn => ({
          tag: btn.tagName,
          text: btn.textContent?.trim(),
          class: btn.className,
          id: btn.id,
        }));
    });

    if (startButtons.length === 0) {
      console.error('\n❌ 未找到"开始上课"相关按钮');

      // 查找教案相关链接
      const lessonLinks = await page.evaluate(() => {
        const links = Array.from(document.querySelectorAll('a'));
        return links
          .filter(link => {
            const text = link.textContent || '';
            return text.includes('教案') || text.includes('课程') || text.includes('教学');
          })
          .map(link => ({
            text: link.textContent?.trim(),
            href: link.getAttribute('href'),
          }));
      });

      console.log('📋 教案相关链接:');
      lessonLinks.forEach(link => {
        console.log(`   ${link.text} -> ${link.href}`);
      });

      console.log('\n等待20秒，请手动查看浏览器并操作...');
      await new Promise(resolve => setTimeout(resolve, 20000));

      await browser.close();
      return;
    }

    console.log(`\n✅ 找到 ${startButtons.length} 个"开始上课"相关按钮:`);
    startButtons.forEach(btn => {
      console.log(`   [${btn.tag}] ${btn.text}`);
    });

    await page.screenshot({ path: path.join(CONFIG.screenshotDir, '04-found-start-button.png') });

    // 步骤 5: 点击"开始上课"按钮
    console.log('\n🖱️  步骤5: 点击"开始上课"按钮');

    // 点击前清空之前的 API 请求
    apiRequests.length = 0;

    const startButton = await page.evaluateHandle(() => {
      const buttons = Array.from(document.querySelectorAll('button, a'));
      return buttons.find(btn => {
        const text = btn.textContent || '';
        return text.includes('开始上课') || text.includes('开始授课');
      });
    });

    if (startButton) {
      await startButton.asElement().click();
      console.log('✅ 按钮已点击');

      // 等待弹窗或响应
      await new Promise(resolve => setTimeout(resolve, 3000));
      await page.screenshot({ path: path.join(CONFIG.screenshotDir, '05-after-click.png') });
    }

    // 步骤 6: 检查弹窗
    console.log('\n🔍 步骤6: 检查班级选择弹窗');

    const modalInfo = await page.evaluate(() => {
      const modalSelectors = [
        '.modal',
        '.dialog',
        '.popup',
        '[role="dialog"]',
        '.ant-modal',
        '.el-dialog',
        '.v-dialog',
        '.drawer',
      ];

      for (const selector of modalSelectors) {
        const modals = Array.from(document.querySelectorAll(selector));
        for (const modal of modals) {
          const style = window.getComputedStyle(modal);
          if (style.display !== 'none' && style.visibility !== 'hidden') {
            return {
              found: true,
              selector: selector,
              content: modal.textContent?.substring(0, 300),
              classList: Array.from(modal.classList),
            };
          }
        }
      }

      return { found: false };
    });

    if (modalInfo.found) {
      console.log(`✅ 发现弹窗: ${modalInfo.selector}`);
      console.log(`类名: ${modalInfo.classList.join(', ')}`);
      console.log(`内容: ${modalInfo.content}`);

      // 查找班级选项
      const classOptions = await page.evaluate(() => {
        const optionSelectors = [
          'li',
          '.item',
          '.option',
          '[role="option"]',
          '.class-item',
          '.class-option',
        ];

        for (const selector of optionSelectors) {
          const options = Array.from(document.querySelectorAll(selector));
          const visibleOptions = options.filter(opt => opt.offsetParent !== null);
          if (visibleOptions.length > 0) {
            return visibleOptions.map(opt => opt.textContent?.trim()).slice(0, 20);
          }
        }

        return [];
      });

      console.log(`📋 班级选项 (${classOptions.length} 个):`);
      classOptions.forEach(opt => {
        console.log(`   - ${opt}`);
      });

      await page.screenshot({ path: path.join(CONFIG.screenshotDir, '06-class-modal.png') });
    } else {
      console.error('❌ 未发现班级选择弹窗');
      console.log('\n📋 诊断信息:');
      console.log(`   控制台错误数: ${consoleErrors.length}`);
      console.log(`   页面错误数: ${pageErrors.length}`);
      console.log(`   API请求数: ${apiRequests.length}`);

      if (consoleErrors.length > 0) {
        console.log('\n🔴 控制台错误详情:');
        consoleErrors.forEach(err => console.log(`   - ${err}`));
      }

      if (pageErrors.length > 0) {
        console.log('\n🔴 页面错误详情:');
        pageErrors.forEach(err => console.log(`   - ${err}`));
      }

      if (apiRequests.length > 0) {
        console.log('\n📤 点击后的API请求:');
        apiRequests.forEach(req => {
          const status = req.status ? ` (${req.status})` : '';
          console.log(`   - ${req.method} ${req.url}${status}`);
        });
      }

      console.log('\n💡 可能的原因:');
      console.log('   1. 用户没有关联的班级数据');
      console.log('   2. 前端代码逻辑错误');
      console.log('   3. API 请求失败');
      console.log('   4. 权限问题');
    }

    // 步骤 7: 收集最终信息
    console.log('\n📊 步骤7: 收集诊断信息');

    const pageInfo = await page.evaluate(() => ({
      url: window.location.href,
      title: document.title,
      localStorage: { ...localStorage },
      sessionStorage: { ...sessionStorage },
    }));

    console.log('📋 页面信息:');
    console.log(`   URL: ${pageInfo.url}`);
    console.log(`   标题: ${pageInfo.title}`);

    console.log('\n📦 LocalStorage:');
    Object.keys(pageInfo.localStorage).forEach(key => {
      const value = pageInfo.localStorage[key];
      const displayValue = value.length > 100 ? value.substring(0, 100) + '...' : value;
      console.log(`   ${key}: ${displayValue}`);
    });

    // 保存诊断报告
    const report = {
      timestamp: new Date().toISOString(),
      config: CONFIG,
      pageInfo: {
        url: pageInfo.url,
        title: pageInfo.title,
      },
      buttonsFound: startButtons,
      modalFound: modalInfo,
      consoleErrors: consoleErrors,
      pageErrors: pageErrors,
      apiRequests: apiRequests,
      localStorageKeys: Object.keys(pageInfo.localStorage),
    };

    fs.writeFileSync(
      path.join(CONFIG.screenshotDir, 'diagnosis-report.json'),
      JSON.stringify(report, null, 2)
    );

    console.log('\n📄 诊断报告已保存到: screenshots/diagnosis-report.json');

    await page.screenshot({ path: path.join(CONFIG.screenshotDir, '07-final-state.png'), fullPage: true });

    console.log('\n⏳ 等待30秒，请查看浏览器中的状态...');
    console.log('📸 所有截图已保存到:', CONFIG.screenshotDir);
    await new Promise(resolve => setTimeout(resolve, 30000));

  } catch (error) {
    console.error('\n❌ 发生错误:', error.message);
    console.error(error.stack);
    await page.screenshot({ path: path.join(CONFIG.screenshotDir, 'error.png') });
  } finally {
    await browser.close();
    console.log('\n✅ 诊断完成');
  }
}

// 运行诊断
diagnose().catch(console.error);

/**
 * 简单的"开始上课"问题诊断脚本
 * 使用 Puppeteer (更轻量) 来诊断问题
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

  const browser = await puppeteer.launch({
    headless: false, // 显示浏览器窗口
    devtools: true,  // 打开开发者工具
    defaultViewport: { width: 1280, height: 720 },
  });

  const page = await browser.newPage();

  // 监听控制台消息
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();

    if (type === 'error') {
      console.log(`🔴 控制台错误: ${text}`);
    } else if (type === 'warning') {
      console.log(`⚠️  控制台警告: ${text}`);
    } else {
      console.log(`📝 控制台 [${type}]: ${text}`);
    }
  });

  // 监听页面错误
  page.on('pageerror', error => {
    console.log(`🔴 页面错误: ${error.message}`);
  });

  // 监听请求
  page.on('request', request => {
    const url = request.url();
    if (url.includes('/api/')) {
      console.log(`📤 API请求: ${request.method()} ${url}`);
    }
  });

  // 监听响应
  page.on('response', response => {
    const url = response.url();
    if (url.includes('/api/')) {
      const status = response.status();
      console.log(`📥 API响应: ${status} ${url}`);

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
    await page.goto(CONFIG.loginURL, { waitUntil: 'networkidle2' });
    console.log('✅ 登录页面加载完成');
    await page.screenshot({ path: path.join(CONFIG.screenshotDir, '01-login-page.png') });

    // 步骤 2: 填写登录表单
    console.log('\n📝 步骤2: 填写登录表单');

    // 尝试多种选择器
    const usernameSelectors = [
      'input[name="username"]',
      'input[type="text"]',
      'input[placeholder*="用户名"]',
      'input[placeholder*="账号"]',
      '#username',
    ];

    const passwordSelectors = [
      'input[name="password"]',
      'input[type="password"]',
      'input[placeholder*="密码"]',
      '#password',
    ];

    let usernameInput = null;
    let passwordInput = null;

    // 查找用户名输入框
    for (const selector of usernameSelectors) {
      try {
        await page.waitForSelector(selector, { timeout: 1000 });
        usernameInput = await page.$(selector);
        if (usernameInput) {
          console.log(`✅ 找到用户名输入框: ${selector}`);
          break;
        }
      } catch (e) {
        // 继续尝试
      }
    }

    // 查找密码输入框
    for (const selector of passwordSelectors) {
      try {
        await page.waitForSelector(selector, { timeout: 1000 });
        passwordInput = await page.$(selector);
        if (passwordInput) {
          console.log(`✅ 找到密码输入框: ${selector}`);
          break;
        }
      } catch (e) {
        // 继续尝试
      }
    }

    if (!usernameInput || !passwordInput) {
      console.error('❌ 无法找到登录表单输入框');
      await page.screenshot({ path: path.join(CONFIG.screenshotDir, 'error-no-form.png') });

      // 尝试获取页面信息
      const pageTitle = await page.title();
      const pageURL = page.url();
      console.log(`页面标题: ${pageTitle}`);
      console.log(`页面URL: ${pageURL}`);

      console.log('\n等待10秒，请手动查看浏览器...');
      await new Promise(resolve => setTimeout(resolve, 10000));

      await browser.close();
      return;
    }

    // 填写表单
    await usernameInput.click();
    await usernameInput.type(CONFIG.username, { delay: 100 });

    await passwordInput.click();
    await passwordInput.type(CONFIG.password, { delay: 100 });

    await page.screenshot({ path: path.join(CONFIG.screenshotDir, '02-form-filled.png') });
    console.log('✅ 表单填写完成');

    // 步骤 3: 点击登录
    console.log('\n🖱️  步骤3: 点击登录按钮');

    const loginButtonSelectors = [
      'button[type="submit"]',
      'button:has-text("登录")',
      'input[type="submit"]',
    ];

    let loginButton = null;
    for (const selector of loginButtonSelectors) {
      try {
        loginButton = await page.$(selector);
        if (loginButton) {
          console.log(`✅ 找到登录按钮: ${selector}`);
          break;
        }
      } catch (e) {
        // 继续尝试
      }
    }

    if (!loginButton) {
      console.error('❌ 无法找到登录按钮');
      await browser.close();
      return;
    }

    await loginButton.click();
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 10000 });
    console.log('✅ 登录成功');

    await page.screenshot({ path: path.join(CONFIG.screenshotDir, '03-after-login.png') });

    // 等待页面完全加载
    await new Promise(resolve => setTimeout(resolve, 3000));

    // 步骤 4: 查找"开始上课"按钮
    console.log('\n🔍 步骤4: 查找"开始上课"按钮');

    // 获取页面上所有按钮
    const allButtons = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button, a[href]'));
      return buttons
        .filter(btn => btn.offsetParent !== null) // 只显示可见的
        .map(btn => ({
          tag: btn.tagName,
          text: btn.textContent?.trim().substring(0, 50),
          class: btn.className,
          id: btn.id,
        }))
        .slice(0, 30); // 只显示前30个
    });

    console.log('📋 页面上的按钮和链接:');
    allButtons.forEach(btn => {
      console.log(`   [${btn.tag}] ${btn.text}`);
    });

    // 查找"开始上课"相关按钮
    const startTeachingButtons = await page.evaluate(() => {
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

    if (startTeachingButtons.length === 0) {
      console.error('\n❌ 未找到"开始上课"相关按钮');
      console.log('📸 截图已保存');

      // 尝试查找教案相关的链接
      console.log('\n🔍 尝试查找教案相关链接...');
      const lessonLinks = await page.evaluate(() => {
        const links = Array.from(document.querySelectorAll('a'));
        return links
          .filter(link => {
            const text = link.textContent || '';
            return (
              text.includes('教案') ||
              text.includes('课程') ||
              text.includes('教学')
            );
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

      console.log('\n等待15秒，请手动查看浏览器并操作...');
      await new Promise(resolve => setTimeout(resolve, 15000));

      await browser.close();
      return;
    }

    console.log(`\n✅ 找到 ${startTeachingButtons.length} 个"开始上课"相关按钮:`);
    startTeachingButtons.forEach(btn => {
      console.log(`   [${btn.tag}] ${btn.text}`);
    });

    // 步骤 5: 点击第一个"开始上课"按钮
    console.log('\n🖱️  步骤5: 点击"开始上课"按钮');

    // 使用 XPath 查找按钮
    const startButton = await page.evaluateHandle(() => {
      const buttons = Array.from(document.querySelectorAll('button, a'));
      return buttons.find(btn => {
        const text = btn.textContent || '';
        return text.includes('开始上课') || text.includes('开始授课');
      });
    });

    if (!startButton) {
      console.error('❌ 无法获取按钮引用');
      await browser.close();
      return;
    }

    await startButton.asElement().click();
    console.log('✅ 按钮已点击');

    await page.screenshot({ path: path.join(CONFIG.screenshotDir, '04-after-click.png') });

    // 步骤 6: 检查是否有弹窗
    console.log('\n🔍 步骤6: 检查班级选择弹窗');

    await new Promise(resolve => setTimeout(resolve, 2000));

    // 检查弹窗
    const hasModal = await page.evaluate(() => {
      // 检查常见的弹窗选择器
      const modalSelectors = [
        '.modal',
        '.dialog',
        '.popup',
        '[role="dialog"]',
        '.ant-modal',
        '.el-dialog',
        '.v-dialog',
      ];

      for (const selector of modalSelectors) {
        const modal = document.querySelector(selector);
        if (modal && window.getComputedStyle(modal).display !== 'none') {
          return {
            found: true,
            selector: selector,
            content: modal.textContent?.substring(0, 200),
          };
        }
      }

      return { found: false };
    });

    if (hasModal.found) {
      console.log(`✅ 发现弹窗: ${hasModal.selector}`);
      console.log(`弹窗内容: ${hasModal.content}`);

      // 检查弹窗中的班级选项
      const classOptions = await page.evaluate(() => {
        const options = Array.from(document.querySelectorAll('li, .item, .option, [role="option"]'));
        return options
          .filter(opt => opt.offsetParent !== null)
          .map(opt => opt.textContent?.trim())
          .slice(0, 20);
      });

      console.log(`📋 班级选项 (${classOptions.length} 个):`);
      classOptions.forEach(opt => {
        console.log(`   - ${opt}`);
      });

      await page.screenshot({ path: path.join(CONFIG.screenshotDir, '05-class-modal.png') });
    } else {
      console.error('❌ 未发现班级选择弹窗');
      console.log('📋 诊断建议:');
      console.log('   1. 检查控制台是否有JavaScript错误');
      console.log('   2. 检查网络请求是否成功');
      console.log('   3. 检查用户是否有班级数据');
      console.log('   4. 检查前端代码逻辑');
    }

    // 步骤 7: 收集更多信息
    console.log('\n📊 步骤7: 收集诊断信息');

    const pageInfo = await page.evaluate(() => {
      return {
        url: window.location.href,
        title: document.title,
        localStorage: { ...localStorage },
      };
    });

    console.log('📋 页面信息:');
    console.log(`   URL: ${pageInfo.url}`);
    console.log(`   标题: ${pageInfo.title}`);

    console.log('\n📦 LocalStorage:');
    Object.keys(pageInfo.localStorage).forEach(key => {
      const value = pageInfo.localStorage[key];
      const displayValue = value.length > 100 ? value.substring(0, 100) + '...' : value;
      console.log(`   ${key}: ${displayValue}`);
    });

    await page.screenshot({ path: path.join(CONFIG.screenshotDir, '06-final-state.png'), fullPage: true });

    // 保存诊断报告
    const report = {
      timestamp: new Date().toISOString(),
      config: CONFIG,
      pageInfo: pageInfo,
      buttonsFound: startTeachingButtons,
      modalFound: hasModal,
    };

    fs.writeFileSync(
      path.join(CONFIG.screenshotDir, 'diagnosis-report.json'),
      JSON.stringify(report, null, 2)
    );

    console.log('\n📄 诊断报告已保存到: screenshots/diagnosis-report.json');

    // 等待一段时间让用户查看
    console.log('\n⏳ 等待20秒，请查看浏览器中的状态...');
    await new Promise(resolve => setTimeout(resolve, 20000));

  } catch (error) {
    console.error('\n❌ 发生错误:', error.message);
    await page.screenshot({ path: path.join(CONFIG.screenshotDir, 'error.png') });
  } finally {
    console.log('\n✅ 诊断完成');
    console.log('📸 截图已保存到:', CONFIG.screenshotDir);
    await browser.close();
  }
}

// 运行诊断
diagnose().catch(console.error);

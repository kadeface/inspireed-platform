/**
 * 使用系统 Chrome 的诊断脚本 - 简化版
 */

import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const CONFIG = {
  baseURL: 'http://111.230.61.28',
  loginURL: 'http://111.230.61.28/login',
  username: 'lzd',
  password: '123',
  screenshotDir: path.join(__dirname, '../../screenshots'),
};

if (!fs.existsSync(CONFIG.screenshotDir)) {
  fs.mkdirSync(CONFIG.screenshotDir, { recursive: true });
}

async function diagnose() {
  console.log('🚀 开始诊断"开始上课"按钮问题\n');

  const browser = await puppeteer.launch({
    headless: false,
    devtools: true,
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    defaultViewport: { width: 1280, height: 720 },
  });

  const page = await browser.newPage();

  const consoleErrors = [];
  const pageErrors = [];
  const apiRequests = [];

  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();
    if (type === 'error') {
      consoleErrors.push(text);
      console.log(`🔴 控制台错误: ${text}`);
    } else if (type === 'warning') {
      console.log(`⚠️  控制台警告: ${text}`);
    }
  });

  page.on('pageerror', error => {
    pageErrors.push(error.message);
    console.log(`🔴 页面错误: ${error.message}`);
  });

  page.on('request', request => {
    const url = request.url();
    if (url.includes('/api/')) {
      console.log(`📤 API请求: ${request.method()} ${url}`);
      apiRequests.push({ method: request.method(), url, timestamp: new Date().toISOString() });
    }
  });

  page.on('response', response => {
    const url = response.url();
    if (url.includes('/api/')) {
      const status = response.status();
      console.log(`📥 API响应: ${status} ${url}`);
      const req = apiRequests.find(r => r.url === url);
      if (req) req.status = status;
    }
  });

  try {
    // 步骤 1: 访问登录页面
    console.log('\n🌐 步骤1: 访问登录页面');
    await page.goto(CONFIG.loginURL, { waitUntil: 'networkidle2', timeout: 30000 });
    console.log('✅ 登录页面加载完成');
    await page.screenshot({ path: path.join(CONFIG.screenshotDir, '01-login-page.png') });

    // 步骤 2: 填写表单
    console.log('\n📝 步骤2: 填写登录表单');

    // 尝试填写用户名
    try {
      await page.type('input[name="username"]', CONFIG.username, { delay: 100 });
    } catch (e) {
      try {
        await page.type('input[type="text"]', CONFIG.username);
      } catch (e2) {
        console.error('❌ 无法填写用户名');
      }
    }

    // 尝试填写密码
    try {
      await page.type('input[name="password"]', CONFIG.password, { delay: 100 });
    } catch (e) {
      try {
        await page.type('input[type="password"]', CONFIG.password);
      } catch (e2) {
        console.error('❌ 无法填写密码');
      }
    }

    await page.screenshot({ path: path.join(CONFIG.screenshotDir, '02-form-filled.png') });
    console.log('✅ 表单填写完成');

    // 步骤 3: 点击登录
    console.log('\n🖱️  步骤3: 点击登录按钮');

    try {
      await Promise.all([
        page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 }).catch(() => {}),
        page.click('button[type="submit"]'),
      ]);
    } catch (e) {
      try {
        await page.click('button:has-text("登录")');
      } catch (e2) {
        console.log('⚠️  点击登录按钮可能失败');
      }
    }

    console.log('✅ 登录操作完成');
    await page.screenshot({ path: path.join(CONFIG.screenshotDir, '03-after-login.png') });

    // 等待页面加载
    await new Promise(resolve => setTimeout(resolve, 3000));

    // 步骤 4: 查找所有按钮
    console.log('\n🔍 步骤4: 分析页面按钮');

    const allButtons = await page.evaluate(() => {
      const elements = Array.from(document.querySelectorAll('button, a'));
      return elements
        .filter(el => el.offsetParent !== null)
        .map(el => ({
          tag: el.tagName,
          text: el.textContent?.trim().substring(0, 60),
          href: el.getAttribute('href'),
          onclick: el.getAttribute('onclick'),
        }))
        .slice(0, 40);
    });

    console.log('📋 页面上的按钮和链接:');
    allButtons.forEach(btn => {
      console.log(`   [${btn.tag}] ${btn.text}`);
    });

    // 查找"开始上课"按钮
    const startButtons = allButtons.filter(btn =>
      btn.text.includes('开始上课') ||
      btn.text.includes('开始授课') ||
      btn.text.includes('授课模式') ||
      btn.text.includes('进入课堂')
    );

    if (startButtons.length === 0) {
      console.error('\n❌ 未找到"开始上课"相关按钮');

      // 列出可能相关的链接
      const relevantLinks = allButtons.filter(btn =>
        btn.text.includes('教案') ||
        btn.text.includes('课程') ||
        btn.text.includes('教学') ||
        btn.text.includes('课堂')
      );

      console.log('📋 相关链接:');
      relevantLinks.forEach(link => {
        console.log(`   ${link.text} ${link.href ? '-> ' + link.href : ''}`);
      });

      console.log('\n等待30秒，请手动查看浏览器...');
      await new Promise(resolve => setTimeout(resolve, 30000));
      await browser.close();
      return;
    }

    console.log(`\n✅ 找到 ${startButtons.length} 个"开始上课"相关按钮:`);
    startButtons.forEach(btn => {
      console.log(`   [${btn.tag}] ${btn.text}`);
    });

    await page.screenshot({ path: path.join(CONFIG.screenshotDir, '04-found-start-button.png') });

    // 步骤 5: 点击"开始上课"
    console.log('\n🖱️  步骤5: 点击"开始上课"按钮');

    apiRequests.length = 0; // 清空之前的请求记录

    try {
      // 使用 XPath 点击包含"开始上课"文本的元素
      await page.evaluateHandle(() => {
        const elements = Array.from(document.querySelectorAll('button, a'));
        const target = elements.find(el => {
          const text = el.textContent || '';
          return text.includes('开始上课') || text.includes('开始授课');
        });
        if (target) target.click();
      });

      console.log('✅ 按钮已点击');
      await new Promise(resolve => setTimeout(resolve, 3000));
      await page.screenshot({ path: path.join(CONFIG.screenshotDir, '05-after-click.png') });
    } catch (e) {
      console.error('❌ 点击按钮失败:', e.message);
    }

    // 步骤 6: 检查弹窗
    console.log('\n🔍 步骤6: 检查班级选择弹窗');

    const modalInfo = await page.evaluate(() => {
      // 检查所有可能的弹窗
      const allElements = Array.from(document.querySelectorAll('*'));
      const modals = allElements.filter(el => {
        const text = el.textContent || '';
        const style = window.getComputedStyle(el);
        return (
          style.position === 'fixed' &&
          style.zIndex > '100' &&
          text.includes('班级') &&
          style.display !== 'none'
        );
      });

      if (modals.length > 0) {
        return {
          found: true,
          count: modals.length,
          content: modals.map(m => m.textContent?.substring(0, 200)).join('\n---\n'),
        };
      }

      return { found: false };
    });

    if (modalInfo.found) {
      console.log(`✅ 发现弹窗 (${modalInfo.count} 个)`);
      console.log(`内容预览:\n${modalInfo.content}`);

      // 查找班级选项
      const classOptions = await page.evaluate(() => {
        const selectors = ['li', '.item', '.option', '[role="option"]', '.class-item'];
        for (const sel of selectors) {
          const options = Array.from(document.querySelectorAll(sel))
            .filter(opt => opt.offsetParent !== null && opt.textContent?.trim())
            .map(opt => opt.textContent?.trim());
          if (options.length > 0) return options.slice(0, 20);
        }
        return [];
      });

      console.log(`📋 班级选项 (${classOptions.length} 个):`);
      classOptions.forEach(opt => console.log(`   - ${opt}`));

      await page.screenshot({ path: path.join(CONFIG.screenshotDir, '06-class-modal.png') });
    } else {
      console.error('❌ 未发现班级选择弹窗');

      console.log('\n📋 诊断信息:');
      console.log(`   控制台错误: ${consoleErrors.length}`);
      console.log(`   页面错误: ${pageErrors.length}`);
      console.log(`   API请求: ${apiRequests.length}`);

      if (consoleErrors.length > 0) {
        console.log('\n🔴 控制台错误:');
        consoleErrors.slice(0, 10).forEach(err => console.log(`   - ${err}`));
      }

      if (apiRequests.length > 0) {
        console.log('\n📤 点击后的API请求:');
        apiRequests.forEach(req => {
          console.log(`   - ${req.method} ${req.url} ${req.status ? `(${req.status})` : ''}`);
        });
      }

      console.log('\n💡 可能原因:');
      console.log('   1. 用户没有关联班级');
      console.log('   2. 前端代码逻辑问题');
      console.log('   3. API请求失败');
    }

    // 步骤 7: 收集最终信息
    console.log('\n📊 收集最终诊断信息');

    const pageInfo = await page.evaluate(() => ({
      url: window.location.href,
      title: document.title,
      localStorageKeys: Object.keys(localStorage),
      sessionStorageKeys: Object.keys(sessionStorage),
    }));

    console.log(`   URL: ${pageInfo.url}`);
    console.log(`   标题: ${pageInfo.title}`);
    console.log(`   LocalStorage键: ${pageInfo.localStorageKeys.join(', ')}`);

    // 保存报告
    const report = {
      timestamp: new Date().toISOString(),
      pageInfo,
      buttonsFound: startButtons,
      modalFound: modalInfo,
      consoleErrors,
      pageErrors,
      apiRequests,
    };

    fs.writeFileSync(
      path.join(CONFIG.screenshotDir, 'diagnosis-report.json'),
      JSON.stringify(report, null, 2)
    );

    console.log('\n📄 诊断报告已保存');
    await page.screenshot({ path: path.join(CONFIG.screenshotDir, '07-final-state.png'), fullPage: true });

    console.log('\n⏳ 等待30秒，请查看浏览器...');
    await new Promise(resolve => setTimeout(resolve, 30000));

  } catch (error) {
    console.error('\n❌ 错误:', error.message);
    await page.screenshot({ path: path.join(CONFIG.screenshotDir, 'error.png') });
  } finally {
    await browser.close();
    console.log('\n✅ 诊断完成');
  }
}

diagnose().catch(console.error);

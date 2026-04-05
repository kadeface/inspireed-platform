/**
 * 半自动诊断脚本 - 手动登录后自动测试"开始上课"
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
  screenshotDir: path.join(__dirname, '../../screenshots'),
};

if (!fs.existsSync(CONFIG.screenshotDir)) {
  fs.mkdirSync(CONFIG.screenshotDir, { recursive: true });
}

async function diagnose() {
  console.log('🚀 开始诊断"开始上课"按钮问题\n');
  console.log('⚠️  这是一个半自动脚本，需要您手动登录\n');

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
    if (msg.type() === 'error') {
      const text = msg.text();
      consoleErrors.push(text);
      console.log(`🔴 控制台错误: ${text}`);
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
      apiRequests.push({ method: request.method(), url, time: Date.now() });
    }
  });

  page.on('response', response => {
    const url = response.url();
    const req = apiRequests.find(r => r.url === url);
    if (req) req.status = response.status();
  });

  try {
    // 步骤 1: 打开登录页面
    console.log('🌐 步骤1: 打开登录页面');
    await page.goto(CONFIG.loginURL);
    await page.screenshot({ path: path.join(CONFIG.screenshotDir, '01-login-page.png') });

    console.log('\n⏳ 请在浏览器中手动登录:');
    console.log(`   URL: ${CONFIG.loginURL}`);
    console.log('   用户名: lzd');
    console.log('   密码: 123');
    console.log('\n登录成功后，请导航到包含"开始上课"按钮的页面');
    console.log('然后在控制台输入: done() 并按回车继续...\n');

    // 等待用户登录
    await page.evaluate(() => {
      window.done = () => {
        window.__manualLoginComplete = true;
      };
    });

    await page.waitForFunction('window.__manualLoginComplete', { timeout: 0 });
    console.log('✅ 用户确认登录完成\n');

    await page.screenshot({ path: path.join(CONFIG.screenshotDir, '02-after-login.png') });
    await new Promise(resolve => setTimeout(resolve, 2000));

    // 步骤 2: 分析页面
    console.log('🔍 步骤2: 分析当前页面');

    const pageInfo = await page.evaluate(() => ({
      url: window.location.href,
      title: document.title,
      pathname: window.location.pathname,
    }));

    console.log(`   URL: ${pageInfo.url}`);
    console.log(`   标题: ${pageInfo.title}`);
    console.log(`   路径: ${pageInfo.pathname}`);

    // 步骤 3: 查找所有按钮
    console.log('\n📋 步骤3: 查找页面上的所有按钮');

    const allButtons = await page.evaluate(() => {
      const elements = Array.from(document.querySelectorAll('button, a, [role="button"]'));
      return elements
        .filter(el => {
          const rect = el.getBoundingClientRect();
          return rect.width > 0 && rect.height > 0;
        })
        .map(el => ({
          tag: el.tagName,
          text: el.textContent?.trim().substring(0, 80),
          className: el.className,
          id: el.id,
          href: el.getAttribute('href'),
          role: el.getAttribute('role'),
        }));
    });

    console.log(`\n共找到 ${allButtons.length} 个可点击元素:\n`);

    // 分类显示
    const teachingRelated = allButtons.filter(btn =>
      btn.text.includes('开始上课') ||
      btn.text.includes('开始授课') ||
      btn.text.includes('授课模式') ||
      btn.text.includes('进入课堂') ||
      btn.text.includes('上课')
    );

    const lessonRelated = allButtons.filter(btn =>
      btn.text.includes('教案') ||
      btn.text.includes('课程') ||
      btn.text.includes('教学')
    );

    const classRelated = allButtons.filter(btn =>
      btn.text.includes('班级') ||
      btn.text.includes('课堂')
    );

    if (teachingRelated.length > 0) {
      console.log('✅ 找到"开始上课"相关按钮:');
      teachingRelated.forEach(btn => {
        console.log(`   [${btn.tag}] ${btn.text}`);
        console.log(`      class: ${btn.className}`);
        console.log(`      id: ${btn.id}`);
      });
    }

    if (lessonRelated.length > 0) {
      console.log('\n📚 教案相关按钮:');
      lessonRelated.slice(0, 10).forEach(btn => {
        console.log(`   [${btn.tag}] ${btn.text}`);
      });
    }

    if (classRelated.length > 0) {
      console.log('\n🏫 班级相关按钮:');
      classRelated.slice(0, 10).forEach(btn => {
        console.log(`   [${btn.tag}] ${btn.text}`);
      });
    }

    // 步骤 4: 如果找到"开始上课"按钮，点击它
    if (teachingRelated.length > 0) {
      console.log('\n🖱️  步骤4: 点击"开始上课"按钮');

      // 清空之前的 API 请求
      apiRequests.length = 0;
      consoleErrors.length = 0;

      // 点击第一个按钮
      await page.evaluate(() => {
        const elements = Array.from(document.querySelectorAll('button, a, [role="button"]'));
        const target = elements.find(el => {
          const text = el.textContent || '';
          return (
            text.includes('开始上课') ||
            text.includes('开始授课') ||
            text.includes('上课')
          );
        });
        if (target) {
          target.scrollIntoView();
          target.click();
          return { clicked: true, text: target.textContent };
        }
        return { clicked: false };
      }).then(result => {
        console.log(result.clicked ? `✅ 已点击: ${result.text}` : '❌ 未找到按钮');
      });

      // 等待响应
      await new Promise(resolve => setTimeout(resolve, 3000));

      await page.screenshot({ path: path.join(CONFIG.screenshotDir, '03-after-click.png'), fullPage: true });

      // 步骤 5: 检查弹窗
      console.log('\n🔍 步骤5: 检查是否有弹窗');

      const modalCheck = await page.evaluate(() => {
        // 查找所有固定定位的元素
        const fixedElements = Array.from(document.querySelectorAll('*')).filter(el => {
          const style = window.getComputedStyle(el);
          return (
            style.position === 'fixed' &&
            parseInt(style.zIndex) > 100 &&
            style.display !== 'none' &&
            style.visibility !== 'hidden' &&
            el.textContent?.trim()
          );
        });

        // 查找包含"班级"的弹窗
        const classModals = fixedElements.filter(el =>
          el.textContent?.includes('班级') ||
          el.className?.toLowerCase().includes('modal') ||
          el.className?.toLowerCase().includes('dialog')
        );

        return {
          fixedElementsCount: fixedElements.length,
          classModalsCount: classModals.length,
          classModalsContent: classModals.map(m => ({
            tag: m.tagName,
            class: m.className,
            text: m.textContent?.substring(0, 200),
          })),
        };
      });

      console.log(`固定定位元素: ${modalCheck.fixedElementsCount}`);
      console.log(`班级相关弹窗: ${modalCheck.classModalsCount}`);

      if (modalCheck.classModalsCount > 0) {
        console.log('\n✅ 发现班级选择弹窗!');
        modalCheck.classModalsContent.forEach(modal => {
          console.log(`\n[${modal.tag}]`);
          console.log(`class: ${modal.class}`);
          console.log(`内容: ${modal.text}`);
        });

        // 查找班级选项
        const classOptions = await page.evaluate(() => {
          const optionSelectors = [
            'li', '.item', '.option', '[role="option"]',
            '.class-item', '.class-option', '[class*="class"]'
          ];

          const allOptions = [];
          for (const sel of optionSelectors) {
            const elements = Array.from(document.querySelectorAll(sel));
            const visible = elements.filter(el => {
              const rect = el.getBoundingClientRect();
              return rect.width > 0 && rect.height > 0;
            });
            if (visible.length > 0) {
              visible.forEach(el => {
                const text = el.textContent?.trim();
                if (text) {
                  allOptions.push({ selector: sel, text });
                }
              });
            }
          }
          return allOptions.slice(0, 30);
        });

        console.log('\n📋 班级选项:');
        classOptions.forEach(opt => {
          console.log(`   [${opt.selector}] ${opt.text}`);
        });

        await page.screenshot({ path: path.join(CONFIG.screenshotDir, '04-class-modal.png') });
      } else {
        console.log('\n❌ 未发现班级选择弹窗');
        console.log('\n📊 诊断信息:');
        console.log(`   控制台错误: ${consoleErrors.length}`);
        console.log(`   API请求: ${apiRequests.length}`);

        if (consoleErrors.length > 0) {
          console.log('\n🔴 控制台错误详情:');
          consoleErrors.forEach(err => console.log(`   - ${err}`));
        }

        if (apiRequests.length > 0) {
          console.log('\n📤 点击后的API请求:');
          apiRequests.forEach(req => {
            console.log(`   - ${req.method} ${req.url}`);
            if (req.status) console.log(`     状态: ${req.status}`);
          });
        }

        console.log('\n💡 可能的原因:');
        console.log('   1. 当前用户没有关联的班级');
        console.log('   2. 前端代码逻辑问题');
        console.log('   3. 后端API返回错误');
        console.log('   4. 权限不足');

        console.log('\n🔧 建议:');
        console.log('   1. 检查浏览器控制台的错误信息');
        console.log('   2. 检查网络请求是否成功');
        console.log('   3. 检查用户数据中是否有班级信息');
        console.log('   4. 查看前端代码中"开始上课"按钮的点击处理逻辑');
      }

      // 步骤 6: 收集用户数据
      console.log('\n📊 步骤6: 收储用户数据');

      const userData = await page.evaluate(() => {
        const getStorage = (storage) => {
          const data = {};
          for (let i = 0; i < storage.length; i++) {
            const key = storage.key(i);
            if (key) {
              try {
                const value = storage.getItem(key);
                data[key] = value.length > 200 ? value.substring(0, 200) + '...' : value;
              } catch (e) {
                data[key] = '[无法读取]';
              }
            }
          }
          return data;
        };

        return {
          localStorage: getStorage(localStorage),
          sessionStorage: getStorage(sessionStorage),
        };
      });

      console.log('\n📦 LocalStorage:');
      Object.entries(userData.localStorage).forEach(([key, value]) => {
        console.log(`   ${key}: ${value}`);
      });

      // 查找用户信息
      const userInfo = await page.evaluate(() => {
        const userKey = Object.keys(localStorage).find(k =>
          k.toLowerCase().includes('user') ||
          k.toLowerCase().includes('token')
        );

        if (userKey) {
          try {
            return JSON.parse(localStorage.getItem(userKey));
          } catch (e) {
            return null;
          }
        }
        return null;
      });

      if (userInfo) {
        console.log('\n👤 用户信息:');
        console.log(JSON.stringify(userInfo, null, 2));
      }

      // 保存完整报告
      const report = {
        timestamp: new Date().toISOString(),
        pageInfo,
        buttonsFound: {
          total: allButtons.length,
          teachingRelated: teachingRelated.length,
          lessonRelated: lessonRelated.length,
          classRelated: classRelated.length,
        },
        teachingButtons: teachingRelated,
        modalFound: modalCheck.classModalsCount > 0,
        modalDetails: modalCheck.classModalsContent,
        consoleErrors,
        apiRequests,
        userData: {
          localStorageKeys: Object.keys(userData.localStorage),
          userInfo,
        },
      };

      fs.writeFileSync(
        path.join(CONFIG.screenshotDir, 'diagnosis-report.json'),
        JSON.stringify(report, null, 2)
      );

      console.log('\n📄 完整报告已保存到: screenshots/diagnosis-report.json');

    } else {
      console.log('\n❌ 当前页面没有找到"开始上课"按钮');
      console.log('请导航到正确的页面，然后刷新页面重新运行脚本');
      console.log('\n等待30秒...');
      await new Promise(resolve => setTimeout(resolve, 30000));
    }

    await page.screenshot({ path: path.join(CONFIG.screenshotDir, '05-final-state.png'), fullPage: true });

    console.log('\n⏳ 保持浏览器打开60秒供您查看...');
    console.log('   截图已保存到:', CONFIG.screenshotDir);
    await new Promise(resolve => setTimeout(resolve, 60000));

  } catch (error) {
    console.error('\n❌ 错误:', error.message);
    await page.screenshot({ path: path.join(CONFIG.screenshotDir, 'error.png') });
  } finally {
    await browser.close();
    console.log('\n✅ 诊断完成');
  }
}

diagnose().catch(console.error);

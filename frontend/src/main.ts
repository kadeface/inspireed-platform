import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import './assets/main.css'

if (import.meta.env.DEV) {
  console.info('[InspireEd] main.ts 模块已加载，开始创建应用')

  function showDevGlobalError(msg: string) {
    let el = document.getElementById('dev-global-error')
    if (!el) {
      el = document.createElement('pre')
      el.id = 'dev-global-error'
      el.setAttribute(
        'style',
        'position:fixed;z-index:2147483647;left:0;right:0;bottom:0;max-height:50vh;overflow:auto;margin:0;padding:12px;background:#fee;color:#900;font:12px/1.4 monospace;border-top:3px solid #c00;'
      )
      document.body.appendChild(el)
    }
    el.textContent = msg
  }

  window.addEventListener(
    'error',
    (ev: ErrorEvent) => {
      showDevGlobalError(
        '[全局 error]\n' +
          (ev.message || '') +
          '\n' +
          (ev.filename || '') +
          (ev.lineno ? `:${ev.lineno}:${ev.colno}` : '')
      )
    },
    true
  )
  window.addEventListener('unhandledrejection', (ev: PromiseRejectionEvent) => {
    const r = ev.reason
    showDevGlobalError(
      '[全局 unhandledrejection]\n' +
        (r instanceof Error && r.stack ? r.stack : String(r))
    )
  })
}

const app = createApp(App)
const pinia = createPinia()

if (import.meta.env.DEV) {
  app.config.errorHandler = (err, _instance, info) => {
    console.error('[Vue errorHandler]', err, info)
    const msg = `[Vue 渲染错误]\n${err instanceof Error ? err.message : String(err)}\n${info}`
    let el = document.getElementById('dev-vue-error')
    if (!el) {
      el = document.createElement('pre')
      el.id = 'dev-vue-error'
      el.setAttribute(
        'style',
        'position:fixed;z-index:2147483646;left:0;right:0;bottom:0;max-height:40vh;overflow:auto;margin:0;padding:12px;background:#fff7ed;color:#9a3412;font:12px/1.4 monospace;border-top:2px solid #ea580c;'
      )
      document.body.appendChild(el)
    }
    el.textContent = msg
  }
}

app.use(pinia)
app.use(router)

// Element Plus 已安装并启用，配置中文本地化
app.use(ElementPlus, {
  locale: zhCn,
})

// 注册所有 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

void router
  .isReady()
  .then(() => {
    try {
      app.mount('#app')
      const boot = document.getElementById('app-static-boot')
      if (boot) boot.remove()
      if (import.meta.env.DEV) {
        console.info('[InspireEd] app.mount 完成')
      }
    } catch (e) {
      console.error('[InspireEd] app.mount 失败', e)
      const root = document.getElementById('app')
      if (root) {
        root.innerHTML =
          '<pre style="padding:16px;color:#b91c1c;font:14px/1.5 monospace;white-space:pre-wrap;">应用挂载失败（请截图发开发者）：\n\n' +
          (e instanceof Error ? e.stack || e.message : String(e)) +
          '</pre>'
      }
      throw e
    }
  })
  .catch((e) => {
    console.error('[InspireEd] router.isReady 失败', e)
    const root = document.getElementById('app')
    if (root) {
      root.innerHTML =
        '<pre style="padding:16px;color:#b91c1c;font:14px/1.5 monospace;white-space:pre-wrap;">路由初始化失败（请截图发开发者）：\n\n' +
        (e instanceof Error ? e.stack || e.message : String(e)) +
        '</pre>'
    }
  })

/**
 * Toast通知 Composable
 */
import { createVNode, render } from 'vue'
import type { App as VueApp } from 'vue'
import Toast, { type ToastOptions } from '../components/Common/Toast.vue'

let toastInstance: any = null
let container: HTMLElement | null = null

function ensureInstance() {
  if (!toastInstance) {
    container = document.createElement('div')
    document.body.appendChild(container)
    
    const vnode = createVNode(Toast)
    render(vnode, container)
    toastInstance = vnode.component?.exposed
  }
  
  return toastInstance
}

export function useToast() {
  const instance = ensureInstance()
  
  return {
    show: (options: ToastOptions) => instance.show(options),
    success: (message: string, title?: string) => instance.success(message, title),
    error: (message: string, title?: string) => instance.error(message, title),
    warning: (message: string, title?: string) => instance.warning(message, title),
    info: (message: string, title?: string) => instance.info(message, title),
    remove: (id: string) => instance.remove(id)
  }
}

// 全局安装
export function installToast(app: VueApp) {
  const toast = useToast()
  app.config.globalProperties.$toast = toast
  
  // 也可以通过 inject 使用
  app.provide('toast', toast)
}

// 导出默认实例
export const toast = {
  show: (options: ToastOptions) => ensureInstance().show(options),
  success: (message: string, title?: string) => ensureInstance().success(message, title),
  error: (message: string, title?: string) => ensureInstance().error(message, title),
  warning: (message: string, title?: string) => ensureInstance().warning(message, title),
  info: (message: string, title?: string) => ensureInstance().info(message, title),
  remove: (id: string) => ensureInstance().remove(id)
}

export default toast


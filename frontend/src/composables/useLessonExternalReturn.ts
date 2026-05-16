import { onBeforeUnmount, onMounted } from 'vue'
import {
  handleLessonReturnMessage,
  LESSON_RETURN_CHANNEL,
} from '@/utils/externalBrowserReturn'

/** 授课页监听外部浏览窗口的「继续听课」消息 */
export function useLessonExternalReturn() {
  let postMessageHandler: ((event: MessageEvent) => void) | null = null
  let channel: BroadcastChannel | null = null

  onMounted(() => {
    postMessageHandler = (event: MessageEvent) => {
      if (event.origin !== window.location.origin) return
      handleLessonReturnMessage(event.data)
    }
    window.addEventListener('message', postMessageHandler)

    try {
      channel = new BroadcastChannel(LESSON_RETURN_CHANNEL)
      channel.onmessage = (event: MessageEvent) => {
        handleLessonReturnMessage(event.data)
      }
    } catch {
      channel = null
    }
  })

  onBeforeUnmount(() => {
    if (postMessageHandler) {
      window.removeEventListener('message', postMessageHandler)
      postMessageHandler = null
    }
    if (channel) {
      channel.close()
      channel = null
    }
  })
}

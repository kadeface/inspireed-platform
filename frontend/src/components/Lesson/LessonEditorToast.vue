<template>
  <Transition name="toast-slide">
    <div v-if="toast.show" class="fixed top-4 right-4 z-50 max-w-sm">
      <div
        :class="[
          'rounded-lg shadow-xl p-4 border-l-4 transform transition-all duration-300',
          toast.type === 'success'
            ? 'bg-green-50 border-green-400 border-l-green-500'
            : toast.type === 'warning'
              ? 'bg-amber-50 border-amber-400 border-l-amber-500'
              : 'bg-red-50 border-red-400 border-l-red-500',
        ]"
      >
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <div
              :class="[
                'rounded-full p-1',
                toast.type === 'success'
                  ? 'bg-green-100'
                  : toast.type === 'warning'
                    ? 'bg-amber-100'
                    : 'bg-red-100',
              ]"
            >
              <svg
                v-if="toast.type === 'success'"
                class="h-4 w-4 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <svg
                v-else-if="toast.type === 'warning'"
                class="h-4 w-4 text-amber-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
              <svg
                v-else
                class="h-4 w-4 text-red-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </div>
          </div>
          <div class="ml-3 flex-1">
            <p
              :class="[
                'text-sm font-semibold',
                toast.type === 'success'
                  ? 'text-green-800'
                  : toast.type === 'warning'
                    ? 'text-amber-800'
                    : 'text-red-800',
              ]"
            >
              {{ toast.message }}
            </p>
          </div>
          <button
            @click="$emit('close')"
            class="ml-2 flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
export interface ToastData {
  show: boolean
  type: 'success' | 'error' | 'warning'
  message: string
}

interface Props {
  toast: ToastData
}

defineProps<Props>()

defineEmits<{
  close: []
}>()
</script>

<style scoped>
.toast-slide-enter-active {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.toast-slide-leave-active {
  transition: all 0.3s ease-in;
}

.toast-slide-enter-from {
  opacity: 0;
  transform: translateX(100%) scale(0.8);
}

.toast-slide-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.8);
}

/* 添加脉冲动画效果 */
@keyframes pulse-success {
  0% {
    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(34, 197, 94, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0);
  }
}

.toast-slide-enter-active .rounded-lg {
  animation: pulse-success 0.6s ease-out;
}
</style>

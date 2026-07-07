<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex justify-between items-start mb-6">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">AI 配置</h2>
        <p class="text-gray-600 mt-2">
          文本助手与个性化学习图像链路分开配置。API Key 仍由后端环境变量提供。
        </p>
      </div>
      <el-tag :type="settings?.api_key_configured ? 'success' : 'warning'">
        API Key {{ settings?.api_key_configured ? '已配置' : '未配置' }}
      </el-tag>
    </div>

    <el-alert
      class="mb-6"
      type="info"
      :closable="false"
      show-icon
      title="当前页面只管理运行参数；不会在前端显示或存储 API Key。"
    />

    <div v-if="loading" class="py-10 text-center text-gray-500">
      正在加载配置...
    </div>

    <div v-else>
      <div v-if="errorMessage" class="mb-4">
        <el-alert :title="errorMessage" type="error" :closable="false" show-icon />
      </div>

      <el-form label-width="150px" class="space-y-8">
        <div class="rounded-xl border border-slate-200 p-5">
          <div class="mb-4">
            <h3 class="text-lg font-semibold text-gray-900">文本助手配置</h3>
            <p class="text-sm text-gray-500 mt-1">
              影响教师 AI 助手、学生 AI 助手、QA Cell 等文本问答入口。
            </p>
          </div>
          <el-form-item label="Base URL">
            <el-input v-model="form.text.base_url" placeholder="https://api.openai.com/v1" />
          </el-form-item>
          <el-form-item label="模型">
            <el-input v-model="form.text.model" placeholder="gpt-4o-mini" />
          </el-form-item>
          <el-form-item label="Max Tokens">
            <el-input-number v-model="form.text.max_tokens" :min="1" :max="100000" />
          </el-form-item>
          <el-form-item label="Temperature">
            <el-input-number v-model="form.text.temperature" :min="0" :max="2" :step="0.1" :precision="1" />
          </el-form-item>
        </div>

        <div class="rounded-xl border border-slate-200 p-5">
          <div class="mb-4">
            <h3 class="text-lg font-semibold text-gray-900">个性化学习图像配置</h3>
            <p class="text-sm text-gray-500 mt-1">
              影响题图可读性检查、图像理解引导和标准解释生成。
            </p>
          </div>
          <el-form-item label="Base URL">
            <el-input v-model="form.self_study_vision.base_url" placeholder="https://api.openai.com/v1" />
          </el-form-item>
          <el-form-item label="模型">
            <el-input v-model="form.self_study_vision.model" placeholder="gpt-4.1-mini" />
          </el-form-item>
          <el-form-item label="Max Tokens">
            <el-input-number v-model="form.self_study_vision.max_tokens" :min="1" :max="100000" />
          </el-form-item>
          <el-form-item label="Temperature">
            <el-input-number v-model="form.self_study_vision.temperature" :min="0" :max="2" :step="0.1" :precision="1" />
          </el-form-item>
        </div>

        <div class="flex justify-end gap-3">
          <el-button @click="loadSettings" :disabled="saving">重新加载</el-button>
          <el-button type="primary" @click="saveSettings" :loading="saving">保存配置</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import aiSettingsService from '@/services/aiSettings'
import type { AISettingsResponse, AISettingsUpdateRequest } from '@/types/aiSettings'

const loading = ref(false)
const saving = ref(false)
const errorMessage = ref<string | null>(null)
const settings = ref<AISettingsResponse | null>(null)

const form = reactive<AISettingsUpdateRequest>({
  text: {
    base_url: '',
    model: '',
    max_tokens: 2000,
    temperature: 0.7,
  },
  self_study_vision: {
    base_url: '',
    model: '',
    max_tokens: 2000,
    temperature: 0.1,
  },
})

function syncForm(data: AISettingsResponse) {
  form.text.base_url = data.text.base_url
  form.text.model = data.text.model
  form.text.max_tokens = data.text.max_tokens
  form.text.temperature = data.text.temperature

  form.self_study_vision.base_url = data.self_study_vision.base_url
  form.self_study_vision.model = data.self_study_vision.model
  form.self_study_vision.max_tokens = data.self_study_vision.max_tokens
  form.self_study_vision.temperature = data.self_study_vision.temperature
}

async function loadSettings() {
  loading.value = true
  errorMessage.value = null
  try {
    const data = await aiSettingsService.getSettings()
    settings.value = data
    syncForm(data)
  } catch (error: any) {
    errorMessage.value = error.message || '加载 AI 配置失败'
  } finally {
    loading.value = false
  }
}

async function saveSettings() {
  saving.value = true
  errorMessage.value = null
  try {
    const data = await aiSettingsService.updateSettings({
      text: { ...form.text },
      self_study_vision: { ...form.self_study_vision },
    })
    settings.value = data
    syncForm(data)
    ElMessage.success('AI 配置已保存')
  } catch (error: any) {
    errorMessage.value = error.message || '保存 AI 配置失败'
  } finally {
    saving.value = false
  }
}

onMounted(loadSettings)
</script>

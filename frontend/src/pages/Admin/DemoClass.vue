<template>
  <div class="demo-class p-6">
    <div class="header flex items-center gap-4 mb-8">
      <el-button @click="router.back()" circle>
        <el-icon><ArrowLeft /></el-icon>
      </el-button>
      <div>
        <h1 class="text-3xl font-bold text-gray-900">实验班</h1>
        <p class="text-gray-600 mt-2">演示账号一键开通与重置</p>
      </div>
    </div>

    <el-card v-loading="loading" class="max-w-2xl">
      <template #header>
        <span class="font-semibold">状态</span>
      </template>

      <el-descriptions v-if="status" :column="1" border>
        <el-descriptions-item label="学校">
          {{ status.school_name }}
          <el-tag :type="status.school_ready ? 'success' : 'warning'" size="small" class="ml-2">
            {{ status.school_ready ? '已就绪' : '未创建' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="班级">
          {{ status.classroom_name }}
          <el-tag :type="status.classroom_ready ? 'success' : 'warning'" size="small" class="ml-2">
            {{ status.classroom_ready ? '已就绪' : '未创建' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="账号进度">
          {{ status.ready_accounts }} / {{ status.target_accounts }}
        </el-descriptions-item>
        <el-descriptions-item label="账号规则">
          {{ status.account_rule }}
        </el-descriptions-item>
      </el-descriptions>

      <div class="actions mt-6 flex gap-3">
        <el-button type="primary" :loading="provisioning" @click="handleProvision">
          一键创建/补齐
        </el-button>
        <el-button type="warning" :loading="resetting" @click="handleResetPasswords">
          一键重置密码
        </el-button>
        <el-button @click="handleCopyAccountList">复制账号清单</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  demoClassService,
  buildAccountListText,
  type DemoClassStatus,
} from '@/services/demoClass'

const router = useRouter()

const status = ref<DemoClassStatus | null>(null)
const loading = ref(false)
const provisioning = ref(false)
const resetting = ref(false)

async function loadStatus() {
  loading.value = true
  try {
    status.value = await demoClassService.getStatus()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载状态失败')
  } finally {
    loading.value = false
  }
}

async function handleProvision() {
  try {
    await ElMessageBox.confirm(
      '确定要一键创建/补齐实验班演示账号吗？',
      '一键创建/补齐',
      { type: 'warning' }
    )
  } catch {
    return
  }

  provisioning.value = true
  try {
    const result = await demoClassService.provision()
    ElMessage.success(result.message || '创建/补齐成功')
    await loadStatus()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '创建/补齐失败')
  } finally {
    provisioning.value = false
  }
}

async function handleResetPasswords() {
  try {
    await ElMessageBox.confirm(
      '确定要将实验班全部账号密码重置为默认密码吗？',
      '一键重置密码',
      { type: 'warning' }
    )
  } catch {
    return
  }

  resetting.value = true
  try {
    const result = await demoClassService.resetPasswords()
    ElMessage.success(result.message || '重置成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '重置密码失败')
  } finally {
    resetting.value = false
  }
}

async function handleCopyAccountList() {
  try {
    await navigator.clipboard.writeText(buildAccountListText())
    ElMessage.success('账号清单已复制')
  } catch {
    ElMessage.error('复制失败，请手动复制')
  }
}

onMounted(loadStatus)
</script>

<style scoped>
.demo-class {
  min-height: 100vh;
  background: #f8fafc;
}
</style>

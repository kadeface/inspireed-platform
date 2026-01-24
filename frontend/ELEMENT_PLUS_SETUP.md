# Element Plus 集成指南

## 📦 安装步骤

### 1. 安装 Element Plus

```bash
cd frontend
pnpm install element-plus @element-plus/icons-vue
```

或使用 npm:
```bash
npm install element-plus @element-plus/icons-vue
```

### 2. 配置 Element Plus

#### 修改 `src/main.ts`:

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import './assets/main.css'

const app = createApp(App)
const pinia = createPinia()

// 注册 Element Plus
app.use(pinia)
app.use(router)
app.use(ElementPlus)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
```

### 3. 配置 Vite (可选)

如果需要按需导入，创建 `vite.config.ts` 配置：

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-vue-components/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      resolvers: [ElementPlusResolver()],
    }),
  ],
})
```

## 📝 使用示例

### 示例1: 基础组件使用

```vue
<template>
  <div>
    <!-- 按钮 -->
    <el-button type="primary">主要按钮</el-button>
    <el-button>默认按钮</el-button>
    <el-button type="success">成功按钮</el-button>
    <el-button type="warning">警告按钮</el-button>
    <el-button type="danger">危险按钮</el-button>

    <!-- 表单 -->
    <el-form :model="form" :rules="rules" ref="formRef">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submit">提交</el-button>
      </el-form-item>
    </el-form>

    <!-- 表格 -->
    <el-table :data="tableData">
      <el-table-column prop="name" label="姓名" />
      <el-table-column prop="age" label="年龄" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import type { FormInstance } from 'element-plus'

const formRef = ref<FormInstance>()
const form = reactive({
  username: '',
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ]
}

const tableData = ref([
  { name: '张三', age: 25 },
  { name: '李四', age: 30 },
])

const submit = async () => {
  await formRef.value?.validate()
  console.log('表单验证通过')
}
</script>
```

### 示例2: 对话框使用

```vue
<template>
  <div>
    <el-button type="primary" @click="dialogVisible = true">
      打开对话框
    </el-button>

    <el-dialog v-model="dialogVisible" title="提示" width="30%">
      <span>这是一段消息</span>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="dialogVisible = false">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const dialogVisible = ref(false)
</script>
```

### 示例3: 消息提示

```typescript
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'

// 消息提示
ElMessage.success('操作成功')
ElMessage.error('操作失败')
ElMessage.warning('警告信息')
ElMessage.info('提示信息')

// 确认对话框
ElMessageBox.confirm('确定要删除吗？', '提示', {
  confirmButtonText: '确定',
  cancelButtonText: '取消',
  type: 'warning',
})
  .then(() => {
    ElMessage.success('删除成功')
  })
  .catch(() => {
    ElMessage.info('已取消删除')
  })

// 通知
ElNotification({
  title: '通知',
  message: '这是一条通知消息',
  type: 'success',
})
```

## 🎨 主题定制 (可选)

### 自定义主题色

创建 `src/styles/element-plus.scss`:

```scss
@forward 'element-plus/theme-chalk/src/common/var.scss' with (
  $colors: (
    'primary': (
      'base': #409eff,
    ),
  )
);
```

然后在 `main.ts` 中引入：

```typescript
import 'element-plus/theme-chalk/src/button.scss'
```

## 📚 常用组件

### 表格组件

```vue
<el-table :data="data" v-loading="loading" stripe>
  <el-table-column prop="name" label="姓名" width="120" />
  <el-table-column prop="age" label="年龄" sortable />
  <el-table-column label="操作" width="200">
    <template #default="{ row }">
      <el-button size="small" @click="handleEdit(row)">编辑</el-button>
      <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
    </template>
  </el-table-column>
</el-table>
```

### 分页组件

```vue
<el-pagination
  v-model:current-page="currentPage"
  v-model:page-size="pageSize"
  :page-sizes="[10, 20, 50, 100]"
  :total="1000"
  layout="total, sizes, prev, pager, next, jumper"
  @size-change="handleSizeChange"
  @current-change="handleCurrentChange"
/>
```

### 表单组件

```vue
<el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
  <el-form-item label="活动名称" prop="name">
    <el-input v-model="form.name" placeholder="请输入活动名称" />
  </el-form-item>

  <el-form-item label="活动区域" prop="region">
    <el-select v-model="form.region" placeholder="请选择活动区域">
      <el-option label="区域一" value="region1" />
      <el-option label="区域二" value="region2" />
    </el-select>
  </el-form-item>

  <el-form-item label="活动时间" prop="date">
    <el-date-picker
      v-model="form.date"
      type="date"
      placeholder="选择日期"
      format="YYYY-MM-DD"
      value-format="YYYY-MM-DD"
    />
  </el-form-item>

  <el-form-item>
    <el-button type="primary" @click="submitForm">立即创建</el-button>
    <el-button @click="resetForm">重置</el-button>
  </el-form-item>
</el-form>
```

### 上传组件

```vue
<el-upload
  action="/api/v1/import-tasks/"
  :headers="uploadHeaders"
  :on-success="handleSuccess"
  :on-error="handleError"
  :before-upload="beforeUpload"
>
  <el-button type="primary">点击上传</el-button>
  <template #tip>
    <div class="el-upload__tip">
      只能上传 xlsx/xls 文件，且不超过 10MB
    </div>
  </template>
</el-upload>
```

## 🔧 故障排除

### 问题1: 样式未生效

确保在 `main.ts` 中引入了样式：

```typescript
import 'element-plus/dist/index.css'
```

### 问题2: 图标不显示

确保注册了图标组件：

```typescript
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
```

### 问题3: TypeScript类型错误

安装类型定义：

```bash
pnpm install -D @element-plus/icons-vue
```

## 📖 参考资源

- [Element Plus 官方文档](https://element-plus.org/)
- [Element Plus GitHub](https://github.com/element-plus/element-plus)
- [Vue 3 文档](https://vuejs.org/)

## ✅ 验证安装

运行以下命令验证安装：

```bash
cd frontend
pnpm dev
```

然后在浏览器中打开 http://localhost:5173，检查页面是否正常显示Element Plus组件。

---

**安装完成后即可使用 `src/pages/DistrictExamAdmin/ExamManagement.vue` 示例页面**

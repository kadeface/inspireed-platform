# AntV X6 配置指南

## 🎛️ 环境变量配置

在 `frontend/.env` 或 `frontend/.env.local` 中添加以下配置：

```env
# 启用 AntV X6 编辑器（替代 Vue Flow）
VITE_USE_X6_EDITOR=false

# 启用思维导图功能（需要 X6 编辑器）
VITE_USE_MINDMAP=false

# 启用自动保存
VITE_USE_AUTO_SAVE=true
```

## 🚀 快速启用

### 开发环境

在 `frontend/.env.local` (如果不存在则创建) 中添加：

```env
VITE_USE_X6_EDITOR=true
VITE_USE_MINDMAP=true
```

然后重启开发服务器：

```bash
cd frontend
npm run dev
```

### 浏览器控制台

无需重启，直接在浏览器控制台执行：

```javascript
// 启用 X6 编辑器
localStorage.setItem('feature-flags', JSON.stringify({
  'use-x6-editor': true,
  'use-mindmap': true
}))

// 刷新页面
location.reload()
```

## 📋 配置优先级

特性开关的配置优先级：

1. **浏览器 localStorage** (最高优先级)
2. **环境变量** (.env.local)
3. **默认配置** (代码中)

这意味着用户可以通过浏览器控制台覆盖环境变量的配置。

## 🔍 验证配置

### 方法 1：浏览器控制台

```javascript
// 查看当前配置
JSON.parse(localStorage.getItem('feature-flags') || '{}')
```

### 方法 2：Vue DevTools

在 Vue DevTools 中查看 `useFeatureFlag` composable 的状态。

## 🌍 不同环境的推荐配置

### 开发环境 (Development)

```env
# .env.development
VITE_USE_X6_EDITOR=true
VITE_USE_MINDMAP=true
VITE_DEBUG_MODE=true
```

### 测试环境 (Staging)

```env
# .env.staging
VITE_USE_X6_EDITOR=false  # 默认关闭，需要手动开启
VITE_USE_MINDMAP=false
```

### 生产环境 (Production)

```env
# .env.production
VITE_USE_X6_EDITOR=false  # 灰度期间默认关闭
VITE_USE_MINDMAP=false
```

## 💻 代码中使用

### 检查特性是否启用

```typescript
import { useFeatureFlag } from '@/composables/useFeatureFlag'

const { isEnabled } = useFeatureFlag()

if (isEnabled('use-x6-editor')) {
  console.log('X6 编辑器已启用')
}
```

### 动态启用/禁用

```typescript
import { useFeatureFlag } from '@/composables/useFeatureFlag'

const { enable, disable, toggle } = useFeatureFlag()

// 启用
enable('use-x6-editor')

// 禁用
disable('use-x6-editor')

// 切换
toggle('use-x6-editor')
```

### 获取所有特性状态

```typescript
import { useFeatureFlag } from '@/composables/useFeatureFlag'

const { allFlags } = useFeatureFlag()

console.log(allFlags.value)
// { 'use-x6-editor': true, 'use-mindmap': false, ... }
```

## 🔐 安全注意事项

1. **不要在生产环境默认启用未测试的特性**
2. **使用灰度发布策略逐步推广**
3. **始终保留回滚机制**
4. **监控错误率和性能指标**

## 📊 A/B 测试配置

如果需要进行 A/B 测试：

```typescript
// 根据用户 ID 决定是否启用
const userId = getCurrentUserId()
const shouldEnableX6 = userId % 2 === 0 // 50% 用户

if (shouldEnableX6) {
  enable('use-x6-editor')
}
```

## 🔄 配置更新策略

### 无缝更新（推荐）

用户无感知的配置更新：

1. 通过后端 API 控制特性开关
2. 前端定期轮询配置
3. 自动应用新配置

### 强制更新

需要用户刷新页面：

1. 修改环境变量
2. 重新部署
3. 用户刷新页面后生效

## 📝 配置日志

建议添加配置变更日志：

```typescript
// 监听配置变更
watch(() => allFlags.value, (newFlags, oldFlags) => {
  console.log('Feature flags changed:', {
    before: oldFlags,
    after: newFlags,
    timestamp: new Date().toISOString()
  })
}, { deep: true })
```

## 🆘 故障排查

### 问题：配置不生效

**解决方案**：

1. 检查浏览器控制台是否有错误
2. 清除 localStorage: `localStorage.clear()`
3. 检查环境变量是否正确
4. 重启开发服务器

### 问题：配置冲突

**解决方案**：

```javascript
// 重置为默认配置
localStorage.removeItem('feature-flags')
location.reload()
```

### 问题：部分用户无法启用

**解决方案**：

检查浏览器兼容性：

```javascript
// 检查 localStorage 可用性
try {
  localStorage.setItem('test', 'test')
  localStorage.removeItem('test')
  console.log('localStorage 可用')
} catch (e) {
  console.error('localStorage 不可用', e)
}
```

---

**最后更新**: 2025-11-18


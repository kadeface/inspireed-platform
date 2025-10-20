# 组件使用参考手册

## 📦 资源相关组件

### PDFResourceItem

**路径：** `frontend/src/components/Resource/PDFResourceItem.vue`

#### Props
```typescript
{
  resource: Resource  // 资源对象
}
```

#### Events
```typescript
{
  preview: (resourceId: number) => void       // 预览PDF
  createLesson: (resourceId: number) => void  // 创建教案
}
```

#### 使用示例
```vue
<PDFResourceItem
  :resource="resource"
  @preview="openPDFViewer"
  @create-lesson="openCreateModal"
/>
```

---

### PDFViewerModal

**路径：** `frontend/src/components/Resource/PDFViewerModal.vue`

#### Props
```typescript
{
  modelValue: boolean           // v-model 控制显示/隐藏
  resourceId: number | null     // 资源ID
}
```

#### Events
```typescript
{
  'update:modelValue': (value: boolean) => void
  'create-lesson': (resourceId: number) => void
}
```

#### 使用示例
```vue
<PDFViewerModal
  v-model="showModal"
  :resource-id="selectedResourceId"
  @create-lesson="handleCreateLesson"
/>
```

---

### CreateLessonFromResourceModal

**路径：** `frontend/src/components/Resource/CreateLessonFromResourceModal.vue`

#### Props
```typescript
{
  modelValue: boolean           // v-model 控制显示/隐藏
  resourceId: number | null     // 资源ID
}
```

#### Events
```typescript
{
  'update:modelValue': (value: boolean) => void
  'success': (lessonId: number) => void
}
```

#### 使用示例
```vue
<CreateLessonFromResourceModal
  v-model="showModal"
  :resource-id="resourceId"
  @success="handleSuccess"
/>
```

---

### ReferenceResourcePanel

**路径：** `frontend/src/components/Resource/ReferenceResourcePanel.vue`

#### Props
```typescript
{
  lessonId: number       // 教案ID
  resource: Resource     // 参考资源对象
  notes?: string         // 参考笔记
}
```

#### Events
```typescript
{
  close: () => void
  'view-pdf': (resourceId: number) => void
  'notes-updated': (notes: string) => void
}
```

#### 使用示例
```vue
<ReferenceResourcePanel
  :lesson-id="lessonId"
  :resource="referenceResource"
  :notes="lesson.reference_notes"
  @close="showPanel = false"
  @view-pdf="openPDFViewer"
  @notes-updated="handleNotesUpdated"
/>
```

---

### ResourceStatistics

**路径：** `frontend/src/components/Resource/ResourceStatistics.vue`

#### Props
```typescript
{
  resource: Resource     // 资源对象
  lessonsCount?: number  // 关联教案数量
}
```

#### 使用示例
```vue
<ResourceStatistics
  :resource="resource"
  :lessons-count="10"
/>
```

---

### CurriculumWithResources

**路径：** `frontend/src/components/Curriculum/CurriculumWithResources.vue`

#### Events
```typescript
{
  'lesson-created': (lessonId: number) => void
}
```

#### 使用示例
```vue
<CurriculumWithResources
  @lesson-created="refreshLessons"
/>
```

---

### UploadResourceModal

**路径：** `frontend/src/components/Admin/UploadResourceModal.vue`

#### Props
```typescript
{
  modelValue: boolean  // v-model 控制显示/隐藏
}
```

#### Events
```typescript
{
  'update:modelValue': (value: boolean) => void
  'success': (resourceId: number) => void
}
```

#### 使用示例
```vue
<UploadResourceModal
  v-model="showModal"
  @success="handleUploadSuccess"
/>
```

---

## 🔧 服务层 API

### resourceService

**路径：** `frontend/src/services/resource.ts`

```typescript
// 获取章节资源列表
await resourceService.getChapterResources(chapterId, {
  resource_type: 'pdf',
  page: 1,
  page_size: 20
})

// 获取资源详情
await resourceService.getResource(resourceId)

// 创建资源（管理员）
await resourceService.createResource(data, file)

// 更新资源
await resourceService.updateResource(resourceId, data)

// 删除资源
await resourceService.deleteResource(resourceId)

// 下载资源
await resourceService.downloadResource(resourceId)
```

### chapterService

**路径：** `frontend/src/services/resource.ts`

```typescript
// 获取课程章节（树形）
await chapterService.getCourseChapters(courseId, true)

// 获取章节详情
await chapterService.getChapter(chapterId)

// 创建章节（管理员）
await chapterService.createChapter(data)

// 更新章节
await chapterService.updateChapter(chapterId, data)

// 删除章节
await chapterService.deleteChapter(chapterId)
```

### lessonService (扩展)

**路径：** `frontend/src/services/lesson.ts`

```typescript
// 基于资源创建教案
await lessonService.createFromResource({
  reference_resource_id: resourceId,
  title: '教案标题',
  description: '描述',
  reference_notes: '参考笔记',
  tags: ['标签1', '标签2'],
  estimated_duration: 45
})

// 获取参考资源
await lessonService.getReferenceResource(lessonId)

// 更新参考笔记
await lessonService.updateReferenceNotes(lessonId, notes)
```

---

## 🎨 样式说明

所有组件使用 Scoped CSS，配色方案：

- **主色：** 蓝色系（#3b82f6）
- **成功：** 绿色系（#16a34a）
- **警告：** 橙色系（#d97706）
- **错误：** 红色系（#ef4444）
- **中性：** 灰色系（#6b7280）

---

## 📖 相关文档

- [MVP 设计方案](./MVP_LESSON_FROM_PDF.md)
- [测试指南](./MVP_TESTING_GUIDE.md)
- [最终总结](./MVP_FINAL_SUMMARY.md)

---

**版本：** v1.0.0  
**最后更新：** 2025-10-17


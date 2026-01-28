# 维护文档索引

本目录包含系统维护、迁移、修复相关的文档。

## 📋 文档分类

### 迁移相关

- **[MIGRATION_SUMMARY.md](./MIGRATION_SUMMARY.md)** - 数据库迁移总结
- **[MIGRATION_EXECUTION_GUIDE.md](./MIGRATION_EXECUTION_GUIDE.md)** - 迁移执行指南
- **[MIGRATION_CLEANUP_PLAN.md](./MIGRATION_CLEANUP_PLAN.md)** - 迁移清理计划
- **[X6_MIGRATION_CHECKLIST.md](./X6_MIGRATION_CHECKLIST.md)** - X6 迁移检查清单

### 功能回滚

- **[CURRICULUM_MANAGEMENT_REVERT.md](./CURRICULUM_MANAGEMENT_REVERT.md)** - 课程管理功能回滚说明

### 系统更新

- **[DASHBOARD_UPDATE_SUMMARY.md](./DASHBOARD_UPDATE_SUMMARY.md)** - 仪表盘更新总结

### 问题修复

#### 核心功能修复

- **[LESSON_SYNC_FIX.md](./LESSON_SYNC_FIX.md)** - 教案同步问题修复
- **[SESSION_END_FIX.md](./SESSION_END_FIX.md)** - 课堂结束功能修复
- **[ACTIVITY_DISPLAY_FIX.md](./ACTIVITY_DISPLAY_FIX.md)** - 活动显示问题修复
- **[ACTIVITY_CLICK_SHOW_STATISTICS_FIX.md](./ACTIVITY_CLICK_SHOW_STATISTICS_FIX.md)** - 活动点击统计修复

#### 权限和配置修复

- **[QUESTION_PERMISSION_FIX.md](./QUESTION_PERMISSION_FIX.md)** - 问题权限修复
- **[TOKEN_KEY_FIX_SUMMARY.md](./TOKEN_KEY_FIX_SUMMARY.md)** - Token 密钥修复总结
- **[CORS_ENUM_FIX_SUMMARY.md](./CORS_ENUM_FIX_SUMMARY.md)** - CORS 枚举修复总结
- **[CELL_TYPE_ENUM_FIX.md](./CELL_TYPE_ENUM_FIX.md)** - Cell 类型枚举修复

#### UI 和导航修复

- **[NAVIGATION_MULTIPLE_ROWS_FIX.md](./NAVIGATION_MULTIPLE_ROWS_FIX.md)** - 导航多行显示修复
- **[CHECKBOX_HIDE_CELL_FEATURE.md](./CHECKBOX_HIDE_CELL_FEATURE.md)** - 复选框隐藏 Cell 功能

#### 考试相关修复

- **[exam-room-fix-summary.md](./exam-room-fix-summary.md)** - 考场修复总结
- **[exam-number-system-usage.md](./exam-number-system-usage.md)** - 考试编号系统使用说明

### 数据导入

#### 学生导入

- **[student-import-implementation-summary.md](./student-import-implementation-summary.md)** - 学生导入实现总结
- **[student-import-quickref.md](./student-import-quickref.md)** - 学生导入快速参考
- **[student-import-template-update-summary.md](./student-import-template-update-summary.md)** - 学生导入模板更新总结
- **[student-import-template-with-school-code.md](./student-import-template-with-school-code.md)** - 带学校代码的学生导入模板
- **[student-account-import-guide.md](./student-account-import-guide.md)** - 学生账号导入指南

#### 模板下载

- **[template-download-guide.md](./template-download-guide.md)** - 模板下载指南
- **[template-download-implementation.md](./template-download-implementation.md)** - 模板下载实现

### 合并策略

- **[MERGE_STRATEGY.md](./MERGE_STRATEGY.md)** - 代码合并策略

### 快速修复总结

- **[QUICK_FIX_SUMMARY.md](./QUICK_FIX_SUMMARY.md)** - 快速修复总结
- **[QUICK_FIX_COMPLETED.md](./QUICK_FIX_COMPLETED.md)** - 快速修复完成确认

### 中文文档

- **[完整修复总结.md](./完整修复总结.md)** - 完整修复总结（中文）
- **[教案发布问题解决方案.md](./教案发布问题解决方案.md)** - 教案发布问题解决方案（中文）
- **[频繁401错误已修复.md](./频繁401错误已修复.md)** - 401 错误修复说明（中文）

### 计划和发现

- **[task_plan.md](./task_plan.md)** - 任务计划
- **[findings.md](./findings.md)** - 发现和问题记录

## 🔍 快速查找

### 按问题类型查找

- **数据库迁移问题** → 查看 [迁移相关](#迁移相关)
- **功能回滚** → 查看 [功能回滚](#功能回滚)
- **权限问题** → 查看 [权限和配置修复](#权限和配置修复)
- **数据导入问题** → 查看 [数据导入](#数据导入)
- **UI 显示问题** → 查看 [UI 和导航修复](#ui-和导航修复)

### 按功能模块查找

- **教案相关** → `LESSON_SYNC_FIX.md`, `教案发布问题解决方案.md`
- **课堂相关** → `SESSION_END_FIX.md`
- **活动相关** → `ACTIVITY_DISPLAY_FIX.md`, `ACTIVITY_CLICK_SHOW_STATISTICS_FIX.md`
- **考试相关** → `exam-room-fix-summary.md`, `exam-number-system-usage.md`
- **学生导入** → `student-import-*.md`

## 📝 文档维护规范

1. **新增修复文档**：在修复完成后，创建对应的修复文档
2. **命名规范**：使用 `功能名_FIX.md` 或 `功能名-修复说明.md` 格式
3. **文档内容**：应包含问题描述、原因分析、解决方案、验证步骤
4. **更新索引**：新增文档后，更新本 README.md

## 🔗 相关文档

- [部署文档](../deployment/README.md) - 部署和维护相关
- [设计文档](../design/) - 系统设计文档
- [功能文档](../features/) - 功能使用文档

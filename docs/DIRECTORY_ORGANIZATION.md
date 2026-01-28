# 目录结构整理总结

**整理时间**: 2025-01-28  
**整理范围**: 根目录文档和备份文件

## 📋 整理内容

### 1. 根目录文档整理

将根目录的总结类文档移动到 `docs/` 下的相应子目录：

#### 迁移到 `docs/maintenance/`
- `CURRICULUM_MANAGEMENT_REVERT.md` - 课程管理功能回滚说明
- `DASHBOARD_UPDATE_SUMMARY.md` - 仪表盘更新总结
- `MIGRATION_EXECUTION_GUIDE.md` - 迁移执行指南
- `MIGRATION_SUMMARY.md` - 数据库迁移总结

#### 迁移到 `docs/config/`
- `EXAM_SUBJECT_CONFIG_SUMMARY.md` - 考试科目配置总结

#### 迁移到 `docs/progress/`
- `PROGRESS_SUMMARY.md` - 项目进度总结
- `REFACTORING_SUMMARY.md` - 重构总结

### 2. 备份文件整理

创建了统一的备份目录结构：

```
backups/
├── backend/
│   └── .env.prod.backup-before-security-fix
└── docker/
    ├── docker-compose.prod.yml.backup-20260126_221210
    ├── docker-compose.prod.yml.backup-final
    └── docker-compose.prod.yml.bak
```

### 3. 导出文件整理

- `exported_exam_numbers.xlsx` → `docs/exam/exported_exam_numbers.xlsx`

### 4. 索引文档创建

为新增的文档目录创建了索引：

- `docs/config/README.md` - 配置文档索引
- `docs/progress/README.md` - 项目进度文档索引
- `docs/maintenance/README.md` - 已存在，包含完整的维护文档索引

## 📁 整理后的目录结构

### 根目录（清理后）

根目录现在只保留：
- `README.md` - 项目主文档
- 核心代码目录：`backend/`, `frontend/`, `docker/`, `scripts/`, `tests/`
- 资源目录：`assets/`, `templates/`, `logs/`
- 文档目录：`docs/`
- 配置文件：`package.json`, `pnpm-*.yaml`, `pyrightconfig.json`
- 启动脚本：`start.sh`, `stop.sh`, `restart.sh`

### docs/ 目录结构

```
docs/
├── config/              # 配置相关文档（新增）
│   ├── README.md
│   └── EXAM_SUBJECT_CONFIG_SUMMARY.md
├── maintenance/         # 维护相关文档
│   ├── README.md        # 完整的维护文档索引
│   ├── CURRICULUM_MANAGEMENT_REVERT.md
│   ├── DASHBOARD_UPDATE_SUMMARY.md
│   ├── MIGRATION_EXECUTION_GUIDE.md
│   ├── MIGRATION_SUMMARY.md
│   └── ... (其他维护文档)
├── progress/            # 项目进度文档（新增）
│   ├── README.md
│   ├── PROGRESS_SUMMARY.md
│   └── REFACTORING_SUMMARY.md
├── deployment/          # 部署相关文档
├── design/             # 设计文档
├── features/            # 功能文档
└── ... (其他文档目录)
```

### backups/ 目录结构

```
backups/
├── backend/            # 后端备份文件
└── docker/            # Docker 配置备份文件
```

## ✅ 整理效果

### 整理前
- 根目录有 7+ 个总结类文档散落
- 备份文件分散在多个目录
- 导出文件在根目录

### 整理后
- ✅ 根目录只保留核心文件和 `README.md`
- ✅ 所有文档按主题分类到 `docs/` 子目录
- ✅ 备份文件统一管理在 `backups/` 目录
- ✅ 每个文档目录都有索引 README
- ✅ `.gitignore` 已更新，忽略 `backups/` 目录

## 🔍 查找文档

### 按主题查找

- **迁移相关** → `docs/maintenance/MIGRATION_*.md`
- **配置相关** → `docs/config/`
- **项目进度** → `docs/progress/`
- **部署相关** → `docs/deployment/`
- **设计文档** → `docs/design/`

### 按功能查找

- **考试配置** → `docs/config/EXAM_SUBJECT_CONFIG_SUMMARY.md`
- **课程管理** → `docs/maintenance/CURRICULUM_MANAGEMENT_REVERT.md`
- **仪表盘** → `docs/maintenance/DASHBOARD_UPDATE_SUMMARY.md`

## 📝 维护规范

### 新增文档时

1. **总结类文档** → 根据主题放入 `docs/maintenance/`, `docs/config/`, `docs/progress/` 等
2. **备份文件** → 放入 `backups/` 对应子目录
3. **导出文件** → 放入 `docs/` 相应主题目录
4. **更新索引** → 更新对应目录的 `README.md`

### 命名规范

- 维护文档：`功能名_SUMMARY.md` 或 `功能名_REVERT.md`
- 配置文档：`配置项_CONFIG_SUMMARY.md`
- 进度文档：`项目名_PROGRESS.md` 或 `项目名_SUMMARY.md`

## 🔗 相关文档

- [部署文档索引](./deployment/README.md)
- [维护文档索引](./maintenance/README.md)
- [配置文档索引](./config/README.md)
- [进度文档索引](./progress/README.md)

# Alembic 迁移顺序检查报告

## 检查结果

✅ **迁移顺序检查通过！**

### 检查项

1. ✅ **断链检查**：没有发现断链（所有 down_revision 都指向存在的 revision）
2. ✅ **根节点检查**：找到 1 个根节点（`001`）
3. ✅ **循环依赖检查**：没有发现循环依赖
4. ⚠️ **孤立迁移**：发现 1 个孤立的迁移（`4eac54cf4de2`），这是正常的，因为它是合并迁移，是依赖链的终点

## 迁移依赖链

从根节点 `001` 开始的完整依赖链：

```
001 (001_add_curriculum_system.py)
└─ 002 (002_add_chapters_resources_mvp.py)
   └─ 2f1d0b37129d (20251020_2236_2f1d0b37129d_add_chapter_id_to_lessons.py)
      └─ 003_add_organization (003_add_organization_tables.py)
         └─ 004 (004_add_student_enhancement_features.py)
            └─ 005_add_qa_system (005_add_qa_system.py)
               └─ 006_learning_science (006_add_learning_science_fields.py)
                  └─ 007_fix_lesson_enum (007_fix_lesson_enum_values.py)
                     └─ 008_add_activity_system (008_add_activity_system.py)
                        └─ 009_add_subject_groups (009_add_subject_groups.py)
                           └─ f920685b3054 (20251107_0912_f920685b3054_add_grade_id_to_subject_groups.py)
                              └─ 088e21d1e159 (20251108_1358_088e21d1e159_add_classrooms_and_user_scope_fields.py)
                                 └─ 5a7c9d8b1f23 (20251109_1015_5a7c9d8b1f23_add_lesson_classroom_assignments.py)
                                    └─ b2e6f4321abc (20251109_1430_b2e6f4321abc_add_formative_assessment_tables.py)
                                       └─ c9e2f8a1d5ef (20251110_0900_c9e2f8a1d5ef_remove_course_subject_grade_unique.py)
                                          ├─ 016_add_classroom_session (016_add_classroom_session_tables.py)
                                          │  └─ 017 (017_add_library_assets_and_resource_asset_id.py)
                                          │     └─ 018 (018_add_subject_id_to_library_assets.py)
                                          │        └─ 97119fda8aae (20251213_0309_97119fda8aae_merge_018_and_merge_subjects_cell_uuid.py)
                                          │           └─ add_grade_id_library_assets (20251214_0826_add_grade_id_to_library_assets.py)
                                          │              └─ add_knowledge_point_fields (20251215_add_knowledge_point_fields_to_library_assets.py)
                                          │                 └─ add_view_count_library_assets (20251216_add_view_count_to_library_assets.py)
                                          │                    └─ add_library_asset_versions (20251219_add_library_asset_versions.py)
                                          │                       └─ add_classroom_assistant_tables (20251220_add_classroom_assistant_tables.py)
                                          │                          └─ add_last_login_to_users (20251221_add_last_login_to_users.py)
                                          │                             └─ add_student_id_number_to_users (20251221_1723_add_student_id_number_to_users.py)
                                          │                                ├─ 20250122_add_student_projects (20250122_add_student_projects.py)
                                          │                                │  └─ 4eac54cf4de2 (20251225_2219_4eac54cf4de2_merge_student_projects_and_session_id_.py)
                                          │                                └─ session_id_formative (20251222_add_session_id_to_formative_assessments.py)
                                          │                                   └─ 4eac54cf4de2 (20251225_2219_4eac54cf4de2_merge_student_projects_and_session_id_.py)
                                          └─ 2e224926b436 (20251117_0205_2e224926b436_fix_celltype_enum_add_activity_flowchart.py)
                                             └─ 57a9a465710d (20251117_0427_57a9a465710d_merge_classroom_session_and_celltype_fix.py)
                                                └─ a1b2c3d4e5f6 (20251127_1535_add_browser_celltype.py)
                                                   ├─ add_cell_uuid_to_submissions (20250101_add_cell_uuid_to_submissions.py)
                                                   │  └─ merge_subjects_cell_uuid (20250102_merge_subjects_and_cell_uuid.py)
                                                   │     └─ 97119fda8aae (20251213_0309_97119fda8aae_merge_018_and_merge_subjects_cell_uuid.py)
                                                   └─ f7e8d9c0b1a2 (20250102_add_new_subjects.py)
                                                      └─ merge_subjects_cell_uuid (20250102_merge_subjects_and_cell_uuid.py)
                                                         └─ 97119fda8aae (20251213_0309_97119fda8aae_merge_018_and_merge_subjects_cell_uuid.py)
```

## 如何检查迁移顺序问题

### 1. 运行检查脚本

```bash
cd backend
python3 check_alembic_migration_order.py
```

### 2. 检查 Alembic 历史记录

```bash
# 在 Docker 容器中
docker exec inspireed-backend alembic history

# 或直接运行
cd backend
alembic history
```

### 3. 检查当前数据库版本

```bash
docker exec inspireed-backend alembic current
```

### 4. 查看迁移状态

```bash
docker exec inspireed-backend alembic heads
```

## 常见问题

### 问题 1: "Multiple heads detected"

**原因**：存在多个迁移分支没有合并

**解决方法**：
1. 运行 `alembic heads` 查看所有 head
2. 创建合并迁移：`alembic merge -m "merge_branches" heads`
3. 运行 `alembic upgrade head`

### 问题 2: "Can't locate revision identified by 'xxx'"

**原因**：down_revision 指向不存在的 revision

**解决方法**：
1. 运行检查脚本找出断链
2. 修复迁移文件中的 down_revision
3. 重新运行迁移

### 问题 3: "Target database is not up to date"

**原因**：数据库版本落后于代码中的迁移

**解决方法**：
```bash
docker exec inspireed-backend alembic upgrade head
```

## 修复迁移顺序的步骤

如果检查脚本发现了问题，按以下步骤修复：

1. **修复断链**：
   - 找到断链的迁移文件
   - 检查正确的 down_revision 应该是什么
   - 更新迁移文件中的 down_revision

2. **合并多个根节点**：
   - 如果存在多个根节点，需要创建一个合并迁移
   - 或者将其中一个的 down_revision 指向另一个

3. **修复循环依赖**：
   - 检查循环依赖的迁移文件
   - 调整 down_revision 以打破循环

## 预防措施

1. **创建新迁移时**：
   - 使用 `alembic revision --autogenerate -m "description"` 自动生成
   - 或者使用 `alembic revision -m "description"` 然后手动编写

2. **合并分支时**：
   - 使用 `alembic merge` 命令创建合并迁移
   - 不要手动创建合并迁移

3. **定期检查**：
   - 运行检查脚本确保迁移顺序正确
   - 在 CI/CD 流程中加入迁移检查

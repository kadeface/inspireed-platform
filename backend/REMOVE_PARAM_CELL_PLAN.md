# PARAM Cell 移除方案

## 📊 影响评估报告

**检查时间:** 2025-02-06
**数据库:** inspireed
**检查结果:** ✅ 可以安全移除

### 检查结果摘要

| 项目 | 结果 |
|------|------|
| PARAM 枚举值 | ✅ 存在于数据库定义中 |
| PARAM Cell 记录 | ✅ 0 个（无实际使用） |
| Cell 总数 | 14 个 |
| 影响范围 | 无 |

### 当前 Cell 类型分布

```
ACTIVITY   ████████████████████████████████████████████ 9 个 (64.29%)
CODE       ████████████ 3 个 (21.43%)
VIDEO       ███ 1 个 (7.14%)
TEXT        ███ 1 个 (7.14%)
PARAM       0 个 (0.00%) ⚠️
```

---

## 🎯 移除方案

由于数据库中**没有PARAM类型的cell记录**，可以直接移除，无需数据迁移。

### 需要修改的文件清单

#### 后端修改（2个文件）

1. **backend/app/models/cell.py**
   - 从 `CellType` 枚举中删除：`PARAM = "PARAM"`
   - 删除注释：`# PARAM = "PARAM"  # 参数设置单元`

#### 前端修改（4个文件）

2. **frontend/src/types/cell.ts**
   - 从 `CellType` 对象中删除：`PARAM: 'param'`
   - 删除接口定义：
     ```typescript
     export interface ParamCellContent {
       schema: any
       values: Record<string, any>
     }
     export interface ParamCell extends CellBase {
       type: typeof CellType.PARAM
       content: ParamCellContent
     }
     ```
   - 从 `Cell` 联合类型中删除 `| ParamCell`

3. **frontend/src/composables/useLessonEditorCells.ts**
   - 删除 case 分支：
     ```typescript
     case CellType.PARAM:
       return { ...baseCell, type: CellType.PARAM, content: { schema: {}, values: {} } } as Cell
     ```

4. **frontend/src/utils/lessonEditorHelpers.ts**
   - 从类型映射中删除：`[CellType.PARAM]: '参数单元'`
   - 从短名称映射中删除：`[CellType.PARAM]: '参数'`

5. **frontend/src/utils/cellId.ts**（如果包含PARAM相关代码）
   - 检查并清理相关代码

---

## 🔧 具体实施步骤

### 步骤1：创建数据库迁移（可选，但推荐）

虽然当前没有PARAM cell，但为了清理枚举值，建议创建迁移：

```bash
cd backend
alembic revision -m "remove_param_cell_type"
```

在生成的迁移文件中添加：

```python
def upgrade():
    # 从枚举类型中移除 PARAM 值
    op.execute("ALTER TABLE cells ALTER COLUMN cell_type DROP DEFAULT")
    op.execute("ALTER TYPE celltype RENAME TO celltype_old")
    op.execute("CREATE TYPE celltype AS ENUM ('ACTIVITY', 'CHART', 'CODE', 'CONTEST', 'FLOWCHART', 'SIM', 'TEXT', 'VIDEO')")
    op.execute("ALTER TABLE cells ALTER COLUMN cell_type TYPE celltype USING cell_type::text::celltype")
    op.execute("DROP TYPE celltype_old")
    op.execute("ALTER TABLE cells ALTER COLUMN cell_type SET DEFAULT 'TEXT'")

def downgrade():
    # 恢复 PARAM 值
    op.execute("ALTER TABLE cells ALTER COLUMN cell_type DROP DEFAULT")
    op.execute("ALTER TYPE celltype RENAME TO celltype_old")
    op.execute("CREATE TYPE celltype AS ENUM ('ACTIVITY', 'CHART', 'CODE', 'CONTEST', 'FLOWCHART', 'PARAM', 'SIM', 'TEXT', 'VIDEO')")
    op.execute("ALTER TABLE cells ALTER COLUMN cell_type TYPE celltype USING cell_type::text::celltype")
    op.execute("DROP TYPE celltype_old")
    op.execute("ALTER TABLE cells ALTER COLUMN cell_type SET DEFAULT 'TEXT'")
```

### 步骤2：修改后端代码

```bash
# 编辑 backend/app/models/cell.py
# 删除 PARAM = "PARAM" 枚举值
```

### 步骤3：修改前端代码

```bash
# 按照上面的文件清单逐个修改
```

### 步骤4：测试验证

1. **启动后端**
   ```bash
   cd backend
   python3 -m app.main
   ```

2. **启动前端**
   ```bash
   cd frontend
   npm run dev
   ```

3. **测试教案编辑器**
   - 创建新教案
   - 尝试添加各种类型的cell
   - 确认PARAM选项不存在
   - 确认其他类型正常工作

4. **检查已有教案**
   - 打开现有教案
   - 确认所有cell正常显示
   - 确认编辑和保存功能正常

### 步骤5：提交代码

```bash
git add .
git commit -m "refactor: remove unused PARAM cell type

- Remove PARAM from CellType enum in backend
- Remove ParamCell type definitions in frontend
- Remove PARAM cell creation functions
- Clean up related utility mappings

No PARAM cells exist in database, safe to remove.

Checked with: backend/check_param_cell_usage.py"
```

---

## ⚠️ 注意事项

1. **数据库迁移前备份**
   ```bash
   pg_dump inspireed > backup_before_param_removal.sql
   ```

2. **枚举值顺序**
   - PostgreSQL枚举值的顺序很重要
   - 确保迁移脚本中枚举值的顺序与数据库一致

3. **现有枚举值**
   当前数据库中的枚举值（包含重复）：
   - `ACTIVITY, CHART, CODE, CONTEST, FLOWCHART, PARAM, QA, SIM, TEXT, VIDEO, activity, browser, flowchart`
   - 注意：有大小写重复的值，可能需要同时清理

4. **建议顺便清理**
   - `QA`（已在前端注释移除）
   - 大小写重复的枚举值（activity/ACTIVITY等）

---

## ✅ 验证清单

执行移除后，确认以下项目：

- [ ] 后端启动无错误
- [ ] 前端启动无错误
- [ ] 数据库迁移成功执行
- [ ] 教案编辑器中无PARAM选项
- [ ] 其他cell类型正常工作
- [ ] 现有教案正常加载
- [ ] TypeScript编译无错误
- [ ] 所有测试通过

---

## 📞 回滚方案

如果发现问题需要回滚：

1. **恢复数据库**
   ```bash
   psql inspireed < backup_before_param_removal.sql
   ```

2. **恢复代码**
   ```bash
   git revert HEAD
   ```

3. **回滚迁移**
   ```bash
   alembic downgrade -1
   ```

---

## 📚 相关文件

- 检查脚本：`backend/check_param_cell_usage.py`
- 后端模型：`backend/app/models/cell.py`
- 前端类型：`frontend/src/types/cell.ts`
- 创建函数：`frontend/src/composables/useLessonEditorCells.ts`
- 工具函数：`frontend/src/utils/lessonEditorHelpers.ts`

---

**状态:** ✅ 可以安全执行
**预计耗时:** 30-60 分钟
**风险等级:** 🟢 低风险（无实际数据影响）

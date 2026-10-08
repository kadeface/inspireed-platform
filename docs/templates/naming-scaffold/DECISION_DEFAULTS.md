# 命名决策表（禁止自由发挥）

新表、新接口、新枚举时**只查本表**，不要发明第二套同义词。

| 场景 | 唯一默认 | 禁止 / 避免 |
|------|----------|-------------|
| 创建人（FK → users） | `created_by` | `creator_id`、`author_id`、`owner_id`（所有者语义另用 `owner_user_id`） |
| 更新人 | `updated_by` | `updated_by_user_id`（新项目不要混用） |
| 布尔开关 | `is_active`、`has_*`、`*_enabled` | 无前缀的 `active`、`editable`、`synced`（除非领域词极强且团队书面批准） |
| 时刻 | `created_at`、`updated_at`、`ended_at` | `createTime`、`*_time` 表示时刻 |
| 日期（无时分） | `*_date`（如 `exam_date`） | 与 `*_at` 混用同一语义 |
| 枚举存库值 | 小写 `snake_case`：`in_progress` | `IN_PROGRESS`、`InProgress`、`in-progress` |
| PG 枚举类型名 | `snake_case`：`class_session_status` | `classsessionstatus`、`ClassSessionStatus` |
| 普通索引 | `ix_tablename_col` | `idx_`、无前缀、`unique_` 当索引名 |
| 唯一约束 | `uq_tablename_cols` | `unique_user_lesson_favorite` 这类自由句式（新项目） |
| JSON 列 | 语义名：`settings`、`content`、`payload` | 有的加 `_json` 有的不加——**新项目统一不加 `_json` 后缀** |
| 前端 DTO 字段 | 与 API 相同 `snake_case` | 为「JS 习惯」把 DTO 改成 camelCase |
| API 输出别名 | 不使用 | `serialization_alias="studentName"` |

## 样板字段（复制到新模型）

```python
id = Column(Integer, primary_key=True)
created_at = Column(DateTime, nullable=False)
updated_at = Column(DateTime, nullable=False)
created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
is_active = Column(Boolean, nullable=False, default=True)
```

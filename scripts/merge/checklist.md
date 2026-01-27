# 项目合并检查清单

使用此清单跟踪合并进度，确保不遗漏任何重要步骤。

## 📋 合并前准备

### Git 和备份
- [ ] 创建备份分支: `backup/before-merge-YYYYMMDD`
- [ ] 创建代码备份压缩包
- [ ] 创建合并分支: `feature/multi-app-merge`
- [ ] 提交所有未提交的更改
- [ ] 确认当前分支状态

### 环境准备
- [ ] 确认 Docker 环境正常
- [ ] 确认数据库可以连接
- [ ] 确认开发环境依赖已安装
- [ ] 创建必要的目录结构

### 文档审查
- [ ] 阅读完整合并计划: `docs/PROJECT_MERGE_PLAN.md`
- [ ] 阅读架构设计文档: `docs/MULTI_DATABASE_SHARING_DESIGN.md`
- [ ] 阅读实施示例: `docs/SCHEMA_ISOLATION_EXAMPLE.md`
- [ ] 理解 Schema 隔离方案

---

## 🔄 阶段二：重构目录结构

### 创建目录
- [ ] 创建 `apps/inspireed/` 目录
- [ ] 创建 `apps/app2/` 目录
- [ ] 创建 `shared/models/shared/` 目录
- [ ] 创建 `infrastructure/` 目录
- [ ] 创建 `docs/inspireed/` 和 `docs/app2/` 目录

### 移动 InspireEd 代码
- [ ] 移动 `backend/` → `apps/inspireed/backend/`
- [ ] 移动 `frontend/` → `apps/inspireed/frontend/`
- [ ] 备份 `docker/` → `infrastructure/docker/inspireed/`
- [ ] 移动相关文档到 `docs/inspireed/`

### 更新路径引用
- [ ] 更新 InspireEd 后端的导入路径
- [ ] 更新 InspireEd 前端的构建配置
- [ ] 更新启动脚本中的路径
- [ ] 更新 Dockerfile 中的路径
- [ ] 更新 CI/CD 配置中的路径
- [ ] 更新文档中的路径引用

### 验证移动
- [ ] 后端代码可以正常导入
- [ ] 前端代码可以正常构建
- [ ] 启动脚本可以正常运行
- [ ] 所有测试通过

---

## 🗄️ 阶段三：数据库 Schema 隔离

### 规划共享模型
- [ ] 确定哪些模型需要共享（User, Region, School, Classroom, Subject, Grade）
- [ ] 确定哪些模型属于 InspireEd（Lesson, Cell, Activity 等）
- [ ] 确定应用2需要哪些模型

### 创建共享模型
- [ ] 创建 `shared/models/shared/user.py` 并指定 `schema="shared"`
- [ ] 创建 `shared/models/shared/organization.py`
- [ ] 创建 `shared/models/shared/curriculum.py` (部分)
- [ ] 更新所有外键引用为完整路径 `ForeignKey("shared.users.id")`
- [ ] 创建 `shared/models/__init__.py` 导出所有共享模型

### 更新 InspireEd 模型
- [ ] 删除 InspireEd 中的共享模型（改为从 shared 导入）
- [ ] 更新所有 InspireEd 模型，指定 `schema="inspireed"`
- [ ] 更新所有外键引用，使用完整路径
- [ ] 更新模型导入语句
- [ ] 更新 `apps/inspireed/backend/app/models/__init__.py`

### 创建数据库迁移
- [ ] 创建 Alembic 迁移脚本
- [ ] 在迁移中创建 `shared` schema
- [ ] 在迁移中创建 `inspireed` schema
- [ ] 在迁移中创建 `app2` schema
- [ ] 移动共享表到 `shared` schema
- [ ] 移动 InspireEd 表到 `inspireed` schema
- [ ] 更新外键约束
- [ ] 创建回滚脚本（downgrade 函数）

### 测试数据库迁移
- [ ] 在开发环境执行迁移
- [ ] 验证 Schema 创建成功: `\dn`
- [ ] 验证表在正确 Schema: `SELECT schemaname, tablename FROM pg_tables`
- [ ] 验证外键约束正确
- [ ] 测试查询跨 Schema 的数据
- [ ] 测试回滚脚本
- [ ] 验证现有数据完整性

### 更新数据库配置
- [ ] 更新数据库连接字符串，添加搜索路径
- [ ] 更新 `apps/inspireed/backend/app/core/config.py`
- [ ] 更新 `.env` 文件
- [ ] 测试数据库连接

---

## 🔌 阶段四：整合应用2

### 应用2 代码准备
- [ ] 确认应用2的代码来源（Git 仓库、本地路径等）
- [ ] 决定导入方式（Submodule、Subtree、直接复制）
- [ ] 审查应用2的代码结构

### 导入应用2代码
- [ ] 导入/创建应用2后端代码到 `apps/app2/backend/`
- [ ] 导入/创建应用2前端代码到 `apps/app2/frontend/`
- [ ] 创建应用2的 README.md
- [ ] 创建应用2的配置文件

### 配置应用2使用共享模型
- [ ] 在应用2后端导入共享模型: `from shared.models.shared import User`
- [ ] 配置应用2的数据库连接（使用 `app2` schema）
- [ ] 创建应用2的模型，指定 `schema="app2"`
- [ ] 创建应用2模型的外键引用（指向 `shared.users.id` 等）
- [ ] 创建应用2的 Alembic 迁移

### 应用2 Schema 迁移
- [ ] 创建应用2的 Schema 迁移脚本
- [ ] 在迁移中创建 `app2` schema（如果尚未创建）
- [ ] 创建应用2的表
- [ ] 测试迁移脚本

### 验证应用2
- [ ] 应用2后端可以正常启动
- [ ] 应用2前端可以正常构建和运行
- [ ] 应用2可以访问共享数据（如用户信息）
- [ ] 应用2的业务数据在 `app2` schema 中

---

## 🏗️ 阶段五：统一基础设施

### Docker Compose 配置
- [ ] 创建根目录的 `docker-compose.yml`
- [ ] 配置共享服务（postgres, redis, minio）
- [ ] 配置 InspireEd 后端和前端服务
- [ ] 配置应用2后端和前端服务
- [ ] 设置正确的端口映射
- [ ] 配置服务依赖关系
- [ ] 配置健康检查

### 启动脚本
- [ ] 创建统一启动脚本 `scripts/start-all.sh`
- [ ] 创建统一停止脚本 `scripts/stop-all.sh`
- [ ] 更新现有的启动脚本
- [ ] 测试所有启动脚本

### 依赖管理
- [ ] 更新根 `package.json`（如果使用 workspace）
- [ ] 更新根 `pyproject.toml` 或 `requirements.txt`
- [ ] 统一共享依赖的版本
- [ ] 测试依赖安装

### CI/CD 配置
- [ ] 更新 GitHub Actions 或其他 CI 配置
- [ ] 配置 InspireEd 的测试和构建
- [ ] 配置应用2的测试和构建
- [ ] 配置共享代码的测试
- [ ] 测试 CI/CD 流程

---

## ✅ 阶段六：测试和验证

### 单元测试
- [ ] 测试共享模型的导入和使用
- [ ] 测试跨 Schema 查询
- [ ] 测试 InspireEd 的功能
- [ ] 测试应用2的功能
- [ ] 所有单元测试通过

### 集成测试
- [ ] 测试两个应用可以同时访问数据库
- [ ] 测试用户认证和授权（如果共享）
- [ ] 测试 API 接口
- [ ] 测试跨应用的数据一致性
- [ ] 所有集成测试通过

### 数据库测试
- [ ] 测试数据库迁移在生产环境
- [ ] 验证现有数据完整性
- [ ] 验证新数据可以正确创建
- [ ] 测试回滚脚本
- [ ] 测试数据备份和恢复

### 性能测试
- [ ] 测试跨 Schema JOIN 查询性能
- [ ] 测试两个应用同时运行时的性能
- [ ] 测试数据库连接池是否足够
- [ ] 监控内存和 CPU 使用

### 端到端测试
- [ ] 测试 InspireEd 的完整用户流程
- [ ] 测试应用2的完整用户流程
- [ ] 测试两个应用的交互（如果有）
- [ ] 在浏览器中手动测试关键功能

---

## 📚 阶段七：文档和部署

### 文档更新
- [ ] 更新主 README.md，说明多应用架构
- [ ] 创建 `apps/inspireed/README.md`
- [ ] 创建 `apps/app2/README.md`
- [ ] 创建 `shared/README.md`
- [ ] 更新开发指南
- [ ] 更新部署文档
- [ ] 更新 API 文档

### 部署准备
- [ ] 更新生产环境的 Docker Compose
- [ ] 准备 Kubernetes 配置（如果使用）
- [ ] 准备数据库备份策略
- [ ] 准备回滚计划
- [ ] 准备监控和日志配置

### 代码审查
- [ ] 代码审查：InspireEd 移动后的代码
- [ ] 代码审查：应用2的代码
- [ ] 代码审查：共享模型的代码
- [ ] 代码审查：基础设施配置

### 最终检查
- [ ] 所有测试通过
- [ ] 所有文档已更新
- [ ] CI/CD 配置正确
- [ ] 数据库迁移已验证
- [ ] 回滚计划已准备
- [ ] 团队已培训新结构

---

## 🚀 合并完成

### 合并到主分支
- [ ] 合并请求已创建
- [ ] 代码审查已通过
- [ ] 所有检查已通过
- [ ] 合并到主分支（main 或 dev）

### 部署到生产
- [ ] 数据库迁移在生产环境执行
- [ ] 应用部署成功
- [ ] 验证生产环境功能正常
- [ ] 监控生产环境指标

### 清理
- [ ] 删除合并分支
- [ ] 归档备份文件
- [ ] 更新项目标签/版本
- [ ] 通知团队成员

---

## 📝 备注

使用此检查清单时，建议：
1. 每完成一个任务，及时勾选
2. 遇到问题及时记录
3. 定期审查进度
4. 与团队同步进度

**当前进度**: ___% 完成

**最后更新**: $(date)

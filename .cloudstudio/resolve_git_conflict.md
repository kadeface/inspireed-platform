# Cloud Studio Git 冲突解决方案

## 问题
执行 `git pull origin dev` 时提示：
```
error: Your local changes to the following files would be overwritten by merge:
        .cloudstudio/preview.yaml
```

## 解决方案

**由于远程版本已经包含了最新的修复（我们刚推送的），最简单的方法是丢弃本地修改，直接使用远程版本：**

```bash
# 1. 丢弃本地对 preview.yaml 的修改（使用远程版本）
git checkout -- .cloudstudio/preview.yaml

# 2. 拉取远程更新
git pull origin dev
```

## 其他选项（如果需要保留本地修改）

### 选项2：暂存本地修改后拉取
```bash
# 暂存本地修改
git stash

# 拉取远程更新
git pull origin dev

# 如果需要应用本地修改（可能会产生冲突）
git stash pop
```

### 选项3：提交本地修改后拉取（可能会有冲突需要手动解决）
```bash
# 提交本地修改
git add .cloudstudio/preview.yaml
git commit -m "本地修改说明"

# 拉取远程更新（可能会有冲突）
git pull origin dev

# 如果有冲突，需要手动解决冲突后：
# git add .cloudstudio/preview.yaml
# git commit
```

## 推荐方案

**推荐使用选项1**（丢弃本地修改），因为：
- 远程版本已经包含了完整的端口修复功能
- 本地修改可能是旧的或不完整的
- 这样可以避免冲突，快速同步到最新代码


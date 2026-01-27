# 配置文件说明

本目录包含项目配置文件。

## 文件说明

### `pyrightconfig.json`
Python 类型检查配置文件（Pyright）。用于配置 Python 代码的类型检查规则。

**使用方式：**
- 如果使用 VS Code 或其他支持 Pyright 的编辑器，通常会自动读取此配置
- 如果配置文件不在根目录，可能需要手动指定路径

**注意：** 此文件已从根目录移动到此目录。如果编辑器无法找到配置，可以：
1. 在项目根目录创建符号链接：`ln -s docs/config/pyrightconfig.json pyrightconfig.json`
2. 或者在编辑器设置中指定配置文件路径
